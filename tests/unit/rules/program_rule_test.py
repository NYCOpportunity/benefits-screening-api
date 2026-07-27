import json
import pathlib
import pytest

from src.models.schemas import AggregateEligibilityRequest
from src.rules.registry import get_rules
from src.validation.validate_request import validate_request

PAYLOADS_DIR = pathlib.Path(__file__).parents[2] / "data" / "payloads"


def get_test_cases():
    rules_by_program = {rule_cls.program: rule_cls for rule_cls in get_rules()}
    test_cases = []

    for payload_folder in sorted(PAYLOADS_DIR.iterdir()):
        if not payload_folder.is_dir():
            continue

        program_code = payload_folder.name.split("_")[0]
        cls = rules_by_program[program_code]

        for label in ("true", "false"):
            folder = payload_folder / label
            if not folder.exists():
                continue

            for json_file in sorted(folder.rglob("*.json")):
                expected = label == "true"  # Convert from str to bool
                test_id = f"{program_code}-{json_file.relative_to(payload_folder).as_posix()}"
                test_cases.append(
                    pytest.param(
                        program_code,
                        cls,
                        json_file,
                        expected,
                        id=test_id,
                    )
                )

    return test_cases


@pytest.mark.parametrize(
    "program_code,cls,json_file,expected",
    get_test_cases(),
)
def test_all_program_rules(program_code, cls, json_file, expected):
    with open(json_file) as f:
        payload = json.load(f)

    is_valid, eligibility_request, error_messages = validate_request(payload)
    assert is_valid, f"Sample data validation failed: {error_messages}"

    aggregate_eligibility_request = AggregateEligibilityRequest.from_eligibility_request(
        eligibility_request
    )
    result = cls.evaluate(aggregate_eligibility_request)

    assert result is expected, (
        f"Benefit {program_code} ({json_file.name}): expected {expected}, got {result}"
    )
