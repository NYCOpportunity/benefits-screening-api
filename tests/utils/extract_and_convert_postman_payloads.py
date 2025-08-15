import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional


class PostmanPayloadConverter:
    
    def __init__(self, postman_file_path: str):
        self.postman_file_path = Path(postman_file_path)
        self.data_dir = Path(__file__).parent.parent / "data"
        
    def load_postman_collection(self) -> Dict:
        with open(self.postman_file_path, 'r') as f:
            return json.load(f)
    
    def convert_boolean_string(self, value: str) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() == "true"
        return False
    
    def convert_to_number(self, value: Any) -> Optional[float]:
        if value is None or value == "":
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def convert_household(self, old_household: Dict) -> Dict:
        household = {}
        
        if 'cashOnHand' in old_household:
            cash = self.convert_to_number(old_household['cashOnHand'])
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
                household[field] = self.convert_boolean_string(old_household[field])
        
        return household
    
    def convert_person(self, old_person: Dict) -> Dict:
        person = {}
        
        if 'age' in old_person:
            age = self.convert_to_number(old_person['age'])
            if age is not None:
                person['age'] = int(age)
        
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
                person[field] = self.convert_boolean_string(old_person[field])
        
        if 'incomes' in old_person and isinstance(old_person['incomes'], list):
            incomes = []
            for income in old_person['incomes']:
                converted_income = {}
                if 'amount' in income:
                    amount = self.convert_to_number(income['amount'])
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
        
        if 'expenses' in old_person and isinstance(old_person['expenses'], list):
            expenses = []
            for expense in old_person['expenses']:
                converted_expense = {}
                if 'amount' in expense:
                    amount = self.convert_to_number(expense['amount'])
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
    
    def extract_payload_from_body(self, body_raw: str) -> Optional[Dict]:
        try:
            cleaned_body = body_raw.replace('\r\n', '\n').replace('\r', '')
            data = json.loads(cleaned_body)
            
            if 'commands' in data and isinstance(data['commands'], list):
                household_data = None
                persons_data = []
                
                for command in data['commands']:
                    if 'insert' in command and 'object' in command['insert']:
                        obj = command['insert']['object']
                        
                        if 'accessnyc.request.Household' in obj:
                            household_data = obj['accessnyc.request.Household']
                        elif 'accessnyc.request.Person' in obj:
                            persons_data.append(obj['accessnyc.request.Person'])
                
                if household_data or persons_data:
                    converted_payload = {}
                    
                    if household_data:
                        converted_household = self.convert_household(household_data)
                        if converted_household:
                            converted_payload['household'] = [converted_household]
                    else:
                        converted_payload['household'] = []
                    
                    if persons_data:
                        converted_persons = []
                        for person_data in persons_data:
                            converted_person = self.convert_person(person_data)
                            if converted_person:
                                converted_persons.append(converted_person)
                        if converted_persons:
                            converted_payload['person'] = converted_persons
                    else:
                        converted_payload['person'] = []
                    
                    converted_payload['withholdPayload'] = True
                    
                    return converted_payload
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"  Error parsing payload: {e}")
        
        return None
    
    def traverse_items(self, items: List, parent_path: str = "") -> List[Dict]:
        found_payloads = []
        
        for item in items:
            current_path = f"{parent_path}/{item.get('name', 'unnamed')}" if parent_path else item.get('name', 'unnamed')
            
            if 'item' in item:
                found_payloads.extend(self.traverse_items(item['item'], current_path))
            
            if 'request' in item and 'body' in item['request']:
                body = item['request'].get('body', {})
                
                if body.get('mode') == 'raw':
                    raw_body = body.get('raw', '')
                    payload = self.extract_payload_from_body(raw_body)
                    
                    if payload:
                        found_payloads.append({
                            'name': current_path,
                            'payload': payload,
                            'url': item['request'].get('url', {})
                        })
        
        return found_payloads
    
    def sanitize_filename(self, name: str) -> str:
        name = re.sub(r'[^\w\s-]', '', name)
        name = re.sub(r'[-\s]+', '-', name)
        return name.lower()[:100]
    
    def save_payloads(self, payloads: List[Dict]) -> List[str]:
        saved_files = []
        
        for i, payload_info in enumerate(payloads, 1):
            sanitized_name = self.sanitize_filename(payload_info['name'])
            filename = f"converted-payload-{i:02d}-{sanitized_name}.json"
            filepath = self.data_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(payload_info['payload'], f, indent=2)
            
            saved_files.append(str(filepath))
            print(f"Saved: {filename}")
            print(f"  From: {payload_info['name']}")
            
        return saved_files
    
    def extract_and_convert(self) -> Dict:
        print(f"Loading Postman collection from: {self.postman_file_path}")
        collection = self.load_postman_collection()
        
        print("\nSearching for payloads to convert...")
        items = collection.get('item', [])
        found_payloads = self.traverse_items(items)
        
        print(f"\nFound and converted {len(found_payloads)} payloads")
        
        if found_payloads:
            print("\nConverted payload details:")
            for i, payload_info in enumerate(found_payloads, 1):
                print(f"{i}. {payload_info['name']}")
                household_count = len(payload_info['payload'].get('household', []))
                person_count = len(payload_info['payload'].get('person', []))
                print(f"   - Household members: {household_count}")
                print(f"   - Person members: {person_count}")
            
            print("\nSample of first converted payload:")
            print(json.dumps(found_payloads[0]['payload'], indent=2)[:500] + "...")
            
            print("\nSaving converted payloads to data directory...")
            saved_files = self.save_payloads(found_payloads)
            
            print(f"\nSuccessfully saved {len(saved_files)} converted payload files")
            
            return {
                'total_found': len(found_payloads),
                'payloads': found_payloads,
                'saved_files': saved_files
            }
        else:
            print("\nNo payloads found to convert in the Postman collection")
            return {
                'total_found': 0,
                'payloads': [],
                'saved_files': []
            }


def main():
    postman_file = Path(__file__).parent.parent / "data" / "Benefit Eligibility API Tests Copy.postman_collection.json"
    
    if not postman_file.exists():
        print(f"Error: Postman collection not found at {postman_file}")
        return
    
    converter = PostmanPayloadConverter(str(postman_file))
    results = converter.extract_and_convert()
    
    print("\n" + "="*60)
    print("CONVERSION COMPLETE")
    print(f"Total payloads converted: {results['total_found']}")
    print("="*60)


if __name__ == "__main__":
    main()