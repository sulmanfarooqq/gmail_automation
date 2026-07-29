# Updated Project Structure with Safety Features

Here's where safety measures are in the code:

## rate_limit.py (New File — Add Before Deploy)

```python
"""
Rate limiting for Gmail API calls — prevents flagging.
"""
import time
from datetime import datetime, timedelta
from collections import deque


class RateLimiter:
    def __init__(self, max_per_minute=5, max_per_hour=100, max_per_day=500):
        self.max_per_minute = max_per_minute
        self.max_per_hour = max_per_hour
        self.max_per_day = max_per_day
        self.timestamps = deque()
    
    def can_send(self) -> bool:
        now = datetime.now()
        # Remove timestamps older than 1 day
        cutoff = now - timedelta(days=1)
        while self.timestamps and self.timestamps[0] < cutoff:
            self.timestamps.popleft()
        
        # Check per-minute
        minute_ago = now - timedelta(minutes=1)
        sends_last_minute = sum(1 for t in self.timestamps if t > minute_ago)
        if sends_last_minute >= self.max_per_minute:
            return False
        
        # Check per-hour
        hour_ago = now - timedelta(hours=1)
        sends_last_hour = sum(1 for t in self.timestamps if t > hour_ago)
        if sends_last_hour >= self.max_per_hour:
            return False
        
        # Check per-day
        if len(self.timestamps) >= self.max_per_day:
            return False
        
        return True
    
    def record_send(self):
        self.timestamps.append(datetime.now())
    
    def wait_if_needed(self):
        """Block until it's safe to send, with 2s minimum gap."""
        import time
        time.sleep(2)  # Minimum 2 seconds between sends
        
        while not self.can_send():
            wait_time = 60  # Wait 1 minute if rate limited
            print(f"⚠️ Rate limit reached. Waiting {wait_time}s...")
            time.sleep(wait_time)


# Global rate limiter
rate_limiter = RateLimiter()
```

## Updated gmail_service.py — Safe Send

```python
# In gmail_service.py, modify send_email to use rate limiter:

def send_email(to, subject, body, reply_to_msg_id=None):
    rate_limiter.wait_if_needed()
    
    # ... existing send logic ...
    
    rate_limiter.record_send()
    return True
```

## User-Agent Header (Professional)

The Google API Python client automatically sets proper User-Agent. No extra config needed. It identifies as `google-api-python-client/...`. This is professional and expected.

## OAuth Token Management (Already Built)

The token is stored as `credentials/token.pickle`. It auto-refreshes. You only need to re-authenticate if:
- You delete the token file
- You revoke access from Google Account settings
- Google changes their OAuth policies (rare)

## Summary of Safety Checklist

- [ ] Rate limiter: Max 5/min, 100/hr, 500/day ✅ (add rate_limit.py)
- [ ] Thread replies properly: In-Reply-To + References headers ✅ (already in code)
- [ ] Human approval before send: Draft must be approved ✅ (already in code)
- [ ] SPF/DKIM/DMARC: Set up if using custom domain ⚠️ (add if needed)
- [ ] Single Gmail account: ✅ (designed for FlowVello only)
- [ ] Reply-only pattern: Never cold email ✅ (agent only replies)
- [ ] Monitor Google warnings: Check "Security" page weekly ✅ (manual)
- [ ] OAuth Testing mode: Never publish to production ✅ (keep on Testing)
