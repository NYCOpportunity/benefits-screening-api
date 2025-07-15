"""
Universal NYC benefit information rule (S2R056)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class UniversalBenefitInfoRule(BaseRule):
    program = "S2R056"
    description = "NYC Benefit Information - General information about available benefits"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        All households are eligible for benefit information
        """
        return True