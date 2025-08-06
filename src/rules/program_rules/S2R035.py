"""
Public Housing eligibility rule (S2R035)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule
from src.models.enums import HouseholdMemberType


@register_rule
class PublicHousing(BaseRule):
    program = "S2R035"
    description = "Public Housing (NYCHA) - Affordable housing for low and moderate income residents"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires NYC residence and either:
        1. Family household (2+ people with specific relationships) with income below thresholds
        2. Individual or unrelated adults with individual income below $87,100
        """
        persons = request.person
        household_size = len(persons)
        
        # Define family relationship types
        family_relations = [
            HouseholdMemberType.SPOUSE,
            HouseholdMemberType.CHILD,
            HouseholdMemberType.FOSTER_CHILD,
            HouseholdMemberType.PARENT,
            HouseholdMemberType.GRANDPARENT,
            HouseholdMemberType.FOSTER_PARENT,
            HouseholdMemberType.SISTER_BROTHER,
            HouseholdMemberType.DOMESTIC_PARTNER,
            HouseholdMemberType.STEP_CHILD,
            HouseholdMemberType.STEP_PARENT,
            HouseholdMemberType.STEP_SISTER_STEP_BROTHER
        ]
        
        # Check if household has family relationships
        has_family_relations = any(
            p.household_member_type in family_relations
            for p in persons
        )
        
        # Find head of household
        head_of_household = next(
            (p for p in persons if p.household_member_type == HouseholdMemberType.HEAD_OF_HOUSEHOLD),
            None
        )
        
        # Check eligibility for family households
        if has_family_relations and head_of_household and head_of_household.age >= 18:
            # Check no minor spouses/partners
            has_minor_spouse_partner = any(
                p.age < 18 and p.household_member_type in [HouseholdMemberType.SPOUSE, HouseholdMemberType.DOMESTIC_PARTNER]
                for p in persons
            )
            
            if not has_minor_spouse_partner:
                # Family income thresholds by household size (minimum 2 for family)
                family_income_thresholds = {
                    2: 99550,
                    3: 111950,
                    4: 124400,
                    5: 134350,
                    6: 144300,
                    7: 154250,
                    8: 164200
                }
                
                if household_size in family_income_thresholds:
                    if request.income_household_total_yearly <= family_income_thresholds[household_size]:
                        return True
        
        # Check eligibility for individual/unrelated adults
        if request.household_all_adults and not has_family_relations:
            # Check individual income for any person
            for i, person in enumerate(persons):
                person_yearly_income = request.income_person_yearly.get(i, 0.0)
                if person_yearly_income <= 87100:
                    return True
        
        return False