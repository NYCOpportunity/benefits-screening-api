import json
import re
from pathlib import Path
from typing import Dict, List, Any


class PostmanPayloadExtractor:
    
    def __init__(self, postman_file_path: str):
        self.postman_file_path = Path(postman_file_path)
        self.data_dir = Path(__file__).parent.parent / "data"
        
    def load_postman_collection(self) -> Dict:
        with open(self.postman_file_path, 'r') as f:
            return json.load(f)
    
    def is_matching_payload(self, payload: Any) -> bool:
        if not isinstance(payload, dict):
            return False
        
        has_household = "household" in payload and isinstance(payload.get("household"), list)
        has_person = "person" in payload and isinstance(payload.get("person"), list)
        
        return has_household and has_person
    
    def extract_payload_from_body(self, body_raw: str) -> Dict:
        try:
            cleaned_body = body_raw.replace('\r\n', '\n').replace('\r', '')
            return json.loads(cleaned_body)
        except json.JSONDecodeError:
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
                    
                    if payload and self.is_matching_payload(payload):
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
            filename = f"postman-payload-{i:02d}-{sanitized_name}.json"
            filepath = self.data_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(payload_info['payload'], f, indent=2)
            
            saved_files.append(str(filepath))
            print(f"Saved: {filename}")
            print(f"  From: {payload_info['name']}")
            
        return saved_files
    
    def extract_and_save(self) -> Dict:
        print(f"Loading Postman collection from: {self.postman_file_path}")
        collection = self.load_postman_collection()
        
        print("\nSearching for payloads matching structure...")
        items = collection.get('item', [])
        found_payloads = self.traverse_items(items)
        
        print(f"\nFound {len(found_payloads)} matching payloads")
        
        if found_payloads:
            print("\nPayload details:")
            for i, payload_info in enumerate(found_payloads, 1):
                print(f"{i}. {payload_info['name']}")
                household_count = len(payload_info['payload'].get('household', []))
                person_count = len(payload_info['payload'].get('person', []))
                print(f"   - Household members: {household_count}")
                print(f"   - Person members: {person_count}")
                print(f"   - Has withholdPayload: {'withholdPayload' in payload_info['payload']}")
            
            print("\nSaving payloads to data directory...")
            saved_files = self.save_payloads(found_payloads)
            
            print(f"\nSuccessfully saved {len(saved_files)} payload files")
            
            return {
                'total_found': len(found_payloads),
                'payloads': found_payloads,
                'saved_files': saved_files
            }
        else:
            print("\nNo matching payloads found in the Postman collection")
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
    
    extractor = PostmanPayloadExtractor(str(postman_file))
    results = extractor.extract_and_save()
    
    print("\n" + "="*60)
    print("EXTRACTION COMPLETE")
    print(f"Total payloads extracted: {results['total_found']}")
    print("="*60)


if __name__ == "__main__":
    main()