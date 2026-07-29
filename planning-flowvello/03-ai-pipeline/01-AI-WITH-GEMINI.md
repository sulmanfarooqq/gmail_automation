# AI Pipeline — Gemini for FlowVello

## Why Gemini (Not OpenAI/Claude)

| Factor | Gemini | GPT-4o-mini | Claude Haiku |
|--------|--------|-------------|--------------|
| Cost per 1K emails | ~$0.50 | ~$2.00 | ~$1.50 |
| Urdu/Roman Urdu support | Good | Poor | Poor |
| Speed | Fast | Medium | Fast |
| Free tier | Yes (60 req/min) | No | No |
| Google ecosystem | Native with Gmail | No | No |

**FlowVello will handle Pakistani clients. Urdu/Roman Urdu support matters.** Gemini is the best choice.

## What the AI Does

### 1. Email Classification

```
Input: Email subject + body (stripped)
Output: JSON with intent, priority, sentiment, is_lead

Prompt (System):
You are FlowVello's AI email assistant. Classify this email:

Categories:
- lead: Someone inquiring about AI automation services
- client_support: Existing client asking for help
- partnership: Collaboration or partnership offer
- billing: Payment/invoice related
- spam: Promotional or irrelevant
- other: Anything else

Also detect:
- is_lead: true/false (did they ask about buying a service?)
- priority: low/medium/high/urgent
- sentiment: negative/neutral/positive
- requested_service: what service they want (if lead)
- customer_name: extracted name
- phone: extracted phone number (Pakistani numbers +92...)
- company: extracted company name

Respond ONLY with valid JSON.
```

### 2. Reply Generation

```
Input: Original email + classification + knowledge base
Output: Draft reply

Prompt (System):
You are FlowVello's AI email assistant. Draft a reply to this email.

Company: FlowVello — AI Automation Agency
Services:
- AI Chatbots & Voice Agents
- WhatsApp Automation Systems
- Email Automation
- CRM & Lead Management
- Custom AI Workflows
- Property Deal Systems for Real Estate

Location: Mirpur, Pakistan
Tone: Professional, helpful, confident
Languages: English, Urdu, Roman Urdu
Default CTA: Book a free discovery call

Incoming email: [email]
Classification: [intent]

Rules:
- If they ask about services → explain briefly, offer a call
- If they ask pricing → give range, offer custom quote
- If they're a lead → include CTA to book a call
- If support → be helpful, offer timeline
- If complaint → apologize, offer solution
- If partnership → show interest, suggest meeting
- Keep it concise (3-5 sentences)
- Sign off with "Best, FlowVello Team"

Generate a draft reply in the language the email was written in.
Respond ONLY with valid JSON:
{
  "subject": "Re: [original subject]",
  "body": "draft reply here",
  "tone": "professional",
  "needs_approval": true/false
}
```

### 3. Follow-up Generation

```
Input: Original email + previous reply + no response in N days
Output: Follow-up email

Prompt (System):
Generate a polite follow-up email. The recipient hasn't replied to our previous email.

Previous email: [email]
Our reply: [reply]
Days since: [N]

Tone: Polite, not pushy
Goal: Get a response without being annoying

Version 1 (Day 3): "Just checking if you saw this..."
Version 2 (Day 7): "Still interested? Happy to answer questions."
Version 3 (Day 14): "Last follow-up. If timing isn't right, no problem."
```

## AI Abstraction Layer (Architecture)

```typescript
// src/services/ai.ts
// Single provider for now (Gemini), but structured for swap

interface AIService {
  classifyEmail(email: EmailData): Promise<Classification>;
  generateReply(data: ReplyInput): Promise<Draft>;
  generateFollowUp(data: FollowUpInput): Promise<string>;
  summarizeThread(thread: ThreadData): Promise<string>;
}

class GeminiService implements AIService {
  private model: GenerativeModel;
  
  constructor(apiKey: string) {
    const genAI = new GoogleGenerativeAI(apiKey);
    this.model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });
  }

  async classifyEmail(email: EmailData): Promise<Classification> {
    const prompt = this.buildClassificationPrompt(email);
    const result = await this.model.generateContent(prompt);
    return JSON.parse(this.cleanResponse(result.response.text()));
  }
  // ... similar for other methods
}

// Use:
const ai = new GeminiService(process.env.GEMINI_API_KEY);
const classification = await ai.classifyEmail(email);
```

## Cost Calculation for FlowVello

| Volume | Emails/mo | AI Calls | Cost (Gemini Flash) |
|--------|-----------|----------|---------------------|
| Solo FlowVello | ~100 | ~300 | ~$0.15 |
| + 3 agency clients | ~500 | ~1500 | ~$0.75 |
| + 10 agency clients | ~2000 | ~6000 | ~$3.00 |

**Gemini is so cheap you don't need to worry about AI costs at your scale.**

## Error Handling

| Failure | Action |
|---------|--------|
| AI returns invalid JSON | Retry with stricter prompt, max 2 attempts |
| AI rate limited | Wait 1 second, retry |
| AI down (500 error) | Fall back to "manual classification" — flag email for human |
| AI returns empty | Mark as "unclassified", notify admin |
