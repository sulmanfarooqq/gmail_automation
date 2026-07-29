"""
FlowVello Gmail Agent - Data Models
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

@dataclass
class EmailMessage:
    id: str                     # Gmail message ID
    thread_id: str
    from_address: str
    from_name: str
    to_addresses: list
    cc_addresses: list
    subject: str
    body_text: str              # Clean plain text body
    body_html: str              # Original HTML body
    received_at: datetime
    is_incoming: bool           # True = received, False = sent
    labels: list = field(default_factory=list)
    attachments: list = field(default_factory=list)

@dataclass
class EmailClassification:
    email_id: str
    intent: str                 # lead, client_support, billing, etc.
    confidence: float
    priority: str               # low, medium, high, urgent
    sentiment: str              # negative, neutral, positive
    is_lead: bool
    lead_score: int             # 0-100
    requires_reply: bool
    requires_approval: bool
    categories: list
    extracted_name: str = ""
    extracted_phone: str = ""
    extracted_company: str = ""
    extracted_service: str = ""
    summary: str = ""
    ai_model: str = "gemini-1.5-flash"

@dataclass
class DraftReply:
    email_id: str
    subject: str
    body: str
    tone: str
    status: str = "pending"     # pending, approved, rejected, sent
    needs_approval: bool = True
    edited_body: str = ""
    approval_reason: str = ""

@dataclass
class FollowUp:
    id: str
    original_email_id: str
    contact_email: str
    contact_name: str
    subject: str
    step: int
    max_steps: int
    last_sent_at: Optional[datetime]
    next_scheduled_at: Optional[datetime]
    status: str = "running"     # running, completed, stopped

@dataclass
class Lead:
    email: str
    name: str
    phone: str
    company: str
    service_interest: str
    score: int
    source_email_id: str
    status: str = "new"         # new, contacted, qualified, converted, lost
    created_at: datetime = field(default_factory=datetime.now)
