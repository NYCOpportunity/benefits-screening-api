"""
Supplemental Nutrition Assistance Program eligibility rule (S2R007)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule
from src.models.enums import IncomeType, HouseholdMemberType


@register_rule
class SupplementalNutritionAssistanceProgram(BaseRule):
    program = "S2R007"
    description = "Supplemental Nutrition Assistance Program (SNAP/Food Stamps) (HRA) - Food assistance program"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        SNAP eligibility has multiple pathways:
        1. All household members receive SSI or Cash Assistance (categorical eligibility)
        2. Income under 200% FPL with special circumstances (elderly/disabled/child care expenses)
        3. Income under 150% FPL with earned income
        4. Income under 130% FPL for all others
        """
        household = request.household[0]
        persons = request.person
        household_size = len(persons) + request.members_pregnant
        
        # Check categorical eligibility (all members have SSI or Cash Assistance)
        if cls._check_categorical_eligibility(request, persons):
            return True
        
        # Calculate SNAP budget
        snap_income = cls._calculate_snap_income(request)
        
        # Determine which FPL threshold applies
        fpl_multiplier = cls._determine_fpl_multiplier(request, persons)
        
        # Get FPL limit for household size
        fpl_limit = cls._get_fpl_limit(household_size, fpl_multiplier)
        
        # Compare income to limit
        return snap_income <= fpl_limit
    
    @classmethod
    def _check_categorical_eligibility(cls, request, persons) -> bool:
        """Check if all household members have SSI or Cash Assistance"""
        if len(persons) == 0:
            return False
            
        # Check if all persons have either SSI or Cash Assistance
        all_have_benefits = True
        for person in persons:
            has_ssi = False
            has_cash_assistance = False
            
            for income in person.incomes:
                if income.type == IncomeType.SSI:
                    has_ssi = True
                elif income.type == IncomeType.CASH_ASSISTANCE:
                    has_cash_assistance = True
            
            if not (has_ssi or has_cash_assistance):
                all_have_benefits = False
                break
        
        return all_have_benefits
    
    @classmethod
    def _calculate_snap_income(cls, request) -> float:
        """Calculate SNAP net income after all deductions"""
        # Start with gross income
        gross_income = (request.income_household_wage_self_employment_monthly + 
                       request.income_household_boarder_monthly +
                       request.income_household_unearned_monthly -
                       request.expense_household_child_support_monthly)
        
        # Calculate deductions
        deductions = 0.0
        
        # 20% earned income deduction
        earned_income = (request.income_household_wage_self_employment_monthly + 
                        request.income_household_boarder_monthly)
        deductions += earned_income * 0.20
        
        # Standard deduction based on household size
        household_size = len(request.person) + request.members_pregnant
        if household_size <= 3:
            deductions += 198
        elif household_size == 4:
            deductions += 208
        elif household_size == 5:
            deductions += 244
        else:
            deductions += 279
        
        # Homeless deduction if applicable
        household = request.household[0]
        if household.living_shelter:
            deductions += 179.66
        
        # Dependent care expenses
        deductions += request.expense_household_child_dependent_care_monthly
        
        # Medical expenses (only amount over $35 counts)
        if request.expense_household_medical_monthly > 35:
            deductions += request.expense_household_medical_monthly - 35
        
        # Calculate adjusted income
        adjusted_income = gross_income - deductions
        if adjusted_income < 0:
            adjusted_income = 0
        
        # Calculate excess shelter costs
        shelter_costs = request.expense_household_rent_mortgage_monthly + 992  # $992 utility allowance
        excess_shelter = shelter_costs - (adjusted_income / 2)
        if excess_shelter < 0:
            excess_shelter = 0
        
        # Final SNAP net income
        net_income = adjusted_income - excess_shelter
        if net_income < 0:
            net_income = 0
        
        return net_income
    
    @classmethod
    def _determine_fpl_multiplier(cls, request, persons) -> float:
        """Determine which FPL multiplier applies based on household circumstances"""
        # Check for 200% FPL conditions
        has_child_care_expenses = request.expense_household_has_child_or_dependent_care
        has_elderly = any(p.age >= 60 for p in persons)
        has_disabled_or_blind = any(p.disabled or p.blind for p in persons)
        
        if has_child_care_expenses or has_elderly or has_disabled_or_blind:
            return 2.0
        
        # Check for 150% FPL condition (has earned income)
        has_earned_income = (request.income_household_wage_self_employment_monthly > 0 or
                           request.income_household_boarder_monthly > 0)
        
        if has_earned_income:
            return 1.5
        
        # Default to 130% FPL
        return 1.3
    
    @classmethod
    def _get_fpl_limit(cls, household_size: int, multiplier: float) -> float:
        """Get the FPL limit for given household size and multiplier"""
        # 2024 FPL monthly amounts (approximate)
        base_fpl = {
            1: 1255,
            2: 1704,
            3: 2152,
            4: 2600,
            5: 3049,
            6: 3497,
            7: 3945,
            8: 4394
        }
        
        # For households larger than 8, add $449 per additional person
        if household_size > 8:
            limit = base_fpl[8] + (household_size - 8) * 449
        else:
            limit = base_fpl.get(household_size, base_fpl[1])
        
        return limit * multiplier