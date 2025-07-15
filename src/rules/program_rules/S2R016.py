"""
Pre-K for All eligibility rule (S2R016)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class PreKForAllRule(BaseRule):
    program = "S2R016"
    description = "Pre-K for All - Free pre-kindergarten for 4-year-olds"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. NYC residence (assumed for all requests)
        2. At least one child aged 3 or 4
        """
        persons = request.person
        
        # Check for child aged 3-4
        has_eligible_child = any(
            3 <= p.age < 5
            for p in persons
        )
        
        return has_eligible_child