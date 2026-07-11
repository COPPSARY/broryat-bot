import httpx

from bot.schemas.breach import BreachCheckResult, BreachRecord

_BASE_URL = "https://api.xposedornot.com/v1"
_DEFAULT_TIMEOUT = httpx.Timeout(30.0, connect=15.0)


class BreachCheckError(Exception):
    pass


class BreachCheckClient:
    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client or httpx.AsyncClient(base_url=_BASE_URL, timeout=_DEFAULT_TIMEOUT)

    async def check(self, email: str) -> BreachCheckResult:
        try:
            response = await self._client.get("/breach-analytics", params={"email": email})
        except httpx.HTTPError as exc:
            raise BreachCheckError(f"breach check request failed for {email}") from exc

        if response.status_code == 404:
            return BreachCheckResult(email=email, found=False)

        if response.status_code >= 400:
            raise BreachCheckError(f"breach check failed with status {response.status_code}")

        data = response.json()
        details = (data.get("ExposedBreaches") or {}).get("breaches_details") or []
        records = [
            BreachRecord(
                breach=item["breach"],
                domain=item["domain"],
                xposed_date=item["xposed_date"],
                xposed_data=[part for part in item["xposed_data"].split(";") if part],
                password_risk=item["password_risk"],
            )
            for item in details
        ]

        risk_entries = (data.get("BreachMetrics") or {}).get("risk") or []
        risk_label = risk_entries[0]["risk_label"] if risk_entries else None
        risk_score = risk_entries[0]["risk_score"] if risk_entries else None

        return BreachCheckResult(
            email=email,
            found=len(records) > 0,
            records=records,
            risk_label=risk_label,
            risk_score=risk_score,
        )
