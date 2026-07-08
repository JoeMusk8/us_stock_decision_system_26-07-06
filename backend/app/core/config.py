from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os


def _load_env_file() -> None:
    env_path = Path(__file__).resolve().parents[3] / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if not line or line.strip().startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


_load_env_file()


DEFAULT_DATABASE_URL = "/tmp/app.sqlite3" if os.getenv("VERCEL") else "backend/data/app.sqlite3"


@dataclass(frozen=True)
class Settings:
    x_bearer_token: str = os.getenv("X_BEARER_TOKEN", "")
    fmp_api_key: str = os.getenv("FMP_API_KEY", "")
    alpha_vantage_api_key: str = os.getenv("ALPHA_VANTAGE_API_KEY", "")
    ai_api_key: str = os.getenv("AI_API_KEY", "")
    ai_base_url: str = os.getenv("AI_BASE_URL", "https://api.openai.com/v1").rstrip("/")
    ai_model: str = os.getenv("AI_MODEL", "gpt-4.1-mini")
    database_url: str = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
    frontend_origin: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173,http://127.0.0.1:5173")
    app_name: str = "美股交易决策辅助系统"

    @property
    def has_x(self) -> bool:
        return bool(self.x_bearer_token)

    @property
    def has_fmp(self) -> bool:
        return bool(self.fmp_api_key)

    @property
    def has_alpha_vantage(self) -> bool:
        return bool(self.alpha_vantage_api_key)

    @property
    def has_ai(self) -> bool:
        return bool(self.ai_api_key)

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origin.split(",") if origin.strip()]


settings = Settings()
