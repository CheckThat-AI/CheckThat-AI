"""
Simple rate limiting middleware for FastAPI
"""
import time
from typing import Dict, Tuple
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import asyncio

class SimpleRateLimiter:
    def __init__(self):
        # Store: {ip_address: (request_count, window_start_time)}
        self.requests: Dict[str, Tuple[int, float]] = {}
        # Conservative limits for free tier API usage
        self.max_requests = 10  # requests per window (much more conservative)
        self.window_seconds = 60  # 1 minute window
        
    def is_allowed(self, client_ip: str) -> bool:
        now = time.time()
        
        # Clean old entries (simple cleanup)
        if len(self.requests) > 1000:  # Prevent memory bloat
            cutoff = now - self.window_seconds
            self.requests = {
                ip: (count, start_time) 
                for ip, (count, start_time) in self.requests.items() 
                if start_time > cutoff
            }
        
        # Get current window data
        if client_ip not in self.requests:
            self.requests[client_ip] = (1, now)
            return True
            
        count, window_start = self.requests[client_ip]
        
        # Check if we're in a new window
        if now - window_start > self.window_seconds:
            self.requests[client_ip] = (1, now)
            return True
            
        # Check if limit exceeded
        if count >= self.max_requests:
            return False
            
        # Increment counter
        self.requests[client_ip] = (count + 1, window_start)
        return True

# Global rate limiter instance
rate_limiter = SimpleRateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    
    # Get client IP (handle proxies)
    client_ip = request.headers.get("x-forwarded-for")
    if client_ip:
        client_ip = client_ip.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "unknown"
    
    # Check rate limit for POST requests to sensitive endpoints
    if request.method == "POST" and request.url.path in ["/chat"]:
        if not rate_limiter.is_allowed(client_ip):
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded", 
                    "message": "You've made too many requests. Please wait 1 minute before trying again. This helps us keep the service available for everyone.",
                    "retry_after": 60,
                    "limit": "10 requests per minute"
                },
                headers={"Retry-After": "60"}
            )
    
    response = await call_next(request)
    return response
