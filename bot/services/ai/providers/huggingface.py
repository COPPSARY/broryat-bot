import logging
from collections.abc import Sequence
from typing import Any

from openai import APIStatusError, AsyncOpenAI

from bot.schemas.intent import IntentResult
from bot.services.ai.providers.base import AIProvider, AIProviderError
from bot.services.ai.prompt import DISCLAIMER, build_prompt
from bot.services.ai.response_parsing import parse_ai_response

_BASE_URL = "https://router.huggingface.co/v1"
_MODEL = "meta-llama/Llama-3.1-8B-Instruct"
_ROTATABLE_STATUS_CODES = {401, 402, 403, 429}

logger = logging.getLogger(__name__)


class HuggingFaceProvider(AIProvider):
    provider_name = "huggingface"

    def __init__(
        self,
        api_key: str | None = None,
        client: Any | None = None,
        model: str = _MODEL,
        base_url: str = _BASE_URL,
        api_keys: Sequence[str] | None = None,
    ):
        keys = list(dict.fromkeys(key for key in (api_keys or [api_key]) if key))
        if client is None and not keys:
            raise ValueError("At least one Hugging Face API key is required")

        self._clients = (
            (client,)
            if client is not None
            else tuple(AsyncOpenAI(api_key=key, base_url=base_url) for key in keys)
        )
        self._client = self._clients[0]
        self._client_index = 0
        self._model = model

    async def classify(self, text: str, language: str, vt_context: str | None = None) -> IntentResult:
        prompt = build_prompt(text, language, vt_context)
        last_error = None
        for _ in self._clients:
            index = self._client_index
            try:
                response = await self._clients[index].chat.completions.create(
                    model=self._model,
                    messages=[{"role": "user", "content": prompt}],
                )
                break
            except APIStatusError as exc:
                if exc.status_code not in _ROTATABLE_STATUS_CODES:
                    raise
                last_error = exc
                self._client_index = (index + 1) % len(self._clients)
                logger.warning(
                    "Hugging Face key %d rejected with HTTP %d; trying next key",
                    index + 1,
                    exc.status_code,
                )
        else:
            raise last_error

        reply = response.choices[0].message.content.strip()

        try:
            risk_level, visible_message = parse_ai_response(reply)
        except ValueError as exc:
            raise AIProviderError(
                f"HuggingFace response has no parseable risk level: {exc}. Raw response: {reply!r}"
            ) from exc

        message = f"{visible_message}\n\n{DISCLAIMER[language]}"
        return IntentResult(risk_level=risk_level, message=message, language=language, raw_response=reply)
