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
    <img src="https://img.shields.io/badge/status-production-blueviolet?style=flat-square"/>
  </p>

  <br/>
</div>

---

## 📋 Table of Contents

- [What It Does](#-what-it-does)
- [Full Feature List](#-full-feature-list)
- [UML Diagrams — System Workflow](#-complete-system-diagram--full-agent-workflow)
  - [Complete System Diagram](#-complete-system-diagram--full-agent-workflow)
- [Human Handoff](#-human-handoff)
- [Quick Start](#-quick-start)
- [Modes](#-modes)
- [Classification Categories](#-email-classification-categories)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Safety First](#-safety-first)
- [Tech Stack](#-tech-stack)
- [Deployment](#-deployment)

---

## 🧠 What It Does

FlowVello Gmail AI Agent connects to your agency's Gmail inbox and becomes your **AI email operations assistant**. It reads every incoming email, understands its intent using Gemini AI, drafts context-aware replies, presents them for your approval, sends them, and automatically follows up when there's no response. If you want to take over a conversation at any point, you can — the AI steps aside.

```
                    ┌──────────────────────────────────────┐
                    │       Incoming Email arrives          │
                    └──────────────────┬───────────────────┘
                                       │
                    ┌──────────────────▼───────────────────┐
                    │    1. AI Classifies Intent            │
                    │       (lead / support / billing /..)  │
                    └──────────────────┬───────────────────┘
                                       │
                    ┌──────────────────▼───────────────────┐
                    │    2. AI Generates Draft Reply        │
                    │       (context-aware, personalized)   │
                    └──────────────────┬───────────────────┘
                                       │
                    ┌──────────────────▼───────────────────┐
                    │    3. You Review + Approve            │
                    │       (or edit, or reject, or take    │
                    │        over the conversation)         │
                    └──────────────────┬───────────────────┘
                                       │
                    ┌──────────────────▼───────────────────┐
                    │    4. Reply Sent via Gmail API        │
                    └──────────────────┬───────────────────┘
                                       │
                    ┌──────────────────▼───────────────────┐
                    │    5. Auto Follow-up Sequence         │
                    │       Day 3 → Day 7 → Day 14          │
                    │       (stops if contact replies)      │
                    └──────────────────────────────────────┘
```

---

## ✨ Full Feature List

| # | Feature | Description | Human Role |
|---|---------|-------------|-----------|
| 1 | 📬 **Inbox Monitoring** | Continuously scans Gmail inbox for new emails via API | Passive — system monitors |
| 2 | 🧠 **AI Classification** | Gemini classifies each email: lead, support, billing, partnership, meeting_request, complaint, spam, or other | Review classification |
| 3 | 🔥 **Lead Detection** | Extracts name, phone (Pakistani +92), company, and service interest. Scores leads 0-100. Creates lead record | Review lead data |
| 4 | ✏️ **AI Draft Generation** | Gemini writes context-aware replies using FlowVello's knowledge base (services, tone, pricing) | Approve / Edit / Reject |
| 5 | ✅ **Human Approval Gate** | Every draft requires explicit approval before sending. No auto-sending for new conversations | Click approve or edit |
| 6 | 📤 **Send via Gmail API** | Sends approved replies with proper threading headers (In-Reply-To, References) | One-click approve |
| 7 | 🔄 **Follow-up Sequences** | Automatic 3-step follow-up: Day 3 ("checking in"), Day 7 ("still interested?"), Day 14 ("last try") | Monitor progress |
| 8 | 👤 **Human Handoff** | Take full control of any conversation — AI stops drafting, follow-ups stop. Re-enable AI anytime | Click "Take Over" |
| 9 | 📊 **Analytics Dashboard** | Tracks: emails processed, leads captured, drafts generated, replies sent, follow-ups sent, hours saved | View reports |
| 10 | 📋 **Daily Summary** | Auto-generated morning report: pending drafts, new leads, urgent emails, follow-ups due | Read & act |
| 11 | 🔐 **Rate-Limited Sending** | 4 sends/min max, 80/hr, 400/day. 3-second gap between sends. Proper email threading headers | Transparent |
| 12 | 🏷️ **Smart Filters** | Filter inbox by leads, urgent, support. Badges on every email row | Click filter |
| 13 | 🚫 **Spam Detection** | Classifies promotional/irrelevant emails as spam — skips processing | Review if needed |
| 14 | ⏹️ **Follow-up Stop on Reply** | Detects when contact replies and auto-stops the follow-up sequence | Automatic |
| 15 | 🖥️ **Web Dashboard** | Full Flask UI with sidebar navigation: Dashboard, Inbox, Drafts, Leads, Follow-ups, Analytics | All interaction |

---

## 📐 Complete System Diagram — Full Agent Workflow

```mermaid
flowchart TD
    START([📬 Email arrives in Gmail]) --> CHECK{Already processed?}
    CHECK -->|Yes| DONE([End])
    CHECK -->|No| HANDOFF_CHECK{Thread under<br/>human control?}
    HANDOFF_CHECK -->|Yes| SKIP_AI[⏭️ Mark processed<br/>Skip AI entirely]
    HANDOFF_CHECK -->|No| STORE[💾 Store raw email<br/>in SQLite]
    
    SKIP_AI --> DONE
    STORE --> CLASSIFY[🧠 Gemini AI classifies intent]

    CLASSIFY -->|lead 🔥| LEAD_FLOW
    CLASSIFY -->|client_support 🛠️| SUPPORT_FLOW
    CLASSIFY -->|billing 💰| BILLING_FLOW  
    CLASSIFY -->|meeting_request 📅| MEETING_FLOW
    CLASSIFY -->|complaint ⚠️| COMPLAINT_FLOW
    CLASSIFY -->|partnership 🤝| PARTNER_FLOW
    CLASSIFY -->|spam 🚫| SPAM[Mark spam - discarded]
    CLASSIFY -->|other 📨| DRAFT_FLOW

    subgraph LEAD_FLOW [Lead Detection]
        LEAD_EXTRACT[Extract: name, phone,<br/>company, service interest] --> LEAD_SCORE[Score lead 0-100]
        LEAD_SCORE --> LEAD_SAVE[💾 Save to Leads table]
        LEAD_SAVE --> LEAD_NOTIFY[🔔 Notify user]
        LEAD_NOTIFY --> DRAFT_FLOW
    end

    subgraph DRAFT_FLOW [Draft Generation]
        DRAFT[✏️ Gemini generates<br/>context-aware reply] --> PENDING[⏳ Mark as pending<br/>Show in AI Drafts]
    end

    SPAM --> DONE
    SUPPORT_FLOW --> DRAFT_FLOW
    BILLING_FLOW --> DRAFT_FLOW
    MEETING_FLOW --> DRAFT_FLOW
    COMPLAINT_FLOW --> DRAFT_FLOW
    PARTNER_FLOW --> DRAFT_FLOW

    PENDING --> HUMAN_VIEW[👤 User opens email<br/>in dashboard]

    HUMAN_VIEW --> ACTION{User action}
    ACTION -->|✅ Approve| SEND_FLOW
    ACTION -->|✏️ Edit| EDIT[User edits draft] --> SEND_FLOW
    ACTION -->|❌ Reject| REJECTED[🗑️ Draft rejected]
    ACTION -->|👤 Take Over| TAKEOVER[HUMAN HANDOFF]

    REJECTED --> DONE

    subgraph SEND_FLOW [Send & Follow-up]
        SEND[📤 Send via Gmail API<br/>with threading headers] --> SENT[✅ Mark as sent]
        SENT --> DECIDE{Is lead or<br/>inquiry?}
        DECIDE -->|Yes| SCHEDULE[📅 Schedule 3-step<br/>follow-up sequence]
        DECIDE -->|No| DONE
        SCHEDULE --> DAY3[Day 3: Follow-up #1<br/>'Checking in']
        DAY3 --> R1{Contact<br/>replied?}
        R1 -->|Yes| STOP[⏹️ Stop sequence]
        R1 -->|No| DAY7[Day 7: Follow-up #2<br/>'Still interested?']
        DAY7 --> R2{Contact<br/>replied?}
        R2 -->|Yes| STOP
        R2 -->|No| DAY14[Day 14: Final follow-up<br/>'Last try']
        DAY14 --> R3{Contact<br/>replied?}
        R3 -->|Yes| STOP
        R3 -->|No| COMPLETE[✅ Sequence complete]
    end

    STOP --> DONE
    COMPLETE --> DONE

    subgraph TAKEOVER [Human Handoff Cycle]
        HANDOFF_MARK[✋ Mark thread<br/>human_handled = 1] --> FO_STOP[⏹️ Stop all follow-ups<br/>for this thread]
        FO_STOP --> MANUAL[💬 User replies manually]
        MANUAL --> REENABLE{User clicks<br/>Re-enable AI?}
        REENABLE -->|Yes| AI_BACK[🤖 AI resumes for<br/>this thread]
        REENABLE -->|No| MANUAL
    end

    TAKEOVER --> HANDOFF_MARK
    AI_BACK --> HANDOFF_CHECK

    SEND --> SEND_FLOW
```

---

## 👤 Human Handoff

The agent has a **Human-in-the-Loop** design. You are always in control.

### How It Works

| State | What Happens | AI Behavior |
|-------|-------------|-------------|
| **AI Active** (default) | AI classifies, drafts, follows up. You approve/reject | Fully active |
| **You Take Over** | You click "Take Over" on any email thread | AI stops for this thread |
| **Human Handling** | You reply manually. AI does nothing for this thread | Paused |
| **Re-enable AI** | You click "Re-enable AI" | AI resumes |

### When to Use Human Handoff

- **Complex negotiations** where AI might say the wrong thing
- **Sensitive topics** (complaints, legal, pricing disputes)
- **Personal relationships** where the client expects direct human interaction
- **Any time you want full control** of a conversation

### Button Locations

- **Email Detail page** — "👤 Take Over (Stop AI)" button next to the page header
- **Human Active** — A purple info card appears showing "You're handling this conversation"
- **Re-enable** — "🤖 Re-enable AI" button to bring AI back

```mermaid
flowchart LR
    A[📬 Email arrives] --> B{AI Active?}
    B -->|Yes| C[AI classifies + drafts]
    B -->|No - Human| D[No AI action]
    C --> E{User action?}
    E -->|Approve| F[AI sends + follows up]
    E -->|Take Over| G[AI pauses forever thread]
    G --> H{User clicks re-enable?}
    H -->|Yes| C
    H -->|No| D
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- A Gmail account (FlowVello's)
- A Google Cloud Project with Gmail API enabled
- A Gemini API key (free tier from aistudio.google.com)

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

---

## 📊 Email Classification Categories

| Intent | Description | Auto-Replyable? | Follow-up? |
|--------|-------------|----------------|------------|
| `lead` | Someone asking about AI automation services | No (needs approval) | ✅ Yes |
| `client_support` | Existing client with a technical issue | Depends on complexity | No |
| `billing` | Payment, invoice, or pricing questions | No (needs approval) | No |
| `partnership` | Collaboration or partnership offer | No (needs approval) | Conditional |
| `meeting_request` | Asking to schedule a call/meeting | ✅ Yes (suggest times) | No |
| `complaint` | Negative feedback or complaint | No (human only) | No |
| `spam` | Promotional, newsletter, irrelevant | Skipped entirely | No |
| `other` | Everything that doesn't fit above | No | No |

---

## 🏗️ Architecture

```mermaid
flowchart TB
    subgraph EXTERNAL [External Services]
        GMAIL[Gmail API<br/>OAuth 2.0]
        GEMINI[Gemini AI<br/>1.5 Flash]
    end
    
    subgraph CORE [gmail_agent - Core Engine]
        AUTH[auth.py<br/>OAuth flow]
        GMAIL_SVC[gmail_service.py<br/>Fetch · Send · Modify]
        PARSER[email_parser.py<br/>Strip signatures · Clean]
        CLASSIFIER[classifier.py<br/>Gemini classification]
        DRAFTER[drafter.py<br/>Gemini reply gen]
        FOLLOWER[followup.py<br/>Schedule sequences]
        RATE[rate_limit.py<br/>Throttle sends]
    end
    
    subgraph DATA [Data Layer]
        DB[database.py<br/>SQLite storage]
        MODELS[models.py<br/>Data classes]
    end
    
    subgraph SCHED [Background Tasks]
        SCHEDULER[scheduler.py<br/>Scan · Process · Follow-up]
    end
    
    subgraph UI [Web Dashboard]
        FLASK[web.py<br/>Flask routes]
        TEMPLATES[templates/<br/>7 HTML pages]
        CSS[static/brand.css<br/>FlowVello theme]
    end
    
    GMAIL <--> AUTH
    GMAIL <--> GMAIL_SVC
    GMAIL_SVC --> PARSER
    PARSER --> CLASSIFIER
    CLASSIFIER --> GEMINI
    CLASSIFIER --> DRAFTER
    DRAFTER --> GEMINI
    DRAFTER --> FOLLOWER
    
    GMAIL_SVC --> DB
    CLASSIFIER --> DB
    DRAFTER --> DB
    FOLLOWER --> DB
    RATE --> GMAIL_SVC
    
    SCHEDULER --> GMAIL_SVC
    SCHEDULER --> CLASSIFIER
    SCHEDULER --> DRAFTER
    SCHEDULER --> FOLLOWER
    SCHEDULER --> DB
    
    FLASK --> DB
    FLASK --> SCHEDULER
    FLASK --> TEMPLATES
    FLASK --> CSS
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
│       ├── email_detail.html  # Full email + AI panel + Handoff
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

---

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

---

## 🛡️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| Web Framework | Flask 3.0 |
| AI | Google Gemini 1.5 Flash |
| Gmail | Google API Python Client |
| Database | SQLite (via sqlite3) |
| Styling | Custom CSS (FlowVello brand theme) |
| Auth | Gmail OAuth 2.0 |
| Diagrams | Mermaid.js (rendered by GitHub) |

---

## 🚢 Deployment

### Heroku (Recommended)

```bash
heroku create flowvello-agent
heroku addons:create heroku-postgresql:mini
heroku config:set GEMINI_API_KEY=your-key
heroku config:set FLASK_SECRET_KEY=your-secret
heroku config:set APP_URL=https://flowvello-agent.herokuapp.com
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

## 📊 Database Schema

```mermaid
erDiagram
    EMAILS {
        string id PK
        string thread_id
        string from_address
        string from_name
        string subject
        text body_text
        datetime received_at
        int human_handled
        datetime human_handled_at
    }
    
    CLASSIFICATIONS {
        string email_id PK, FK
        string intent
        float confidence
        string priority
        string sentiment
        int is_lead
        int lead_score
    }
    
    DRAFTS {
        int id PK
        string email_id FK
        string subject
        text body
        string status
        int needs_approval
    }
    
    FOLLOWUPS {
        string id PK
        string original_email_id FK
        string contact_email
        int step
        int max_steps
        string status
    }
    
    LEADS {
        int id PK
        string email
        string name
        string phone
        string service_interest
        int score
    }
    
    ANALYTICS {
        string date PK
        int emails_processed
        int leads_captured
        int drafts_generated
    }
    
    EMAILS ||--o| CLASSIFICATIONS : "has"
    EMAILS ||--o| DRAFTS : "has"
    EMAILS ||--o| FOLLOWUPS : "triggers"
    EMAILS ||--o| LEADS : "generates"
```

---

<div align="center">
  <p>
    Built for <strong>FlowVello</strong> — AI Automation Agency, Mirpur, Pakistan
  </p>
  <p>
    <sub>Gemini · Gmail API · Python · Flask · Mermaid</sub>
  </p>
  <br/>
</div>
