"""
ORCA Configuration Management
Loads settings from environment variables with validation
"""

from typing import List, Optional
from pydantic import field_validator
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
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
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
        """Fix Render's postgres:// to postgresql+asyncpg://"""
        if v and isinstance(v, str) and v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        return v
    
    @field_validator("POSTGIS_URL", mode="before")
    @classmethod
    def default_postgis_url(cls, v: Optional[str], info) -> str:
        """Default POSTGIS_URL to DATABASE_URL if not provided"""
        if v is None:
            db_url = info.data.get("DATABASE_URL", "")
            return db_url
        if v and isinstance(v, str) and v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        return v
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: any) -> List[str]:
        """Support comma-separated strings for CORS origins in Render"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v
    
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
