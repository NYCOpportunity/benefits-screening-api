"""
Veterans' Property Tax Exemption rule (S2R018)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class VeteransPropertyTaxExemption(BaseRule):
    program = "S2R018"
    description = "Veterans' Property Tax Exemption (DOF) - Property tax exemption for veteran homeowners"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. NYC residence (assumed for all requests)
        2. Household owns their home
        3. At least one veteran is on the deed
        """
        household = request.household[0]
        persons = request.person
        
        # Check home ownership
        if not household.living_owner:
            return False
        
        # Check for veteran owner on deed
        has_veteran_owner = any(
            p.veteran and p.living_owner_on_deed
            for p in persons
        )
        
        return has_veteran_owner