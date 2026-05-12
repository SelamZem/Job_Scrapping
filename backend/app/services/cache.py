from typing import Optional, Any
from functools import wraps

class NoOpCache:
    """No-op cache service - does nothing but maintains same interface"""
    
    def __init__(self):
        print("⚠️ Running without cache (database only)")
    
    def get(self, key: str) -> Optional[Any]:
        """Always returns None (no cache hit)"""
        return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Always returns False (cache not set)"""
        return False
    
    def delete(self, key: str) -> bool:
        """Always returns False (cache not deleted)"""
        return False
    
    def invalidate_jobs_cache(self) -> None:
        """Does nothing"""
        pass

# Global cache instance
cache = NoOpCache()

def cached(ttl: int = 3600, key_prefix: str = "cache"):
    """Decorator that does nothing (no caching)"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Just execute function without caching
            return func(*args, **kwargs)
        return wrapper
    return decorator
