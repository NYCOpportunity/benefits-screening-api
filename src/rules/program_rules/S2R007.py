"""
Supplemental Nutrition Assistance Program eligibility rule (S2R007)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule
from src.models.enums import IncomeType


@register_rule
class SupplementalNutritionAssistanceProgram(BaseRule):
    program = "S2R007"
    description = "Supplemental Nutrition Assistance Program (SNAP/Food Stamps) (HRA) - Food assistance program"

    SPECIAL_CIRCUMSTANCE_LIMITS = {
        1: 2608,
        2: 3525,
        3: 4442,
        4: 5358,
        5: 6275,
        6: 7192,
        7: 8108,
        8: 9025,
    }
    EARNED_INCOME_LIMITS = {
        1: 1957,
        2: 2644,
        3: 3332,
        4: 4019,
        5: 4707,
        6: 5394,
        7: 6082,
        8: 6769,
    }
    OTHER_INCOME_LIMITS = {
        1: 1696,
        2: 2292,
        3: 2888,
        4: 3483,
        5: 4079,
        6: 4675,
        7: 5271,
        8: 5867,
    }

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        SNAP eligibility follows the public ACCESS NYC Drools gross-income screen:
        1. All household members receive SSI or Cash Assistance (categorical eligibility)
        2. 200% gross income with child/dependent care, elderly, disabled, or blind
        3. 150% gross income with earned income
        4. 130% gross income for all others
        """
        persons = request.person
        household_size = len(persons)

        if cls._check_categorical_eligibility(request, persons):
            return True

        gross_income = cls._gross_income_minus_child_support(request)
        limits = cls._income_limits_for_household(request, persons)
        return gross_income <= limits.get(household_size, float("-inf"))

    @classmethod
    def _check_categorical_eligibility(cls, request, persons) -> bool:
        """Check if all household members have SSI or Cash Assistance"""
        if len(persons) == 0:
            return False

        # Check if all persons have either SSI or Cash Assistance
        all_have_benefits = True
        for person in persons:
            has_ssi = False
            has_cash_assistance = False

            for income in person.incomes:
                if income.type == IncomeType.SSI:
                    has_ssi = True
                elif income.type == IncomeType.CASH_ASSISTANCE:
                    has_cash_assistance = True

            if not (has_ssi or has_cash_assistance):
                all_have_benefits = False
                break

        return all_have_benefits

    @classmethod
    def _gross_income_minus_child_support(cls, request) -> float:
        gross_income = (
            request.income_household_wage_self_employment_monthly
            + request.income_household_boarder_monthly
            + request.income_household_unearned_monthly
            - request.expense_household_child_support_monthly
        )
        return max(gross_income, 0.0)

    @classmethod
    def _income_limits_for_household(cls, request, persons) -> dict[int, int]:
        has_child_care_expenses = request.expense_household_has_child_or_dependent_care
        has_elderly = any(p.age >= 60 for p in persons)
        has_disabled_or_blind = any(p.disabled or p.blind for p in persons)

        if has_child_care_expenses or has_elderly or has_disabled_or_blind:
            return cls.SPECIAL_CIRCUMSTANCE_LIMITS

        has_earned_income = (
            request.income_household_wage_self_employment_monthly > 0
            or request.income_household_boarder_monthly > 0
        )

        if has_earned_income:
            return cls.EARNED_INCOME_LIMITS

        return cls.OTHER_INCOME_LIMITS
