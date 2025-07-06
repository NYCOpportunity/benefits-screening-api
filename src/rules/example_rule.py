"""Example (placeholder) eligibility rule.

This rule is *not* intended to be used in production.  It always returns
False but demonstrates the recommended structure.  Replace this with real
rules as program requirements are defined.
"""

from __future__ import annotations

from .base_rule import BaseRule
from ..models.enums import BenefitProgram
from .registry import register_rule


@register_rule
class PlaceholderSnapRule(BaseRule):
    program = BenefitProgram.SNAP
    description = "Demonstration placeholder for SNAP eligibility. Always False."

    @classmethod
    def evaluate(cls, request):
        # TODO: implement SNAP eligibility logic
        return False 