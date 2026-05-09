import json
from pathlib import Path

import pytest

from src.models.schemas import AggregateEligibilityRequest
from src.rules.program_rules.S2R057 import ChildHealthPlus
from src.rules.program_rules.S2R058 import EssentialPlan
from src.rules.program_rules.S2R059 import NYCFerryDiscount
from src.rules.program_rules.S2R060 import MedicaidTransportation
from src.validation.validate_request import validate_request


def test_child_health_plus_for_child_above_medicaid_threshold():
    request = _aggregate_request(
        [
            _person(age=35, income=40_000),
            _person(age=5, household_member_type="Child"),
        ]
    )

    assert ChildHealthPlus.evaluate(request)


def test_child_health_plus_false_at_medicaid_threshold():
    request = _aggregate_request(
        [
            _person(age=35, income=31_478),
            _person(age=5, household_member_type="Child"),
        ]
    )

    assert not ChildHealthPlus.evaluate(request)


def test_child_health_plus_false_without_child():
    request = _aggregate_request([_person(age=35, income=40_000)])

    assert not ChildHealthPlus.evaluate(request)


def test_essential_plan_for_adult_in_income_range():
    request = _aggregate_request([_person(age=35, income=30_000)])

    assert EssentialPlan.evaluate(request)


def test_essential_plan_false_at_lower_income_bound():
    request = _aggregate_request([_person(age=35, income=21_597)])

    assert not EssentialPlan.evaluate(request)


def test_essential_plan_true_at_upper_income_bound():
    request = _aggregate_request([_person(age=35, income=39_125)])

    assert EssentialPlan.evaluate(request)


def test_essential_plan_false_above_upper_income_bound():
    request = _aggregate_request([_person(age=35, income=39_125.01)])

    assert not EssentialPlan.evaluate(request)


def test_essential_plan_false_for_reported_medicaid():
    request = _aggregate_request(
        [_person(age=35, income=30_000, benefitsMedicaid=True)]
    )

    assert not EssentialPlan.evaluate(request)


def test_nyc_ferry_discount_for_older_adult():
    request = _aggregate_request([_person(age=65, income=0)])

    assert NYCFerryDiscount.evaluate(request)


def test_nyc_ferry_discount_false_without_qualifying_person():
    request = _aggregate_request([_person(age=35, income=0)])

    assert not NYCFerryDiscount.evaluate(request)


@pytest.mark.parametrize(
    "payload_path",
    sorted(Path("tests/data/payloads/S2R059_NYC_Ferry_Discount").glob("*/*.json")),
)
def test_nyc_ferry_discount_pr6_fixture_corpus(payload_path):
    expected = payload_path.parent.name == "true"
    with payload_path.open() as f:
        payload = json.load(f)

    request = _aggregate_request_from_payload(payload)

    assert NYCFerryDiscount.evaluate(request) is expected


def test_medicaid_transportation_for_medicaid_recipient():
    request = _aggregate_request([_person(age=35, benefitsMedicaid=True)])

    assert MedicaidTransportation.evaluate(request)


def test_medicaid_transportation_false_without_medicaid():
    request = _aggregate_request([_person(age=35)])

    assert not MedicaidTransportation.evaluate(request)


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
    return _aggregate_request_from_payload(payload)


def _aggregate_request_from_payload(payload):
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
