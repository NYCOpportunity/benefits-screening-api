"""
Community Food Connection eligibility rule (S2R056)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class CommunityFoodConnection(BaseRule):
    program = "S2R056"
    description = "Community Food Connection (CFC) (HRA) - Food assistance and community resources"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        All households are eligible for benefit information
        """
        return True