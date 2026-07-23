"""
Section 8 Housing eligibility rule (S2R013)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class Section8Housing(BaseRule):
    program = "S2R013"
    description = "Section 8 Housing (NYCHA) - Housing assistance voucher program"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. NYC residence (assumed for all requests)
        2. Head of household is 18 or older
        3. Household income below thresholds based on household size
        """
        persons = request.person
        household_size = len(persons)
        
        # Check for head of household 18+
        from src.models.enums import HouseholdMemberType
        has_adult_head = any(
            p.household_member_type == HouseholdMemberType.HEAD_OF_HOUSEHOLD and p.age >= 18
            for p in persons
        )
        
        if not has_adult_head:
            return False
        
        # Income thresholds by household size
        income_thresholds = {
            1: 56700,
            2: 64800,
            3: 72900,
            4: 81000,
            5: 87500,
            6: 94000,
            7: 100450,
            8: 106950
        }
        
        # Check income eligibility
        if household_size in income_thresholds:
            if request.income_household_total_yearly <= income_thresholds[household_size]:
                return True
        
        return False