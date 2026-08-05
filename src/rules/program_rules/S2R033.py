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

    INCOME_THRESHOLDS = {
        1: 3473,
        2: 4542,
        3: 5611,
        4: 6680,
        5: 7749,
        6: 8818,
        7: 9018,
        8: 9218,
    }

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires any of:
        1. Household receives Cash Assistance (any household size)
        2. Household receives SSI (single-member households only)
        3. Total monthly household income at or below size-based thresholds
        """
        household_size = len(request.person)

        if request.income_household_has_cash_assistance:
            return True

        if household_size == 1 and request.income_household_has_ssi:
            return True

        threshold = cls.INCOME_THRESHOLDS.get(household_size)
        if threshold is not None:
            return request.income_household_total_monthly <= threshold

        return False
