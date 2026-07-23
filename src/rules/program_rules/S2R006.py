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
        3. Investment income <= $11,600
        4. Earned income thresholds
        5. Age requirements for childless filers
        """
        persons = request.person
        num_qualifying_children = request.children_student_blind_disabled_eitc
        
        head = next((p for p in persons if p.household_member_type == HouseholdMemberType.HEAD_OF_HOUSEHOLD), None)
        if not head:
            # No head of household, check individual members only
            return cls._check_individual_eligibility(request, persons)
        
        head_index = persons.index(head)
        
        if request.head_of_household_married:
            # Check investment income for HoH and Spouse combined
            hoh_and_spouse_investment = cls._get_head_and_spouse_investment(request, persons)
            if hoh_and_spouse_investment > 11600:
                # Investment income too high, check individual members
                return cls._check_individual_eligibility(request, persons)
            
            combined_earned_income = request.income_head_and_spouse_earned_yearly
            
            # Rule 1: Married with qualifying children
            if num_qualifying_children > 0:
                threshold = cls._get_married_threshold(num_qualifying_children)
                if 0 < combined_earned_income <= threshold:
                    return True
            
            # Rule 2: Married without qualifying children (either HoH or Spouse age 25-64 required)
            if num_qualifying_children == 0:
                spouse = next((p for p in persons if p.household_member_type == HouseholdMemberType.SPOUSE), None)
                # Either HoH or Spouse must be 25-64
                if (25 <= head.age < 65) or (spouse and 25 <= spouse.age < 65):
                    if 0 < combined_earned_income <= 25511:
                        return True
        
        # Rule 3 & 4: Single head of household
        else:
            # Check investment income for HoH only
            head_investment = request.income_person_investment_yearly.get(head_index, 0.0)
            if head_investment > 11600:
                # Investment income too high, check individual members
                return cls._check_individual_eligibility(request, persons)
            
            head_earned_income = request.income_person_earned_yearly.get(head_index, 0.0)
            
            # Rule 3: Single with qualifying children
            if num_qualifying_children > 0:
                threshold = cls._get_single_threshold(num_qualifying_children)
                if 0 < head_earned_income <= threshold:
                    return True
            
            # Rule 4: Single without qualifying children (age 25-64 required)
            if num_qualifying_children == 0:
                if 25 <= head.age < 65:
                    if 0 < head_earned_income <= 18591:
                        return True
        
        # Rule 5: Check individual household members (non-HoH/spouse)
        return cls._check_individual_eligibility(request, persons)
    
    @classmethod
    def _get_married_threshold(cls, num_children: int) -> float:
        """Get EITC threshold for married filing jointly"""
        if num_children == 0:
            return 25511
        elif num_children == 1:
            return 56004
        elif num_children == 2:
            return 62688
        else:  # 3 or more
            return 66819
    
    @classmethod
    def _get_single_threshold(cls, num_children: int) -> float:
        """Get EITC threshold for single filers"""
        if num_children == 0:
            return 18591
        elif num_children == 1:
            return 49084
        elif num_children == 2:
            return 55768
        else:  # 3 or more
            return 59899
    
    @classmethod
    def _get_head_and_spouse_investment(cls, request, persons) -> float:
        """Calculate combined investment income for HoH and Spouse"""
        total = 0.0
        for i, person in enumerate(persons):
            if person.household_member_type in [HouseholdMemberType.HEAD_OF_HOUSEHOLD, HouseholdMemberType.SPOUSE]:
                total += request.income_person_investment_yearly.get(i, 0.0)
        return total
    
    @classmethod
    def _check_individual_eligibility(cls, request, persons) -> bool:
        """
        Rule 5: Check if any individual household member (non-HoH/spouse) qualifies.
        Matches Drools rule: person age 25-64, earned income > 0 and <= 18591,
        and investment income <= 11600 for that person.
        """
        for i, person in enumerate(persons):
            # Skip head of household and spouse
            if person.household_member_type in [HouseholdMemberType.HEAD_OF_HOUSEHOLD, HouseholdMemberType.SPOUSE]:
                continue
            
            # Check age requirement (25-64)
            if not (25 <= person.age < 65):
                continue
            
            # Check investment income for this person
            person_investment = request.income_person_investment_yearly.get(i, 0.0)
            if person_investment > 11600:
                continue
            
            # Check earned income
            person_earned_income = request.income_person_earned_yearly.get(i, 0.0)
            if 0 < person_earned_income <= 18591:
                return True
        
        return False