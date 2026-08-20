# Phase 8: Multi-Tenant SaaS Platform Specification

## Objective
Build complete SaaS platform: client onboarding, subscription billing, usage limits, tenant isolation, white-label branding.

## Tech Stack
- Stripe for billing/subscriptions
- Next.js (admin + client-portal)
- PostgreSQL RLS for isolation
- Feature flags per plan

## Data Model

```sql
-- Plans
CREATE TABLE plans (
    id UUID PRIMARY KEY,
    name VARCHAR(50) UNIQUE,  -- basic, business, sales, automation, enterprise
    display_name VARCHAR(100),
    description TEXT,
    monthly_price_cents INTEGER,
    yearly_price_cents INTEGER,
    features JSONB,  -- {mailboxes: 10, storage_gb: 50, ai_calls_month: 10000, ...}
    limits JSONB,    -- {max_mailboxes: 50, max_domains: 5, ...}
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER
);

-- Subscriptions
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id) UNIQUE,
    plan_id UUID REFERENCES plans(id),
    stripe_subscription_id VARCHAR(100),
    stripe_customer_id VARCHAR(100),
    status VARCHAR(20),  -- trialing, active, past_due, cancelled, paused
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    trial_end TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Usage tracking (aggregated daily)
CREATE TABLE usage_records (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    date DATE NOT NULL,
    metric VARCHAR(50) NOT NULL,  -- emails_sent, emails_received, storage_bytes, ai_calls, workflow_runs, api_calls
    value BIGINT DEFAULT 0,
    UNIQUE (tenant_id, date, metric)
);

-- Invoices
CREATE TABLE invoices (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    stripe_invoice_id VARCHAR(100),
    amount_cents INTEGER,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(20),  -- draft, open, paid, void, uncollectible
    period_start TIMESTAMPTZ,
    period_end TIMESTAMPTZ,
    pdf_url VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Tenant branding
CREATE TABLE tenant_branding (
    tenant_id UUID PRIMARY KEY REFERENCES tenants(id),
    logo_light_url VARCHAR(500),
    logo_dark_url VARCHAR(500),
    primary_color VARCHAR(7),  -- #hex
    secondary_color VARCHAR(7),
    font_family VARCHAR(100),
    custom_domain VARCHAR(255),  -- mail.clientdomain.com
    custom_domain_verified BOOLEAN DEFAULT FALSE,
    login_page_html TEXT,  -- Custom HTML for login
    email_header_html TEXT,
    email_footer_html TEXT,
    favicon_url VARCHAR(500),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Onboarding progress
CREATE TABLE onboarding_steps (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    step VARCHAR(50) NOT NULL,  -- dns, dkim, mailboxes, kb, ai, workflows, crm, whatsapp
    status VARCHAR(20) DEFAULT 'pending',  -- pending, in_progress, completed, skipped
    completed_at TIMESTAMPTZ,
    data JSONB,
    UNIQUE (tenant_id, step)
);
```

## Plan Definitions

| Feature | Basic | Business | Sales | Automation | Enterprise |
|---------|-------|----------|-------|------------|------------|
| Mailboxes | 5 | 25 | 50 | 100 | Unlimited |
| Storage | 5 GB | 50 GB | 100 GB | 200 GB | 1 TB |
| Domains | 1 | 3 | 5 | 10 | Unlimited |
| Users | 3 | 10 | 25 | 50 | Unlimited |
| AI Calls/mo | 1,000 | 10,000 | 50,000 | 100,000 | 500,000 |
| Workflow Runs/mo | - | 1,000 | 10,000 | 50,000 | Unlimited |
| CRM | - | Basic | Full | Full | Full |
| WhatsApp | - | - | - | 1 channel | 5 channels |
| Voice | - | - | - | - | Yes |
| Custom Branding | - | - | - | Yes | Yes |
| Custom Domain | - | - | - | Yes | Yes |
| SLA | - | - | 99.9% | 99.9% | 99.99% |
| Support | Email | Email+Chat | Priority | Priority | Dedicated |

**Pricing (example):**
- Basic: $5/mailbox/mo
- Business: $15/mailbox/mo
- Sales: $30/mailbox/mo
- Automation: $50/mailbox/mo
- Enterprise: Custom

## Client Onboarding Flow

