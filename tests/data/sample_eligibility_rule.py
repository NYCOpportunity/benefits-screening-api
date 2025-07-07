from src.validation.validate_request import validate_request
from src.models.schemas import EligibilityRequest
import json

def sample_eligibility_rule() -> EligibilityRequest:

    userInfo = 'tests/data/eligibility-program-test-payload.json' 
    data = json.load(userInfo)
    eligibility_request = validate_request(data)
    return eligibility_request

