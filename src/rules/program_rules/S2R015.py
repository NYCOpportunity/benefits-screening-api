"""
Senior Citizen Rent Increase Exemption (SCRIE) eligibility rule (S2R015)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule
from src.models.enums import HouseholdMemberType, LivingRentalType


@register_rule
class SCRIERule(BaseRule):
    program = "S2R015"
    description = "SCRIE - Senior Citizen Rent Increase Exemption for eligible rental types"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. Household is renting
        2. Rental type is one of: RentControlled, HDFC, RentRegulatedHotel, MitchellLama, Section213
        3. Head of household is age 62+ and on the lease
        4. Total yearly household income (excluding gifts) ≤ $50,000
        """
        household = request.household[0]
        persons = request.person
        
        # Check if household is renting
        if not household.living_renting:
            return False
        
        # Check rental type
        eligible_rental_types = [
            LivingRentalType.RENT_CONTROLLED,
            LivingRentalType.HDFC,
            LivingRentalType.RENT_REGULATED_HOTEL,
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
        
        # Check if head of household is 62+ and on lease
        if head_of_household.age < 62 or not head_of_household.living_rental_on_lease:
            return False
        
        # Check income threshold
        if request.income_household_total_yearly - request.income_household_total_monthly_less_gifts * 12 > 50000:
            return False
        
        return True