"""
AI Reply Drafter — generates context-aware email replies using Gemini.
"""
import json
import re
import google.generativeai as genai
from config import config
from .models import EmailMessage, EmailClassification, DraftReply
from .email_parser import clean_email_body


FLOWVELLO_KNOWLEDGE = """
Company: FlowVello — AI Automation Agency
Website: (your website)
Location: Mirpur, Pakistan

Services:
- AI Chatbots & Voice Agents: 24/7 customer service bots, WhatsApp AI assistants
- WhatsApp Automation Systems: Lead capture, auto-reply, follow-ups, property alerts
- Email Automation: Smart email classification, AI drafting, auto follow-ups
- CRM & Lead Management: Automated lead tracking from multiple sources
- Custom AI Workflows: n8n/Make automations, custom integrations
- Real Estate Sales Systems: Complete lead-to-deal automation for property agencies

Pricing: Custom quotes based on scope. Typically Rs. 15,000-50,000 setup + Rs. 5,000-25,000/month.

Tone: Professional, friendly, confident. Mix of English and Urdu when appropriate.

Default CTA: "Book a free discovery call to discuss your needs."

Rules:
- Never promise guaranteed results or specific ROI
- Never offer discounts without discussing first
- Keep replies concise (3-5 sentences preferred)
- Always include a CTA when appropriate
- For pricing questions, give ranges and offer a call
- For support, acknowledge the issue and provide timeline
"""


class DraftGenerator:
    def __init__(self):
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            config.AI_MODEL,
            generation_config={
                "temperature": 0.4,
                "max_output_tokens": config.AI_MAX_TOKENS,
            }
        )
    
    def generate(self, email: EmailMessage, classification: EmailClassification) -> DraftReply:
        """Generate a draft reply for an email."""
        clean_body = clean_email_body(email.body_text, email.body_html)
        
        lang_hint = ""
        if any(char in email.body_text for char in "۔کیےہیںآپ"):
            lang_hint = "Write the reply in Urdu/Roman Urdu mixed with English where natural."
        
        auto_reply_services = [
            "do you offer", "what services", "how much", "pricing",
            "business hours", "location", "what is flowvello"
        ]
        is_auto_replyable = any(
        keyword in email.subject.lower() + clean_body[:500].lower()
            for keyword in auto_reply_services
        )
        
        prompt = f"""You are FlowVello's AI email assistant. Draft a professional reply.

CONTEXT:
Company Info: {FLOWVELLO_KNOWLEDGE}

INCOMING EMAIL:
From: {email.from_name} <{email.from_address}>
Subject: {email.subject}
Body:
{clean_body[:2000]}

CLASSIFICATION:
Intent: {classification.intent}
Priority: {classification.priority}
Sentiment: {classification.sentiment}
Lead: {'Yes' if classification.is_lead else 'No'}

{lang_hint}

RULES:
- If they ask about services: briefly explain, offer a discovery call
- If they ask pricing: give a range (Rs. 15K-50K setup, Rs. 5K-25K/mo), offer a call
- If lead: enthusiastic, include CTA to book call
- If support: acknowledge, apologize if needed, give timeline
- If complaint: apologize sincerely, offer solution
- If partnership: show interest, suggest a meeting
- Keep it to 3-5 sentences
- Sign with "Best, FlowVello Team"
- {"This can be sent automatically (FAQ-type question)" if is_auto_replyable else "This needs human approval before sending"}

AUTO-REPLYABLE: {"true" if is_auto_replyable else "false"}

Return ONLY valid JSON:
{{
  "subject": "Re: {email.subject}",
  "body": "full draft reply",
  "tone": "professional",
  "needs_approval": true/false,
  "approval_reason": "reason if needs_approval or empty string"
}}"""
        
        try:
            response = self.model.generate_content(prompt)
            result = self._parse_response(response.text)
            if result:
                return DraftReply(
                    email_id=email.id,
                    subject=result.get("subject", f"Re: {email.subject}"),
                    body=result.get("body", ""),
                    tone=result.get("tone", "professional"),
                    needs_approval=result.get("needs_approval", True),
                    approval_reason=result.get("approval_reason", ""),
                )
        except Exception as e:
            print(f"AI draft generation failed: {e}")
        
        # Fallback draft
        return DraftReply(
            email_id=email.id,
            subject=f"Re: {email.subject}",
            body=f"Hi {email.from_name},\n\nThank you for reaching out to FlowVello. I'd love to help you with this.\n\nCould you please share a few more details about what you need? I'll get back to you promptly with a tailored solution.\n\nBest,\nFlowVello Team",
            tone="professional",
            needs_approval=True,
            approval_reason="Standard fallback draft — needs review",
        )
    
    def generate_followup(self, email: EmailMessage, original_reply: str, step: int) -> str:
        """Generate a follow-up email."""
        prompt = f"""Generate a polite, brief follow-up email. The recipient hasn't replied to our previous email.

Original email from: {email.from_name} <{email.from_address}>
Subject: {email.subject}
Previous reply: {original_reply[:500]}

Step {step} of 3 follow-up sequence.

Guidelines:
- Step 1 (Day 3): "Just checking if you saw my previous email..."
- Step 2 (Day 7): "Still interested? Happy to answer any questions."
- Step 3 (Day 14): "Last follow-up. If timing isn't right, no worries."

Keep it to 2-3 sentences. Be polite, not pushy.
Sign: "Best, FlowVello Team"

Return ONLY the email body text, no JSON."""
        
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Follow-up generation failed: {e}")
            return f"Hi {email.from_name},\n\nJust checking in on my previous email. Let me know if you have any questions!\n\nBest,\nFlowVello Team"
    
    def _parse_response(self, text: str) -> dict:
        """Extract JSON from AI response."""
        text = re.sub(r'```(?:json)?\s*', '', text)
        text = text.strip()
        
        start = text.find('{')
        end = text.rfind('}')
        if start == -1 or end == -1:
            return None
        
        json_str = text[start:end + 1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None
