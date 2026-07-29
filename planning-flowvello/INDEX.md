# FlowVello Gmail Agent — Planning Index

Read in this order:

## 0. Brutal Reality Check
**`00-BRUTAL-REALITY-CHECK.md`** — Read FIRST. Answers "should I even build this?"

## 1. MVP Spec (What to Build)
**`01-mvp-spec/01-MVP-FOR-FLOWVELLO.md`** — Exact features, build order, 14-day timeline

## 2. Gmail Integration (How It Connects)
**`02-gmail-integration/01-GMAIL-SETUP-FOR-FLOWVELLO.md`** — OAuth, Pub/Sub, polling, token management

## 3. AI Pipeline (The Brain)
**`03-ai-pipeline/01-AI-WITH-GEMINI.md`** — Gemini models, prompts (English + Urdu), cost calculation

## 4. Hosting (Where It Lives)
**`04-hosting/01-HEROKU-DEPLOYMENT.md`** — Heroku setup, config vars, $16/mo cost breakdown

## 5. Workflows (FlowVello's Operations)
**`05-workflows/01-FLOWVELLO-OPERATIONS.md`** — 5 workflows that run your agency: lead detection, client check-in, follow-ups, daily summary, weekly report

## 6. Sales (How to Sell It)
**`06-sales-packaging/01-SELLING-THIS-PRODUCT.md`** — Pricing (Rs. 5K-50K/mo), positioning, objection handling in Urdu, scripts adapted from your existing AGENCY_KIT

## 7. Gmail Safety (Never Get Flagged)
**`07-gmail-safety/01-NEVER-GET-FLAGGED.md`** — Why OAuth > password, rate limits, sending patterns that trigger flags, domain setup (SPF/DKIM)
**`07-gmail-safety/02-SAFETY-CHANGES.md`** — Code changes: rate limiter, proper threading headers, human approval gate

---

## Summary

| Folder | Purpose |
|--------|---------|
| 00 | Reality check — should you build this? |
| 01 | Exactly what to build over 14 days |
| 02 | How Gmail connects |
| 03 | How AI works (Gemini, Urdu support) |
| 04 | Where to host ($16/mo Heroku) |
| 05 | How FlowVello uses it daily |
| 06 | How to sell it (PK pricing) |
| 07 | Gmail safety — never get flagged |
