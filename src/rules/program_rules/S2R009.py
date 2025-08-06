"""
Comprehensive After School System of NYC eligibility rule (S2R009)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class ComprehensiveAfterSchoolSystem(BaseRule):
    program = "S2R009"
    description = "Comprehensive After School System of NYC (COMPASS NYC) (DYCD) - After school programs for students"

    @classmethod
    def evaluate(cls, request) -> bool:
        """
        Eligibility requires:
        1. NYC residence (assumed for all requests)
        2. At least one person aged 5-21 who is a student
        """
        persons = request.person
        
        # Check for student aged 5-21
        has_eligible_student = any(
            5 <= p.age <= 21 and p.student 
            for p in persons
        )
        
        return has_eligible_student