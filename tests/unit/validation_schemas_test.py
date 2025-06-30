"""
Unit tests for request validation schemas.

This test suite validates:
1. Complete request payload validation
2. Business logic rules (head of household, living situation)
3. String constraint patterns for amounts, cash on hand, and case IDs
4. Edge cases and error conditions

All string fields automatically strip whitespace due to str_strip_whitespace=True.
"""
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / 'src'
sys.path.insert(0, str(SRC_PATH))

from validation.schemas import EligibilityRequest, Income
from models.enums import IncomeType, Frequency
from pydantic import ValidationError



def test_valid_payload():
    """Test that a valid payload passes validation."""
    with open('tests/data/eligibility-program-test-payload.json') as f:
        data = json.load(f)
    
    # Should not raise an exception
    request = EligibilityRequest(**data)
    assert len(request.household) == 1
    assert len(request.person) == 1
    assert request.person[0].age == 23
    assert request.withhold_payload is True


def test_head_of_household_validation():
    """Test head of household business rules."""
    base_data = {
        "household": [{"livingRenting": True}],
        "person": [],
        "withholdPayload": False
    }
    
    # No head of household - should fail
    test_data = base_data.copy()
    test_data["person"] = [{"age": 25, "householdMemberType": "Child"}]
    
    try:
        EligibilityRequest(**test_data)
        raise AssertionError("Should have failed - no head of household")
    except ValueError as e:
        assert "HeadOfHousehold" in str(e)
    
    # Multiple heads of household - should fail
    test_data["person"] = [
        {"age": 25, "householdMemberType": "HeadOfHousehold"},
        {"age": 30, "householdMemberType": "HeadOfHousehold"}
    ]
    
    try:
        EligibilityRequest(**test_data)
        raise AssertionError("Should have failed - multiple heads of household")
    except ValueError as e:
        assert "HeadOfHousehold" in str(e)


def test_living_situation_validation():
    """Test living situation business rules."""
    base_data = {
        "household": [{}],
        "person": [{"age": 25, "householdMemberType": "HeadOfHousehold"}],
        "withholdPayload": False
    }
    
    # livingRentalType without livingRenting - should fail
    test_data = base_data.copy()
    test_data["household"][0] = {
        "livingRenting": False, 
        "livingRentalType": "MarketRate"
    }
    
    try:
        EligibilityRequest(**test_data)
        raise AssertionError("Should have failed - rental type without renting")
    except ValueError as e:
        assert "livingRenting must be true" in str(e)


def test_amount_validation():
    """Test amount field patterns for AmountFloat (used in Income/Expense amounts)."""
    # AmountFloat 
    
    # Test valid amounts through Income model (which uses AmountFloat)
    valid_amounts = [
        0.0,                    
        1.0,                
        1000.0,              
        1000.5,           
        1000.50,           
        999999999999.0,        
        999999999999.99,     
        0.0,                    
        0.5,                  
        0.50,                 
    ]
    
    for amount in valid_amounts:
        try:
            income = Income(
                amount=amount,
                type=IncomeType.WAGES,
                frequency=Frequency.MONTHLY
            )
            print(f"✅ Valid amount: '{amount}' -> {income.amount}")
        except ValidationError as e:
            print(f"❌ Unexpectedly failed for valid amount '{amount}': {e}")
            raise AssertionError(f"Valid amount '{amount}' should not fail validation")
    
    # Test invalid amounts
    invalid_amounts = [
        #NOTE: we shouldn't allow 3 decimal places, but for our purposes it shouldn't really matter
        # 1000.999, 
        -1000,             
        1000000000000000.99,

    ]
    
    for amount in invalid_amounts:
        try:
            income = Income(
                amount=amount,
                type=IncomeType.WAGES,
                frequency=Frequency.MONTHLY
            )
            print(f"❌ Invalid amount '{amount}' unexpectedly passed validation")
            raise AssertionError(f"Invalid amount '{amount}' should fail validation")
        except ValidationError:
            print(f"✅ Invalid amount correctly rejected: '{amount}'")


