"""
Earned Income Tax Credit eligibility rule (S2R006)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule
from src.models.enums import HouseholdMemberType


@register_rule
class EarnedIncomeTaxCredit(BaseRule):
    program = "S2R006"
    description = "Earned Income Tax Credit (EITC) (DCA/IRS) - Tax credit based on marital status, children, and income"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Complex eligibility with multiple pathways based on:
        1. Marital status
        2. Number of qualifying children
        3. Investment income < $11,000
        4. Earned income thresholds
        5. Age requirements for childless filers
        """
        persons = request.person
        
        # Check investment income cap
        total_investment_income = sum(request.income_person_investment_yearly.values())
        if total_investment_income >= 11000:
            return False
        
        # Get number of qualifying children (EITC definition)
        num_qualifying_children = request.children_student_blind_disabled_eitc
        
        # Check head of household pathway
        head = next((p for p in persons if p.household_member_type == HouseholdMemberType.HEAD_OF_HOUSEHOLD), None)
        if head:
            head_index = persons.index(head)
            head_earned_income = request.income_person_earned_yearly.get(head_index, 0.0)
            
            # Get combined earned income for married couples
            if request.head_of_household_married:
                combined_earned_income = request.income_head_and_spouse_earned_yearly
                threshold = cls._get_married_threshold(num_qualifying_children)
                
                # Special age check for childless married couples
                if num_qualifying_children == 0:
                    spouse = next((p for p in persons if p.household_member_type == HouseholdMemberType.SPOUSE), None)
                    if not (25 <= head.age <= 64) or not (spouse and 25 <= spouse.age <= 64):
                        # Check individual eligibility instead
                        return cls._check_individual_eligibility(request, persons)
                
                if 0 < combined_earned_income <= threshold:
                    return True
            else:
                # Single head of household
                threshold = cls._get_single_threshold(num_qualifying_children)
                
                # Special age check for childless singles
                if num_qualifying_children == 0 and not (25 <= head.age <= 64):
                    # Check individual eligibility instead
                    return cls._check_individual_eligibility(request, persons)
                
                if 0 < head_earned_income <= threshold:
                    return True
        
        # Check individual household members (non-HoH/spouse)
        return cls._check_individual_eligibility(request, persons)
    
    @classmethod
    def _get_married_threshold(cls, num_children: int) -> float:
        """Get EITC threshold for married filing jointly"""
        if num_children == 0:
            return 24210
        elif num_children == 1:
            return 53120
        elif num_children == 2:
            return 59478
        else:  # 3 or more
            return 63398
    
    @classmethod
    def _get_single_threshold(cls, num_children: int) -> float:
        """Get EITC threshold for single filers"""
        if num_children == 0:
            return 17640
        elif num_children == 1:
            return 46560
        elif num_children == 2:
            return 52918
        else:  # 3 or more
            return 56838
    
    @classmethod
    def _check_individual_eligibility(cls, request, persons) -> bool:
        """Check if any individual household member qualifies"""
        for i, person in enumerate(persons):
            # Skip head of household and spouse
            if person.household_member_type in [HouseholdMemberType.HEAD_OF_HOUSEHOLD, HouseholdMemberType.SPOUSE]:
                continue
            
            # Check age requirement for childless EITC
            if 25 <= person.age <= 64:
                person_earned_income = request.income_person_earned_yearly.get(i, 0.0)
                if 0 < person_earned_income <= 17640:
                    return True
        
        return False