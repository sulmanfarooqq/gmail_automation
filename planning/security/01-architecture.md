# Security & Deliverability Architecture

## Security Principles

1. **Defense in Depth** - Multiple layers of protection
2. **Zero Trust** - Never trust, always verify
3. **Least Privilege** - Minimum access required
4. **Tenant Isolation** - Absolute data separation
5. **Audit Everything** - Immutable logs for all mutations
6. **Encryption** - At rest (AES-256) and in transit (TLS 1.3)
7. **Secure by Default** - Safe configurations out of the box

## Authentication & Authorization

### Authentication Flow
```
User -> Login Page -> Credentials + MFA -> JWT (access: 15min, refresh: 7d)
                                    |
                                    v
                            Token Validation Middleware
                                    |
                                    v
                          Set app.current_tenant_id (RLS)
                                    |
                                    v
                              Route Handler
```

### JWT Structure
```json
{
  "sub": "user_uuid",
  "tenant_id": "tenant_uuid",
  "role": "admin",
  "permissions": ["mail:read", "mail:send", "admin:tenants"],
  "mfa_verified": true,
  "impersonated_by": "super_admin_uuid",  // Only if impersonating
  "iat": 1234567890,
  "exp": 1234568790
}
```

### MFA Implementation
- TOTP (RFC 6238) via authenticator apps
- Backup codes (10 single-use)
- Enforced for: super-admin, tenant owners, admin roles
- Optional for: regular users (configurable per tenant)

### Session Management
- Access token: 15 min, stored in memory (not localStorage)
- Refresh token: 7 days, httpOnly Secure SameSite=Strict cookie
- Rotation on refresh
- Revocation on: password change, MFA disable, admin revoke, suspicious activity
- Concurrent session limit: 5 per user

### Role-Based Access Control (RBAC)

| Role | Platform | Tenant | Mailbox |
|------|----------|--------|---------|
| Super Admin | Full | All | All |
| Support | Read | Assigned | Assigned |
| Billing | Billing only | - | - |
| Tenant Owner | - | Full | All |
| Tenant Admin | - | Most | All |
| User | - | Limited | Own |

### Permission Matrix
```typescript
const permissions = {
  'mail:read': ['user', 'admin', 'owner'],
  'mail:send': ['user', 'admin', 'owner'],
  'mail:delete': ['admin', 'owner'],
  'settings:write': ['admin', 'owner'],
  'users:manage': ['admin', 'owner'],
  'domain:manage': ['owner'],
  'billing:manage': ['owner'],
  'ai:configure': ['admin', 'owner'],
  'workflow:manage': ['admin', 'owner'],
  'crm:manage': ['admin', 'owner'],
  'platform:tenants': ['super_admin'],
  'platform:impersonate': ['super_admin'],
};
```

## Tenant Isolation (Critical)

### Database Level (PostgreSQL RLS)
```sql
-- Enable RLS on all tables
ALTER TABLE emails ENABLE ROW LEVEL SECURITY;
ALTER TABLE contacts ENABLE ROW LEVEL SECURITY;
-- ... all tables

-- Policy: tenant can only see own data
CREATE POLICY tenant_isolation ON emails
  USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

-- Super-admin bypass
CREATE POLICY super_admin_bypass ON emails
  USING (current_setting('app.is_super_admin', true)::boolean = true);
```

### Application Level
```typescript
// Middleware: sets tenant context
export async function tenantMiddleware(req, res, next) {
  const token = getToken(req);
  const payload = verifyToken(token);
  
  // Validate tenant access
  if (payload.tenant_id && !await canAccessTenant(payload.sub, payload.tenant_id)) {
    return res.status(403).json({ error: 'Tenant access denied' });
  }
  
  // Set for RLS
  await db.execute(`SET LOCAL app.current_tenant_id = '${payload.tenant_id}'`);
  if (payload.role === 'super_admin') {
    await db.execute(`SET LOCAL app.is_super_admin = 'true'`);
  }
  
  req.tenantId = payload.tenant_id;
  req.userId = payload.sub;
  req.role = payload.role;
  next();
}
```

### File Storage Isolation
```
MinIO Bucket: mail-attachments
Path: tenant/{tenant_id}/{mailbox_id}/{email_id}/{attachment_id}
Policy: tenant users can only access their tenant prefix
```

### AI/Knowledge Base Isolation
- Vector search: `WHERE tenant_id = $1` in pgvector queries
- Separate embedding collections per tenant (if using Qdrant)
- Prompt injection prevention: sanitize user input in prompts

