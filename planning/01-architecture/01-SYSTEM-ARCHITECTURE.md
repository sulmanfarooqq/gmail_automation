# System Architecture

## High-Level Architecture

```
                    ┌──────────────────────────┐
                    │       Gmail API          │
                    │   (Client's Inbox)       │
                    └──────────┬───────────────┘
                               │
                    Google Pub/Sub (Watch)
                               │
                    ┌──────────▼───────────────┐
                    │   Email Ingestion        │
                    │   Service                │
                    │   (Polling + Webhook)    │
                    └──────────┬───────────────┘
                               │
                    ┌──────────▼───────────────┐
                    │   Email Processing       │
                    │   Pipeline               │
                    │   (Queue-based)          │
                    └──────────┬───────────────┘
                               │
                    ┌──────────▼───────────────┐
                    │   AI Intelligence         │
                    │   Layer                   │
                    │                           │
                    │   ┌─────────────────┐    │
                    │   │ Gemini / OpenAI │    │
                    │   │ / Anthropic     │    │
                    │   └─────────────────┘    │
                    └──────────┬───────────────┘
                               │
                    ┌──────────▼───────────────┐
                    │   Workflow Engine        │
                    │                           │
                    │   Trigger → Condition →   │
                    │   Action → Integration    │
                    └──────────┬───────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
   ┌──────────────┐   ┌──────────────┐   ┌────────────────┐
   │   CRM        │   │   Calendar   │   │   Dashboard    │
   │ (HubSpot/    │   │ (Google      │   │   & Analytics  │
   │  Salesforce) │   │  Calendar)   │   │                │
   └──────────────┘   └──────────────┘   └────────────────┘
          │                                          
          ▼                                          
   ┌──────────────┐                                   
   │ Follow-up    │                                   
   │ Engine       │                                   
   │ (BullMQ)     │                                   
   └──────────────┘                                   
```

## Service Architecture

```
┌─────────────────────────────────────────────────────┐
│                   API Gateway                        │
│              (Express.js + TypeScript)               │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │ Auth     │ │ Email   │ │ AI       │ │ Workfl │ │
│  │ Service  │ │ Service │ │ Service  │ │ Engine │ │
│  └──────────┘ └──────────┘ └──────────┘ └────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │ CRM     │ │ Calendar │ │ KB       │ │ Webhook│ │
│  │ Service │ │ Service  │ │ Service  │ │ Service│ │
│  └──────────┘ └──────────┘ └──────────┘ └────────┘ │
├─────────────────────────────────────────────────────┤
│                Background Workers (BullMQ)           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐ │
│  │ Email   │ │ AI       │ │ Followup │ │ Notifi │ │
│  │ Worker  │ │ Worker   │ │ Worker   │ │ Worker │ │
│  └──────────┘ └──────────┘ └──────────┘ └────────┘ │
└─────────────────────────────────────────────────────┘
```

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Backend Framework | Express.js + TypeScript | User's existing expertise, production-ready |
| Frontend | Next.js + TypeScript + Tailwind + shadcn/ui | Modern, fast, excellent DX |
| Database | PostgreSQL + Prisma ORM | Reliable, great multi-tenancy support, migrations |
| Queue | Redis + BullMQ | Persistent queues, delayed jobs, rate limiting |
| AI Layer | Multi-provider (Gemini/OpenAI/Anthropic) | No vendor lock-in, fallback, cost optimization |
| File Storage | S3-compatible (Cloudflare R2) | No egress fees, S3 API compatible |
| Background Jobs | BullMQ Workers | Scheduled follow-ups, delayed processing |
| Real-time | WebSocket (Socket.io) | Live inbox updates, notification delivery |
| Search | PostgreSQL full-text search (initially) → Meilisearch later | Simpler initial setup, upgrade later |

## Multi-Tenancy Architecture

```
Platform
   │
   ├── Agency A (organization_id = 1)
   │     ├── Users (admin, agent, viewer roles)
   │     ├── Gmail Accounts (multiple per agency)
   │     ├── Emails (all synced emails)
   │     ├── AI Config (model, tone, rules)
   │     ├── Knowledge Base (services, pricing, FAQs)
   │     ├── Workflows (custom automation rules)
   │     ├── CRM Config (HubSpot API key etc.)
   │     ├── Calendar Config (Google Calendar)
   │     └── Branding (logo, colors for white-label)
   │
   └── Agency B (organization_id = 2)
         └── ...same structure...
```

**Critical Rule**: Every database query MUST filter by `organization_id`. Never allow cross-organization data access.

## Data Flow (End-to-End)

```
1. Google sends Pub/Push notification → Webhook endpoint
2. Ingestion service fetches email via Gmail API (thread + message)
3. Email stored with raw + parsed content in DB
4. Job queued to AI Processing Worker
5. AI classifies intent, extracts data, detects lead
6. Workflow engine evaluates rules against classified email
7. Actions executed: CRM upsert, reply drafted, notification sent
8. Human reviews draft in dashboard → Approve/Edit/Reject
9. Approved email sent via Gmail API
10. Follow-up scheduled if no response within N days
```

## Rate Limiting & Quota Management

| Service | Limit | Strategy |
|---------|-------|----------|
| Gmail API Read | 250 quota units/user/sec | Queue + backoff + batch |
| Gmail API Send | 100 messages/user/sec | Queue + rate limit |
| AI Provider | Varies by provider | Token bucket per agency |
| Google Pub/Sub | 1000/sec per project | Auto-scaling workers |
