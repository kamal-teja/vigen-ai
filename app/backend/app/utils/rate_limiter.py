"""
Rate limiting utilities for API endpoints
"""
import time
import asyncio
from collections import defaultdict, deque
from functools import wraps
from fastapi import HTTPException, status

class RateLimiter:
    def __init__(self):
        # Store request timestamps per user
        self.requests = defaultdict(deque)
    
    def is_allowed(self, user_id: str, max_requests: int = 10, window_seconds: int = 60) -> bool:
        """
        Check if user is within rate limit
        Args:
            user_id: Unique identifier for the user
            max_requests: Maximum requests allowed in the window
            window_seconds: Time window in seconds
        """
        now = time.time()
        user_requests = self.requests[user_id]
        
        # Remove old requests outside the window
        while user_requests and user_requests[0] < now - window_seconds:
            user_requests.popleft()
        
        # Check if under limit
        if len(user_requests) < max_requests:
            user_requests.append(now)
            return True
        
        return False

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(max_requests: int = 10, window_seconds: int = 60, use_ip_fallback: bool = True):
    """
    Decorator to rate limit API endpoints
    Args:
        max_requests: Maximum requests allowed in the window
        window_seconds: Time window in seconds
        use_ip_fallback: Use client IP if no user found (for auth endpoints)
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extract current_user from kwargs (assuming it's passed as dependency)
            current_user = None
            request = None
            
            # Find current_user and request objects
            for arg in args:
                if hasattr(arg, 'email'):
                    current_user = arg
                elif hasattr(arg, 'client') and hasattr(arg, 'headers'):
                    request = arg
            
            if not current_user:
                for value in kwargs.values():
                    if hasattr(value, 'email'):
                        current_user = value
                        break
                    elif hasattr(value, 'client') and hasattr(value, 'headers'):
                        request = value
            
            # Determine identifier for rate limiting
            identifier = None
            if current_user:
                identifier = current_user.email
            elif use_ip_fallback and request:
                # Use IP address for unauthenticated endpoints
                identifier = request.client.host
            elif use_ip_fallback:
                # Fallback identifier if we can't find IP
                identifier = "anonymous"
            
            if identifier:
                if not rate_limiter.is_allowed(identifier, max_requests, window_seconds):
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Rate limit exceeded. Maximum {max_requests} requests per {window_seconds} seconds."
                    )
            
            return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Extract current_user from kwargs (assuming it's passed as dependency)
            current_user = None
            request = None
            
            # Find current_user and request objects
            for arg in args:
                if hasattr(arg, 'email'):
                    current_user = arg
                elif hasattr(arg, 'client') and hasattr(arg, 'headers'):
                    request = arg
            
            if not current_user:
                for value in kwargs.values():
                    if hasattr(value, 'email'):
                        current_user = value
                        break
                    elif hasattr(value, 'client') and hasattr(value, 'headers'):
                        request = value
            
            # Determine identifier for rate limiting
            identifier = None
            if current_user:
                identifier = current_user.email
            elif use_ip_fallback and request:
                # Use IP address for unauthenticated endpoints
                identifier = request.client.host
            elif use_ip_fallback:
                # Fallback identifier if we can't find IP
                identifier = "anonymous"
            
            if identifier:
                if not rate_limiter.is_allowed(identifier, max_requests, window_seconds):
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail=f"Rate limit exceeded. Maximum {max_requests} requests per {window_seconds} seconds."
                    )
            
            return func(*args, **kwargs)
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator