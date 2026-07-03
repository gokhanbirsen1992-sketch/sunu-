"""Değişken tipi çıkarımı: SPSS metadata + veri özelliklerinden."""
from __future__ import annotations

import re

import numpy as np
import pandas as pd

from app.models import VariableInfo

_ID_NAME_RE = re.compile(r"(?i)^(id|no|num|sira|sıra|subject|subj|kod|katilimci|katılımcı)([_ ]?(no|id))?$")


def _is_integer_like(series: pd.Series) -> bool:
    vals = series.dropna()
    if vals.empty or not pd.api.types.is_numeric_dtype(vals):
        return False
    return bool(np.allclose(vals.astype(float) % 1, 0))


def infer_variable(name: str, series: pd.Series, meta: dict) -> VariableInfo:
    label = (meta.get("labels") or {}).get(name)
    value_labels = (meta.get("value_labels") or {}).get(name)
    measure = (meta.get("measures") or {}).get(name, "unknown")

    n_missing = int(series.isna().sum())
    non_missing = series.dropna()
    n_unique = int(non_missing.nunique())

    info = VariableInfo(
        name=name, label=label, n_missing=n_missing, n_unique=n_unique, value_labels=value_labels
    )

    if pd.api.types.is_datetime64_any_dtype(series):
        info.kind = "date"
        return info
    if n_unique <= 1:
        info.kind = "excluded"
        return info

    is_numeric = pd.api.types.is_numeric_dtype(series)
    n = len(non_missing)
    integer_like = _is_integer_like(series)

    # Kimlik değişkeni: (neredeyse) her satırda benzersiz ve isim ipucu veya metin/tamsayı
    if n > 10 and n_unique >= 0.9 * n:
        if _ID_NAME_RE.match(name):
            info.kind = "id"
            return info
        if n_unique == n and (not is_numeric or (integer_like and measure != "scale")):
            info.kind = "id"
            return info

    if not is_numeric:
        info.kind = "nominal" if n_unique <= 12 else "excluded"
        if n_unique == 2:
            info.kind = "binary"
        return info

    # SPSS ölçüm düzeyi güçlü bir ipucudur
    if measure == "scale" and n_unique > 2:
        info.kind = "continuous"
        return info
    if measure == "ordinal":
        info.kind = "ordinal" if n_unique > 2 else "binary"
        return info
    if measure == "nominal":
        info.kind = "binary" if n_unique == 2 else ("nominal" if n_unique <= 12 else "excluded")
        return info

    # Veriden çıkarım
    if n_unique == 2:
        info.kind = "binary"
    elif value_labels and n_unique <= 10:
        info.kind = "ordinal" if integer_like and _labels_look_ordered(value_labels) else "nominal"
    elif integer_like and 3 <= n_unique <= 7:
        info.kind = "ordinal"  # tipik Likert
    elif n_unique >= 8:
        info.kind = "continuous"
    else:
        info.kind = "nominal"
    return info


def _labels_look_ordered(value_labels: dict[str, str]) -> bool:
    """Değer anahtarları ardışık tamsayı ise sıralı (Likert) kabul et."""
    try:
        keys = sorted(float(k) for k in value_labels)
    except ValueError:
        return False
    return all(abs(b - a - 1) < 1e-9 for a, b in zip(keys, keys[1:]))


def infer_types(df: pd.DataFrame, meta: dict) -> list[VariableInfo]:
    return [infer_variable(col, df[col], meta) for col in df.columns]
