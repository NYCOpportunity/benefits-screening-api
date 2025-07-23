"""
IDNYC municipal ID card eligibility rule (S2R032)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class IDNYC(BaseRule):
    program = "S2R032"
    description = "IDNYC (HRA) - Free municipal ID card for NYC residents"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. NYC residence (assumed for all requests)
        2. At least one person aged 10 or older
        """
        persons = request.person
        
        # Check for person aged 10+
        has_eligible_person = any(
            p.age >= 10
            for p in persons
        )
        
        return has_eligible_person