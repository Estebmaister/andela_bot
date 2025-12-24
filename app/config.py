from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # OpenRouter / LLM Configuration
    OPENROUTER_API_KEY: str = "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"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    MODEL_NAME: str = "gpt-4o-mini"

    # MCP Server Configuration
    MCP_SERVER_URL: str

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # LLM Parameters
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 700


settings = Settings()
