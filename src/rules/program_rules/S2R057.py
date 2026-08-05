"""
Child Health Plus eligibility rule (S2R057)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class ChildHealthPlus(BaseRule):
    program = "S2R057"
    description = (
        "Child Health Plus (NYS DOH) - Health insurance for children 18 and under "
        "who don’t qualify for Medicaid and do not have other health insurance coverage."
    )

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires household income above thresholds based on
        household size and the age of children in the household:

        1. If any child is under 1, income must exceed infant thresholds.
        2. If any child is aged 1-18 and no child is under 1, income must
           exceed child thresholds.
        """
        persons = request.person
        household_size = len(persons)
        yearly_income = request.income_household_total_yearly

        has_infant = any(p.age < 1 for p in persons)
        if has_infant:
            infant_thresholds = {
                1: 33584,
                2: 45582,
                3: 57579,
                4: 69576,
                5: 81574,
                6: 93571,
                7: 105569,
                8: 117566,
            }
            if household_size in infant_thresholds:
                return yearly_income > infant_thresholds[household_size]
            return False

        has_child_1_to_18 = any(1 <= p.age <= 18 for p in persons)
        if has_child_1_to_18:
            child_thresholds = {
                1: 23193,
                2: 31478,
                3: 39763,
                4: 48048,
                5: 56334,
                6: 64619,
                7: 72904,
                8: 81189,
            }
            if household_size in child_thresholds:
                return yearly_income > child_thresholds[household_size]

        return False
