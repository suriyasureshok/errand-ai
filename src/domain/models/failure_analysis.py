from pydantic import BaseModel, Field


class FailureAnalysis(BaseModel):
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
