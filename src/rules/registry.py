"""Registry that stores all instantiated eligibility rules.

Rules register themselves when their module is imported.  The calculate_eligibility
function can then fetch the list of rules from this module.
"""

from __future__ import annotations

from typing import List, Sequence, Type

from .base_rule import BaseRule


# Internal list of rule *classes* (not instances) so we don't repeatedly
# instantiate them during a single evaluation run.
_rules: List[Type[BaseRule]] = []


def register_rule(rule_cls: Type[BaseRule]) -> Type[BaseRule]:
    """Decorator or helper used by individual rule modules to register themselves."""
    if rule_cls not in _rules:
        _rules.append(rule_cls)
    return rule_cls


def get_rules() -> Sequence[Type[BaseRule]]:
    """Return an immutable sequence of all registered rule classes."""
    return tuple(_rules) 