from pydantic import BaseModel


class PatchRecommendation(BaseModel):
    root_cause: str

    proposed_solution: str

    unified_diff: str
