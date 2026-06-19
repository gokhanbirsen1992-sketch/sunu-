"""FastAPI backend — iPhone PWA için SPSS→Makale servisi.

Akış: `.sav` yükle → sav2q1.pipeline.generate_article (deterministik) → .docx indir.
Gizlilik: yüklenen `.sav` işlemden HEMEN sonra silinir; iş klasörü indirme sonrası
arka planda temizlenir; PII loglanmaz.
"""

from __future__ import annotations

import shutil
import tempfile
import time
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from starlette.background import BackgroundTask

from sav2q1.pipeline import generate_article

app = FastAPI(title="SPSS → Makale")
STATIC = Path(__file__).parent / "static"
JOBS = Path(tempfile.gettempdir()) / "makale_jobs"
JOBS.mkdir(exist_ok=True)
_RESULTS: dict[str, dict] = {}        # job -> {"docx": path, "ts": epoch}
_TTL = 3600                            # 1 saat sonra temizle

_DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def _sweep() -> None:
    now = time.time()
    for job, info in list(_RESULTS.items()):
        if now - info["ts"] > _TTL:
            shutil.rmtree(JOBS / job, ignore_errors=True)
            _RESULTS.pop(job, None)


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return (STATIC / "index.html").read_text(encoding="utf-8")


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/api/analyze")
async def analyze(file: UploadFile = File(...), with_pubmed: str = Form("false"),
                  topic: str = Form("")) -> dict:
    _sweep()
    if not (file.filename or "").lower().endswith(".sav"):
        raise HTTPException(400, "Lütfen bir SPSS .sav dosyası yükleyin.")
    brief = {"topic": topic.strip()} if topic.strip() else None
    job = uuid.uuid4().hex[:12]
    rundir = JOBS / job
    (rundir / "input").mkdir(parents=True, exist_ok=True)
    sav = rundir / "input" / "data.sav"
    with open(sav, "wb") as f:
        shutil.copyfileobj(file.file, f)
    try:
        res = generate_article(str(sav), str(rundir), brief=brief,
                               with_pubmed=(with_pubmed == "true"), log=lambda *_: None)
    except Exception as e:  # noqa: BLE001
        shutil.rmtree(rundir, ignore_errors=True)
        raise HTTPException(500, f"Analiz sırasında hata: {e}")
    finally:
        try:
            sav.unlink()                # gizlilik: ham veriyi hemen sil
        except OSError:
            pass
    _RESULTS[job] = {"docx": res["docx"], "ts": time.time()}
    return {"ok": True, "job": job, "group_var": res["group_var"], "n_results": res["n_results"],
            "gate": res["gate"], "with_citations": res["with_citations"]}


@app.get("/api/result/{job}")
def result(job: str):
    info = _RESULTS.get(job)
    if not info or not Path(info["docx"]).exists():
        raise HTTPException(404, "Sonuç bulunamadı veya süresi doldu.")

    def _cleanup(j=job):
        shutil.rmtree(JOBS / j, ignore_errors=True)
        _RESULTS.pop(j, None)

    return FileResponse(info["docx"], filename="makale_tr.docx", media_type=_DOCX_MIME,
                        background=BackgroundTask(_cleanup))


app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")
