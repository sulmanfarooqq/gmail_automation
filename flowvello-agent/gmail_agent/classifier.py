"""
AI Email Classifier — uses Gemini to understand every incoming email.
"""
import json
import re
import google.generativeai as genai
from config import config
from .models import EmailMessage, EmailClassification
from .email_parser import clean_email_body


class EmailClassifier:
    def __init__(self):
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            config.AI_MODEL,
            generation_config={
                "temperature": config.AI_TEMPERATURE,
                "max_output_tokens": config.AI_MAX_TOKENS,
            }
        )
    
    def classify(self, email: EmailMessage) -> EmailClassification:
        """Classify a single email using Gemini."""
        clean_body = clean_email_body(email.body_text, email.body_html)
        
        prompt = f"""You are FlowVello's AI email assistant. Analyze this email and return JSON only.

EMAIL:
From: {email.from_name} <{email.from_address}>
Subject: {email.subject}
Body:
{clean_body[:3000]}

TASK: Classify this email into exactly one category:

Categories:
- lead: Someone asking about AI automation services (chatbots, voice agents, WhatsApp systems, email automation, CRM)
- client_support: Existing client with a technical issue or question
- billing: Payment, invoice, or pricing questions
- partnership: Collaboration or partnership request
- meeting_request: Asking to schedule a call/meeting
- complaint: Negative feedback or complaint
- spam: Promotional, newsletter, or irrelevant
- other: Anything that doesn't fit above

Return ONLY valid JSON (no markdown, no code blocks):
{{
  "intent": "category_name",
  "confidence": 0.0-1.0,
  "priority": "low|medium|high|urgent",
  "sentiment": "negative|neutral|positive",
  "is_lead": true/false,
  "lead_score": 0-100,
  "requires_reply": true/false,
  "requires_approval": true/false,
  "categories": ["tag1", "tag2"],
  "extracted_name": "person name or empty string",
  "extracted_phone": "phone number or empty string",
  "extracted_company": "company name or empty string",
  "extracted_service": "requested service or empty string",
  "summary": "one-line summary of the email"
}}"""
        
        for attempt in range(config.AI_RETRY_ATTEMPTS + 1):
            try:
                response = self.model.generate_content(prompt)
                result = self._parse_response(response.text)
                if result:
                    return EmailClassification(
                        email_id=email.id,
                        **result
                    )
            except Exception as e:
                if attempt < config.AI_RETRY_ATTEMPTS:
                    continue
                print(f"AI classification failed: {e}")
        
        # Fallback classification
        return EmailClassification(
            email_id=email.id,
            intent="other",
            confidence=0.0,
            priority="medium",
            sentiment="neutral",
            is_lead=False,
            lead_score=0,
            requires_reply=True,
            requires_approval=True,
            categories=["unclassified"],
            summary=f"Email from {email.from_name}: {email.subject[:100]}",
            ai_model=config.AI_MODEL
        )
    
    def _parse_response(self, text: str) -> dict:
        """Extract JSON from AI response, handling markdown wrappers."""
        # Remove markdown code blocks
        text = re.sub(r'```(?:json)?\s*', '', text)
        text = text.strip()
        
        # Find JSON object
        start = text.find('{')
        end = text.rfind('}')
        if start == -1 or end == -1:
            return None
        
        json_str = text[start:end + 1]
        
        try:
            data = json.loads(json_str)
            
            # Validate required fields
            required = ["intent", "priority", "sentiment", "is_lead"]
            for field in required:
                if field not in data:
                    return None
            
            return {
                "intent": data.get("intent", "other"),
                "confidence": float(data.get("confidence", 0.5)),
                "priority": data.get("priority", "medium"),
                "sentiment": data.get("sentiment", "neutral"),
                "is_lead": bool(data.get("is_lead", False)),
                "lead_score": int(data.get("lead_score", 0)),
                "requires_reply": bool(data.get("requires_reply", True)),
                "requires_approval": bool(data.get("requires_approval", True)),
                "categories": data.get("categories", []),
                "extracted_name": str(data.get("extracted_name", "")),
                "extracted_phone": str(data.get("extracted_phone", "")),
                "extracted_company": str(data.get("extracted_company", "")),
                "extracted_service": str(data.get("extracted_service", "")),
                "summary": str(data.get("summary", "")),
                "ai_model": config.AI_MODEL,
            }
        except (json.JSONDecodeError, ValueError, TypeError):
            return None
