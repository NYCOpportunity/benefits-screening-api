"""
Child Health Plus eligibility rule (S2R057)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class ChildHealthPlus(BaseRule):
    program = "S2R057"
    description = "Child Health Plus (NYS DOH) - Healthcare coverage for children"

    INFANT_MEDICAID_LIMITS = {
        1: 33584,
        2: 45582,
        3: 57579,
        4: 69576,
        5: 81574,
        6: 93571,
        7: 105569,
        8: 117566,
    }
    CHILD_MEDICAID_LIMITS = {
        1: 23193,
        2: 31478,
        3: 39763,
        4: 48048,
        5: 56334,
        6: 64619,
        7: 72904,
        8: 81189,
    }

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility follows the public ACCESS NYC Drools thresholds:
        1. Infant under age 1 with household income above the infant Medicaid limit
        2. Child age 1-18 with household income above the child Medicaid limit,
           unless an infant is present
        """
        persons = request.person
        household_size = len(persons)
        income = request.income_household_total_yearly

        if any(person.age < 1 for person in persons):
            return income > cls.INFANT_MEDICAID_LIMITS.get(household_size, float("inf"))

        if any(1 <= person.age <= 18 for person in persons):
            return income > cls.CHILD_MEDICAID_LIMITS.get(household_size, float("inf"))

        return False
