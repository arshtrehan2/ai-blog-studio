from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    # Database
    DATABASE_URL: str = "postgresql://postgres:dev@localhost:5432/blogstudio"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Anthropic
    ANTHROPIC_API_KEY: str = ""

    # CORS — comma-separated origins
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    # AI Rate Limiting
    AI_RATE_LIMIT_REQUESTS: int = 20
    AI_RATE_LIMIT_WINDOW_SECONDS: int = 3600  # 1 hour

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]


settings = Settings()
