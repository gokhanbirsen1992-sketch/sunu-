"""Değişken profilleme: tip/rol çıkarımı, eksiklik, dağılım özetleri.

ÖNEMLİ (Reviewer-2): rol çıkarımı sezgiseldir ve YANILABİLİR. Bu yüzden çıktı,
methodologist + İNSAN KAPISI 1 tarafından gözden geçirilmek üzere üretilir;
brief.yaml'daki açık rol bildirimleri her zaman çıkarımı geçersiz kılar.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any

import numpy as np
import pandas as pd

from .io_sav import SavData


@dataclass
class VariableProfile:
    name: str
    label: str
    storage: str            # "numeric" | "string"
    measure: str            # "nominal" | "ordinal" | "scale" | "unknown"
    role: str               # continuous|binary|nominal|ordinal|id|scale_item|constant|unknown
    n: int
    n_missing: int
    pct_missing: float
    n_unique: int
    value_labels: dict
    summary: dict           # sürekli: mean/sd/...; kategorik: categories[]

    def to_dict(self) -> dict:
        return asdict(self)


def _norm_code(code: Any) -> Any:
    """value_counts indeksini value_labels anahtarlarıyla eşleştirmek için normalize et."""
    try:
        f = float(code)
        return f
    except (TypeError, ValueError):
        return code


def _lookup_label(value_labels: dict, code: Any) -> str | None:
    if not value_labels:
        return None
    if code in value_labels:
        return value_labels[code]
    nc = _norm_code(code)
    if nc in value_labels:
        return value_labels[nc]
    # bazen anahtarlar int, kod float
    try:
        return value_labels.get(int(nc))
    except (TypeError, ValueError):
        return None


def _infer_role(s: pd.Series, measure: str, value_labels: dict, n_rows: int) -> str:
    non_null = s.dropna()
    nun = int(non_null.nunique())
    is_string = (s.dtype == object) or pd.api.types.is_string_dtype(s)

    if nun <= 1:
        return "constant"
    if is_string:
        return "id" if nun > 0.9 * max(n_rows, 1) else "nominal"
    # numeric:
    if nun > 0.95 * max(n_rows, 1) and not value_labels:
        return "id"
    if nun == 2:
        return "binary"
    if value_labels and nun <= max(len(value_labels) + 1, 12):
        return "ordinal" if measure == "ordinal" else "nominal"
    if measure == "scale":
        return "continuous"
    if measure == "ordinal":
        return "ordinal"
    return "continuous" if nun > 12 else "nominal"


def _summary(s: pd.Series, role: str, value_labels: dict) -> dict:
    non_null = s.dropna()
    if role in ("id", "constant", "unknown"):
        # Kimlik/sabit değişkenler raporlanmaz; kategori listesini şişirme.
        return {"note": "kimlik/sabit değişken, özetlenmedi", "n_unique": int(non_null.nunique())}
    if role == "continuous":
        return {
            "mean": float(non_null.mean()),
            "sd": float(non_null.std(ddof=1)),
            "median": float(non_null.median()),
            "q1": float(non_null.quantile(0.25)),
            "q3": float(non_null.quantile(0.75)),
            "min": float(non_null.min()),
            "max": float(non_null.max()),
            "skew": float(non_null.skew()) if len(non_null) > 2 else None,
            "kurtosis": float(non_null.kurtosis()) if len(non_null) > 3 else None,
        }
    # kategorik / ikili / sıralı
    counts = non_null.value_counts().sort_index()
    total = int(counts.sum())
    cats = []
    for code, n in counts.items():
        label = _lookup_label(value_labels, code) or str(code)
        cats.append({
            "code": (int(code) if isinstance(code, (int, np.integer)) or (isinstance(code, float) and float(code).is_integer()) else code),
            "label": str(label),
            "n": int(n),
            "pct": round(100.0 * n / total, 1) if total else 0.0,
        })
    return {"categories": cats, "total": total}


def profile_variable(sav: SavData, name: str) -> VariableProfile:
    s = sav.df[name]
    n = int(len(s))
    n_missing = int(s.isna().sum())
    measure = sav.measure.get(name, "unknown") or "unknown"
    value_labels = sav.value_labels.get(name, {})
    role = _infer_role(s, measure, value_labels, sav.n_rows)
    return VariableProfile(
        name=name,
        label=sav.column_labels.get(name, ""),
        storage=("string" if (s.dtype == object or pd.api.types.is_string_dtype(s)) else "numeric"),
        measure=measure,
        role=role,
        n=n,
        n_missing=n_missing,
        pct_missing=round(100.0 * n_missing / n, 1) if n else 0.0,
        n_unique=int(s.dropna().nunique()),
        value_labels={str(k): v for k, v in value_labels.items()},
        summary=_summary(s, role, value_labels),
    )


def profile_dataset(sav: SavData) -> dict:
    """Tüm veri setinin profili (dataset_profile.json gövdesi)."""
    variables = [profile_variable(sav, name).to_dict() for name in sav.df.columns]
    complete_cases = int(sav.df.dropna().shape[0])
    return {
        "source_file": sav.source_file,
        "n_rows": sav.n_rows,
        "n_vars": int(sav.df.shape[1]),
        "n_complete_cases": complete_cases,
        "variables": variables,
        # M1'de doldurulacak: ölçek-grupları (Likert madde kümeleri)
        "scale_groups": [],
    }
