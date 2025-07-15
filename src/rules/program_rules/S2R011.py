"""
Universal eligibility program (S2R011)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class UniversalEligibilityRule(BaseRule):
    program = "S2R011"
    description = "Universal program - all households may be eligible"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        All households are eligible for this program.
        No conditions need to be checked.
        """
        return True