# Monitoring & Logging

## Logging Infrastructure

### Structured Logging (Pino)

```typescript
// logger.ts
import pino from 'pino';

export const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  transport: process.env.NODE_ENV === 'development'
    ? { target: 'pino-pretty' }
    : undefined,
  redact: ['req.headers.authorization', 'req.body.accessToken', 'req.body.refreshToken'],
});
```

### Log Levels
| Level | Usage |
|-------|-------|
| error | Unhandled errors, external API failures, auth failures |
| warn | Rate limit approaching, AI confidence low, retry attempts |
| info | Email processed, draft approved, CRM synced, workflow executed |
| debug | AI prompts/responses (do not enable in production by default) |

### What to Log (Always)
- Incoming requests (method, path, status, duration, org_id)
- Email processing pipeline (each step with timing)
- AI calls (model, tokens, cost, success/failure)
- Workflow executions (trigger, conditions met, actions executed)
- Integration events (CRM create, calendar book, email sent)
- Auth events (login, logout, failed attempt, token refresh)
- Errors (full stack trace, context, correlation ID)

### What NOT to Log
- OAuth tokens (redacted)
- Passwords (never)
- Full email bodies in debug logs (log only IDs)
- API keys

## Error Tracking: Sentry

```typescript
import * as Sentry from '@sentry/node';

Sentry.init({
  dsn: process.env.SENTRY_DSN,
  environment: process.env.NODE_ENV,
  tracesSampleRate: 0.1, // 10% in production
  integrations: [new Sentry.Integrations.Prisma()],
});

// Add context to every event
Sentry.setUser({ id: userId, organizationId });
Sentry.setTag('organization_id', orgId);
```

## Health Checks

### Endpoints
```text
GET /health         → 200 OK (basic server health)
GET /health/ready   → 200/503 (DB, Redis, AI provider reachable)
```

### Checks Run
- PostgreSQL connection
- Redis connection (if used)
- AI provider reachability (ping with small request)
- Gmail API reachability (placeholder)
- Queue worker status (alive, not backed up)
- Disk space

## Metrics (Prometheus)

```typescript
// metrics.ts
import prometheus from 'prom-client';

// Email metrics
export const emailsProcessed = new prometheus.Counter({
  name: 'emails_processed_total',
  help: 'Total emails processed',
  labelNames: ['organization_id', 'status'],
});

export const emailProcessingDuration = new prometheus.Histogram({
  name: 'email_processing_duration_ms',
  help: 'Email processing time in ms',
  buckets: [100, 500, 1000, 3000, 5000, 10000],
});

// AI metrics
export const aiCallDuration = new prometheus.Histogram({
  name: 'ai_call_duration_ms',
  help: 'AI provider call duration',
  labelNames: ['provider', 'model', 'operation'],
});

export const aiTokensUsed = new prometheus.Counter({
  name: 'ai_tokens_used_total',
  help: 'Total AI tokens used',
  labelNames: ['provider', 'model'],
});

export const aiCostTotal = new prometheus.Counter({
  name: 'ai_cost_total_usd',
  help: 'Total AI cost in USD',
  labelNames: ['organization_id'],
});

// Queue metrics
export const queueJobCount = new prometheus.Gauge({
  name: 'queue_jobs_count',
  help: 'Number of jobs in queue',
  labelNames: ['queue_name', 'status'],
});

export const queueJobDuration = new prometheus.Histogram({
  name: 'queue_job_duration_ms',
  help: 'Job processing time',
  labelNames: ['queue_name', 'job_type'],
});
```

## Alerting Rules

### Critical (Respond within 15 min)
- Queue backlog > 1000 unprocessed jobs
- AI provider failure rate > 10% over 5 min
- Email send failure rate > 5%
- Gmail API 401 errors (token expired)
- Database connection failures
- Worker process down

### Warning (Respond within 1 hour)
- Email processing latency > 30 seconds
- AI confidence < 70% for > 10% of classifications
- Rate limit warnings (approaching limit)
- OAuth tokens expiring within 24 hours
- High memory/CPU usage

### Info (Review daily)
- New organization signups
- Daily email volume by org
- AI cost per org
- Integration disconnections
- Failed workflow executions

## Dashboard (Grafana)

### Panels
1. **Email Pipeline**: Processed, classified, drafted, sent (time series)
2. **AI Performance**: Call duration, token usage, cost per provider
3. **Queue Health**: Job count by queue, processing time, failure rate
4. **Error Rate**: 5xx responses, unhandled exceptions, AI errors
5. **Org Activity**: Active orgs, emails per org, storage usage
6. **API Performance**: Response times, endpoint hit rates, status codes
