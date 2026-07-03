"""PaperForge — SPSS'ten makaleye ajan ordulu pipeline. Çalıştır: uvicorn app.main:app"""
from __future__ import annotations

import base64
import os
import secrets
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import config
from app.api.routes import router
from app.api.standalone_routes import router as standalone_router
from app.jobs.store import store


@asynccontextmanager
async def lifespan(app: FastAPI):
    config.ensure_dirs()
    store.load_all()
    yield


app = FastAPI(title="PaperForge", lifespan=lifespan)


@app.middleware("http")
async def basic_auth_middleware(request: Request, call_next):
    """APP_PASSWORD ortam değişkeni ayarlıysa tüm siteyi HTTP Basic ile korur.

    İnternete açık dağıtımlarda (Render/HF Spaces) mutlaka ayarlayın.
    """
    password = os.environ.get("APP_PASSWORD", "")
    if password:
        header = request.headers.get("authorization", "")
        ok = False
        if header.startswith("Basic "):
            try:
                decoded = base64.b64decode(header[6:]).decode("utf-8", "ignore")
                given = decoded.partition(":")[2]
                ok = secrets.compare_digest(given, password)
            except Exception:
                ok = False
        if not ok:
            return Response(
                status_code=401,
                headers={"WWW-Authenticate": 'Basic realm="PaperForge"'},
                content="Parola gerekli / Password required",
            )
    return await call_next(request)


app.include_router(router, prefix="/api")
app.include_router(standalone_router, prefix="/api/standalone")


@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(config.STATIC_DIR / "index.html")


@app.get("/analiz", include_in_schema=False)
async def standalone_page():
    return FileResponse(config.STATIC_DIR / "standalone.html")


app.mount("/static", StaticFiles(directory=config.STATIC_DIR), name="static")
