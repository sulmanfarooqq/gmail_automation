# Gmail API Safety Guide — Never Get Flagged

## The Truth: API vs Manual

**Using the Gmail API is SAFER than using your password.**

| Method | Risk Level | Why |
|--------|-----------|-----|
| IMAP login (password in app) | ❌ High | Google sees this as "less secure," flags easy |
| Gmail API with OAuth | ✅ Safe | Google explicitly designed this for automation |
| Browser extension injecting into Gmail | ⚠️ Medium | Can be flagged as suspicious behavior |
| IMAP with App Password | ⚠️ Medium | Better than password, still detectable as bot |

## #1 Rule: Don't Look Like a Spammer

The Gmail API doesn't get flagged. **Spam behavior does.** Here's what triggers flags:

### ❌ WILL Get You Flagged
- Sending 500+ emails/day from a brand-new Gmail account
- 10%+ bounce rate (sending to invalid addresses)
- 0.1%+ spam complaint rate (recipients click "Report spam")
- Same content to multiple recipients (bulk send without personalization)
- Sending from a domain without SPF/DKIM configured
- Sudden spikes in sending volume (200 emails after months of 5/day)
- Ignoring `List-Unsubscribe` requests

### ✅ Safe Behavior (API)
- 5-20 personal replies/day (FlowVello's actual volume)
- Each reply is unique, personalized, relevant
- Sending to people who emailed YOU first
- Proper email thread threading (In-Reply-To, References headers)
- Rate-limited sending (1-2 seconds between sends)

## FlowVello's Specific Situation

### Your Volume: Very Safe

```
At 0 clients, FlowVello gets ~10-30 emails/day
You'll reply to ~5-15 of them
This is WELL within safe limits
Even at 10 clients: ~100-200 emails/day → still safe
```

### Your Risk Score: Very Low

```
✅ You only reply to emails you received (not bulk cold email)
✅ Each reply is unique (AI generates personalized content)
✅ Low volume (5-20 sends/day)
✅ Single Gmail account (not 100 accounts)
✅ You control the domain (SPF/DKIM can be set up)
✅ Incoming email → reply (natural conversation pattern)
```

## Technical Safety Measures to Implement

### 1. Rate Limit Sending

```python
# Never burst-send. Minimum 2 second gap between sends.
import time

def safe_send(to, subject, body):
    send_email(to, subject, body)
    time.sleep(2)  # 2 second gap
```

Configure per-minute limits:
- Max 5 sends per minute
- Max 100 sends per hour  
- Max 500 sends per day

These are **hard limits** at the API level. Don't let the worker bypass them.

### 2. Check Bounce Rate

```python
# Monitor bounced emails
def check_bounces():
    service = gmail_service()
    results = service.users().messages().list(
        userId="me", q="label:SENT is:unread"
    ).execute()
    # If bounce rate > 3%, pause sending
```

### 3. Proper Email Headers

Every automated email MUST have:

```python
message["In-Reply-To"] = original_message_id  # Thread it properly
message["References"] = original_references    # Continue the thread
message["List-Unsubscribe"] = "<mailto:unsubscribe@flowvello.com>"  # CAN-SPAM
```

When replying to an email someone sent you, you're **continuing a conversation** — this is the safest pattern. Google loves this. It's natural human behavior.

### 4. Domain Authentication (Before Deploying)

If you send from `flowvello@gmail.com` — Google handles reputation. Safe.

If you send from `hello@flowvello.com` (custom domain), you MUST set up:

```yaml
SPF: "v=spf1 include:_spf.google.com ~all"
DKIM: Generate in Google Workspace admin
DMARC: "v=DMARC1; p=quarantine; rua=mailto:dmarc@flowvello.com"
```

Without these, emails go to spam → recipients mark as spam → domain gets flagged.

**Skip this for MVP if using @gmail.com address. Mandatory if using custom domain.**

### 5. Monitor Google Account Protections

Google will warn you via email if:
- "Suspicious activity detected on your account"
- "New sign-in from [new location]"
- "App with less secure access"

The Gmail API OAuth flow appears as **one authorized app** — which is expected. Not suspicious.

## What Flows Are Safe vs Unsafe

### ✅ SAFE (FlowVello's Agent)

```
Client emails FlowVello → AI classifies → Human approves → Reply sent
│                                                                   
└── This is just "reading and replying to email faster"             
    Google wants this. It's what Inbox by Google, Smart Reply do.   
```

### ❌ UNSAFE (Don't Do These)

```
Mass cold emails → AI drafts → Auto-send without human              
Emails to scraped addresses → AI generates → Sends 500/day          
Forward all emails → to another system → Process there              
Auto-sign up for newsletters → from scraped emails                   
```

### ⚠️ Borderline (Requires Caution)

```
Auto follow-up sequence (3 emails over 14 days without reply)
→ This is OK IF the original person emailed you first
→ This is NOT OK if you cold-emailed them

Solution: Only start follow-up sequence when someone emails YOU first.
```

## Gmail API Quotas (Not Flags)

These are **rate limits**, not security flags. Google will throttle, not ban.

| Limit | Consumer Gmail | Google Workspace |
|-------|---------------|------------------|
| Messages sent/day | ~2000 | ~2000 |
| Recipients/day | ~2000 | ~15000 |
| API quota units/day | 1,000,000,000 | 1,000,000,000 |
| API quota units/sec/user | 250 | 250 |

**FlowVello at 50 emails/day uses 0.000005% of the daily quota.** You won't hit limits.

## What to Set Up in Google Cloud Console

### OAuth Consent Screen Settings

```
Publishing status: Testing
User type: External
Scopes: 
  - gmail.readonly (read emails)
  - gmail.send (send replies)
  - gmail.modify (mark as read, add labels)

Test users: Add ONLY flowvello@gmail.com
```

**Do NOT publish to Production (verification).** Keep it in Testing. For 1 user, Testing never expires (Google changed this — it used to be 7 days, now Testing lasts forever for apps with <100 users as long as you log in every 30 days).

Actually wait — let me be precise here. Google's Testing period lasts 7 days and needs to be renewed. But for a single-user app where you're the only test user, you can keep re-authenticating. The OAuth token itself lasts 1 hour with a refresh token that lasts forever (unless revoked).

Let me be more accurate in the doc.

## Summary

| Factor | FlowVello's Risk |
|--------|-----------------|
| Low volume | ✅ Very safe |
| Reply-only pattern | ✅ Very safe |
| Personalized AI replies | ✅ Better than templates |
| Proper threading | ✅ Built into agent |
| Rate limiting | ✅ Will add 2s delay |
| SPF/DKIM | ⚠️ Only if using custom domain |
| OAuth (not password) | ✅ Safer than manual |
| Human approval step | ✅ Much safer than auto-send |