```
1. Signup (company name, admin email, password)
   -> Create tenant + admin user + trial subscription (14 days)
   
2. Domain Setup Wizard
   -> Enter domain
   -> Show DNS records (A, MX, SPF, DKIM, DMARC, PTR)
   -> Verify button (checks DNS)
   -> Auto-generate DKIM keys
   
3. Mailbox Creation
   -> Suggest: info@, sales@, support@
   -> Create mailboxes
   -> Set quotas
   
4. Knowledge Base Setup
   -> Upload: Services, Pricing, FAQs, Policies, Team
   -> Auto-chunk + embed
   -> Test search
   
5. AI Configuration
   -> Enable: Lead Detection, Auto-Followup, Sentiment, Classification
   -> Set approval level: Suggest / Auto-safe / Autonomous
   -> Test with sample emails
   
6. CRM Setup (Sales+ plans)
   -> Pipeline stages
   -> Custom fields
   -> Import contacts
   
7. Automation Setup (Automation+ plans)
   -> Select workflow templates: Lead, Support, Appointment, Quote
   -> Customize per business
   -> Test run
   
8. WhatsApp Setup (Automation+ plans)
   -> Connect WhatsApp Business Account
   -> Verify phone number
   -> Create templates
   
9. Branding (Automation+ plans)
   -> Upload logos
   -> Set colors
   -> Configure custom domain (CNAME)
   
10. Go Live
    -> Switch DNS to production
    -> Send test emails
    -> Enable billing
```

## Billing Integration (Stripe)

### 1. Checkout
```typescript
// Create checkout session for plan upgrade
const session = await stripe.checkout.sessions.create({
  customer: tenant.stripe_customer_id,
  mode: 'subscription',
  line_items: [{ price: plan.stripe_price_id, quantity: mailboxes }],
  success_url: `${appUrl}/billing?success=true`,
  cancel_url: `${appUrl}/billing?canceled=true`,
  subscription_data: {
    trial_period_days: 14,
    metadata: { tenant_id: tenant.id },
  },
});
```

### 2. Webhook Handlers
```typescript
// stripe-webhook.ts
switch (event.type) {
  case 'customer.subscription.created':
  case 'customer.subscription.updated':
    await syncSubscription(event.data.object);
    break;
  case 'customer.subscription.deleted':
    await cancelSubscription(event.data.object);
    break;
  case 'invoice.payment_failed':
    await handlePaymentFailed(event.data.object);
    break;
  case 'invoice.paid':
    await createInvoiceRecord(event.data.object);
    break;
}
```

### 3. Usage-Based Billing (for overages)
- Track daily usage per metric
- At period end, calculate overages
- Create invoice items for overages
- Alert at 80%, 100% of limits

## Usage Enforcement

```typescript
// Middleware on all API routes
async function enforceLimits(tenantId: string, metric: string, increment: number = 1) {
  const subscription = await getSubscription(tenantId);
  const plan = await getPlan(subscription.plan_id);
  const limit = plan.limits[metric];
  
  if (limit === -1) return; // Unlimited
  
  const current = await getUsageThisMonth(tenantId, metric);
  if (current + increment > limit) {
    if (subscription.plan !== 'enterprise') {
      throw new LimitExceededError(metric, limit, current);
    }
    // Enterprise: allow but track overage
  }
  
  await incrementUsage(tenantId, metric, increment);
}
```

## Tenant Isolation (Security)

1. **Database**: RLS on every table (enforced at DB level)
2. **API**: Middleware extracts tenant_id from JWT, sets `app.current_tenant_id`
3. **File Storage**: MinIO paths prefixed with `tenant/{tenant_id}/`
4. **AI/KB**: Vector search filtered by tenant_id
5. **Queue**: Redis streams namespaced `tenant:{tenant_id}:{stream}`
6. **Mailu**: Separate virtual domains per tenant
7. **Admin Impersonation**: Audit-logged, time-limited, requires MFA

## White-Label Branding

- Custom login page (HTML/CSS injection)
- Custom email headers/footers
- Custom domain: `mail.clientdomain.com` -> CNAME to platform
- TLS for custom domains (Let's Encrypt wildcard or customer cert)
- Favicon, logos, colors applied via CSS variables
- Email templates use tenant branding variables

## Admin Features

- Tenant search/filter/sort
- Impersonate tenant (with audit)
- Override limits (support)
- Manual invoice/adjustment
- Pause/resume subscription
- Export tenant data (GDPR)
- Delete tenant 
