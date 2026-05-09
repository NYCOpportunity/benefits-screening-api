import json
from pathlib import Path

import pytest

from src.models.schemas import AggregateEligibilityRequest
from src.rules.program_rules.S2R007 import SupplementalNutritionAssistanceProgram
from src.rules.program_rules.S2R022 import WomenInfantsChildren
from src.validation.validate_request import validate_request


@pytest.mark.parametrize(
    "payload_path",
    sorted(Path("tests/data/payloads/S2R007_SNAP").glob("*/*.json")),
)
def test_snap_generated_fixture_corpus(payload_path):
    expected = payload_path.parent.name == "true"
    request = _aggregate_request_from_payload_path(payload_path)

    assert SupplementalNutritionAssistanceProgram.evaluate(request) is expected


@pytest.mark.parametrize(
    "payload_path",
    sorted(Path("tests/data/payloads/S2R022_WIC").glob("*/*.json")),
)
def test_wic_generated_fixture_corpus(payload_path):
    expected = payload_path.parent.name == "true"
    request = _aggregate_request_from_payload_path(payload_path)

    assert WomenInfantsChildren.evaluate(request) is expected


@pytest.mark.parametrize(
    ("monthly_income", "expected"),
    [
        (1957, True),
        (1958, False),
    ],
)
def test_snap_earned_income_uses_public_drools_gross_threshold(
    monthly_income, expected
):
    request = _aggregate_request(
        [
            _person(
                age=30,
                incomes=[
                    {
                        "amount": monthly_income,
                        "type": "Wages",
                        "frequency": "Monthly",
                    }
                ],
            )
        ]
    )

    assert SupplementalNutritionAssistanceProgram.evaluate(request) is expected


@pytest.mark.parametrize(
    ("monthly_income", "expected"),
    [
        (2608, True),
        (2609, False),
    ],
)
def test_snap_elderly_household_uses_public_drools_gross_threshold(
    monthly_income, expected
):
    request = _aggregate_request(
        [
            _person(
                age=60,
                incomes=[
                    {
                        "amount": monthly_income,
                        "type": "SSRetirement",
                        "frequency": "Monthly",
                    }
                ],
            )
        ]
    )

    assert SupplementalNutritionAssistanceProgram.evaluate(request) is expected


@pytest.mark.parametrize(
    ("monthly_income", "expected"),
    [
        (1696, True),
        (1697, False),
    ],
)
def test_snap_unearned_income_uses_public_drools_gross_threshold(
    monthly_income, expected
):
    request = _aggregate_request(
        [
            _person(
                age=30,
                incomes=[
                    {
                        "amount": monthly_income,
                        "type": "SSRetirement",
                        "frequency": "Monthly",
                    }
                ],
            )
        ]
    )

    assert SupplementalNutritionAssistanceProgram.evaluate(request) is expected


@pytest.mark.parametrize(
    ("income", "expected"),
    [
        (28_953, True),
        (28_954, False),
    ],
)
def test_wic_single_pregnant_adult_uses_public_drools_threshold(
    income, expected
):
    request = _aggregate_request([_person(age=30, income=income, pregnant=True)])

    assert WomenInfantsChildren.evaluate(request) is expected


@pytest.mark.parametrize(
    ("income", "expected"),
    [
        (39_128, True),
        (39_129, False),
    ],
)
def test_wic_two_person_child_household_uses_public_drools_threshold(
    income, expected
):
    request = _aggregate_request(
        [
            _person(age=30, income=income),
            _person(age=4, household_member_type="Child"),
        ]
    )

    assert WomenInfantsChildren.evaluate(request) is expected


def test_wic_for_child_household_reporting_medicaid():
    request = _aggregate_request(
        [
            _person(age=30, income=100_000),
            _person(age=4, household_member_type="Child", benefitsMedicaid=True),
        ]
    )

    assert WomenInfantsChildren.evaluate(request)


def test_wic_for_child_household_with_cash_assistance_income():
    request = _aggregate_request(
        [
            _person(
                age=30,
                incomes=[
                    {
                        "amount": 100_000,
                        "type": "CashAssistance",
                        "frequency": "Yearly",
                    }
                ],
            ),
            _person(age=4, household_member_type="Child"),
        ]
    )

    assert WomenInfantsChildren.evaluate(request)


def _aggregate_request(persons):
    payload = {
        "household": [
            {
                "cashOnHand": 0.0,
                "livingRentalType": "MarketRate",
                "livingRenting": True,
                "livingOwner": False,
                "livingStayingWithFriend": False,
                "livingHotel": False,
                "livingShelter": False,
                "livingPreferNotToSay": False,
            }
        ],
        "person": persons,
        "withholdPayload": False,
    }

    is_valid, eligibility_request, errors = validate_request(payload)
    assert is_valid, errors
    return AggregateEligibilityRequest.from_eligibility_request(eligibility_request)


def _aggregate_request_from_payload_path(payload_path):
    with payload_path.open() as f:
        payload = json.load(f)

    is_valid, eligibility_request, errors = validate_request(payload)
    assert is_valid, errors
    return AggregateEligibilityRequest.from_eligibility_request(eligibility_request)


def _person(age, income=0, household_member_type="HeadOfHousehold", **overrides):
    person = {
        "age": age,
        "householdMemberType": household_member_type,
        "student": False,
        "pregnant": False,
        "studentFulltime": False,
        "blind": False,
        "disabled": False,
        "veteran": False,
        "unemployed": False,
        "unemployedWorkedLast18Months": False,
        "benefitsMedicaid": False,
        "benefitsMedicaidDisability": False,
        "livingOwnerOnDeed": False,
        "livingRentalOnLease": household_member_type == "HeadOfHousehold",
        "incomes": [],
        "expenses": [],
    }
    if income:
        person["incomes"].append(
            {"amount": income, "type": "Wages", "frequency": "Yearly"}
        )
    person.update(overrides)
    return person
