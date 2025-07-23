"""
Cash Assistance eligibility rule (S2R010)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class CashAssistance(BaseRule):
    program = "S2R010"
    description = "Cash Assistance (HRA) - Financial assistance program with income-based eligibility"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility based on income thresholds that vary by:
        1. Household size
        2. Whether any person is ≤18 or pregnant (higher thresholds)
        """
        persons = request.person
        household_size = len(persons) + request.members_pregnant
        
        # Check if any person is ≤18 or pregnant
        has_child_or_pregnant = any(p.age <= 18 or p.pregnant for p in persons)
        
        # Get monthly income after work expense deduction
        monthly_income = request.income_household_monthly_ca_minus_work_expense
        
        # Get appropriate threshold based on household size and composition
        if has_child_or_pregnant:
            threshold = cls._get_child_pregnant_threshold(household_size)
        else:
            threshold = cls._get_general_threshold(household_size)
        
        return monthly_income < threshold
    
    @classmethod
    def _get_child_pregnant_threshold(cls, household_size: int) -> float:
        """Get income threshold for households with children or pregnant members"""
        thresholds = {
            1: 460.10,
            2: 574.50,
            3: 789.00,
            4: 951.70,
            5: 1119.70,
            6: 1238.20,
            7: 1357.70,
            8: 1455.20
        }
        
        # For households larger than 8, extrapolate
        if household_size > 8:
            return thresholds[8] + (household_size - 8) * 119.50
        
        return thresholds.get(household_size, thresholds[1])
    
    @classmethod
    def _get_general_threshold(cls, household_size: int) -> float:
        """Get income threshold for general households"""
        thresholds = {
            1: 398.10,
            2: 541.50,
            3: 675.00,
            4: 813.70,
            5: 955.70,
            6: 1063.20,
            7: 1214.70,
            8: 1330.20
        }
        
        # For households larger than 8, extrapolate
        if household_size > 8:
            return thresholds[8] + (household_size - 8) * 115.50
        
        return thresholds.get(household_size, thresholds[1])