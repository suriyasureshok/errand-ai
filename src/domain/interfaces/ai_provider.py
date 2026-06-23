from abc import ABC, abstractmethod
from typing import TypeVar

T = TypeVar("T")


class AIProvider(ABC):
    """
    Base contract for all LLM providers.

    Supported implementations may include:
    - Ollama
    - Gemini
    - NVIDIA NIM
    - OpenAI
    - LM Studio
    - Any OpenAI-compatible endpoint
    """

    @abstractmethod
    def run(
        self,
        prompt: str,
        system_prompt: str | None = None,
        response_schema: type[T] | None = None,
    ) -> T:
        """
        Execute an LLM request.

        Args:
            prompt:
                Main user prompt.

            system_prompt:
                Optional system instructions.

            response_schema:
                Optional Pydantic model used to validate
                and structure the response.

        Returns:
            Structured or raw model response.
        """
        raise NotImplementedError
