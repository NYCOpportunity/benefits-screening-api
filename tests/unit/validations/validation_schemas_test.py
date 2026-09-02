"""
Unit tests for request parsing schemas.

Covers type coercion and field constraints used when building rule input.
"""
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.models.schemas import EligibilityRequest, Household, Income, Person
from src.models.enums import IncomeType, Frequency

def test_valid_payload():
    """Test that a valid payload passes validation."""
    current_dir = Path(__file__).parent
    file_path = current_dir.parent.parent / "data" / "payloads" / "eligibility-program-test-payload.json"
    with open(file_path) as f:
        data = json.load(f)
    
    # Should not raise an exception
    request = EligibilityRequest(**data)
    assert len(request.household) == 1
    assert len(request.person) == 1
    assert request.person[0].age == 23
    assert request.withhold_payload is True


def test_amount_parsing():
    """Parse income/expense amounts as non-negative floats"""
    for amount in [0.0, 1000.5, 999999999999.99, 1000.999, 1000000000000000.99]:
        income = Income(
            amount=amount,
            type=IncomeType.WAGES,
            frequency=Frequency.MONTHLY,
        )
        assert income.amount == amount

    income = Income(amount="", type=IncomeType.WAGES, frequency=Frequency.MONTHLY)
    assert income.amount == 0.0

    for amount in [-1000, -0.01]:
        with pytest.raises(ValidationError):
            Income(amount=amount, type=IncomeType.WAGES, frequency=Frequency.MONTHLY)


def test_cash_on_hand_parsing():
    """Parse cashOnHand as optional float"""
    base_household_data = {
        "livingRenting": False,
        "livingOwner": False,
        "livingStayingWithFriend": False,
        "livingHotel": False,
        "livingShelter": False,
        "livingPreferNotToSay": False
    }

    for amount in [0.0, 1000.5, 9999999.99, 1000.999, 10000000.0]:
        household = Household(**{**base_household_data, "cashOnHand": amount})
        assert household.cash_on_hand == amount

    with pytest.raises(ValidationError):
        Household(**{**base_household_data, "cashOnHand": -1000})


def test_empty_string_optional_fields():
    """Empty strings on optional fields should be treated as unset."""
    base_household_data = {
        "livingRenting": False,
        "livingOwner": False,
        "livingStayingWithFriend": False,
        "livingHotel": False,
        "livingShelter": False,
        "livingPreferNotToSay": False,
    }

    household = Household(**{**base_household_data, "cashOnHand": ""})
    assert household.cash_on_hand is None

    household = Household(**{**base_household_data, "livingRentalType": ""})
    assert household.living_rental_type is None


def test_empty_string_amount_fields():
    payload = {
        "household": [
            {
                "livingPreferNotToSay": "true",
                "caseId": "10",
                "cashOnHand": "",
            }
        ],
        "person": [
            {
                "age": 64,
                "householdMemberType": "HeadOfHousehold",
                "disabled": "false",
                "incomes": [
                    {
                        "amount": "76445",
                        "type": "Wages",
                        "frequency": "Yearly",
                    }
                ],
            },
            {
                "age": "9",
                "householdMemberType": "Grandchild",
                "disabled": "false",
                "incomes": [],
            },
        ],
        "withholdPayload": "false",
    }

    request = EligibilityRequest(**payload)
    assert request.household[0].cash_on_hand is None
    assert request.person[0].incomes[0].amount == 76445.0
    assert request.person[1].age == 9


def test_empty_string_boolean_fields():
    """Allow '' on optional boolean fields."""
    base_household_data = {
        "livingRenting": False,
        "livingOwner": False,
        "livingStayingWithFriend": False,
        "livingHotel": False,
        "livingShelter": False,
        "livingPreferNotToSay": False,
    }

    household = Household(**{**base_household_data, "livingRenting": ""})
    assert household.living_renting is None

    person = Person(age=25, householdMemberType="HeadOfHousehold", disabled="")
    assert person.disabled is None


def test_case_id_parsing():
    """Parse caseId as optional string"""
    base_household_data = {
        "livingRenting": False,
        "livingOwner": False,
        "livingStayingWithFriend": False,
        "livingHotel": False,
        "livingShelter": False,
        "livingPreferNotToSay": False
    }

    household = Household(**{**base_household_data, "caseId": ""})
    assert household.case_id is None

    household = Household(**{**base_household_data, "caseId": "case123"})
    assert household.case_id == "case123"


if __name__ == "__main__":
    print("Running validation tests...")
    print("=" * 50)
    
    test_valid_payload()
    print("✅ Valid payload test passed!")
    print()
    
    print("Testing amount parsing...")
    test_amount_parsing()
    print("✅ Amount parsing test passed!")
    print()
    
    print("Testing cash on hand parsing...")
    test_cash_on_hand_parsing()
    print("✅ Cash on hand parsing test passed!")
    print()
    
    print("Testing case ID parsing...")
    test_case_id_parsing()
    print("✅ Case ID parsing test passed!")
    print()
    
    print("🎉 All validation tests passed (let's go)!")