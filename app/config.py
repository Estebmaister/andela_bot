from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # OpenRouter / LLM Configuration
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    MODEL_NAME: str = "openai/gpt-4o-mini"

    # MCP Server Configuration
    MCP_SERVER_URL: str = "https://vipfapwm3x.us-east-1.awsapprunner.com/mcp"

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # LLM Parameters
    TEMPERATURE: float = 0.7
    MAX_TOKENS: int = 700


settings = Settings()
