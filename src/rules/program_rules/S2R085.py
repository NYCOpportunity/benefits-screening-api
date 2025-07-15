"""
NYC program for 3-year-olds eligibility rule (S2R085)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class ThreeYearOldProgramRule(BaseRule):
    program = "S2R085"
    description = "NYC program for households with 3-year-old children"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. Household is in NYC
        2. At least one person is exactly 3 years old
        """
        persons = request.person
        
        # Check if at least one person is exactly 3 years old
        has_three_year_old = any(p.age == 3 for p in persons)
        
        return has_three_year_old