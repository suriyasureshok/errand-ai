from pydantic import BaseModel


class FailureAnalysis(BaseModel):
    error_type: str
    summary: str
    relevant_files: list[str]
    relevant_tests: list[str]
    related_modules: list[str]
