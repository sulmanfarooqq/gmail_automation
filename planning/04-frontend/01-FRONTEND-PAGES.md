# Frontend Pages (Next.js App Router)

## Technology Stack
- Next.js 14+ (App Router)
- TypeScript
- Tailwind CSS
- shadcn/ui components
- React Query (TanStack Query) for data fetching
- Zustand for client state
- Socket.io-client for real-time

---

## Page Structure

### Public Pages

| Route | Page | Description |
|-------|------|-------------|
| `/` | Landing | Marketing page, features, pricing |
| `/pricing` | Pricing | Plan comparison |
| `/login` | Login | Email + password auth |
| `/register` | Register | New org signup |
| `/forgot-password` | Forgot Password | Reset flow |
| `/privacy` | Privacy Policy | Legal |
| `/terms` | Terms of Service | Legal |

### App Pages (Protected)

#### Dashboard

| Route | Page | Key Components |
|-------|------|----------------|
| `/app` | Overview | Stats cards: emails processed, leads, AI replies, time saved |
| `/app/inbox` | Inbox View | Email list, filters (All/Leads/Urgent/Support/Unanswered/AI Drafts) |
| `/app/inbox/:id` | Email Detail | Full email, classification, draft, actions |

#### AI Drafts

| Route | Page | Key Components |
|-------|------|----------------|
| `/app/drafts` | Draft List | Filterable list of pending drafts |
| `/app/drafts/:id` | Draft Review | Email + AI draft side-by-side, edit, approve, reject |

#### Leads

| Route | Page | Key Components |
|-------|------|----------------|
| `/app/leads` | Lead Dashboard | Table, filters, search |
| `/app/leads/:id` | Lead Detail | Full lead info, activity, email history |

#### Automations

| Route | Page | Key Components |
|-------|------|----------------|
| `/app/automations` | Workflow List | Cards with status, runs, success rate |
| `/app/automations/new` | Create Workflow | Visual workflow builder |
| `/app/automations/:id` | Edit Workflow | Visual workflow builder (edit mode) |
| `/app/automations/:id/executions` | Execution Logs | History of workflow runs |

#### Follow-ups

| Route | Page | Key Components |
|-------|------|----------------|
| `/app/follow-ups` | Sequence List | Active/paused/completed sequences |
| `/app/follow-ups/new` | Create Sequence | Step builder with delays and templates |
| `/app/follow-ups/:id` | Sequence Detail | Progress, executions |

#### Knowledge Base

| Route | Page | Key Components |
|-------|------|----------------|
| `/app/knowledge-base` | KB Dashboard | Sections: Company Info, FAQs, Services, Team |
| `/app/knowledge-base/edit` | Edit KB | Form with all KB fields |

#### Integrations

| Route | Page | Key Components |
|-------|------|----------------|
| `/app/integrations` | Integration Hub | Cards for Gmail, Calendar, CRM, Slack, etc. |
| `/app/integrations/gmail` | Gmail Setup | OAuth flow, connected accounts |
| `/app/integrations/calendar` | Calendar Setup | Calendar OAuth, availability settings |
| `/app/integrations/crm` | CRM Setup | Provider selection, API key config |

#### Team

| Route | Page | Key Components |
|-------|------|----------------|
| `/app/team` | Team Dashboard | User list, roles, status |
| `/app/team/invite` | Invite Member | Email + role selection |

#### Settings

| Route | Page | Key Components |
|-------|------|----------------|
| `/app/settings` | Org Settings | Name, branding, timezone |
| `/app/settings/billing` | Billing | Plan, usage, payment method |
| `/app/settings/ai` | AI Config | Provider selection, API keys, model settings |

#### Analytics

| Route | Page | Key Components |
|-------|------|----------------|
| `/app/analytics` | Analytics Dashboard | Charts, metrics, export |

#### Search

| Route | Page | Key Components |
|-------|------|----------------|
| `/app/search` | Global Search | Search bar, results with filters |

---

## Shared Layout Components

### Sidebar Navigation
```
Logo
──
Dashboard
Inbox
AI Drafts {count}
Leads
──
Automations
Follow-ups
Knowledge Base
──
Integrations
Team
──
Analytics
Search
Settings
```

### Top Bar
- Organization selector (if multi-account)
- Notification bell with unread count
- User menu (profile, logout)

### Inbox Filters
```
All | Leads | Urgent | Support | Unanswered | AI Drafts
```

## Real-time Features
- Socket.io connection on app mount
- Live inbox updates when new email arrives
- Real-time notification toast
- Draft status updates without refresh
- Team member activity indicators
