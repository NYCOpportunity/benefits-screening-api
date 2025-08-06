"""
New York State Unemployment Insurance eligibility rule (S2R021)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class NewYorkStateUnemploymentInsurance(BaseRule):
    program = "S2R021"
    description = "New York State Unemployment Insurance (NYS Department of Labor) - Financial assistance for those who lost their job"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. At least one person who is unemployed
        2. That person worked in the last 18 months
        """
        persons = request.person
        
        # Check for unemployed person who worked in last 18 months
        has_eligible_unemployed = any(
            p.unemployed and p.unemployed_worked_last_18_months
            for p in persons
        )
        
        return has_eligible_unemployed