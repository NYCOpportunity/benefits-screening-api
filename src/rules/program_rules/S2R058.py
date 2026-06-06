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
        1: (22025, 39900),
        2: (29864, 54100),
        3: (37702, 68300),
        4: (45540, 82500),
        5: (53379, 96700),
        6: (61217, 110900),
        7: (69056, 125100),
        8: (76894, 139300),
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
