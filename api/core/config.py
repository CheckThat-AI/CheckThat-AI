import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    title: str = "CheckThat AI - Advanced Claim Normalization & Fact-Checking Platform"
    description: str = "API for the CheckThat AI Platform"
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
            return ["http://localhost:5173", "http://127.0.0.1:5173"]
        elif self.env_type == "prod":
            # For production public API, allow all origins
            return ["*"]
        else:
            # Default to public access for public API endpoints
            return ["*"]
    
    class Config:
        env_file = ".env"

settings = Settings() 