from typing import Any

from openai import AsyncOpenAI

from bot.services.ai.providers.openai import OpenAIProvider

BASE_URL = "https://ai.broryat.tech/v1"
DEFAULT_MODEL = "gemma4"


class BroryatProvider(OpenAIProvider):
    provider_name = "broryat"

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
