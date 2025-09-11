from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from .config import settings
from .rate_limiter import rate_limit_middleware

class EndpointSpecificCORSMiddleware(BaseHTTPMiddleware):
    """Custom CORS middleware that applies different origins based on endpoint paths"""
    
    def __init__(self, app, restricted_origins: list, public_origins: list):
        super().__init__(app)
        self.restricted_origins = restricted_origins
        self.public_origins = public_origins
        
        # Common CORS headers
        self.common_headers = [
            "Content-Type", 
            "Authorization", 
            "Accept", 
            "Accept-Language",
            "Accept-Encoding",
            "Cache-Control",
            "Origin",
            "X-Requested-With",
            "X-API-Key",
            "User-Agent",
            "Referer"
        ]
        
        self.expose_headers = [
            "Content-Type", 
            "Content-Length",
            "X-Rate-Limit-Remaining",
            "X-Rate-Limit-Reset",
            "X-Request-ID"
        ]
    
    def get_allowed_origins(self, path: str) -> list:
        """Determine allowed origins based on the request path"""
        # Public API endpoints (completions and models)
        if path.startswith("/v1/"):
            return self.public_origins
        # Restricted endpoints (chat)
        else:
            return self.restricted_origins
    
    def get_allowed_methods(self, path: str) -> list:
        """Determine allowed HTTP methods based on the request path"""
        if path.startswith("/v1/chat/completions"):
            return ["POST", "OPTIONS"]  # Only POST for completions
        elif path.startswith("/v1/models"):
            return ["GET", "OPTIONS"]   # Only GET for models
        elif path.startswith("/chat"):
            return ["POST", "OPTIONS"]  # Only POST for chat
        else:
            return ["GET", "POST", "OPTIONS"]  # Default for other endpoints
    
    def is_origin_allowed(self, origin: str, allowed_origins: list) -> bool:
        """Check if origin is allowed"""
        if "*" in allowed_origins:
            return True
        return origin in allowed_origins
    
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        # Get path from request scope (always available)
        path = request.scope.get("path", "/")
        
        # Get allowed origins and methods for this endpoint
        allowed_origins = self.get_allowed_origins(path)
        allowed_methods = self.get_allowed_methods(path)
        
        # Handle preflight requests
        if request.method == "OPTIONS":
            if origin and not self.is_origin_allowed(origin, allowed_origins):
                return Response(
                    status_code=403,
                    content="CORS policy violation: Origin not allowed",
                    headers={"Access-Control-Allow-Origin": "null"}
                )
            
            # Return preflight response
            response = Response(status_code=200)
            if origin and self.is_origin_allowed(origin, allowed_origins):
                response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Methods"] = ", ".join(allowed_methods)
            response.headers["Access-Control-Allow-Headers"] = ", ".join(self.common_headers)
            response.headers["Access-Control-Expose-Headers"] = ", ".join(self.expose_headers)
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Max-Age"] = "3600"
            return response
        
        # Validate HTTP method for this endpoint
        if request.method not in allowed_methods:
            return Response(
                status_code=405,
                content=f"Method {request.method} not allowed for this endpoint",
                headers={"Allow": ", ".join(allowed_methods)}
            )
        
        # Handle actual requests
        response = await call_next(request)
        
        # Add CORS headers to response
        if origin and self.is_origin_allowed(origin, allowed_origins):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Expose-Headers"] = ", ".join(self.expose_headers)
        
        return response

def setup_middleware(app: FastAPI) -> None:
    """Configure middleware for the FastAPI application"""
    
    # Add rate limiting middleware (CRITICAL for guest mode)
    app.middleware("http")(rate_limit_middleware)
    
    # Configure endpoint-specific CORS
    # Restricted origins for /chat endpoint
    restricted_origins = [
        "https://nikhil-kadapala.github.io",
        "https://www.checkthat-ai.com", 
        "https://checkthat-ai.com"
    ]
    
    # Public origins for /v1/* endpoints (completions and models)
    public_origins = settings.allowed_origins
    
    app.add_middleware(
        EndpointSpecificCORSMiddleware,
        restricted_origins=restricted_origins,
        public_origins=public_origins
    )