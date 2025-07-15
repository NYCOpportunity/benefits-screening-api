"""
Adult education program eligibility rule (S2R026)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class AdultEducationRule(BaseRule):
    program = "S2R026"
    description = "Adult Education - Educational programs for adults"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. At least one person aged 18 or older
        """
        persons = request.person
        
        # Check for adult (18+)
        has_adult = any(p.age >= 18 for p in persons)
        
        return has_adult