# API Design — Express.js Routes

## Base URL: `/api/v1`

## Authentication

All routes (except `/auth/*` and `/webhooks/*`) require:
- Header: `Authorization: Bearer <session_token>`
- Middleware validates session + extracts `organization_id`

---

## Auth Routes

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/auth/register` | Create organization + admin user |
| POST | `/auth/login` | Login, return session token |
| POST | `/auth/logout` | Invalidate session |
| POST | `/auth/refresh` | Refresh session token |
| POST | `/auth/forgot-password` | Send reset email |
| POST | `/auth/reset-password` | Reset password with token |

---

## Organization Routes

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/organizations/me` | Get current org details |
| PATCH | `/organizations/me` | Update org settings |
| PATCH | `/organizations/me/branding` | Update white-label branding |
| GET | `/organizations/me/billing` | Get billing info |
| PATCH | `/organizations/me/billing` | Update billing info |

---

## User Routes

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/users` | List org users |
| POST | `/users/invite` | Invite team member |
| PATCH | `/users/:id` | Update user (admin only) |
| DELETE | `/users/:id` | Remove user (admin only) |
| PATCH | `/users/me` | Update own profile |

---

## Gmail Account Routes

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/gmail/auth-url` | Get Google OAuth URL |
| POST | `/gmail/callback` | Handle OAuth callback |
| GET | `/gmail/accounts` | List connected accounts |
| DELETE | `/gmail/accounts/:id` | Disconnect account |
| POST | `/gmail/accounts/:id/sync` | Force sync |
| GET | `/gmail/accounts/:id/status` | Get sync status |

---

## Email Routes

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/emails` | List emails (paginated, filtered) |
| GET | `/emails/:id` | Get single email (full details) |
| GET | `/emails/:id/thread` | Get full thread |
| DELETE | `/emails/:id` | Soft-delete (GDPR) |
| PATCH | `/emails/:id/read` | Mark as read/unread |
| POST | `/emails/batch` | Batch operations (archive, delete, label) |

---

## Email Classification Routes

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/emails/:id/classification` | Get AI classification |
| POST | `/emails/:id/reclassify` | Force re-classification |
| PATCH | `/emails/:id/classification` | Human override classification |

---

## AI Draft Routes

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/emails/:id/draft` | Get AI draft (or generate if not exists) |
| PUT | `/emails/:id/draft` | Save edited draft |
| POST | `/emails/:id/draft/regenerate` | Regenerate with new instructions |
| POST | `/emails/:id/draft/approve` | Approve draft |
| POST | `/emails/:id/draft/reject` | Reject with reason |
| POST | `/emails/:id/draft/send` | Send approved draft |

---

## Knowledge Base Routes

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/knowledge-base` | Get KB for current org |
| PUT | `/knowledge-base` | Update KB |
| GET | `/knowledge-base/faqs` | List FAQs |
| POST | `/knowledge-base/faqs` | Add FAQ |
| PATCH | `/knowledge-base/faqs/:id` | Update FAQ |
| DELETE | `/knowledge-base/faqs/:id` | Delete FAQ |
| GET | `/knowledge-base/case-studies` | List case studies |
| POST | `/knowledge-base/case-studies` | Add case study |
| GET | `/knowledge-base/team-members` | List team members |
| POST | `/knowledge-base/team-members` | Add team member |
| DELETE | `/knowledge-base/team-members/:id` | Remove team member |

---

## Workflow Routes

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/workflows` | List workflows |
| POST | `/workflows` | Create workflow |
| GET | `/workflows/:id` | Get workflow |
| PATCH | `/workflows/:id` | Update workflow |
| DELETE | `/workflows/:id` | Delete workflow |
| POST | `/workflows/:id/toggle` | Activate/deactivate |
| POST | `/workflows/:id/test` | Test with sample email |
| GET | `/workflows/:id/executions` | Get execution history |

---

## Follow-up Routes

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/follow-ups` | List sequences |
| POST | `/follow-ups` | Create sequence |
| PATCH | `/follow-ups/:id` | Update sequence |
| DELETE | `/follow-ups/:id` | Delete sequence |
| POST | `/follow-ups/:id/stop` | Stop active sequence |
| GET | `/follow-ups/:id/executions` | Execution history |

---

## CRM Routes

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/crm/config` | Get CRM connection config |
| POST | `/crm/config` | Connect/update CRM |
| DELETE | `/crm/config` | Disconnect CRM |
| POST | `/crm/sync` | Force manual sync |
| GET | `/crm/contacts` | List CRM contacts |
| GET | `/crm/contacts/:id` | Get CRM contact detail |
| GET | `/crm/activities` | List CRM activities |
| POST | `/crm/test` | Test CRM connection |

---

## Calendar Routes

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/calendar/auth-url` | Get Google Calendar OAuth URL |
| POST | `/calendar/callback` | Handle OAuth callback |
| GET | `/calendar/config` | Get calendar settings |
| PATCH | `/calendar/config` | Update calendar settings |
| POST | `/calendar/check-availability` | Check available slots |
| POST | `/calendar/book` | Book a meeting |

---

## Task Routes

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/tasks` | List tasks |
| POST | `/tasks` | Create manual task |
| PATCH | `/tasks/:id` | Update task |
| POST | `/tasks/:id/assign` | Assign to user |
| POST | `/tasks/:id/complete` | Mark complete |

---

## Notification Routes

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/notifications` | List notifications |
| POST | `/notifications/read` | Mark all as read |
| PATCH | `/notifications/:id` | Mark single as read |
| GET | `/notifications/unread-count` | Get unread count |

---

## Analytics Routes

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/analytics/overview` | Dashboard overview stats |
| GET | `/analytics/emails` | Email volume analytics |
| GET | `/analytics/leads` | Lead generation analytics |
| GET | `/analytics/response-time` | Response time metrics |
| GET | `/analytics/ai-accuracy` | AI accuracy metrics |
| GET | `/analytics/time-saved` | Time saved estimation |

---

## Webhook Routes

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/webhooks/gmail` | Google Pub/Sub push endpoint |
| POST | `/webhooks/crm` | CRM webhook handler |
| POST | `/webhooks/stripe` | Stripe webhook handler |

---

## Search Route

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/search` | Full-text search across emails |
| Query params | `q`, `from`, `to`, `subject`, `date_from`, `date_to`, `intent`, `has_attachments`, `page`, `limit` |

---

## Health & Monitoring

| Method | Route | Description |
|--------|-------|-------------|
| GET | `/health` | Basic health check |
| GET | `/health/ready` | Readiness check (DB, Redis, AI provider) |
| GET | `/metrics` | Prometheus metrics endpoint |

---

## API Versioning

- Current: `v1`
- Breaking changes → increment version (v2)
- Backward-compatible changes → additive within version
- Maintain at least 1 version back for 6 months
- Include deprecation header: `Deprecation: true`
