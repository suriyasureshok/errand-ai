import json
from typing import Any, TypeVar

from openai import AsyncOpenAI
from pydantic import BaseModel

from src.application import Config
from src.domain.interfaces import AIProvider
from src.utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


class OllamaProvider(AIProvider):
    def __init__(self, config: Config) -> None:
        self._config = config
        
        # Instantiate the asynchronous OpenAI client
        self._client = AsyncOpenAI(
            base_url=config.base_url,
            api_key=config.api_key,
        )

    async def run(
        self,
        prompt: str,
        system_prompt: str | None = None,
        response_schema: type[T] | None = None,
    ) -> T | str:
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

        logger.debug(f"Sending request to model: {self._config.model}")

        if response_schema is not None:
            # 1. Inject the Pydantic schema into the system prompt so the model knows the exact shape
            schema_json = json.dumps(response_schema.model_json_schema())
            json_instruction = f"\n\nYou MUST return strictly valid JSON matching this schema: {schema_json}"
            
            if not messages or messages[0]["role"] != "system":
                messages.insert(0, {"role": "system", "content": json_instruction})
            else:
                messages[0]["content"] += json_instruction

            # 2. Call the standard API endpoint (supported by NVIDIA, Ollama, LM Studio, etc.)
            completion = await self._client.chat.completions.create(
                model=self._config.model,
                messages=messages,
                response_format={"type": "json_object"},  # Force JSON mode
                temperature=0.1,  # Keep it deterministic
            )
            
            content = completion.choices[0].message.content
            
            if not content:
                logger.error("Model returned an empty response.")
                raise ValueError("Model returned empty response.")
                
            # 3. Manually parse and validate the JSON string into the Pydantic model
            try:
                parsed = response_schema.model_validate_json(content)
                return parsed
            except Exception as e:
                logger.error(f"Failed to parse model output into schema. Raw output: {content}")
                raise ValueError(f"JSON validation failed: {e}")

        # If no schema is provided, just return the raw text
        completion = await self._client.chat.completions.create(
            model=self._config.model,
            messages=messages,
        )
        content = completion.choices[0].message.content
        
        if content is None:
            raise ValueError("Model returned empty response.")
            
        return content