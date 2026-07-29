# Testing Strategy

## Testing Pyramid

```
          ╱─────╲
         │  E2E  │   ← 5% of tests (Playwright / Cypress)
        ╱─────────╲
       │ Integration│ ← 30% of tests (Supertest + test DB)
      ╱──────────────╲
     │   Unit Tests   │ ← 65% of tests (Vitest)
    ╱──────────────────╲
```

## Unit Tests (Vitest)

### What to Test
- Service functions with pure logic
- AI provider abstraction layer (with mocked providers)
- Email parsing/normalization
- Workflow condition evaluation
- Permission checks
- Validation schemas
- Utility functions

### What NOT to Test
- Database queries (use integration tests)
- External API calls (mock them)
- Framework behavior (Express, Next.js internals)

### Example Structure
```typescript
// __tests__/services/email-classifier.test.ts
describe('EmailClassifier', () => {
  it('should classify lead intent correctly');
  it('should prioritize urgent emails');
  it('should handle empty body gracefully');
  it('should detect spam with high confidence');
});
```

## Integration Tests (Vitest + Supertest)

### Setup
```typescript
// tests/setup.ts
import { PrismaClient } from '@prisma/client';
import { createTestDatabase, clearDatabase, seedTestData } from './helpers';

beforeAll(async () => {
  await createTestDatabase(); // Separate test DB
  await seedTestData();
});

afterAll(async () => {
  await clearDatabase();
});
```

### What to Test
- API endpoint responses (status codes, shapes)
- Database CRUD operations
- Authentication middleware
- Authorization (RBAC)
- Rate limiting
- Workflow execution
- Email processing pipeline
- AI draft generation (mock AI responses)
- CRM integration (mock CRM APIs)

### Example
```typescript
describe('POST /api/v1/emails/:id/draft/approve', () => {
  it('should approve pending draft');
  it('should reject already approved draft');
  it('should reject unauthorized user');
  it('should send email via Gmail API on approval');
  it('should create audit log entry');
});
```

## E2E Tests (Playwright)

### What to Test
- Complete login flow
- Gmail OAuth flow (mock redirects)
- Inbox view with real data
- Draft approval workflow (full cycle)
- Knowledge base CRUD
- Workflow builder (drag and drop)
- Notification display

### Approach
- Use test database with seeded data
- Mock external APIs (Gmail, AI, CRM)
- Test critical user journeys only
- Run in CI pipeline

## Testing Gmail API Interactions

```typescript
// Mock Gmail API responses
// Test without real Google credentials
const mockGmailApi = {
  users: {
    messages: {
      list: vi.fn().mockResolvedValue({ data: { messages: [...] } }),
      get: vi.fn().mockResolvedValue({ data: mockEmail }),
      send: vi.fn().mockResolvedValue({ data: { id: 'sent123' } }),
    },
    watch: vi.fn().mockResolvedValue({ data: { historyId: '12345' } }),
  },
};
```

## Testing AI Responses

```typescript
// Fixed test responses for AI calls
// Ensures deterministic test results
const mockAiResponse = {
  intent: 'lead',
  priority: 'high',
  sentiment: 'positive',
  leadScore: 85,
  requiresReply: true,
  requiresApproval: true,
};

// Test with malformed/non-JSON AI responses
// Test with empty responses
// Test with partial responses
```

## Test Data

```typescript
// factories/email.factory.ts
export function createMockEmail(overrides = {}): EmailData {
  return {
    gmailMessageId: faker.string.alphanumeric(16),
    fromAddress: faker.internet.email(),
    fromName: faker.person.fullName(),
    subject: faker.lorem.sentence(),
    bodyText: faker.lorem.paragraph(),
    receivedAt: new Date(),
    isIncoming: true,
    ...overrides,
  };
}
```

## Coverage Targets

| Layer | Target |
|-------|--------|
| Services | 90%+ |
| API Routes | 85%+ |
| AI Pipeline | 90%+ |
| Workflow Engine | 95%+ |
| Frontend Components | 70%+ |
| E2E (critical paths) | 100% coverage |

## Test Commands

```json
{
  "test": "vitest",
  "test:watch": "vitest --watch",
  "test:coverage": "vitest --coverage",
  "test:e2e": "playwright test",
  "test:integration": "vitest --config vitest.integration.config.ts",
  "test:all": "npm run test && npm run test:integration"
}
```
