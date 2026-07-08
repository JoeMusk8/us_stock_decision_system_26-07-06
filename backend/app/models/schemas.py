from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from app.core.constants import MARKET_LEVELS, MAPPING_LEVELS, STOCK_DECISION_LEVELS, TRUTH_LEVELS


TruthLevel = Literal["已验证", "部分可验证", "暂无证据", "存疑", "明显不可靠"]
MappingLevel = Literal["直接相关", "间接相关", "弱相关", "暂无明确关系"]
StockDecisionLevel = Literal["不参与", "观察", "等待确认", "可重点关注", "高风险，谨慎"]
MarketLevel = Literal["积极环境", "中性环境", "谨慎环境", "高风险环境"]


class ProviderStatus(BaseModel):
    provider: str
    configured: bool
    status: str
    detail: str


class XAccountIn(BaseModel):
    handle: str = Field(min_length=1, max_length=32)

    @field_validator("handle")
    @classmethod
    def normalize_handle(cls, value: str) -> str:
        value = value.strip()
        if value.startswith("@"):
            value = value[1:]
        return value


class XAccount(BaseModel):
    handle: str
    created_at: str
    since_id: str | None = None


class XPost(BaseModel):
    id: str
    handle: str
    text: str
    created_at: str
    source_status: str = "ok"


class XAnalysis(BaseModel):
    original_text: str
    published_at: str
    account: str
    topics: list[str]
    companies: list[str]
    tickers: list[str]
    truth_level: TruthLevel
    impact_direction: str
    impact_strength: str
    mapping_level: MappingLevel
    evidence_sources: list[str]
    verification_items: list[str]


class IndustryRequest(BaseModel):
    industry_name: str = Field(min_length=1, max_length=80)


class IndustryAnalysis(BaseModel):
    industry_name: str
    summary: str
    upstream_companies: list[str]
    midstream_companies: list[str]
    downstream_companies: list[str]
    core_companies: list[str]
    related_tickers: list[str]
    logic_summary: str
    ai_conclusion: str
    verification_items: list[str]


class StockRequest(BaseModel):
    symbols: list[str] = Field(min_length=1)

    @field_validator("symbols")
    @classmethod
    def normalize_symbols(cls, value: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for item in value:
            symbol = item.strip().upper()
            if not symbol or symbol in seen:
                continue
            seen.add(symbol)
            result.append(symbol)
        if not result:
            raise ValueError("至少输入 1 只股票")
        if len(result) > 15:
            raise ValueError("最多支持 15 只股票")
        return result


class MarketPoint(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    ma20: float | None = None
    ma50: float | None = None
    ma120: float | None = None
    ma250: float | None = None
    rsi: float | None = None


class StockAnalysis(BaseModel):
    symbol: str
    company_name: str
    company_background: str
    main_business: str
    industry_position: str
    current_price: float | None
    change_percent: float | None
    volume: int | None
    average_volume: int | None
    rsi: float | None
    ma20: float | None
    ma50: float | None
    ma120: float | None
    ma250: float | None
    money_flow: str
    financial_summary: str
    related_x_summary: str
    ai_conclusion: str
    observation_range: str
    risk_range: str
    decision_level: StockDecisionLevel
    data_quality: list[str]
    chart_data: list[MarketPoint]


class DashboardResponse(BaseModel):
    market_status: str
    nasdaq: dict[str, Any]
    bitcoin: dict[str, Any]
    sentiment: dict[str, Any]
    events: list[dict[str, str]]
    ai_market_reading: str
    market_level: MarketLevel
    data_quality: list[str]


def allowed_values() -> dict[str, list[str]]:
    return {
        "truth_levels": TRUTH_LEVELS,
        "mapping_levels": MAPPING_LEVELS,
        "stock_decision_levels": STOCK_DECISION_LEVELS,
        "market_levels": MARKET_LEVELS,
    }
