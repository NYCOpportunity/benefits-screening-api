"""
Child Health Plus eligibility rule (S2R023)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class ChildHealthPlusRule(BaseRule):
    program = "S2R023"
    description = "Child Health Plus - Low-cost health insurance for children"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. At least one person under age 19
        """
        persons = request.person
        
        # Check for child under 19
        has_eligible_child = any(
            p.age < 19
            for p in persons
        )
        
        return has_eligible_child