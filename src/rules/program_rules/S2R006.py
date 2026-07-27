"""
Earned Income Tax Credit eligibility rule (S2R006)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule
from src.models.enums import HouseholdMemberType


@register_rule
class EarnedIncomeTaxCredit(BaseRule):
    program = "S2R006"
    description = "Earned Income Tax Credit (EITC) (DCA/IRS) - Tax credit based on marital status, children, and income"

    # Head of household is married
    MARRIED_WITH_CHILDREN_EARNED_THRESHOLDS = {
        1: 57554,
        2: 64430,
        3: 68675,
    }
    MARRIED_NO_CHILDREN_EARNED_THRESHOLD = 26214

    # Head of household is not married
    SINGLE_WITH_CHILDREN_EARNED_THRESHOLDS = {
        1: 50434,
        2: 57310,
        3: 61555,
    }
    SINGLE_NO_CHILDREN_EARNED_THRESHOLD = 19104

    # Step 5 - other household members (Table 2, 0 children)
    OTHER_MEMBER_EARNED_THRESHOLD = 19104
    
    INVESTMENT_LIMIT = 11950

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility follows five pathways based on marital status,
        qualifying children, investment income, earned income, and age.
        """
        persons = request.person
        head = cls._get_head_of_household(persons)
        spouse = cls._get_spouse(persons)
        is_married = request.head_of_household_married
        num_qualifying_children = request.children_student_blind_disabled_eitc

        if cls._head_or_spouse_has_earned_income(request, is_married):
            if num_qualifying_children > 0:
                if cls._eligible_with_qualifying_children(
                    request, is_married, num_qualifying_children
                ):
                    return True
            elif cls._eligible_without_qualifying_children(
                request, head, spouse, is_married
            ):
                return True

        return cls._eligible_other_household_member(request, persons)

    # --- Step 1 ---

    @classmethod
    def _head_or_spouse_has_earned_income(cls, request, is_married: bool) -> bool:
        if is_married:
            return request.income_head_and_spouse_earned_yearly > 0
        return request.income_head_earned_yearly > 0

    # --- Step 3: households with a qualifying child ---

    @classmethod
    def _eligible_with_qualifying_children(
        cls, request, is_married: bool, num_qualifying_children: int
    ) -> bool:
        if is_married:
            return cls._married_with_children_meets_income_limits(
                request, num_qualifying_children
            )
        return cls._unmarried_with_children_meets_income_limits(
            request, num_qualifying_children
        )

    @classmethod
    def _married_with_children_meets_income_limits(
        cls, request, num_qualifying_children: int
    ) -> bool:
        """Table 1: sum HoH and spouse earned and investment income."""
        if cls._head_and_spouse_investment(request) > cls.INVESTMENT_LIMIT:
            return False

        earned_threshold = cls._married_with_children_earned_threshold(
            num_qualifying_children
        )
        earned_income = request.income_head_and_spouse_earned_yearly
        return 0 < earned_income <= earned_threshold

    @classmethod
    def _unmarried_with_children_meets_income_limits(
        cls, request, num_qualifying_children: int
    ) -> bool:
        """Table 2: sum HoH earned and investment income."""
        if cls._head_investment(request) > cls.INVESTMENT_LIMIT:
            return False

        earned_threshold = cls._single_with_children_earned_threshold(
            num_qualifying_children
        )
        earned_income = request.income_head_earned_yearly
        return 0 < earned_income <= earned_threshold

    # --- Step 4: households without a qualifying child ---

    @classmethod
    def _eligible_without_qualifying_children(
        cls, request, head, spouse, is_married: bool
    ) -> bool:
        if is_married:
            return cls._married_without_children_meets_requirements(request, head, spouse)
        return cls._unmarried_without_children_meets_requirements(request, head)

    @classmethod
    def _married_without_children_meets_requirements(cls, request, head, spouse) -> bool:
        """Table 1, 0 children: HoH or spouse age 25-64, combined income limits."""
        if not (
            (head and 25 <= head.age < 65) or (spouse and 25 <= spouse.age < 65)
        ):
            return False
        if cls._head_and_spouse_investment(request) > cls.INVESTMENT_LIMIT:
            return False

        earned_income = request.income_head_and_spouse_earned_yearly
        return 0 < earned_income <= cls.MARRIED_NO_CHILDREN_EARNED_THRESHOLD

    @classmethod
    def _unmarried_without_children_meets_requirements(cls, request, head) -> bool:
        """Table 2, 0 children: HoH age 25-64, HoH income limits."""
        if not head or not (25 <= head.age < 65):
            return False
        if cls._head_investment(request) > cls.INVESTMENT_LIMIT:
            return False

        earned_income = request.income_head_earned_yearly
        return 0 < earned_income <= cls.SINGLE_NO_CHILDREN_EARNED_THRESHOLD

    # --- Step 5: other household members ---

    @classmethod
    def _eligible_other_household_member(cls, request, persons) -> bool:
        for index, person in enumerate(persons):
            if person.household_member_type in (
                HouseholdMemberType.HEAD_OF_HOUSEHOLD,
                HouseholdMemberType.SPOUSE,
            ):
                continue

            if not (25 <= person.age < 65):
                continue

            if request.income_person_investment_yearly.get(index, 0.0) > cls.INVESTMENT_LIMIT:
                continue

            earned_income = request.income_person_earned_yearly.get(index, 0.0)
            if 0 < earned_income <= cls.OTHER_MEMBER_EARNED_THRESHOLD:
                return True

        return False

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
    def _get_spouse(cls, persons):
        return next(
            (
                person
                for person in persons
                if person.household_member_type == HouseholdMemberType.SPOUSE
            ),
            None,
        )

    @classmethod
    def _married_with_children_earned_threshold(cls, num_children: int) -> float:
        if num_children >= 3:
            return cls.MARRIED_WITH_CHILDREN_EARNED_THRESHOLDS[3]
        return cls.MARRIED_WITH_CHILDREN_EARNED_THRESHOLDS[num_children]

    @classmethod
    def _single_with_children_earned_threshold(cls, num_children: int) -> float:
        if num_children >= 3:
            return cls.SINGLE_WITH_CHILDREN_EARNED_THRESHOLDS[3]
        return cls.SINGLE_WITH_CHILDREN_EARNED_THRESHOLDS[num_children]

    @classmethod
    def _head_investment(cls, request) -> float:
        for index, person in enumerate(request.person):
            if person.household_member_type == HouseholdMemberType.HEAD_OF_HOUSEHOLD:
                return request.income_person_investment_yearly.get(index, 0.0)
        return 0.0

    @classmethod
    def _head_and_spouse_investment(cls, request) -> float:
        total = 0.0
        for index, person in enumerate(request.person):
            if person.household_member_type in (
                HouseholdMemberType.HEAD_OF_HOUSEHOLD,
                HouseholdMemberType.SPOUSE,
            ):
                total += request.income_person_investment_yearly.get(index, 0.0)
        return total
