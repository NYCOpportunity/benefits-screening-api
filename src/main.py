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


def lambda_handler(event, context):
    """
    AWS Lambda handler function for benefits screening API.
    
    Args:
        event: API Gateway event containing the request body
        context: Lambda context object
    
    Returns:
        dict: API Gateway response format
    """
    try:
        # Parse request body
        if isinstance(event.get('body'), str):
            request_data = json.loads(event['body'])
        else:
            request_data = event.get('body', {})
        
        # Step 1: Validate the request
        is_valid, eligibility_request, error_messages = validate_request(request_data)
        
        if not is_valid:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'success': False,
                    'errors': error_messages
                })
            }
        
        # Step 2: Calculate which programs the user is eligible for
        aggregate_eligibility_request = AggregateEligibilityRequest.from_eligibility_request(eligibility_request)
        eligibility_programs = calculate_eligibility(aggregate_eligibility_request)
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': True,
                'eligible_programs': eligibility_programs,
                'total_programs_eligible': len(eligibility_programs)
            })
        }
        
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'errors': ['Invalid JSON in request body']
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'errors': [f'Internal server error: {str(e)}']
            })
        }


def main():
    '''
    Test function for local development
    '''
    userInfo = 'tests/data/eligibility-program-test-payload.json'
    try: 
        with open(userInfo, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Test file not found at {userInfo}")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in test file: {e}")
        return
    
    # Simulate API Gateway event
    event = {'body': json.dumps(data)}
    result = lambda_handler(event, None)
    
    print(f"Status Code: {result['statusCode']}")
    print(f"Response: {result['body']}")
    
    



if __name__ == "__main__":
    main()


