# AI Business Mailbox - Project Overview

## Vision
**One self-hosted, multi-tenant business email platform that gives any company its own professional mailbox and automatically handles routine email work.**

## Product Name
**AI Business Mailbox** (codename: Flowvello)

## Two-Layer Architecture

### Layer A — Email Infrastructure (Owned)
```
Domain → DNS → Mail Server (SMTP/IMAP/DKIM/SPF/DMARC/Spam/Malware/Storage) → Webmail
```

### Layer B — AI Automation (Value Differentiator)
```
Incoming Email → AI Agent → Understand → Classify → Extract → Decide Action
                                                    ↓
                    ┌─────────────┬──────────┬──────────┬─────────────┐
                    │ Reply       │ CRM      │ Task     │ Human       │
                    │             │ update   │ creation │ escalation  │
                    └─────────────┴──────────┴──────────┴─────────────┘
```

## Tech Stack Decisions (Finalized)

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Hosting** | Hetzner/Contabo VPS | Cost-effective, full control, good deliverability IPs |
| **Mail Server** | **Mailu** (Docker-based) | Pre-configured Postfix/Dovecot/Rspamd/ClamAV/OpenDKIM, battle-tested, excellent deliverability defaults |
| **Application** | Next.js 14+ (App Router), TypeScript, Node.js | Modern React framework, great DX, server components |
| **Database** | PostgreSQL 16+ | ACID, JSONB for flexible tenant data, row-level security |
| **Cache/Queue** | Redis 7+ (Valkey) | Pub/sub, queues, caching, rate limiting |
| **Object Storage** | MinIO (S3-compatible) | Self-hosted, attachments/backups |
| **AI Layer** | **Gemini API** (Google) | Cost-effective, large context, function calling |
| **Automation Engine** | **Python** (custom) | Full control, async, type-safe with Pydantic |
| **Container Orchestration** | Docker Compose (dev) → k3s (prod) | Simple start, Kubernetes migration path |
| **IaC** | Terraform + Ansible | Reproducible infrastructure |
| **Monitoring** | Prometheus + Grafana + Loki | Full observability stack |
| **CI/CD** | GitHub Actions → ArgoCD | GitOps deployment |

## Multi-Tenancy Model
```
AI Mail Platform
├── Tenant 001 (flowvello.com)
│   ├── domains: [flowvello.com]
│   ├── mailboxes: [contact@, sales@, support@]
│   ├── users: [admin@, john@]
│   ├── AI settings: {lead_detection: true, auto_followup: true}
│   ├── knowledge_base: {...}
│   └── workflows: [...]
├── Tenant 002 (dentist.com)
│   ├── domains: [dentist.com]
│   ├── mailboxes: [info@, appointments@]
│   ├── users: [...]
│   ├── AI settings: {...}
│   ├── knowledge_base: {...}
│   └── workflows: [...]
└── Tenant 003 (...)
```

**Every database object has `tenant_id` - enforced by PostgreSQL RLS policies.**

## Development Phases (8 Phases)

| Phase | Focus | Deliverable | Duration |
|-------|-------|-------------|----------|
| **1** | Mail Infrastructure | `contact@flowvello.com` sends/receives reliably | 2-3 weeks |
| **2** | Custom Webmail | Gmail-like inbox, compose, threads, contacts | 3-4 weeks |
| **3** | Admin Panel | Create tenants/domains/mailboxes without CLI | 2-3 weeks |
| **4** | AI Layer | Classification, summarization, reply drafting, KB | 3-4 weeks |
| **5** | Automation Engine | Triggers, conditions, actions, delays, webhooks | 3-4 weeks |
| **6** | CRM | Contacts, companies, leads, deals, pipeline | 2-3 weeks |
| **7** | Multi-channel | WhatsApp Business API integration | 2-3 weeks |
| **8** | SaaS Platform | Onboarding, billing, usage limits, branding | 3-4 weeks |

**Total estimated: 20-28 weeks (5-7 months)**

## Key Differentiators (Moat)
1. **Email infrastructure + AI + automation** in one platform
2. **Vertical configuration** via knowledge base + prompts + workflows (not code)
3. **Multi-tenant from day one** - onboard new clients without deployments
4. **Approval levels** (Suggest → Auto-send safe → Autonomous)
5. **Deliverability-first** - monitoring, rate limits, abuse detection built-in

## Non-Goals (Explicitly NOT Building)
- Gmail-level mobile apps (Phase 8+)
- Video meetings, Drive clone, Calendar clone, Office suite
- Custom SMTP/IMAP implementation
- Custom AI model training
- Complex collaboration features

## Success Criteria (Phase 1)
- [ ] `contact@flowvello.com` sends email → lands in Gmail inbox (not spam)
- [ ] Gmail sends to `contact@flowvello.com` → received in webmail
- [ ] SPF/DKIM/DMARC all pass (check via mail-tester.com score 10/10)
- [ ] TLS enforced, valid Let's Encrypt certs
- [ ] Rspamd spam filtering working
- [ ] ClamAV malware scanning working
- [ ] Daily encrypted backups to MinIO
