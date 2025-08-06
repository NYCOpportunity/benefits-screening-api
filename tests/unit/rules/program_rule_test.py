# Import rule modules to ensure they are registered
from tests.data.sample_eligibility_rule import sample_eligibility_rule
from src.rules.registry import get_rules


def test_all_program_rules():

    eligibility_request = sample_eligibility_rule()
    all_rules = get_rules()

    # Dynamically include all registered programs with a default expected
    # outcome of False.  Override specific programs below when their expected
    # result differs. (This can eventually be moved to a json/yaml in the test data folder)
    expected_outcomes = {rule.program: False for rule in all_rules}

    # Ensure at least one rule is registered to confirm discovery is working
    assert len(all_rules) > 0, "No rules were found in the registry."

    registered_programs = {rule.program for rule in all_rules}
    expected_programs = set(expected_outcomes.keys())

    assert registered_programs == expected_programs, (
        f"Mismatch between registered rules and expected outcomes. "
        f"Missing from test: {registered_programs - expected_programs}. "
        f"Not registered: {expected_programs - registered_programs}."
    )

    for rule in all_rules:
        program_code = rule.program
        expected_result = expected_outcomes[program_code]
        actual_result = rule.evaluate(eligibility_request)

        assert actual_result == expected_result, (
            f"Rule '{program_code}' failed for sample data. "
            f"Expected: {expected_result}, Got: {actual_result}"
        )