from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    PROJECT_NAME: str = "Nano Workshop Agent"
    VERSION: str = "0.1.0"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DATABASE_URL: str = "postgresql+asyncpg://nwa:nwa_secret@localhost:5432/nano_workshop"
    REDIS_URL: str = "redis://localhost:6379/0"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "nano-workshop"
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # LLM defaults (can be overridden per-project)
    LLM_PROVIDER: str = "mock"  # mock | anthropic | zhipu
    ANTHROPIC_API_KEY: str | None = None
    ZHIPU_API_KEY: str | None = None
    LLM_MODEL: str = "claude-sonnet-4-6"
    LLM_MAX_TOKENS: int = 4096


settings = Settings()
