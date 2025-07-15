"""
Example (placeholder) eligibility rule to show the structure of inheritance
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class PlaceholderSnapRule(BaseRule):
    program = "S2R037"
    description = "Demonstration placeholder for SNAP eligibility. Always False."


    # This takes an AggregateEligibilityRequest and returns true/false if person is eligible. 
    @classmethod
    def evaluate(cls, request):
        # TODO: implement SNAP eligibility logic
        return False 