"""
Summer Youth Employment Program eligibility rule (S2R030)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class SummerYouthEmploymentProgram(BaseRule):
    program = "S2R030"
    description = "Summer Youth Employment Program (SYEP) (DYCD) - Summer employment opportunities for youth"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. NYC residence (assumed for all requests)
        2. At least one person aged 14-24
        """
        persons = request.person
        
        # Check for youth aged 14-24
        has_eligible_youth = any(
            14 <= p.age <= 24
            for p in persons
        )
        
        return has_eligible_youth