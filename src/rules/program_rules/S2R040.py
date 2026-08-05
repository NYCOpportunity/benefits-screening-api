"""
Child Care Voucher program eligibility rule (S2R040)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class ChildCareVoucher(BaseRule):
    program = "S2R040"
    description = "Child Care Voucher (ACS) - Financial assistance for child care expenses"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. At least one eligible dependent:
           - Child age 13 or under, OR
           - Blind or disabled person age 19 or under
        2. Either:
           - Child care voucher household income at or below thresholds by
             eligible household size (2-8 members), OR
           - Household receives Cash Assistance
        """
        persons = request.person

        has_eligible_dependent = any(
            person.age <= 13
            or (person.age <= 19 and (person.disabled or person.blind))
            for person in persons
        )
        if not has_eligible_dependent:
            return False

        if request.income_household_has_cash_assistance:
            return True

        eligible_members = request.child_care_voucher_household_members
        income_thresholds = {
            2: 6601.24,
            3: 8155.48,
            4: 9707.70,
            5: 11260.94,
            6: 12814.18,
            7: 13105.40,
            8: 13396.64,
        }

        if eligible_members in income_thresholds:
            return (
                request.income_child_care_voucher_total_monthly
                <= income_thresholds[eligible_members]
            )

        return False
