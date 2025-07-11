import json
from src.validation.validate_request import validate_request

def test_valid_payload():
    with open('tests/data/eligibility-program-test-payload.json') as f:
        data = json.load(f)
    is_valid, _, result = validate_request(data)
    assert is_valid is True
    assert result == "Validation successful"

def test_invalid_payload():
    with open('tests/data/invalid-eligibility-payload.json') as f:
        data = json.load(f)
    is_valid, _, result = validate_request(data)
    assert is_valid is False
    print(result)
    assert result != "Validation successful"

if __name__ == "__main__":
    print("Running validation tests...")
    print("=" * 50)
    test_valid_payload()
    print("✅ Valid payload test passed!")
    print()
    test_invalid_payload()
    print("✅ Invalid payload test passed!")
    print()
    print("🎉 All validation tests passed!")