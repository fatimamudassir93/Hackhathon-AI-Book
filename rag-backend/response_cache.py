"""
Response cache for frequently asked questions
Implements caching to reduce API calls and improve response time
"""
import hashlib
import json
from typing import Any, Dict, Optional, Tuple
from datetime import datetime, timedelta
from collections import OrderedDict
import threading


class ResponseCache:
    """
    Simple in-memory LRU cache for chat responses.
    """

    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        """
        Initialize response cache.

        Args:
            max_size: Maximum number of cached responses
            ttl_seconds: Time-to-live for cached responses in seconds
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache: OrderedDict[str, Tuple[Any, datetime]] = OrderedDict()
        self.lock = threading.Lock()

    def _get_cache_key(self, question: str, context: Optional[Dict] = None) -> str:
        """
        Generate a cache key from the question and context.

        Args:
            question: The question text
            context: Optional context (selected text, chapter filter, etc.)

        Returns:
            Cache key string
        """
        cache_input = {
            'question': question,
            'context': context or {}
        }
        cache_str = json.dumps(cache_input, sort_keys=True, default=str)
        return hashlib.sha256(cache_str.encode('utf-8')).hexdigest()

    def get(self, question: str, context: Optional[Dict] = None) -> Optional[Any]:
        """
        Get cached response for the given question and context.

        Args:
            question: The question text
            context: Optional context (selected text, chapter filter, etc.)

        Returns:
            Cached response if found and not expired, None otherwise
        """
        with self.lock:
            key = self._get_cache_key(question, context)

            if key not in self.cache:
                return None

            response, timestamp = self.cache[key]

            # Check if expired
            if datetime.now() - timestamp > timedelta(seconds=self.ttl_seconds):
                del self.cache[key]
                return None

            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return response

    def set(self, question: str, response: Any, context: Optional[Dict] = None):
        """
        Set a cached response for the given question and context.

        Args:
            question: The question text
            context: Optional context (selected text, chapter filter, etc.)
            response: The response to cache
        """
        with self.lock:
            key = self._get_cache_key(question, context)

            # Remove expired entries
            self._remove_expired()

            # Add new entry
            self.cache[key] = (response, datetime.now())

            # Remove oldest if over capacity
            while len(self.cache) > self.max_size:
                self.cache.popitem(last=False)

    def _remove_expired(self):
        """Remove expired entries from cache."""
        now = datetime.now()
        expired_keys = [
            key for key, (_, timestamp) in self.cache.items()
            if now - timestamp > timedelta(seconds=self.ttl_seconds)
        ]
        for key in expired_keys:
            del self.cache[key]

    def clear(self):
        """Clear all cached responses."""
        with self.lock:
            self.cache.clear()

    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        with self.lock:
            self._remove_expired()
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'ttl_seconds': self.ttl_seconds
            }


# Global cache instance
_default_cache = None


def get_default_response_cache() -> ResponseCache:
    """
    Get the default response cache instance.
    """
    global _default_cache
    if _default_cache is None:
        # Default: 1000 responses, 1 hour TTL
        _default_cache = ResponseCache(max_size=1000, ttl_seconds=3600)
    return _default_cache


def get_cached_response(question: str, context: Optional[Dict] = None) -> Optional[Any]:
    """
    Get a cached response for the given question and context.

    Args:
        question: The question text
        context: Optional context (selected text, chapter filter, etc.)

    Returns:
        Cached response if found and not expired, None otherwise
    """
    cache = get_default_response_cache()
    return cache.get(question, context)


def cache_response(question: str, response: Any, context: Optional[Dict] = None):
    """
    Cache a response for the given question and context.

    Args:
        question: The question text
        response: The response to cache
        context: Optional context (selected text, chapter filter, etc.)
    """
    cache = get_default_response_cache()
    cache.set(question, response, context)


def get_cache_stats() -> Dict[str, int]:
    """
    Get cache statistics.

    Returns:
        Dictionary with cache statistics
    """
    cache = get_default_response_cache()
    return cache.get_stats()


if __name__ == "__main__":
    # Test the response cache
    cache = ResponseCache(max_size=5, ttl_seconds=10)

    print("Response Cache Test")
    print("=" * 30)

    # Test caching and retrieval
    question1 = "What is machine learning?"
    response1 = {"answer": "Machine learning is a subset of AI...", "sources": ["Chapter 1"]}

    cache.set(question1, response1, None)
    cached = cache.get(question1, None)
    print(f"Cache hit: {cached is not None}")

    # Test with context
    context = {"chapter_filter": "Chapter 2", "selected_text": "Some text here"}
    question2 = "How does this relate to robotics?"
    response2 = {"answer": "In robotics, this relates to...", "sources": ["Chapter 2"]}

    cache.set(question2, response2, context)
    cached = cache.get(question2, context)
    print(f"Cache hit with context: {cached is not None}")

    # Test stats
    stats = cache.get_stats()
    print(f"Cache stats: {stats}")