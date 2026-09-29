"""
ORCA Configuration Management
Loads settings from environment variables with validation
"""

from typing import List, Optional
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )
    
    # Application
    APP_ENV: str = "development"
    APP_SECRET_KEY: str
    JWT_SECRET_KEY: str
    
    # Database
    DATABASE_URL: str
    POSTGIS_URL: Optional[str] = None
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Object Storage (optional — only needed for provenance capture)
    MINIO_ENDPOINT: str = "http://localhost:9000"
    MINIO_ACCESS_KEY: Optional[str] = None
    MINIO_SECRET_KEY: Optional[str] = None
    MINIO_BUCKET_RAW: str = "orca-raw"
    MINIO_BUCKET_PROCESSED: str = "orca-processed"
    
    # LLM Provider
    GROQ_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    LLM_PROVIDER: str = "groq"
    LLM_MODEL: str = "mixtral-8x7b-32768"
    
    # INCOIS Services
    INCOIS_API_KEY: Optional[str] = None
    INCOIS_USERNAME: Optional[str] = None
    INCOIS_PASSWORD: Optional[str] = None
    INCOIS_ERDDAP_BASE: str = "https://erddap.incois.gov.in/erddap/"
    
    # IMD API
    IMD_API_KEY: Optional[str] = None
    IMD_USERNAME: Optional[str] = None
    IMD_PASSWORD: Optional[str] = None
    IMD_API_BASE: str = "https://api.imd.gov.in/public/"
    
    # Copernicus Marine
    COPERNICUSMARINE_SERVICE_USERNAME: Optional[str] = None
    COPERNICUSMARINE_SERVICE_PASSWORD: Optional[str] = None
    
    # MOSDAC
    MOSDAC_USERNAME: Optional[str] = None
    MOSDAC_PASSWORD: Optional[str] = None
    MOSDAC_API_BASE: str = "https://www.mosdac.gov.in/"
    
    # Global Fishing Watch
    GFW_API_TOKEN: Optional[str] = None
    GFW_API_BASE: str = "https://gateway.api.globalfishingwatch.org/"
    
    # Protected Planet / WDPA
    PROTECTED_PLANET_API_TOKEN: Optional[str] = None
    PROTECTED_PLANET_API_BASE: str = "https://api.protectedplanet.net/"
    
    # OBIS
    OBIS_API_KEY: Optional[str] = None
    OBIS_API_BASE: str = "https://api.obis.org/"
    
    # ISRO
    ISRO_API_KEY: Optional[str] = None
    ISRO_BASE: str = "https://www.isro.gov.in/"
    
    # Open-Meteo (supplementary)
    OPEN_METEO_BASE: str = "https://open-meteo.com/"
    
    # Map Provider
    MAPBOX_ACCESS_TOKEN: Optional[str] = None
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    
    # CORS — stored as a plain string to avoid pydantic-settings JSON parse errors;
    # parsed into a list by the model_validator below.
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    
    # Security
    SECRET_MANAGER: str = "env"  # env|vault|aws|gcp
    
    # Performance
    MAX_WORKERS: int = 4
    REQUEST_TIMEOUT: int = 30
    SOURCE_TIMEOUT: int = 10
    WARNING_TIMEOUT: int = 5
    
    # Freshness Policies (seconds)
    FRESHNESS_CRITICAL: int = 300  # 5 minutes
    FRESHNESS_HIGH: int = 900  # 15 minutes
    FRESHNESS_MEDIUM: int = 3600  # 1 hour
    FRESHNESS_LOW: int = 86400  # 24 hours
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def fix_database_url(cls, v: str) -> str:
        """Fix Render's postgres:// or postgresql:// to postgresql+asyncpg://"""
        if not v or not isinstance(v, str):
            return v
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        if v.startswith("postgresql+psycopg2://"):
            return v.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
        return v
    
    @field_validator("POSTGIS_URL", mode="before")
    @classmethod
    def default_postgis_url(cls, v: Optional[str], info) -> str:
        """Default POSTGIS_URL to DATABASE_URL if not provided and fix asyncpg"""
        if v is None:
            # Info.data.get("DATABASE_URL") already ran through its validator
            # if order is preserved, but we should just in case apply the logic
            db_url = info.data.get("DATABASE_URL", "")
            if db_url and isinstance(db_url, str):
                if db_url.startswith("postgres://"):
                    db_url = db_url.replace("postgres://", "postgresql+asyncpg://", 1)
                elif db_url.startswith("postgresql://"):
                    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
                elif db_url.startswith("postgresql+psycopg2://"):
                    db_url = db_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
            return db_url
        if v and isinstance(v, str):
            if v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql+asyncpg://", 1)
            if v.startswith("postgresql://"):
                return v.replace("postgresql://", "postgresql+asyncpg://", 1)
            if v.startswith("postgresql+psycopg2://"):
                return v.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
        return v
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS string into a list of origin URLs."""
        raw = self.CORS_ORIGINS
        if isinstance(raw, str):
            # Support JSON array format or comma-separated
            if raw.startswith("["):
                import json
                try:
                    return json.loads(raw)
                except (json.JSONDecodeError, ValueError):
                    pass
            return [o.strip() for o in raw.split(",") if o.strip()]
        return list(raw) if raw else []
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.APP_ENV == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.APP_ENV == "production"


# Global settings instance
settings = Settings()

