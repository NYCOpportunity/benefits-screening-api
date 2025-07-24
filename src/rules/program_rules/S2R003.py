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
            
            # Check if HoH or spouse has SSI or Cash Assistance
            if cls._head_or_spouse_has_benefits(persons):
                return True
            
            # Pathway 3: Child/stepchild with household income check
            if person.household_member_type in [HouseholdMemberType.CHILD, HouseholdMemberType.STEP_CHILD]:
                household_size = len(persons) + request.members_pregnant
                income_threshold = cls._get_household_income_threshold(household_size)
                
                if request.income_adults_children_total_monthly <= income_threshold:
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
    def _get_household_income_threshold(cls, household_size: int) -> float:
        """Get income threshold based on household size"""
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
        if household_size > 8:
            return thresholds[8]
        
        # For single member households, no threshold defined in rules
        if household_size < 2:
            return 0.0
        
        return thresholds.get(household_size, thresholds[2])