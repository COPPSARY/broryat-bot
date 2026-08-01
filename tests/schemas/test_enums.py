from bot.schemas.enums import RiskLevel


def test_risk_level_has_five_members_matching_prd_taxonomy():
    assert {member.value for member in RiskLevel} == {"UNKNOWN", "SAFE", "LOW", "MEDIUM", "HIGH"}


def test_risk_level_ordering_reflects_severity():
    assert RiskLevel.UNKNOWN < RiskLevel.SAFE < RiskLevel.LOW < RiskLevel.MEDIUM < RiskLevel.HIGH


def test_risk_level_gte_orders_by_severity_not_string_value():
    # RiskLevel is a str-Enum, so without explicit comparison operators "MEDIUM" >=
    # "HIGH" would compare lexicographically and return True. Severity must win.
    assert RiskLevel.SAFE >= RiskLevel.SAFE
    assert not RiskLevel.SAFE >= RiskLevel.HIGH
    assert RiskLevel.MEDIUM >= RiskLevel.MEDIUM
    assert RiskLevel.HIGH >= RiskLevel.MEDIUM
