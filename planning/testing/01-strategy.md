# Testing Strategy

## Overview
Comprehensive testing approach across all 8 phases with unit, integration, E2E, contract, performance, and security testing.

## Test Pyramid

```
                    /\
                   /  \     E2E Tests (Playwright) - 10%
                  /____\    
                 /      \   Integration Tests - 20%
                /________\  
               /          \ Unit Tests - 70%
              /____________\
```

## Phase-Specific Testing

### Phase 1: Mail Infrastructure

**Unit Tests** (pytest)
- DNS record validation functions
- DKIM key generation/validation
- SPF/DMARC parsing
- Backup script functions

**Integration Tests** (Testcontainers)
```python
# test_mail_infrastructure.py
@pytest.fixture
def mail_stack():
    with DockerCompose("docker-compose.test.yml") as compose:
        yield compose

def test_send_receive(mail_stack):
    # Send via SMTP to local Postfix
    # Verify received via IMAP
    # Check SPF/DKIM/DMARC headers
    
def test_spam_filtering(mail_stack):
    # Send known spam samples
    # Verify Rspamd scores > threshold
    # Verify moved to spam folder
    
def test_virus_scanning(mail_stack):
    # Send EICAR test file
    # Verify ClamAV rejects
```

**Deliverability Tests**
- mail-tester.com API integration (automated weekly)
- GlockApps / Mailgun Inbox Placement (monthly)
- Google Postmaster Tools metrics collection
- Microsoft SNDS monitoring
- Blacklist checks (Spamhaus, Barracuda, SURBL)

**Chaos Tests**
- Kill Postfix -> verify queue persistence
- Kill Dovecot -> verify client reconnection
- Network partition -> verify queue retry
- Disk full -> verify graceful degradation

### Phase 2: Webmail

**Unit Tests** (Vitest)
- Email parsing (RFC5322, MIME)
- Thread building algorithm
- Search query parser
- Date formatting/localization
- Keyboard shortcut handler
- Contact deduplication logic

**Component Tests** (React Testing Library)
- EmailList virtualization
- ComposeForm validation
- RichTextEditor (TipTap) extensions
- Attachment upload progress
- Folder tree navigation
- Search results highlighting

**Integration Tests**
- IMAP connection pool lifecycle
- SMTP send with attachments
- Draft auto-save/restore
- Real-time SSE connection
- Offline draft persistence (IndexedDB)

**E2E Tests** (Playwright)
```typescript
// e2e/mail.spec.ts
test('send and receive email', async ({ page }) => {
  await login(page, 'user@flowvello.com');
  await composeAndSend(page, { to: 'external@gmail.com', subject: 'Test' });
  // Verify in Sent folder
  await gotoFolder(page, 'sent');
  await expect(page.locator('text=Test')).toBeVisible();
  
  // Receive reply (via test IMAP account)
  await waitForEmail(page, 'inbox', 'Re: Test');
  await openThread(page, 'Re: Test');
  await expect(page.locator('.thread-body')).toContainText('Reply content');
});

test('threading', async ({ page }) => {
  // Send 3 emails in same thread
  // Verify grouped in thread view
  // Expand/collapse
});

test('search operators', async ({ page }) => {
  await search(page, 'from:john has:attachment before:2024-01-01');
  // Verify results match
});
```

**Visual Regression** (Chromatic)
- Inbox (light/dark, desktop/tablet/mobile)
- Compose modal
- Thread view
- Settings pages
- Empty states
- Loading skeletons

**Accessibility** (axe-core)
- Automated in CI
- Manual: screen reader (NVDA/VoiceOver)
- Keyboard-only navigation
- Color contrast

### Phase 3: Admin Panel

**Unit Tests**
- Tenant CRUD validation
- DNS verification logic
- DKIM key generation
- Plan limit enforcement
- Billing calculation

**Integration Tests**
- Full tenant creation flow
- Domain verification wizard
- Impersonation token generation
- Audit log completeness

**E2E Tests**
- Super-admin creates tenant -> verifies domain -> creates mailboxes
- Support impersonates tenant -> resets password
- Billing views subscription -> upgrades plan

### Phase 4: AI Layer

