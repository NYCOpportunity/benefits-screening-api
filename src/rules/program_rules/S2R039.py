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

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. NYC residence (assumed for all requests)
        2. Either:
           - Single-person household with income <= $59,000, OR
           - Multi-person household where a child/stepchild is head of household with income <= $85,000
        """
        persons = request.person
        household_size = len(persons)
        
        # Check single-person household
        if household_size == 1:
            if request.income_household_total_yearly <= 59000:
                return True
        
        # Check multi-person household with child/stepchild as head
        if household_size > 1:
            # Find if any person is a child/stepchild relation to head of household
            has_child_relation = any(
                p.household_member_type in [HouseholdMemberType.CHILD, HouseholdMemberType.STEP_CHILD]
                for p in persons
            )
            
            if has_child_relation and request.income_household_total_yearly <= 85000:
                return True
        
        return False