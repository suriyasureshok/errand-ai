"""Git automation utilities for the infrastructure layer.

This package contains the GitClient, which provides automated version control operations,
subprocesses, and checkpointing for the application workspace.
"""

from .git_client import GitClient

__all__ = ["GitClient"]
