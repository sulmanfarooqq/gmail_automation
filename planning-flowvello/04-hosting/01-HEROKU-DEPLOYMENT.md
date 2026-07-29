# Heroku Deployment Plan for FlowVello

## Architecture on Heroku

```
Heroku Eco Dyno ($7/mo)
├── web: Express.js API (npm start)
│   ├── REST API endpoints
│   ├── Webhook receiver
│   ├── Next.js serves frontend
│   └── Socket.io (real-time)
│
├── worker: BullMQ worker (Procfile process)
│   ├── Email processing jobs
│   ├── AI classification jobs
│   ├── Follow-up scheduled jobs
│   └── Watch renewal jobs
│
├── Heroku Postgres Mini ($5/mo)
│   └── All application data
│
└── Heroku Redis Mini ($3/mo)
    └── BullMQ queues + job scheduling
```

## Procfile

```yaml
web: cd backend && node dist/index.js
worker: cd backend && node dist/workers/email-worker.js
release: cd backend && npx prisma migrate deploy
```

## Heroku Config Vars (Environment)

```bash
# Heroku CLI commands to set these:
# heroku config:set KEY=value

# App
NODE_ENV=production
PORT=5000
APP_URL=https://flowvello-gmail.herokuapp.com

# Database (auto-set by Heroku Postgres addon)
DATABASE_URL=postgresql://...  # Heroku sets this automatically

# Redis (auto-set by Heroku Redis addon)
REDIS_URL=redis://...  # Heroku sets this automatically

# Encryption (generate: openssl rand -hex 32)
ENCRYPTION_KEY=your-32-byte-hex-key-here

# Auth
JWT_SECRET=your-jwt-secret
SESSION_EXPIRY=72h

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=https://flowvello-gmail.herokuapp.com/api/gmail/callback

# Gemini AI
GEMINI_API_KEY=your-gemini-api-key

# Google Pub/Sub
GOOGLE_PROJECT_ID=flowvello-gmail-agent
GOOGLE_PUBSUB_TOPIC=gmail-notifications
```

## Heroku Setup Commands

```bash
# 1. Install Heroku CLI, login
heroku login

# 2. Create app
heroku create flowvello-gmail-agent
# Or use existing app: heroku git:remote -a flowvello-gmail-agent

# 3. Add addons
heroku addons:create heroku-postgresql:mini
heroku addons:create heroku-redis:mini

# 4. Set config vars (run for each one)
heroku config:set JWT_SECRET=your-secret
heroku config:set GEMINI_API_KEY=your-key
# ... etc for all vars above

# 5. Set buildpacks (Node.js)
heroku buildpacks:set heroku/nodejs

# 6. Deploy
git push heroku main

# 7. Run migrations
heroku run npx prisma migrate deploy

# 8. Scale worker
heroku ps:scale worker=1
```

## Next.js + Express on Same Dyno

```typescript
// In Express, serve Next.js as middleware
// This avoids needing a separate frontend dyno

import next from 'next';

const nextApp = next({ dev: process.env.NODE_ENV !== 'production' });
const handle = nextApp.getRequestHandler();

await nextApp.prepare();

// API routes
app.use('/api', apiRouter);

// Next.js handles all other routes
app.all('*', (req, res) => handle(req, res));
```

## Alternative: Cheaper Setup (Under $10)

If you want absolute minimum cost:

```yaml
Option: Heroku Eco + separate free-tier DB
- Heroku Eco dyno: $5/mo (web + worker in 1 dyno, 1000hrs)
  - Run worker as a separate thread in the web process
  - BullMQ will work, just less isolation
- Supabase Free: $0 (PostgreSQL, 500MB)
  - Better: use Supabase instead of Heroku Postgres
- Heroku Redis Mini: $3/mo
- Total: ~$8/mo

OR even cheaper:
- Railway.app: $5/mo (includes DB)
- Fly.io: Free tier (up to 3 VMs, includes 8GB DB)
- Render: $7/mo (includes DB)

But since you asked for Heroku, the $15/mo setup is more reliable.
```

## Domain Setup

```
flowvello.com (if you own it)
  └── gmail.flowvello.com → flowvello-gmail-agent.herokuapp.com

Or use Heroku's domain:
  └── flowvello-gmail-agent.herokuapp.com (free, looks less professional)
```

## Backup Strategy

```bash
# Automated: Heroku Postgres auto-backups (included)
# Manual: pg_dump weekly

heroku pg:backups:schedule DATABASE_URL --at '02:00 Asia/Karachi'
heroku pg:backups:capture
```

## Monitoring (At Your Scale)

```bash
# Heroku logs (free)
heroku logs --tail

# Uptime monitoring (free)
# - https://uptimerobot.com (free, 5 min interval)
# - Set it to ping https://flowvello-gmail.herokuapp.com/api/health

# Error tracking
# - Sentry free tier: 5K events/month (enough for you)
```
