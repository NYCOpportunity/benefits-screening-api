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

    # Household(members == N) thresholds from S2R025.drl
    INCOME_THRESHOLDS = {
        1: 19563,
        2: 26438,
        3: 33313,
        4: 40188,
        5: 47063,
        6: 53938,
        7: 60813,
        8: 67688,
    }

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. At least one person aged 55+ who is unemployed
        2. Total yearly household income at or below the threshold for household size
        """
        persons = request.person
        household_size = len(persons)

        if not any(person.age >= 55 and person.unemployed for person in persons):
            return False

        threshold = cls.INCOME_THRESHOLDS.get(household_size)
        if threshold is None:
            return False

        return request.income_household_total_yearly <= threshold
