"""
Youth workforce development program eligibility rule (S2R036)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule
from src.models.enums import HouseholdMemberType


@register_rule
class YouthWorkforceRule(BaseRule):
    program = "S2R036"
    description = "Youth Workforce Development - Job training for unemployed youth not in school"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires NYC residence and unemployed youth aged 16-24 not in school who meet ANY of:
        1. Lives in a shelter
        2. Is in foster care
        3. Is disabled or blind
        4. Is pregnant or a parent
        5. Household receives Cash Assistance or SSI
        6. Household income below thresholds based on household size
        """
        household = request.household[0]
        persons = request.person
        household_size = len(persons)
        
        # Find eligible youth (16-24, not student, unemployed)
        eligible_youth = [
            p for p in persons 
            if 16 <= p.age <= 24 and not p.student and p.unemployed
        ]
        
        if not eligible_youth:
            return False
        
        # Check condition 1: Lives in shelter
        if household.living_shelter:
            return True
        
        # Check condition 2: Foster care
        for youth in eligible_youth:
            if youth.household_member_type == HouseholdMemberType.FOSTER_CHILD:
                return True
            # Check if youth is head of household with foster parent
            if (youth.household_member_type == HouseholdMemberType.HEAD_OF_HOUSEHOLD and
                any(p.household_member_type == HouseholdMemberType.FOSTER_PARENT for p in persons)):
                return True
        
        # Check condition 3: Disabled or blind
        if any(youth.disabled or youth.blind for youth in eligible_youth):
            return True
        
        # Check condition 4: Pregnant or parent
        for youth in eligible_youth:
            if youth.pregnant:
                return True
            # Check if youth is a parent (has children in household)
            if youth.household_member_type == HouseholdMemberType.HEAD_OF_HOUSEHOLD:
                if any(p.household_member_type in [HouseholdMemberType.CHILD, HouseholdMemberType.STEP_CHILD] for p in persons):
                    return True
        
        # Check condition 5: Cash Assistance or SSI
        if request.income_household_has_cash_assistance or request.income_household_has_ssi:
            return True
        
        # Check condition 6: Income thresholds
        income_thresholds = {
            1: 15060,
            2: 20440,
            3: 25820,
            4: 31200,
            5: 36580,
            6: 41960,
            7: 47340,
            8: 52720
        }
        
        if household_size in income_thresholds:
            if request.income_household_total_yearly <= income_thresholds[household_size]:
                return True
        
        return False