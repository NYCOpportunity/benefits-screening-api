"""
Big Apple Connect eligibility rule (S2R054)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule
from src.models.enums import LivingRentalType


@register_rule
class BigAppleConnect(BaseRule):
    program = "S2R054"
    description = "Big Apple Connect (NYCHA) - Free internet service for NYCHA residents"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. Household is renting from NYCHA
        """
        household = request.household[0]
        
        # Check NYCHA rental
        if household.living_renting and household.living_rental_type == LivingRentalType.NYCHA:
            return True
        
        return False