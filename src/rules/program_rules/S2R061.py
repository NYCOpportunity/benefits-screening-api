"""
MTA Reduced Fare eligibility rule (S2R061)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule
from src.models.enums import IncomeType


@register_rule
class MTAReducedFare(BaseRule):
    program = "S2R061"
    description = "MTA Reduced Fare - Discounted transit fare for seniors and people with disabilities"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires at least one person who is:
        1. Aged 65 or older, or
        2. Disabled, or
        3. Blind, or
        4. Receiving disability-related Medicaid, or
        5. Receiving SSI
        """
        for person in request.person:
            if (
                person.age >= 65
                or person.disabled
                or person.blind
                or person.benefits_medicaid_disability
            ):
                return True

            for income in person.incomes:
                if income.type == IncomeType.SSI:
                    return True

        return False
