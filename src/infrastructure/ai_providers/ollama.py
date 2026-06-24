"""Ollama local AI infrastructure provider.

This module implements the AIProvider interface utilizing the OpenAI SDK
pointed at a local Ollama instance.
"""

import json
from typing import Optional, Type, TypeVar, Union

from openai import AsyncOpenAI
from pydantic import BaseModel

from src.application.config import Config
from src.domain.interfaces.ai_provider import AIProvider
from src.utils.logger import get_logger
from src.utils.retry import async_retry

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


class OllamaProvider(AIProvider):
    """Implementation of AIProvider for a local Ollama instance."""

    def __init__(self, config: Config) -> None:
        """Initializes the Ollama Provider.

        Args:
            config (Config): Application configuration containing the base URL (e.g., localhost:11434).
        """
        self._config = config
        self._client = AsyncOpenAI(
            base_url=config.base_url,
            api_key="ollama",  # Ollama requires a dummy API key
        )

    @async_retry(max_retries=3, base_delay=2.0)
    async def run(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_schema: Optional[Type[T]] = None,
    ) -> Union[str, T]:
        """Executes an asynchronous LLM generation request against Ollama.

        Args:
            prompt (str): The main user prompt containing context.
            system_prompt (Optional[str]): Optional system-level instructions.
            response_schema (Optional[Type[T]]): A Pydantic model to enforce JSON output.

        Returns:
            Union[str, T]: The hydrated Pydantic model or a raw string.

        Raises:
            ValueError: If the model returns an empty response or JSON validation fails.
        """
        messages: list[dict[str, str]] = []

        if system_prompt is not None:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        logger.debug(f"Sending request to local Ollama model: {self._config.model}")

        if response_schema is not None:
            schema_json = json.dumps(response_schema.model_json_schema())
            json_instruction = (
                f"\n\nYou MUST return your answer as a single, strictly valid JSON object. "
                f"Use the following JSON schema as the blueprint for your output structure. "
                f"DO NOT echo or return the schema itself. Populate the fields with your actual analysis.\n\n"
                f"SCHEMA TO FOLLOW:\n{schema_json}"
            )

            if not messages or messages[0]["role"] != "system":
                messages.insert(0, {"role": "system", "content": json_instruction})
            else:
                messages[0]["content"] += json_instruction

            completion = await self._client.chat.completions.create(
                model=self._config.model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.1,
            )

            content = completion.choices[0].message.content

            if not content:
                logger.error("Model returned an empty response.")
                raise ValueError("Model returned empty response.")

            try:
                return response_schema.model_validate_json(content)
            except Exception as e:
                logger.error(
                    f"Failed to parse model output into schema. Raw output: {content}"
                )
                raise ValueError(f"JSON validation failed: {e}")

        completion = await self._client.chat.completions.create(
            model=self._config.model,
            messages=messages,
        )

        content = completion.choices[0].message.content
        if content is None:
            raise ValueError("Model returned empty response.")

        return content
