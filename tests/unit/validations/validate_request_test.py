import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / 'src'
sys.path.insert(0, str(SRC_PATH))

from validation.validate_request import validate_request

def test_valid_payload():
    with open('tests/data/eligibility-program-test-payload.json') as f:
        data = json.load(f)
    is_valid, result = validate_request(data)
    assert is_valid is True
    assert result == "Validation successful"

def test_invalid_payload():
    with open('tests/data/invalid-eligibility-payload.json') as f:
        data = json.load(f)
    is_valid, result = validate_request(data)
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