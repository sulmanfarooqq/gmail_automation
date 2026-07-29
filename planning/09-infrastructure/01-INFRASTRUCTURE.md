# Infrastructure & DevOps

## Current: Heroku

### Heroku Structure
```text
Heroku
├── web: Express.js API (1 dyno)
├── worker: BullMQ worker (1 dyno)
├── Heroku Postgres (Standard)
├── Heroku Redis (Premium)
└── Heroku Scheduler (for daily summary, cleanup)
```

### Heroku Limitations & Mitigations
| Limitation | Mitigation |
|------------|------------|
| No auto-scaling | Monitor usage, scale manually when needed |
| Dyno sleep (web only if no traffic) | Use Professional dynos (no sleep) |
| Ephemeral filesystem | Store everything in S3/R2 |
| No built-in cron | Heroku Scheduler or BullMQ repeatable jobs |

## Future: Dedicated Hosting (Phase 3)

```text
┌─────────────────────────────────────┐
│         Load Balancer (Nginx)        │
├─────────────────────────────────────┤
│                                     │
│  ┌─────────┐ ┌─────────┐ ┌────────┐ │
│  │ API     │ │ API     │ │ API    │ │
│  │ Node 1  │ │ Node 2  │ │ Node 3 │ │
│  └─────────┘ └─────────┘ └────────┘ │
│                                     │
│  ┌─────────┐ ┌─────────┐ ┌────────┐ │
│  │ Worker  │ │ Worker  │ │ Worker │ │
│  │ Node 1  │ │ Node 2  │ │ Node 3 │ │
│  └─────────┘ └─────────┘ └────────┘ │
│                                     │
├─────────────────────────────────────┤
│  PostgreSQL (Managed: RDS/Crunchy)  │
│  Redis (Managed: Upstash/RedisLabs) │
│  Object Storage (Cloudflare R2)     │
└─────────────────────────────────────┘
```

## CI/CD Pipeline

### GitHub Actions Workflow
```yaml
name: Deploy
on:
  push:
    branches: [main, staging]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
      - run: npm run test
      - run: npm run test:e2e

  deploy-staging:
    needs: test
    if: github.ref == 'refs/heads/staging'
    runs-on: ubuntu-latest
    steps:
      - run: deploy to heroku staging
      - run: npx prisma migrate deploy

  deploy-production:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - run: deploy to heroku production
      - run: npx prisma migrate deploy
```

## Environment Configuration

```env
# .env.example

# App
NODE_ENV=development
PORT=3000
APP_URL=http://localhost:3000

# Database
DATABASE_URL=postgresql://...

# Redis
REDIS_URL=redis://...

# Encryption (generate with: openssl rand -hex 32)
ENCRYPTION_KEY=hexkeyhere

# JWT
JWT_SECRET=...
SESSION_EXPIRY_HOURS=72

# Google OAuth
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=...

# Google Pub/Sub
PUBSUB_PROJECT_ID=...
PUBSUB_TOPIC=gmail-notifications
PUBSUB_SUBSCRIPTION=gmail-sub

# AI Providers
GEMINI_API_KEY=...
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...

# CRM (default: HubSpot)
HUBSPOT_CLIENT_ID=...
HUBSPOT_CLIENT_SECRET=...

# Storage (S3-compatible)
S3_ENDPOINT=https://r2.cloudflarestorage.com
S3_ACCESS_KEY=...
S3_SECRET_KEY=...
S3_BUCKET=gmail-automation-attachments

# Stripe
STRIPE_SECRET_KEY=...
STRIPE_WEBHOOK_SECRET=...

# Slack (notifications)
SLACK_CLIENT_ID=...
SLACK_CLIENT_SECRET=...

# SMTP (for notif emails)
SMTP_HOST=...
SMTP_PORT=587
SMTP_USER=...
SMTP_PASS=...
FROM_EMAIL=noreply@yourapp.com

# Monitoring
SENTRY_DSN=...
```

## Secrets Management
- **Development**: `.env.local` (gitignored)
- **Staging**: Heroku Config Vars
- **Production**: Heroku Config Vars → Later: HashiCorp Vault or AWS Secrets Manager
- Never commit secrets to git
- Rotate secrets quarterly
