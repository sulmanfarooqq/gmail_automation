"""
Gmail OAuth 2.0 — connect flowvello@gmail.com
"""
import os
import pickle
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from config import config


def get_gmail_service():
    """
    Get authenticated Gmail API service.
    First time: opens browser for OAuth consent.
    Subsequent: uses stored token.
    """
    creds = _load_credentials()
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                config.GMAIL_CREDENTIALS_FILE, config.GMAIL_SCOPES
            )
            creds = flow.run_localServer(port=0)
        _save_credentials(creds)
    
    return build("gmail", "v1", credentials=creds)


def _load_credentials():
    """Load saved OAuth token from disk."""
    token_path = Path(config.TOKEN_DIR) / "token.pickle"
    if token_path.exists():
        with open(token_path, "rb") as f:
            return pickle.load(f)
    return None


def _save_credentials(creds):
    """Save OAuth token to disk."""
    Path(config.TOKEN_DIR).mkdir(parents=True, exist_ok=True)
    token_path = Path(config.TOKEN_DIR) / "token.pickle"
    with open(token_path, "wb") as f:
        pickle.dump(creds, f)


def is_authenticated() -> bool:
    """Check if we have valid stored credentials."""
    creds = _load_credentials()
    return creds is not None and creds.valid


def get_auth_url() -> str:
    """Get OAuth URL for manual auth flow (for web dashboard)."""
    flow = InstalledAppFlow.from_client_secrets_file(
        config.GMAIL_CREDENTIALS_FILE, config.GMAIL_SCOPES
    )
    flow.redirect_uri = "urn:ietf:wg:oauth:2.0:oob"
    return flow.authorization_url()[0]
