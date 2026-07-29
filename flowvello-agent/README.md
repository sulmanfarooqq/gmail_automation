<div align="center">
  <br/>
  <h1>⚡ FlowVello · Gmail AI Agent</h1>
  <p><strong>Intelligent email automation for your agency — classify, draft, follow up, never miss a lead.</strong></p>
  <br/>

  <p>
    <img src="https://img.shields.io/badge/python-3.10%2B-blue?style=flat-square"/>
    <img src="https://img.shields.io/badge/Gemini-1.5--flash-8E75B2?style=flat-square"/>
    <img src="https://img.shields.io/badge/Gmail%20API-OAuth%202.0-EA4335?style=flat-square"/>
    <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square"/>
  </p>

  <br/>
</div>

---

## 🧠 What It Does

FlowVello Gmail AI Agent connects to your agency's Gmail inbox and becomes your **AI email operations assistant**. It reads every incoming email, understands what it's about using Gemini AI, drafts a professional reply, and lets you approve with one click. It also follows up automatically when clients don't reply.

```
Incoming Email → AI Classifies → AI Drafts Reply → You Approve → Sent
                                                      ↓
                                      Follow-up Sequence (3d → 7d → 14d)
```

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI Classification** | Detects leads, support requests, invoices, spam using Gemini |
| ✏️ **Smart Drafting** | Generates context-aware replies in FlowVello's brand voice |
| ✅ **Human Approval** | You review every draft before it sends — no rogue AI |
| 🔄 **Auto Follow-ups** | 3-step sequence (Day 3 → 7 → 14) if no reply |
| 🔥 **Lead Detection** | Extracts name, phone (Pakistani +92), company, service interest |
| 📊 **Analytics Dashboard** | Daily metrics: emails processed, leads captured, time saved |
| 📬 **Unified Inbox** | Filter by leads, urgent, support — never miss what matters |
| 🔐 **Rate-Limited Sending** | 4/min max, proper threading headers — your account stays safe |

## 🖼️ Dashboard Preview

```
┌─────────────────────────────────────────────────────────────┐
│  ⚡ FlowVello                                               │
│  ┌───────┬───────┬───────┬───────┬───────┐                  │
│  │Emails │ Leads │Drafts │ Sent  │Follow │                  │
│  │  142  │   18  │   3   │  89   │  12   │                  │
│  └───────┴───────┴───────┴───────┴───────┘                  │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │ Recent Emails   │  │ Pending Drafts  │                   │
│  │ [Lead] Ali Khan  │  │ [Ali] AI Chatbot│                   │
│  │ [Sup] Sarah     │  │ [Sarah] Pricing │                   │
│  └─────────────────┘  └─────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- A Gmail account (FlowVello's)
- A Google Cloud Project with Gmail API enabled
- A Gemini API key (free tier)

### Setup (5 minutes)

```bash
# 1. Clone and install
git clone https://github.com/sulmanfarooqq/gmail_automation.git
cd gmail_automation/flowvello-agent
pip install -r requirements.txt

# 2. Add your Gemini API key
cp .env.example .env
# Edit .env → set GEMINI_API_KEY=your-key

# 3. Add Gmail API credentials
#    Download credentials.json from Google Cloud Console → place in project root

# 4. Run
python main.py --mode auth      # Login with your Gmail (one time)
python main.py --mode web       # Start dashboard at http://localhost:5000
```

### Modes

| Command | What It Does |
|---------|-------------|
| `python main.py --mode web` | Start the web dashboard (Flask) |
| `python main.py --mode scan` | One-time inbox scan + process |
| `python main.py --mode watch` | Continuous monitoring (scans every 5 min) |
| `python main.py --mode auth` | Set up Gmail OAuth (first time only) |
| `python main.py --mode summary` | Print today's email summary |

## 🏗️ Architecture

```
                     ┌──────────────────────────┐
                     │   flowvello@gmail.com     │
                     │   (Gmail Inbox)           │
                     └────────────┬─────────────┘
                                  │
                     ┌────────────▼─────────────┐
                     │     Gmail API (OAuth)     │
                     │   Fetch · Send · Modify   │
                     └────────────┬─────────────┘
                                  │
                     ┌────────────▼─────────────┐
                     │      AI Engine            │
                     │  ┌────────────────────┐  │
                     │  │  Classifier        │  │
                     │  │  (Gemini 1.5 Flash)│  │
                     │  └────────┬───────────┘  │
                     │  ┌────────▼───────────┐  │
                     │  │  Draft Generator   │  │
                     │  │  (Gemini 1.5 Flash)│  │
                     │  └────────┬───────────┘  │
                     │  ┌────────▼───────────┐  │
                     │  │  Follow-up Engine  │  │
                     │  │  (Scheduled Tasks) │  │
                     │  └────────────────────┘  │
                     └────────────┬─────────────┘
                                  │
                     ┌────────────▼─────────────┐
                     │     SQLite Database       │
                     │  Emails · Leads · Drafts  │
                     │  Follow-ups · Analytics   │
                     └────────────┬─────────────┘
                                  │
                     ┌────────────▼─────────────┐
                     │   Flask Web Dashboard    │
                     │  Inbox · Drafts · Leads  │
                     │  Analytics · Follow-ups  │
                     └──────────────────────────┘
