"""
Rate limiter for API endpoints
Implements rate limiting to prevent abuse of the chat endpoint
"""
import time
from typing import Dict, Optional
from collections import defaultdict
import threading
from datetime import datetime, timedelta


class RateLimiter:
    """
    Simple in-memory rate limiter using sliding window algorithm.
    """

    def __init__(self, requests: int = 10, per_seconds: int = 60):
        """
        Initialize rate limiter.

        Args:
            requests: Number of requests allowed
            per_seconds: Time window in seconds
        """
        self.requests = requests
        self.per_seconds = per_seconds
        self.requests_by_key: Dict[str, list] = defaultdict(list)
        self.lock = threading.Lock()

    def is_allowed(self, key: str) -> bool:
        """
        Check if request is allowed for the given key.

        Args:
            key: Unique identifier for the client (IP address, user ID, etc.)

        Returns:
            True if request is allowed, False otherwise
        """
        with self.lock:
            now = time.time()
            # Remove old requests outside the time window
            self.requests_by_key[key] = [
                req_time for req_time in self.requests_by_key[key]
                if now - req_time < self.per_seconds
            ]

            # Check if we've exceeded the limit
            if len(self.requests_by_key[key]) >= self.requests:
                return False

            # Add current request
            self.requests_by_key[key].append(now)
            return True

    def get_reset_time(self, key: str) -> Optional[float]:
        """
        Get the time when the rate limit will reset for the given key.

        Args:
            key: Unique identifier for the client

        Returns:
            Unix timestamp of reset time, or None if no requests recorded
        """
        with self.lock:
            if key not in self.requests_by_key or not self.requests_by_key[key]:
                return None

            # Find the oldest request in the current window
            oldest = min(self.requests_by_key[key])
            return oldest + self.per_seconds


# Global rate limiter instance
_default_limiter = None


def get_default_rate_limiter() -> RateLimiter:
    """
    Get the default rate limiter instance.
    """
    global _default_limiter
    if _default_limiter is None:
        # Default: 10 requests per minute
        _default_limiter = RateLimiter(requests=10, per_seconds=60)
    return _default_limiter


def is_chat_request_allowed(client_identifier: str) -> bool:
    """
    Check if a chat request is allowed for the given client.

    Args:
        client_identifier: Unique identifier for the client

    Returns:
        True if request is allowed, False otherwise
    """
    limiter = get_default_rate_limiter()
    return limiter.is_allowed(client_identifier)


def get_rate_limit_reset_time(client_identifier: str) -> Optional[float]:
    """
    Get the reset time for the given client's rate limit.

    Args:
        client_identifier: Unique identifier for the client

    Returns:
        Unix timestamp of reset time, or None if no requests recorded
    """
    limiter = get_default_rate_limiter()
    return limiter.get_reset_time(client_identifier)


if __name__ == "__main__":
    # Test the rate limiter
    limiter = RateLimiter(requests=3, per_seconds=10)  # 3 requests per 10 seconds

    client_key = "test_client"

    print("Rate Limiter Test")
    print("=" * 30)

    for i in range(5):
        allowed = limiter.is_allowed(client_key)
        reset_time = limiter.get_reset_time(client_key)

        print(f"Request {i+1}: {'ALLOWED' if allowed else 'BLOCKED'}", end="")
        if reset_time:
            import datetime
            reset_dt = datetime.datetime.fromtimestamp(reset_time)
            print(f" (Reset: {reset_dt.strftime('%H:%M:%S')})")
        else:
            print()

        if not allowed:
            print("  Rate limit exceeded!")

        time.sleep(1)