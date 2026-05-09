"""
Medicaid Transportation eligibility rule (S2R060)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class MedicaidTransportation(BaseRule):
    program = "S2R060"
    description = "Medicaid Transportation - Transportation assistance for Medicaid recipients"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires at least one person with Medicaid or disability
        Medicaid benefits.
        """
        return any(
            person.benefits_medicaid or person.benefits_medicaid_disability
            for person in request.person
        )
