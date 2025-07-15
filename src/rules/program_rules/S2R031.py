"""
NYC Care health access program eligibility rule (S2R031)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class NYCCareRule(BaseRule):
    program = "S2R031"
    description = "NYC Care - Low-cost healthcare for those without insurance"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. NYC residence (assumed for all requests)
        2. At least one person without Medicaid benefits
        3. Household monthly income below thresholds based on household size
        """
        persons = request.person
        household_size = len(persons)
        
        # Check for person without Medicaid
        has_uninsured = any(
            not p.benefits_medicaid and not p.benefits_medicaid_disability
            for p in persons
        )
        
        if not has_uninsured:
            return False
        
        # Income thresholds by household size
        income_thresholds = {
            1: 2799,
            2: 3799,
            3: 4799,
            4: 5598,
            5: 6798,
            6: 7798,
            7: 8798,
            8: 9798
        }
        
        # Check income eligibility
        if household_size in income_thresholds:
            if request.income_household_total_monthly <= income_thresholds[household_size]:
                return True
        
        return False