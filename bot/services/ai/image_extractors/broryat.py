from typing import Any

from openai import AsyncOpenAI

from bot.services.ai.image_extractors.openai import OpenAIImageExtractor
from bot.services.ai.providers.broryat import BASE_URL, DEFAULT_MODEL


class BroryatImageExtractor(OpenAIImageExtractor):
    def __init__(
        self,
        api_key: str,
        client: Any | None = None,
        model: str = DEFAULT_MODEL,
    ):
        super().__init__(
            api_key=api_key,
            client=client or AsyncOpenAI(api_key=api_key, base_url=BASE_URL),
            model=model,
        )
