"""
Infants & Toddlers eligibility rule (S2R003)
"""

from __future__ import annotations

from src.models.enums import HouseholdMemberType
from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class InfantsToddlers(BaseRule):
    program = "S2R003"
    description = "Infants & Toddlers (DOE) - Early intervention services for children under 3 years old"

    INCOME_THRESHOLDS = {
        2: 6156,
        3: 7604,
        4: 9053,
        5: 10501,
        6: 11949,
        7: 12221,
        8: 12493,
    }

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. At least one person age 5 or younger
        2. Adults-and-children monthly income at or below the size-based threshold
        """
        persons = request.person
        household_size = cls._household_members_for_threshold(persons)

        if not any(person.age <= 5 for person in persons):
            return False

        threshold = cls.INCOME_THRESHOLDS.get(household_size)
        if threshold is None:
            return False

        return request.income_adults_children_total_monthly <= threshold

    @classmethod
    def _household_members_for_threshold(cls, persons) -> int:
        """
        Count household members including HoH, spouse, and persons under 18.
        Unrelated adults age 18+ are excluded from the household size used for thresholds.
        """
        return sum(
            1
            for person in persons
            if person.household_member_type
            in (
                HouseholdMemberType.HEAD_OF_HOUSEHOLD,
                HouseholdMemberType.SPOUSE,
            )
            or person.age < 18
        )
