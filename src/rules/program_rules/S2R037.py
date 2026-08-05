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
        Eligibility requires at least one person who is disabled, blind, or
        aged 65+ and meets one of:

        1. That same person receives Medicaid or disability-related Medicaid
        2. Household yearly income at or below thresholds by household size
        3. That person's yearly earned income at or below the 1-person household limit
        """
        persons = request.person
        household_size = len(persons)

        for person in persons:
            if (person.disabled or person.blind or person.age >= 65) and (
                person.benefits_medicaid or person.benefits_medicaid_disability
            ):
                return True

        has_eligible_person = any(
            p.disabled or p.blind or p.age >= 65 for p in persons
        )
        if not has_eligible_person:
            return False

        income_thresholds = {
            1: 22025,
            2: 29864,
            3: 37702,
            4: 45540,
            5: 53379,
            6: 61217,
            7: 69056,
            8: 76894,
        }

        if household_size in income_thresholds:
            if (
                request.income_household_total_yearly
                <= income_thresholds[household_size]
            ):
                return True

        for i, person in enumerate(persons):
            if person.disabled or person.blind or person.age >= 65:
                earned_yearly = request.income_person_earned_yearly.get(i, 0.0)
                if earned_yearly <= income_thresholds[1]:
                    return True

        return False
