"""Domain models for aggregating codebase context.

This module defines the structures used to bundle relevant source code,
tests, and error summaries before passing them to the LLM for analysis.
"""

from pydantic import BaseModel, Field


class ContextFile(BaseModel):
    """Represents a single source or test file included in the context.

    Attributes:
        path (str): The relative path to the file within the workspace.
        content (str): The raw text content of the file.
    """

    path: str = Field(description="The relative path to the file within the workspace.")
    content: str = Field(description="The raw text content of the file.")


class ContextPackage(BaseModel):
    """Bundles all necessary context for the patch generation agent.

    Attributes:
        error_type (str): The primary exception class or error category.
        error_summary (str): A brief explanation of the failure.
        collected_files (list[ContextFile]): The actual file contents to be analyzed.
        relevant_tests (list[str]): Paths to the specific tests that failed.
        related_modules (list[str]): Other imported modules that might be involved.
    """

    error_type: str = Field(
        description="The primary exception class or error category."
    )
    error_summary: str = Field(description="A brief explanation of the failure.")
    collected_files: list[ContextFile] = Field(
        description="List of file contents to be analyzed."
    )
    relevant_tests: list[str] = Field(
        description="Paths to the specific tests that failed."
    )
    related_modules: list[str] = Field(description="Other imported modules involved.")
