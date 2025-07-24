"""
Child and Dependent Care Tax Credit eligibility rule (S2R001)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class ChildDependentCareTaxCredit(BaseRule):
    program = "S2R001"
    description = "Child and Dependent Care Tax Credit (DCA/IRS) - Assistance with child or dependent care expenses"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. At least one person under 13, disabled, or blind
        2. Household has child care or dependent care expenses > 0
        3. Head of household and spouse (if present) have earned income > 0
        """
        persons = request.person
        
        # Check condition 1: At least one eligible person
        has_eligible_person = any(
            p.age < 13 or p.disabled or p.blind 
            for p in persons
        )
        
        if not has_eligible_person:
            return False
        
        # Check condition 2: Has child/dependent care expenses
        if request.expense_household_has_child_or_dependent_care is False:
            return False
        
        # Check condition 3: Head and spouse have earned income
        if request.income_head_and_spouse_earned_yearly <= 0:
            return False
        
        return True