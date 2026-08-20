# Phase 1: Mail Infrastructure Specification

## Objective
Establish reliable email infrastructure where contact@flowvello.com can send/receive with 10/10 mail-tester.com score.

## Technology Choice: Mailu (Docker-based)
Why Mailu over raw Postfix/Dovecot:
- Pre-configured with hardened defaults
- Integrated Rspamd + ClamAV + OpenDKIM
- Web admin for domain/mailbox management
- Active maintenance, battle-tested in production
- Generates proper configs for deliverability

## Infrastructure Requirements

### VPS Specifications (Hetzner CX42 / Contabo VPS L)
- 8 vCPU, 16 GB RAM, 160 GB NVMe
- Clean IP reputation (check via mxtoolbox, spamhaus)
- PTR record configurable to mail.flowvello.com
- IPv4 + IPv6
- Location: EU (GDPR) or US based on target market

### DNS Configuration (Namecheap/Cloudflare)
DNS records needed:
mail.flowvello.com.     A       <VPS_IPV4>
mail.flowvello.com.     AAAA    <VPS_IPV6>
flowvello.com.          MX  10  mail.flowvello.com.
flowvello.com.          TXT     v=spf1 ip4:<VPS_IPV4> ip6:<VPS_IPV6> ~all
_dmarc.flowvello.com.   TXT     v=DMARC1; p=quarantine; rua=mailto:dmarc@flowvello.com
default._domainkey.flowvello.com.  TXT  v=DKIM1; k=rsa; p=<PUBLIC_KEY>
<VPS_IPV4>              PTR     mail.flowvello.com.
## Mailu Configuration (docker-compose.yml)

version: '3.8'

services:
  front:
    image: mailu/nginx:1.10
    restart: always
    ports:
      - "25:25"
      - "143:143"
      - "587:587"
      - "993:993"
      - "465:465"
      - "80:80"
      - "443:443"
    volumes:
      - ./data/certs:/certs
      - ./data/dkim:/dkim
    environment:
      - DOMAIN=flowvello.com
      - HOSTNAMES=mail.flowvello.com
      - TLS_FLAVOR=letsencrypt
      - LETSENCRYPT_EMAIL=admin@flowvello.com

  smtp:
    image: mailu/postfix:1.10
    restart: always
    volumes:
      - ./data/mail:/data
      - ./data/dkim:/dkim
    environment:
      - DOMAIN=flowvello.com
      - HOSTNAME=mail.flowvello.com
      - POSTFIX_MESSAGE_SIZE_LIMIT=52428800
      - POSTFIX_SMTPD_TLS_SECURITY_LEVEL=may
      - POSTFIX_SMTP_TLS_SECURITY_LEVEL=may

  imap:
    image: mailu/dovecot:1.10
    restart: always
    volumes:
      - ./data/mail:/data
    environment:
      - DOVECOT_MAILBOX_FORMAT=maildir
      - DOVECOT_QUOTA=5G

  antispam:
    image: mailu/rspamd:1.10
    restart: always
    volumes:
      - ./data/rspamd:/var/lib/rspamd
    environment:
      - RSPAMD_PASSWORD=CHANGE_ME
      - REDIS_HOST=redis
      - REDIS_PORT=6379

  antivirus:
    image: mailu/clamav:1.10
    restart: always
    volumes:
      - ./data/clamav:/var/lib/clamav

  dkim:
    image: mailu/opendkim:1.10
    restart: always
    volumes:
      - ./data/dkim:/dkim

  admin:
    image: mailu/admin:1.10
    restart: always
    volumes:
      - ./data:/data
    environment:
      - DOMAIN=flowvello.com
      - HOSTNAME=mail.flowvello.com
      - ADMIN_PW=CHANGE_ME
      - SECRET_KEY=CHANGE_ME_32_CHARS
      - DB_ENGINE=sqlite

  redis:
    image: redis:7-alpine
    restart: always
    volumes:
      - ./data/redis:/data
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru

  postgres:
    image: postgres:16-alpine
    restart: always
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=mailbox
      - POSTGRES_USER=mailbox
      - POSTGRES_PASSWORD=CHANGE_ME

  minio:
    image: minio/minio:latest
    restart: always
    volumes:
      - ./data/minio:/data
    environment:
      - MINIO_ROOT_USER=minioadmin
      - MINIO_ROOT_PASSWORD=CHANGE_ME
    command: server /data --console-address ":9001"

  prometheus:
    image: prom/prometheus:latest
    restart: always
    volumes:
      - ./config/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./data/prometheus:/prometheus

  grafana:
    image: grafana/grafana:latest
    restart: always
    volumes:
      - ./data/grafana:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=CHANGE_ME