### Mail Server Isolation
- Mailu: Separate virtual domains per tenant
- Dovecot: Per-tenant user databases
- Postfix: Virtual alias maps per tenant
- Queue: Separate Redis streams per tenant

## Encryption

### At Rest
| Data | Method |
|------|--------|
| Database | PostgreSQL TDE (LUKS on volume) + column-level for PII |
| MinIO | SSE-S3 (AES-256) |
| Backups | GPG symmetric (AES-256) before upload |
| DKIM Keys | Encrypted in DB + file system permissions |
| Secrets | HashiCorp Vault / AWS Secrets Manager |

### In Transit
- All external: TLS 1.3 only (min TLS 1.2)
- Internal: mTLS via service mesh (k3s) or stunnel
- SMTP: STARTTLS required, DANE TLSA records
- IMAP: IMAPS (993) only
- API: HTTPS only, HSTS, Certificate Transparency

### Key Management
- Rotation: DKIM annually, DB encryption quarterly
- Storage: Vault with auto-unseal
- Access: Audit logged, approval required

## Deliverability Security

### Outbound Protection
```typescript
// Rate limiting per tenant
const limits = {
  basic: { per_hour: 100, per_day: 1000 },
  business: { per_hour: 500, per_day: 10000 },
  sales: { per_hour: 1000, per_day: 50000 },
  automation: { per_hour: 2000, per_day: 100000 },
  enterprise: { per_hour: 5000, per_day: 500000 },
};

// Content scanning
async function scanOutbound(email: Email) {
  // 1. SpamAssassin/Rspamd scan
  const spamScore = await rspamd.check(email);
  if (spamScore > 7) return { action: 'quarantine', reason: 'High spam score' };
  
  // 2. Virus scan
  const virusResult = await clamav.scan(email.attachments);
  if (virusResult.infected) return { action: 'reject', reason: 'Virus detected' };
  
  // 3. Phishing detection
  if (await phishingDetector.check(email)) {
    return { action: 'quarantine', reason: 'Phishing detected' };
  }
  
  // 4. Suppression list check
  if (await isSuppressed(email.to)) {
    return { action: 'drop', reason: 'Suppressed recipient' };
  }
  
  return { action: 'send' };
}
```

### Abuse Detection
```typescript
// Behavioral anomalies
const abuseSignals = {
  sudden_volume_spike: (current, baseline) => current > baseline * 10,
  high_bounce_rate: (bounces, sent) => bounces / sent > 0.05,
  high_complaint_rate: (complaints, sent) => complaints / sent > 0.001,
  new_domain_high_volume: (domainAge, volume) => domainAge < 30 && volume > 100,
  suspicious_content: (email) => phishingDetector.check(email) || spamScore > 5,
};

// Automated response
async function handleAbuse(tenantId: string, signal: string) {
  const tenant = await getTenant(tenantId);
  
  switch (signal) {
    case 'sudden_volume_spike':
      await setRateLimit(tenantId, limits[tenant.plan].per_hour * 0.1);
      await alertSecurity({ tenantId, signal, action: 'throttled' });
      break;
    case 'high_bounce_rate':
      await pauseOutbound(tenantId);
      await notifyAdmin({ tenantId, signal, action: 'paused' });
      break;
    case 'phishing_detected':
      await suspendTenant(tenantId, 'Phishing content detected');
      await alertSecurity({ tenantId, signal, action: 'suspended', severity: 'critical' });
      break;
  }
}
```

### Monitoring & Alerting
```prometheus
# Key metrics
mail_sent_total{tenant,status="sent|bounced|complained|rejected"}
mail_delivery_latency_seconds{tenant,provider}
mail_spam_score{tenant}  # histogram
mail_bounce_rate{tenant}  # gauge
mail_complaint_rate{tenant}  # gauge
ip_reputation_score  # gauge (from SenderScore)
domain_reputation_score{tenant}  # gauge
tenant_outbound_paused{tenant}  # gauge (0/1)
```

### Feedback Loop Processing
- Dedicated mailbox: `bounces@flowvello.com`, `complaints@flowvello.com`
- Parse bounce types: hard/soft/block
- Parse FBL (Feedback Loop) reports: ARF format
- Auto-suppress: hard bounces, complaints
- Update sender reputation metrics

## Data Protection

### PII Handling
- Email bodies: Encrypted at rest (optional per tenant)
- Attachments: Sc
