from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.core.constants import DATA_SOURCE_PENDING
from app.providers.http import get_json


class FMPProvider:
    name = "FMP"
    base = "https://financialmodelingprep.com/stable"

    @property
    def configured(self) -> bool:
        return settings.has_fmp

    async def _get(self, path: str, **params: Any) -> Any:
        if not self.configured:
            return None
        params["apikey"] = settings.fmp_api_key
        return await get_json(f"{self.base}/{path.lstrip('/')}", params=params)

    async def quote(self, symbol: str) -> dict | None:
        data = await self._get("quote", symbol=symbol)
        rows = data.get("data", data) if isinstance(data, dict) else data
        return rows[0] if isinstance(rows, list) and rows else None

    async def profile(self, symbol: str) -> dict | None:
        data = await self._get("profile", symbol=symbol)
        rows = data.get("data", data) if isinstance(data, dict) else data
        return rows[0] if isinstance(rows, list) and rows else None

    async def income_statement(self, symbol: str) -> dict | None:
        data = await self._get("income-statement", symbol=symbol, period="annual", limit=1)
        rows = data.get("data", data) if isinstance(data, dict) else data
        return rows[0] if isinstance(rows, list) and rows else None

    async def earnings_calendar(self, from_date: str, to_date: str) -> list[dict]:
        data = await self._get("earnings-calendar", **{"from": from_date, "to": to_date})
        rows = data.get("data", data) if isinstance(data, dict) else data
        return rows if isinstance(rows, list) else []

    def status(self) -> dict:
        return {
            "provider": self.name,
            "configured": self.configured,
            "status": "ok" if self.configured else DATA_SOURCE_PENDING,
            "detail": "用于报价、财务、指数、BTC、财报日历" if self.configured else "缺少 FMP_API_KEY",
        }

