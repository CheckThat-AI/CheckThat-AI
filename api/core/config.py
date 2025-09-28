import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    title: str = "CheckThat AI - Advanced Claim Normalization & Fact-Checking Platform"
    description: str = "API for the CheckThat AI Platform - https://www.checkthat-ai.com"
    version: str = "1.0.0"
    
    # Environment
    env_type: str = os.getenv("ENV_TYPE", "dev")
    
    # CORS Origins - Configure for public API access
    # Set CORS_ORIGINS="*" for public API or specific domains for restricted access
    cors_origins: str = os.getenv("CORS_ORIGINS", "")
    
    @property
    def allowed_origins(self) -> List[str]:
        if self.cors_origins:
            # Split by comma and strip whitespace
            origins = [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
            # Allow wildcard for public API if explicitly set
            if "*" in origins:
                return ["*"]
            return origins
        
        # Fallback defaults if no env var is set
        if self.env_type == "dev":
            return [
                # Common development ports on localhost
                "http://localhost:3000",   # React, Next.js
                "http://localhost:3001",
                "http://localhost:4000",
                "http://localhost:5000",
                "http://localhost:8000",   # Some dev servers
                "http://localhost:8080",   # Vue, some dev servers
                "http://localhost:5173",   # Vite
                "http://localhost:5174",
                "http://localhost:9000",
                "http://localhost:9001",

                # Common development ports on 127.0.0.1
                "http://127.0.0.1:3000",
                "http://127.0.0.1:3001",
                "http://127.0.0.1:4000",
                "http://127.0.0.1:5000",
                "http://127.0.0.1:8000",
                "http://127.0.0.1:8080",
                "http://127.0.0.1:5173",
                "http://127.0.0.1:5174",
                "http://127.0.0.1:9000",
                "http://127.0.0.1:9001",

                # HTTPS versions (if using SSL in dev)
                "https://localhost:3000",
                "https://localhost:5173",
                "https://127.0.0.1:3000",
                "https://127.0.0.1:5173",

                # File protocol for static file serving from different folders
                "null",  # For requests from file:// protocol

                # Network access (if testing from different machines)
                "http://192.168.1.1"
            ]
        elif self.env_type == "prod":
            # For production public API, allow all origins
            return ["*"]
        else:
            # Default to public access for public API endpoints
            return ["*"]
    
    class Config:
        env_file = ".env"

settings = Settings() 