# control the main flow. this will bring together all components of the application.

# Ensure the project root is on `sys.path` **before** importing other modules when
# this file is executed directly (e.g., `python src/main.py`).
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.append(str(_PROJECT_ROOT))

# Ensure absolute imports via the top-level `src` package
from src.validation.validate_request import validate_request
from src.rules.calculate_eligibility import calculate_eligibility
import json
from src.models.schemas import AggregateEligibilityRequest

def main():
    '''
    STEP 1: Validate the request
    '''

    userInfo = 'tests/data/eligibility-program-test-payload.json' # TODO: read from aws gateway
    try: 
        with open(userInfo, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Test file not found at {userInfo}")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in test file: {e}")
        return
    is_valid, eligibility_request, error_messages = validate_request(data)
    print(f"is_valid: {is_valid}")
    print(f"eligibility_request: {eligibility_request}") #eligibility request is the validated request
    print(f"error_messages: {error_messages}")

    '''
    STEP 2: Calculate which programs the user is eligible for
    '''
    aggregate_eligibility_request = AggregateEligibilityRequest.from_eligibility_request(eligibility_request)
    eligibility_programs = calculate_eligibility(aggregate_eligibility_request)
    
    print(f"\nEligible programs: {eligibility_programs}")
    print(f"Total programs eligible: {len(eligibility_programs)}")
    
    



if __name__ == "__main__":
    main()


