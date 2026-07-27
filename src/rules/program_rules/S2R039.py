"""
NYC Free Tax Prep eligibility rule (S2R039)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule
from src.models.enums import HouseholdMemberType


@register_rule
class NYCFreeTaxPrep(BaseRule):
    program = "S2R039"
    description = "NYC Free Tax Prep (DCA) - Free tax preparation services for low-income households"

    DEPENDENT_CHILD_TYPES = {
        HouseholdMemberType.CHILD,
        HouseholdMemberType.STEP_CHILD,
        HouseholdMemberType.FOSTER_CHILD,
    }

    GENERAL_INCOME_LIMIT = 68000
    HOUSEHOLD_WITH_DEPENDENT_INCOME_LIMIT = 97000

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires either:
        1. Household yearly income at or below $68,000, or
        2. Multi-person household with a child, stepchild, or foster child
           and household yearly income at or below $97,000
        """
        yearly_income = request.income_household_total_yearly

        if yearly_income <= cls.GENERAL_INCOME_LIMIT:
            return True

        persons = request.person
        if len(persons) > 1 and cls._has_dependent_child(persons):
            return yearly_income <= cls.HOUSEHOLD_WITH_DEPENDENT_INCOME_LIMIT

        return False

    @classmethod
    def _has_dependent_child(cls, persons) -> bool:
        return any(
            person.household_member_type in cls.DEPENDENT_CHILD_TYPES
            for person in persons
        )
