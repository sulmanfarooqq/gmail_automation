# Phase 3: Admin Panel Specification

## Objective
Build platform admin dashboard to manage tenants, domains, mailboxes, users, and monitor system health - all without touching the server manually.

## Tech Stack
- Next.js 14+ (App Router) - separate app in monorepo
- Same UI stack as webmail (Tailwind, shadcn/ui, tRPC)
- Role-based access: super-admin, support, billing

## Application Structure

apps/admin/
|-- app/
|   |-- (auth)/
|   |   |-- login/page.tsx
|   |-- (platform)/
|   |   |-- layout.tsx
|   |   |-- dashboard/page.tsx        # Overview metrics
|   |   |-- tenants/
|   |   |   |-- page.tsx              # List + create tenant
|   |   |   |-- [id]/page.tsx         # Tenant detail
|   |   |   |-- [id]/domains/page.tsx
|   |   |   |-- [id]/mailboxes/page.tsx
|   |   |   |-- [id]/users/page.tsx
|   |   |   |-- [id]/settings/page.tsx
|   |   |   |-- [id]/usage/page.tsx
|   |   |   |-- [id]/logs/page.tsx
|   |   |   |-- [id]/billing/page.tsx
|   |-- (monitoring)/
|   |   |-- page.tsx                  # Server health
|   |   |-- email-volume/page.tsx
|   |   |-- spam/page.tsx
|   |   |-- deliverability/page.tsx
|   |   |-- queue/page.tsx
|   |-- (billing)/
|   |   |-- page.tsx                  # Subscriptions
|   |   |-- invoices/page.tsx
|   |   |-- plans/page.tsx
|   |-- components/
|-- trpc/routers/
|   |-- tenant.ts
|   |-- domain.ts
|   |-- mailbox.ts
|   |-- user.ts
|   |-- monitoring.ts
|   |-- billing.ts

## Core Features

### 1. Tenant Management
- Create tenant (name, slug, plan, admin email)
- Tenant status: active, suspended, trial, cancelled
- Impersonate tenant (super-admin only)
- Tenant usage: mailboxes, storage, AI calls, API calls
- Tenant limits enforcement (plan-based)

### 2. Domain Management
- Add domain to tenant
- DNS verification wizard (checks MX, SPF, DKIM, DMARC, PTR)
- Auto-generate DKIM keys
- Domain status: pending, verified, active, failed
- Custom DKIM selector support

### 3. Mailbox Management
- Create/edit/delete mailboxes per domain
- Set quotas (storage, daily send limit)
- Password reset / generate app passwords
- Alias management
- Mailbox status: active, suspended, full

### 4. User Management
- Platform users (super-admin, support, billing)
- Tenant users (owner, admin, user)
- Role assignments
- MFA enforcement
- Session management (revoke all)

### 5. Monitoring Dashboard
- Real-time: queue size, active connections, memory/CPU
- Email volume: sent/received/bounced/complained (per tenant, per domain)
- Spam stats: caught, false positives, false negatives
- Deliverability: inbox placement, reputation scores
- Alerts: queue backlog, high bounce rate, blacklist detection

### 6. Billing & Plans
- Plan definitions: Basic, Business, Sales, Automation, Enterprise
- Features per plan: mailboxes, storage, AI calls, automation runs, CRM, WhatsApp
- Usage tracking with overage alerts
- Stripe integration for subscriptions
- Invoice generation

## tRPC Procedures (Examples)

### tenant.router.ts


### domain.router.ts


## DNS Verification Wizard (Multi-step)

Step 1: Enter domain name
Step 2: Show required DNS records (with copy buttons)
Step 3: Verify button -> runs checks
Step 4: If all pass -> activate, else show failures with fix instructions
Step 5: Generate DKIM key -> show public key for DNS

## Security
- All routes require super-admin or support role
- Audit log for all mutations (who, what, when, before/after)
- IP allowlist for admin panel access
- Session timeout: 30 min
- MFA required for super-admin

## Timeline: 2-3 Weeks

| Week | Focus |
|------|-------|
| 1 | Tenant CRUD, domain wizard, mailbox management |
| 2 | User management, monitoring dashboard, billing |
| 3 | Impersonation, audit logs, alerts, testing |
