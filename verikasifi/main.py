"""Veri Kâşifi — bağımsız istatistik + örüntü keşif uygulaması. Çalıştır: uvicorn main:app"""
from __future__ import annotations

import asyncio
import os
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from analysis import detect_columns, load_dataset, run_classic_tests, run_discovery
from report import build_report

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
DATA_DIR = Path(os.environ.get("VERIKASIFI_DATA_DIR", BASE_DIR / "data"))
REPORTS_DIR = DATA_DIR / "reports"

MAX_UPLOAD_MB = 50
ALLOWED_SUFFIXES = (".csv", ".xlsx", ".xls", ".sav", ".zsav")


@asynccontextmanager
async def lifespan(app: FastAPI):
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(title="Veri Kâşifi", lifespan=lifespan)


@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/analyze")
async def analyze(
    file: UploadFile = File(...),
    target: Optional[str] = Form(None),
    alpha: float = Form(0.05),
):
    name = file.filename or "veri.csv"
    suffix = "." + name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(400, f"Desteklenmeyen dosya türü: {suffix} (.csv, .xlsx, .xls, .sav kullanın)")
    content = await file.read()
    if len(content) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(400, f"Dosya çok büyük (en fazla {MAX_UPLOAD_MB} MB).")
    if not content:
        raise HTTPException(400, "Dosya boş görünüyor.")

    report_id = uuid.uuid4().hex[:12]
    report_dir = REPORTS_DIR / report_id
    report_dir.mkdir(parents=True, exist_ok=True)
    input_path = report_dir / f"veri{suffix}"
    input_path.write_bytes(content)

    def _run():
        df = load_dataset(input_path)
        if df.empty:
            raise ValueError("Dosya boş görünüyor.")
        columns = detect_columns(df)
        if len(columns) < 2:
            raise ValueError("Analiz için en az 2 uygun değişken bulunamadı.")
        tests, truncated = run_classic_tests(df, columns, alpha=alpha)
        discovery = run_discovery(df, columns, target=(target.strip() or None) if target else None)
        build_report(report_dir / "rapor.docx", name, columns, len(df), tests, truncated, discovery)
        return len(df), columns, tests, discovery

    try:
        n_rows, columns, tests, discovery = await asyncio.to_thread(_run)
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    except Exception as exc:
        raise HTTPException(500, f"Analiz sırasında hata oluştu: {exc}")

    return {
        "report_id": report_id,
        "n_rows": n_rows,
        "n_columns": len(columns),
        "n_tests": len(tests),
        "n_significant": sum(1 for t in tests if t.significant),
        "clustering": (
            {"k": discovery.clustering_k, "silhouette": discovery.clustering_silhouette}
            if discovery.clustering_k else None
        ),
        "n_anomalies": discovery.n_anomalies,
        "n_hidden_relationships": len(discovery.hidden_relationships),
        "risk_score": (
            {
                "target": discovery.risk_score["target"],
                "auc": discovery.risk_score["auc_logreg"] if discovery.risk_score["auc_logreg"] is not None else discovery.risk_score["auc_rf"],
            }
            if discovery.risk_score else None
        ),
        "notes": discovery.notes,
    }


@app.get("/api/download/{report_id}")
async def download(report_id: str):
    if not report_id.isalnum():
        raise HTTPException(404, "Rapor bulunamadı.")
    path = REPORTS_DIR / report_id / "rapor.docx"
    if not path.exists():
        raise HTTPException(404, "Rapor bulunamadı.")
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename="veri-kasifi-raporu.docx",
    )


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
