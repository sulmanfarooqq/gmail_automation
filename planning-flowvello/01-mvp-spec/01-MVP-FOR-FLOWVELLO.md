# MVP Spec — FlowVello Gmail Agent

## What This Product Does

A Gmail inbox assistant for **FlowVello** (and later, other Pakistani agencies/service businesses) that:

1. Reads incoming emails
2. Classifies them (lead, support, inquiry, etc.)
3. Generates AI draft replies
4. Lets human approve/edit/send
5. Follows up automatically when no reply
6. Gives you a dashboard of everything

## FlowVello's Own Use Case

```
flowvello@gmail.com (or flowvello@yourdomain.com)
    │
    ├── Client inquiries → Classify → AI draft → You approve → Send
    ├── Service requests → Detect urgency → Notify you
    ├── Partnership offers → Flag for review
    ├── Follow-ups unpaid → Auto-reminder sequence
    └── Daily summary → "You have 3 new leads, 2 urgent emails"
```

## MVP Feature List (Build These Only)

### Core (Must Have — Week 1)

| # | Feature | Why |
|---|---------|-----|
| 1 | Gmail OAuth login | Connect FlowVello's Gmail |
| 2 | Fetch emails via Gmail API | Read inbox |
| 3 | Email classification (AI) | Lead vs Support vs Other |
| 4 | Simple inbox view | See all emails in dashboard |
| 5 | AI draft reply | One-click draft generation |
| 6 | Approve/edit/send reply | Human-in-the-loop |
| 7 | Basic auth (email + password) | Secure your dashboard |

### Automation (Week 2)

| # | Feature | Why |
|---|---------|-----|
| 8 | Follow-up reminder | "No reply in 3 days → notify" |
| 9 | Lead detection | Extract name, phone, service requested |
| 10 | Simple knowledge base | "What services does FlowVello offer?" |
| 11 | Email labels/tags | Lead, Client, Support, Completed |

### Dashboard (Week 3)

| # | Feature | Why |
|---|---------|-----|
| 12 | Overview stats | Emails today, leads, pending drafts |
| 13 | Draft queue | All AI drafts awaiting approval |
| 14 | Basic analytics | Emails processed, response time |

## What's NOT in MVP

- ❌ Multi-tenant (add when you have 2+ clients)
- ❌ CRM integration (add when clients ask)
- ❌ Calendar booking (Phase 2)
- ❌ WhatsApp integration (keep your existing product separate)
- ❌ Public API
- ❌ Team roles
- ❌ Billing/subscriptions

## Tech Stack (For This MVP)

| Layer | Choice | Why |
|-------|--------|-----|
| Backend | Express.js + TypeScript | You wanted this |
| Frontend | Next.js + Tailwind + shadcn/ui | Same reason |
| Database | PostgreSQL + Prisma | Reliable, free on Heroku |
| AI | Gemini Flash | Cheapest, good enough |
| Queue | BullMQ + Redis | Follow-ups + background jobs |
| Auth | JWT + bcrypt | Simple, no third-party |
| Email | Gmail API + Google Pub/Sub | Official, reliable |
| Hosting | Heroku Eco | $7/mo |
| Domain | flowvello.com (or subdomain) | Professional look |

## Build Order (Day by Day)

```
Day 1-2:  Project setup, database, auth, basic Express + Next.js
Day 3-4:  Google OAuth, Gmail API, fetch + store emails
Day 5-6:  AI classification (Gemini), email parsing, inbox view
Day 7-8:  AI draft generation, approve/send flow
Day 9-10: Follow-up system (BullMQ scheduled jobs)
Day 11:   Knowledge base, lead detection
Day 12:   Dashboard, analytics, polish
Day 13:   Deploy to Heroku, test with real FlowVello emails
Day 14:   Bug fixes, invite 1 beta user
```

**Total: 14 days to a working product you can use and demo.**
