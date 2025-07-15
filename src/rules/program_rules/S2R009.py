"""
School breakfast and lunch program eligibility rule (S2R009)
"""

from __future__ import annotations

from src.rules.base_rule import BaseRule
from src.rules.registry import register_rule


@register_rule
class SchoolMealsRule(BaseRule):
    program = "S2R009"
    description = "School Breakfast and Lunch - Free meals for NYC public school students"

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