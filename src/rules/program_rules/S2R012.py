"""
School Tax Relief program eligibility rule (S2R012)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class SchoolTaxRelief(BaseRule):
    program = "S2R012"
    description = "School Tax Relief (STAR) (DOF) - Property tax relief for homeowners"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. NYC residence (assumed for all requests)
        2. Household owns their home
        3. Total yearly income of all owners <= $500,000
        """
        household = request.household[0]
        
        # Check home ownership
        if not household.living_owner:
            return False
        
        # Check owners' income threshold
        if request.income_owners_total_yearly <= 500000:
            return True
        
        return False