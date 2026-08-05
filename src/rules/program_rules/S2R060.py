"""
Affordable Broadband Act eligibility rule (S2R060)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class AffordableBroadbandAct(BaseRule):
    program = "S2R060"
    description = "Affordable Broadband Act - Discounted internet for Medicaid recipients"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires at least one person with Medicaid or
        disability-related Medicaid benefits.
        """
        return any(
            p.benefits_medicaid or p.benefits_medicaid_disability
            for p in request.person
        )
