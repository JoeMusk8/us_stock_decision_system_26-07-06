from __future__ import annotations

from typing import Any
import json

import httpx

from app.core.config import settings
from app.core.constants import NEEDS_VERIFICATION
from app.models.schemas import IndustryAnalysis, StockAnalysis, XAnalysis
from app.services.guardrails import sanitize_text


SYSTEM_GUARDRAIL = (
    "你是美股交易决策辅助系统。必须基于证据输出，不允许编造。"
    "禁止输出立即买入、立即卖出、最佳买入价格、最佳卖出价格、保证盈利、一定上涨。"
)


class AIService:
    async def _chat_json(self, prompt: str) -> dict[str, Any] | None:
        if not settings.has_ai:
            return None
        async with httpx.AsyncClient(timeout=40) as client:
            response = await client.post(
                f"{settings.ai_base_url}/chat/completions",
                headers={"Authorization": f"Bearer {settings.ai_api_key}"},
                json={
                    "model": settings.ai_model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_GUARDRAIL},
                        {"role": "user", "content": prompt},
                    ],
                    "response_format": {"type": "json_object"},
                },
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            return json.loads(content)

    async def analyze_x_post(self, post: dict[str, Any]) -> XAnalysis:
        prompt = (
            "分析这条 X 内容，返回 JSON 字段：topics, companies, tickers, truth_level, "
            "impact_direction, impact_strength, mapping_level, evidence_sources, verification_items。\n"
            f"账号：{post.get('handle')}\n发布时间：{post.get('created_at')}\n内容：{post.get('text')}"
        )
        data = await self._chat_json(prompt)
        if data is None:
            data = {
                "topics": [],
                "companies": [],
                "tickers": [],
                "truth_level": "暂无证据",
                "impact_direction": "待验证",
                "impact_strength": "待验证",
                "mapping_level": "暂无明确关系",
                "evidence_sources": [],
                "verification_items": ["AI_API_KEY 未配置，需接入 AI 后进行真实性和公司映射分析"],
            }
        return XAnalysis(
            original_text=sanitize_text(post.get("text", "")),
            published_at=post.get("created_at", ""),
            account=post.get("handle", ""),
            topics=data.get("topics", []),
            companies=data.get("companies", []),
            tickers=data.get("tickers", []),
            truth_level=data.get("truth_level", "暂无证据"),
            impact_direction=sanitize_text(data.get("impact_direction", NEEDS_VERIFICATION)),
            impact_strength=sanitize_text(data.get("impact_strength", NEEDS_VERIFICATION)),
            mapping_level=data.get("mapping_level", "暂无明确关系"),
            evidence_sources=data.get("evidence_sources", []),
            verification_items=data.get("verification_items", []),
        )

    async def analyze_industry(self, industry_name: str) -> IndustryAnalysis:
        prompt = (
            "分析行业上下游，返回 JSON 字段：summary, upstream_companies, midstream_companies, "
            "downstream_companies, core_companies, related_tickers, logic_summary, ai_conclusion, verification_items。"
            "无法验证的关系必须写入 verification_items。\n"
            f"行业：{industry_name}"
        )
        data = await self._chat_json(prompt)
        if data is None:
            data = {
                "summary": "AI_API_KEY 未配置，当前只能建立待验证分析任务。",
                "upstream_companies": [],
                "midstream_companies": [],
                "downstream_companies": [],
                "core_companies": [],
                "related_tickers": [],
                "logic_summary": "当前数据不足，部分行业链关系需要人工验证。",
                "ai_conclusion": "数据源待接入，不能编造产业链关系。",
                "verification_items": ["配置 AI_API_KEY，并结合 X/FMP/SEC/Alpha Vantage 后重新分析"],
            }
        return IndustryAnalysis(industry_name=industry_name, **data)

    def build_stock_analysis(self, symbol: str, quote: dict | None, profile: dict | None, income: dict | None, indicators: dict[str, float | None]) -> StockAnalysis:
        company_name = (profile or {}).get("companyName") or (quote or {}).get("name") or symbol
        price = _float((quote or {}).get("price"))
        change_percent = _float((quote or {}).get("changesPercentage"))
        volume = _int((quote or {}).get("volume"))
        avg_volume = _int((quote or {}).get("avgVolume"))
        rsi = indicators.get("rsi")
        ma20 = indicators.get("ma20")
        ma50 = indicators.get("ma50")
        ma120 = indicators.get("ma120")
        ma250 = indicators.get("ma250")

        data_quality: list[str] = []
        if quote is None:
            data_quality.append("FMP 报价数据源待接入或返回为空")
        if rsi is None or ma20 is None:
            data_quality.append("Alpha Vantage 技术指标待接入或返回为空")
        if income is None:
            data_quality.append("财务信息待验证")

        trend = _trend_label(price, ma20, ma50, ma120, ma250)
        heat = "RSI 待验证" if rsi is None else ("RSI 偏热" if rsi >= 70 else "RSI 偏弱" if rsi <= 35 else "RSI 中性或偏强")
        decision = "观察"
        if rsi is not None and rsi >= 75:
            decision = "高风险，谨慎"
        elif price and ma20 and ma50 and price > ma20 > ma50:
            decision = "可重点关注"
        elif price and ma50 and price < ma50:
            decision = "等待确认"

        observation_range = "待验证"
        risk_range = "待验证"
        if ma20 and ma50:
            low, high = sorted([ma20, ma50])
            observation_range = f"{low:.2f} - {high:.2f}"
        if ma120:
            risk_range = f"跌破 MA120 附近 {ma120:.2f} 后需重新评估"

        revenue = _float((income or {}).get("revenue"))
        net_income = _float((income or {}).get("netIncome"))
        financial_summary = "财务信息待验证"
        if revenue is not None:
            financial_summary = f"最近年度收入 {revenue:,.0f}"
            if net_income is not None:
                financial_summary += f"，净利润 {net_income:,.0f}"

        return StockAnalysis(
            symbol=symbol,
            company_name=company_name,
            current_price=price,
            change_percent=change_percent,
            volume=volume,
            average_volume=avg_volume,
            rsi=rsi,
            ma20=ma20,
            ma50=ma50,
            ma120=ma120,
            ma250=ma250,
            money_flow="资金流向待验证",
            financial_summary=financial_summary,
            related_x_summary="相关 X 信息待验证",
            ai_conclusion=sanitize_text(f"{symbol} 当前趋势判断：{trend}；{heat}。该结果仅作辅助观察。"),
            observation_range=observation_range,
            risk_range=risk_range,
            decision_level=decision,
            data_quality=data_quality,
        )


def _float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int(value: Any) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _trend_label(price: float | None, ma20: float | None, ma50: float | None, ma120: float | None, ma250: float | None) -> str:
    if price is None:
        return "待验证"
    mas = [ma for ma in [ma20, ma50, ma120, ma250] if ma is not None]
    if len(mas) < 2:
        return "技术数据不足"
    above = sum(1 for ma in mas if price > ma)
    if above == len(mas):
        return "强势"
    if above >= len(mas) // 2:
        return "震荡"
    return "转弱或下跌"

