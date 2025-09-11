"""
Robust rate limiting middleware for FastAPI with comprehensive error handling
"""
import time
import logging
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import asyncio

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class RateLimitInfo:
    """Rate limit information for a client"""
    request_count: int
    window_start: float
    last_request: float
    
class RobustRateLimiter:
    """
    Robust rate limiter with comprehensive error handling and logging
    
    Features:
    - Sliding window rate limiting
    - Memory-efficient cleanup
    - Comprehensive logging
    - Error handling and recovery
    - Configurable limits per endpoint
    """
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.clients: Dict[str, RateLimitInfo] = {}
        self.cleanup_threshold = 1000  # Clean up when we have too many entries
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # Clean up every 5 minutes
        
        logger.info(
            f"Rate limiter initialized: {max_requests} requests per "
            f"{window_seconds} seconds"
        )
    
    def _cleanup_old_entries(self) -> None:
        """Clean up old entries to prevent memory bloat"""
        try:
            now = time.time()
            
            # Only cleanup if needed
            if (len(self.clients) < self.cleanup_threshold and 
                now - self.last_cleanup < self.cleanup_interval):
                return
            
            cutoff_time = now - self.window_seconds
            old_count = len(self.clients)
            
            # Remove entries older than the window
            self.clients = {
                ip: info for ip, info in self.clients.items()
                if info.window_start > cutoff_time
            }
            
            removed_count = old_count - len(self.clients)
            if removed_count > 0:
                logger.debug(f"Cleaned up {removed_count} old rate limit entries")
            
            self.last_cleanup = now
            
        except Exception as e:
            logger.error(f"Error during rate limiter cleanup: {e}")
            # Continue operation even if cleanup fails
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request with proper proxy handling"""
        try:
            # Check for X-Forwarded-For header (common with proxies/load balancers)
            forwarded_for = request.headers.get("x-forwarded-for")
            if forwarded_for:
                # Take the first IP in the chain
                client_ip = forwarded_for.split(",")[0].strip()
                logger.debug(f"Using X-Forwarded-For IP: {client_ip}")
                return client_ip
            
            # Check for X-Real-IP header (nginx)
            real_ip = request.headers.get("x-real-ip")
            if real_ip:
                logger.debug(f"Using X-Real-IP: {real_ip}")
                return real_ip.strip()
            
            # Fall back to direct client IP
            if request.client and request.client.host:
                client_ip = request.client.host
                logger.debug(f"Using direct client IP: {client_ip}")
                return client_ip
            
            # Last resort
            logger.warning("Could not determine client IP, using 'unknown'")
            return "unknown"
            
        except Exception as e:
            logger.error(f"Error extracting client IP: {e}")
            return "unknown"
    
    def is_allowed(self, client_ip: str) -> Tuple[bool, Optional[int]]:
        """
        Check if a request is allowed for the given client IP
        
        Returns:
            Tuple[bool, Optional[int]]: (is_allowed, seconds_until_reset)
        """
        try:
            now = time.time()
            
            # Perform cleanup if needed
            self._cleanup_old_entries()
            
            # Get or create client info
            if client_ip not in self.clients:
                self.clients[client_ip] = RateLimitInfo(
                    request_count=1,
                    window_start=now,
                    last_request=now
                )
                logger.debug(f"New client {client_ip}: 1/{self.max_requests} requests")
                return True, None
            
            client_info = self.clients[client_ip]
            
            # Check if we're in a new window
            if now - client_info.window_start > self.window_seconds:
                # Reset the window
                self.clients[client_ip] = RateLimitInfo(
                    request_count=1,
                    window_start=now,
                    last_request=now
                )
                logger.debug(f"Reset window for {client_ip}: 1/{self.max_requests} requests")
                return True, None
            
            # Check if limit exceeded
            if client_info.request_count >= self.max_requests:
                seconds_until_reset = int(
                    self.window_seconds - (now - client_info.window_start)
                ) + 1
                logger.warning(
                    f"Rate limit exceeded for {client_ip}: "
                    f"{client_info.request_count}/{self.max_requests} requests. "
                    f"Reset in {seconds_until_reset}s"
                )
                return False, seconds_until_reset
            
            # Increment counter
            self.clients[client_ip] = RateLimitInfo(
                request_count=client_info.request_count + 1,
                window_start=client_info.window_start,
                last_request=now
            )
            
            logger.debug(
                f"Client {client_ip}: "
                f"{self.clients[client_ip].request_count}/{self.max_requests} requests"
            )
            return True, None
            
        except Exception as e:
            logger.error(f"Error in rate limiter for {client_ip}: {e}")
            # Fail open - allow the request if we can't determine rate limit
            return True, None
    
    def get_rate_limit_headers(self, client_ip: str) -> Dict[str, str]:
        """Get rate limit headers for response"""
        try:
            if client_ip not in self.clients:
                return {
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": str(self.max_requests - 1),
                    "X-RateLimit-Reset": str(int(time.time() + self.window_seconds))
                }
            
            client_info = self.clients[client_ip]
            remaining = max(0, self.max_requests - client_info.request_count)
            reset_time = int(client_info.window_start + self.window_seconds)
            
            return {
                "X-RateLimit-Limit": str(self.max_requests),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(reset_time)
            }
            
        except Exception as e:
            logger.error(f"Error generating rate limit headers: {e}")
            return {}

# Global rate limiter instances
chat_rate_limiter = RobustRateLimiter(max_requests=10, window_seconds=60)
public_api_rate_limiter = RobustRateLimiter(max_requests=10, window_seconds=60)

async def rate_limit_middleware(request: Request, call_next):
    """
    Robust rate limiting middleware with comprehensive error handling
    
    Applies rate limiting to:
    - /chat endpoint: 10 requests per minute
    - /v1/* endpoints: 10 requests per minute  
    - All other POST endpoints: 10 requests per minute
    """
    try:
        path = request.url.path
        method = request.method
        
        # Determine which rate limiter to use
        rate_limiter = None
        endpoint_name = ""
        
        if path.startswith("/v1/"):
            rate_limiter = public_api_rate_limiter
            endpoint_name = "Public API"
        elif path.startswith("/chat"):
            rate_limiter = chat_rate_limiter
            endpoint_name = "Chat"
        elif method in ["POST", "PUT", "DELETE", "PATCH"]:
            # Rate limit other write operations
            rate_limiter = chat_rate_limiter
            endpoint_name = "API"
        
        # Skip rate limiting for read-only operations and health checks
        if rate_limiter is None or path in ["/", "/health", "/docs", "/openapi.json"]:
            response = await call_next(request)
            return response
        
        # Get client IP with proper proxy handling
        client_ip = rate_limiter._get_client_ip(request)
        
        # Check rate limit
        is_allowed, seconds_until_reset = rate_limiter.is_allowed(client_ip)
        
        if not is_allowed:
            # Create comprehensive error response
            retry_after = seconds_until_reset or 60
            error_response = {
                "error": "Rate limit exceeded",
                "message": f"You've exceeded the rate limit for {endpoint_name} endpoints. "
                          f"Please wait {retry_after} seconds before trying again.",
                "details": {
                    "limit": f"{rate_limiter.max_requests} requests per {rate_limiter.window_seconds} seconds",
                    "retry_after": retry_after,
                    "endpoint": path,
                    "client_ip": client_ip
                },
                "help": "This helps us keep the service available for everyone."
            }
            
            headers = {
                "Retry-After": str(retry_after),
                **rate_limiter.get_rate_limit_headers(client_ip)
            }
            
            logger.warning(
                f"Rate limit exceeded for {client_ip} on {endpoint_name} endpoint {path}"
            )
            
            return JSONResponse(
                status_code=429,
                content=error_response,
                headers=headers
            )
        
        # Process the request
        response = await call_next(request)
        
        # Add rate limit headers to successful responses
        rate_limit_headers = rate_limiter.get_rate_limit_headers(client_ip)
        for header, value in rate_limit_headers.items():
            response.headers[header] = value
        
        return response
        
    except Exception as e:
        logger.error(f"Error in rate limiting middleware: {e}")
        # Fail open - continue with the request if rate limiting fails
        response = await call_next(request)
        return response
