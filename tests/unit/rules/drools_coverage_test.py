from src.rules.registry import get_rule_codes


ACTIVE_PUBLIC_DROOLS_RULE_CODES = {
    "S2R001",
    "S2R003",
    "S2R004",
    "S2R005",
    "S2R006",
    "S2R007",
    "S2R008",
    "S2R009",
    "S2R010",
    "S2R011",
    "S2R012",
    "S2R013",
    "S2R014",
    "S2R015",
    "S2R016",
    "S2R017",
    "S2R018",
    "S2R019",
    "S2R021",
    "S2R022",
    "S2R023",
    "S2R024",
    "S2R025",
    "S2R026",
    "S2R027",
    "S2R028",
    "S2R029",
    "S2R030",
    "S2R031",
    "S2R032",
    "S2R033",
    "S2R034",
    "S2R035",
    "S2R036",
    "S2R037",
    "S2R038",
    "S2R039",
    "S2R040",
    "S2R043",
    "S2R045",
    "S2R046",
    "S2R047",
    "S2R054",
    "S2R055",
    "S2R056",
    "S2R057",
    "S2R058",
    "S2R059",
    "S2R060",
    "S2R085",
}

INACTIVE_PUBLIC_DROOLS_RULE_CODES = {
    # S2R020 exists in ACCESS-NYC-Rules, but the EligibleProgram insert is
    # commented out in both rules.
    "S2R020",
    # S2R053 exists in ACCESS-NYC-Rules, but it stopped accepting applications
    # in 2024 and the EligibleProgram inserts are commented out in both rules.
    "S2R053",
}

KNOWN_REGISTERED_INACTIVE_PUBLIC_DROOLS_RULE_CODES = {
    # Existing implementation predating this coverage test. Keep documented
    # until a separate cleanup decides whether to remove it or expose it as
    # historical-only.
    "S2R053",
}


def test_registered_rules_cover_active_public_drools_codes():
    registered_codes = set(get_rule_codes())

    assert ACTIVE_PUBLIC_DROOLS_RULE_CODES <= registered_codes
    assert not (
        registered_codes
        - ACTIVE_PUBLIC_DROOLS_RULE_CODES
        - KNOWN_REGISTERED_INACTIVE_PUBLIC_DROOLS_RULE_CODES
    )
    assert registered_codes.isdisjoint(
        INACTIVE_PUBLIC_DROOLS_RULE_CODES
        - KNOWN_REGISTERED_INACTIVE_PUBLIC_DROOLS_RULE_CODES
    )
