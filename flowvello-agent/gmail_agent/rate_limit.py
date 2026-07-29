"""
Rate limiting for Gmail API — prevents flagging by looking like a human.
"""
import time
from datetime import datetime, timedelta
from collections import deque


class RateLimiter:
    """Ensures sending behavior stays within safe limits."""

    def __init__(self, max_per_minute=4, max_per_hour=80, max_per_day=400):
        self.max_per_minute = max_per_minute
        self.max_per_hour = max_per_hour
        self.max_per_day = max_per_day
        self.timestamps = deque()

    def can_send(self) -> bool:
        now = datetime.now()
        cutoff = now - timedelta(days=1)
        while self.timestamps and self.timestamps[0] < cutoff:
            self.timestamps.popleft()

        per_minute = sum(1 for t in self.timestamps if t > now - timedelta(minutes=1))
        per_hour = sum(1 for t in self.timestamps if t > now - timedelta(hours=1))

        if per_minute >= self.max_per_minute:
            return False
        if per_hour >= self.max_per_hour:
            return False
        if len(self.timestamps) >= self.max_per_day:
            return False
        return True

    def record_send(self):
        self.timestamps.append(datetime.now())

    def wait_if_needed(self):
        """Block until it's safe to send. Minimum 3s gap between sends."""
        time.sleep(3)
        while not self.can_send():
            wait = 60
            print(f"⏳ Rate limit reached. Waiting {wait}s...")
            time.sleep(wait)


rate_limiter = RateLimiter()
