from bot.schemas.enums import RiskLevel


def test_risk_level_has_four_members_matching_prd_taxonomy():
    assert {member.value for member in RiskLevel} == {"SAFE", "LOW", "MEDIUM", "HIGH"}


def test_risk_level_ordering_reflects_severity():
    assert RiskLevel.SAFE < RiskLevel.LOW < RiskLevel.MEDIUM < RiskLevel.HIGH
