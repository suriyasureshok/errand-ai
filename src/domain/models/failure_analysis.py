"""Domain models for representing test failure root causes.

This module defines the schema output by the LogAnalyzer agent after
evaluating a raw test failure dump.
"""

from pydantic import BaseModel, Field


class FailureAnalysis(BaseModel):
    """Structured analysis of why a specific test suite failed.

    Attributes:
        error_type (str): The primary exception or error type (e.g., ImportError, TypeError).
        summary (str): A concise explanation of why the test failed.
        relevant_files (list[str]): List of source file paths related to the failure.
        relevant_tests (list[str]): List of test file paths that failed.
        related_modules (list[str]): List of imported modules or dependencies involved.
    """

    error_type: str = Field(
        description="The primary exception or error type (e.g., ImportError, TypeError)"
    )
    summary: str = Field(description="A concise explanation of why the test failed")
    relevant_files: list[str] = Field(
        description="List of source file paths related to the failure"
    )
    relevant_tests: list[str] = Field(description="List of test file paths that failed")
    related_modules: list[str] = Field(
        description="List of imported modules or dependencies involved"
    )
