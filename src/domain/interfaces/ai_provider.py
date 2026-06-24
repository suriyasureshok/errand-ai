"""Interface definition for Large Language Model (LLM) providers.

This module provides the contract for AI text generation, ensuring that
the pipeline can hot-swap between providers (e.g., Ollama, OpenAI, NVIDIA)
seamlessly.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Type, TypeVar, Union

from pydantic import BaseModel

# T must be a Pydantic BaseModel when strict schema validation is requested
T = TypeVar("T", bound=BaseModel)


class AIProvider(ABC):
    """Base contract for all LLM inference providers.

    Supported implementations may interface with local models (Ollama, LM Studio)
    or cloud APIs (Gemini, OpenAI, NVIDIA NIM).
    """

    @abstractmethod
    async def run(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        response_schema: Optional[Type[T]] = None,
    ) -> Union[str, T]:
        """Executes an asynchronous LLM generation request.

        Args:
            prompt (str): The main user prompt containing context, logs, and
                instructional data.
            system_prompt (Optional[str]): Optional system-level instructions
                for role-playing, formatting, or strict constraints.
            response_schema (Optional[Type[T]]): A Pydantic model class. If
                provided, the provider must force the LLM to output valid JSON
                that matches this schema, and return the hydrated model.

        Returns:
            Union[str, T]: The instantiated Pydantic model containing the
                structured response if `response_schema` was provided,
                otherwise a raw generated string.

        Raises:
            NotImplementedError: If the subclass does not implement this method.
        """
        raise NotImplementedError
