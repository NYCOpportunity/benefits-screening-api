"""
Head Start early childhood education program eligibility rule (S2R008)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule
from src.models.enums import HouseholdMemberType


@register_rule
class HeadStart(BaseRule):
    program = "S2R008"
    description = "Head Start (DOE) - Free early childhood education for children aged 3-4"

    INCOME_THRESHOLDS = {
        1: 15960,
        2: 21640,
        3: 27320,
        4: 33000,
        5: 38680,
        6: 44360,
        7: 50040,
        8: 55720,
    }

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility follows the Head Start policy decision tree:
        1. Household member must be age 5 or younger
        2. Cash Assistance or SSI
        3. Gross yearly income within household-size limits
        4. Foster child of Head of Household (when income exceeds limits)
        """
        persons = request.person
        household_size = len(persons)

        if not cls._has_child_age_five_or_younger(persons):
            return False

        if cls._has_cash_assistance_or_ssi(request):
            return True

        if cls._income_within_limits(request, household_size):
            return True

        return cls._has_foster_child_of_head(persons, request)

    # --- Step 1 ---

    @classmethod
    def _has_child_age_five_or_younger(cls, persons) -> bool:
        return any(person.age <= 5 for person in persons)

    # --- Step 2 ---

    @classmethod
    def _has_cash_assistance_or_ssi(cls, request) -> bool:
        return (
            request.income_household_has_cash_assistance
            or request.income_household_has_ssi
        )

    # --- Step 3 ---

    @classmethod
    def _income_within_limits(cls, request, household_size: int) -> bool:
        threshold = cls.INCOME_THRESHOLDS.get(household_size)
        if threshold is None:
            return False
        return request.income_household_total_yearly <= threshold

    # --- Step 4 ---

    @classmethod
    def _has_foster_child_of_head(cls, persons, request) -> bool:
        has_head_of_household = any(
            person.household_member_type == HouseholdMemberType.HEAD_OF_HOUSEHOLD
            for person in persons
        )
        return has_head_of_household and request.foster_children > 0
