# Workflow Engine Design

## Core Concept

Visual "If-This-Then-That" engine specifically for email operations. Agencies create workflows without code.

## Workflow Structure

```typescript
interface Workflow {
  id: string;
  organizationId: string;
  name: string;
  trigger: Trigger;
  conditions: ConditionGroup;  // AND/OR tree of conditions
  actions: Action[];           // Ordered actions to execute
  isActive: boolean;
}

type Trigger = 
  | { type: 'email_received' }
  | { type: 'email_classified'; intent?: IntentType }
  | { type: 'lead_detected'; minScore?: number }
  | { type: 'no_reply_timeout'; days: number }
  | { type: 'scheduled'; cron: string };

interface ConditionGroup {
  operator: 'AND' | 'OR';
  conditions: (Condition | ConditionGroup)[];
}

interface Condition {
  field: ConditionField;
  operator: 'equals' | 'contains' | 'greater_than' | 'less_than' | 'in' | 'matches_regex';
  value: string | number | string[];
}

type ConditionField = 
  | 'email.intent'
  | 'email.priority'
  | 'email.sentiment'
  | 'email.lead_score'
  | 'email.from_domain'
  | 'email.has_attachments'
  | 'email.subject_contains'
  | 'email.body_contains'
  | 'email.sender_is_known'
  | 'email.sender_is_contact';

interface Action {
  type: ActionType;
  config: Record<string, any>;
  order: number;
}

type ActionType =
  | 'classify_email'
  | 'generate_reply'
  | 'send_reply'
  | 'request_approval'
  | 'create_crm_contact'
  | 'update_crm_contact'
  | 'create_task'
  | 'assign_task'
  | 'send_notification'
  | 'schedule_follow_up'
  | 'check_calendar_availability'
  | 'book_meeting'
  | 'add_label'
  | 'forward_email'
  | 'archive_email'
  | 'call_webhook'
  | 'stop_processing';
```

## Example Workflow: New Lead Handler

```json
{
  "name": "New Lead Handler",
  "trigger": { "type": "email_classified", "intent": "lead" },
  "conditions": {
    "operator": "AND",
    "conditions": [
      { "field": "email.lead_score", "operator": "greater_than", "value": 50 },
      { "field": "email.sender_is_known", "operator": "equals", "value": false }
    ]
  },
  "actions": [
    { "type": "create_crm_contact", "config": { "listId": "leads" }, "order": 1 },
    { "type": "generate_reply", "config": { "tone": "professional" }, "order": 2 },
    { "type": "request_approval", "config": { "assignTo": "sales_team" }, "order": 3 },
    { "type": "schedule_follow_up", "config": { "delayDays": 2 }, "order": 4 },
    { "type": "send_notification", "config": { "channel": "slack", "message": "New lead!" }, "order": 5 }
  ]
}
```

## Execution Engine

```
Workflow matched email
    │
    ▼
[Step 1] Check conditions
    │ Pass → Continue
    │ Fail → Mark execution as skipped
    │
    ▼
[Step 2] Execute actions in order
    │ Each action:
    │   1. Validate config
    │   2. Execute with retry (3 attempts)
    │   3. Log result
    │   4. If failed → continue or stop (configurable)
    │
    ▼
[Step 3] Update execution record
    │ Store: status, result, error, timing
    │
    ▼
[Step 4] Trigger side effects
    │ Notifications, webhooks, logging
```

## Visual Builder (Frontend)

```typescript
// Drag-and-drop workflow builder
// Canvas with nodes:
//   TRIGGER → CONDITION → ACTION → ACTION → ...

// Node types:
//   - Trigger node (rounded rectangle, green)
//   - Condition node (diamond, yellow) 
//   - Action node (rectangle, blue)
//   - Connector lines with arrow

// Each node configurable via side panel
// Real-time validation
// Test mode: run against sample email
```

## Workflow Templates (Pre-built)

1. **Lead Capture** — Detect lead → Create CRM → Notify team → Follow up
2. **Support Auto-Reply** — FAQ questions → Auto-reply from KB
3. **Meeting Booker** — Meeting request → Check calendar → Send options
4. **Urgent Alert** — High priority from key client → Notify immediately
5. **Follow-up Sequence** — No reply in N days → Send reminder sequence
6. **Invoice Handler** — Invoice attachment → Extract data → Notify finance
7. **Lead Scoring** — Score thresholds → Different assignment paths
