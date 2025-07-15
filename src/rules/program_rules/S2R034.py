"""
Fair Fares NYC discount MetroCard program eligibility rule (S2R034)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class FairFaresRule(BaseRule):
    program = "S2R034"
    description = "Fair Fares NYC - Half-price MetroCards for low-income New Yorkers"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. NYC residence (assumed for all requests)
        2. At least one person aged 18-64
        3. Household yearly income below thresholds based on household size
        """
        persons = request.person
        household_size = len(persons)
        
        # Check for adult aged 18-64
        has_eligible_adult = any(
            18 <= p.age <= 64
            for p in persons
        )
        
        if not has_eligible_adult:
            return False
        
        # Income thresholds by household size
        income_thresholds = {
            1: 21837,
            2: 29638,
            3: 37439,
            4: 45240,
            5: 53041,
            6: 60842,
            7: 68643,
            8: 76444
        }
        
        # Check income eligibility
        if household_size in income_thresholds:
            if request.income_household_total_yearly <= income_thresholds[household_size]:
                return True
        
        return False