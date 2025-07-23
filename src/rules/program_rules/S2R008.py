"""
Head Start early childhood education program eligibility rule (S2R008)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class HeadStart(BaseRule):
    program = "S2R008"
    description = "Head Start (DOE) - Free early childhood education for children aged 3-4"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires NYC residence and any of:
        1. Child aged 3-4 with household income below thresholds based on household size
        2. Household receives Cash Assistance or SSI
        3. Household has foster children
        """
        persons = request.person
        household_size = len(persons)
        
        # Check for child aged 3-4
        has_eligible_child = any(2 < p.age < 5 for p in persons)
        
        # Income thresholds by household size
        income_thresholds = {
            1: 15060,
            2: 20440,
            3: 25820,
            4: 31200,
            5: 36580,
            6: 41960,
            7: 47340,
            8: 52720
        }
        
        # Check income eligibility (only if eligible child present)
        if has_eligible_child and household_size in income_thresholds:
            if request.income_household_total_yearly <= income_thresholds[household_size]:
                return True
        
        # Check Cash Assistance or SSI
        if request.income_household_has_cash_assistance or request.income_household_has_ssi:
            return True
        
        # Check foster children
        if request.foster_children > 0:
            return True
        
        return False