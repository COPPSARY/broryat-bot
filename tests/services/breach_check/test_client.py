import httpx
import pytest
import respx

from bot.services.breach_check.client import BreachCheckClient, BreachCheckError

EMAIL = "test@example.com"
BASE_URL = "https://api.xposedornot.com/v1/breach-analytics"


@pytest.fixture
def client():
    return BreachCheckClient()


@respx.mock
async def test_check_parses_breaches_found(client):
    respx.get(BASE_URL, params={"email": EMAIL}).mock(
        return_value=httpx.Response(
            200,
            json={
                "BreachMetrics": {"risk": [{"risk_score": 8.5, "risk_label": "High"}]},
                "ExposedBreaches": {
                    "breaches_details": [
                        {
                            "breach": "Zomato",
                            "domain": "zomato.com",
                            "xposed_date": "2016",
                            "xposed_data": "Email addresses;Passwords",
                            "password_risk": "easytocrack",
                        }
                    ]
                },
            },
        )
    )

    result = await client.check(EMAIL)

    assert result.found is True
    assert result.email == EMAIL
    assert result.risk_label == "High"
    assert result.risk_score == 8.5
    assert len(result.records) == 1
    assert result.records[0].breach == "Zomato"
    assert result.records[0].xposed_data == ["Email addresses", "Passwords"]
    assert result.records[0].password_risk == "easytocrack"


@respx.mock
async def test_check_returns_not_found_when_api_returns_404(client):
    respx.get(BASE_URL, params={"email": EMAIL}).mock(return_value=httpx.Response(404))

    result = await client.check(EMAIL)

    assert result.found is False
    assert result.records == []


@respx.mock
async def test_check_handles_null_exposed_breaches_and_null_breach_metrics(client):
    respx.get(BASE_URL, params={"email": EMAIL}).mock(
        return_value=httpx.Response(200, json={"ExposedBreaches": None, "BreachMetrics": None})
    )

    result = await client.check(EMAIL)

    assert result.found is False
    assert result.records == []
    assert result.risk_label is None
    assert result.risk_score is None


@respx.mock
async def test_check_raises_breach_check_error_on_server_error(client):
    respx.get(BASE_URL, params={"email": EMAIL}).mock(return_value=httpx.Response(500))

    with pytest.raises(BreachCheckError):
        await client.check(EMAIL)


@respx.mock
async def test_check_raises_breach_check_error_on_timeout(client):
    respx.get(BASE_URL, params={"email": EMAIL}).mock(side_effect=httpx.TimeoutException("timed out"))

    with pytest.raises(BreachCheckError):
        await client.check(EMAIL)
