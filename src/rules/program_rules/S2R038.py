"""
Medicaid eligibility rule (S2R038)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule
from src.models.enums import HouseholdMemberType


@register_rule
class MedicaidPregnantWomen(BaseRule):
    program = "S2R038"
    description = "Medicaid"

    MEDICAID_CHILD_RELATIONS = {
        HouseholdMemberType.CHILD,
        HouseholdMemberType.FOSTER_CHILD,
        HouseholdMemberType.STEP_CHILD,
        HouseholdMemberType.GRANDCHILD,
        HouseholdMemberType.SISTER_BROTHER,
        HouseholdMemberType.STEP_SISTER_STEP_BROTHER,
    }

    PREGNANT_AND_INFANT_THRESHOLDS = {
        1: 35591,
        2: 48258,
        3: 60924,
        4: 73590,
        5: 86257,
        6: 98923,
        7: 111590,
        8: 124256,
        9: 136922,
    }

    YOUNG_ADULT_THRESHOLDS = {
        1: 24738,
        2: 33542,
        3: 42346,
        4: 51150,
        5: 59954,
        6: 68758,
        7: 77562,
        8: 86366,
    }

    YOUTH_THRESHOLDS = {
        1: 24579,
        2: 33326,
        3: 42073,
        4: 50820,
        5: 59568,
        6: 68315,
        7: 77062,
        8: 85809,
    }

    DEFAULT_THRESHOLDS = {
        1: 22025,
        2: 29864,
        3: 37702,
        4: 45540,
        5: 53379,
        6: 61217,
        7: 69056,
        8: 76894,
    }

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility follows:
        1. Pregnant head of household or pregnant spouse with Medicaid income limits
        2. Infant under age 1 with Medicaid income limits
        3. Age 19-20 with qualifying child relationship and youth-adult income limits
        4. Age 18 or younger with qualifying relationship and youth income limits
        5. General Medicaid income limits for counted household members
        """
        persons = request.person
        members_medicaid = cls._members_medicaid(persons)
        income_medicaid = cls._income_medicaid_total_yearly(request, persons)

        if cls._has_pregnant_hoh_or_spouse(persons):
            if cls._meets_income_threshold(
                members_medicaid,
                income_medicaid,
                cls.PREGNANT_AND_INFANT_THRESHOLDS,
            ):
                return True

        if any(person.age < 1 for person in persons):
            if cls._meets_income_threshold(
                members_medicaid,
                income_medicaid,
                cls.PREGNANT_AND_INFANT_THRESHOLDS,
            ):
                return True

        if any(cls._is_19_or_20_with_child_relation(person) for person in persons):
            if cls._meets_income_threshold(
                members_medicaid,
                income_medicaid,
                cls.YOUNG_ADULT_THRESHOLDS,
            ):
                return True

        if any(cls._is_youth_eligible(person) for person in persons):
            if cls._meets_income_threshold(
                members_medicaid,
                income_medicaid,
                cls.YOUTH_THRESHOLDS,
            ):
                return True

        return cls._meets_income_threshold(
            members_medicaid,
            income_medicaid,
            cls.DEFAULT_THRESHOLDS,
        )

    @classmethod
    def _members_medicaid(cls, persons) -> int:
        """
        Count HoH, spouse, and qualifying members age 20 or under, plus one
        additional member for each pregnant HoH or spouse (unborn child).
        """
        count = sum(
            1
            for person in persons
            if cls._is_medicaid_household_member(person)
        )
        count += sum(
            1
            for person in persons
            if person.pregnant
            and person.household_member_type
            in (
                HouseholdMemberType.HEAD_OF_HOUSEHOLD,
                HouseholdMemberType.SPOUSE,
            )
        )
        return count

    @classmethod
    def _income_medicaid_total_yearly(cls, request, persons) -> float:
        """
        Sum yearly income for HoH, spouse, and qualifying members age 20 or under.
        Excludes income from pregnant HoH or spouse under age 21.
        """
        total = 0.0
        for index, person in enumerate(persons):
            if not cls._counts_for_medicaid_income(person):
                continue
            total += request.income_person_yearly.get(index, 0.0)
        return total

    @classmethod
    def _is_medicaid_household_member(cls, person) -> bool:
        member_type = person.household_member_type
        if member_type in (
            HouseholdMemberType.HEAD_OF_HOUSEHOLD,
            HouseholdMemberType.SPOUSE,
        ):
            return True
        return person.age <= 20 and member_type in cls.MEDICAID_CHILD_RELATIONS

    @classmethod
    def _counts_for_medicaid_income(cls, person) -> bool:
        member_type = person.household_member_type
        if member_type == HouseholdMemberType.HEAD_OF_HOUSEHOLD:
            return not person.pregnant or person.age >= 21
        if member_type == HouseholdMemberType.SPOUSE:
            return not person.pregnant or person.age >= 21
        return person.age <= 20 and member_type in cls.MEDICAID_CHILD_RELATIONS

    @classmethod
    def _has_pregnant_hoh_or_spouse(cls, persons) -> bool:
        return any(
            person.pregnant
            and person.household_member_type
            in (
                HouseholdMemberType.HEAD_OF_HOUSEHOLD,
                HouseholdMemberType.SPOUSE,
            )
            for person in persons
        )

    @classmethod
    def _is_19_or_20_with_child_relation(cls, person) -> bool:
        return (
            person.age in (19, 20)
            and person.household_member_type in cls.MEDICAID_CHILD_RELATIONS
        )

    @classmethod
    def _is_youth_eligible(cls, person) -> bool:
        if person.age > 18:
            return False
        if person.household_member_type == HouseholdMemberType.HEAD_OF_HOUSEHOLD:
            return True
        return person.household_member_type in (
            {HouseholdMemberType.SPOUSE} | cls.MEDICAID_CHILD_RELATIONS
        )

    @classmethod
    def _meets_income_threshold(
        cls,
        members_medicaid: int,
        income_medicaid: float,
        thresholds: dict[int, int],
    ) -> bool:
        if members_medicaid >= 9 and 9 in thresholds:
            return income_medicaid <= thresholds[9]
        if members_medicaid in thresholds:
            return income_medicaid <= thresholds[members_medicaid]
        return False
