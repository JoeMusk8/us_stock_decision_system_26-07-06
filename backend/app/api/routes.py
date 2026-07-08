from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import (
    DashboardResponse,
    IndustryAnalysis,
    IndustryRequest,
    ProviderStatus,
    StockAnalysis,
    StockRequest,
    XAccount,
    XAccountIn,
    XAnalysis,
    XPost,
    allowed_values,
)
from app.providers.alpha_vantage import AlphaVantageProvider
from app.providers.events import EventsProvider
from app.providers.fmp import FMPProvider
from app.providers.sec import SECProvider
from app.providers.x_api import XProvider
from app.services.ai import AIService
from app.services.x_store import add_account, delete_account, get_post, list_accounts, list_posts, save_posts

router = APIRouter(prefix="/api")

x_provider = XProvider()
fmp = FMPProvider()
alpha = AlphaVantageProvider()
sec = SECProvider()
events_provider = EventsProvider()
ai = AIService()


@router.get("/health/providers", response_model=list[ProviderStatus])
async def provider_health() -> list[dict]:
    return [x_provider.status(), fmp.status(), alpha.status(), sec.status(), events_provider.status()]


@router.get("/meta/allowed-values")
async def meta_allowed_values() -> dict:
    return allowed_values()


@router.get("/x/accounts", response_model=list[XAccount])
async def get_x_accounts() -> list[dict]:
    return list_accounts()


@router.post("/x/accounts", response_model=XAccount)
async def create_x_account(payload: XAccountIn) -> dict:
    try:
        return add_account(payload.handle)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.delete("/x/accounts/{handle}")
async def remove_x_account(handle: str) -> dict:
    delete_account(handle.lstrip("@"))
    return {"ok": True}


@router.get("/x/posts", response_model=list[XPost])
async def get_x_posts(handle: str | None = Query(default=None)) -> list[dict]:
    for account in list_accounts():
        if handle and account["handle"] != handle.lstrip("@"):
            continue
        posts = await x_provider.recent_posts(account["handle"], account.get("since_id"))
        save_posts(account["handle"], posts)
    rows = list_posts(handle.lstrip("@") if handle else None)
    if rows:
        return rows
    if not x_provider.configured:
        return [
            {
                "id": "pending-x-api",
                "handle": handle or "system",
                "text": "X API 数据源待接入：请配置 X_BEARER_TOKEN 后抓取真实账号内容。",
                "created_at": "",
                "source_status": "数据源待接入",
            }
        ]
    return []


@router.post("/x/posts/{post_id}/analyze", response_model=XAnalysis)
async def analyze_x_post(post_id: str) -> XAnalysis:
    post = get_post(post_id)
    if post is None and post_id == "pending-x-api":
        post = {
            "id": post_id,
            "handle": "system",
            "text": "X API 数据源待接入：请配置 X_BEARER_TOKEN 后抓取真实账号内容。",
            "created_at": "",
        }
    if post is None:
        raise HTTPException(status_code=404, detail="post not found")
    return await ai.analyze_x_post(post)


@router.post("/industry/analyze", response_model=IndustryAnalysis)
async def analyze_industry(payload: IndustryRequest) -> IndustryAnalysis:
    return await ai.analyze_industry(payload.industry_name)


@router.post("/stocks/analyze", response_model=list[StockAnalysis])
async def analyze_stocks(payload: StockRequest) -> list[StockAnalysis]:
    results: list[StockAnalysis] = []
    for symbol in payload.symbols:
        quote = await fmp.quote(symbol)
        profile = await fmp.profile(symbol)
        income = await fmp.income_statement(symbol)
        indicators = {
            "rsi": await alpha.rsi(symbol),
            "ma20": await alpha.sma(symbol, 20),
            "ma50": await alpha.sma(symbol, 50),
            "ma120": await alpha.sma(symbol, 120),
            "ma250": await alpha.sma(symbol, 250),
        }
        results.append(ai.build_stock_analysis(symbol, quote, profile, income, indicators))
    return results


@router.get("/dashboard", response_model=DashboardResponse)
async def dashboard() -> DashboardResponse:
    nasdaq_quote = await fmp.quote("^IXIC") or await fmp.quote("QQQ")
    btc_quote = await fmp.quote("BTCUSD")
    nasdaq_indicators = {
        "rsi": await alpha.rsi("QQQ"),
        "ma20": await alpha.sma("QQQ", 20),
        "ma50": await alpha.sma("QQQ", 50),
        "ma120": await alpha.sma("QQQ", 120),
        "ma250": await alpha.sma("QQQ", 250),
    }
    events = await events_provider.major_events()
    today = date.today()
    if fmp.configured:
        try:
            earnings = await fmp.earnings_calendar(today.isoformat(), (today + timedelta(days=45)).isoformat())
            big_tech = {"AAPL", "MSFT", "NVDA", "GOOGL", "GOOG", "AMZN", "META", "TSLA"}
            for item in earnings:
                symbol = str(item.get("symbol", "")).upper()
                if symbol in big_tech:
                    events.append(
                        {
                            "name": f"{symbol} 财报日期",
                            "date": str(item.get("date", "待验证")),
                            "source": "FMP earnings calendar",
                            "status": "待验证",
                        }
                    )
        except Exception:
            events.append({"name": "FMP 财报日历", "date": "待验证", "source": "FMP", "status": "接口返回异常"})

    data_quality: list[str] = []
    if nasdaq_quote is None:
        data_quality.append("纳斯达克指数数据源待接入")
    if btc_quote is None:
        data_quality.append("比特币实时价格数据源待接入")
    if nasdaq_indicators["rsi"] is None:
        data_quality.append("纳斯达克 RSI/均线数据源待接入")
    data_quality.append("恐惧贪婪指数数据源待接入")

    nasdaq_price = nasdaq_quote.get("price") if nasdaq_quote else None
    market_level = "中性环境"
    if nasdaq_indicators["rsi"] and nasdaq_indicators["rsi"] >= 75:
        market_level = "高风险环境"
    elif data_quality:
        market_level = "谨慎环境"

    return DashboardResponse(
        market_status="数据完整性待验证" if data_quality else "市场数据已接入",
        nasdaq={
            "price": nasdaq_price,
            "change_percent": (nasdaq_quote or {}).get("changesPercentage"),
            "volume": (nasdaq_quote or {}).get("volume"),
            "money_flow": "纳斯达克资金流向待接入",
            **nasdaq_indicators,
        },
        bitcoin={
            "price": (btc_quote or {}).get("price"),
            "change_percent": (btc_quote or {}).get("changesPercentage"),
            "risk_signal": "风险偏好待验证" if btc_quote is None else "用于辅助观察风险偏好",
        },
        sentiment={"label": "数据源待接入", "fear_greed_index": None, "status": "不使用非授权抓取作为默认实现"},
        events=events,
        ai_market_reading="纳斯达克技术、BTC 风险偏好与事件日历需结合完整数据源后解读。当前不输出确定性交易建议。",
        market_level=market_level,
        data_quality=data_quality,
    )

