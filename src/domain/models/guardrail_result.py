from dataclasses import dataclass
from typing import Optional

from src.domain.models.patch_recommendation import PatchRecommendation

@dataclass
class GuardrailResult:
    passed: bool
    recommendation: PatchRecommendation
    reason: Optional[str] = None