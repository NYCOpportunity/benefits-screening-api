"""
Defines the Pydantic models (schemas) for validating API request payloads.

For parsing, validating, and type-casting incoming JSON data. 
"""
from typing import Annotated, List, Optional

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from models.enums import (
    ExpenseType,
    Frequency,
    HouseholdMemberType,
    IncomeType,
    LivingRentalType,
)

# Type aliases for commonly used constraints
AmountStr = Annotated[
    str,
    StringConstraints(pattern=r"^\d{0,12}(\.\d{1,2})?$")
]

CashOnHandStr = Annotated[
    str,
    StringConstraints(pattern=r"^\d{1,7}(\.\d{1,2})?$")
]

CaseIdStr = Annotated[
    str,
    StringConstraints(pattern=r"^[a-zA-Z0-9/.-]*$", max_length=64)
]

AgeInt = Annotated[int, Field(ge=0, le=999)]


class Income(BaseModel):
    """A single source of income for a person."""
    amount: AmountStr
    type: IncomeType
    frequency: Frequency


class Expense(BaseModel):
    """A single expense for a person."""
    amount: AmountStr
    type: ExpenseType
    frequency: Frequency


class Person(BaseModel):
    """Represents a single person in the household."""
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True
    )

    age: AgeInt
    student: bool = False
    student_fulltime: bool = Field(False, alias='studentFulltime')
    pregnant: bool = False
    unemployed: bool = False
    unemployed_worked_last_18_months: bool = Field(False, alias='unemployedWorkedLast18Months')
    blind: bool = False
    disabled: bool = False
    veteran: bool = False
    benefits_medicaid: bool = Field(False, alias='benefitsMedicaid')
    benefits_medicaid_disability: bool = Field(False, alias='benefitsMedicaidDisability')
    living_owner_on_deed: bool = Field(False, alias='livingOwnerOnDeed')
    living_rental_on_lease: bool = Field(False, alias='livingRentalOnLease')

    incomes: List[Income] = []
    expenses: List[Expense] = []
    household_member_type: HouseholdMemberType = Field(..., alias='householdMemberType')


class Household(BaseModel):
    """Represents the household-level information."""
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True
    )

    case_id: Optional[CaseIdStr] = Field(None, alias='caseId')
    cash_on_hand: Optional[CashOnHandStr] = Field(None, alias='cashOnHand')
    living_rental_type: Optional[LivingRentalType] = Field(None, alias='livingRentalType')
    living_renting: bool = Field(False, alias='livingRenting')
    living_owner: bool = Field(False, alias='livingOwner')
    living_staying_with_friend: bool = Field(False, alias='livingStayingWithFriend')
    living_hotel: bool = Field(False, alias='livingHotel')
    living_shelter: bool = Field(False, alias='livingShelter')
    living_prefer_not_to_say: bool = Field(False, alias='livingPreferNotToSay')


class EligibilityRequest(BaseModel):
    """
    The main schema for eligibility screening requests.
    It contains one household and a list of persons.
    """
    model_config = ConfigDict(populate_by_name=True)

    withhold_payload: bool = Field(False, alias='withholdPayload')
    household: List[Household] = Field(..., min_length=1, max_length=1)
    person: List[Person] = Field(..., min_length=1)


    @model_validator(mode='after')
    def validate_head_of_household_rule(self):
        """Ensures exactly one person is designated as HeadOfHousehold."""
        if not self.person:
            return self  # Let other validators handle missing persons list

        head_of_household_count = sum(
            1 for p in self.person if p.household_member_type == HouseholdMemberType.HEAD_OF_HOUSEHOLD
        )

        if head_of_household_count != 1:
            raise ValueError("Exactly one person's householdMemberType must be 'HeadOfHousehold'")

        return self

    @model_validator(mode='after')
    def validate_living_situation_rules(self):
        """Enforces rules related to living situation fields."""
        if not self.household or not self.person:
            return self

        household = self.household[0]

        # Rule 1: household.livingRentalType can only be set if household.livingRenting is true
        if household.living_rental_type and not household.living_renting:
            raise ValueError("household.livingRenting must be true if household.livingRentalType is specified.")

        # Rule 2: if household.livingPreferNotToSay is true, other living flags must be false
        if household.living_prefer_not_to_say:
            other_living_flags = [
                household.living_renting,
                household.living_owner,
                household.living_staying_with_friend,
                household.living_hotel,
                household.living_shelter,
            ]
            if any(other_living_flags):
                raise ValueError(
                    "If household.livingPreferNotToSay is true, other living flags (renting, owner, etc.) must be false."
                )

        # Rule 3: No person.livingRentalOnLease can be True when household.livingRenting is false
        if not household.living_renting and any(p.living_rental_on_lease for p in self.person):
            raise ValueError("No person.livingRentalOnLease can be true when household.livingRenting is false.")

        # Rule 4: No person.livingOwnerOnDeed can be true when household.livingOwner is false
        if not household.living_owner and any(p.living_owner_on_deed for p in self.person):
            raise ValueError("No person.livingOwnerOnDeed can be true when household.livingOwner is false.")

        return self