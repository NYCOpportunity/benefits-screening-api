"""
Disability/blind homeowner exemption rule (S2R017)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule
from src.models.enums import IncomeType


@register_rule
class DisabilityHomeownerExemptionRule(BaseRule):
    program = "S2R017"
    description = "Disability/Blind Homeowner Exemption - Property tax relief for disabled/blind homeowners"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. NYC residence (assumed for all requests)
        2. Household owns their home
        3. Total yearly income of all owners <= $58,399
        4. At least one owner is either:
           - Disabled
           - Blind  
           - Receiving SSI or SS Disability benefits
        """
        household = request.household[0]
        persons = request.person
        
        # Check home ownership
        if not household.living_owner:
            return False
        
        # Check owners' income threshold
        if request.income_owners_total_yearly > 58399:
            return False
        
        # Check for disabled or blind owner on deed
        has_disabled_or_blind_owner = any(
            p.living_owner_on_deed and (p.disabled or p.blind)
            for p in persons
        )
        
        if has_disabled_or_blind_owner:
            return True
        
        # Check if any owner has SSI or SS Disability income
        for person in persons:
            if person.living_owner_on_deed:
                for income in person.incomes:
                    if income.type in [IncomeType.SSI, IncomeType.SS_DISABILITY]:
                        return True
        
        return False