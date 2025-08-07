"""
This module is used to convert the legacy Drools command format payload to the API expected format

This is just a quick fix so that no frontend changes are needed. 
"""

from typing import Dict, List, Any, Optional

def convert_drools_to_api_format(drools_payload: Dict) -> Optional[Dict]:
    
    if 'commands' not in drools_payload or not isinstance(drools_payload['commands'], list):
        return None
    
    household_data = None
    persons_data = []
    
    # Extract household and person data from commands
    for command in drools_payload['commands']:
        if 'insert' in command and 'object' in command['insert']:
            obj = command['insert']['object']
            
            if 'accessnyc.request.Household' in obj:
                household_data = obj['accessnyc.request.Household']
            elif 'accessnyc.request.Person' in obj:
                persons_data.append(obj['accessnyc.request.Person'])
    
    if not household_data and not persons_data:
        return None
    
    # Build converted payload
    converted_payload = {}
    
    if household_data:
        converted_household = _convert_household(household_data)
        if converted_household:
            converted_payload['household'] = [converted_household]
    else:
        converted_payload['household'] = []
    
    if persons_data:
        converted_persons = []
        for person_data in persons_data:
            converted_person = _convert_person(person_data)
            if converted_person:
                converted_persons.append(converted_person)
        if converted_persons:
            converted_payload['person'] = converted_persons
    else:
        converted_payload['person'] = []
    
    converted_payload['withholdPayload'] = True
    
    return converted_payload


def _convert_boolean_string(value: Any) -> bool:
    """Convert string boolean to actual boolean."""
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() == "true"
    return False


def _convert_to_number(value: Any) -> Optional[float]:
    """Convert string number to float."""
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _convert_household(old_household: Dict) -> Dict:
    """Convert household data from Drools format to API format."""
    household = {}
    
    if 'cashOnHand' in old_household:
        cash = _convert_to_number(old_household['cashOnHand'])
        if cash is not None:
            household['cashOnHand'] = cash
    
    if 'livingRentalType' in old_household:
        household['livingRentalType'] = old_household['livingRentalType']
    
    boolean_fields = [
        'livingPreferNotToSay', 'livingRenting', 'livingOwner',
        'livingStayingWithFriend', 'livingHotel', 'livingShelter'
    ]
    
    for field in boolean_fields:
        if field in old_household:
            household[field] = _convert_boolean_string(old_household[field])
    
    return household


def _convert_person(old_person: Dict) -> Dict:
    """Convert person data from Drools format to API format."""
    person = {}
    
    if 'age' in old_person:
        age = _convert_to_number(old_person['age'])
        if age is not None:
            person['age'] = int(age)
    
    # Determine household member type
    if 'applicant' in old_person or 'headOfHousehold' in old_person:
        is_hoh = old_person.get('applicant') == 'true' or old_person.get('headOfHousehold') == 'true'
        person['householdMemberType'] = 'HeadOfHousehold' if is_hoh else 'HouseholdMember'
    
    boolean_fields = [
        'student', 'pregnant', 'studentFulltime', 'blind', 'disabled',
        'veteran', 'unemployed', 'unemployedWorkedLast18Months',
        'benefitsMedicaid', 'benefitsMedicaidDisability',
        'livingOwnerOnDeed', 'livingRentalOnLease'
    ]
    
    for field in boolean_fields:
        if field in old_person:
            person[field] = _convert_boolean_string(old_person[field])
    
    # Convert incomes
    if 'incomes' in old_person and isinstance(old_person['incomes'], list):
        incomes = []
        for income in old_person['incomes']:
            converted_income = {}
            if 'amount' in income:
                amount = _convert_to_number(income['amount'])
                if amount is not None:
                    converted_income['amount'] = amount
            if 'type' in income:
                converted_income['type'] = income['type']
            if 'frequency' in income:
                freq = income['frequency']
                converted_income['frequency'] = freq.capitalize() if freq else freq
            if converted_income and 'amount' in converted_income:
                incomes.append(converted_income)
        if incomes:
            person['incomes'] = incomes
    
    # Convert expenses
    if 'expenses' in old_person and isinstance(old_person['expenses'], list):
        expenses = []
        for expense in old_person['expenses']:
            converted_expense = {}
            if 'amount' in expense:
                amount = _convert_to_number(expense['amount'])
                if amount is not None:
                    converted_expense['amount'] = amount
            if 'type' in expense:
                converted_expense['type'] = expense['type']
            if 'frequency' in expense:
                freq = expense['frequency']
                converted_expense['frequency'] = freq.capitalize() if freq else freq
            if converted_expense:
                expenses.append(converted_expense)
        if expenses:
            person['expenses'] = expenses
    
    return person