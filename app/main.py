"""PaperForge — SPSS'ten makaleye ajan ordulu pipeline. Çalıştır: uvicorn app.main:app"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import config
from app.api.routes import router
from app.jobs.store import store


@asynccontextmanager
async def lifespan(app: FastAPI):
    config.ensure_dirs()
    store.load_all()
    yield


app = FastAPI(title="PaperForge", lifespan=lifespan)
app.include_router(router, prefix="/api")


@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(config.STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")
