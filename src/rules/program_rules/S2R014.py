"""
Senior Citizen Homeowners' Exemption rule (S2R014)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class SeniorCitizenHomeownersExemption(BaseRule):
    program = "S2R014"
    description = "Senior Citizen Homeowners' Exemption (SCHE) (DOF) - Property tax exemption for senior homeowners"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. NYC residence (assumed for all requests)
        2. Household owns their home
        3. Total yearly income of all owners <= $58,399
        4. At least one owner is 65 or older
        """
        household = request.household[0]
        persons = request.person
        
        # Check home ownership
        if not household.living_owner:
            return False
        
        # Check owners' income threshold
        if request.income_owners_total_yearly > 58399:
            return False
        
        # Check for senior owner (65+) on deed
        has_senior_owner = any(
            p.living_owner_on_deed and p.age >= 65
            for p in persons
        )
        
        return has_senior_owner