"""Parse raw request dicts into typed models for rule evaluation."""

from typing import Dict

from src.models.schemas import EligibilityRequest

INVALID_PAYLOAD_MESSAGE = 'Invalid eligibility request payload'


def parse_request(request: Dict) -> EligibilityRequest:
    """
    Parse and coerce a request dict into an EligibilityRequest.

    Public API validation runs in screeningapi before Lambda invoke. This parse
    step types/coerces data for rules and guards direct or legacy invoke paths.
    """
    return EligibilityRequest(**request)
