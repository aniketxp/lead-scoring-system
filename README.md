# Lead Qualification and Conversion Scoring

An end-to-end product case study. It filters spam out of an inbound lead queue, scores every genuine lead by how likely it is to convert, and explains each score in plain words so sales knows who to call first and why.

**[Live prototype](https://aniketxp.github.io/lead-scoring-system/)** | **[Case study PDF](case_study.pdf)**

> All data in this repo is synthetic. 800 invented leads were generated to rehearse the method, so the results validate the approach rather than predict real-world performance.

## The problem

Spam, vendor pitches and real buyers land in one queue and get answered in arrival order. High-intent leads wait as long as junk, and many leads never get an outcome recorded, so nobody learns what a good lead looks like.

## The approach

The work treats this as two separate problems with opposite error costs.

1. **Spam gate.** A yes or no filter where blocking a real buyer is the worst mistake. Leads are quarantined for review, never deleted, and rules are kept only if they are highly precise.
2. **Conversion score.** A ranking where leaving a hot lead waiting is the worst mistake. Leads land in Hot, Warm or Nurture with a calibrated probability and plain-language reasons.

It was built in phases, each useful on its own.

| Phase | What it does |
| --- | --- |
| 0. Labels and logging | Audit the data, define outcomes, measure baselines |
| 1. Spam gate | Precision-first rules with a quarantine queue |
| 2. Points score | Transparent, editable weights with buckets and reasons |
| 3. Learned model | Logistic regression trained on outcomes, tested on a later time period |
| Product | Clickable sales queue with quarantine review and model health views |

## Results on synthetic data

| Measure | Result |
| --- | --- |
| Genuine leads wrongly quarantined | 0%, down from 34% in the first draft of the rules |
| Hot leads that reached a qualified opportunity | 92%, against 2% for Nurture |
| Qualified leads in the top 20% of scores | 57%, against a 50% target |
| Ranking quality (AUC) on an unseen later period | 0.972 for the model, 0.966 for the points score |

The biggest lesson was that clean outcome logging mattered more than any model, and that a well-designed points score captured most of the value.

## What's in the repo

```
lead_scoring_dummy.xlsx     Workbook with leads, audit, spam rules, points score and live model probabilities (all formulas)
dummy_leads.csv             The same synthetic leads as plain CSV, created by the generator script
train_model.py              Trains the model, tests it on a later period, compares it with the points score, exports weights
generate_dummy_leads.py     Rebuilds the synthetic dataset
index.html                  The clickable prototype (served by GitHub Pages)
case_study.pdf              19-slide case study
```

## Run it

```bash
pip install -r requirements.txt
python generate_dummy_leads.py   # optional, rebuilds dummy_leads.csv
python train_model.py            # trains and tests on lead_scoring_dummy.xlsx
```

The script prints test results and writes the learned weights to `model_output.json`. Paste those weights into the workbook's Conversion Model tab and every probability updates.

## Caveats

The patterns in the synthetic data were designed, so strong results are expected. The points score weights were drafted on the same data they were tested on. The model's test period holds only 83 resolved leads. A real deployment should run in shadow mode on real leads before anyone relies on the scores.

## Tools

Python (pandas, scikit-learn), Excel formulas, vanilla HTML/CSS/JS.

## License

MIT
