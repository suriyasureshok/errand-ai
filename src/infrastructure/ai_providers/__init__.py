"""AI provider implementations for the infrastructure layer.

This package contains concrete wrappers for interacting with local or cloud-based
Large Language Models, conforming to the domain's AIProvider interface.
"""

from .nvidia_nim import NvidiaNIMProvider
from .ollama import OllamaProvider

__all__ = [
    "NvidiaNIMProvider",
    "OllamaProvider",
]
