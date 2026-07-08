from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_provider_health_shape() -> None:
    response = client.get("/api/health/providers")
    assert response.status_code == 200
    payload = response.json()
    assert {item["provider"] for item in payload} >= {"X API", "FMP", "Alpha Vantage", "SEC EDGAR"}


def test_dashboard_degrades_without_sources() -> None:
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    payload = response.json()
    assert payload["market_level"] in ["积极环境", "中性环境", "谨慎环境", "高风险环境"]
    assert "sentiment" in payload

