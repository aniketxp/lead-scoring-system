"""
Generates the synthetic lead dataset used in this project.
Every name, email, company and message is invented.
Company names are coined words, and every email address and website uses the
reserved .example domain (RFC 2606), so none can belong to a real organisation.

Usage (from the repo root)
    python generate_dummy_leads.py
"""
import random, datetime as dt
import numpy as np
random.seed(42); np.random.seed(42)

N = 800
start = dt.datetime(2025,10,1)
end = dt.datetime(2026,9,24)

sources = {
 # source: (weight, P(spam), P(unqual | genuine), P(qualified+ | genuine))
 "Website Contact Form": (0.30, 0.55, 0.55, 0.22),
 "Chat Widget":          (0.14, 0.60, 0.65, 0.12),
 "Pricing Page Form":    (0.14, 0.18, 0.35, 0.45),
 "Docs Signup":          (0.14, 0.25, 0.70, 0.12),
 "LinkedIn ABM":         (0.12, 0.03, 0.40, 0.40),
 "Event":                (0.10, 0.08, 0.50, 0.30),
 "Partner Referral":     (0.06, 0.02, 0.25, 0.60),
}
src_names = list(sources); src_w = [sources[s][0] for s in src_names]

first = ["Arjun","Priya","Daniel","Mei","Lucas","Sofia","Omar","Hana","Ethan","Aisha","Ravi","Chloe","Mateo","Yuki","Noah","Fatima","Leon","Ananya","Ivan","Grace","Kenji","Zara","Felix","Nadia","Sam","Elena","Tariq","Lina","Marco","Ji-woo"]
last = ["Sharma","Chen","Muller","Garcia","Okafor","Tanaka","Silva","Nguyen","Khan","Rossi","Kim","Patel","Novak","Haddad","Berg","Mehta","Costa","Lee","Ivanova","Brown"]
pre = ["Brindlewick", "Quillmoor", "Tarnvale", "Ostrivo", "Plumeridge", "Vexmoor", "Kestralith", "Dunmarrow", "Ferrowind", "Glimmerfen", "Hollowquay", "Juniperholt", "Larkspindle", "Marrowgate", "Nettlebrisk", "Orrowmere", "Pellowin", "Quarrytide", "Rushbarrow", "Sallowfenn", "Thornlacey", "Umberwick", "Wyndlefoss", "Yarrowtun", "Zellowmark"]
suf = ["Labs", "Pay", "Money", "Finance", "Bank", "Commerce", "Studio", "Wallet", "Capital", "Systems"]
countries = ["India","USA","Singapore","UAE","UK","Germany","South Korea","Vietnam","Nigeria","Brazil","Switzerland","Japan","Canada","Turkey"]
free = ["freemail.example", "inboxly.example", "postbox.example", "webmail.example", "letterdrop.example"]
disposable = ["tempinbox.example", "throwaway.example", "burnmail.example", "quickdrop.example", "vanishmail.example"]

products_good = ["Payments - Card Issuing","Payments - Cross-Border","Payments - Payouts","Payments - Virtual Accounts","KYC Verification","Lending - Loan Origination","Lending - Credit Scoring","Banking Data API"]

good_msgs = [
 "We are launching a {p} product and need a managed {t} setup with go-live in Q{q}.",
 "Looking for pricing on KYC verification across {n} countries. Our current vendor keeps missing checks.",
 "Our team is building a lending product for small businesses. Need help with sandbox setup and credit rules. Timeline 2 to 3 months.",
 "Need a banking data API with SLA for our budgeting app, around {r}M calls per day.",
 "Evaluating {t} providers for our {p} app. Can we get a demo and a cost comparison?",
 "We raised a seed round and plan to launch a digital savings platform for SMEs. Want to discuss infrastructure.",
 "Migrating from another provider for our card program, need a quote this month.",
]
unq_msgs = [
 "I am a student researching open banking for my thesis. Can you share some material?",
 "Are you hiring fintech developers? Please share openings.",
 "Can I use your API for a personal budget tracker?",
 "Just exploring, what does your company do?",
 "Can you give a free account for our hackathon project?",
 "Interested in learning about fintech, where do I start?",
]
spam_msgs = [
 "We offer premium SEO backlinks and guest post services for fintech websites. Reply for rates.",
 "Get your app listing on top review sites in 48 hours, guaranteed. Contact our listing agent.",
 "Exclusive investment opportunity with 300% returns, DM on telegram.",
 "We are a dev agency from offshore, 20 fintech developers available at low rates.",
 "Claim your cashback reward now at the link below.",
 "asdf qwer",
 "hi",
 "Boost your Twitter followers and Telegram members, organic fintech marketing.",
 "Partnership proposal for fintech influencer marketing campaign, 500k reach.",
 "test",
]

def ts():
    d = start + (end-start)*random.random()
    return d.replace(minute=random.randint(0,59), second=0, microsecond=0)

def company():
    return f"{random.choice(pre)} {random.choice(suf)}"

