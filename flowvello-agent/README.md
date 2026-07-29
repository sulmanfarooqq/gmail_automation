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
- [UML Diagrams — System Workflow](#-uml-diagrams--system-workflow)
  - [Full Email Processing Workflow](#1-full-email-processing-workflow)
  - [AI Pipeline — Sequence Diagram](#2-ai-pipeline--sequence-diagram)
  - [Human Handoff Flow](#3-human-handoff-flow)
  - [Use Case Diagram — All Agent Functionalities](#4-use-case-diagram--all-agent-functionalities)
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

## 📐 UML Diagrams — System Workflow

### 1. Full Email Processing Workflow

```mermaid
flowchart TD
    START([Email arrives in Gmail Inbox]) --> CHECK{Already processed?}
    CHECK -->|Yes| SKIP[Skip email]
    CHECK -->|No| HANDLED{Thread human-handled?}
    HANDLED -->|Yes| SKIP_H[Mark processed, skip AI]
    HANDLED -->|No| STORE[1. Store raw email in SQLite]
    STORE --> CLASSIFY[2. Gemini AI Classifies]
    
    CLASSIFY --> CLASSIFY_RESULT{Intent?}
    
    CLASSIFY_RESULT -->|lead| LEAD_FLOW
    CLASSIFY_RESULT -->|client_support| SUPPORT_FLOW
    CLASSIFY_RESULT -->|billing| BILLING_FLOW
    CLASSIFY_RESULT -->|meeting_request| MEETING_FLOW
    CLASSIFY_RESULT -->|complaint| COMPLAINT_FLOW
    CLASSIFY_RESULT -->|partnership| PARTNER_FLOW
    CLASSIFY_RESULT -->|spam| SPAM[Mark as spam - skip]
    CLASSIFY_RESULT -->|other| DRAFT_FLOW
    
    subgraph LEAD_FLOW [Lead Detection]
        LEAD[Extract: name, phone, company, service] --> LEAD_SAVE[Save lead to database]
        LEAD_SAVE --> LEAD_NOTIFY[Notify user]
        LEAD_NOTIFY --> DRAFT_FLOW
    end
    
    subgraph DRAFT_FLOW [Draft Generation]
        DRAFT[3. Gemini generates reply] --> DRAFT_CHECK{Needs approval?}
        DRAFT_CHECK -->|Yes| PENDING[Mark as pending - show in AI Drafts]
        DRAFT_CHECK -->|No| AUTO_APPROVE{Is FAQ / auto-replyable?}
        AUTO_APPROVE -->|Yes| SEND_FLOW
        AUTO_APPROVE -->|No| PENDING
    end
    
    subgraph APPROVAL_FLOW [Human Review]
        PENDING --> HUMAN_VIEW[User views draft]
        HUMAN_VIEW --> ACTION{Action}
        ACTION -->|Approve| SEND_FLOW
        ACTION -->|Edit| EDIT[User edits] --> SEND_FLOW
        ACTION -->|Reject| REJECTED[Mark rejected]
        ACTION -->|Take Over| HANDOFF[Human takes over]
    end
    
    subgraph SEND_FLOW [Send & Follow-up]
        SEND[4. Send via Gmail API] --> SENT[Mark as sent]
        SENT --> FOLLOWUP{Is lead or inquiry?}
        FOLLOWUP -->|Yes| SCHEDULE[5. Schedule follow-up sequence]
        FOLLOWUP -->|No| DONE
        SCHEDULE --> DAY3[Day 3: Follow-up #1]
        DAY3 --> REPLY1{Contact replied?}
        REPLY1 -->|Yes| STOP[Stop sequence]
        REPLY1 -->|No| DAY7[Day 7: Follow-up #2]
        DAY7 --> REPLY2{Contact replied?}
        REPLY2 -->|Yes| STOP
        REPLY2 -->|No| DAY14[Day 14: Final follow-up]
        DAY14 --> COMPLETE[Mark sequence complete]
    end
    
    subgraph HANDOFF [Human Handoff]
        HANDOFF_TAKEN[AI stops for this thread] --> FO_STOP[Follow-ups stopped]
        FO_STOP --> MANUAL[User replies manually]
        MANUAL --> REENABLE{User can re-enable AI}
        REENABLE -->|Yes| AI_BACK[AI resumes for thread]
        REENABLE -->|No| STAY_MANUAL[Stays manual]
    end
    
    SKIP --> DONE([End])
    SKIP_H --> DONE
    SPAM --> DONE
    REJECTED --> DONE
    STOP --> DONE
    COMPLETE --> DONE
    SEND_FLOW --> FOLLOWUP
```

### 2. AI Pipeline — Sequence Diagram

```mermaid
sequenceDiagram
    participant G as Gmail Inbox
    participant A as Gmail API
    participant S as Scheduler
    participant D as Database (SQLite)
    participant AI as Gemini AI
    participant U as User (Dashboard)

    Note over G,U: === EMAIL ARRIVES ===
    G->>A: New email received
    S->>A: Poll for unread emails
    A->>S: Return email data
    
    Note over S,AI: === CLASSIFICATION ===
    S->>D: Save raw email
    S->>AI: Send email body + subject
    AI->>S: Return classification JSON
    S->>D: Store classification
    
    alt is lead
        S->>D: Create lead record
        S->>U: Notify: new lead detected
    end
    
    Note over S,AI: === DRAFT GENERATION ===
    S->>AI: Send email + classification + KB context
    AI->>S: Return draft reply JSON
    S->>D: Store draft (pending)
    
    Note over U: === HUMAN REVIEW ===
    U->>D: View email + AI draft
    U->>U: Review / Edit / Approve / Reject
    
    alt approved
        U->>S: Approve draft
        S->>A: Send email via Gmail API
        A->>S: Confirm sent
        S->>D: Mark draft as sent
        S->>D: Schedule follow-up sequence
    else rejected
        U->>S: Reject draft
        S->>D: Mark draft as rejected
    else take over
        U->>S: Take over conversation
        S->>D: Mark thread human_handled
        S->>D: Stop all follow-ups for thread
    end
    
    Note over S: === FOLLOW-UP (background) ===
    S->>D: Check due follow-ups every 5 min
    alt follow-up due
        S->>AI: Generate follow-up text
        S->>A: Send follow-up
        S->>D: Update step, schedule next
    end
    
    alt contact replies
        S->>D: Stop follow-up sequence
    end
```

### 3. Human Handoff Flow

```mermaid
stateDiagram-v2
    [*] --> AI_ACTIVE: Email received
    
    state AI_ACTIVE {
        [*] --> Classifying
        Classifying --> Drafting
        Drafting --> Awaiting_Approval
        Awaiting_Approval --> Sending : Approve
        Awaiting_Approval --> FollowUps
        FollowUps --> Complete
    }
    
    AI_ACTIVE --> HUMAN_CONTROL: User clicks "Take Over"
    
    state HUMAN_CONTROL {
        [*] --> AI_Paused
        AI_Paused --> Manual_Replies
        Manual_Replies --> AI_Paused : New emails in thread
        AI_Paused --> Re_enable_AI : User clicks "Re-enable AI"
        Re_enable_AI --> [*]
    }
    
    HUMAN_CONTROL --> AI_ACTIVE: AI re-enabled
    
    AI_ACTIVE --> COMPLETED: Thread resolved
    HUMAN_CONTROL --> COMPLETED: Thread resolved
    COMPLETED --> [*]
```

### 4. Use Case Diagram — All Agent Functionalities

```mermaid
flowchart LR
    USER([Human User])
    
    subgraph FEATURES [System Capabilities]
        direction TB
        F1[📬 Monitor Inbox]
        F2[🧠 Classify Emails]
        F3[🔥 Detect Leads]
        F4[✏️ Generate Drafts]
        F5[✅ Approve / Reject]
        F6[📤 Send Replies]
        F7[👤 Take Over Conversation]
        F8[🤖 Re-enable AI]
        F9[🔄 Auto Follow-ups]
        F10[📊 View Analytics]
        F11[📋 Daily Summary]
        F12[🔐 Rate Limit Sending]
        F13[🏷️ Filter Inbox]
        F14[⏹️ Stop Follow-ups]
    end
    
    USER --- F1
    USER --- F2
    USER --- F3
    USER --- F4
    USER --- F5
    USER --- F6
    USER --- F7
    USER --- F8
    USER --- F9
    USER --- F10
    USER --- F11
    USER --- F12
    USER --- F13
    USER --- F14
    
    subgraph AI [AI Performs]
        AI1[Classify Intent]
        AI2[Extract Lead Data]
        AI3[Generate Draft]
        AI4[Generate Follow-up]
        AI5[Summarize Thread]
    end
    
    subgraph TRIGGERS [Automated Triggers]
        T1[New email arrives]
        T2[No reply in 3 days]
        T3[Contact replies]
        T4[Daily at 8 AM]
        T5[Human takes over]
    end
    
    AI1 --> F2
    AI2 --> F3
    AI3 --> F4
    AI4 --> F9
    T1 --> F1
    T2 --> F9
    T3 --> F14
    T4 --> F11
    T5 --> F7
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
