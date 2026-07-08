from __future__ import annotations

from app.core.constants import NEEDS_VERIFICATION
from app.providers.http import get_json


class SECProvider:
    name = "SEC EDGAR"

    async def companyfacts(self, cik: str) -> dict:
        cik10 = str(cik).zfill(10)
        return await get_json(
            f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik10}.json",
            headers={"User-Agent": "market-decision-assistant contact@example.com"},
        )

    def status(self) -> dict:
        return {
            "provider": self.name,
            "configured": True,
            "status": NEEDS_VERIFICATION,
            "detail": "无需密钥；用于辅助验证 SEC filings 与 companyfacts",
        }

