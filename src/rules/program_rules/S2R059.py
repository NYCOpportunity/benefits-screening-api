"""
NYC Ferry Discount eligibility rule (S2R059)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class NYCFerryDiscount(BaseRule):
    program = "S2R059"
    description = "NYC Ferry Discount - Discounted ferry fare for older adults, disabled riders, and eligible students"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires at least one person who is 65+, blind, disabled,
        or a student age 14-18.
        """
        return any(
            person.age >= 65
            or person.blind
            or person.disabled
            or (person.student and 14 <= person.age <= 18)
            for person in request.person
        )
