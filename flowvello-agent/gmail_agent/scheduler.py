"""
Scheduler — background jobs for periodic email processing.
"""
import time
from datetime import datetime, timezone
from threading import Thread, Event

from config import config
from .database import Database
from .gmail_service import fetch_recent_emails, fetch_unread_emails
from .classifier import EmailClassifier
from .drafter import DraftGenerator
from .followup import FollowUpEngine
from .models import EmailClassification, DraftReply, Lead
from .email_parser import extract_phone_numbers


class EmailScheduler:
    def __init__(self):
        self.db = Database()
        self.classifier = EmailClassifier()
        self.drafter = DraftGenerator()
        self.followup = FollowUpEngine(self.db)
        self._stop_event = Event()
    
    def process_new_emails(self):
        """Scan for new/unread emails and process them."""
        emails = fetch_unread_emails(max_results=config.MAX_EMAILS_PER_SCAN)
        
        if not emails:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] No new emails")
            return 0
        
        processed = 0
        for email in emails:
            if self.db.email_exists(email.id):
                continue
            
            # Skip if thread is under human control
            if self.db.is_thread_human_handled(email.thread_id):
                print(f"   ⏭️ Skipped (human handling thread): {email.subject[:60]}")
                self.db.save_email(email)
                self.db.mark_processed(email.id)
                continue
            
            print(f"\n📬 Processing: {email.subject[:60]}...")
            
            # 1. Store raw email
            self.db.save_email(email)
            
            # 2. AI Classify
            classification = self.classifier.classify(email)
            self.db.save_classification(classification)
            print(f"   └─ Intent: {classification.intent} | Priority: {classification.priority} | Lead: {classification.is_lead}")
            
            # 3. Generate draft if reply needed
            if classification.requires_reply:
                draft = self.drafter.generate(email, classification)
                self.db.save_draft(draft)
                print(f"   └─ Draft: {'✅ Auto' if not draft.needs_approval else '⏳ Needs approval'}")
            
            # 4. Save lead if detected
            if classification.is_lead:
                phone = classification.extracted_phone or (extract_phone_numbers(email.body_text)[:1] or [""])[0]
                lead = Lead(
                    email=email.from_address,
                    name=classification.extracted_name or email.from_name,
                    phone=phone,
                    company=classification.extracted_company or "",
                    service_interest=classification.extracted_service or classification.intent,
                    score=classification.lead_score,
                    source_email_id=email.id,
                )
                self.db.save_lead(lead)
                print(f"   └─ 🔔 LEAD: {lead.name} | Score: {lead.score} | Service: {lead.service_interest}")
                
                if config.NOTIFY_ON_LEAD:
                    self._send_notification(f"🔔 New lead: {lead.name} ({lead.service_interest})")
            
            # 5. Start follow-up if it's a lead or needs reply
            if classification.is_lead or classification.intent in ("meeting_request", "sales_inquiry"):
                self.followup.start_sequence(
                    email_id=email.id,
                    contact_email=email.from_address,
                    contact_name=email.from_name or email.from_address,
                    subject=email.subject,
                    max_steps=3,
                )
            
            # 6. Mark as processed
            self.db.mark_processed(email.id)
            self.db.increment_analytics(
                datetime.now().strftime("%Y-%m-%d"), "emails_processed"
            )
            if classification.is_lead:
                self.db.increment_analytics(
                    datetime.now().strftime("%Y-%m-%d"), "leads_captured"
                )
            processed += 1
        
        print(f"\n✅ Processed {processed} new emails")
        return processed
    
    def process_followups(self):
        """Process due follow-ups."""
        sent = self.followup.process_due()
        if sent:
            print(f"📤 Sent {sent} follow-up(s)")
    
    def generate_daily_summary(self):
        """Generate and send daily email summary."""
        today = datetime.now().strftime("%Y-%m-%d")
        totals = self.db.get_totals()
        
        # Get today's unclassified/unanswered
        emails = self.db.get_all_emails(limit=5)
        pending = self.db.get_pending_drafts()
        leads = self.db.get_all_leads()
        new_leads = [l for l in leads if l.get("status") == "new"]
        
        summary = f"""FlowVello Daily Summary — {today}

📊 Today's Snapshot:
├── Emails processed: {totals.get('total_emails', 0)}
├── New leads: {len(new_leads)}
├── Pending drafts: {totals.get('total_drafts', 0)}
├── Active follow-ups: {totals.get('active_followups', 0)}
└── Replies sent: {totals.get('sent_count', 0)}

📋 Recent Emails:
"""
        for e in emails[:5]:
            summary += f"  [{e.get('intent', '?')}] {e.get('from_name', '?')}: {e.get('subject', '')[:60]}\n"
        
        if pending:
            summary += f"\n✏️ Pending Drafts ({len(pending)}):\n"
            for d in pending[:5]:
                summary += f"  → {d.get('from_name', '?')}: {d.get('subject', '')[:60]}\n"
        
        if new_leads:
            summary += f"\n🔥 New Leads:\n"
            for l in new_leads[:5]:
                summary += f"  → {l.get('name', '?')} ({l.get('service_interest', '?')}) - Score: {l.get('score', 0)}\n"
        
        print(f"\n📋 Daily Summary:\n{summary}")
        return summary
    
    def run_continuous(self, interval_minutes: int = None):
        """Run continuous email monitoring loop."""
        interval = interval_minutes or config.SCAN_INTERVAL_MINUTES
        print(f"🚀 FlowVello Gmail Agent started")
        print(f"   Scanning every {interval} minutes")
        print(f"   Press Ctrl+C to stop\n")
        
        # Run initial scan immediately
        self.process_new_emails()
        self.process_followups()
        
        # Run daily summary check (every hour, only send at 8 AM-ish)
        last_summary_date = ""
        
        while not self._stop_event.is_set():
            try:
                time.sleep(interval * 60)
                
                self.process_new_emails()
                self.process_followups()
                
                # Daily summary at first run after 7 AM
                now = datetime.now()
                if now.hour >= 7 and now.strftime("%Y-%m-%d") != last_summary_date:
                    self.generate_daily_summary()
                    last_summary_date = now.strftime("%Y-%m-%d")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error in scheduler loop: {e}")
                time.sleep(60)
    
    def stop(self):
        self._stop_event.set()
    
    def _send_notification(self, message: str):
        """Placeholder for notification. In full version, could email/SMS/WhatsApp."""
        print(f"   🔔 NOTIFICATION: {message}")
