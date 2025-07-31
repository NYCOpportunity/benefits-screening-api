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
        1. NYC residence (assumed for all requests)
        2. At least one person aged 60 or older
        3. Household income below thresholds based on household size
        """
        persons = request.person
        household_size = len(persons)
        
        # Check for senior (60+)
        has_senior = any(p.age >= 60 for p in persons)
        
        if not has_senior:
            return False
        
        # Income thresholds by household size
        income_thresholds = {
            1: 19578,
            2: 26572,
            3: 33566,
            4: 40560,
            5: 47554,
            6: 54548,
            7: 61542,
            8: 68536
        }
        
        # Check income eligibility
        if household_size in income_thresholds:
            if request.income_household_total_yearly <= income_thresholds[household_size]:
                return True
        
        return False