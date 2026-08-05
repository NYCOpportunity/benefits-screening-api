"""
Nurse-Family Partnership eligibility rule (S2R029)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class NurseFamilyPartnership(BaseRule):
    program = "S2R029"
    description = "Nurse-Family Partnership (DOHMH) - Prenatal and postnatal support for first-time mothers"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires at least one pregnant person and either:
        1. That pregnant person receives Medicaid or disability-related Medicaid, or
        2. Household yearly income at or below thresholds based on members plus pregnant
        """
        persons = request.person

        for person in persons:
            if person.pregnant and (
                person.benefits_medicaid or person.benefits_medicaid_disability
            ):
                return True

        has_pregnant = any(p.pregnant for p in persons)
        if not has_pregnant:
            return False

        members_plus_pregnant = request.members_plus_pregnant
        income_thresholds = {
            1: 34900,
            2: 47165,
            3: 59430,
            4: 71695,
            5: 83960,
            6: 96225,
            7: 108490,
            8: 120755,
            9: 133020,
        }

        if members_plus_pregnant in income_thresholds:
            return (
                request.income_household_total_yearly
                <= income_thresholds[members_plus_pregnant]
            )

        return False
