import logging
from typing import Any, Optional

from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for interacting with OpenAI-compatible LLM APIs."""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.OPENROUTER_API_KEY,
            base_url=settings.OPENROUTER_BASE_URL,
        )
        self.model = settings.MODEL_NAME

    async def chat(
        self,
        messages: list[dict[str, str]],
        tools: Optional[list[dict]] = None,
    ) -> Any:
        """Send a chat completion request to the LLM."""
        from openai.types.chat import ChatCompletion

        params: dict[str, Any] = {
            "extra_headers": {
                "HTTP-Referer": "https://github.com/estebmaister/andela_bot",
                "X-Title": "andela_bot"
            },
            "model": self.model,
            "messages": messages,
            "temperature": settings.TEMPERATURE,
            "max_tokens": settings.MAX_TOKENS,
        }

        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"

        response: ChatCompletion = await self.client.chat.completions.create(**params)
        return response

    async def health_check(self) -> bool:
        """Check if LLM service is accessible."""
        try:
            await self.client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://github.com/estebmaister/andela_bot",
                    "X-Title": "andela_bot"
                },
                model=self.model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5,
            )
            return True
        except Exception as e:
            logger.error(f"LLM health check failed: {e}")
            return False


# Global LLM service instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get or create the global LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
