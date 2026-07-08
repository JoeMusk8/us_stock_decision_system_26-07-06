from __future__ import annotations

from app.core.config import settings
from app.core.constants import DATA_SOURCE_PENDING
from app.providers.http import get_json


class XProvider:
    name = "X API"

    @property
    def configured(self) -> bool:
        return settings.has_x

    async def recent_posts(self, handle: str, since_id: str | None = None) -> list[dict]:
        if not self.configured:
            return []
        query = f"from:{handle} -is:retweet"
        params = {
            "query": query,
            "max_results": 20,
            "tweet.fields": "created_at,author_id,entities",
        }
        if since_id:
            params["since_id"] = since_id
        data = await get_json(
            "https://api.x.com/2/tweets/search/recent",
            headers={"Authorization": f"Bearer {settings.x_bearer_token}"},
            params=params,
        )
        return data.get("data", [])

    def status(self) -> dict:
        return {
            "provider": self.name,
            "configured": self.configured,
            "status": "ok" if self.configured else DATA_SOURCE_PENDING,
            "detail": "用于抓取指定账号 recent search 内容" if self.configured else "缺少 X_BEARER_TOKEN",
        }

