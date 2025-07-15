"""
Child Tax Credit eligibility rule (S2R004)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule
from src.models.enums import HouseholdMemberType


@register_rule
class ChildTaxCreditRule(BaseRule):
    program = "S2R004"
    description = "Child Tax Credit for households with children under 17"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. At least one child under 17 in household
        2. Yearly income between $2,500 and threshold based on marital status:
           - Married: $400,000
           - Single: $200,000
        """
        persons = request.person
        
        # Check if any child under 17
        has_eligible_child = any(p.age < 17 for p in persons)
        
        if not has_eligible_child:
            return False
        
        # Check income range
        yearly_income = request.income_household_total_yearly
        
        if yearly_income < 2500:
            return False
        
        # Determine if head of household is married
        if request.head_of_household_married:
            return yearly_income <= 400000
        else:
            return yearly_income <= 200000