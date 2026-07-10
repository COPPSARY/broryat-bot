from typing import Any

from openai import AsyncOpenAI

from bot.schemas.intent import IntentResult
from bot.services.ai.base import AIProvider, AIProviderError
from bot.services.ai.prompt import DISCLAIMER, build_prompt
from bot.services.ai.response_parsing import parse_ai_response

_BASE_URL = "https://router.huggingface.co/v1"
_MODEL = "meta-llama/Llama-3.1-8B-Instruct"


class HuggingFaceProvider(AIProvider):
    provider_name = "huggingface"

    def __init__(
        self,
        api_key: str,
        client: Any | None = None,
        model: str = _MODEL,
        base_url: str = _BASE_URL,
    ):
        self._client = client or AsyncOpenAI(api_key=api_key, base_url=base_url)
        self._model = model

    async def classify(self, text: str, language: str, vt_context: str | None = None) -> IntentResult:
        prompt = build_prompt(text, language, vt_context)
        response = await self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
        )
        reply = response.choices[0].message.content.strip()

        try:
            risk_level, visible_message = parse_ai_response(reply)
        except ValueError as exc:
            raise AIProviderError(
                f"HuggingFace response has no parseable risk level: {exc}. Raw response: {reply!r}"
            ) from exc

        message = f"{visible_message}\n\n{DISCLAIMER[language]}"
        return IntentResult(risk_level=risk_level, message=message, language=language, raw_response=reply)
