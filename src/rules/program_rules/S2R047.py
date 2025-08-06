"""
NYC NY Connects eligibility rule (S2R047)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule
from src.models.enums import IncomeType


@register_rule
class NYCNYConnects(BaseRule):
    program = "S2R047"
    description = "NYC NY Connects (DFTA) - Information and assistance services for older adults and people with disabilities"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. NYC residence (assumed for all requests)
        2. At least one person who is:
           - Blind, OR
           - Disabled, OR
           - Has Medicaid disability benefits, OR
           - Has Disability Medicaid income
        """
        persons = request.person
        
        # Check for blind, disabled, or Medicaid disability benefits
        has_disability = any(
            p.blind or p.disabled or p.benefits_medicaid_disability
            for p in persons
        )
        
        if has_disability:
            return True
        
        # Check if any person has Disability Medicaid income
        for person in persons:
            for income in person.incomes:
                if income.type == IncomeType.DISABILITY_MEDICAID:
                    return True
        
        return False