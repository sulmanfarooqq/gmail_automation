# System Architecture

## High-Level Component Diagram

INTERNET
   |
   v
DNS (Namecheap/Cloudflare)
   A / MX / SPF / DKIM / DMARC / PTR
   |
   v
VPS (Hetzner/Contabo)
  Traefik (Reverse Proxy)
     TLS Termination + Rate Limiting + Auth
     |
  +--+--+--+
  |  |  |  |
  v  v  v  v
Mail Stack  App Stack  AI Stack
(Mailu)    (Next.js)   (Python)
  |          |          |
Postfix     API        Gemini API
Dovecot     Webmail    Function Calling
Rspamd      Admin UI   Embeddings
ClamAV      tRPC       Vector DB
OpenDKIM
  |          |          |
  +----------+----------+
             |
      PostgreSQL + Redis
             |
      MinIO + Monitoring

## Mail Stack (Mailu) - Internal Architecture

MAILU CONTAINER
  Postfix (SMTP)    Dovecot (IMAP)    Rspamd (Spam/ML)
  Port: 25          Port: 143         Port: 11334
  Port: 587         Port: 993           - Bayesian
  Port: 465                        - Neural
                                      - DKIM
                                      - SPF
                                      - DMARC
         OpenDKIM (Signing/Verification)
              |
         SHARED VOLUME
         /data/mail/   -> Maildir storage
         /data/dkim/   -> DKIM private keys
         /data/rspamd/ -> Rspamd learning data

## Application Stack - Module Boundaries

apps/
webmail/           # Next.js app - User-facing mailbox
  app/(auth)/
  app/(mail)/
  app/(contacts)/
  app/(settings)/
  components/

admin/             # Next.js app - Platform admin
  app/(platform)/
  app/(monitoring)/
  app/(billing)/
  components/

client-portal/     # Next.js app - Tenant admin
  app/(tenant)/
  app/(knowledge)/
  app/(automation)/
  app/(crm)/
  components/

api/               # Shared API layer (tRPC)
  routers/
    mail.ts
    tenant.ts
    user.ts
    ai.ts
    automation.ts
    crm.ts
    webhook.ts
  middleware/
    auth.ts
    rateLimit.ts
    rbac.ts
  db/
    schema.ts
    rls.ts
    migrations/
