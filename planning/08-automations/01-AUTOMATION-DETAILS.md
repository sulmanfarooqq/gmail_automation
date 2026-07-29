# 10 Core Automations — Detailed Implementation

## Automation 1: AI Email Classification

**Purpose**: Every incoming email is automatically classified before any action.

**Implementation**:
- Trigger: `email_received`
- Action: Call AI classification endpoint
- Store: `EmailClassification` record
- Fallback: If AI fails, classify as "other", flag for manual review
- Accuracy tracking: Store human override → retrain/improve prompts

**Classification Categories**: lead, customer_support, sales_inquiry, billing, complaint, partnership, newsletter, spam, internal, meeting_request, other

---

## Automation 2: AI Lead Detection

**Purpose**: Detect sales opportunities automatically.

**Detection Signals**:
- Keywords: "website", "development", "automation", "agency", "service"
- Intent patterns: "we need", "we're looking for", "do you offer"
- Company name mentioned
- Phone number included
- Sentiment + urgency combined

**Actions**: Create CRM lead → assign to available salesperson → notify → schedule follow-up

---

## Automation 3: AI Reply Drafting (MVP Feature)

**Purpose**: Generate context-aware draft replies for human approval.

**Input Context**:
1. Incoming email body + subject
2. Previous messages in thread (conversation history)
3. Company knowledge base (services, tone, FAQs)
4. Classification result (intent, priority)
5. Sender's CRM data (if known)

**Output**: Draft reply with:
- Suggested subject line
- Body text with proper greeting/signature
- Tone indicator
- Confidence score
- Whether approval is needed

---

## Automation 4: Auto Reply (Low-Risk Only)

**Rules Engine**:
```
ALWAYS require approval:
  - Pricing questions
  - Contract terms
  - Refunds/complaints
  - Legal matters
  - Sensitive topics
  - First contact from unknown sender

CAN auto-send:
  - FAQ answers from knowledge base
  - "Do you offer X?" → "Yes, here's info"
  - "What are your hours?"
  - "Where are you located?"
  - Confirmation of receipt
```

---

## Automation 5: Lead Follow-up Sequence

**Default Sequence** (configurable):
```
Day 0: Lead arrives → AI replies
Day 2: No response → Follow-up: "Just checking in..."
Day 5: No response → Follow-up: Value-add content
Day 10: No response → Final: "Last chance to connect"
Day 14: No response → Mark as cold, notify sales
```

**Configuration per agency**:
- Number of steps (1-10)
- Delay between steps (hours/days)
- Custom email templates per step
- Stop on reply (auto-detect response)
- Assign to specific team member after N steps

---

## Automation 6: Meeting Booking

**Flow**:
```
Client: "Can we schedule a call next week?"
    │
    ▼
AI detects meeting intent
    │
    ▼
Check Google Calendar availability (next 7 days)
    │
    ▼
Generate time slot options (3-4 options)
    │
    ▼
Send to client with calendar links
    │
    ▼
Client clicks → Calendar event created
    │
    ▼
Confirmation + Zoom/Google Meet link generated
```

**Calendar Integration**:
- Read: Check existing events for conflicts
- Write: Create events with Meet/Zoom links
- Configurable duration (15/30/45/60 min)
- Buffer time between meetings
- Multiple calendars (personal + team)

---

## Automation 7: Email → Task Creation

**Detection**:
- "Please send me..." → Task: Send X by Y
- "Can you prepare..." → Task: Prepare X by Y
- "I need this by Friday" → Due date extraction

**Task Fields**:
- Title (from email subject/body)
- Description (email body summary)
- Due date (extracted or N days from now)
- Assignee (from workflow or AI suggestion)
- Priority (from email priority)
- Source email link

---

## Automation 8: Attachment Intelligence

**Document Types**:
- Invoice → Extract amount, due date, vendor → Notify finance
- Contract → Extract parties, dates, terms → Save for review
- Proposal → Extract scope, pricing → Forward to sales
- Resume/CV → Extract skills, experience → Forward to HR

**Processing**:
```typescript
// For PDFs: Use pdf-parse or Gemini Vision
// For images: Use OCR via AI provider
// For Office docs: Convert to text, then AI extract
// Store extracted data as JSON in Attachment model
```

---

## Automation 9: Customer Support

**Triage Logic**:
```
Intent = Support
    │
    ▼
Search Knowledge Base for matching FAQ
    │
    ├── Match found (confidence > 90%)
    │     → Auto-reply (if allowed)
    │     → Draft reply for approval
    │
    ├── Match found (confidence 70-90%)
    │     → Draft reply, flag "verify answer"
    │
    └── No match
          → Draft reply: "Let me connect you..."
          → Assign to support agent
          → Create support ticket
```

---

## Automation 10: Daily AI Summary

**Generation**: Scheduled job at configurable time (default: 8 AM)

**Content**:
```
Subject: Daily Email Summary — {org_name}

Good morning, {team_name}

📊 Today's Summary:
├── {count} new emails processed
├── {count} new leads detected (worth ${estimated_value})
├── {count} urgent emails
├── {count} support requests
├── {count} pending AI drafts (awaiting approval)
└── {count} unanswered emails (older than 24h)

🔥 Top Priorities:
1. {sender} — {subject} ({priority})
2. {sender} — {subject} ({priority})
3. {sender} — {subject} ({priority})

⚡ Quick Actions:
• Review {count} pending drafts
• Respond to {count} urgent emails
• Follow up on {count} old leads

📈 Yesterday vs Last Week:
• Emails: +{percent}%
• Leads: +{percent}%
• Response time: {time} faster
```

**Delivery**: In-app notification + email + optional Slack webhook

**Purpose**: Agency owners immediately see the pulse of their email operations.
