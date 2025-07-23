"""
Home Care Services Program eligibility rule (S2R037)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class HomeCareServicesProgram(BaseRule):
    program = "S2R037"
    description = "Home Care Services Program (HRA) - In-home care services for individuals with Medicaid"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. Household is in NYC
        2. At least one person has Medicaid benefits
        """
        household = request.household[0]
        persons = request.person
        
        # Check condition 1: Must be in NYC
        # Since the API is for NYC benefits, we assume all requests are from NYC
        # In a real implementation, this might check a specific field
        
        # Check condition 2: At least one person has Medicaid
        has_medicaid = any(p.benefits_medicaid for p in persons)
        
        return has_medicaid