"""
Home Energy Assistance Program eligibility rule (S2R019)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class HomeEnergyAssistanceProgram(BaseRule):
    program = "S2R019"
    description = "Home Energy Assistance Program (HEAP) (HRA) - Help with heating costs for vulnerable households"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        Either:
           - Household receives Cash Assistance (any household size), OR
           - Household receives SSI (single-member households only), OR
           - Adults' total monthly income below thresholds based on household size
        """
        persons = request.person
        household_size = len(persons)
        
        # Check SSI for single-member households
        if household_size == 1 and request.income_household_has_ssi:
            return True
        
        # Check Cash Assistance (any household size)
        if request.income_household_has_cash_assistance:
            return True
        
        # Income thresholds by household size
        income_thresholds = {
            1: 3473,
            2: 4542,
            3: 5611,
            4: 6680,
            5: 7749,
            6: 8818,
            7: 9018,
            8: 9218
        }
        
        # Check income eligibility
        if household_size in income_thresholds:
            if request.income_household_total_monthly <= income_thresholds[household_size]:
                return True
        
        return False