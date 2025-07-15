"""
NYC library card eligibility rule (S2R046)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class LibraryCardRule(BaseRule):
    program = "S2R046"
    description = "NYC Library Card - Free library services and resources"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. NYC residence (assumed for all requests)
        2. At least one person aged 5 or older
        """
        persons = request.person
        
        # Check for person aged 5+
        has_eligible_person = any(p.age >= 5 for p in persons)
        
        return has_eligible_person