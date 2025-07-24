"""
Cooling Assistance Benefit eligibility rule (S2R033)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class CoolingAssistanceBenefit(BaseRule):
    program = "S2R033"
    description = "Cooling Assistance Benefit (HRA) - Help with cooling costs for vulnerable households"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. NYC residence (assumed for all requests)
        2. At least one person who is:
           - Age 6 or under
           - Age 60 or over
           - Disabled
           - Blind
        3. Either:
           - Household receives Cash Assistance, OR
           - Single-person household receives SSI, OR
           - Household monthly income below thresholds based on household size
        """
        persons = request.person
        household_size = len(persons)
        
        # Check for vulnerable person
        has_vulnerable_person = any(
            p.age <= 6 or p.age >= 60 or p.disabled or p.blind
            for p in persons
        )
        
        if not has_vulnerable_person:
            return False
        
        # Check Cash Assistance
        if request.income_household_has_cash_assistance:
            return True
        
        # Check single-person household with SSI
        if household_size == 1 and request.income_household_has_ssi:
            return True
        
        # Income thresholds by household size
        income_thresholds = {
            1: 3035,
            2: 3970,
            3: 4904,
            4: 5838,
            5: 6772,
            6: 7706,
            7: 7881,
            8: 8056
        }
        
        # Check income eligibility
        if household_size in income_thresholds:
            if request.income_household_total_monthly <= income_thresholds[household_size]:
                return True
        
        return False