from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_ENV: str = "development"
    SECRET_KEY: str = "change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/agentops"
    REDIS_URL: str = "redis://localhost:6379"

    ANTHROPIC_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    DEFAULT_MODEL: str = "claude-sonnet-4-6"

    # Self-hosted / local models
    # Ollama: set OLLAMA_BASE_URL to wherever Ollama is running.
    #   Use model IDs like  ollama/qwen2.5:27b  in the UI.
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # vLLM endpoint (OpenAI-compatible).
    #   Use model IDs like  openai/qwen3-27b  in the UI.
    VLLM_API_BASE: str = ""
    VLLM_API_KEY: str = ""

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


settings = Settings()
