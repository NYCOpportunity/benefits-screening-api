"""
Women, Infants and Children program eligibility rule (S2R022)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class WomenInfantsChildren(BaseRule):
    program = "S2R022"
    description = "Women, Infants and Children (WIC) (NYS DOH) - Nutrition assistance for pregnant women and young children"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. NYC residence (assumed for all requests)
        2. At least one person who is pregnant or under age 5
        3. Household income below thresholds based on household size
        """
        persons = request.person
        household_size = len(persons)
        
        # Check for pregnant person or child under 5
        has_eligible_person = any(
            p.pregnant or p.age < 5
            for p in persons
        )
        
        if not has_eligible_person:
            return False
        
        # Income thresholds by household size
        income_thresholds = {
            1: 27861,
            2: 37814,
            3: 47767,
            4: 57720,
            5: 67673,
            6: 77626,
            7: 87579,
            8: 97532
        }
        
        # Check income eligibility
        if household_size in income_thresholds:
            if request.income_household_total_yearly <= income_thresholds[household_size]:
                return True
        
        return False