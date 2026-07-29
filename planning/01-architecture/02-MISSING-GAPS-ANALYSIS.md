# CRITICAL: Gaps & Missing Items in Original Plan

This document identifies what the gmail.txt plan missed. These must be addressed before production.

---

## 🔴 HIGH PRIORITY — Must Have for MVP

| # | Gap | Why It Matters |
|---|-----|----------------|
| 1 | **Email Threading** | Gmail uses threads. Without thread-level conversation context, AI generates replies that ignore previous messages. Entire conversation history must be tracked. |
| 2 | **OAuth Token Refresh** | Google access tokens expire after 1 hour. Without robust, silent refresh + retry, the system silently breaks after 60 minutes. |
| 3 | **Email Deduplication** | Gmail Push + Polling can deliver the same email twice. Need idempotency keys / historyId tracking. |
| 4 | **Concurrent Send Locking** | Two workers can approve + send the same draft simultaneously. Need row-level locks or Redis locks. |
| 5 | **Rate Limiting Strategy** | Gmail API: 250 quota units/user/sec. AI providers have strict limits. Without rate limiting, you get 429 errors and data loss. |
| 6 | **Error Handling + Retry** | Gmail API fails. AI goes down. Redis goes down. Every external call needs retry with exponential backoff + dead letter queue. |

## 🟡 MEDIUM PRIORITY — Phase 2 / Agency Ready

| # | Gap | Why It Matters |
|---|-----|----------------|
| 7 | **SPF/DKIM/DMARC** | Emails sent via Gmail API need proper authentication. Without it, replies go to spam. Agencies will blame you. |
| 8 | **Unsubscribe Handling** | CAN-SPAM law requires opt-out mechanism. Automated follow-ups need List-Unsubscribe headers. |
| 9 | **GDPR / Data Compliance** | Agencies handle client data. Need data retention policies, export, delete, consent tracking. |
| 10 | **Email Search** | Agencies process hundreds of emails/day. Without search (full-text, by sender, by date, by intent), the dashboard is useless. |
| 11 | **Notification Architecture** | How does the team know a lead arrived? In-app, email, Slack, push? The original plan doesn't specify. |
| 12 | **Onboarding Flow** | An agency needs to set up: Google OAuth → knowledge base → workflows → team members. No onboarding = churn. |

## 🟢 LOWER PRIORITY — Phase 3 / SaaS Polish

| # | Gap | Why It Matters |
|---|-----|----------------|
| 13 | **White-labeling** | Agencies want to resell this as their own product. Needs custom domain, logo, branding per agency. |
| 14 | **Audit Logs** | Every action (approve, reject, edit, send) needs to be logged with actor, timestamp, and previous state. |
| 15 | **API Versioning** | If you expose a public API, versioning is non-negotiable. Start with `/api/v1/` pattern. |
| 16 | **Data Retention** | Old emails, logs, drafts need cleanup policies. Automate archival/deletion. |
| 17 | **Monitoring + Alerting** | Workers die, queues back up, AI returns errors. Need health checks, metrics, and PagerDuty/Slack alerts. |
| 18 | **CI/CD Pipeline** | No deployment strategy = fragile releases. Need automated testing + staging + production pipeline. |
| 19 | **Database Migrations** | Prisma migrations need to run in CI/CD. Never run migrations manually on production. |
| 20 | **Backup Strategy** | Daily PostgreSQL backups, point-in-time recovery, S3 backup for attachments. |
| 21 | **Email Template Variables** | Follow-ups need dynamic placeholders: `{{client_name}}`, `{{service}}`, `{{meeting_link}}`. |
| 22 | **Multi-language Support** | Agencies serve diverse clients. AI instructions should support language detection + response in same language. |
| 23 | **Attachment Size Limits** | Gmail allows 25MB. What's your limit? How do you handle large attachments? |

## Missing Functions/Endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /api/v1/webhooks/gmail` | Google Pub/Sub push endpoint |
| `POST /api/v1/auth/refresh` | Force refresh Gmail token |
| `GET /api/v1/search` | Full-text email search |
| `POST /api/v1/emails/:id/thread` | Get full thread context |
| `DELETE /api/v1/emails/:id` | Soft-delete (GDPR compliance) |
| `GET /api/v1/organization/branding` | White-label settings |
| `POST /api/v1/emails/batch` | Batch operations |
| `GET /api/v1/health` | Health check endpoint |
| `GET /api/v1/metrics` | Prometheus metrics |
| `POST /api/v1/workflows/test` | Test workflow against sample email |
