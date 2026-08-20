# Phase 5: Automation Engine Specification (Python)

## Objective
Build a general-purpose automation engine with triggers, conditions, actions, delays, and webhooks - the core that turns email into automated workflows.

## Tech Stack
- Python 3.11+ (asyncio)
- PostgreSQL for workflow definitions + execution state
- Redis for queue + pub/sub
- Celery for distributed task execution
- Pydantic for validation
- Custom state machine (no external workflow engine)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AUTOMATION ENGINE                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  TRIGGERS                                                    │
│  ├── EmailReceivedTrigger    (from Redis stream)            │
│  ├── ScheduledTrigger        (cron)                          │
│  ├── WebhookTrigger          (HTTP endpoint)                │
│  ├── ManualTrigger           (API call)                     │
│  └── EmailOpenedTrigger      (tracking pixel)               │
│                                                              │
│  CONDITIONS                                                  │
│  ├── AIClassificationCondition  (category, confidence)      │
│  ├── FieldMatchCondition        (from, to, subject, etc.)   │
│  ├── TimeCondition              (business hours, timezone)  │
│  ├── ContactExistsCondition     (CRM lookup)                │
│  ├── CustomExpressionCondition  (JSONLogic/Cel)             │
│  └── TenantSettingsCondition    (plan limits, features)     │
│                                                              │
│  ACTIONS                                                     │
│  ├── SendEmailAction           (via SMTP)                   │
│  ├── CreateLeadAction          (CRM)                        │
│  ├── UpdateContactAction       (CRM)                        │
│  ├── CreateTaskAction          (CRM/Asana/Linear)           │
│  ├── ScheduleFollowupAction    (delayed email)              │
│  ├── ForwardEmailAction        (to mailbox/user)            │
│  ├── BookAppointmentAction     (Calendly/Cal.com)           │
│  ├── GenerateQuoteAction       (template + data)            │
│  ├── SendNotificationAction    (Slack, Email, Webhook)      │
│  ├── WebhookAction             (custom HTTP)                │
│  ├── AddLabelAction            (email labels)               │
│  ├── MoveEmailAction           (folder)                     │
│  └── AIDraftReplyAction        (generate + save draft)      │
│                                                              │
│  DELAYS                                                      │
│  ├── WaitDelay                 (fixed duration)             │
│  ├── CronDelay                 (next business day 9am)      │
│  ├── RandomDelay               (human-like variation)       │
│  └── UntilConditionDelay       (wait for condition)         │
│                                                              │
│  STATE MACHINE                                               │
│  ├── WorkflowInstance          (execution context)          │
│  ├── NodeExecution             (per-node state)             │
│  ├── Checkpointing             (persist after each node)    │
│  ├── Compensation              (rollback on failure)        │
│  └── Timeout/Heartbeat         (detect stuck executions)    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Workflow Definition (JSON)

```json
{
  "name": "Sales Lead Workflow",
  "trigger": {
    "type": "email_received",
    "config": {
      "mailbox_ids": ["uuid1", "uuid2"],
      "folders": ["inbox"]
    }
  },
  "nodes": [
    {
      "id": "classify",
      "type": "condition",
      "config": {
        "condition_type": "ai_classification",
        "categories": ["lead", "quote_request"],
        "min_confidence": 0.7
      }
    },
    {
      "id": "create_lead",
      "type": "action",
      "config": {
        "action_type": "create_lead",
        "fields": {
          "name": "{{extracted.name}}",
          "company": "{{extracted.company}}",
          "email": "{{email.from}}",
          "source": "email",
          "metadata": "{{extracted}}"
        }
      }
    },
    {
      "id": "draft_reply",
      "type": "action",
      "config": {
        "action_type": "ai_draft_reply",
        "tone": "professional",
        "template": "lead_acknowledgment"
      }
    },
    {
      "id": "send_reply",
      "type": "action",
      "config": {
        "action_type": "send_email",
        "draft_node_id": "draft_reply",
        "approval_level": "suggest"
      }
    },
    {
      "id": "wait_24h",
      "type": "delay",
      "config": { "duration": "24h" }
    },
    {
      "id": "check_response",
      "type": "condition",
      "config": {
        "condition_type": "email_replied",
        "thread_id": "{{trigger.thread_id}}"
      }
    },
    {
      "id": "followup_1",
      "type": "action",
      "config": {
        "action_type": "send_email",
        "template": "lead_followup_1"
      }
    },
    {
      "id": "wait_3d",
      "type": "delay",
      "config": { "duration": "72h" }
    },
    {
      "id": "notify_sales",
      "type": "action",
      "config": {
        "action_type": "send_notification",
        "channels": ["slack", "email"],
        "recipients": ["sales-team"],
        "message": "Lead {{lead.id}} no response after 3 days"
      }
    }
  ],
  "edges": [
    { "from": "classify", "to": "create_lead", "condition": "matched" },
    { "from": "create_lead", "to": "draft_reply" },
    { "from": "draft_reply", "to": "send_reply" },
    { "from": "send_reply", "to": "wait_24h" },
    { "from": "wait_24h", "to": "check_response" },
    { "from": "check_response", "to": "followup_1", "condition": "not_replied" },
    { "from": "followup_1", "to": "wait_3d" },
    { "from": "wait_3d", "to": "notify_sales" }
  ]
}
```

## Core Components

### 1. Workflow Engine (services/workflow/engine.py)

```python
class WorkflowEngine:
    def __init__(self, db: AsyncSession, redis: Redis, action_registry: ActionRegistry):
        self.db = db
        self.redis = redis
        self.actions = action_registry
    
    async def execute(self, workflow_id: str, trigger_payload: Dict) -> ExecutionResult:
        # Create execution record
        execution = await self.create_execution(workflow_id, trigger_payload)
        
        # Get workflow definition
        workflow = await self.get_workflow(workflow_id)
        
        # Start from trigger node
        await self.run_node(execution, workflow.trigger_node_id, trigger_payload)
        
        return ExecutionResult(execution_id=execution.id)
    
    async def run_node(self, execution: WorkflowExecution, node_id: str, context: Dict):
        node = execution.workflow.nodes[node_id]
        
        # Checkpoint state
        await self.checkpoint(execution, node_id, context)
        
        if node.type == 'condition':
            result = await self.evaluate_condition(node, context)
            next_nodes = self.get_matching_edges(node_id, result)
        elif node.type == 'action':
            result = await self.execute_action(node, context)
            next_nodes = self.get_outgoing_edges(node_id)
        elif node.type == 'delay':
            result = await self.schedule_delay(node, context)
            next_nodes = self.get_outgoing_edges(node_id)
        
        # Continue to next nodes
        for next_node in next_nodes:
            await self.run_node(execution, next_node, {**context, **result})
```

### 2. Action Registry (services/workflow/actions/registry.py)

```python
class ActionRegistry:
    def __init__(self):
        self._actions: Dict[str, Action] = {}
    
    def register(self, action_type: str, action: Action):
        self._actions[action_type] = action
    
    async def execute(self, action_type: str, config: Dict, context: Dict) -> Dict:
        action = self._actions.get(action_type)
 
