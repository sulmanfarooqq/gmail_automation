"""
Database — SQLite storage for emails, classifications, leads, follow-ups.
"""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from config import config
from .models import EmailMessage, EmailClassification, DraftReply, FollowUp, Lead


class Database:
    def __init__(self):
        Path(config.DATA_DIR).mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(config.DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def _create_tables(self):
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS emails (
                id TEXT PRIMARY KEY,
                thread_id TEXT,
                from_address TEXT,
                from_name TEXT,
                subject TEXT,
                body_text TEXT,
                body_html TEXT,
                received_at TEXT,
                is_incoming INTEGER,
                labels TEXT,
                is_processed INTEGER DEFAULT 0
            );
            
            CREATE TABLE IF NOT EXISTS classifications (
                email_id TEXT PRIMARY KEY,
                intent TEXT,
                confidence REAL,
                priority TEXT,
                sentiment TEXT,
                is_lead INTEGER,
                lead_score INTEGER,
                requires_reply INTEGER,
                requires_approval INTEGER,
                categories TEXT,
                extracted_name TEXT,
                extracted_phone TEXT,
                extracted_company TEXT,
                extracted_service TEXT,
                summary TEXT,
                ai_model TEXT,
                created_at TEXT
            );
            
            CREATE TABLE IF NOT EXISTS drafts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email_id TEXT,
                subject TEXT,
                body TEXT,
                tone TEXT,
                status TEXT DEFAULT 'pending',
                needs_approval INTEGER DEFAULT 1,
                edited_body TEXT,
                approval_reason TEXT,
                created_at TEXT
            );
            
            CREATE TABLE IF NOT EXISTS followups (
                id TEXT PRIMARY KEY,
                original_email_id TEXT,
                contact_email TEXT,
                contact_name TEXT,
                subject TEXT,
                step INTEGER DEFAULT 0,
                max_steps INTEGER DEFAULT 3,
                last_sent_at TEXT,
                next_scheduled_at TEXT,
                status TEXT DEFAULT 'running'
            );
            
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT,
                name TEXT,
                phone TEXT,
                company TEXT,
                service_interest TEXT,
                score INTEGER DEFAULT 0,
                source_email_id TEXT,
                status TEXT DEFAULT 'new',
                created_at TEXT
            );
            
            CREATE TABLE IF NOT EXISTS analytics (
                date TEXT PRIMARY KEY,
                emails_processed INTEGER DEFAULT 0,
                leads_captured INTEGER DEFAULT 0,
                drafts_generated INTEGER DEFAULT 0,
                drafts_approved INTEGER DEFAULT 0,
                replies_sent INTEGER DEFAULT 0,
                followups_sent INTEGER DEFAULT 0,
                hours_saved REAL DEFAULT 0
            );
        """)
        self.conn.commit()
    
    # ─── Emails ────────────────────────────────────────────────
    
    def save_email(self, email: EmailMessage):
        self.conn.execute("""
            INSERT OR REPLACE INTO emails
            (id, thread_id, from_address, from_name, subject, body_text,
             body_html, received_at, is_incoming, labels, is_processed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        """, (
            email.id, email.thread_id, email.from_address, email.from_name,
            email.subject, email.body_text, email.body_html,
            email.received_at.isoformat(), int(email.is_incoming),
            json.dumps(email.labels)
        ))
        self.conn.commit()
    
    def email_exists(self, email_id: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM emails WHERE id = ?", (email_id,)
        ).fetchone()
        return row is not None
    
    def get_unprocessed_emails(self, limit: int = 10) -> list[dict]:
        rows = self.conn.execute("""
            SELECT * FROM emails
            WHERE is_processed = 0
            ORDER BY received_at DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]
    
    def mark_processed(self, email_id: str):
        self.conn.execute(
            "UPDATE emails SET is_processed = 1 WHERE id = ?",
            (email_id,)
        )
        self.conn.commit()
    
    def get_all_emails(self, limit: int = 50, offset: int = 0) -> list[dict]:
        rows = self.conn.execute("""
            SELECT e.*, c.intent, c.priority, c.is_lead, c.lead_score,
                   c.extracted_name, c.summary,
                   d.status as draft_status
            FROM emails e
            LEFT JOIN classifications c ON e.id = c.email_id
            LEFT JOIN drafts d ON e.id = d.email_id
            WHERE e.is_incoming = 1
            ORDER BY e.received_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset)).fetchall()
        return [dict(r) for r in rows]
    
    def get_email_by_id(self, email_id: str) -> Optional[dict]:
        row = self.conn.execute("""
            SELECT e.*, c.intent, c.priority, c.sentiment, c.is_lead,
                   c.lead_score, c.extracted_name, c.extracted_phone,
                   c.extracted_company, c.extracted_service, c.summary,
                   d.id as draft_id, d.subject as draft_subject,
                   d.body as draft_body, d.status as draft_status,
                   d.needs_approval
            FROM emails e
            LEFT JOIN classifications c ON e.id = c.email_id
            LEFT JOIN drafts d ON e.id = d.email_id
            WHERE e.id = ?
        """, (email_id,)).fetchone()
        return dict(row) if row else None
    
    # ─── Classifications ──────────────────────────────────────
    
    def save_classification(self, c: EmailClassification):
        self.conn.execute("""
            INSERT OR REPLACE INTO classifications
            (email_id, intent, confidence, priority, sentiment, is_lead,
             lead_score, requires_reply, requires_approval, categories,
             extracted_name, extracted_phone, extracted_company,
             extracted_service, summary, ai_model, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            c.email_id, c.intent, c.confidence, c.priority, c.sentiment,
            int(c.is_lead), c.lead_score, int(c.requires_reply),
            int(c.requires_approval), json.dumps(c.categories),
            c.extracted_name, c.extracted_phone, c.extracted_company,
            c.extracted_service, c.summary, c.ai_model,
            datetime.now().isoformat()
        ))
        self.conn.commit()
    
    # ─── Drafts ────────────────────────────────────────────────
    
    def save_draft(self, draft: DraftReply):
        self.conn.execute("""
            INSERT INTO drafts
            (email_id, subject, body, tone, status, needs_approval,
             edited_body, approval_reason, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            draft.email_id, draft.subject, draft.body, draft.tone,
            draft.status, int(draft.needs_approval),
            draft.edited_body, draft.approval_reason,
            datetime.now().isoformat()
        ))
        self.conn.commit()
    
    def update_draft_status(self, draft_id: int, status: str, edited_body: str = ""):
        self.conn.execute("""
            UPDATE drafts SET status = ?, edited_body = ?
            WHERE id = ?
        """, (status, edited_body, draft_id))
        self.conn.commit()
    
    def get_pending_drafts(self) -> list[dict]:
        rows = self.conn.execute("""
            SELECT d.*, e.from_name, e.from_address, e.subject as original_subject
            FROM drafts d
            JOIN emails e ON d.email_id = e.id
            WHERE d.status = 'pending'
            ORDER BY d.created_at DESC
        """).fetchall()
        return [dict(r) for r in rows]
    
    # ─── Follow-ups ────────────────────────────────────────────
    
    def save_followup(self, fu: FollowUp):
        self.conn.execute("""
            INSERT OR REPLACE INTO followups
            (id, original_email_id, contact_email, contact_name,
             subject, step, max_steps, last_sent_at, next_scheduled_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fu.id, fu.original_email_id, fu.contact_email, fu.contact_name,
            fu.subject, fu.step, fu.max_steps,
            fu.last_sent_at.isoformat() if fu.last_sent_at else None,
            fu.next_scheduled_at.isoformat() if fu.next_scheduled_at else None,
            fu.status
        ))
        self.conn.commit()
    
    def get_due_followups(self) -> list[dict]:
        rows = self.conn.execute("""
            SELECT * FROM followups
            WHERE status = 'running'
            AND next_scheduled_at <= datetime('now')
            ORDER BY next_scheduled_at ASC
        """).fetchall()
        return [dict(r) for r in rows]
    
    def get_active_followups(self) -> list[dict]:
        rows = self.conn.execute("""
            SELECT * FROM followups
            WHERE status = 'running'
            ORDER BY next_scheduled_at ASC
        """).fetchall()
        return [dict(r) for r in rows]
    
    def update_followup_step(self, fu_id: str, step: int, next_scheduled: str):
        self.conn.execute("""
            UPDATE followups
            SET step = ?, last_sent_at = datetime('now'),
                next_scheduled_at = ?
            WHERE id = ?
        """, (step, next_scheduled, fu_id))
        self.conn.commit()
    
    def stop_followup(self, fu_id: str):
        self.conn.execute(
            "UPDATE followups SET status = 'stopped' WHERE id = ?",
            (fu_id,)
        )
        self.conn.commit()
    
    # ─── Leads ─────────────────────────────────────────────────
    
    def save_lead(self, lead: Lead):
        existing = self.conn.execute(
            "SELECT id FROM leads WHERE email = ? AND source_email_id != ?",
            (lead.email, lead.source_email_id)
        ).fetchone()
        
        if existing:
            self.conn.execute("""
                UPDATE leads SET score = MAX(score, ?), status = 'new',
                    service_interest = ?, source_email_id = ?
                WHERE id = ?
            """, (lead.score, lead.service_interest, lead.source_email_id, existing["id"]))
        else:
            self.conn.execute("""
                INSERT INTO leads
                (email, name, phone, company, service_interest, score,
                 source_email_id, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'new', ?)
            """, (
                lead.email, lead.name, lead.phone, lead.company,
                lead.service_interest, lead.score, lead.source_email_id,
                lead.created_at.isoformat()
            ))
        self.conn.commit()
    
    def get_all_leads(self) -> list[dict]:
        rows = self.conn.execute("""
            SELECT l.*, e.subject, e.received_at
            FROM leads l
            LEFT JOIN emails e ON l.source_email_id = e.id
            ORDER BY l.score DESC, l.created_at DESC
        """).fetchall()
        return [dict(r) for r in rows]
    
    # ─── Analytics ─────────────────────────────────────────────
    
    def increment_analytics(self, date: str, field: str, amount: int = 1):
        self.conn.execute(f"""
            INSERT INTO analytics (date, {field})
            VALUES (?, ?)
            ON CONFLICT(date) DO UPDATE SET
                {field} = {field} + ?
        """, (date, amount, amount))
        self.conn.commit()
    
    def get_analytics(self, days: int = 30) -> list[dict]:
        rows = self.conn.execute("""
            SELECT * FROM analytics
            WHERE date >= date('now', ?)
            ORDER BY date DESC
        """, (f'-{days} days',)).fetchall()
        return [dict(r) for r in rows]
    
    def get_totals(self) -> dict:
        row = self.conn.execute("""
            SELECT
                COUNT(DISTINCT e.id) as total_emails,
                COUNT(DISTINCT l.id) as total_leads,
                COUNT(DISTINCT d.id) as total_drafts,
                SUM(CASE WHEN d.status = 'sent' THEN 1 ELSE 0 END) as sent_count,
                COUNT(DISTINCT f.id) as active_followups
            FROM emails e
            LEFT JOIN leads l ON l.source_email_id = e.id
            LEFT JOIN drafts d ON d.email_id = e.id
            LEFT JOIN followups f ON f.original_email_id = e.id AND f.status = 'running'
        """).fetchone()
        return dict(row) if row else {}
    
    def close(self):
        self.conn.close()
