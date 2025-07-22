"""
Defines the Pydantic models (schemas) for validating API request payloads.

For parsing, validating, and type-casting incoming JSON data. 
"""
from typing import Annotated, List, Optional
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator, field_validator, AfterValidator

from src.models.enums import (
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
MAIN VALIDATION SCHEMA
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
    

'''
AGGREGATE ELIGIBILITY REQUEST SCHEMA
'''

class AggregateEligibilityRequest(EligibilityRequest):
    """
    Extended version of EligibilityRequest that includes aggregated data types from the Drools engine.
    These aggregates are computed from the base request data and used by the eligibility rules.
    """
    model_config = ConfigDict(populate_by_name=True)
    
    # Household composition aggregates
    head_of_household_married: bool = Field(False, alias='headOfHouseholdMarried')
    members_nuclear_only: int = Field(0, alias='membersNuclearOnly')
    foster_children: int = Field(0, alias='fosterChildren')
    members_pregnant: int = Field(0, alias='membersPregnant')
    members_pregnant_not_foster: int = Field(0, alias='membersPregnantNotFoster')
    members_plus_pregnant_minus_foster: int = Field(0, alias='membersPlusPregnantMinusFoster')
    members_plus_pregnant: int = Field(0, alias='membersPlusPregnant')
    children_student_blind_disabled_eitc: int = Field(0, alias='childrenStudentBlindDisabledEITC')
    child_care_voucher_household_members: int = Field(0, alias='childCareVoucherHouseholdMembers')
    household_all_adults: bool = Field(False, alias='householdAllAdults')
    
    # Income aggregates - Person level
    income_person_wage_self_employment_monthly: dict[int, float] = Field(default_factory=dict)
    income_person_wage_self_employment_boarder_monthly: dict[int, float] = Field(default_factory=dict)
    income_person_earned_yearly: dict[int, float] = Field(default_factory=dict)
    income_person_investment_yearly: dict[int, float] = Field(default_factory=dict)
    income_person_gifts_monthly: dict[int, float] = Field(default_factory=dict)
    income_person_monthly: dict[int, float] = Field(default_factory=dict)
    income_person_yearly: dict[int, float] = Field(default_factory=dict)
    income_person_isy_monthly: dict[int, float] = Field(default_factory=dict)
    income_person_isy_yearly: dict[int, float] = Field(default_factory=dict)
    income_person_ses_monthly: dict[int, float] = Field(default_factory=dict)
    
    # Income aggregates - Household level
    income_household_total_monthly: float = Field(0.0, alias='incomeHouseholdTotalMonthly')
    income_household_total_yearly: float = Field(0.0, alias='incomeHouseholdTotalYearly')
    income_household_total_monthly_less_foster: float = Field(0.0, alias='incomeHouseholdTotalMonthlyLessFoster')
    income_household_total_monthly_less_gifts: float = Field(0.0, alias='incomeHouseholdTotalMonthlyLessGifts')
    income_household_wage_self_employment_monthly: float = Field(0.0, alias='incomeHouseholdWageSelfEmploymentMonthly')
    income_household_unearned_monthly: float = Field(0.0, alias='incomeHouseholdUnearnedMonthly')
    income_household_boarder_monthly: float = Field(0.0, alias='incomeHouseholdBoarderMonthly')
    income_household_nuclear_isy_yearly: float = Field(0.0, alias='incomeHouseholdNuclearISYYearly')
    income_household_monthly_ca: float = Field(0.0, alias='incomeHouseholdMonthlyCA')
    income_household_monthly_ca_minus_work_expense: float = Field(0.0, alias='incomeHouseholdMonthlyCAMinusWorkExpense')
    
    # Income aggregates - Special household members
    income_head_earned_yearly: float = Field(0.0, alias='incomeHeadEarnedYearly')
    income_head_and_spouse_earned_yearly: float = Field(0.0, alias='incomeHeadAndSpouseEarnedYearly')
    income_head_and_spouse_ses_monthly: float = Field(0.0, alias='incomeHeadAndSpouseSESMonthly')
    income_owners_total_yearly: float = Field(0.0, alias='incomeOwnersTotalYearly')
    income_adults_children_total_monthly: float = Field(0.0, alias='incomeAdultsChildrenTotalMonthly')
    income_child_care_voucher_total_monthly: float = Field(0.0, alias='incomeChildCareVoucherTotalMonthly')
    income_adults_total_monthly: float = Field(0.0, alias='incomeAdultsTotalMonthly')
    
    # Income boolean flags
    income_household_has_cash_assistance: bool = Field(False, alias='incomeHouseholdHasCashAssistance')
    income_household_has_ui: bool = Field(False, alias='incomeHouseholdHasUI')
    income_household_has_benefit: bool = Field(False, alias='incomeHouseholdHasBenefit')
    income_household_has_ssi: bool = Field(False, alias='incomeHouseholdHasSSI')
    
    # Expense aggregates - Household level
    expense_household_child_dependent_care_monthly: float = Field(0.0, alias='expenseHouseholdChildDependentCareMonthly')
    expense_household_medical_monthly: float = Field(0.0, alias='expenseHouseholdMedicalMonthly')
    expense_household_rent_mortgage_monthly: float = Field(0.0, alias='expenseHouseholdRentMortgageMonthly')
    expense_household_rent_monthly: float = Field(0.0, alias='expenseHouseholdRentMonthly')
    expense_household_child_support_monthly: float = Field(0.0, alias='expenseHouseholdChildSupportMonthly')
    
    # Expense boolean flags
    expense_household_has_heating: bool = Field(False, alias='expenseHouseholdHasHeating')
    expense_household_has_dependent_care: bool = Field(False, alias='expenseHouseholdHasDependentCare')
    expense_household_has_child_or_dependent_care: bool = Field(False, alias='expenseHouseholdHasChildOrDependentCare')
    
    @classmethod
    def from_eligibility_request(cls, request: EligibilityRequest) -> 'AggregateEligibilityRequest':
        """
        Factory method to create AggregateEligibilityRequest from base EligibilityRequest.
        Computes all aggregate values from the base request data.
        """
        # Start with the base request data
        data = request.model_dump()
        
        # Compute aggregates
        aggregates = cls._compute_aggregates(request)
        
        # Merge aggregates with base data
        data.update(aggregates)
        
        return cls(**data)
    
    @staticmethod
    def _compute_aggregates(request: EligibilityRequest) -> dict:
        """Compute all aggregate values from the base request using the helper module."""
        from src.rules.aggregate_eligibility_helper import compute_aggregates  # local import to avoid circular
        return compute_aggregates(request) 




