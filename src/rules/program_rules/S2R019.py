"""
Heating assistance program eligibility rule (S2R019)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class HeatingAssistanceRule(BaseRule):
    program = "S2R019"
    description = "Heating Assistance - Help with heating costs for vulnerable households"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. At least one person who is:
           - Age 6 or under
           - Age 60 or over
           - Disabled
           - Blind
        2. Either:
           - Household receives Cash Assistance, OR
           - Adults' total monthly income below thresholds based on household size
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
        
        # Income thresholds by household size
        income_thresholds = {
            1: 3322,
            2: 4345,
            3: 5367,
            4: 6390,
            5: 7412,
            6: 8434,
            7: 8626,
            8: 8818
        }
        
        # Check income eligibility
        if household_size in income_thresholds:
            if request.income_adults_total_monthly <= income_thresholds[household_size]:
                return True
        
        return False