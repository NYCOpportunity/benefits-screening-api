"""
Affordable Connectivity Program (ACP) eligibility rule (S2R053)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class ACPRule(BaseRule):
    program = "S2R053"
    description = "Affordable Connectivity Program - Internet service discount (Program closed as of Feb 8, 2024)"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        NOTE: This program is no longer accepting new applications as of February 8, 2024.
        Returning False for all requests.
        
        Original eligibility would have required NYC residence and ANY of:
        1. At least one person has Medicaid benefits
        2. Household has certain government benefits
        3. Full-time student aged 21 or under
        4. Household income below thresholds based on household size
        """
        # Program is closed - always return False
        return False