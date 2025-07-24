from __future__ import annotations

"""
Provides the abstract base class that all benefit eligibility rules must inherit from.

Each rule must implement the `evaluate` method which returns `True` if the
`EligibilityRequest` satisfies the rule (meaning the household/persons are
eligible for the corresponding benefit program) and `False` otherwise.

The `EligibilityRequest` is just the validated information sent from the user questionaire.

Sub-classes should set the `program` attribute to the `BenefitProgram` value
that they correspond to.  A short human-readable `description` can also be set
for documentation and debugging purposes. 
(This can be modified for future to be compatible with Swagger documentation).
"""

from abc import ABC, abstractmethod
from typing import ClassVar

from src.models.schemas import AggregateEligibilityRequest


class BaseRule(ABC):
    """Abstract base class for all eligibility rules."""

    #: The program code ex S2R037
    program: ClassVar[str]


    #: Optional human-readable description shown when debugging.
    description: ClassVar[str] = ""

    @classmethod
    @abstractmethod
    def evaluate(cls, request: AggregateEligibilityRequest) -> bool: 
        """Return *True* if *request* is eligible for *program*.

        """
        raise NotImplementedError 