from typing import Dict, Tuple, Union, List
from pydantic import ValidationError

from .schemas import EligibilityRequest


# func that the lambda will call
def validate_request(request: Dict) -> Tuple[bool, Union[str, List[str]]]:
    """    
    Args:
        request: Dictionary containing the eligibility request data (from JSON)
        
    Returns:
        Tuple containing:
        - bool: True if validation passes, False otherwise
        - Union[str, List[str]]: Success message if valid, or list of error messages if invalid
    """
    try:
        EligibilityRequest(**request)
        return True, "Validation successful"
    except ValidationError as e:
        error_messages = []
        for error in e.errors():
            loc = " -> ".join(str(x) for x in error["loc"])
            msg = error["msg"]
            error_messages.append(f"{loc}: {msg}")
        return False, error_messages
    except Exception as e:
        return False, [f"Unexpected validation error: {str(e)}"]



# if __name__ == "__main__":

#     # note: jsonFile will come from the AWS gateway as a JSONn
#     jsonFile = 'tests/data/eligibility-program-test-payload.json'
#     with open(jsonFile, 'r') as f:
#         data = json.load(f)
#     is_valid, result = validate_request(data)
#     print(is_valid)
#     print(result)
