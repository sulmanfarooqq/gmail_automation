# Phase 2: Custom Webmail Specification

## Objective
Build a Gmail-like webmail interface with inbox, compose, threading, search, contacts, and settings.

## Tech Stack
- Next.js 14+ (App Router)
- TypeScript (strict mode)
- tRPC for type-safe API
- Tailwind CSS + shadcn/ui
- TanStack Query (React Query) for server state
- Zod for validation
- IMAP/SMTP via shared library

## Application Structure

apps/webmail/
|-- app/
|   |-- (auth)/
|   |   |-- login/page.tsx
|   |   |-- mfa/page.tsx
|   |   |-- forgot-password/page.tsx
|   |   |-- layout.tsx
|   |-- (mail)/
|   |   |-- layout.tsx          # Sidebar + header shell
|   |   |-- inbox/page.tsx      # Email list + thread view
|   |   |-- sent/page.tsx
|   |   |-- drafts/page.tsx
|   |   |-- spam/page.tsx
|   |   |-- trash/page.tsx
|   |   |-- archive/page.tsx
|   |   |-- label/[id]/page.tsx
|   |   |-- search/page.tsx
|   |   |-- compose/page.tsx    # New email / reply / forward
|   |   |-- thread/[id]/page.tsx
|   |   |-- components/
|   |   |   |-- EmailList.tsx
|   |   |   |-- EmailRow.tsx
|   |   |   |-- ThreadView.tsx
|   |   |   |-- ComposeForm.tsx
|   |   |   |-- AttachmentUpload.tsx
|   |   |   |-- RichTextEditor.tsx
|   |   |   |-- Sidebar.tsx
|   |   |   |-- SearchBar.tsx
|   |   |   |-- FolderTree.tsx
|   |-- (contacts)/
|   |   |-- page.tsx
|   |   |-- new/page.tsx
|   |   |-- [id]/page.tsx
|   |   |-- components/
|   |-- (settings)/
|   |   |-- page.tsx
|   |   |-- signature/page.tsx
|   |   |-- auto-reply/page.tsx
|   |   |-- forwarding/page.tsx
|   |   |-- security/page.tsx
|   |   |-- notifications/page.tsx
|   |   |-- components/
|   |-- layout.tsx
|-- components/
|   |-- ui/                     # shadcn/ui components
|   |-- providers/              # QueryProvider, AuthProvider
|   |-- hooks/
|-- lib/
|   |-- trpc.ts                 # tRPC client
|   |-- imap.ts                 # IMAP connection pool
|   |-- smtp.ts                 # SMTP sender
|   |-- auth.ts                 # JWT handling
|   |-- utils.ts
|-- trpc/
|   |-- routers/
|   |   |-- mail.ts
|   |   |-- folders.ts
|   |   |-- compose.ts
|   |   |-- contacts.ts
|   |   |-- settings.ts
|   |-- middleware/
|   |   |-- auth.ts
|   |   |-- tenant.ts
|-- package.json

## Core Features