rows = []
emails_seen = []
for i in range(N):
    src = random.choices(src_names, src_w)[0]
    w, pspam, punq, pqual = sources[src]
    created = ts()
    is_spam = random.random() < pspam
    fn, ln = random.choice(first), random.choice(last)
    if is_spam:
        r = random.random()
        if r < 0.35:
            etype, dom = "Disposable", random.choice(disposable)
            comp, web = "", ""
        elif r < 0.75:
            etype, dom = "Free", random.choice(free)
            comp = random.choice(["", "", "Boostquill Media", "Listpeak Directory", "Rankfarrow SEO Agency"])
            web = ""
        else:
            etype = "Company"; comp = random.choice(["Boostquill Media","Listpeak Directory","Rankfarrow SEO Agency","Codewhistle Outsourcing","Hypemarrow PR"])
            dom = comp.lower().replace(" ","") + ".example"; web = "https://"+dom
        msg = random.choice(spam_msgs)
        prod = random.choice(["Other","Other","Payments - Card Issuing","KYC Verification"])
        truth = "Spam"
        pages = random.randint(1,2)
        country = random.choice(countries)
        # duplicate spam submissions
        if emails_seen and random.random() < 0.18:
            prev = random.choice([e for e in emails_seen if e[1]=="Spam"] or emails_seen)
            email = prev[0]
        else:
            email = f"{fn.lower()}{random.randint(1,999)}@{dom}"
    else:
        comp = company()
        u = random.random()
        if u < punq:
            truth = "Unqualified"
            msg = random.choice(unq_msgs)
            etype = random.choices(["Free","Company"],[0.75,0.25])[0]
            prod = random.choice(["Other","KYC Verification","Banking Data API","Payments - Card Issuing"])
            pages = random.randint(1,4)
            if etype=="Free": comp = random.choice(["", comp])
        else:
            # genuine buyer; will it qualify?
            qual_prob = pqual/(1-punq)
            truth = "Qualified+" if random.random() < min(qual_prob,0.9) else "Not qualified"
            etype = random.choices(["Company","Free"],[0.85,0.15] if truth=="Qualified+" else [0.6,0.4])[0]
            p = random.choice(products_good)
            msg = random.choice(good_msgs).format(p=random.choice(["marketplace","payroll","remittance","BNPL","loyalty"]),
                  t=p.split(" - ")[-1].lower() if "Payments" in p else "card issuing", q=random.randint(1,4), n=random.randint(2,6), r=random.randint(5,80))
            prod = p
            pages = random.randint(3,12) if truth=="Qualified+" else random.randint(1,6)
        dom = (comp.lower().replace(" ","")+".example") if (etype=="Company" and comp) else random.choice(free)
        if etype=="Company" and not comp: etype="Free"
        web = ("https://"+dom) if etype=="Company" else ""
        email = f"{fn.lower()}.{ln.lower()}@{dom}"
        country = random.choice(countries)
    emails_seen.append((email, truth))

    # status as recorded (logging gaps, worse in older months)
    age_months = (end - created).days/30
    p_untag = 0.15 + 0.03*age_months  # ~15% recent to ~48% old
    if truth == "Spam" and random.random() < 0.25:  # spam often just ignored
        p_untag += 0.15
    status = ""
    if random.random() >= min(p_untag, 0.7):
        if truth == "Spam": status = "Spam"
        elif truth == "Unqualified": status = "Unqualified"
        elif truth == "Not qualified": status = random.choice(["Unqualified","Open"])
        else:
            status = random.choices(["Qualified","Won","Lost"],[0.35,0.25,0.40])[0]
            if (end-created).days < 30: status = random.choice(["Qualified","Open"])
    # response time in hours
    if truth == "Spam": resp = round(float(np.random.lognormal(3.2,0.8)),1) if random.random()<0.6 else None
    else: resp = round(float(np.random.lognormal(2.6,1.0)),1)
    deal = random.choice([18000,24000,36000,48000,60000,96000,120000]) if status=="Won" else None
    owner = random.choice(["Rahul","Neha","Vikram","Unassigned"]) if status!="Spam" else random.choice(["Unassigned","Rahul"])
    rows.append(dict(created=created, source=src, name=f"{fn} {ln}", email=email, etype=etype, company=comp,
                     website=web, country=country, product=prod, message=msg, pages=pages, resp=resp,
                     owner=owner, status=status, deal=deal, truth=truth))

rows.sort(key=lambda r: r["created"])
import pandas as pd
from pathlib import Path
out = Path(__file__).resolve().parent / "dummy_leads.csv"
df = pd.DataFrame(rows).rename(columns={"created": "created_at", "etype": "email_type", "resp": "first_response_hrs",
                                        "deal": "deal_value_usd", "truth": "hidden_true_label"})
df.insert(0, "lead_id", [f"L-{i+1:04d}" for i in range(len(df))])
df.to_csv(out, index=False)
print(f"Wrote {len(df)} synthetic leads to {out}")
