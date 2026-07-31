from bot.config.settings import Settings
from bot.services.ai.image_extractors.anthropic import AnthropicImageExtractor
from bot.services.ai.image_extractors.base import ImageExtractor
from bot.services.ai.image_extractors.gemini import GeminiImageExtractor
from bot.services.ai.image_extractors.huggingface import HuggingFaceImageExtractor
from bot.services.ai.image_extractors.openai import OpenAIImageExtractor


def get_image_extractor(settings: Settings) -> ImageExtractor:
    match settings.ai_provider:
        case "gemini":
            return GeminiImageExtractor(api_key=settings.gemini_api_key, model=settings.llm_model)
        case "openai":
            return OpenAIImageExtractor(api_key=settings.openai_api_key, model=settings.llm_model)
        case "anthropic":
            return AnthropicImageExtractor(api_key=settings.anthropic_api_key, model=settings.llm_model)
        case "huggingface":
            return HuggingFaceImageExtractor(api_key=settings.huggingface_api_key, model=settings.llm_model)
        case _:
            raise ValueError(f"Unsupported AI provider: {settings.ai_provider}")
