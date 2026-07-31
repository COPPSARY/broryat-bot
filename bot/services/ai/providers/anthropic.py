from typing import Any

from anthropic import AsyncAnthropic

from bot.schemas.intent import IntentResult
from bot.services.ai.providers.base import AIProvider, AIProviderError
from bot.services.ai.prompt import DISCLAIMER, build_prompt
from bot.services.ai.response_parsing import parse_ai_response

_MODEL = "claude-3-5-haiku-latest"
_MAX_TOKENS = 1024


class AnthropicProvider(AIProvider):
    provider_name = "anthropic"

    def __init__(self, api_key: str, client: Any | None = None, model: str = _MODEL):
        self._client = client or AsyncAnthropic(api_key=api_key)
        self._model = model

    async def classify(self, text: str, language: str, vt_context: str | None = None) -> IntentResult:
        prompt = build_prompt(text, language, vt_context)
        response = await self._client.messages.create(
            model=self._model,
            max_tokens=_MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
        reply = response.content[0].text.strip()

        try:
            risk_level, visible_message = parse_ai_response(reply)
        except ValueError as exc:
            raise AIProviderError(
                f"Anthropic response has no parseable risk level: {exc}. Raw response: {reply!r}"
            ) from exc

        message = f"{visible_message}\n\n{DISCLAIMER[language]}"
        return IntentResult(risk_level=risk_level, message=message, language=language, raw_response=reply)
