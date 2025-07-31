import json
import pytest
from pathlib import Path
from src.main import main


class TestLambdaHandler:
    """End-to-end tests for the Lambda handler function."""
    
    def test_lambda_handler_with_valid_payload(self, test_payload):
        """Test Lambda handler with valid test payload."""
        # Simulate API Gateway event
        event = {'body': json.dumps(test_payload)}
        
        # Call the Lambda handler
        result = main(event, None)
        
        # Verify response structure
        assert result['statusCode'] == 200
        assert 'headers' in result
        assert result['headers']['Content-Type'] == 'application/json'
        
        # Parse response body
        body = json.loads(result['body'])
        assert body['success'] is True
        assert 'eligible_programs' in body
        assert 'total_programs_eligible' in body
        assert isinstance(body['eligible_programs'], list)
        assert body['total_programs_eligible'] == len(body['eligible_programs'])
    
    def test_lambda_handler_with_json_string_body(self, test_payload):
        """Test Lambda handler when body is already a JSON string."""
        event = {'body': json.dumps(test_payload)}
        result = main(event, None)
        
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
    
    def test_lambda_handler_with_dict_body(self, test_payload):
        """Test Lambda handler when body is a dictionary."""
        event = {'body': test_payload}
        result = main(event, None)
        
        assert result['statusCode'] == 200
        body = json.loads(result['body'])
        assert body['success'] is True
    
    def test_lambda_handler_with_invalid_json(self):
        """Test Lambda handler with invalid JSON."""
        event = {'body': 'invalid json'}
        result = main(event, None)
        
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert body['success'] is False
        assert 'Invalid JSON in request body' in body['errors'][0]
    
    def test_lambda_handler_with_empty_body(self):
        """Test Lambda handler with empty body."""
        event = {'body': '{}'}
        result = main(event, None)
        
        assert result['statusCode'] == 400
        body = json.loads(result['body'])
        assert body['success'] is False
        assert 'errors' in body