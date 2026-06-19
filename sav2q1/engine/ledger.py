"""Sonuç defteri (results_ledger.json) — makaledeki TEK sayı kaynağı.

`number_index`, her `result_id` için yazarların kullanabileceği BİREBİR sayı
token'larını tutar. `verify-numeric`, bir cümledeki sayıların yalnızca o cümlenin
binding'indeki id'ye ait token kümesinde (ve istatistik-dışı whitelist'te)
bulunmasına izin verir — böylece "doğru sayı / yanlış bağlam" hatası da yakalanır.
"""

from __future__ import annotations

import datetime as _dt
import json
import platform
from pathlib import Path
from typing import Any

import numpy as np

from . import ENGINE_VERSION, GLOBAL_SEED
from .numbers import extract_tokens


def _software_versions() -> dict:
    out = {"python": platform.python_version()}
    for mod in ("numpy", "scipy", "statsmodels", "pingouin", "pandas", "pyreadstat"):
        try:
            out[mod] = __import__(mod).__version__
        except Exception:  # noqa: BLE001
            out[mod] = None
    return out


class _NpEncoder(json.JSONEncoder):
    """numpy tiplerini JSON'a çevirir."""

    def default(self, o: Any):
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, (np.ndarray,)):
            return o.tolist()
        if isinstance(o, (np.bool_,)):
            return bool(o)
        return super().default(o)


class LedgerBuilder:
    def __init__(self, run_id: str, dataset: dict, design: dict):
        self.ledger: dict[str, Any] = {
            "run_id": run_id,
            "engine_version": ENGINE_VERSION,
            "seed": GLOBAL_SEED,
            "generated_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
            "software": _software_versions(),
            "dataset": dataset,
            "design": design,
            "descriptives": [],
            "results": [],
            "reliability": [],
            "factor": [],
            "regression": [],
            "tables": [],
            "figures": [],
            "number_index": {},
            # Her cümlede kabul edilebilir sayılar (örneklem büyüklükleri vb.).
            "global_index": [],
        }

    def _register(self, key: str, display_strings: list[str]) -> None:
        """Render edilmiş string'leri TARAYARAK o id'nin izinli sayı kümesini kur."""
        cur = self.ledger["number_index"].setdefault(key, [])
        for s in display_strings:
            for t in extract_tokens(s):
                if t and t not in cur:
                    cur.append(t)

    def _register_global(self, display_strings: list[str]) -> None:
        cur = self.ledger["global_index"]
        for s in display_strings:
            for t in extract_tokens(s):
                if t and t not in cur:
                    cur.append(t)

    def add_descriptive(self, d: dict) -> None:
        display = d.pop("_display", [])
        glob = d.pop("_global", [])
        self.ledger["descriptives"].append(d)
        self._register(d["id"], display)
        self._register_global(glob)

    def add_result(self, r: dict) -> None:
        display = r.pop("_display", [])
        glob = r.pop("_global", [])
        self.ledger["results"].append(r)
        self._register(r["id"], display)
        self._register_global(glob)

    def add_table(self, t: dict) -> None:
        self.ledger["tables"].append(t)

    def add_figure(self, f: dict) -> None:
        self.ledger["figures"].append(f)

    def to_dict(self) -> dict:
        return self.ledger

    def write(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.ledger, ensure_ascii=False, indent=2, cls=_NpEncoder),
                        encoding="utf-8")
