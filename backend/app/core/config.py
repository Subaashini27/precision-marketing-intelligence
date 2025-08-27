from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Application
    app_name: str = "Precision Marketing Intelligence Platform"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Database
    database_url: str = "postgresql://user:password@localhost/precision_marketing"
    
    # Security
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Power BI
    powerbi_client_id: Optional[str] = None
    powerbi_client_secret: Optional[str] = None
    powerbi_tenant_id: Optional[str] = None
    powerbi_workspace_id: Optional[str] = None
    powerbi_report_id: Optional[str] = None
    
    # ML Model
    ml_model_path: str = "ml_pipeline/models/"
    prediction_threshold: float = 0.5
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # External APIs
    google_analytics_api_key: Optional[str] = None
    facebook_ads_api_key: Optional[str] = None
    linkedin_ads_api_key: Optional[str] = None
    
    # Email
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # File Storage
    upload_dir: str = "uploads/"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()

# Override with environment variables if they exist
if os.getenv("DATABASE_URL"):
    settings.database_url = os.getenv("DATABASE_URL")
if os.getenv("SECRET_KEY"):
    settings.secret_key = os.getenv("SECRET_KEY")
if os.getenv("POWERBI_CLIENT_ID"):
    settings.powerbi_client_id = os.getenv("POWERBI_CLIENT_ID")
