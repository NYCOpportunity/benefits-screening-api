"""
Women, Infants and Children program eligibility rule (S2R022)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class WomenInfantsChildren(BaseRule):
    program = "S2R022"
    description = "Women, Infants and Children (WIC) (NYS DOH) - Nutrition assistance for pregnant women and young children"

    INCOME_THRESHOLDS = {
        1: 28953,
        2: 39128,
        3: 49303,
        4: 59478,
        5: 69653,
        6: 79828,
        7: 90003,
        8: 100178,
    }

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. NYC residence (assumed for all requests)
        2. At least one person who is pregnant or under age 5
        3. Household income below thresholds based on household size, or reported
           Medicaid, Disability Medicaid, or Cash Assistance
        """
        persons = request.person
        household_size = len(persons)

        # Check for pregnant person or child under 5
        has_eligible_person = any(
            p.pregnant or p.age < 5
            for p in persons
        )

        if not has_eligible_person:
            return False

        if cls._has_categorical_benefit(request, persons):
            return True

        threshold = cls.INCOME_THRESHOLDS.get(household_size)
        return threshold is not None and request.income_household_total_yearly <= threshold

    @classmethod
    def _has_categorical_benefit(cls, request, persons) -> bool:
        return (
            any(
                p.benefits_medicaid or p.benefits_medicaid_disability
                for p in persons
            )
            or request.income_household_has_cash_assistance
        )
