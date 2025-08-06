import json
from src.validation.validate_request import validate_request
from src.rules.calculate_eligibility import calculate_eligibility
from src.models.schemas import AggregateEligibilityRequest


def main(event, context):
    """
    AWS Lambda handler for benefits screening API.
    
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
        
        # Validate the request
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
        
        # Calculate eligible programs
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
        print("internal server error:", e)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'success': False,
                'errors': [f'Internal server error']
            })
        }