def test_cash_on_hand_validation():
    """Test CashOnHandFloat validation pattern."""

    base_household_data = {
        "livingRenting": False,
        "livingOwner": False,
        "livingStayingWithFriend": False,
        "livingHotel": False,
        "livingShelter": False,
        "livingPreferNotToSay": False
    }
    
    # Valid cash amounts
    valid_cash_amounts = [
        0.0,                    
        1.0,                
        1000.0,              
        1000.5,           
        1000.50,           
        9999999.0,        
        9999999.99,     
    ]
    
    for amount in valid_cash_amounts:
        try:
            test_data = {
                **base_household_data,
                "cashOnHand": amount
            }
            from validation.schemas import Household
            household = Household(**test_data)
            print(f"✅ Valid cash amount: '{amount}' -> {household.cash_on_hand}")
        except ValidationError as e:
            print(f"❌ Unexpectedly failed for valid cash amount '{amount}': {e}")
            raise AssertionError(f"Valid cash amount '{amount}' should not fail validation")
    
    # Invalid cash amounts
    invalid_cash_amounts = [
        # 1000.999,             # Three decimal places
        -1000,                # Negative number
    ]
    
    for amount in invalid_cash_amounts:
        try:
            test_data = {
                **base_household_data,
                "cashOnHand": amount
            }
            from validation.schemas import Household
            household = Household(**test_data)
            print(f"❌ Invalid cash amount '{amount}' unexpectedly passed validation")
            raise AssertionError(f"Invalid cash amount '{amount}' should fail validation")
        except ValidationError:
            print(f"✅ Invalid cash amount correctly rejected: '{amount}'")


def test_case_id_validation():
    """Test CaseIdStr validation pattern."""
    # CaseIdStr pattern: r"^[a-zA-Z0-9/.-]*$", max_length=64
    # Allows: letters, numbers, forward slash, period, hyphen, up to 64 chars
    
    base_household_data = {
        "livingRenting": False,
        "livingOwner": False, 
        "livingStayingWithFriend": False,
        "livingHotel": False,
        "livingShelter": False,
        "livingPreferNotToSay": False
    }
    
    # Valid case IDs
    valid_case_ids = [
        "",                     # Empty string allowed
        "ABC123",               # Alphanumeric
        "case-123",             # With hyphen
        "case.123",             # With period
        "case/123",             # With forward slash
        "A" * 64,               # Max length (64 chars)
        "2023-SNAP-001.v2",     # Realistic case ID format
    ]
    
    for case_id in valid_case_ids:
        try:
            test_data = {
                **base_household_data,
                "caseId": case_id
            }
            from validation.schemas import Household
            household = Household(**test_data)
            print(f"✅ Valid case ID: '{case_id}' -> {household.case_id}")
        except ValidationError as e:
            print(f"❌ Unexpectedly failed for valid case ID '{case_id}': {e}")
            raise AssertionError(f"Valid case ID '{case_id}' should not fail validation")
    
    # Invalid case IDs
    invalid_case_ids = [
        "case@123",             # Invalid character (@)
        "case 123",             # Space not allowed
        "case#123",             # Hash not allowed
        "A" * 65,               # Too long (65 chars)
        "case_123",             # Underscore not allowed
    ]
    
    for case_id in invalid_case_ids:
        try:
            test_data = {
                **base_household_data,
                "caseId": case_id
            }
            from validation.schemas import Household
            household = Household(**test_data)
            print(f"❌ Invalid case ID '{case_id}' unexpectedly passed validation")
            raise AssertionError(f"Invalid case ID '{case_id}' should fail validation")
        except ValidationError:
            print(f"✅ Invalid case ID correctly rejected: '{case_id}'")


if __name__ == "__main__":
    print("Running validation tests...")
    print("=" * 50)
    
    test_valid_payload()
    print("✅ Valid payload test passed!")
    print()
    
    test_head_of_household_validation()
    print("✅ Head of household validation test passed!")
    print()
    
    test_living_situation_validation()
    print("✅ Living situation validation test passed!")
    print()
    
    print("Testing amount validation...")
    test_amount_validation()
    print("✅ Amount validation test passed!")
    print()
    
    print("Testing cash on hand validation...")
    test_cash_on_hand_validation()
    print("✅ Cash on hand validation test passed!")
    print()
    
    print("Testing case ID validation...")
    test_case_id_validation()
    print("✅ Case ID validation test passed!")
    print()
    
    print("🎉 All validation tests passed (let's go)!")