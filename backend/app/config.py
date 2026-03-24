from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "AI Blog Studio"
    DEBUG: bool = False
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # Database
    DATABASE_URL: str = "postgresql://postgres:dev@localhost/blogstudio"
    TEST_DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # JWT
    JWT_SECRET_KEY: str = "changeme-super-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Anthropic
    ANTHROPIC_API_KEY: str = "sk-ant-placeholder"
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"

    # Rate limiting
    AI_RATE_LIMIT_REQUESTS: int = 20
    AI_RATE_LIMIT_WINDOW_SECONDS: int = 3600  # 1 hour

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
