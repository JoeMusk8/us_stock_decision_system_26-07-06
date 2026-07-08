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

    async def technical_series(self, symbol: str, *, digital_currency: bool = False) -> list[dict[str, Any]]:
        """Return real OHLCV data enriched with local SMA and RSI calculations."""
        if not self.configured:
            return []
        params: dict[str, Any] = {
            "function": "DIGITAL_CURRENCY_DAILY" if digital_currency else "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": settings.alpha_vantage_api_key,
        }
        if digital_currency:
            params["market"] = "USD"
        else:
            params["outputsize"] = "full"
        data = await get_json(self.base, params=params)
        series_key = "Time Series (Digital Currency Daily)" if digital_currency else "Time Series (Daily)"
        rows = data.get(series_key, {})
        if not isinstance(rows, dict):
            return []

        points: list[dict[str, Any]] = []
        for day in sorted(rows.keys()):
            row = rows[day]
            try:
                points.append(
                    {
                        "date": day,
                        "open": _series_number(row, "1. open"),
                        "high": _series_number(row, "2. high"),
                        "low": _series_number(row, "3. low"),
                        "close": _series_number(row, "4. close"),
                        "volume": int(_series_number(row, "5. volume")),
                    }
                )
            except (TypeError, ValueError):
                continue

        closes = [point["close"] for point in points]
        for index, point in enumerate(points):
            point["ma20"] = _sma(closes, index, 20)
            point["ma50"] = _sma(closes, index, 50)
            point["ma120"] = _sma(closes, index, 120)
            point["ma250"] = _sma(closes, index, 250)
            point["rsi"] = _rsi(closes, index, 14)
        return points[-60:]

    def status(self) -> dict:
        return {
            "provider": self.name,
            "configured": self.configured,
            "status": "ok" if self.configured else DATA_SOURCE_PENDING,
            "detail": "用于 RSI 与 20/50/120/250 日均线" if self.configured else "缺少 ALPHA_VANTAGE_API_KEY",
        }


def _series_number(row: dict[str, Any], prefix: str) -> float:
    for key, value in row.items():
        if key == prefix or key.startswith(prefix):
            return float(value)
    raise ValueError(f"missing {prefix}")


def _sma(values: list[float], index: int, period: int) -> float | None:
    if index + 1 < period:
        return None
    window = values[index + 1 - period : index + 1]
    return round(sum(window) / period, 4)


def _rsi(values: list[float], index: int, period: int) -> float | None:
    if index < period:
        return None
    changes = [values[i] - values[i - 1] for i in range(index - period + 1, index + 1)]
    gains = sum(max(change, 0) for change in changes) / period
    losses = sum(max(-change, 0) for change in changes) / period
    if losses == 0:
        return 100.0
    return round(100 - (100 / (1 + gains / losses)), 2)
