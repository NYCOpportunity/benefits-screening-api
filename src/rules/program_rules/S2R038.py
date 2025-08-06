"""
Medicaid for Pregnant Women eligibility rule (S2R038)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class MedicaidPregnantWomen(BaseRule):
    program = "S2R038"
    description = "Medicaid for Pregnant Women (HRA) - Healthcare coverage for pregnant women"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. NYC residence (assumed for all requests)
        2. At least one pregnant person
        3. Household yearly income below thresholds based on household size
        """
        persons = request.person
        household_size = len(persons)
        
        # Check for pregnant person
        has_pregnant = any(p.pregnant for p in persons)
        
        if not has_pregnant:
            return False
        
        # Income thresholds by household size
        income_thresholds = {
            1: 33584,
            2: 45581,
            3: 57579,
            4: 69576,
            5: 81573,
            6: 93571,
            7: 105568,
            8: 117566
        }
        
        # Check income eligibility
        if household_size in income_thresholds:
            if request.income_household_total_yearly <= income_thresholds[household_size]:
                return True
        
        return False