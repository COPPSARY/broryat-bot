from bot.schemas.breach import BreachCheckResult, BreachRecord


def test_breach_record_holds_expected_fields():
    record = BreachRecord(
        breach="Zomato",
        domain="zomato.com",
        xposed_date="2016",
        xposed_data=["Email addresses", "Passwords"],
        password_risk="easytocrack",
    )

    assert record.breach == "Zomato"
    assert record.xposed_data == ["Email addresses", "Passwords"]


def test_breach_check_result_defaults_to_no_records():
    result = BreachCheckResult(email="test@example.com", found=False)

    assert result.records == []
    assert result.risk_label is None
    assert result.risk_score is None


def test_breach_check_result_with_records():
    record = BreachRecord(
        breach="Sysco", domain="sysco.com", xposed_date="2023",
        xposed_data=["Names"], password_risk="unknown",
    )

    result = BreachCheckResult(
        email="test@example.com", found=True, records=[record],
        risk_label="High", risk_score=8.5,
    )

    assert result.found is True
    assert result.records[0].breach == "Sysco"
    assert result.risk_score == 8.5