**Unit Tests** (pytest)
```python
# test_classifier.py
@pytest.mark.parametrize("email,expected_category", [
    ("Hi, I'd like a quote for 100 units...", "quote_request"),
    ("My order #12345 is broken...", "complaint"),
    ("Invoice #INV-2024-001 attached...", "invoice"),
])
async def test_classification(classifier, email, expected_category):
    result = await classifier.classify(email)
    assert result.category == expected_category
    assert result.confidence > 0.7
```

**Golden Dataset Evaluation**
- 500 labeled emails per category (13 categories = 6,500 total)
- Metrics: Accuracy, Precision, Recall, F1 per category + macro avg
- Run on every prompt/model change
- Track regression in CI

**RAG Evaluation**
- 200 question/answer pairs per tenant type
- Metrics: Recall@5, MRR, Answer correctness (LLM judge)
- Citation accuracy

**Draft Quality Evaluation**
- 100 email threads with human-written replies
- LLM-as-judge: rate draft 1-5 on relevance, tone, completeness
- Target: > 4.0 average, > 60% "would send with minor edits"

**Cost/Performance Tests**
- Token counting per request
- Latency percentiles (p50, p95, p99)
- Cache hit rate
- Cost per 1000 emails

### Phase 5: Automation Engine

**Unit Tests**
- State machine transitions
- Condition evaluation (all types)
- Action execution (mocked externals)
- Delay scheduling
- Context merging
- Edge condition routing

**Integration Tests**
```python
# test_workflows.py
async def test_lead_workflow(engine, mock_smtp, mock_crm):
    # Trigger: email received (classified as lead)
    # Verify: lead created in CRM
    # Verify: draft reply created
    # Verify: draft sent (approval=suggest -> manual send)
    # Advance time 24h
    # Verify: followup sent
    # Advance time 72h
    # Verify: Slack notification sent
```

**Property-Based Tests** (hypothesis)
- Random workflow DAGs -> verify no cycles
- Random context merges -> verify no key collisions
- Random delay sequences -> verify ordering

**Chaos Tests**
- Kill engine mid-execution -> verify recovery from checkpoint
- Database failure -> verify graceful retry
- External API timeout -> verify compensation

### Phase 6: CRM

**Unit Tests**
- Lead scoring algorithm
- Pipeline probability calculation
- Forecast weighting
- Contact merge logic
- Activity timeline ordering

**Integration Tests**
- Email -> Lead auto-creation
- Lead -> Deal conversion
- Task completion -> Deal stage advance
- Email tracking pixel -> activity log

**E2E Tests**
- Kanban drag-drop updates status
- Pipeline view filters
- Report generation

### Phase 7: Multi-Channel

**Unit Tests**
- WhatsApp signature verification
- Template variable substitution
- Session window logic
- Contact unification (email + phone)

**Integration Tests**
- WhatsApp webhook -> conversation -> AI -> workflow
- Cross-channel: email -> WhatsApp follow-up
- Media handling (upload, download, thumbnail)

**E2E Tests** (requires WhatsApp Business test number)
- Receive WhatsApp -> appears in unified inbox
- Reply via WhatsApp -> delivered
- Template send -> status tracking

### Phase 8: SaaS Platform

**Unit Tests**
- Plan limit enforcement
- Usage aggregation
- Overage calculation
- Proration on plan change
- Trial expiration

**Integration Tests**
- Full onboarding flow (10 steps)
- Plan upgrade/downgrade
- Custom domain provisioning
- Branding application
- GDPR data export
- Tenant deletion

**E2E Tests**
- Signup -> domain -> mailboxes -> KB -> AI -> workflows -> go live
- Billing portal: update card, view invoices, cancel

## Cross-Cutting Testing

### Contract Testing (Pact)
- tRPC procedures: consumer-driven contracts
- AI Engine API: provider contracts
- Webhook payloads: schema validation

### Performance Tests (k6)
```javascript
// load-test.js
export const options = {
  stages: [
    { duration: '2m', target: 100 },   // Ramp up
    { duration: '5m', target: 100 },   // Steady
    { duration: '2m', target: 500 },   // Spike
    { duration: '5m', target: 500 },   // Sustained
    { duration: '2m', target: 0 },     // Ramp down
  ],
  thresholds: {
    'http_req_duration{type:api}': ['p(95)<500'],
    'http_req_failed': ['rate<0.01'],
    'ws_connecting': ['p(95)<100'],
  },
};

expo
