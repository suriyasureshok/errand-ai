from typing import Any

from openai import OpenAI

from src.application.config import Config
from src.domain.interfaces.ai_provider import AIProvider


class NvidiaNIMProvider(AIProvider):
    def __init__(self, config: Config) -> None:
        self._config = config
        self._client = OpenAI(
            base_url=config.base_url,
            api_key=config.api_key,
        )

    def run(
        self,
        prompt: str,
        system_prompt: str | None = None,
        response_schema: type | None = None,
    ) -> Any:
        messages: list[dict[str, str]] = []

        if system_prompt is not None:
            messages.append(
                {
                    "role": "system",
                    "content": system_prompt,
                }
            )

        messages.append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        if response_schema is not None:
            completion = self._client.beta.chat.completions.parse(
                model=self._config.model,
                messages=messages,
                response_format=response_schema,
            )
            parsed = completion.choices[0].message.parsed
            if parsed is None:
                raise ValueError("Failed to parse response.")
            return parsed

        completion = self._client.chat.completions.create(
            model=self._config.model,
            messages=messages,
        )
        content = completion.choices[0].message.content
        if content is None:
            raise ValueError("Model returned empty response.")
        return content
