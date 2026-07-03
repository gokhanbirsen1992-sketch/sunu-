"""Bağımsız istatistik analiz aracı için basit, tek istekli web ucu.

PaperForge'un ana iş (job) hattından tamamen ayrıdır: literatür taraması, makale yazımı veya
LLM yoktur. Dosya yüklenir, `standalone_stats.report.analyze()` senkron çalıştırılır ve sonuç
JSON özet + indirilebilir Word raporu olarak döner.
"""
from __future__ import annotations

import asyncio
import uuid
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app import config
from standalone_stats.report import analyze

router = APIRouter()

MAX_UPLOAD_MB = 50
ALLOWED_SUFFIXES = (".sav", ".zsav", ".csv", ".xlsx", ".xls")
REPORTS_DIR = config.STANDALONE_REPORTS_DIR


@router.post("/analyze")
async def standalone_analyze(
    file: UploadFile = File(...),
    dv: Optional[str] = Form(None),
    lang: str = Form("tr"),
    alpha: float = Form(0.05),
    p_adjust: str = Form("holm"),
):
    name = file.filename or "veri.csv"
    suffix = "." + name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(400, f"Desteklenmeyen dosya türü: {suffix} (.sav, .csv, .xlsx, .xls kullanın)")
    content = await file.read()
    if len(content) > MAX_UPLOAD_MB * 1024 * 1024:
        raise HTTPException(400, f"Dosya çok büyük (en fazla {MAX_UPLOAD_MB} MB).")
    if lang not in ("tr", "en"):
        raise HTTPException(400, "Geçersiz dil.")
    if p_adjust not in ("none", "holm", "fdr_bh"):
        raise HTTPException(400, "Geçersiz p-değeri düzeltme yöntemi.")

    report_id = uuid.uuid4().hex[:12]
    report_dir = REPORTS_DIR / report_id
    report_dir.mkdir(parents=True, exist_ok=True)
    input_path = report_dir / f"veri{suffix}"
    input_path.write_bytes(content)

    try:
        result = await asyncio.to_thread(
            analyze, input_path,
            out_path=report_dir / "rapor.docx",
            dv=(dv.strip() or None) if dv else None,
            lang=lang, alpha=alpha, p_adjust=p_adjust,
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    except Exception as exc:
        raise HTTPException(500, f"Analiz sırasında hata oluştu: {exc}")

    d = result.discovery
    return {
        "report_id": report_id,
        "n_rows_before": result.n_rows_before,
        "n_rows_after": result.n_rows_after,
        "n_tests": len(result.findings),
        "n_significant": sum(1 for f in result.findings if f.significant),
        "clustering": {"k": d.clustering.k, "silhouette": d.clustering.silhouette} if d.clustering else None,
        "n_anomalies": d.anomalies.n_flagged if d.anomalies else None,
        "n_hidden_relationships": sum(1 for p in d.mutual_info if p.hidden),
        "risk_score": (
            {
                "dv": d.risk_score.dv,
                "auc": d.risk_score.auc_logreg if d.risk_score.auc_logreg is not None else d.risk_score.auc_rf,
            }
            if d.risk_score else None
        ),
        "skipped_reasons": d.skipped_reasons,
    }


@router.get("/download/{report_id}")
async def standalone_download(report_id: str):
    if not report_id.isalnum():
        raise HTTPException(404, "Rapor bulunamadı.")
    path = REPORTS_DIR / report_id / "rapor.docx"
    if not path.exists():
        raise HTTPException(404, "Rapor bulunamadı.")
    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename="istatistik-raporu.docx",
    )
