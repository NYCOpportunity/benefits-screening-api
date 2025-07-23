"""
Older Adult Employment Program eligibility rule (S2R025)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class OlderAdultEmploymentProgram(BaseRule):
    program = "S2R025"
    description = "Older Adult Employment Program (DFTA) - Employment assistance for seniors aged 55+"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. At least one person aged 55+ who is unemployed
        2. Total yearly household income below threshold based on household size
        """
        persons = request.person
        household_size = len(persons) + request.members_pregnant
        
        # Check if any person is 55+ and unemployed
        has_eligible_senior = any(p.age >= 55 and p.unemployed for p in persons)
        
        if not has_eligible_senior:
            return False
        
        # Check income threshold
        yearly_income = request.income_household_total_yearly
        threshold = cls._get_income_threshold(household_size)
        
        return yearly_income <= threshold
    
    @classmethod
    def _get_income_threshold(cls, household_size: int) -> float:
        """Get income threshold based on household size"""
        thresholds = {
            1: 18825,
            2: 25550,
            3: 32275,
            4: 39000,
            5: 45725,
            6: 52450,
            7: 59175,
            8: 65900
        }
        
        # For households larger than 8, add $6,725 per additional person
        if household_size > 8:
            return thresholds[8] + (household_size - 8) * 6725
        
        return thresholds.get(household_size, thresholds[1])