### 1. Inbox & Threading
- Virtualized email list (react-window) for 10k+ emails
- Conversation threading (References/In-Reply-To headers)
- Expand/collapse threads
- Keyboard shortcuts (j/k, enter, c, /, e, #, etc.)
- Infinite scroll pagination
- Real-time updates via WebSocket/SSE

### 2. Compose
- Rich text editor (TipTap or Plate)
- Attachments drag-drop + progress
- To/CC/BCC with contact autocomplete
- Signature insertion
- Save draft (auto-save every 30s)
- Send later scheduling
- Template/snippet support

### 3. Search
- Full-text search via PostgreSQL tsvector
- Search operators: from:, to:, subject:, has:attachment, label:, before:, after:
- Search suggestions/history
- Highlight matches

### 4. Contacts
- CRUD for contacts
- Import/export (CSV, vCard)
- Contact suggestions in compose
- Merge duplicates
- Contact groups/labels

### 5. Settings
- Signature (per identity)
- Auto-reply (vacation responder)
- Forwarding rules
- Password change + MFA (TOTP)
- Notification preferences
- Theme (light/dark/system)
- Language

## IMAP/SMTP Integration

### IMAP Connection Pool
```typescript
// lib/imap.ts
import { ImapFlow } from 'imapflow';
import { Pool } from 'generic-pool';

interface ImapConfig {
  host: string;
  port: number;
  secure: boolean;
  auth: { user: string; pass: string };
}

const createPool = (config: ImapConfig) => new Pool({
  create: async () => {
    const client = new ImapFlow(config);
    await client.connect();
    return client;
  },
  destroy: async (client) => client.close(),
  validate: async (client) => client.isConnected(),
  max: 10,
  min: 2,
});

// Usage
const mailbox = await pool.acquire();
try {
  await mailbox.mailboxOpen('INBOX');
  const messages = await mailbox.fetch('1:*', { envelope: true, flags: true });
  // ...
} finally {
  pool.release(mailbox);
}
```

### SMTP Sender
```typescript
// lib/smtp.ts
import { createTransport } from 'nodemailer';

const transporter = createTransport({
  host: process.env.SMTP_HOST,
  port: 587,
  secure: false,
  auth: { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS },
  tls: { minVersion: 'TLSv1.2' },
  pool: true,
  maxConnections: 10,
  rateLimit: 10, // messages per second
});

export async function sendMail(params: {
  from: string;
  to: string[];
  cc?: string[];
  bcc?: string[];
  subject: string;
  text?: string;
  html?: string;
  attachments?: Attachment[];
  inReplyTo?: string;
  references?: string;
}) {
  return transporter.sendMail({
    ...params,
    headers: {
      'X-Mailer': 'AI Business Mailbox',
      'Auto-Submitted': 'auto-generated',
      ...(params.inReplyTo ? { 'In-Reply-To': params.inReplyTo } : {}),
      ...(params.references ? { References: params.references } : {}),
    },
  });
}
```

## tRPC Routers

### mail.router.ts
```typescript
export const mailRouter = router({
  list: protectedProcedure
    .input(z.object({
      folder: z.enum(['inbox', 'sent', 'drafts', 'spam', 'trash', 'archive']).default('inbox'),
      labelId: z.string().uuid().optional(),
      page: z.number().min(1).default(1),
      limit: z.number().min(1).max(100).default(50),
      query: z.string().optional(),
      sort: z.enum(['date', 'from', 'subject', 'size']).default('date'),
      order: z.enum(['asc', 'desc']).default('desc'),
    }))
    .query(async ({ ctx, input }) => {
      // Query PostgreSQL with RLS (tenant_id auto-filtered)
      return ctx.db.query.emails.findMany({ ... });
    }),

  getThread: protectedProcedure
    .input(z.object({ threadId: z.string().uuid() }))
    .query(async ({ ctx, input }) => {
      // Fetch all emails in thread, ordered chronologically
    }),

  getMessage: protectedProcedure
    .input(z.object({ id: z.string().uuid() }))
    .query(async ({ ctx, input }) => {
      // Fetch full message with body + attachments
    }),

  move: protectedProcedure
    .input(z.object({
      ids: z.array(z.string().uuid()).min(1),
      folder: z.enum(['inbox', 'sent', 'drafts', 'spam', 'trash', 'archive']),
    }))
    .mutation(async ({ ctx, input }) => {
      // IMAP MOVE + update DB
    }),

  flag: protectedProcedure
    .input(z.object({
      ids: z.array(z.string().uuid()).min(1),
      flag: z.enum(['seen', 'flagged', 'answered', 'forwarded']),
      value: z.boolean(),
    }))
    .mutation(async ({ ctx, input }) => {
      // IMAP STORE +FLAGS/-FLAGS
    }),

  delete: protectedProcedure
    .input(z.object({ ids: z.array(z.string().uuid()).min(1) }))
    .mutation(async ({ ctx, input }) => {
      // Move to trash, schedule permanent delete after 30 days
    }),

  search: protectedProcedure
    .input(z.object({
      q: z.string().min(1),
      folder: z.string().optional(),
      page: z.number().min(1).default(1),
    }))
    .query(async ({ ctx, input }) => {
      // PostgreSQL full-text search
    }),
});
```

### compose.router.ts
```typescript
export const composeRouter = router({
  send: protectedProcedure
    .input(z.object({
      to: z.array(z.string().email()).min(1),
      cc: z.array(z.string().email()).optional(),
      bcc: z.array(z.string().email()).optional(),
      subject: z.string().min(1).max(500),
      text: z.string().optional(),
      html: z.string().optional(),
      attachments: z.array(z.object({
        filename: z.string(),
        contentType: z.string(),
        size: z.number(),
        minioKey: z.string(),
      })).optional(),
      inReplyTo: z.string().optional(),
      references: z.string().optional(),
      sendAt: z.date().optional(), // Schedule send
    }))
    .mutation(async ({ ctx, input }) => {
      if (input.sendAt && input.sendAt > new Date()) {
        // Schedule via automation engine
        return scheduleSend(ctx.tenantId, input);
      }
      // Send immediately via SMTP
      const result = await sendMail({ ...input, from: ctx.user.email });
      // Save to Sent folder via IMAP
