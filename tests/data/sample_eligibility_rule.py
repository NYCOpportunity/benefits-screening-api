from src.validation.validate_request import validate_request
from src.models.schemas import EligibilityRequest
import json

def sample_eligibility_rule() -> EligibilityRequest:

    file_path = 'tests/data/eligibility-program-test-payload.json'
    with open(file_path, 'r') as f:
        data = json.load(f)
    is_valid, eligibility_request, error_messages = validate_request(data)
    if not is_valid:
        raise ValueError(f"Sample data validation failed: {error_messages}")
    return eligibility_request

    