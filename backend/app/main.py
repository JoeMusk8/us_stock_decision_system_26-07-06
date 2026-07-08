from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import settings
from app.core.database import init_db


app = FastAPI(title=settings.app_name, version="0.1.0")
STATIC_DIR = Path(__file__).resolve().parent / "static"
ASSETS_DIR = STATIC_DIR / "assets"

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/")
async def root():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"name": settings.app_name, "status": "ok"}


app.include_router(router)

if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")


@app.get("/{full_path:path}", include_in_schema=False)
async def spa_fallback(full_path: str):
    index_path = STATIC_DIR / "index.html"
    if index_path.exists() and not full_path.startswith("api/"):
        return FileResponse(index_path)
    return {"name": settings.app_name, "status": "ok"}
