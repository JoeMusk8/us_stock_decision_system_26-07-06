from __future__ import annotations

import json
from sqlite3 import IntegrityError

from app.core.database import get_conn


MAX_X_ACCOUNTS = 15


def list_accounts() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("SELECT handle, created_at, since_id FROM x_accounts ORDER BY created_at DESC").fetchall()
        return [dict(row) for row in rows]


def add_account(handle: str) -> dict:
    accounts = list_accounts()
    if len(accounts) >= MAX_X_ACCOUNTS and handle not in {item["handle"] for item in accounts}:
        raise ValueError("最多支持 15 个 X 账号")
    with get_conn() as conn:
        try:
            conn.execute("INSERT INTO x_accounts(handle) VALUES (?)", (handle,))
        except IntegrityError:
            pass
        row = conn.execute("SELECT handle, created_at, since_id FROM x_accounts WHERE handle = ?", (handle,)).fetchone()
        return dict(row)


def delete_account(handle: str) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM x_accounts WHERE handle = ?", (handle,))


def save_posts(handle: str, posts: list[dict]) -> None:
    if not posts:
        return
    with get_conn() as conn:
        max_id = None
        for post in posts:
            post_id = str(post.get("id"))
            max_id = max(max_id or post_id, post_id)
            conn.execute(
                """
                INSERT OR IGNORE INTO x_posts(id, handle, text, created_at, raw_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    post_id,
                    handle,
                    post.get("text", ""),
                    post.get("created_at", ""),
                    json.dumps(post, ensure_ascii=False),
                ),
            )
        if max_id:
            conn.execute("UPDATE x_accounts SET since_id = ? WHERE handle = ?", (max_id, handle))


def list_posts(handle: str | None = None) -> list[dict]:
    query = "SELECT id, handle, text, created_at FROM x_posts"
    params: tuple = ()
    if handle:
        query += " WHERE handle = ?"
        params = (handle,)
    query += " ORDER BY created_at DESC LIMIT 100"
    with get_conn() as conn:
        return [dict(row) for row in conn.execute(query, params).fetchall()]


def get_post(post_id: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT id, handle, text, created_at FROM x_posts WHERE id = ?", (post_id,)).fetchone()
        return dict(row) if row else None

