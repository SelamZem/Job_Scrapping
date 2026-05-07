import json
import redis
import os
from typing import Optional, Any
from functools import wraps

class RedisCache:
    """Redis cache service for job listings"""
    
    def __init__(self):
        self.enabled = False
        self.client = None
        self.ttl = 3600  # 1 hour default
        
        # Try to connect to Redis
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        try:
            self.client = redis.from_url(redis_url, decode_responses=True)
            self.client.ping()
            self.enabled = True
            print(f"✅ Redis connected: {redis_url}")
        except Exception as e:
            print(f"⚠️ Redis not available: {e}")
            print("⚠️ Running without cache (database only)")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.enabled or not self.client:
            return None
        
        try:
            data = self.client.get(key)
            if data:
                return json.loads(data)
        except Exception as e:
            print(f"Cache get error: {e}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache"""
        if not self.enabled or not self.client:
            return False
        
        try:
            ttl = ttl or self.ttl
            self.client.setex(key, ttl, json.dumps(value))
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self.enabled or not self.client:
            return False
        
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def invalidate_jobs_cache(self) -> None:
        """Invalidate all jobs-related cache"""
        if not self.enabled or not self.client:
            return
        
        try:
            # Delete all keys starting with "jobs:"
            for key in self.client.scan_iter(match="jobs:*"):
                self.client.delete(key)
            print("🗑️ Jobs cache invalidated")
        except Exception as e:
            print(f"Cache invalidate error: {e}")

# Global cache instance
cache = RedisCache()

def cached(ttl: int = 3600, key_prefix: str = "cache"):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                print(f"⚡ Cache hit: {func.__name__}")
                return cached_result
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result, ttl)
            print(f"💾 Cache set: {func.__name__}")
            
            return result
        return wrapper
    return decorator
