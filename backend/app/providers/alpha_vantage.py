from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.core.constants import DATA_SOURCE_PENDING
from app.providers.http import get_json


class AlphaVantageProvider:
    name = "Alpha Vantage"
    base = "https://www.alphavantage.co/query"

    @property
    def configured(self) -> bool:
        return settings.has_alpha_vantage

    async def indicator(self, symbol: str, function: str, time_period: int) -> float | None:
        if not self.configured:
            return None
        data = await get_json(
            self.base,
            params={
                "function": function,
                "symbol": symbol,
                "interval": "daily",
                "time_period": time_period,
                "series_type": "close",
                "apikey": settings.alpha_vantage_api_key,
            },
        )
        key = f"Technical Analysis: {function}"
        rows: dict[str, Any] = data.get(key, {})
        if not rows:
            return None
        latest = rows[sorted(rows.keys())[-1]]
        value = latest.get(function)
        return float(value) if value is not None else None

    async def rsi(self, symbol: str) -> float | None:
        return await self.indicator(symbol, "RSI", 14)

    async def sma(self, symbol: str, period: int) -> float | None:
        return await self.indicator(symbol, "SMA", period)

    def status(self) -> dict:
        return {
            "provider": self.name,
            "configured": self.configured,
            "status": "ok" if self.configured else DATA_SOURCE_PENDING,
            "detail": "用于 RSI 与 20/50/120/250 日均线" if self.configured else "缺少 ALPHA_VANTAGE_API_KEY",
        }

