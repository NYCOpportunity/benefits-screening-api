"""
Essential Plan eligibility rule (S2R058)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class EssentialPlan(BaseRule):
    program = "S2R058"
    description = "Essential Plan (NY State of Health) - Low-cost healthcare coverage for adults"

    INCOME_RANGES = {
        1: (21597, 39125),
        2: (29187, 52875),
        3: (36777, 66625),
        4: (44367, 80375),
        5: (51957, 94125),
        6: (66451, 107875),
        7: (67137, 121625),
        8: (74727, 135375),
    }

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires an adult age 19-64 who does not already report
        Medicaid or disability Medicaid, with household income in the Drools
        threshold range for household size.
        """
        household_size = len(request.person)
        income_range = cls.INCOME_RANGES.get(household_size)
        if income_range is None:
            return False

        lower, upper = income_range
        if not lower < request.income_household_total_yearly <= upper:
            return False

        return any(
            19 <= person.age <= 64
            and not person.benefits_medicaid
            and not person.benefits_medicaid_disability
            for person in request.person
        )
