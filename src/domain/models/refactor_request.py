from dataclasses import dataclass

from src.domain.models.context_package import ContextPackage
from src.domain.models.patch_recommendation import PatchRecommendation

@dataclass
class RefactorRequest:
    package: ContextPackage
    previous_recommendation: PatchRecommendation
    rejection_reason: str