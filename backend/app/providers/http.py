from __future__ import annotations

from typing import Any

import httpx


async def get_json(url: str, *, headers: dict[str, str] | None = None, params: dict[str, Any] | None = None) -> dict[str, Any]:
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, dict):
            return {"data": data}
        return data

