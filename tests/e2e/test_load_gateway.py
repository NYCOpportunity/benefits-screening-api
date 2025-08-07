import json
import time
import requests
import concurrent.futures
from pathlib import Path
from typing import Dict, List, Optional
import random


class TestLoadGateway:
    GATEWAY_URL = "GATEWAY_URL_REMOVED"
    NUM_REQUESTS = 100
    MAX_WORKERS = 10

    def load_test_payload(self, filename: str) -> Dict:
        test_data_path = Path(__file__).parent.parent / "data" / "payloads"/ filename
        with open(test_data_path, 'r') as f:
            return json.load(f)
    
    def get_all_payload_files(self) -> List[Path]:
        data_dir = Path(__file__).parent.parent / "data" / "payloads"
        payload_files = []
        
        payload_files.extend(data_dir.glob("eligibility-program-test-payload.json"))
        payload_files.extend(data_dir.glob("invalid-eligibility-payload.json"))
        payload_files.extend(data_dir.glob("converted-payload-*.json"))
        
        return sorted(payload_files)
    
    def load_all_payloads(self) -> List[Dict]:
        payload_files = self.get_all_payload_files()
        payloads = []
        
        for filepath in payload_files:
            try:
                with open(filepath, 'r') as f:
                    payload = json.load(f)
                    payloads.append({
                        'filename': filepath.name,
                        'data': payload
                    })
            except Exception as e:
                print(f"Error loading {filepath.name}: {e}")
        
        return payloads

    def send_request(self, payload: Dict, request_id: int, payload_name: str = "") -> Dict:
        start_time = time.time()
        try:
            response = requests.post(
                self.GATEWAY_URL,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            elapsed_time = time.time() - start_time
            return {
                'request_id': request_id,
                'payload_name': payload_name,
                'status_code': response.status_code,
                'elapsed_time': elapsed_time,
                'response_body': response.text[:500],
                'success': True
            }
        except Exception as e:
            elapsed_time = time.time() - start_time
            return {
                'request_id': request_id,
                'payload_name': payload_name,
                'status_code': None,
                'elapsed_time': elapsed_time,
                'error': str(e),
                'success': False
            }

    def run_load_test(self, payload: Dict, test_name: str) -> None:
        print(f"\n{'='*60}")
        print(f"Starting {test_name}")
        print(f"{'='*60}")
        print(f"Sending {self.NUM_REQUESTS} requests to: {self.GATEWAY_URL}")
        print(f"Using {self.MAX_WORKERS} concurrent workers\n")

        results = []
        start_time = time.time()

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            futures = [
                executor.submit(self.send_request, payload, i)
                for i in range(self.NUM_REQUESTS)
            ]
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results.append(result)
                if result['request_id'] % 10 == 0:
                    print(f"Completed {result['request_id'] + 1}/{self.NUM_REQUESTS} requests")

        total_time = time.time() - start_time
        self.print_statistics(results, total_time, test_name)

    def print_statistics(self, results: List[Dict], total_time: float, test_name: str) -> None:
        successful_requests = [r for r in results if r['success']]
        failed_requests = [r for r in results if not r['success']]
        
        print(f"\n{test_name} Results:")
        print(f"{'='*60}")
        print(f"Total requests: {len(results)}")
        print(f"Successful: {len(successful_requests)}")
        print(f"Failed: {len(failed_requests)}")
        print(f"Total time: {total_time:.2f} seconds")
        print(f"Requests per second: {len(results) / total_time:.2f}")
        
        if successful_requests:
            response_times = [r['elapsed_time'] for r in successful_requests]
            avg_time = sum(response_times) / len(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            
            print(f"\nResponse Time Statistics:")
            print(f"  Average: {avg_time:.3f} seconds")
            print(f"  Min: {min_time:.3f} seconds")
            print(f"  Max: {max_time:.3f} seconds")
            
            status_codes = {}
            for r in successful_requests:
                code = r['status_code']
                status_codes[code] = status_codes.get(code, 0) + 1
            
            print(f"\nStatus Code Distribution:")
            for code, count in sorted(status_codes.items()):
                print(f"  {code}: {count} requests")
        
        if failed_requests:
            print(f"\nFailed Requests Details:")
            for r in failed_requests[:5]:
                print(f"  Request {r['request_id']}: {r.get('error', 'Unknown error')}")
            if len(failed_requests) > 5:
                print(f"  ... and {len(failed_requests) - 5} more failed requests")

    def test_load_valid_payload(self):
        payload = self.load_test_payload("eligibility-program-test-payload.json")
        self.run_load_test(payload, "Valid Payload Load Test")

    def test_load_invalid_payload(self):
        payload = self.load_test_payload("invalid-eligibility-payload.json")
        self.run_load_test(payload, "Invalid Payload Load Test")

    def test_load_both_payloads(self):
        print("\n" + "="*60)
        print("RUNNING COMPLETE LOAD TEST SUITE")
        print("="*60)
        
        self.test_load_valid_payload()
        print("\nWaiting 5 seconds before next test...\n")
        time.sleep(5)
        self.test_load_invalid_payload()
        
        print("\n" + "="*60)
        print("LOAD TEST SUITE COMPLETE")
        print("="*60)
    
    def run_load_test_all_payloads(self) -> None:
        all_payloads = self.load_all_payloads()
        
        if not all_payloads:
            print("No payload files found!")
            return
        
        print(f"\n{'='*60}")
        print(f"LOAD TEST WITH ALL PAYLOADS")
        print(f"{'='*60}")
        print(f"Found {len(all_payloads)} payload files")
        print(f"Sending {self.NUM_REQUESTS} total requests")
        print(f"Using {self.MAX_WORKERS} concurrent workers\n")
        
        for i, payload_info in enumerate(all_payloads):
            print(f"  {i+1}. {payload_info['filename']}")
        
        results = []
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.MAX_WORKERS) as executor:
            futures = []
            for i in range(self.NUM_REQUESTS):
                payload_info = all_payloads[i % len(all_payloads)]
                future = executor.submit(
                    self.send_request, 
                    payload_info['data'], 
                    i,
                    payload_info['filename']
                )
                futures.append(future)
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                results.append(result)
                if len(results) % 10 == 0:
                    print(f"Completed {len(results)}/{self.NUM_REQUESTS} requests")
        
        total_time = time.time() - start_time
        self.print_statistics_with_payloads(results, total_time)
    
    def print_statistics_with_payloads(self, results: List[Dict], total_time: float) -> None:
        successful_requests = [r for r in results if r['success']]
        failed_requests = [r for r in results if not r['success']]
        
        print(f"\nLoad Test Results:")
        print(f"{'='*60}")
        print(f"Total requests: {len(results)}")
        print(f"Successful: {len(successful_requests)}")
        print(f"Failed: {len(failed_requests)}")
        print(f"Total time: {total_time:.2f} seconds")
        print(f"Requests per second: {len(results) / total_time:.2f}")
        
        if successful_requests:
            response_times = [r['elapsed_time'] for r in successful_requests]
            avg_time = sum(response_times) / len(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            
            print(f"\nResponse Time Statistics:")
            print(f"  Average: {avg_time:.3f} seconds")
            print(f"  Min: {min_time:.3f} seconds")
            print(f"  Max: {max_time:.3f} seconds")
            
            status_codes = {}
            for r in successful_requests:
                code = r['status_code']
                status_codes[code] = status_codes.get(code, 0) + 1
            
            print(f"\nStatus Code Distribution:")
            for code, count in sorted(status_codes.items()):
                print(f"  {code}: {count} requests")
            
            payload_stats = {}
            for r in successful_requests:
                name = r.get('payload_name', 'unknown')
                if name not in payload_stats:
                    payload_stats[name] = {'count': 0, 'status_codes': {}}
                payload_stats[name]['count'] += 1
                code = r['status_code']
                payload_stats[name]['status_codes'][code] = payload_stats[name]['status_codes'].get(code, 0) + 1
            
            print(f"\nPayload Statistics:")
            for name, stats in sorted(payload_stats.items())[:10]:
                print(f"  {name[:50]}:")
                print(f"    Requests: {stats['count']}")
                for code, count in stats['status_codes'].items():
                    print(f"    Status {code}: {count}")
        
        if failed_requests:
            print(f"\nFailed Requests Details:")
            for r in failed_requests[:5]:
                print(f"  Request {r['request_id']} ({r.get('payload_name', 'unknown')[:30]}): {r.get('error', 'Unknown error')}")
            if len(failed_requests) > 5:
                print(f"  ... and {len(failed_requests) - 5} more failed requests")
    
    def test_load_all_payloads_sequential(self) -> None:
        all_payloads = self.load_all_payloads()
        
        if not all_payloads:
            print("No payload files found!")
            return
        
        print(f"\n{'='*60}")
        print(f"SEQUENTIAL LOAD TEST - ALL PAYLOADS")
        print(f"{'='*60}")
        print(f"Testing {len(all_payloads)} different payloads")
        print(f"Each payload will be sent multiple times\n")
        
        for payload_info in all_payloads:
            print(f"\nTesting: {payload_info['filename']}")
            print("-" * 40)
            
            results = []
            requests_per_payload = min(10, self.NUM_REQUESTS // len(all_payloads))
            
            for i in range(requests_per_payload):
                result = self.send_request(payload_info['data'], i, payload_info['filename'])
                results.append(result)
                
            successful = [r for r in results if r['success']]
            failed = [r for r in results if not r['success']]
            
            print(f"  Sent: {len(results)} | Success: {len(successful)} | Failed: {len(failed)}")
            
            if successful:
                status_codes = {}
                for r in successful:
                    code = r['status_code']
                    status_codes[code] = status_codes.get(code, 0) + 1
                
                for code, count in status_codes.items():
                    print(f"  Status {code}: {count}")
            
            if failed:
                print(f"  Errors: {failed[0].get('error', 'Unknown')}")
            
            time.sleep(0.5)


if __name__ == "__main__":
    tester = TestLoadGateway()
    tester.run_load_test_all_payloads()