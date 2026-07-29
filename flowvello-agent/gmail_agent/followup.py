"""
Follow-up Engine — automatically schedules and sends follow-up emails.
"""
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from .models import FollowUp
from .gmail_service import send_email
from .drafter import DraftGenerator
from .database import Database


class FollowUpEngine:
    def __init__(self, db: Database):
        self.db = db
        self.drafter = DraftGenerator()
    
    def start_sequence(self, email_id: str, contact_email: str, contact_name: str,
                       subject: str, max_steps: int = 3):
        """Start a follow-up sequence for an email that received a reply."""
        fu = FollowUp(
            id=str(uuid4()),
            original_email_id=email_id,
            contact_email=contact_email,
            contact_name=contact_name,
            subject=subject,
            step=0,
            max_steps=max_steps,
            last_sent_at=None,
            next_scheduled_at=datetime.now(timezone.utc) + timedelta(days=3),
            status="running",
        )
        self.db.save_followup(fu)
        print(f"Follow-up sequence started for {contact_email} (3d → 7d → 14d)")
        return fu.id
    
    def process_due(self) -> int:
        """Process all follow-ups that are due. Returns count sent."""
        due = self.db.get_due_followups()
        sent_count = 0
        
        for fu_data in due:
            try:
                self._send_step(fu_data)
                sent_count += 1
            except Exception as e:
                print(f"Follow-up failed for {fu_data['id']}: {e}")
        
        return sent_count
    
    def _send_step(self, fu_data: dict):
        """Send the next follow-up step."""
        from .gmail_service import fetch_recent_emails
        from .database import Database
        db = Database()
        
        email = db.get_email_by_id(fu_data["original_email_id"])
        if not email:
            db.stop_followup(fu_data["id"])
            return
        
        step = fu_data["step"] + 1
        
        # Get the original reply to use as context
        original_reply = email.get("body_text", "")
        
        # Generate follow-up text
        followup_body = self.drafter.generate_followup(
            email=None,  # We'll skip for now
            original_reply=original_reply,
            step=step,
        )
        
        # Use the body directly
        subject = f"Re: {fu_data['subject']}"
        
        # Send the follow-up
        success = send_email(
            to=fu_data["contact_email"],
            subject=subject,
            body=followup_body,
        )
        
        if success:
            # Schedule next step or complete
            if step >= fu_data["max_steps"]:
                db.stop_followup(fu_data["id"])
                print(f"Follow-up completed for {fu_data['contact_email']} ({step}/{fu_data['max_steps']} steps)")
            else:
                delays = {1: 7, 2: 14}  # Step 1→wait 7d, Step 2→wait 14d
                next_delay = delays.get(step, 7)
                next_scheduled = (datetime.now(timezone.utc) + timedelta(days=next_delay)).isoformat()
                db.update_followup_step(fu_data["id"], step, next_scheduled)
                print(f"Follow-up {step}/{fu_data['max_steps']} sent to {fu_data['contact_email']}")
            
            db.increment_analytics(datetime.now().strftime("%Y-%m-%d"), "followups_sent")
