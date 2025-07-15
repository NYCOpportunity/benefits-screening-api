"""
NYC housing program eligibility rule (S2R013)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class HousingProgramRule(BaseRule):
    program = "S2R013"
    description = "NYC Housing Program - Affordable housing assistance"

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
            1: 54350,
            2: 62150,
            3: 69900,
            4: 77650,
            5: 83850,
            6: 90050,
            7: 96300,
            8: 102500
        }
        
        # Check income eligibility
        if household_size in income_thresholds:
            if request.income_household_total_yearly <= income_thresholds[household_size]:
                return True
        
        return False