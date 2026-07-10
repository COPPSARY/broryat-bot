from bot.config.settings import Settings
from bot.services.ai.base import AIProvider
from bot.services.ai.gemini_provider import GeminiProvider
from bot.services.ai.huggingface_provider import HuggingFaceProvider


def get_ai_provider(settings: Settings) -> AIProvider:
    match settings.ai_provider:
        case "gemini":
            return GeminiProvider(api_key=settings.gemini_api_key, model=settings.llm_model)
        case "huggingface":
            return HuggingFaceProvider(
                api_key=settings.huggingface_api_key,
                model=settings.llm_model,
                base_url=settings.huggingface_base_url,
            )
        case _:
            raise ValueError(f"Unsupported AI provider: {settings.ai_provider}")