```

## 📁 Project Structure

```
flowvello-agent/
├── main.py                    # Entry point (5 modes)
├── config.py                  # Configuration
├── requirements.txt           # Dependencies
├── .env.example               # Environment template
│
├── gmail_agent/               # Core engine
│   ├── auth.py                # Gmail OAuth 2.0
│   ├── gmail_service.py       # Fetch, send, manage
│   ├── email_parser.py        # Strip signatures, clean body
│   ├── classifier.py          # Gemini classification
│   ├── drafter.py             # Gemini reply generation
│   ├── followup.py            # Follow-up sequences
│   ├── database.py            # SQLite storage
│   ├── scheduler.py           # Background processing
│   ├── rate_limit.py          # Throttle sends (anti-flag)
│   └── models.py              # Data classes
│
├── dashboard/                 # Web interface
│   ├── web.py                 # Flask routes
│   ├── static/
│   │   └── brand.css          # FlowVello theme
│   └── templates/
│       ├── base.html          # Layout with sidebar
│       ├── dashboard.html     # Stats overview
│       ├── inbox.html         # Email list
│       ├── email_detail.html  # Full email + AI panel
│       ├── drafts.html        # Pending approvals
│       ├── leads.html         # Lead table
│       ├── followups.html     # Active sequences
│       └── analytics.html     # Daily metrics
│
└── planning-flowvello/        # Documentation
    ├── 00-BRUTAL-REALITY-CHECK.md
    ├── 01-mvp-spec/
    ├── 02-gmail-integration/
    ├── 03-ai-pipeline/
    ├── 04-hosting/
    ├── 05-workflows/
    ├── 06-sales-packaging/
    └── 07-gmail-safety/
```

## 🔒 Safety First

This agent is built so your Gmail account **never gets flagged**:

| Protection | Detail |
|-----------|--------|
| **Official API** | Uses Gmail API (OAuth 2.0), not passwords or IMAP |
| **Rate Limited** | Caps at 4 sends/minute, 80/hour, 400/day |
| **Threaded Replies** | Proper In-Reply-To + References headers |
| **Human Approval** | No auto-sending — every draft needs your review |
| **Personalized** | Each reply is unique, not a template blast |
| **Reply-Only** | Only responds to people who email you first |

## 🛡️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| Web Framework | Flask 3.0 |
| AI | Google Gemini 1.5 Flash |
| Gmail | Google API Python Client |
| Database | SQLite (via sqlite3) |
| Styling | Tailwind CSS (CDN) |
| Auth | Gmail OAuth 2.0 |

## 📊 Email Classification Categories

| Intent | Description |
|--------|-------------|
| `lead` | Someone asking about AI automation services |
| `client_support` | Existing client with a technical issue |
| `billing` | Payment, invoice, or pricing |
| `partnership` | Collaboration or partnership offer |
| `meeting_request` | Asking to schedule a call |
| `complaint` | Negative feedback |
| `spam` | Promotional or irrelevant |
| `other` | Everything else |

## 🚢 Deployment

### Heroku (Recommended)

```bash
heroku create flowvello-agent
heroku addons:create heroku-postgresql:mini
heroku config:set GEMINI_API_KEY=your-key
heroku config:set FLASK_SECRET_KEY=your-secret
git push heroku main
```

### Docker (Alternative)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "main.py", "--mode", "web"]
```

---

<div align="center">
  <p>
    Built for <strong>FlowVello</strong> — AI Automation Agency, Mirpur, Pakistan
  </p>
  <p>
    <sub>Gemini · Gmail API · Python · Flask</sub>
  </p>
</div>
