# Phase 7: Multi-Channel Specification (WhatsApp + Prep for Voice)

## Objective
Add WhatsApp Business API integration as second channel, with architecture ready for voice/website chat.

## Tech Stack
- WhatsApp Business API (Meta) or Twilio/MessageBird
- Same AI Engine + Automation Engine + CRM
- Shared contact/conversation model

## Architecture

```
                    AI CUSTOMER ENGINE
                           |
           ┌───────────────┼───────────────┐
           |               |               |
           v               v               v
      WhatsApp         Email            Voice (future)
        (Meta)         (SMTP/IMAP)      (Twilio/Telnyx)
           |               |               |
           └───────────────┼───────────────┘
                           v
                      Unified Conversation
                           |
                    ┌──────┴──────┐
                    v             v
               CRM + KB      Automation
```

## Data Model

```sql
-- Channels
CREATE TABLE channels (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    type VARCHAR(20) NOT NULL,  -- email, whatsapp, voice, chat
    name VARCHAR(100),
    config JSONB,  -- API keys, webhook URLs, templates
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Conversations (unified across channels)
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    channel_id UUID REFERENCES channels(id),
    contact_id UUID REFERENCES contacts(id),
    external_id VARCHAR(255),  -- WhatsApp contact ID, email thread ID
    subject VARCHAR(500),  -- For email
    status VARCHAR(20) DEFAULT 'open',  -- open, pending, closed, snoozed
    assignee_id UUID REFERENCES users(id),
    tags TEXT[],
    metadata JSONB,
    last_message_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Messages (unified)
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    conversation_id UUID REFERENCES conversations(id),
    channel_id UUID REFERENCES channels(id),
    direction VARCHAR(10) NOT NULL,  -- inbound, outbound
    type VARCHAR(20) DEFAULT 'text',  -- text, image, document, audio, video, location, template
    content TEXT,
    media_url VARCHAR(500),
    media_mime VARCHAR(100),
    external_id VARCHAR(255),  -- WhatsApp message ID, email Message-ID
    status VARCHAR(20) DEFAULT 'sent',  -- sent, delivered, read, failed
    ai_processed BOOLEAN DEFAULT FALSE,
    ai_classification_id UUID REFERENCES email_classifications(id),
    created_at TIMESTAMPTZ DEFAULT now()
);

-- WhatsApp specific
CREATE TABLE whatsapp_templates (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    name VARCHAR(100) NOT NULL,
    language VARCHAR(10) DEFAULT 'en_US',
    category VARCHAR(20),  -- marketing, utility, authentication
    header_type VARCHAR(20),  -- text, image, document, video
    header_content TEXT,
    body_text TEXT NOT NULL,
    footer_text TEXT,
    buttons JSONB,  -- Quick reply, URL, phone
    status VARCHAR(20) DEFAULT 'pending',  -- pending, approved, rejected
    meta_template_id VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT now()
);
```

## WhatsApp Integration

### 1. Webhook Handler
```python
# POST /webhook/whatsapp/{tenant_id}
async def whatsapp_webhook(tenant_id: str, payload: dict):
    # Verify signature (X-Hub-Signature-256)
    # Parse message: text, media, interactive, template
    # Create/update conversation
    # Store message
    # Publish to Redis stream: "whatsapp:received:{tenant_id}"
    # AI Engine consumes -> classify -> workflow
```

### 2. Send Message
```python
async def send_whatsapp(tenant_id: str, to: str, message: WhatsAppMessage):
    # Get channel config (phone_number_id, access_token)
    # Format per message type (text, template, media)
    # POST to Graph API
    # Handle rate limits (per phone number)
    # Store outbound message
    # Return message ID for tracking
```

### 3. Template Management
- Create templates in admin panel
- Submit to Meta for approval
- Sync approved templates
- Use in workflows (template messages for outbound)

### 4. Session Management
- 24-hour customer service window (free-form)
- Outside window: template messages only
- Track session state per contact

## Unified Inbox (Client Portal)

- Single conversation list across channels
- Channel indicator (email, WhatsApp, voice)
- Same threading model
- Channel-specific compose (WhatsApp: templates, media)
- Shared AI: classification, drafting, KB work across channels

## Contact Unification

- One contact record per person
- Multiple channel identities: email, WhatsApp phone, phone
- Merge logic: email + phone matching
- Conversation history across channels

## Automation Across Channels

Workflow triggers:
- `whatsapp_received` - new WhatsApp message
- `whatsapp_template_sent` - template delivered
- `conversation_opened` - any channel

Actions:
- `send_whatsapp` - text, template, media
- `send_whatsapp_template` - approved template
- Cross-channel: email received -> WhatsApp follow-up

## Testing

- WhatsApp Business API sandbox
- Meta webhook verification
- Template approval flow
- Rate limit handling
- Media upload/download
- Session window transitions

## Timeline: 2-3 Weeks

| Week | Focus |
|------|-------|
| 1 | WhatsApp webhook, send/receive, templates |
| 2 | Unified conversation model, contact merge, UI |
| 3 | Cross-channel workflows, testing, docs |
