# Phase 4: AI Layer Specification (Gemini)

## Objective
Build AI capabilities: email classification, summarization, reply drafting, knowledge base (RAG), entity extraction, and intent detection.

## Tech Stack
- Python 3.11+ (FastAPI)
- Google Gemini API (gemini-1.5-pro, gemini-1.5-flash, text-embedding-004)
- Pydantic for validation
- pgvector (PostgreSQL) for embeddings
- Redis for caching + rate limiting
- Celery for async task processing

## Service Architecture

ai-engine/
|-- services/
|   |-- classifier/
|   |   |-- prompts.py
|   |   |-- schema.py
|   |   |-- service.py
|   |-- summarizer/
|   |   |-- prompts.py
|   |   |-- service.py
|   |-- drafter/
|   |   |-- prompts.py
|   |   |-- context.py
|   |   |-- service.py
|   |-- extractor/
|   |   |-- schema.py
|   |   |-- service.py
|   |-- knowledge/
|   |   |-- embeddings.py
|   |   |-- vector_store.py
|   |   |-- ingestion.py
|   |   |-- retrieval.py
|   |-- workflow/
|   |   |-- engine.py
|   |   |-- triggers/
|   |   |-- conditions/
|   |   |-- actions/
|-- shared/
|   |-- gemini_client.py
|   |-- config.py
|   |-- logging.py
|   |-- metrics.py
|-- tests/
|-- pyproject.toml
|-- Dockerfile

## Core Features

### 1. Email Classification
Categories: lead, support, existing_customer, complaint, invoice, payment, quote_request, meeting_request, job_application, spam, newsletter, internal, other

```python
class ClassificationResult(BaseModel):
    category: Literal['lead', 'support', 'existing_customer', 'complaint', 
                      'invoice', 'payment', 'quote_request', 'meeting_request',
                      'job_application', 'spam', 'newsletter', 'internal', 'other']
    confidence: float = Field(ge=0, le=1)
    sub_category: Optional[str] = None
    reasoning: str
    suggested_actions: List[SuggestedAction]

class SuggestedAction(BaseModel):
    action: str
    params: Dict[str, Any]
    priority: int
    requires_approval: bool
```

Few-shot prompt with 20+ examples per category, stored in DB per tenant for customization.

### 2. Summarization
- Thread summary (3-5 bullet points)
- Single email summary (1-2 sentences)
- Key decisions/action items extraction
- Language detection + response in same language

### 3. Reply Drafting
- Context: email thread + knowledge base + tenant settings
- Tone: professional, friendly, formal, casual
- Length: short, medium, long
- Placeholders for missing info
- Approval levels: suggest only / auto-send safe / autonomous

### 4. Knowledge Base (RAG)
- Document ingestion: PDF, text, URLs, API sync
- Chunking: semantic + fixed-size overlap
- Embeddings: Gemini text-embedding-004 (768 dims)
- Storage: pgvector in PostgreSQL (tenant-isolated)
- Retrieval: hybrid (BM25 + vector) with reranking
- Citations in responses

### 5. Entity Extraction
Structured schemas for:
- Lead: name, company, email, phone, budget, timeline, requirements
- Invoice: vendor, amount, date, invoice_number, line_items
- Appointment: date, time, duration, attendees, location, type
- Quote: items, quantities, prices, terms, validity
- Complaint: issue, severity, order_id, desired_resolution

### 6. Intent Detection
- Primary intent + confidence
- Secondary intents
- Urgency: low, medium, high, critical
- Sentiment: positive, neutral, negative
- Requires human: boolean

## API Endpoints (FastAPI)

POST /classify -> ClassificationResult
POST /summarize -> SummaryResponse
POST /draft-reply -> DraftResponse
POST /extract -> ExtractResponse
POST /knowledge/ingest -> IngestResponse
POST /knowledge/search -> SearchResponse
POST /intent -> IntentResponse

## Integration with Webmail
1. Email received -> Redis stream 'email:received:{tenant_id}'
2. AI Engine consumer picks up
3. Runs classification + extraction + intent
4. Stores results in PostgreSQL
5. Checks workflows for matching triggers
6. Enqueues actions
7. Webmail polls or receives SSE for AI results

## Prompt Management
- Prompts stored in DB per tenant (JSON)
- Version control for prompts
- A/B testing framework
- Fallback to global defaults

## Rate Limiting & Cost Control
- Per-tenant daily limits (configurable per plan)
- Per-minute burst limits
- Token counting for cost estimation
- Cache repeated requests
- Use flash model for classification, pro for drafting

## Success Criteria

| Metric | Target |
|--------|--------|
| Classification accuracy | > 90% (weighted F1) |
| Summarization quality | > 4/5 human eval |
| Draft acceptance rate | > 60% |
| RAG recall@5 | > 85% |
| P99 latency | < 3s |
| Cost per email | < $0.02 |

## Timeline: 3-4 Weeks

| Week | Focus |
|------|-------|
| 1 | Gemini client, classifier, basic prompts |
| 2 | Summarizer, drafter, knowledge base ingestion |
| 3 | Extractor, intent detection, RAG retrieval |
| 4 | Integration, evaluation, cost optimization, testing |
