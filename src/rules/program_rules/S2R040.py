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
           - Child age 12 or under, OR
           - Blind or disabled person age 17 or under, OR
           - Blind or disabled person age 18 who is a full-time student
        2. Household income (excluding foster children) below thresholds based on eligible household size
        """
        persons = request.person
        
        # Check for eligible dependent
        has_eligible_dependent = False
        for p in persons:
            if p.age <= 12:
                has_eligible_dependent = True
                break
            if p.age <= 17 and (p.disabled or p.blind):
                has_eligible_dependent = True
                break
            if p.age == 18 and p.student_fulltime and (p.disabled or p.blind):
                has_eligible_dependent = True
                break
        
        if not has_eligible_dependent:
            return False
        
        # Use pre-computed child care voucher household members (excludes foster children)
        eligible_members = request.child_care_voucher_household_members
        
        # Income thresholds by eligible household size
        income_thresholds = {
            2: 6156,
            3: 7604,
            4: 9053,
            5: 10501,
            6: 11949,
            7: 12221,
            8: 12493
        }
        
        # Check income eligibility using child care voucher total income (excludes foster children)
        if eligible_members in income_thresholds:
            if request.income_child_care_voucher_total_monthly <= income_thresholds[eligible_members]:
                return True
        
        return False