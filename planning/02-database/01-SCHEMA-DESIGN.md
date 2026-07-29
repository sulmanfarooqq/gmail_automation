# Database Schema Design (PostgreSQL + Prisma)

## Schema Overview

```prisma
// ============================================================
// MULTI-TENANCY CORE
// ============================================================

model Organization {
  id          String   @id @default(cuid())
  name        String
  slug        String   @unique
  logo        String?
  brandColor  String?
  customDomain String?
  plan        PlanType @default(free)
  isActive    Boolean  @default(true)
  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt

  users       User[]
  gmailAccounts GmailAccount[]
  knowledgeBase KnowledgeBase[]
  workflows   Workflow[]
  crmConfig   CrmConfig?
  calendarConfig CalendarConfig?
  billing     BillingInfo?
  aiConfig    AiConfig?
  auditLogs   AuditLog[]
}

enum PlanType {
  free
  starter
  professional
  enterprise
}

// ============================================================
// AUTH & USERS
// ============================================================

model User {
  id             String   @id @default(cuid())
  organizationId String
  email          String   @unique
  passwordHash   String?
  name           String
  role           UserRole @default(agent)
  isActive       Boolean  @default(true)
  avatarUrl      String?
  lastLoginAt    DateTime?
  createdAt      DateTime @default(now())
  updatedAt      DateTime @updatedAt

  organization   Organization @relation(fields: [organizationId], references: [id])
  sessions       Session[]
  approvalActions ApprovalAction[]
  tasks          Task[]
}

enum UserRole {
  admin
  agent
  viewer
}

model Session {
  id        String   @id @default(cuid())
  userId    String
  token     String   @unique
  expiresAt DateTime
  createdAt DateTime @default(now())
  user      User     @relation(fields: [userId], references: [id])
}

// ============================================================
// GMAIL INTEGRATION
// ============================================================

model GmailAccount {
  id              String   @id @default(cuid())
  organizationId  String
  email           String
  isPrimary       Boolean  @default(false)
  accessToken     String   // encrypted
  refreshToken    String   // encrypted
  tokenExpiresAt  DateTime
  historyId       BigInt?  // for incremental sync
  watchExpiration DateTime?
  isActive        Boolean  @default(true)
  lastSyncedAt    DateTime?
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt

  organization    Organization @relation(fields: [organizationId], references: [id])
  emails          Email[]
  emailThreads    EmailThread[]
}

// ============================================================
// EMAIL STORAGE
// ============================================================

model EmailThread {
  id              String   @id @default(cuid())
  gmailThreadId   String
  gmailAccountId  String
  organizationId  String
  subject         String?
  lastMessageAt   DateTime?
  messageCount    Int      @default(0)
  isArchived      Boolean  @default(false)
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt

  gmailAccount    GmailAccount @relation(fields: [gmailAccountId], references: [id])
  emails          Email[]
  classification  EmailClassification?
  conversationContext AiConversationContext?
}

model Email {
  id              String   @id @default(cuid())
  gmailMessageId  String   @unique
  threadId        String
  gmailAccountId  String
  organizationId  String
  fromAddress     String
  fromName        String?
  toAddresses     String[]
  ccAddresses     String[]
  bccAddresses    String[]
  subject         String?
  bodyText        String?   // plain text extracted body
  bodyHtml        String?   // HTML body (stripped of scripts)
  strippedBody    String?   // body without signatures/replies
  rawBody         String?   // full raw for reprocessing
  receivedAt      DateTime
  isIncoming      Boolean   // true = received, false = sent
  isRead          Boolean   @default(false)
  labels          String[]  // Gmail labels
  createdAt       DateTime  @default(now())

  thread          EmailThread @relation(fields: [threadId], references: [id])
  gmailAccount    GmailAccount @relation(fields: [gmailAccountId], references: [id])
  attachments     Attachment[]
  classification  EmailClassification?
  aiReply         AiReply?
  approvalAction  ApprovalAction?
  crmActivity     CrmActivity[]
  task            Task?
}

// ============================================================
// AI PIPELINE
// ============================================================

model EmailClassification {
  id              String   @id @default(cuid())
  emailId         String   @unique
  threadId        String   @unique
  organizationId  String
  intent          IntentType
  confidence      Float
  priority        PriorityType
  sentiment       SentimentType
  leadScore       Int?
  isLead          Boolean  @default(false)
  requiresReply   Boolean  @default(true)
  requiresApproval Boolean @default(true)
  categories      String[]
  extractedData   Json?    // flexible: name, company, phone, service, etc.
  aiModelUsed     String
  processingTime  Int      // ms
  createdAt       DateTime @default(now())

  email           Email    @relation(fields: [emailId], references: [id])
  thread          EmailThread @relation(fields: [threadId], references: [id])
}

enum IntentType {
  lead
  customer_support
  sales_inquiry
  billing
  complaint
  partnership
  newsletter
  spam
  internal
  meeting_request
  other
}

enum PriorityType {
  low
  medium
  high
  urgent
}

enum SentimentType {
  very_negative
  negative
  neutral
  positive
  very_positive
}

model AiReply {
  id              String   @id @default(cuid())
  emailId         String   @unique
  organizationId  String
  draftBody       String
  tone            String?
  status          DraftStatus @default(pending)
  editedBody      String?  // human edited version
  approvedById    String?
  approvedAt      DateTime?
  rejectedReason  String?
  aiModelUsed     String
  tokenCount      Int?
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt

  email           Email    @relation(fields: [emailId], references: [id])
}

enum DraftStatus {
  pending
  approved
  rejected
  sent
  failed
}

model AiConversationContext {
  id              String   @id @default(cuid())
  threadId        String   @unique
  organizationId  String
  summary         String?  // AI-generated thread summary
  keyPoints       String[] // key points extracted
  actionItems     String[] // action items detected
  unresolvedQuestions String[]
  lastAnalyzedAt  DateTime  @default(now())

  thread          EmailThread @relation(fields: [threadId], references: [id])
}

// ============================================================
// KNOWLEDGE BASE
// ============================================================

model KnowledgeBase {
  id              String   @id @default(cuid())
  organizationId  String   @unique
  companyName     String
  companyDescription String?
  services        String[] // list of services offered
  pricingSummary  String?
  toneOfVoice     String?
  defaultCta      String?
  businessHours   String?
  refundPolicy    String?
  rules           String[] // "Never promise guarantees" etc.
  customInstructions String?
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt

  organization    Organization @relation(fields: [organizationId], references: [id])
  faqs            Faq[]
  caseStudies     CaseStudy[]
  teamMembers     TeamMember[]
}

model Faq {
  id              String   @id @default(cuid())
  knowledgeBaseId String
  question        String
  answer          String
  category        String?
  order           Int      @default(0)
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt

  knowledgeBase   KnowledgeBase @relation(fields: [knowledgeBaseId], references: [id])
}

model CaseStudy {
  id              String   @id @default(cuid())
  knowledgeBaseId String
  title           String
  industry        String?
  result          String?
  pdfUrl          String?
  createdAt       DateTime @default(now())

  knowledgeBase   KnowledgeBase @relation(fields: [knowledgeBaseId], references: [id])
}

model TeamMember {
  id              String   @id @default(cuid())
  knowledgeBaseId String
  name            String
  role            String?
  email           String?
  bio             String?
  photoUrl        String?
  createdAt       DateTime @default(now())

  knowledgeBase   KnowledgeBase @relation(fields: [knowledgeBaseId], references: [id])
}

// ============================================================
// WORKFLOW ENGINE
// ============================================================

model Workflow {
  id              String       @id @default(cuid())
  organizationId  String
  name            String
  description     String?
  isActive        Boolean      @default(true)
  trigger         WorkflowTrigger
  conditions      Json         // flexible condition tree
  actions         Json         // ordered action list
  runCount        Int          @default(0)
  successCount    Int          @default(0)
  lastRunAt       DateTime?
  createdById     String?
  createdAt       DateTime     @default(now())
  updatedAt       DateTime     @updatedAt

  organization    Organization @relation(fields: [organizationId], references: [id])
  executions      WorkflowExecution[]
}

enum WorkflowTrigger {
  email_received
  email_sent
  ai_classified
  lead_detected
  no_reply_timeout
  scheduled
}

model WorkflowExecution {
  id              String       @id @default(cuid())
  workflowId      String
  organizationId  String
  emailId         String?
  status          ExecutionStatus
  result          Json?
  errorMessage    String?
  startedAt       DateTime     @default(now())
  completedAt     DateTime?

  workflow        Workflow @relation(fields: [workflowId], references: [id])
}

enum ExecutionStatus {
  running
  completed
  failed
  skipped
}

// ============================================================
// CRM INTEGRATION
// ============================================================

model CrmConfig {
  id              String   @id @default(cuid())
  organizationId  String   @unique
  provider        CrmProvider
  apiKey          String?  // encrypted
  apiUrl          String?
  webhookUrl      String?
  defaultAssignee String?
  isConnected     Boolean  @default(false)
  lastSyncAt      DateTime?
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt

  organization    Organization @relation(fields: [organizationId], references: [id])
  contacts        CrmContact[]
  activities      CrmActivity[]
}

enum CrmProvider {
  hubspot
  salesforce
  pipedrive
  gohighlevel
}

model CrmContact {
  id              String   @id @default(cuid())
  crmConfigId     String
  organizationId  String
  externalId      String?  // CRM's own ID
  email           String
  name            String?
  company         String?
  phone           String?
  leadScore       Int?
  status          String?  // lead, qualified, customer, lost
  assignedTo      String?
  source          String?  // email, website, referral
  metadata        Json?
  lastContactedAt DateTime?
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt

  crmConfig   CrmConfig @relation(fields: [crmConfigId], references: [id])
  activities  CrmActivity[]
}

model CrmActivity {
  id              String   @id @default(cuid())
  crmConfigId     String
  organizationId  String
  contactId       String?
  emailId         String?
  activityType    String   // note, email, call, meeting
  description     String?
  performedAt     DateTime @default(now())
  createdAt       DateTime @default(now())

  crmConfig CrmConfig @relation(fields: [crmConfigId], references: [id])
  contact   CrmContact? @relation(fields: [contactId], references: [id])
}

// ============================================================
// CALENDAR
// ============================================================

model CalendarConfig {
  id              String   @id @default(cuid())
  organizationId  String   @unique
  accessToken     String?  // encrypted
  refreshToken    String?  // encrypted
  tokenExpiresAt  DateTime?
  calendarId      String?  // primary calendar ID
  isConnected     Boolean  @default(false)
  defaultDuration Int      @default(30) // minutes
  availableHours  Json?    // {"monday": ["09:00-17:00"], ...}
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt

  organization    Organization @relation(fields: [organizationId], references: [id])
}

// ============================================================
// FOLLOW-UP SEQUENCES
// ============================================================

model FollowUpSequence {
  id              String   @id @default(cuid())
  organizationId  String
  name            String
  triggerEmailId  String?
  steps           Json     // [{delay: "2d", template: "..."}, ...]
  maxSteps        Int      @default(3)
  stopOnReply     Boolean  @default(true)
  status          SequenceStatus @default(active)
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt

  executions      FollowUpExecution[]
}

enum SequenceStatus {
  active
  paused
  completed
}

model FollowUpExecution {
  id              String   @id @default(cuid())
  sequenceId      String
  organizationId  String
  contactEmail    String
  currentStep     Int      @default(0)
  lastSentAt      DateTime?
  nextScheduledAt DateTime?
  status          FollowUpStatus
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt

  sequence        FollowUpSequence @relation(fields: [sequenceId], references: [id])
}

enum FollowUpStatus {
  running
  completed
  stopped
  failed
}

// ============================================================
// TASKS
// ============================================================

model Task {
  id              String   @id @default(cuid())
  organizationId  String
  emailId         String?
  assignedToId    String?
  title           String
  description     String?
  dueDate         DateTime?
  status          TaskStatus @default(pending)
  priority        PriorityType @default(medium)
  source          String?  // ai_detected, manual, workflow
  completedAt     DateTime?
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt

  email           Email?   @relation(fields: [emailId], references: [id])
  assignedTo      User?    @relation(fields: [assignedToId], references: [id])
}

enum TaskStatus {
  pending
  in_progress
  completed
  cancelled
}

// ============================================================
// NOTIFICATIONS
// ============================================================

model Notification {
  id              String   @id @default(cuid())
  organizationId  String
  userId          String?
  title           String
  body            String?
  type            NotificationType
  channel         NotificationChannel
  referenceId     String?  // email ID, task ID, etc.
  isRead          Boolean  @default(false)
  sentAt          DateTime @default(now())
  readAt          DateTime?
  createdAt       DateTime @default(now())
}

enum NotificationType {
  new_lead
  urgent_email
  draft_ready
  approval_required
  follow_up_due
  task_assigned
  system_alert
}

enum NotificationChannel {
  in_app
  email
  slack
}

// ============================================================
// AUDIT & MONITORING
// ============================================================

model AuditLog {
  id              String   @id @default(cuid())
  organizationId  String
  userId          String?
  action          String   // "email.approved", "workflow.created", etc.
  entityType      String
  entityId        String?
  oldValue        Json?
  newValue        Json?
  ipAddress       String?
  userAgent       String?
  createdAt       DateTime @default(now())

  organization    Organization @relation(fields: [organizationId], references: [id])
}

model AiLog {
  id              String   @id @default(cuid())
  organizationId  String
  emailId         String?
  modelUsed       String
  promptTokens    Int
  completionTokens Int
  totalCost       Float?
  processingTime  Int      // ms
  success         Boolean
  errorMessage    String?
  createdAt       DateTime @default(now())
}

// ============================================================
// BILLING
// ============================================================

model BillingInfo {
  id              String       @id @default(cuid())
  organizationId  String       @unique
  stripeCustomerId String?     @unique
  stripeSubscriptionId String?
  plan            PlanType     @default(free)
  emailQuota      Int          @default(1000) // per month
  emailsUsed      Int          @default(0)
  billingEmail    String?
  billingCycle    BillingCycle @default(monthly)
  nextBillingDate DateTime?
  isActive        Boolean      @default(true)
  createdAt       DateTime     @default(now())
  updatedAt       DateTime     @updatedAt

  organization    Organization @relation(fields: [organizationId], references: [id])
}

enum BillingCycle {
  monthly
  yearly
}

model AiConfig {
  id              String   @id @default(cuid())
  organizationId  String   @unique
  preferredProvider AiProvider @default(gemini)
  geminiApiKey    String?  // encrypted
  openaiApiKey    String?  // encrypted
  anthropicApiKey String?  // encrypted
  fallbackProvider AiProvider?
  temperature     Float    @default(0.3)
  maxTokens       Int      @default(2048)
  customInstructions String?
  createdAt       DateTime @default(now())
  updatedAt       DateTime @updatedAt

  organization    Organization @relation(fields: [organizationId], references: [id])
}

enum AiProvider {
  gemini
  openai
  anthropic
}

// ============================================================
// ATTACHMENTS
// ============================================================

model Attachment {
  id              String   @id @default(cuid())
  emailId         String
  organizationId  String
  filename        String
  mimeType        String
  sizeBytes       Int
  storageUrl      String
  documentType    String?  // invoice, contract, proposal
  extractedData   Json?    // AI-extracted data from document
  createdAt       DateTime @default(now())

  email           Email @relation(fields: [emailId], references: [id])
}
```

