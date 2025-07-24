from __future__ import annotations

"""Helper utilities to compute aggregate values for eligibility requests.
This module was extracted from the bulky _compute_aggregates staticmethod that
lived on AggregateEligibilityRequest to improve readability and maintainability.
The public entry-point is `compute_aggregates`, which returns the same dictionary
of aggregate values that the original implementation produced.
"""

from typing import Dict

from src.models.schemas import EligibilityRequest
from src.models.enums import (
    ExpenseType,
    Frequency,
    HouseholdMemberType,
    IncomeType,
)


def compute_aggregates(request: EligibilityRequest) -> Dict[str, object]:
    """Compute all aggregate values from the base request.

    This implementation is a direct copy of the original logic from
    `AggregateEligibilityRequest._compute_aggregates` so that behaviour remains
    identical. Only whitespace and helper-function placement has been adjusted
    to satisfy linters.
    """
    household = request.household[0]
    persons = request.person

    # Initialize result dictionary
    result: Dict[str, object] = {}

    # Frequency conversion factors
    frequency_to_monthly = {
        Frequency.WEEKLY: 4.3333333333333,
        Frequency.BIWEEKLY: 2.166666666667,
        Frequency.SEMIMONTHLY: 2.0,
        Frequency.MONTHLY: 1.0,
        Frequency.YEARLY: 1.0 / 12.0,
    }

    # Helper function to convert to monthly amount
    def to_monthly(amount: float, frequency: Frequency) -> float:  # noqa: WPS430
        return amount * frequency_to_monthly.get(frequency, 1.0)

    # Helper function to convert to yearly amount
    def to_yearly(amount: float, frequency: Frequency) -> float:  # noqa: WPS430
        monthly = to_monthly(amount, frequency)
        return monthly * 12.0

    # Find head of household and spouse
    head_of_household = next(
        (
            p
            for p in persons
            if p.household_member_type == HouseholdMemberType.HEAD_OF_HOUSEHOLD
        ),
        None,
    )
    spouse = next(
        (
            p for p in persons if p.household_member_type == HouseholdMemberType.SPOUSE
        ),
        None,
    )

    # Household composition aggregates
    result["head_of_household_married"] = spouse is not None

    # Nuclear family members (HoH, spouse, children, stepchildren)
    nuclear_types = [
        HouseholdMemberType.HEAD_OF_HOUSEHOLD,
        HouseholdMemberType.SPOUSE,
        HouseholdMemberType.CHILD,
        HouseholdMemberType.STEP_CHILD,
    ]
    result["members_nuclear_only"] = sum(
        1 for p in persons if p.household_member_type in nuclear_types
    )

    # Foster children
    result["foster_children"] = sum(
        1 for p in persons if p.household_member_type == HouseholdMemberType.FOSTER_CHILD
    )

    # Pregnant members
    result["members_pregnant"] = sum(1 for p in persons if p.pregnant)
    result["members_pregnant_not_foster"] = sum(
        1
        for p in persons
        if p.pregnant and p.household_member_type != HouseholdMemberType.FOSTER_CHILD
    )

    # Members calculations
    total_members = len(persons)
    result["members_plus_pregnant_minus_foster"] = (
        total_members + result["members_pregnant"] - result["foster_children"]
    )
    result["members_plus_pregnant"] = total_members + result["members_pregnant"]

    # EITC eligible children
    eitc_children = 0
    for p in persons:
        if p.household_member_type in [
            HouseholdMemberType.CHILD,
            HouseholdMemberType.STEP_CHILD,
        ]:
            if (
                p.age < 19
                or (p.age < 24 and p.student)
                or p.blind
                or p.disabled
            ):
                eitc_children += 1
    result["children_student_blind_disabled_eitc"] = eitc_children

    # Child care voucher household members (excluding foster children)
    result["child_care_voucher_household_members"] = total_members - result[
        "foster_children"
    ]

    # Check if all adults
    result["household_all_adults"] = all(p.age >= 18 for p in persons)

    # Income aggregates - Person level
    result["income_person_wage_self_employment_monthly"] = {}
    result["income_person_wage_self_employment_boarder_monthly"] = {}
    result["income_person_earned_yearly"] = {}
    result["income_person_investment_yearly"] = {}
    result["income_person_gifts_monthly"] = {}
    result["income_person_monthly"] = {}
    result["income_person_yearly"] = {}
    result["income_person_isy_monthly"] = {}
    result["income_person_isy_yearly"] = {}
    result["income_person_ses_monthly"] = {}

    for i, person in enumerate(persons):
        wage_self_employment_monthly = 0.0
        boarder_monthly = 0.0
        investment_yearly = 0.0
        gifts_monthly = 0.0
        total_monthly = 0.0

        for income in person.incomes:
            monthly_amount = to_monthly(income.amount, income.frequency)
            yearly_amount = to_yearly(income.amount, income.frequency)

            # Add to total
            total_monthly += monthly_amount

            # Categorize by type
            if income.type in [IncomeType.WAGES, IncomeType.SELF_EMPLOYMENT]:
                wage_self_employment_monthly += monthly_amount
            elif income.type == IncomeType.BOARDER:
                boarder_monthly += monthly_amount
            elif income.type in [IncomeType.INVESTMENT, IncomeType.RENTAL]:
                investment_yearly += yearly_amount
            elif income.type == IncomeType.GIFTS:
                gifts_monthly += monthly_amount

        result["income_person_wage_self_employment_monthly"][i] = (
            wage_self_employment_monthly
        )
        result["income_person_wage_self_employment_boarder_monthly"][i] = (
            wage_self_employment_monthly + boarder_monthly
        )
        result["income_person_earned_yearly"][i] = wage_self_employment_monthly * 12.0
        result["income_person_investment_yearly"][i] = investment_yearly
        result["income_person_gifts_monthly"][i] = gifts_monthly
        result["income_person_monthly"][i] = total_monthly
        result["income_person_yearly"][i] = total_monthly * 12.0

        # ISY income (excludes certain benefits)
        isy_excluded = [
            IncomeType.CHILD_SUPPORT,
            IncomeType.CASH_ASSISTANCE,
            IncomeType.SS_SURVIVOR,
            IncomeType.SSI,
            IncomeType.UNEMPLOYMENT,
        ]
        isy_monthly = sum(
            to_monthly(inc.amount, inc.frequency)
            for inc in person.incomes
            if inc.type not in isy_excluded
        )
        result["income_person_isy_monthly"][i] = isy_monthly
        result["income_person_isy_yearly"][i] = isy_monthly * 12.0

        # SES income (Social Security at 75%)
        ses_monthly = 0.0
        for income in person.incomes:
            monthly_amount = to_monthly(income.amount, income.frequency)
            if income.type in [IncomeType.SS_RETIREMENT, IncomeType.SS_SURVIVOR]:
                ses_monthly += monthly_amount * 0.75
            else:
                ses_monthly += monthly_amount
        result["income_person_ses_monthly"][i] = ses_monthly

    # Income aggregates - Household level
    result["income_household_total_monthly"] = sum(
        result["income_person_monthly"].values()
    )
    result["income_household_total_yearly"] = result[
        "income_household_total_monthly"
    ] * 12.0

    # Income less foster children
    income_less_foster = 0.0
    for i, person in enumerate(persons):
        if person.household_member_type != HouseholdMemberType.FOSTER_CHILD:
            income_less_foster += result["income_person_monthly"].get(i, 0.0)
    result["income_household_total_monthly_less_foster"] = income_less_foster

    # Income less gifts
    income_less_gifts = 0.0
    for i, person in enumerate(persons):
        income_less_gifts += result["income_person_monthly"].get(i, 0.0) - result[
            "income_person_gifts_monthly"
        ].get(i, 0.0)
    result["income_household_total_monthly_less_gifts"] = income_less_gifts

    # Wage and self-employment income
    result["income_household_wage_self_employment_monthly"] = sum(
        result["income_person_wage_self_employment_monthly"].values()
    )

    # Unearned income (all income except wages, self-employment, boarder)
    unearned_monthly = 0.0
    for person in persons:
        for income in person.incomes:
            if income.type not in [
                IncomeType.WAGES,
                IncomeType.SELF_EMPLOYMENT,
                IncomeType.BOARDER,
            ]:
                unearned_monthly += to_monthly(income.amount, income.frequency)
    result["income_household_unearned_monthly"] = unearned_monthly

    # Boarder income
    boarder_monthly = 0.0
    for person in persons:
        for income in person.incomes:
            if income.type == IncomeType.BOARDER:
                boarder_monthly += to_monthly(income.amount, income.frequency)
    result["income_household_boarder_monthly"] = boarder_monthly

    # Nuclear ISY income
    nuclear_isy_yearly = 0.0
    for i, person in enumerate(persons):
        if person.household_member_type in nuclear_types:
            nuclear_isy_yearly += result["income_person_isy_yearly"].get(i, 0.0)
    result["income_household_nuclear_isy_yearly"] = nuclear_isy_yearly

    # Cash Assistance income
    ca_income_types = [
        IncomeType.ALIMONY,
        IncomeType.BOARDER,
        IncomeType.CASH_ASSISTANCE,
        IncomeType.CHILD_SUPPORT,
        IncomeType.GIFTS,
        IncomeType.INVESTMENT,
        IncomeType.PENSION,
        IncomeType.RENTAL,
        IncomeType.SELF_EMPLOYMENT,
        IncomeType.SS_DEPENDENT,
        IncomeType.SS_DISABILITY,
        IncomeType.SS_RETIREMENT,
        IncomeType.SS_SURVIVOR,
        IncomeType.SSI,
        IncomeType.UNEMPLOYMENT,
        IncomeType.VETERAN,
        IncomeType.WAGES,
        IncomeType.WORKERS_COMP,
    ]
    ca_monthly = 0.0
    employed_persons = 0
    for person in persons:
        person_ca_income = 0.0
        has_employment = False
        for income in person.incomes:
            if income.type in ca_income_types:
                person_ca_income += to_monthly(income.amount, income.frequency)
            if income.type in [IncomeType.WAGES, IncomeType.SELF_EMPLOYMENT]:
                has_employment = True
        ca_monthly += person_ca_income
        if has_employment:
            employed_persons += 1

    result["income_household_monthly_ca"] = ca_monthly
    result["income_household_monthly_ca_minus_work_expense"] = ca_monthly - (
        150.0 * employed_persons
    )

    # Special household member incomes
    head_index = persons.index(head_of_household) if head_of_household else None
    spouse_index = persons.index(spouse) if spouse else None

    result["income_head_earned_yearly"] = (
        result["income_person_earned_yearly"].get(head_index, 0.0)
        if head_index is not None
        else 0.0
    )

    head_spouse_earned = result["income_head_earned_yearly"]
    if spouse_index is not None:
        head_spouse_earned += result["income_person_earned_yearly"].get(
            spouse_index, 0.0
        )
    result["income_head_and_spouse_earned_yearly"] = head_spouse_earned

    head_spouse_ses = 0.0
    if head_index is not None:
        head_spouse_ses += result["income_person_ses_monthly"].get(head_index, 0.0)
    if spouse_index is not None:
        head_spouse_ses += result["income_person_ses_monthly"].get(spouse_index, 0.0)
    result["income_head_and_spouse_ses_monthly"] = head_spouse_ses

    # Owners income
    owners_yearly = 0.0
    for i, person in enumerate(persons):
        if person.living_owner_on_deed:
            owners_yearly += result["income_person_yearly"].get(i, 0.0)
    result["income_owners_total_yearly"] = owners_yearly

    # Adults and children income
    adults_children_monthly = 0.0
    adult_types = [
        HouseholdMemberType.HEAD_OF_HOUSEHOLD,
        HouseholdMemberType.SPOUSE,
        HouseholdMemberType.CHILD,
        HouseholdMemberType.STEP_CHILD,
    ]
    for i, person in enumerate(persons):
        if person.household_member_type in adult_types:
            adults_children_monthly += result["income_person_monthly"].get(i, 0.0)
    result["income_adults_children_total_monthly"] = adults_children_monthly

    # Child care voucher income
    ccv_monthly = 0.0
    for i, person in enumerate(persons):
        if person.household_member_type != HouseholdMemberType.FOSTER_CHILD:
            ccv_monthly += result["income_person_monthly"].get(i, 0.0)
    result["income_child_care_voucher_total_monthly"] = ccv_monthly

    # Adults total income (household minus children's wages)
    adults_total = result["income_household_total_monthly"]
    for i, person in enumerate(persons):
        if person.household_member_type in [
            HouseholdMemberType.CHILD,
            HouseholdMemberType.STEP_CHILD,
        ]:
            adults_total -= result["income_person_wage_self_employment_monthly"].get(
                i, 0.0
            )
    result["income_adults_total_monthly"] = adults_total

    # Income boolean flags
    has_cash_assistance = False
    has_ui = False
    has_benefit = False
    has_ssi = False

    for person in persons:
        for income in person.incomes:
            if income.type == IncomeType.CASH_ASSISTANCE:
                has_cash_assistance = True
            if income.type == IncomeType.UNEMPLOYMENT:
                has_ui = True
            if income.type in [
                IncomeType.VETERAN,
                IncomeType.SSI,
                IncomeType.SS_RETIREMENT,
                IncomeType.SS_DISABILITY,
                IncomeType.SS_SURVIVOR,
            ]:
                has_benefit = True
            if income.type == IncomeType.SSI:
                has_ssi = True

    result["income_household_has_cash_assistance"] = has_cash_assistance
    result["income_household_has_ui"] = has_ui
    result["income_household_has_benefit"] = has_benefit
    result["income_household_has_ssi"] = has_ssi

    # Expense aggregates
    child_dependent_care_monthly = 0.0
    medical_monthly = 0.0
    rent_mortgage_monthly = 0.0
    rent_monthly = 0.0
    child_support_monthly = 0.0
    has_heating = False
    has_dependent_care = False

    for person in persons:
        for expense in person.expenses:
            monthly_amount = to_monthly(expense.amount, expense.frequency)

            if expense.type in [ExpenseType.CHILD_CARE, ExpenseType.DEPENDENT_CARE]:
                child_dependent_care_monthly += monthly_amount
            if expense.type == ExpenseType.MEDICAL:
                medical_monthly += monthly_amount
            if expense.type in [ExpenseType.RENT, ExpenseType.MORTGAGE]:
                rent_mortgage_monthly += monthly_amount
            if expense.type == ExpenseType.RENT:
                rent_monthly += monthly_amount
            if expense.type == ExpenseType.CHILD_SUPPORT:
                child_support_monthly += monthly_amount
            if expense.type == ExpenseType.HEATING:
                has_heating = True
            if expense.type == ExpenseType.DEPENDENT_CARE:
                has_dependent_care = True

    result["expense_household_child_dependent_care_monthly"] = (
        child_dependent_care_monthly
    )
    result["expense_household_medical_monthly"] = medical_monthly
    result["expense_household_rent_mortgage_monthly"] = rent_mortgage_monthly
    result["expense_household_rent_monthly"] = rent_monthly
    result["expense_household_child_support_monthly"] = child_support_monthly
    result["expense_household_has_heating"] = has_heating
    result["expense_household_has_dependent_care"] = has_dependent_care
    result["expense_household_has_child_or_dependent_care"] = (
        child_dependent_care_monthly > 0
    )

    return result 