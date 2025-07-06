from typing import List
from ..models.schemas import EligibilityRequest
from .registry import get_rules
from ..models.enums import BenefitProgram


def calculate_eligibility(eligibility_request: EligibilityRequest) -> List[BenefitProgram]:
    """Return a list of benefit programs the *eligibility_request* qualifies for.

    The function iterates through all registered rules and evaluates them
    against the provided request.  A program is added to the result list when
    its corresponding rule evaluates to *True*.
    """

    eligible_programs: List[BenefitProgram] = []

    for rule_cls in get_rules():
        try:
            if rule_cls.evaluate(eligibility_request):
                eligible_programs.append(rule_cls.program)
        except Exception as exc:  # pragma: no cover
            # Optionally log the exception here.  For now we fail closed (i.e. not eligible)
            # so that a broken rule does not grant benefits in error.
            print(f"[WARN] Rule '{rule_cls.__name__}' raised an exception during evaluation: {exc}")

    return eligible_programs


# NOTE: Individual rule modules are imported elsewhere (see their own files) and
# register themselves with the registry via the @register_rule decorator.  Make
# sure to import new rule modules in `src/rules/__init__.py` or another import
# path executed at runtime so they are available during evaluation.



