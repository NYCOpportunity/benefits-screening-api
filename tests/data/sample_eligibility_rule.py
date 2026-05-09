from src.validation.validate_request import validate_request
from src.models.schemas import AggregateEligibilityRequest
import json
from pathlib import Path


def sample_eligibility_rule() -> AggregateEligibilityRequest:

    current_dir = Path(__file__).parent
    file_path = current_dir / "payloads" / "eligibility-program-test-payload.json"
    with open(file_path, 'r') as f:
        data = json.load(f)
    is_valid, eligibility_request, error_messages = validate_request(data)
    if not is_valid:
        raise ValueError(f"Sample data validation failed: {error_messages}")
    return AggregateEligibilityRequest.from_eligibility_request(eligibility_request)
