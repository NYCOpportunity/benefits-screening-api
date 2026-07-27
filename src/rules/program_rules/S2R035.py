"""
Public Housing eligibility rule (S2R035)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule
from src.models.enums import HouseholdMemberType


@register_rule
class PublicHousing(BaseRule):
    program = "S2R035"
    description = "Public Housing (NYCHA) - Affordable housing for low and moderate income residents"

    FAMILY_RELATIONS = {
        HouseholdMemberType.SPOUSE,
        HouseholdMemberType.CHILD,
        HouseholdMemberType.FOSTER_CHILD,
        HouseholdMemberType.PARENT,
        HouseholdMemberType.GRANDPARENT,
        HouseholdMemberType.GRANDCHILD,
        HouseholdMemberType.FOSTER_PARENT,
        HouseholdMemberType.SISTER_BROTHER,
        HouseholdMemberType.DOMESTIC_PARTNER,
        HouseholdMemberType.STEP_CHILD,
        HouseholdMemberType.STEP_PARENT,
        HouseholdMemberType.STEP_SISTER_STEP_BROTHER,
    }

    UNRELATED_TO_HEAD_OF_HOUSEHOLD = {
        HouseholdMemberType.UNRELATED,
        HouseholdMemberType.OTHER,
        HouseholdMemberType.BOYFRIEND_GIRLFRIEND,
    }

    HOUSEHOLD_INCOME_THRESHOLDS = {
        1: 95000,
        2: 108600,
        3: 122150,
        4: 135700,
        5: 146600,
        6: 157450,
        7: 168300,
        8: 179150,
    }

    @classmethod
    def evaluate(cls, request) -> bool:
        persons = request.person
        household_size = len(persons)

        head_of_household = cls._get_head_of_household(persons)

        # Step 1: Head of household must be 18 or older.
        if not head_of_household or head_of_household.age < 18:
            return False

        # Step 2: Spouse or domestic partner must be 18 or older, if present.
        if cls._has_minor_spouse_or_partner(persons):
            return False

        # Step 3: Households larger than 1 use family relationships to choose a path.
        if household_size > 1:
            if cls._has_family_relationship(persons):
                # Step 4: Household gross annual income by household size.
                return cls._meets_household_income_threshold(
                    request.income_household_total_yearly, household_size
                )

            # Step 5: Two or more unrelated adults check income individually.
            return cls._meets_individual_unrelated_adult_income(request, persons)

        # Single-person households use the household income threshold for size 1.
        return cls._meets_household_income_threshold(
            request.income_household_total_yearly, household_size
        )

    @classmethod
    def _get_head_of_household(cls, persons):
        return next(
            (
                person
                for person in persons
                if person.household_member_type == HouseholdMemberType.HEAD_OF_HOUSEHOLD
            ),
            None,
        )

    @classmethod
    def _has_minor_spouse_or_partner(cls, persons) -> bool:
        return any(
            person.age < 18
            and person.household_member_type
            in {HouseholdMemberType.SPOUSE, HouseholdMemberType.DOMESTIC_PARTNER}
            for person in persons
        )

    @classmethod
    def _has_family_relationship(cls, persons) -> bool:
        return any(
            person.household_member_type in cls.FAMILY_RELATIONS for person in persons
        )

    @classmethod
    def _meets_household_income_threshold(
        cls, household_yearly_income: float, household_size: int
    ) -> bool:
        threshold = cls.HOUSEHOLD_INCOME_THRESHOLDS.get(household_size)
        if threshold is None:
            return False
        return household_yearly_income <= threshold

    @classmethod
    def _meets_individual_unrelated_adult_income(cls, request, persons) -> bool:
        adult_count = sum(1 for person in persons if person.age >= 18)
        if adult_count < 2:
            return False

        for person in persons:
            if person.household_member_type == HouseholdMemberType.HEAD_OF_HOUSEHOLD:
                continue
            if person.household_member_type not in cls.UNRELATED_TO_HEAD_OF_HOUSEHOLD:
                return False

        for index, person in enumerate(persons):
            if person.age < 18:
                continue
            if (
                request.income_person_yearly.get(index, 0.0)
                <= cls.HOUSEHOLD_INCOME_THRESHOLDS.get(1)
            ):
                return True

        return False
