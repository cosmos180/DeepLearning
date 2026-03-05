import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Personal Assistant Brain"
    API_V1_STR: str = "/api/v1"
    
    # Data Storage
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent
    DATA_DIR: Path = BASE_DIR / "data" / "knowledge_base"
    
    # LLM Settings
    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"  # Default to a efficient model
    
    class Config:
        env_file = ".env"

settings = Settings()

# Ensure data directory exists
os.makedirs(settings.DATA_DIR, exist_ok=True)
