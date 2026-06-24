"""Filesystem layer for source code context extraction.

This module provides the ContextManager class, responsible for safely reading
source code files, filtering out binary files, and enforcing size limits
to protect downstream Large Language Model context windows.
"""

from pathlib import Path
from typing import Optional

from src.utils.logger import get_logger

logger = get_logger(__name__)

# Protects the LLM from massive bundled files (e.g., minified JS or huge datasets)
_MAX_FILE_SIZE_BYTES = 100_000


class ContextManager:
    """Manages safe extraction of text from source code files.

    Attributes:
        workspace (Path): The absolute path to the root directory of the codebase.
    """

    def __init__(self, workspace: Path) -> None:
        """Initializes the ContextManager.

        Args:
            workspace (Path): The root directory of the target codebase.
        """
        self.workspace = workspace

    def read_source_file(self, relative_path: str) -> Optional[str]:
        """Safely reads the content of a file relative to the workspace.

        This method includes protections against missing files, massive files,
        and binary files. If a file is deemed unsafe or unreadable, it logs
        the error and returns None rather than crashing the pipeline.

        Args:
            relative_path (str): The path to the file, relative to the workspace.

        Returns:
            Optional[str]: The UTF-8 decoded string content of the file, or
                None if the file is unreadable, binary, or too large.
        """
        abs_path = self.workspace / relative_path

        if not abs_path.exists() or not abs_path.is_file():
            logger.warning(f"File not found or is not a file: {abs_path}")
            return None

        # Size protection
        if abs_path.stat().st_size > _MAX_FILE_SIZE_BYTES:
            logger.warning(f"File too large to include in context: {abs_path}")
            return None

        try:
            # Strict UTF-8 decoding naturally filters out binaries
            return abs_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            logger.warning(f"Skipping binary or non-UTF-8 file: {abs_path}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error reading {abs_path}: {e}")
            return None
