"""
NYCHA resident employment program eligibility rule (S2R024)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule
from src.models.enums import LivingRentalType


@register_rule
class NYCHAResidentEmploymentRule(BaseRule):
    program = "S2R024"
    description = "NYCHA Resident Employment Program - Job training for NYCHA residents"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. NYC residence (assumed for all requests)
        2. Household is renting from NYCHA
        3. At least one person aged 18 or older
        """
        household = request.household[0]
        persons = request.person
        
        # Check NYCHA rental
        if not (household.living_renting and household.living_rental_type == LivingRentalType.NYCHA):
            return False
        
        # Check for adult (18+)
        has_adult = any(p.age >= 18 for p in persons)
        
        return has_adult