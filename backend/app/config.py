"""
Production configuration for Render deployment
"""
import os
from functools import wraps
import time
import json

# Production environment detection
IS_PRODUCTION = os.getenv("RENDER", "false").lower() == "true"

# Simple in-memory cache for production (no Redis dependency)
class SimpleCache:
    def __init__(self):
        self.cache = {}
        self.cache_times = {}
        self.default_ttl = 300  # 5 minutes for production
    
    def get(self, key):
        if key not in self.cache:
            return None
        
        # Check if cache is expired
        if time.time() - self.cache_times.get(key, 0) > self.default_ttl:
            del self.cache[key]
            del self.cache_times[key]
            return None
        
        return self.cache[key]
    
    def set(self, key, value, ttl=None):
        self.cache[key] = value
        self.cache_times[key] = time.time()
    
    def delete(self, key):
        self.cache.pop(key, None)
        self.cache_times.pop(key, None)
    
    def clear_pattern(self, pattern):
        keys_to_delete = [k for k in self.cache.keys() if pattern in k]
        for key in keys_to_delete:
            self.cache.pop(key, None)
            self.cache_times.pop(key, None)

# Global cache instance
cache = SimpleCache()

def cache_response(ttl=300):
    """Decorator for caching API responses in production"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not IS_PRODUCTION:
                return await func(*args, **kwargs)
            
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                print(f"🚀 Cache hit: {func.__name__}")
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            print(f"💾 Cache set: {func.__name__}")
            
            return result
        return wrapper
    return decorator

def get_database_url():
    """Get production database URL"""
    return os.getenv("DATABASE_URL")

def get_openai_key():
    """Get OpenAI API key"""
    return os.getenv("OPENAI_API_KEY")

def get_secret_key():
    """Get secret key for JWT"""
    return os.getenv("SECRET_KEY")

def get_frontend_url():
    """Get frontend URL for CORS"""
    return os.getenv("FRONTEND_URL", "http://localhost:3000")
