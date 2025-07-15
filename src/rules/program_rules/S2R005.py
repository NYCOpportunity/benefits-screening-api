"""
Rental Assistance eligibility rule (S2R005)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule
from src.models.enums import HouseholdMemberType, LivingRentalType, IncomeType


@register_rule
class RentalAssistanceRule(BaseRule):
    program = "S2R005"
    description = "Rental Assistance for specific housing types with income requirements"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. Household is renting specific types (Rent Controlled, HDFC, Mitchell Lama, Section 213)
        2. Head of household is 18+ and on the lease
        3. Head of household has qualifying income types
        4. Total yearly household income ≤ $50,000
        """
        household = request.household[0]
        persons = request.person
        
        # Check if renting
        if not household.living_renting:
            return False
        
        # Check rental type
        eligible_rental_types = [
            LivingRentalType.RENT_CONTROLLED,
            LivingRentalType.HDFC,
            LivingRentalType.MITCHELL_LAMA,
            LivingRentalType.SECTION_213
        ]
        
        if household.living_rental_type not in eligible_rental_types:
            return False
        
        # Find head of household
        head_of_household = next(
            (p for p in persons if p.household_member_type == HouseholdMemberType.HEAD_OF_HOUSEHOLD),
            None
        )
        
        if not head_of_household:
            return False
        
        # Check if head is 18+ and on lease
        if head_of_household.age < 18 or not head_of_household.living_rental_on_lease:
            return False
        
        # Check if head has qualifying income types
        if not cls._head_has_qualifying_income(head_of_household):
            return False
        
        # Check income threshold
        if request.income_household_total_yearly > 50000:
            return False
        
        return True
    
    @classmethod
    def _head_has_qualifying_income(cls, head_of_household) -> bool:
        """Check if head of household has S2R005 qualifying income types"""
        # Based on Drools rules, qualifying income types include:
        # wages, self-employment, pension, SS benefits, unemployment, workers comp, etc.
        # Excludes: cash assistance, SSI
        
        qualifying_income_types = [
            IncomeType.WAGES,
            IncomeType.SELF_EMPLOYMENT,
            IncomeType.PENSION,
            IncomeType.SS_RETIREMENT,
            IncomeType.SS_DISABILITY,
            IncomeType.SS_SURVIVOR,
            IncomeType.UNEMPLOYMENT,
            IncomeType.WORKERS_COMP,
            IncomeType.VETERAN,
            IncomeType.RENTAL,
            IncomeType.INVESTMENT,
            IncomeType.ALIMONY,
            IncomeType.CHILD_SUPPORT,
        ]
        
        for income in head_of_household.incomes:
            if income.type in qualifying_income_types:
                return True
        
        return False