from abc import ABC, abstractmethod

from bot.schemas.intent import IntentResult


class AIProviderError(Exception):
    pass


class AIProvider(ABC):
    provider_name: str

    @abstractmethod
    async def classify(self, text: str, language: str, vt_context: str | None = None) -> IntentResult: ...
