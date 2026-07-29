# AI Pipeline Design

## AI Provider Abstraction Layer

```typescript
// ai/providers/interface.ts
interface AIProvider {
  classifyEmail(params: ClassifyParams): Promise<ClassificationResult>;
  generateReply(params: ReplyParams): Promise<ReplyResult>;
  extractData(params: ExtractParams): Promise<ExtractResult>;
  summarizeThread(params: SummaryParams): Promise<SummaryResult>;
  analyzeIntent(params: IntentParams): Promise<IntentResult>;
  analyzeDocument(params: DocumentParams): Promise<DocumentResult>;
  generateFollowUp(params: FollowUpParams): Promise<FollowUpResult>;
}

// ai/providers/gemini.ts
// ai/providers/openai.ts
// ai/providers/anthropic.ts

// ai/provider-factory.ts
function getProvider(orgId: string): AIProvider {
  const config = getAiConfig(orgId);
  switch (config.preferredProvider) {
    case 'gemini': return new GeminiProvider(config);
    case 'openai': return new OpenAIProvider(config);
    case 'anthropic': return new AnthropicProvider(config);
  }
}
```

## Email Processing Pipeline

```
Raw Email (Gmail API)
    │
    ▼
[Step 1] Parse & Normalize
    │ Extract headers, body, attachments
    │ Strip signatures (regex-based)
    │ Strip quoted replies (Gmail quoted message detection)
    │ Normalize encoding (UTF-8)
    │
    ▼
[Step 2] Pre-classification Check
    │ Check if known sender (existing CRM contact)
    │ Check if part of existing thread
    │ Check if unsubscribe/autoresponder (skip AI)
    │ Check if spam score > threshold (skip)
    │
    ▼
[Step 3] AI Classification
    │ Input: Clean email body + subject + sender
    │ Output: Intent, Priority, Sentiment, Lead Score
    │
    ▼
[Step 4] Data Extraction
    │ If lead → extract name, company, phone, service
    │ If support → extract issue, urgency
    │ If meeting → extract date preferences
    │ If invoice → extract amount, due date
    │
    ▼
[Step 5] Knowledge Base Enrichment
    │ Fetch matching FAQs
    │ Fetch company services info
    │ Fetch previous conversation context
    │
    ▼
[Step 6] Reply Generation
    │ Input: Email + Classification + KB Context + Conversation History
    │ Output: Draft reply
    │ Post-processing: Replace placeholders, validate links
    │
    ▼
[Step 7] Human Approval Decision
    │ Auto-send? → Check rules
    │ Needs approval? → Queue for human review
    │
    ▼
[Step 8] Workflow Execution
    │ If lead → create CRM contact, assign sales, notify
    │ If support → check KB, generate answer or escalate
    │ If meeting → check calendar, send options
```

## Prompt Engineering

### Classification Prompt (System)

```
You are an AI email classifier for {agency_name}. 
Classify the following email into exactly one of these categories:
- lead: Someone inquiring about services, potential new client
- customer_support: Existing client with an issue
- sales_inquiry: Existing lead asking about pricing/services
- billing: Payment, invoice, billing questions
- complaint: Negative feedback or complaint
- partnership: Collaboration or partnership request
- newsletter: Marketing/promotional email
- spam: Unsolicited commercial email
- internal: Company internal communication
- meeting_request: Request to schedule a meeting
- other: Anything that doesn't fit above

Also provide:
- priority: low|medium|high|urgent
- sentiment: very_negative|negative|neutral|positive|very_positive
- lead_score: 0-100 (how likely this is a sales opportunity)
- requires_reply: boolean
- requires_approval: boolean (if reply involves pricing, contracts, complaints)
- summary: one-line summary of the email

{agency_rules_context}

Return JSON only.
```

### Reply Generation Prompt (System)

```
You are an AI email assistant for {agency_name}.
Generate a professional email reply based on:

1. The incoming email
2. The company information below
3. Previous conversation context
4. Classification result

Company: {company_name}
Services: {services}
Tone: {tone_of_voice}
Default CTA: {default_cta}

Rules:
- Never promise guaranteed results
- Never offer discounts without approval
- Never discuss internal processes
- Always include the CTA when appropriate
- Keep replies concise and professional
- Use {sender_name} in the greeting

Relevant FAQs: {matching_faqs}
Case Studies: {matching_case_studies}

Context: This email was classified as {intent} with priority {priority}.

Generate a draft reply. Return JSON:
{
  "subject": "Re: {original_subject}",
  "body": "email body here",
  "tone": "professional|friendly|formal",
  "needs_approval": true|false,
  "approval_reason": "reason if needs_approval"
}
```

## Cost Optimization Strategy

| Model | Use Case | Cost | When to Use |
|-------|----------|------|-------------|
| Gemini Flash | Classification, summarization | Lowest | Default for all classification |
| Gemini Pro | Reply generation, complex extraction | Medium | Default for replies |
| GPT-4o | Complex support, legal, complaints | Highest | Fallback only |
| Claude Haiku | Fast replies, simple FAQ | Low | Alternative to Gemini |

- Cache classification results for similar emails
- Batch AI calls where possible
- Use streaming for draft generation (better UX)
- Log all AI calls with cost tracking per organization

## Error Handling

| Failure Mode | Action |
|-------------|--------|
| AI provider down | Failover to next provider |
| Rate limited | Exponential backoff + queue |
| Invalid response (not JSON) | Retry with stricter prompt |
| Content filtered | Log warning, draft manual reply instead |
| Timeout | Retry with smaller context |
