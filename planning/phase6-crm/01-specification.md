# Phase 6: CRM Specification

## Objective
Build lightweight CRM integrated with email: contacts, companies, leads, deals, pipeline, tasks, notes, activities.

## Tech Stack
- Next.js (client-portal app)
- tRPC + PostgreSQL (shared with webmail)
- Reuses authentication, tenancy, permissions

## Data Model

```sql
-- Contacts (people)
CREATE TABLE contacts (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    company_id UUID REFERENCES companies(id),
    phone VARCHAR(50),
    title VARCHAR(100),
    tags TEXT[],
    custom_fields JSONB,
    source VARCHAR(50),  -- email, manual, import, api, workflow
    owner_id UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Companies (organizations)
CREATE TABLE companies (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    name VARCHAR(255) NOT NULL,
    domain VARCHAR(255),
    industry VARCHAR(100),
    size VARCHAR(50),
    address JSONB,
    tags TEXT[],
    custom_fields JSONB,
    owner_id UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Leads (potential opportunities)
CREATE TABLE leads (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    contact_id UUID REFERENCES contacts(id),
    email_id UUID REFERENCES emails(id),
    status VARCHAR(30) DEFAULT 'new',  -- new, qualified, contacted, proposal, won, lost
    score INTEGER DEFAULT 0,
    source VARCHAR(50),
    owner_id UUID REFERENCES users(id),
    metadata JSONB,  -- Extracted from email: budget, timeline, requirements
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Deals (opportunities in pipeline)
CREATE TABLE deals (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    lead_id UUID REFERENCES leads(id),
    contact_id UUID REFERENCES contacts(id),
    company_id UUID REFERENCES companies(id),
    name VARCHAR(255) NOT NULL,
    value DECIMAL(12,2),
    currency VARCHAR(3) DEFAULT 'USD',
    stage_id UUID REFERENCES pipeline_stages(id),
    probability INTEGER DEFAULT 0,
    expected_close_date DATE,
    owner_id UUID REFERENCES users(id),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Pipeline stages (customizable per tenant)
CREATE TABLE pipeline_stages (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    name VARCHAR(100) NOT NULL,
    order_index INTEGER,
    probability INTEGER DEFAULT 0,
    is_closed BOOLEAN DEFAULT FALSE,
    is_won BOOLEAN DEFAULT FALSE
);

-- Tasks
CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50),  -- call, email, meeting, todo, followup
    status VARCHAR(20) DEFAULT 'pending',  -- pending, in_progress, completed, cancelled
    priority VARCHAR(10) DEFAULT 'medium',  -- low, medium, high, urgent
    due_date TIMESTAMPTZ,
    related_type VARCHAR(50),  -- lead, deal, contact, email
    related_id UUID,
    owner_id UUID REFERENCES users(id),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT now(),
    completed_at TIMESTAMPTZ
);

-- Notes (timeline entries)
CREATE TABLE notes (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    content TEXT NOT NULL,
    type VARCHAR(20) DEFAULT 'note',  -- note, email, call, meeting, system
    related_type VARCHAR(50),
    related_id UUID,
    author_id UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Activities (unified timeline)
CREATE TABLE activities (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    type VARCHAR(50),  -- email_sent, email_received, call, meeting, note, task, lead_created, deal_updated
    subject VARCHAR(255),
    description TEXT,
    related_type VARCHAR(50),
    related_id UUID,
    user_id UUID REFERENCES users(id),
    metadata JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);
```

## Core Features

### 1. Contact Management
- CRUD + import/export (CSV, vCard)
- Auto-create from email (sender/recipients)
- Merge duplicates (email-based)
- Contact timeline (emails, notes, tasks, deals)
- Custom fields per tenant

### 2. Lead Management
- Auto-create from AI classification (lead category)
- Kanban board by status
- Lead scoring (email engagement, firmographics, behavior)
- Assignment rules (round-robin, territory)
- Convert to deal

### 3. Pipeline Management
- Customizable stages per tenant
- Drag-drop deal movement
- Probability per stage
- Forecasting (weighted pipeline)
- Stage automation (move on email reply, task completion)

### 4. Activity Timeline
- Unified view: emails, calls, meetings, notes, tasks
- Filter by type, date, user
- Auto-log from email (sent/received)
- Manual activity logging

### 5. Email Integration
- Sidebar in webmail: show contact/lead/deal for current thread
- Quick actions: create lead, log call, schedule meeting
- Email tracking (opens, clicks) via pixel/link wrapping
- Thread-to-deal linking

### 6. Reporting
- Pipeline by stage/rep
- Conversion rates
- Activity metrics
- Email response times
- Lead source attribution

## tRPC Routers

```typescript
// crm.router.ts
export const crmRouter = router({
  // Contacts
  contacts: {
    list: protectedProcedure.query(...),
    get: protectedProcedure.query(...),
    create: protectedProcedure.mutation(...),
    update: protectedProcedure.mutation(...),
    merge: protectedProcedure.mutation(...),
    import: protectedProcedure.mutation(...),
  },
  
  // Companies
  companies: { list, get, create, update, ... },
  
  // Leads
  leads: {
    list: protectedProcedure.query(...),
    kanban: protectedProcedure.query(...),  // Grouped by status
    create: protectedProcedure.mutation(...),
    updateStatus: protectedProcedure.mutation(...),
    convertToDeal: protectedProcedure.mutation(...),
    assign: protectedProcedure.mutation(...),
  },
  
  // Deals
  deals: {
    list: protectedProcedure.query(...),
    pipeline: protectedProcedure.query(...),  // Grouped by stage
    create: protectedProcedure.mutation(...),
    moveStage: protectedProcedure.mutation(...),
    forecast: protectedProcedure.query(...),
  },
  
  // Pipeline
  pipeline: {
    getStages: protectedProcedure.query(...),
    updateStages: protectedProcedure.mutation(...),
  },
  
  // Tasks
  tasks: { list, get, create, update, complete, ... },
  
  // Activities
  activities: {
    timeline: protectedProcedure.query(...),  // Unified feed
    log: protectedProcedure.mutation(...),
  },
  
  // Reports
  reports: {
    pipeline: protectedProcedure.query(...),
    conversion: protectedProcedure.query(...),
    activity: protectedProcedure.query(...),
  },
});
```

## Automation Integration

Workflow actions that interact with CRM:
- `create_lead` - from classified email
- `update_contact` - enrich from email signature
- `create_task` - follow-up reminder
- `create_deal` - from qualified lead
- `move_deal_stage` - on email reply
- `log_activity` - any workflow step

## UI Components

- Contact/Company detail drawer (in webmail sidebar)
- Leads Kanban board
- Deals pipeline view (horizontal stages)
- Task list/calendar
- Activity timeline (infinite scroll)
- Reports dashboard (charts via Recharts)

## Timeline: 2-3 Weeks

| Week | Focus |
|------|-------|
| 1 | Data models, CRUD, contact/lead management |
| 2 | Pipeline, tasks, activities, email integration |
| 3 | Reports, automation actions, testing |
