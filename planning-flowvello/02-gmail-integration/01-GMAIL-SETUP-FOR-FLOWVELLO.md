# Gmail Integration Plan for FlowVello

## Google Cloud Project Setup

### Step 1: Create Project
1. Go to https://console.cloud.google.com
2. Create new project: `flowvello-gmail-agent`
3. Enable **Gmail API**
4. Enable **Google Pub/Sub API**

### Step 2: OAuth Consent Screen
```
User Type: External (or Internal if you use a Google Workspace)
Scopes needed:
  - https://www.googleapis.com/auth/gmail.readonly
  - https://www.googleapis.com/auth/gmail.send
  - https://www.googleapis.com/auth/gmail.modify
  - https://www.googleapis.com/auth/pubsub

Test users: Add your flowvello@gmail.com
```

### Step 3: Credentials
```
Type: Web application
Authorized redirect URIs:
  - http://localhost:3000/api/gmail/callback (dev)
  - https://flowvello-gmail.herokuapp.com/api/gmail/callback (prod)
```

## How Gmail Integration Works

```
                    ┌─────────────────────┐
                    │  flowvello@gmail.com │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Google Pub/Sub      │
                    │  (Watch on inbox)    │
                    └──────────┬──────────┘
                               │ POST /webhooks/gmail
                    ┌──────────▼──────────┐
                    │  Your Express API    │
                    │  Receives notification│
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Fetch full email    │
                    │  via Gmail API       │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Store in PostgreSQL │
                    │  Queue AI processing │
                    └─────────────────────┘
```

## OAuth Flow (Single User — FlowVello)

```
1. User clicks "Connect Gmail"
2. Redirected to Google OAuth page
3. User grants permissions
4. Google redirects back with auth code
5. Backend exchanges code for access_token + refresh_token
6. Tokens stored in database (encrypted)
7. Backend sets up Gmail Watch (Pub/Sub)
8. Done. Inbox syncing starts.
```

## Token Management

```typescript
// Critical: Access tokens expire in 3600 seconds (1 hour)
// Refresh tokens expire NEVER (but can be revoked)
// You MUST handle silent refresh

interface GmailTokens {
  access_token: string;    // Expires in 1 hour
  refresh_token: string;   // Long-lived
  expiry_date: number;     // Timestamp
}

// Before every Gmail API call:
if (token.expiry_date < Date.now() + 60000) {
  // Refresh the token
  const { credentials } = await oauth2Client.refreshToken(token.refresh_token);
  // Update stored tokens
  // Then proceed with API call
}
```

## Pub/Sub Watch Setup

```typescript
// Called once after OAuth success
async function setupWatch(auth: OAuth2Client) {
  const gmail = google.gmail({ version: 'v1', auth });
  const res = await gmail.users.watch({
    userId: 'me',
    requestBody: {
      topicName: 'projects/flowvello-gmail-agent/topics/gmail-notifications',
      labelIds: ['INBOX'],
      labelFilterAction: 'include',
    },
  });
  // Store historyId for incremental sync
  // Store watch expiration (7 days — needs renewal)
}

// Renewal: Setup a cron job to re-watch every 6 days
```

## Webhook Endpoint

```typescript
// POST /api/webhooks/gmail
// Receives Pub/Sub push notifications
// Contains historyId — fetch changes since last sync

async function handleNotification(payload) {
  const historyId = payload.message.data; // base64 decoded
  const changes = await gmail.users.history.list({
    userId: 'me',
    startHistoryId: storedHistoryId,
    historyTypes: ['messageAdded'],
  });
  
  for (const history of changes.data.history) {
    for (const message of history.messages) {
      await queueEmailProcessing(message.id);
    }
  }
  
  // Update stored historyId
  await updateHistoryId(historyId);
}
```

## Polling Fallback

```typescript
// Pub/Sub can miss messages or have delays
// Run a polling job every 5 minutes as backup

async function pollForNewEmails() {
  const res = await gmail.users.messages.list({
    userId: 'me',
    q: 'is:unread',                    // Only unread
    maxResults: 10,
  });
  
  for (const msg of res.data.messages || []) {
    if (!await isMessageProcessed(msg.id)) {
      await queueEmailProcessing(msg.id);
    }
  }
}
```

## Security Notes for FlowVello

- Store tokens **encrypted** in PostgreSQL (AES-256-GCM)
- Never send tokens to frontend
- Frontend only gets `isConnected: true/false`
- If using Heroku, configure GOOGLE_OAUTH vars in Heroku Config Vars, not in code
- For Pakistani market: make sure your callback URLs work with local internet (no unexpected redirect blocking)
