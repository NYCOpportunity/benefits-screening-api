from __future__ import annotations

"""
Provides the abstract base class that all benefit eligibility rules must inherit from.

Each rule must implement the `evaluate` method which returns `True` if the
`EligibilityRequest` satisfies the rule (meaning the household/persons are
eligible for the corresponding benefit program) and `False` otherwise.

Sub-classes should set the `program` attribute to the `BenefitProgram` value
that they correspond to.  A short human-readable `description` can also be set
for documentation and debugging purposes.
"""

from abc import ABC, abstractmethod
from typing import ClassVar

from ..models.schemas import EligibilityRequest
from ..models.enums import BenefitProgram


class BaseRule(ABC):
    """Abstract base class for all eligibility rules."""

    #: The benefit program that this rule determines eligibility for.
    program: ClassVar[BenefitProgram]

    #: Optional human-readable description shown when debugging.
    description: ClassVar[str] = ""

    @classmethod
    @abstractmethod
    def evaluate(cls, request: EligibilityRequest) -> bool:  # pragma: no cover
        """Return *True* if *request* is eligible for *program*.

        Concrete subclasses **must** implement this method.
        """
        raise NotImplementedError 