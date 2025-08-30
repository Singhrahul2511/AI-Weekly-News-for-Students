# config.py
import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Loads and validates application settings from environment variables."""
    # Application
    FASTAPI_SECRET_KEY: str
    ADMIN_TOKEN: str
    ADMIN_EMAIL: str
    
    # Database
    DATABASE_URL: str = "sqlite:///./newsletter.db"
    
    # Mailchimp
    MAILCHIMP_API_KEY: str
    MAILCHIMP_SERVER_PREFIX: str
    MAILCHIMP_LIST_ID: str
    MAILCHIMP_FROM_NAME: str = "AI Weekly Newsletter"
    MAILCHIMP_REPLY_TO: str
    
    # Gemini
    GEMINI_API_KEY: str
    X_BEARER_TOKEN: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Instantiate settings
settings = Settings()
