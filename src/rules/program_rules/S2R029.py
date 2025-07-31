"""
Nurse-Family Partnership eligibility rule (S2R029)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class NurseFamilyPartnership(BaseRule):
    program = "S2R029"
    description = "Nurse-Family Partnership (DOHMH) - Prenatal and postnatal support for first-time mothers"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. NYC residence (assumed for all requests)
        2. At least one pregnant person
        3. Household monthly income below thresholds based on household size + pregnant members
        """
        persons = request.person
        
        # Check for pregnant person
        has_pregnant = any(p.pregnant for p in persons)
        
        if not has_pregnant:
            return False
        
        # Use the pre-computed members_plus_pregnant aggregate
        members_plus_pregnant = request.members_plus_pregnant
        
        # Income thresholds by household size including pregnant members
        income_thresholds = {
            2: 2960,
            3: 3733,
            4: 4606,
            5: 5280,
            6: 6053,
            7: 6826,
            8: 7599
        }
        
        # Check income eligibility
        if members_plus_pregnant in income_thresholds:
            if request.income_household_total_monthly <= income_thresholds[members_plus_pregnant]:
                return True
        
        return False