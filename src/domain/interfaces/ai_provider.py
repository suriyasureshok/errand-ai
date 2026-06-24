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
    - Any OpenAI-compatible endpoint
    """

    @abstractmethod
    async def run(
        self,
        prompt: str,
        system_prompt: str | None = None,
        response_schema: type[T] | None = None,
    ) -> T:
        """
        Execute an asynchronous LLM request.

        Args:
            prompt:
                Main user prompt containing context and instructions.

            system_prompt:
                Optional system instructions for role-playing or constraints.

            response_schema:
                Optional Pydantic model used to validate and force
                structured JSON output from the model.

        Returns:
            The instantiated Pydantic model containing the structured response,
            or a raw string if no schema is provided.
        """
        raise NotImplementedError
