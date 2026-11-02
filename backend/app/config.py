import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_name: str = "NitiSetu API"
    port: int = 8000
    frontend_origin: str = "http://localhost:5173"

    # Supabase PostgreSQL Connection
    database_url: Optional[str] = None

    # Supabase API & Storage
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    supabase_service_role_key: Optional[str] = None
    supabase_storage_bucket: str = "nitisetu-user-documents"

    # Google Gemini AI Settings
    gemini_api_key: Optional[str] = None
    gemini_generation_model: str = "gemini-3.5-flash"
    gemini_judge_model: str = "gemini-3.1-flash-lite"
    gemini_embedding_model: str = "text-embedding-004"
    gemini_embedding_dimensions: int = 768

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
