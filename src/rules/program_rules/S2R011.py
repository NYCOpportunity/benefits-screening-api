"""
Qualified Health Plans eligibility rule (S2R011)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class QualifiedHealthPlans(BaseRule):
    program = "S2R011"
    description = "Qualified Health Plans (NY State of Health) - Healthcare marketplace plans"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        All households are eligible for this program.
        No conditions need to be checked.
        """
        return True