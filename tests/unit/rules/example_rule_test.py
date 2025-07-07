from src.rules.example_rule import PlaceholderSnapRule
from tests.data.sample_eligibility_rule import sample_eligibility_rule

def test_placeholder_snap_rule():
    # conceptual grasp over how to unit test the rules efficiently

    eligibility_request = sample_eligibility_rule()

    assert PlaceholderSnapRule.evaluate(eligibility_request) == False 
