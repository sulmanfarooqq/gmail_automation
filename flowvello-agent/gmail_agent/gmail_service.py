"""
Gmail API operations — fetch, send, manage emails.
Rate-limited to never trigger Google's spam detection.
"""
import base64
import time
from datetime import datetime, timezone
from email.mime.text import MIMEText
from typing import Optional

from googleapiclient.errors import HttpError

from .auth import get_gmail_service
from .models import EmailMessage
from .rate_limit import rate_limiter


def fetch_recent_emails(max_results: int = 20) -> list[EmailMessage]:
    """Fetch most recent emails from inbox."""
    service = get_gmail_service()
    emails = []

    try:
        result = service.users().messages().list(
            userId="me",
            labelIds=["INBOX"],
            maxResults=max_results,
        ).execute()

        for msg_data in result.get("messages", []):
            email = _fetch_message_detail(service, msg_data["id"])
            if email:
                emails.append(email)

    except HttpError as e:
        print(f"Gmail API error: {e}")

    return emails


def fetch_unread_emails(max_results: int = 20) -> list[EmailMessage]:
    """Fetch unread emails from inbox."""
    service = get_gmail_service()
    emails = []

    try:
        result = service.users().messages().list(
            userId="me",
            labelIds=["INBOX", "UNREAD"],
            maxResults=max_results,
        ).execute()

        for msg_data in result.get("messages", []):
            email = _fetch_message_detail(service, msg_data["id"])
            if email:
                emails.append(email)

    except HttpError as e:
        print(f"Gmail API error: {e}")

    return emails


def _fetch_message_detail(service, msg_id: str) -> Optional[EmailMessage]:
    """Fetch full email details by ID."""
    try:
        msg = service.users().messages().get(
            userId="me", id=msg_id, format="full"
        ).execute()
    except HttpError:
        return None

    headers = {h["name"].lower(): h["value"] for h in msg["payload"].get("headers", [])}
    
    # Parse body
    body_text, body_html = _extract_body(msg["payload"])
    
    # Parse attachments
    attachments = _extract_attachments(service, msg_id, msg["payload"])
    
    # Parse timestamp
    internal_date = int(msg.get("internalDate", 0))
    received_at = datetime.fromtimestamp(internal_date / 1000, tz=timezone.utc)
    
    # Determine if incoming
    from_addr = headers.get("from", "")
    is_incoming = True  # Messages in INBOX are incoming
    
    return EmailMessage(
        id=msg["id"],
        thread_id=msg["threadId"],
        from_address=_extract_email(from_addr),
        from_name=_extract_name(from_addr),
        to_addresses=[_extract_email(headers.get("to", ""))],
        cc_addresses=[_extract_email(headers.get("cc", ""))] if headers.get("cc") else [],
        subject=headers.get("subject", "(No Subject)"),
        body_text=body_text,
        body_html=body_html,
        received_at=received_at,
        is_incoming=is_incoming,
        labels=msg.get("labelIds", []),
        attachments=attachments,
    )


def _extract_body(payload) -> tuple[str, str]:
    """Extract plain text and HTML body from email payload."""
    body_text = ""
    body_html = ""
    
    if "parts" in payload:
        for part in payload["parts"]:
            if part["mimeType"] == "text/plain":
                data = part["body"].get("data", "")
                body_text = _decode_base64(data)
            elif part["mimeType"] == "text/html":
                data = part["body"].get("data", "")
                body_html = _decode_base64(data)
            elif "parts" in part:
                # Nested multipart
                t, h = _extract_body(part)
                body_text = body_text or t
                body_html = body_html or h
    else:
        data = payload["body"].get("data", "")
        if payload["mimeType"] == "text/plain":
            body_text = _decode_base64(data)
        elif payload["mimeType"] == "text/html":
            body_html = _decode_base64(data)
    
    return body_text, body_html


def _extract_attachments(service, msg_id, payload) -> list:
    """Extract attachment metadata."""
    attachments = []
    if "parts" in payload:
        for part in payload["parts"]:
            if part.get("filename") and part.get("filename") != "":
                attachments.append({
                    "id": part["body"].get("attachmentId"),
                    "filename": part["filename"],
                    "mimeType": part["mimeType"],
                    "size": part["body"].get("size", 0),
                })
            if "parts" in part:
                attachments.extend(_extract_attachments(service, msg_id, part))
    return attachments


def send_email(to: str, subject: str, body: str, reply_to_msg_id: Optional[str] = None):
    """Send an email via Gmail with rate limiting to prevent flagging."""
    rate_limiter.wait_if_needed()
    service = get_gmail_service()

    message = MIMEText(body, "plain")
    message["to"] = to
    message["subject"] = subject

    if reply_to_msg_id:
        original = service.users().messages().get(
            userId="me", id=reply_to_msg_id, format="metadata",
            metadataHeaders=["Message-ID", "References"]
        ).execute()

        orig_headers = {h["name"]: h["value"] for h in original["payload"]["headers"]}
        message["In-Reply-To"] = orig_headers.get("Message-ID", "")
        message["References"] = orig_headers.get("References", "") + " " + orig_headers.get("Message-ID", "")

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        service.users().messages().send(userId="me", body={"raw": raw}).execute()
        rate_limiter.record_send()
        print(f"   ✅ Sent to {to}")
        return True
    except HttpError as e:
        print(f"   ❌ Send error: {e}")
        return False


def mark_as_read(msg_id: str):
    """Mark email as read."""
    service = get_gmail_service()
    service.users().messages().modify(
        userId="me", id=msg_id,
        body={"removeLabelIds": ["UNREAD"]}
    ).execute()


def add_label(msg_id: str, label: str):
    """Add a label to an email."""
    service = get_gmail_service()
    service.users().messages().modify(
        userId="me", id=msg_id,
        body={"addLabelIds": [label]}
    ).execute()


def _decode_base64(data: str) -> str:
    """Decode base64 email data."""
    if not data:
        return ""
    try:
        padded = data + "=" * (4 - len(data) % 4)
        return base64.urlsafe_b64decode(padded).decode("utf-8", errors="replace")
    except Exception:
        return ""


def _extract_email(from_str: str) -> str:
    """Extract email address from 'Name <email>' format."""
    if "<" in from_str:
        return from_str.split("<")[1].rstrip(">")
    return from_str.strip()


def _extract_name(from_str: str) -> str:
    """Extract name from 'Name <email>' format."""
    if "<" in from_str:
        return from_str.split("<")[0].strip().strip('"')
    return from_str.rsplit("@", 1)[0] if "@" in from_str else from_str
