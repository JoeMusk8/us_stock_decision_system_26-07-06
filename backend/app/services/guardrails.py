from __future__ import annotations

from typing import Any

from app.core.constants import FORBIDDEN_PHRASES


def contains_forbidden_text(payload: Any) -> list[str]:
    text = str(payload)
    return [phrase for phrase in FORBIDDEN_PHRASES if phrase in text]


def sanitize_text(text: str) -> str:
    clean = text
    replacements = {
        "最佳买入价格": "辅助观察区间",
        "最佳卖出价格": "风险区间",
        "立即买入": "可重点关注",
        "立即卖出": "不参与",
        "保证盈利": "不保证结果",
        "一定上涨": "存在不确定性",
    }
    for src, dst in replacements.items():
        clean = clean.replace(src, dst)
    return clean

