from __future__ import annotations

from datetime import date, timedelta

from app.core.constants import DATA_SOURCE_PENDING


class EventsProvider:
    name = "BLS/Fed Events"

    async def major_events(self) -> list[dict[str, str]]:
        today = date.today()
        return [
            {
                "name": "大非农发布时间",
                "date": DATA_SOURCE_PENDING,
                "source": "BLS Employment Situation schedule",
                "status": "需接入官方日历解析",
            },
            {
                "name": "美联储议息会议",
                "date": DATA_SOURCE_PENDING,
                "source": "Federal Reserve FOMC calendar",
                "status": "需接入官方日历解析",
            },
            {
                "name": "大型科技公司财报",
                "date": f"{today.isoformat()} 至 {(today + timedelta(days=45)).isoformat()}",
                "source": "FMP earnings calendar",
                "status": "配置 FMP 后自动筛选 AAPL/MSFT/NVDA/GOOGL/AMZN/META/TSLA",
            },
        ]

    def status(self) -> dict:
        return {
            "provider": self.name,
            "configured": True,
            "status": DATA_SOURCE_PENDING,
            "detail": "BLS/Fed 页面需专门解析；FMP 财报日历配置后可用",
        }

