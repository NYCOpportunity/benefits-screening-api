"""
S2R058 eligibility rule
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class S2R058(BaseRule):
    program = "S2R058"
    description = (
        "Healthcare coverage for adults aged 19-64 without Medicaid, "
        "based on household income"
    )

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. At least one person aged 19-64 without Medicaid benefits
        2. Household yearly income below thresholds based on household size
        """
        persons = request.person
        household_size = len(persons)

        has_eligible_adult = any(
            19 <= p.age <= 64
            and not p.benefits_medicaid
            and not p.benefits_medicaid_disability
            for p in persons
        )

        if not has_eligible_adult:
            return False

        income_thresholds = {
            1: 31920,
            2: 43280,
            3: 54640,
            4: 66000,
            5: 77360,
            6: 88720,
            7: 100080,
            8: 111440,
        }

        if household_size in income_thresholds:
            if request.income_household_total_yearly <= income_thresholds[household_size]:
                return True

        return False
