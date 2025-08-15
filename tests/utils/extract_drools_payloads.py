import json
import re
from pathlib import Path
from typing import Dict, List, Any


class DroolsPayloadExtractor:
    
    def __init__(self, postman_file_path: str):
        self.postman_file_path = Path(postman_file_path)
        self.output_dir = Path(__file__).parent.parent / "data" / "legacy-drools-payloads"
        
    def load_postman_collection(self) -> Dict:
        with open(self.postman_file_path, 'r') as f:
            return json.load(f)
    
    def extract_drools_payload(self, body_raw: str) -> Dict:
        """Extract the raw Drools format payload from Postman body."""
        try:
            cleaned_body = body_raw.replace('\r\n', '\n').replace('\r', '')
            payload = json.loads(cleaned_body)
            
            # Check if this is a Drools format payload
            if 'commands' in payload and isinstance(payload['commands'], list):
                return payload
            
        except json.JSONDecodeError:
            pass
        
        return None
    
    def traverse_items(self, items: List, parent_path: str = "") -> List[Dict]:
        """Traverse Postman collection items and extract Drools payloads."""
        found_payloads = []
        
        for item in items:
            current_path = f"{parent_path}/{item.get('name', 'unnamed')}" if parent_path else item.get('name', 'unnamed')
            
            # Recursively process nested items
            if 'item' in item:
                found_payloads.extend(self.traverse_items(item['item'], current_path))
            
            # Extract payload from request body
            if 'request' in item and 'body' in item['request']:
                body = item['request'].get('body', {})
                
                if body.get('mode') == 'raw':
                    raw_body = body.get('raw', '')
                    payload = self.extract_drools_payload(raw_body)
                    
                    if payload:
                        found_payloads.append({
                            'name': current_path,
                            'payload': payload,
                            'url': item['request'].get('url', {})
                        })
        
        return found_payloads
    
    def sanitize_filename(self, name: str) -> str:
        """Create a safe filename from the test name."""
        # Remove the parent path parts, keep only the test name
        if '/' in name:
            name = name.split('/')[-1]
        
        # Remove special characters and clean up
        name = re.sub(r'[^\w\s-]', '', name)
        name = re.sub(r'[-\s]+', '-', name)
        return name.lower()[:100]
    
    def save_payloads(self, payloads: List[Dict]) -> List[str]:
        """Save extracted Drools payloads to individual JSON files."""
        saved_files = []
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        for i, payload_info in enumerate(payloads, 1):
            sanitized_name = self.sanitize_filename(payload_info['name'])
            filename = f"drools-payload-{i:03d}-{sanitized_name}.json"
            filepath = self.output_dir / filename
            
            with open(filepath, 'w') as f:
                json.dump(payload_info['payload'], f, indent=2)
            
            saved_files.append(str(filepath))
            print(f"Saved: {filename}")
            print(f"  From: {payload_info['name']}")
            
        return saved_files
    
    def extract_and_save(self) -> Dict:
        """Main method to extract and save all Drools payloads."""
        print(f"Loading Postman collection from: {self.postman_file_path}")
        collection = self.load_postman_collection()
        
        print("\nSearching for Drools format payloads...")
        items = collection.get('item', [])
        found_payloads = self.traverse_items(items)
        
        print(f"\nFound {len(found_payloads)} Drools format payloads")
        
        if found_payloads:
            print("\nPayload details:")
            for i, payload_info in enumerate(found_payloads, 1):
                print(f"{i}. {payload_info['name']}")
                commands_count = len(payload_info['payload'].get('commands', []))
                print(f"   - Commands: {commands_count}")
            
            print(f"\nSaving payloads to {self.output_dir}...")
            saved_files = self.save_payloads(found_payloads)
            
            print(f"\nSuccessfully saved {len(saved_files)} Drools payload files")
            
            return {
                'total_found': len(found_payloads),
                'payloads': found_payloads,
                'saved_files': saved_files
            }
        else:
            print("\nNo Drools format payloads found in the Postman collection")
            return {
                'total_found': 0,
                'payloads': [],
                'saved_files': []
            }


def main():
    """Main function to run the extraction."""
    postman_file = Path(__file__).parent.parent / "data" / "_drools-postman.json"
    
    if not postman_file.exists():
        print(f"Error: Postman collection not found at {postman_file}")
        return
    
    extractor = DroolsPayloadExtractor(str(postman_file))
    results = extractor.extract_and_save()
    
    print("\n" + "="*60)
    print("EXTRACTION COMPLETE")
    print(f"Total Drools payloads extracted: {results['total_found']}")
    print("="*60)


if __name__ == "__main__":
    main()