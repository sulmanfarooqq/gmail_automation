# Security & Compliance

## Data Security

### Encryption at Rest
- PostgreSQL: Transparent Data Encryption (Heroku provides)
- OAuth tokens: AES-256-GCM before DB storage
- API keys: AES-256-GCM before DB storage
- Encryption key stored in environment variable (never in DB)
- Attachment files: Server-side encryption at S3/R2

### Encryption in Transit
- All API endpoints: HTTPS only (enforce via middleware)
- Database connections: TLS
- Redis connections: TLS (if supported by provider)
- External API calls: HTTPS

### OAuth Token Management
```typescript
// Never expose tokens to frontend
// Server-side only operations
// Auto-refresh before expiry
// Revoke on account disconnect
// Rotate refresh tokens periodically
```

## Authentication & Authorization

### Session Management
- JWT-based sessions with server-side validation
- Session expiry: 72 hours (configurable)
- Refresh token rotation
- Rate limit auth endpoints (5 attempts/minute/IP)
- Force logout on password change

### Role-Based Access Control
```typescript
enum Role {
  admin = 'admin',       // Full access, manage users, billing
  agent = 'agent',       // View inbox, approve/reply, manage leads
  viewer = 'viewer',     // Read-only access
}

// Permission matrix
const permissions: Record<Role, Permission[]> = {
  admin: ['*'],
  agent: [
    'emails:read', 'emails:write',
    'drafts:read', 'drafts:approve', 'drafts:send',
    'leads:read', 'leads:write',
    'knowledge_base:read', 'knowledge_base:write',
    'tasks:read', 'tasks:write',
  ],
  viewer: [
    'emails:read',
    'drafts:read',
    'leads:read',
    'analytics:read',
  ],
};
```

### API Security
- Rate limiting: 100 req/min per user (stricter for auth: 5/min)
- CORS: Whitelist allowed origins
- Request validation: Zod schemas on all endpoints
- SQL injection prevention: Prisma parameterized queries
- XSS prevention: Input sanitization, CSP headers

## Email Compliance

### CAN-SPAM Act
- Every automated email must include:
  - Clear "From" identification
  - Physical mailing address (agency address)
  - Unsubscribe link in every marketing/follow-up email
  - Honored opt-out within 10 business days
- Subject lines must not be deceptive

### GDPR
- Data processing agreement required with each agency
- Right to be forgotten: Delete all personal data on request
- Data portability: Export all data in JSON
- Data retention: Configurable auto-delete (default: 365 days)
- Cookie consent for dashboard

### Email Authentication
```text
SPF: Include Heroku send grid / your sending infrastructure
DKIM: Sign all outgoing emails
DMARC: Policy = quarantine (monitor → enforce)
```

### List-Unsubscribe Header
```text
List-Unsubscribe: <mailto:unsubscribe@yourdomain.com?subject=unsubscribe>
List-Unsubscribe-Post: List-Unsubscribe=One-Click
```

## Audit Trail

Every **user action** that modifies state is logged:
- Email approved/rejected/sent
- Workflow created/modified/deleted  
- KB updated
- User invited/removed
- Settings changed
- Integration connected/disconnected

Audit log includes: who, what, when, old value, new value, IP address, user agent.

## Monitoring & Alerting

### Security Events (alert immediately)
- 5+ failed login attempts from same IP
- Token refresh failure for multiple accounts
- Unusual email volume (10x normal)
- Access from unusual location
- API endpoint scanning detected

## Backup Strategy

| Data | Frequency | Retention | Type |
|------|-----------|-----------|------|
| PostgreSQL | Daily | 30 days | Automated backup |
| PostgreSQL | Continuous | Point-in-time (7 days) | WAL streaming |
| Attachments (S3/R2) | Real-time | Indefinite | Replicated |
| Config (env vars) | On change | All versions | Version control |

## Incident Response Plan

1. **Detection**: Monitoring alert or user report
2. **Containment**: Rate limit suspected abuse, revoke compromised tokens
3. **Investigation**: Audit logs, access logs, DB queries
4. **Remediation**: Fix vulnerability, rotate keys if needed
5. **Communication**: Notify affected users (agencies)
6. **Post-mortem**: Document root cause, update processes
