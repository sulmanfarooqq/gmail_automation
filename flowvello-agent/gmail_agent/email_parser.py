"""
Email parsing — clean up email body for AI processing.
"""
import re
from bs4 import BeautifulSoup
from markdownify import markdownify as md


def clean_email_body(body_text: str, body_html: str = "") -> str:
    """
    Clean email body for AI consumption.
    Strips signatures, quoted replies, and normalizes text.
    """
    text = body_text
    
    # If no plain text, convert HTML
    if not text and body_html:
        text = html_to_text(body_html)
    
    if not text:
        return ""
    
    # Remove email signatures (common patterns)
    text = _strip_signatures(text)
    
    # Remove quoted replies
    text = _strip_quoted_replies(text)
    
    # Normalize whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = text.strip()
    
    return text


def html_to_text(html: str) -> str:
    """Convert HTML email body to clean text."""
    soup = BeautifulSoup(html, "html.parser")
    
    # Remove scripts and styles
    for tag in soup(["script", "style"]):
        tag.decompose()
    
    text = soup.get_text(separator="\n")
    return re.sub(r'\n{3,}', '\n\n', text).strip()


def _strip_signatures(text: str) -> str:
    """Remove common email signature patterns."""
    patterns = [
        r'-- \n.*',           # Standard email sig
        r'^Best regards.*$',  # Common sign-offs
        r'^Thanks,.*$',
        r'^Regards,.*$',
        r'^Sincerely,.*$',
        r'^Cheers,.*$',
        r'^Warmly,.*$',
        r'^Sent from.*$',     # Mobile signatures
        r'^Get Outlook.*$',
    ]
    
    lines = text.split('\n')
    clean_lines = []
    
    for line in lines:
        stripped = line.strip()
        # Stop at common signature markers
        if stripped == '--' or stripped == '___':
            break
        # Skip if matches signature pattern
        if any(re.match(p, stripped) for p in patterns):
            continue
        clean_lines.append(line)
    
    return '\n'.join(clean_lines).strip()


def _strip_quoted_replies(text: str) -> str:
    """Remove quoted reply content (lines starting with >)."""
    lines = text.split('\n')
    clean_lines = []
    
    in_quote = False
    for line in lines:
        stripped = line.strip()
        # Gmail quote marker
        if stripped.startswith('>'):
            in_quote = True
            continue
        # On <date>, <person> wrote:
        if re.match(r'^On .+ wrote:$', stripped):
            in_quote = True
            continue
        # Forwarded message
        if re.match(r'^-+\s*Forwarded message\s*-+', stripped, re.IGNORECASE):
            in_quote = True
            continue
        # Original message
        if re.match(r'^[-_]+Original Message[-_]+', stripped, re.IGNORECASE):
            in_quote = True
            continue
        
        if not in_quote:
            clean_lines.append(line)
        elif stripped == '':
            # Empty line might end the quote
            in_quote = False
            clean_lines.append(line)
    
    return '\n'.join(clean_lines).strip()


def extract_phone_numbers(text: str) -> list[str]:
    """Extract Pakistani phone numbers from text."""
    patterns = [
        r'\+92\d{10}',              # +923001234567
        r'03\d{9}',                 # 03001234567
        r'0\d{2,3}[-\s]?\d{7}',     # 051-1234567
    ]
    phones = []
    for pattern in patterns:
        phones.extend(re.findall(pattern, text))
    return phones


def extract_name_from_email(from_address: str) -> str:
    """Extract likely name from email prefix."""
    name_part = from_address.split('@')[0]
    name_part = name_part.replace('.', ' ').replace('_', ' ').replace('-', ' ')
    # Capitalize
    return ' '.join(w.capitalize() for w in name_part.split())
