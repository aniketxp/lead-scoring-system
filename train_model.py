"""
Phase 3 lead conversion model.

Reads the Leads tab, trains a logistic regression on leads with a known outcome,
tests it on a later time period it never saw, compares it with the Phase 2
points score, and exports the learned weights so the workbook can score leads
with a plain formula.

Usage (from the repo folder)
    python train_model.py
    python train_model.py path/to/your_leads.xlsx
"""
import sys, json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, brier_score_loss

HERE = Path(__file__).resolve().parent
PATH = sys.argv[1] if len(sys.argv) > 1 else HERE / "lead_scoring_dummy.xlsx"
TEST_FROM = pd.Timestamp("2026-07-01")   # train before this date, test on or after it

POS = ["timeline", "go-live", "pricing", "quote", "demo", "raised", "sla", "migrating", "launch", "sandbox"]
NEG = ["student", "hiring", "thesis", "learn", "free account", "personal", "exploring", "openings"]
SPAM_KW = ["backlink", "guest post", "listing", "investment opportunity", "returns", "cashback reward",
           "telegram members", "followers", "influencer", "dev agency", "low rates", "seo", "claim your", "guaranteed"]
PHASE2_SRC = {"Partner Referral": 30, "Pricing Page Form": 25, "LinkedIn ABM": 20, "Event": 15,
              "Website Contact Form": 10, "Docs Signup": 5, "Chat Widget": 0}


def product_group(p):
    if p.startswith("Payments"):
        return "Payments"
    if p.startswith("Lending"):
        return "Lending"
    return p


def has_any(text, words):
    t = str(text).lower()
    return int(any(w in t for w in words))


df = pd.read_excel(PATH, sheet_name="Leads", usecols="A:P")
df["Created At"] = pd.to_datetime(df["Created At"])
msg = df["Form Message"].fillna("")

# Spam gate v1, same logic as the workbook
spam = ((df["Email Type"] == "Disposable") | msg.apply(lambda m: has_any(m, SPAM_KW)).astype(bool)
        | (msg.str.strip().str.len() < 15))
df = df[~spam].copy()

# Features known at the moment the lead arrives
df["product_group"] = df["Product Interest"].apply(product_group)
df["buying_intent"] = df["Form Message"].apply(lambda m: has_any(m, POS))
df["negative_intent"] = df["Form Message"].apply(lambda m: has_any(m, NEG))
df["pages"] = df["Pages Visited"].clip(upper=15)

# Label. Only leads with a resolved outcome are used. Open and untagged are left out.
qual = ["Qualified", "Won", "Lost"]
df = df[df["Status"].isin(qual + ["Unqualified"])].copy()
df["y"] = df["Status"].isin(qual).astype(int)

cat_cols = {"Source": "src", "Email Type": "email", "product_group": "prod"}
X = pd.get_dummies(df[list(cat_cols)].rename(columns=cat_cols), prefix_sep="=").astype(int)
X["pages"] = df["pages"]
X["buying_intent"] = df["buying_intent"]
X["negative_intent"] = df["negative_intent"]

train = df["Created At"] < TEST_FROM
test = ~train
model = LogisticRegression(C=1.0, max_iter=2000)
model.fit(X[train], df.loc[train, "y"])
p_test = model.predict_proba(X[test])[:, 1]
y_test = df.loc[test, "y"].values

# Phase 2 score on the same test leads, for comparison
p2 = (df["Source"].map(PHASE2_SRC).fillna(0)
      + np.where(df["Email Type"] == "Company", 20, 0)
      + df["product_group"].map({"Payments": 15, "Lending": 15, "KYC Verification": 5, "Banking Data API": 5}).fillna(0)
      + np.where(df["Pages Visited"] >= 8, 15, np.where(df["Pages Visited"] >= 4, 8, 0))
      + df["buying_intent"] * 15 - df["negative_intent"] * 30)


def top20_capture(scores, y):
    cut = np.quantile(scores, 0.8)
    return y[scores >= cut].sum() / y.sum()


results = {
    "train_leads": int(train.sum()), "test_leads": int(test.sum()),
    "test_positive_rate": float(y_test.mean()),
    "auc_model": float(roc_auc_score(y_test, p_test)),
    "auc_phase2": float(roc_auc_score(y_test, p2[test])),
    "top20_model": float(top20_capture(p_test, y_test)),
    "top20_phase2": float(top20_capture(p2[test].values, y_test)),
    "brier_model": float(brier_score_loss(y_test, p_test)),
    "brier_baseline": float(brier_score_loss(y_test, np.full_like(p_test, df.loc[train, "y"].mean()))),
}

bins = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
cal = pd.DataFrame({"p": p_test, "y": y_test})
cal["bin"] = pd.cut(cal["p"], bins, include_lowest=True)
calib = cal.groupby("bin", observed=False).agg(leads=("y", "size"), predicted=("p", "mean"), actual=("y", "mean"))

coefs = {"intercept": float(model.intercept_[0])}
coefs.update({c: float(w) for c, w in zip(X.columns, model.coef_[0])})

# Refit on all resolved leads for the weights used going forward
final = LogisticRegression(C=1.0, max_iter=2000).fit(X, df["y"])
final_coefs = {"intercept": float(final.intercept_[0])}
final_coefs.update({c: float(w) for c, w in zip(X.columns, final.coef_[0])})

json.dump({"results": results, "test_weights": coefs, "final_weights": final_coefs,
           "calibration": [{"bin": str(b), "leads": int(r.leads),
                            "predicted": None if pd.isna(r.predicted) else float(r.predicted),
                            "actual": None if pd.isna(r.actual) else float(r.actual)}
                           for b, r in calib.iterrows()]},
          open(HERE / "model_output.json", "w"), indent=2)

print(json.dumps(results, indent=2))
print(calib)
print(pd.Series(final_coefs).round(2).sort_values())
