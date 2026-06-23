from pydantic import BaseModel


class ContextFile(BaseModel):
    path: str
    content: str


class ContextPackage(BaseModel):
    error_type: str
    error_summary: str

    collected_files: list[ContextFile]

    relevant_tests: list[str]

    related_modules: list[str]
