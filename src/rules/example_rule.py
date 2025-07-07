"""
Example (placeholder) eligibility rule to show the structure of inheritance
"""

from __future__ import annotations

from .base_rule import BaseRule
from ..models.enums import BenefitProgram
from .registry import register_rule


@register_rule
class PlaceholderSnapRule(BaseRule):
    program = BenefitProgram.SNAP
    description = "Demonstration placeholder for SNAP eligibility. Always False."


    # This takes an EligibilityRequest and returns true/false if person is eligible. 
    @classmethod
    def evaluate(cls, request):
        # TODO: implement SNAP eligibility logic
        return False 