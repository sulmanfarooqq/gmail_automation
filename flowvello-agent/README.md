# FlowVello Gmail AI Agent

A full Gmail automation agent for FlowVello — classifies emails, drafts replies, follows up automatically.

**⚠️ Safety First**: This agent uses the official Gmail API (OAuth 2.0), not passwords or IMAP.  
It rate-limits to 4 sends/minute, always threads replies properly, and requires human approval before sending.  
Your account will NOT be flagged — you're just replying to your own emails, faster.

## Quick Start

```bash
# 1. Install
pip install -r requirements.txt

# 2. Set up Gmail API credentials
#    Go to https://console.cloud.google.com
#    Create project → Enable Gmail API → Create OAuth 2.0 credentials
#    Download as credentials.json → place in project root

# 3. Set your Gemini API key (get from https://aistudio.google.com/)
cp .env.example .env
# Edit .env with your GEMINI_API_KEY

# 4. Run the agent
python main.py --mode web    # Web dashboard
python main.py --mode scan   # One-time inbox scan
python main.py --mode watch  # Continuous monitoring
```

## Architecture

```
                    ┌─────────────────────┐
                    │  flowvello@gmail.com │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Gmail API          │
                    │  (OAuth 2.0)        │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  gmail_agent/       │
                    │  Core Processing    │
                    │                     │
                    │  ┌───────────────┐  │
                    │  │  Classifier   │  │
                    │  │  (Gemini AI)  │  │
                    │  └──────┬────────┘  │
                    │         │           │
                    │  ┌──────▼────────┐  │
                    │  │   Drafter     │  │
                    │  │  (Gemini AI)  │  │
                    │  └──────┬────────┘  │
                    │         │           │
                    │  ┌──────▼────────┐  │
                    │  │  Follow-up    │  │
                    │  │  Scheduler    │  │
                    │  └───────────────┘  │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Dashboard (Flask)  │
                    │  Inbox | Drafts |   │
                    │  Analytics | Leads  │
                    └─────────────────────┘
```

## Features

- [x] Gmail OAuth 2.0 (connect your inbox)
- [x] Email classification (lead, support, invoice, etc.)
- [x] AI reply drafting with Gemini
- [x] Human approval before sending
- [x] Automatic follow-up sequences
- [x] Lead detection + extraction
- [x] Web dashboard (Flask)
- [x] Daily email summary
- [x] SQLite storage (zero setup)

## Project Structure

```
flowvello-agent/
├── main.py                 # Entry point (CLI + Web)
├── config.py               # App configuration
├── requirements.txt        # Dependencies
├── .env.example            # Environment template
├── credentials/            # OAuth tokens stored here
├── data/                   # SQLite database
│
├── gmail_agent/
│   ├── __init__.py
│   ├── auth.py             # Gmail OAuth 2.0
│   ├── gmail_service.py    # Gmail API operations
│   ├── email_parser.py     # Parse + clean emails
│   ├── classifier.py       # AI classification
│   ├── drafter.py          # AI reply generation
│   ├── followup.py         # Follow-up scheduling
│   ├── database.py         # SQLite storage
│   ├── scheduler.py        # Background jobs
│   └── models.py           # Data classes
│
└── dashboard/
    ├── web.py              # Flask web app
    ├── templates/          # HTML templates
    └── static/             # CSS/JS
```
