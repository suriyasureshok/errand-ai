from pydantic import BaseModel, Field, field_validator

class SearchReplacePatch(BaseModel):
    file_path: str = Field(description="The exact relative path to the file.")
    search_block: str = Field(description="The exact block of code to be replaced. Must match the file byte-for-byte, including indentation.")
    replace_block: str = Field(description="The new block of code to insert in its place.")

class PatchRecommendation(BaseModel):
    root_cause: str = Field(description="Detailed explanation of why the failure occurred.")
    proposed_solution: str = Field(description="Explanation of the code modifications.")
    patches: list[SearchReplacePatch] = Field(description="List of exact search/replace blocks to apply to the files.")
    unified_diff: str = Field(description="A visual unified diff patch for the human reviewer. Must be a single string.")

    @field_validator("unified_diff", mode="before")
    @classmethod
    def assemble_diff(cls, value: str | list[str]) -> str:
        """Fixes LLM arrays into proper strings."""
        if isinstance(value, list):
            return "\n".join(value)
        return value