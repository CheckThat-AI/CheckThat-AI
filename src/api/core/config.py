import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    title: str = "Claim Extraction and Normalization"
    description: str = "API for the CLEF 2025 CheckThat Lab Task 2"
    version: str = "1.0.0"
    
    # Environment
    env_type: str = os.getenv("ENV_TYPE", "dev")
    
    # CORS Origins
    @property
    def allowed_origins(self) -> List[str]:
        if self.env_type == "dev":
            return ["http://localhost:5173", "http://127.0.0.1:5173"]
        return ["https://nikhil-kadapala.github.io"]
    
    # API Keys (optional defaults)
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    grok_api_key: str = os.getenv("GROK_API_KEY", "")
    together_api_key: str = os.getenv("TOGETHER_API_KEY", "")
    
    class Config:
        env_file = ".env"

settings = Settings() 