"""
Defines the Pydantic models (schemas) for validating API request payloads.

For parsing, validating, and type-casting incoming JSON data. 
"""
from typing import Annotated, List, Optional
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator, field_validator, AfterValidator

from models.enums import (
    ExpenseType,
    Frequency,
    HouseholdMemberType,
    IncomeType,
    LivingRentalType,
)


def validate_amount_decimals(v: float) -> float:
    """Ensure amount has no more than 2 decimal places."""
    if isinstance(v, (int, float)):
        # Convert to Decimal to check decimal places
        decimal_value = Decimal(str(v))
        if decimal_value.as_tuple().exponent < -2:
            # alternatively, we could just round to 2 decimals. 
            raise ValueError('Amount cannot have more than 2 decimal places')
        

    return v


# Type aliases for commonly used constraints
AmountFloat = Annotated[float, Field(ge=0.0, le=999999999999.99), AfterValidator(validate_amount_decimals)]


CashOnHandFloat = Annotated[float, Field(ge=0.0, le=9999999.99)]

CaseIdStr = Annotated[
    str,
    StringConstraints(pattern=r"^[a-zA-Z0-9/.-]*$", max_length=64)
]

AgeInt = Annotated[int, Field(ge=0, le=150)]


class Income(BaseModel):
    """A single source of income for a person."""
    amount: AmountFloat
    type: IncomeType
    frequency: Frequency


class Expense(BaseModel):
    """A single expense for a person."""
    amount: AmountFloat
    type: ExpenseType
    frequency: Frequency


class Person(BaseModel):
    """Represents a single person in the household."""
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True
    )

    age: AgeInt  # Required field
    student: Optional[bool] = False
    student_fulltime: Optional[bool] = Field(False, alias='studentFulltime')
    pregnant: Optional[bool] = False
    unemployed: Optional[bool] = False
    unemployed_worked_last_18_months: Optional[bool] = Field(False, alias='unemployedWorkedLast18Months')
    blind: Optional[bool] = False
    disabled: Optional[bool] = False
    veteran: Optional[bool] = False
    benefits_medicaid: Optional[bool] = Field(False, alias='benefitsMedicaid')
    benefits_medicaid_disability: Optional[bool] = Field(False, alias='benefitsMedicaidDisability')
    living_owner_on_deed: Optional[bool] = Field(False, alias='livingOwnerOnDeed')
    living_rental_on_lease: Optional[bool] = Field(False, alias='livingRentalOnLease')

    incomes: Optional[List[Income]] = []
    expenses: Optional[List[Expense]] = []
    household_member_type: Optional[HouseholdMemberType] = Field(None, alias='householdMemberType')


class Household(BaseModel):
    """Represents the household-level information."""
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True
    )

    case_id: Optional[CaseIdStr] = Field(None, alias='caseId')
    cash_on_hand: Optional[CashOnHandFloat] = Field(None, alias='cashOnHand')
    living_rental_type: Optional[LivingRentalType] = Field(None, alias='livingRentalType')
    living_renting: Optional[bool] = Field(False, alias='livingRenting')
    living_owner: Optional[bool] = Field(False, alias='livingOwner')
    living_staying_with_friend: Optional[bool] = Field(False, alias='livingStayingWithFriend')
    living_hotel: Optional[bool] = Field(False, alias='livingHotel')
    living_shelter: Optional[bool] = Field(False, alias='livingShelter')
    living_prefer_not_to_say: Optional[bool] = Field(False, alias='livingPreferNotToSay')

    @field_validator('cash_on_hand')
    @classmethod
    def validate_cash_on_hand_decimals(cls, v):
        """Ensure cash_on_hand has no more than 2 decimal places."""
        if v is not None and isinstance(v, (int, float)):
            # Convert to Decimal to check decimal places
            decimal_value = Decimal(str(v))
            if decimal_value.as_tuple().exponent < -2:
                raise ValueError('Cash on hand cannot have more than 2 decimal places')
        return v

'''
MAIN SCHEMA
'''
class EligibilityRequest(BaseModel):
    """
    The main schema for eligibility screening requests.
    It contains one household and a list of persons.
    """
    model_config = ConfigDict(populate_by_name=True)

    withhold_payload: Optional[bool] = Field(False, alias='withholdPayload')
    household: List[Household] = Field(..., min_length=1, max_length=1)
    person: List[Person] = Field(..., min_length=1, max_length=8)
    

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