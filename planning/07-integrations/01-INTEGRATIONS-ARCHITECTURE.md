# Integrations Architecture

## Design Pattern: Adapter Pattern

Every external integration follows the same pattern:

```typescript
interface Integration<TConfig, TOutput> {
  connect(config: TConfig): Promise<ConnectionResult>;
  disconnect(): Promise<void>;
  test(): Promise<boolean>;
  getStatus(): IntegrationStatus;
}

// CRM Example
interface CrmIntegration {
  createContact(data: CrmContactData): Promise<CrmContact>;
  updateContact(id: string, data: Partial<CrmContactData>): Promise<CrmContact>;
  findContactByEmail(email: string): Promise<CrmContact | null>;
  logActivity(contactId: string, activity: CrmActivity): Promise<void>;
  getPipelines(): Promise<CrmPipeline[]>;
}

// Calendar Example
interface CalendarIntegration {
  checkAvailability(start: Date, end: Date): Promise<TimeSlot[]>;
  createEvent(event: CalendarEvent): Promise<CalendarEvent>;
  findFreeSlots(date: Date, duration: number): Promise<TimeSlot[]>;
}
```

## CRM Integrations

### Priority Order
1. **HubSpot** (first — easiest API, free tier)
2. **GoHighLevel** (common in agency world)
3. **Pipedrive** (popular with sales agencies)
4. **Salesforce** (enterprise, complex OAuth)

### Each CRM Integration
- OAuth 2.0 or API key auth (configurable per provider)
- Field mapping stored per organization
- Bi-directional sync where possible
- Rate limiting per provider

## Notification Channels

```typescript
interface NotificationChannel {
  send(notification: NotificationPayload): Promise<void>;
}

// Channels to implement:
// 1. In-app (Socket.io) - always on
// 2. Email - for daily digests, urgent alerts
// 3. Slack - webhook integration
// 4. SMS (Twilio) - Phase 3
// 5. WhatsApp - Phase 4
```

## Integration Status Tracking

| Status | Meaning |
|--------|---------|
| connected | Working, actively syncing |
| disconnected | Needs re-authentication |
| expired | Token expired (OAuth) |
| error | Failed calls, needs attention |
| rate_limited | Temporarily paused |

## Health Check System

```typescript
// Every 5 minutes, check all integrations
// If 3 consecutive failures → alert admin
// If OAuth token expires in < 24h → trigger refresh
// Log all integration status changes
```

## Webhook System (For Agencies to Extend)

Each agency should be able to:
- Configure outbound webhooks on workflow actions
- Receive email events via webhook
- Use webhook secrets for verification
- Retry failed webhook deliveries
