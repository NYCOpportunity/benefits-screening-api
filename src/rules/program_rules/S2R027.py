"""
Commodity Supplemental Food Program eligibility rule (S2R027)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class CommoditySupplementalFoodProgram(BaseRule):
    program = "S2R027"
    description = "Commodity Supplemental Food Program (CSFP) (NYS DOH) - Food assistance for seniors"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. At least one person aged 60 or older
        2. Household income below thresholds based on household size
        """
        persons = request.person
        household_size = len(persons)
        
        # Check for senior (60+)
        has_senior = any(p.age >= 60 for p in persons)
        
        if not has_senior:
            return False
        
        # Income thresholds by household size
        income_thresholds = {
            1: 23940,
            2: 32460,
            3: 40980,
            4: 49500,
            5: 58020,
            6: 66540,
            7: 75060,
            8: 83580,
        }
        
        # Check income eligibility
        if household_size in income_thresholds:
            if request.income_household_total_yearly <= income_thresholds[household_size]:
                return True
        
        return False