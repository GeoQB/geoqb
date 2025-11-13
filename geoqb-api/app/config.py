"""Application configuration management."""
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "GeoQB API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False

    # API
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str
    REDIS_CACHE_TTL: int = 3600

    # Email
    SENDGRID_API_KEY: str = ""
    FROM_EMAIL: str = "noreply@geoqb.io"
    SUPPORT_EMAIL: str = "support@geoqb.io"

    # TigerGraph
    TIGERGRAPH_HOST: str
    TIGERGRAPH_USERNAME: str
    TIGERGRAPH_PASSWORD: str
    TIGERGRAPH_GRAPHNAME: str = "GeoQB"

    # Stripe
    STRIPE_SECRET_KEY: str = ""
    STRIPE_PUBLISHABLE_KEY: str = ""
    STRIPE_WEBHOOK_SECRET: str = ""

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Usage Limits
    FREE_PLAN_LAYER_LIMIT: int = 5
    FREE_PLAN_QUERY_LIMIT: int = 100
    PROFESSIONAL_PLAN_LAYER_LIMIT: int = 50
    PROFESSIONAL_PLAN_QUERY_LIMIT: int = 10000
    BUSINESS_PLAN_LAYER_LIMIT: int = 200
    BUSINESS_PLAN_QUERY_LIMIT: int = 100000

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
