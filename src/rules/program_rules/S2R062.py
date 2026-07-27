"""
Summer EBT eligibility rule (S2R062)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule
from src.models.enums import IncomeType


@register_rule
class SummerEBT(BaseRule):
    program = "S2R062"
    description = "Summer EBT - Food benefits for eligible school-age children"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires at least one child aged 6-16 and either:
        1. Medicaid, disability-related Medicaid, or Cash Assistance, or
        2. Household monthly income below thresholds based on household size
        """
        persons = request.person
        household_size = len(persons)

        has_eligible_child = any(6 <= p.age <= 16 for p in persons)
        if not has_eligible_child:
            return False

        if cls._has_categorical_eligibility(persons):
            return True

        income_thresholds = {
            1: 2413,
            2: 3261,
            3: 4109,
            4: 4957,
            5: 5805,
            6: 6653,
            7: 7501,
            8: 8349,
        }

        if household_size in income_thresholds:
            if request.income_household_total_monthly <= income_thresholds[household_size]:
                return True

        return False

    @classmethod
    def _has_categorical_eligibility(cls, persons) -> bool:
        """Check if any person has Medicaid, disability Medicaid, or Cash Assistance."""
        for person in persons:
            if person.benefits_medicaid or person.benefits_medicaid_disability:
                return True

            for income in person.incomes:
                if income.type == IncomeType.CASH_ASSISTANCE:
                    return True

        return False
