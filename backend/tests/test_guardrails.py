from app.models.schemas import StockRequest
from app.services.guardrails import contains_forbidden_text, sanitize_text


def test_stock_request_limits_to_15() -> None:
    payload = StockRequest(symbols=[f"T{i}" for i in range(15)])
    assert len(payload.symbols) == 15


def test_stock_request_rejects_more_than_15() -> None:
    try:
        StockRequest(symbols=[f"T{i}" for i in range(16)])
    except Exception as exc:
        assert "最多支持 15 只股票" in str(exc)
    else:
        raise AssertionError("expected validation error")


def test_forbidden_text_is_detected_and_sanitized() -> None:
    text = "最佳买入价格不是允许输出，立即买入也不允许"
    assert contains_forbidden_text(text)
    sanitized = sanitize_text(text)
    assert "最佳买入价格" not in sanitized
    assert "立即买入" not in sanitized

