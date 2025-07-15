"""
NYC Free Tax Prep eligibility rule (S2R045)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class FreeTaxPrepRule(BaseRule):
    program = "S2R045"
    description = "NYC Free Tax Prep - Free tax preparation services"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. NYC residence (assumed for all requests)
        2. At least one person aged 18 or older
        """
        persons = request.person
        
        # Check for adult (18+)
        has_adult = any(p.age >= 18 for p in persons)
        
        return has_adult