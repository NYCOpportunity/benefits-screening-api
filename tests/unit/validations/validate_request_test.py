import json
from pathlib import Path

from src.validation.validate_request import validate_request

current_dir = Path(__file__).parent
data_payloads_dir = current_dir.parent.parent / "data" / "payloads"

def test_valid_payload():
    file_path = data_payloads_dir / "eligibility-program-test-payload.json"
    with open(file_path) as f:
        data = json.load(f)
    is_valid, _, result = validate_request(data)
    assert is_valid is True
    assert result == "Validation successful"

def test_invalid_payload():
    file_path = data_payloads_dir / "invalid-eligibility-payload.json"
    with open(file_path) as f:
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