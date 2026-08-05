"""
NYC Ferry Discount eligibility rule (S2R059)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class NYCFerryDiscount(BaseRule):
    program = "S2R059"
    description = "NYC Ferry Discount - Reduced fare for eligible riders"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires at least one person who is:
        1. Aged 65 or older, or
        2. Blind, or
        3. Disabled, or
        4. A student aged 14-18
        """
        return any(
            p.age >= 65
            or p.blind
            or p.disabled
            or (p.student and 14 <= p.age <= 18)
            for p in request.person
        )
