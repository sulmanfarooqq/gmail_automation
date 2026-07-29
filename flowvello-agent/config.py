"""
FlowVello Gmail AI Agent - Configuration
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    # Gmail OAuth
    GMAIL_CREDENTIALS_FILE = os.getenv("GMAIL_CREDENTIALS_FILE", "credentials.json")
    GMAIL_TOKEN_DIR = os.getenv("GMAIL_TOKEN_DIR", "credentials")
    GMAIL_SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/gmail.send",
        "https://www.googleapis.com/auth/gmail.modify",
    ]
    
    # Flask
    FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
    FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
    FLASK_DEBUG = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    
    # Email processing
    SCAN_INTERVAL_MINUTES = int(os.getenv("SCAN_INTERVAL_MINUTES", "5"))
    MAX_EMAILS_PER_SCAN = int(os.getenv("MAX_EMAILS_PER_SCAN", "20"))
    FOLLOWUP_CHECK_HOURS = int(os.getenv("FOLLOWUP_CHECK_HOURS", "6"))
    
    # AI
    AI_MODEL = os.getenv("AI_MODEL", "gemini-1.5-flash")
    AI_TEMPERATURE = float(os.getenv("AI_TEMPERATURE", "0.3"))
    AI_MAX_TOKENS = int(os.getenv("AI_MAX_TOKENS", "1024"))
    AI_RETRY_ATTEMPTS = 2
    
    # Paths
    DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
    TOKEN_DIR = os.path.join(os.path.dirname(__file__), "credentials")
    DB_PATH = os.path.join(DATA_DIR, "flowvello_agent.db")
    
    # Notifications
    NOTIFY_ON_LEAD = os.getenv("NOTIFY_ON_LEAD", "true").lower() == "true"
    NOTIFY_ON_URGENT = os.getenv("NOTIFY_ON_URGENT", "true").lower() == "true"
    
    HOURS_SAVED_PER_EMAIL = float(os.getenv("HOURS_SAVED_PER_EMAIL", "0.1"))

config = Config()
