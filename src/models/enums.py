'''
This replatforms original src/api/validationSchemas/constants.js

Define fixed-value enums (income types, frequencies, etc.)
'''

from enum import Enum




class LivingRentalType(str, Enum):
    """Corresponds to `livingRentalTypeValues`"""
    NYCHA = "NYCHA"
    MARKET_RATE = "MarketRate"
    RENT_CONTROLLED = "RentControlled"
    RENT_REGULATED_HOTEL = "RentRegulatedHotel"
    SECTION_213 = "Section213"
    LIMITED_DIVIDEND_DEVELOPMENT = "LimitedDividendDevelopment"

    MITCHELL_LAMA = "MitchellLama"
    REDEVELOPMENT_COMPANY = "RedevelopmentCompany"
    HDFC = "HDFC"
    FAMILY_HOME = "FamilyHome"
    CONDO = "Condo"


class IncomeType(str, Enum):
    """Corresponds to `incomeTypeValues`"""
    WAGES = "Wages"
    SELF_EMPLOYMENT = "SelfEmployment"
    UNEMPLOYMENT = "Unemployment"
    CASH_ASSISTANCE = "CashAssistance"
    CHILD_SUPPORT = "ChildSupport"
    DISABILITY_MEDICAID = "DisabilityMedicaid"
    SSI = "SSI"
    SS_DEPENDENT = "SSDependent"
    SS_DISABILITY = "SSDisability"
    SS_SURVIVOR = "SSSurvivor"
    SS_RETIREMENT = "SSRetirement"
    NYS_DISABILITY = "NYSDisability"
    VETERAN = "Veteran"
    PENSION = "Pension"
    DEFERRED_COMP = "DeferredComp"
    WORKERS_COMP = "WorkersComp"
    ALIMONY = "Alimony"
    BOARDER = "Boarder"
    GIFTS = "Gifts"
    RENTAL = "Rental"
    INVESTMENT = "Investment"


class ExpenseType(str, Enum):
    """Corresponds to `expenseTypeValues`"""
    CHILD_CARE = "ChildCare"
    CHILD_SUPPORT = "ChildSupport"
    DEPENDENT_CARE = "DependentCare"
    RENT = "Rent"
    MEDICAL = "Medical"
    HEATING = "Heating"
    COOLING = "Cooling"
    MORTGAGE = "Mortgage"
    UTILITIES = "Utilities"
    TELEPHONE = "Telephone"
    INSURANCE_PREMIUMS = "InsurancePremiums"


class Frequency(str, Enum):
    """Corresponds to `frequencyValues`"""
    WEEKLY = "Weekly"
    BIWEEKLY = "Biweekly"
    MONTHLY = "Monthly"
    SEMIMONTHLY = "Semimonthly"
    YEARLY = "Yearly"


class HouseholdMemberType(str, Enum):
    """Corresponds to `householdMemberTypeValues`"""
    HEAD_OF_HOUSEHOLD = "HeadOfHousehold"
    CHILD = "Child"
    FOSTER_CHILD = "FosterChild"
    STEP_CHILD = "StepChild"
    GRANDCHILD = "Grandchild"
    SPOUSE = "Spouse"
    PARENT = "Parent"
    FOSTER_PARENT = "FosterParent"
    STEP_PARENT = "StepParent"
    GRANDPARENT = "Grandparent"
    SISTER_BROTHER = "SisterBrother"
    STEP_SISTER_STEP_BROTHER = "StepSisterStepBrother"
    BOYFRIEND_GIRLFRIEND = "BoyfriendGirlfriend"
    DOMESTIC_PARTNER = "DomesticPartner"
    UNRELATED = "Unrelated"
    OTHER = "Other"