## Indexes

```sql
-- Critical indexes for performance
CREATE INDEX idx_email_org_received ON email(organization_id, received_at DESC);
CREATE INDEX idx_email_org_thread ON email(organization_id, thread_id);
CREATE INDEX idx_email_gmail_id ON email(gmail_message_id);
CREATE INDEX idx_classification_org_intent ON email_classification(organization_id, intent);
CREATE INDEX idx_thread_org ON email_thread(organization_id, gmail_thread_id);
CREATE INDEX idx_workflow_org ON workflow(organization_id, is_active);
CREATE INDEX idx_audit_org_created ON audit_log(organization_id, created_at DESC);
CREATE INDEX idx_notification_user_read ON notification(user_id, is_read, created_at DESC);
CREATE INDEX idx_email_search ON email USING gin(to_tsvector('english', body_text));
CREATE INDEX idx_crm_contact_email ON crm_contact(email);
CREATE INDEX idx_followup_next_scheduled ON follow_up_execution(next_scheduled_at) WHERE status = 'running';
```

## Data Encryption

- OAuth tokens: AES-256-GCM encryption at rest
- API keys: AES-256-GCM encryption at rest
- All sensitive fields: encrypted before DB insert, decrypted in service layer
- Encryption keys stored in environment variables / secrets manager (never in DB)
