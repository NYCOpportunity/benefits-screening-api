# control the main flow. this will bring together all components of the application.

from validation.validate_request import validate_request
import json

def main():
    # read the json w user info from the aws gateway 
    # currently just testing data
    userInfo = 'tests/data/eligibility-program-test-payload.json'
    try: 
        with open(userInfo, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Test file not found at {userInfo}")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in test file: {e}")
        return
    is_valid, result = validate_request(data)
    print(is_valid)
    print(result)

if __name__ == "__main__":
    main()


