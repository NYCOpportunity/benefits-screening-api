import json
from typing import Dict, List

from pydantic import ValidationError

from src.validation.parse_request import INVALID_PAYLOAD_MESSAGE, parse_request
from src.rules.calculate_eligibility import calculate_eligibility
from src.models.schemas import AggregateEligibilityRequest
from src.utils.drools_converter import convert_drools_to_api_format


def _success(status_code: int, body: Dict) -> Dict:
    return {'statusCode': status_code, **body}


def _error(status_code: int, errors: List[str]) -> Dict:
    return {'statusCode': status_code, 'errors': errors}


def main(event, context):
    try:
        if not event:
            request_data = {}
        elif isinstance(event, str):
            request_data = json.loads(event)
        else:
            request_data = event

        if isinstance(request_data, list):
            if len(request_data) != 1:
                return _error(400, ['Request body must be a single eligibility submission'])
            request_data = request_data[0]

        if not isinstance(request_data, dict):
            return _error(400, ['Request body must be a JSON object'])

        if 'commands' in request_data:
            converted_data = convert_drools_to_api_format(request_data)
            if not converted_data:
                return _error(400, ['Failed to convert legacy rules engine payload'])
            request_data = converted_data

        try:
            eligibility_request = parse_request(request_data)
        except ValidationError as error:
            print('invalid eligibility request payload:', error)
            return _error(400, [INVALID_PAYLOAD_MESSAGE])

        aggregate_eligibility_request = AggregateEligibilityRequest.from_eligibility_request(
            eligibility_request
        )
        eligibility_programs = calculate_eligibility(aggregate_eligibility_request)

        return _success(200, {'eligiblePrograms': eligibility_programs})

    except json.JSONDecodeError:
        return _error(400, ['Invalid JSON in request body'])
    except Exception as e:
        print('internal server error:', e)
        return _error(500, ['Internal server error'])
