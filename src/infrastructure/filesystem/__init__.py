"""Filesystem package for the Errand AI pipeline.

This package isolates all direct OS-level file manipulation. It provides
dedicated managers for reading context, saving logs, and safely applying
code modifications.
"""

from .context_manager import ContextManager
from .log_manager import LogManager
from .patch_manager import PatchManager

__all__ = [
    "ContextManager",
    "LogManager",
    "PatchManager",
]
