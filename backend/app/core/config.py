"""
core/config.py — Centralized settings management.
All configuration comes from .env file — never hardcoded.
"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # App
    APP_NAME: str = "AI Data Analyst Pro"
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = Field(default="change-this-secret-key-in-production")

    # Database
    DATABASE_URL: str = Field(default="postgresql+asyncpg://postgres:postgres@localhost:5432/ai_analyst_db")

    # AI
    GROQ_API_KEY: str = Field(default="")
    GROQ_MODEL: str = Field(default="llama-3.3-70b-versatile")
    LLM_TIMEOUT: int = 30
    LLM_MAX_RETRIES: int = 2

    # JWT
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # Files
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: set = {".csv", ".xlsx", ".xls", ".json", ".parquet", ".pdf", ".txt"}

    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    RESEND_API_KEY: str = ""
    FROM_EMAIL: str = "onboarding@resend.dev"
    


    # Frontend
    FRONTEND_URL: str = "https://insight-flow-chi-smoky.vercel.app"

        # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_BUCKET: str = "uploads"

    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    @property
    def STORAGE_DIR(self): return os.path.join(self.BASE_DIR, "storage")
    @property
    def UPLOAD_DIR(self): return os.path.join(self.STORAGE_DIR, "uploads")
    @property
    def REPORT_DIR(self): return os.path.join(self.STORAGE_DIR, "reports")
    @property
    def CHART_DIR(self): return os.path.join(self.STORAGE_DIR, "charts")

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    s = Settings()
    for folder in [s.STORAGE_DIR, s.UPLOAD_DIR, s.REPORT_DIR, s.CHART_DIR]:
        os.makedirs(folder, exist_ok=True)
    return s


settings = get_settings()