## Critical Rspamd Overrides (deliverability focus)

### overrides/rspamd/dkim_signing.conf
dkim_signing {
  allow_username_mismatch = true;
  sign_local = true;
  sign_authenticated = true;
  use_esld = true;
  selector_map = "/etc/rspamd/dkim_selectors.map";
  key_path = "/dkim/$domain.$selector.key";
}

### overrides/rspamd/options.inc
options {
  greylist = true;
  greylist_whitelists = ["SPF_WHITELIST", "DKIM_WHITELIST"];
  phishing_enabled = true;
  phishing_check_all = true;
  neural_enabled = true;
}

### overrides/rspamd/antivirus.conf
antivirus {
  action = "reject";
  message = "Infected mail rejected";
  log_clean = true;
  servers = "antivirus:3310";
}

## Deliverability Hardening Checklist

### IP Reputation
- Request clean IP from provider (Hetzner/Contabo support)
- Warmup schedule: Week 1: 50/day, Week 2: 200/day, Week 3: 1000/day, Week 4: 5000/day
- Monitor via: mxtoolbox.com, senderbase.org, google postmaster tools

### Authentication
- SPF: v=spf1 ip4:<IP> ip6:<IP> ~all (no +all!)
- DKIM: 2048-bit RSA keys, rotate annually
- DMARC: Start p=none -> p=quarantine -> p=reject
- PTR: Matches mail hostname exactly
- TLS: Valid Let's Encrypt cert, TLS 1.2+ only

### List Management
- Suppression list (bounces, complaints, unsubscribes)
- Double opt-in for any marketing
- One-click unsubscribe header (List-Unsubscribe)
- Honor List-Unsubscribe-Post (RFC 8058)

### Monitoring
- Google Postmaster Tools configured
- Microsoft SNDS configured
- DMARC reports parsed weekly
- Blacklist monitoring (Spamhaus, Barracuda, SURBL, etc.)

## Backup Strategy

Daily encrypted backup script to MinIO with monthly restore verification.

## Success Criteria (Definition of Done)

| Test | Tool/Method | Pass Criteria |
|------|-------------|---------------|
| Send to Gmail | mail-tester.com | Score 10/10 |
| Send to Outlook | mail-tester.com | Score 10/10 |
| Receive from Gmail | Manual test | Appears in webmail inbox |
| SPF Check | mxtoolbox.com | Pass |
| DKIM Check | mxtoolbox.com | Pass |
| DMARC Check | dmarcanalyzer.com | Pass |
| PTR Check | mxtoolbox.com | Matches mail.flowvello.com |
| TLS Check | testssl.sh | Grade A+ |
| Spam Filter | Send spam test | Caught by Rspamd |
| Virus Filter | EICAR test | Blocked by ClamAV |
| Backup Restore | Monthly drill | Full restore < 30 min |

## Timeline: 2-3 Weeks

| Week | Tasks |
|------|-------|
| 1 | VPS provision, DNS, Mailu deploy, TLS, basic send/receive |
| 2 | DKIM/DMARC/SPF config, Rspamd tuning, ClamAV, deliverability testing |
| 3 | Backup automation, monitoring setup, documentation, load testing |

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| IP blacklisted on day 1 | Pre-check IP reputation, request clean IP, have backup IP |
| Emails to spam | mail-tester.com iteration, Rspamd training, warmup schedule |
| TLS cert renewal fails | Monitor cert expiry, auto-renewal via Let's Encrypt + Traefik |
| Data loss | Daily encrypted backups to separate MinIO, monthly restore test |
| Abuse/spam from tenants | Rate limits, outbound scanning, auto-suspend on complaints |
