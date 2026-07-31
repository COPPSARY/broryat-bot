from bot.config.settings import Settings
from bot.services.ai.providers.anthropic import AnthropicProvider
from bot.services.ai.providers.base import AIProvider
from bot.services.ai.providers.broryat import BroryatProvider
from bot.services.ai.providers.gemini import GeminiProvider
from bot.services.ai.providers.huggingface import HuggingFaceProvider
from bot.services.ai.providers.openai import OpenAIProvider


def get_ai_provider(settings: Settings) -> AIProvider:
    match settings.ai_provider:
        case "gemini":
            return GeminiProvider(api_key=settings.gemini_api_key, model=settings.llm_model)
        case "openai":
            return OpenAIProvider(api_key=settings.openai_api_key, model=settings.llm_model)
        case "anthropic":
            return AnthropicProvider(api_key=settings.anthropic_api_key, model=settings.llm_model)
        case "huggingface":
            return HuggingFaceProvider(
                api_keys=settings.huggingface_api_keys,
                model=settings.llm_model,
            )
        case "broryat":
            return BroryatProvider(
                api_key=settings.broryat_api_key,
                model=settings.llm_model,
            )
        case _:
            raise ValueError(f"Unsupported AI provider: {settings.ai_provider}")
