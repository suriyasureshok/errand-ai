"""Utility package for the Errand AI pipeline.

This package exposes the core, stateless utility functions used across
the entire application, including logging factories, asynchronous retry
resilience, string manipulation for LLM outputs, and strict UTC timestamps.
"""

from .diff import normalize_line_endings, sanitize_patch_block, strip_markdown_blocks
from .logger import get_logger, setup_root_logger
from .retry import async_retry
from .timestamps import (
    get_current_utc_iso,
    get_filesystem_safe_timestamp,
    parse_iso_utc,
)

# Explicitly define the public API of the utils package.
# This prevents tools from importing private helper functions if they exist,
# and makes wildcard imports (which should generally be avoided) predictable.
__all__ = [
    "async_retry",
    "get_current_utc_iso",
    "get_filesystem_safe_timestamp",
    "get_logger",
    "normalize_line_endings",
    "parse_iso_utc",
    "sanitize_patch_block",
    "setup_root_logger",
    "strip_markdown_blocks",
]
