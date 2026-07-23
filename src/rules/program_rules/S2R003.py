"""
Infants & Toddlers eligibility rule (S2R003)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule
from src.models.enums import HouseholdMemberType, IncomeType


@register_rule
class InfantsToddlers(BaseRule):
    program = "S2R003"
    description = "Infants & Toddlers (DOE) - Early intervention services for children under 3 years old"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Multiple eligibility pathways for children under 3:
        1. Foster children under 3
        2. Children under 3 with HoH/spouse receiving SSI or Cash Assistance
        3. Children/stepchildren under 3 with household income below threshold
        4. Other children under 3 with individual income below threshold
        """
        persons = request.person
        
        # Check each person for eligibility
        for i, person in enumerate(persons):
            if person.age >= 3:
                continue
                
            # Pathway 1: Foster child under 3
            if person.household_member_type == HouseholdMemberType.FOSTER_CHILD:
                return True
            
            # Pathway 2: Person under 3 with HoH/spouse receiving SSI or Cash Assistance
            if cls._head_or_spouse_has_benefits(persons):
                return True
            
            # Pathway 3: Child/stepchild with household income check
            if person.household_member_type in [HouseholdMemberType.CHILD, HouseholdMemberType.STEP_CHILD]:
                adults_children_income = request.income_adults_children_total_monthly
                
                # Calculate count of persons included in the income calculation for threshold lookup
                adults_children_count = cls._count_adults_children(request)
                
                income_threshold = cls._get_income_threshold(adults_children_count)
                
                if income_threshold > 0 and adults_children_income <= income_threshold:
                    return True
            
            # Pathway 4: Other children with individual income check
            if person.household_member_type not in [HouseholdMemberType.CHILD, HouseholdMemberType.STEP_CHILD]:
                person_monthly_income = request.income_person_monthly.get(i, 0.0)
                if person_monthly_income <= 4301.0:
                    return True
        
        return False
    
    @classmethod
    def _head_or_spouse_has_benefits(cls, persons) -> bool:
        """Check if head of household or spouse has SSI or Cash Assistance"""
        for person in persons:
            if person.household_member_type in [HouseholdMemberType.HEAD_OF_HOUSEHOLD, HouseholdMemberType.SPOUSE]:
                for income in person.incomes:
                    if income.type in [IncomeType.SSI, IncomeType.CASH_ASSISTANCE]:
                        return True
        return False
    
    @classmethod
    def _count_adults_children(cls, request) -> int:
        """
        Count persons included in adults_children_total_monthly calculation.
        Matches Drools rule: (headOfHousehold == true || headOfHouseholdRelation == "Spouse" || age < 18)
        """
        count = 0
        persons = request.person
        
        for person in persons:
            is_hoh = person.household_member_type == HouseholdMemberType.HEAD_OF_HOUSEHOLD
            is_spouse = person.household_member_type == HouseholdMemberType.SPOUSE
            is_under_18 = person.age < 18
            
            if is_hoh or is_spouse or is_under_18:
                count += 1
        
        return count
    
    @classmethod
    def _get_income_threshold(cls, adults_children_count: int) -> float:
        """
        Get income threshold based on count of adults and children in the household.
        """
        thresholds = {
            2: 5624.0,
            3: 6948.0,
            4: 8271.0,
            5: 9594.0,
            6: 10918.0,
            7: 11166.0,
            8: 11414.0
        }
        
        # For households larger than 8, use the 8-member threshold
        if adults_children_count > 8:
            return thresholds[8]
        
        # For single member households, no threshold defined in rules
        if adults_children_count < 2:
            return 0.0
        
        return thresholds.get(adults_children_count, thresholds[2])