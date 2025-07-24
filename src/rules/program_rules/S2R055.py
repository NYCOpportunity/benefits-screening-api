"""
NYC Housing Connect eligibility rule (S2R055)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class NYCHousingConnect(BaseRule):
    program = "S2R055"
    description = "NYC Housing Connect (HPD) - Affordable housing lottery and application portal"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. At least one person aged 18 or older
        2. Household cash on hand <= $256,245
        3. Household yearly income below thresholds based on household size
        """
        household = request.household[0]
        persons = request.person
        household_size = len(persons)
        
        # Check for adult (18+)
        has_adult = any(p.age >= 18 for p in persons)
        
        if not has_adult:
            return False
        
        # Check cash on hand limit
        if household.cash_on_hand is not None and household.cash_on_hand > 256245:
            return False
        
        # Income thresholds by household size
        income_thresholds = {
            1: 179355,
            2: 205095,
            3: 230670,
            4: 256245,
            5: 276705,
            6: 297165,
            7: 317790,
            8: 338250
        }
        
        # Check income eligibility
        if household_size in income_thresholds:
            if request.income_household_total_yearly <= income_thresholds[household_size]:
                return True
        
        return False