"""SPSS .sav okuma ve meta veri çıkarımı (pyreadstat tabanlı).

Değer kodlarını (numeric) ve etiketleri AYNI ANDA tutarız: analiz kodlarla
yapılır, raporlama etiketlerle (ör. 1 -> "Kadın"). `apply_value_formats=False`
bu yüzden zorunlu.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import pandas as pd
import pyreadstat


@dataclass
class SavData:
    df: pd.DataFrame
    column_labels: dict[str, str]          # değişken adı -> değişken etiketi
    value_labels: dict[str, dict[Any, str]]  # değişken adı -> {kod: etiket}
    measure: dict[str, str]                # değişken adı -> nominal|ordinal|scale
    n_rows: int
    source_file: str
    meta: Any = field(default=None, repr=False)


def read_sav(path: str) -> SavData:
    """.sav dosyasını oku; DataFrame + etiket/ölçek meta verisini döndür."""
    df, meta = pyreadstat.read_sav(path, apply_value_formats=False)

    names = list(meta.column_names)
    labels = list(meta.column_labels or [])
    column_labels = {n: (labels[i] or "") if i < len(labels) else "" for i, n in enumerate(names)}

    # pyreadstat: variable_value_labels -> {var: {code(float): label}}
    value_labels = {k: dict(v) for k, v in (meta.variable_value_labels or {}).items()}

    measure = dict(getattr(meta, "variable_measure", {}) or {})

    return SavData(
        df=df,
        column_labels=column_labels,
        value_labels=value_labels,
        measure=measure,
        n_rows=len(df),
        source_file=path,
        meta=meta,
    )


def write_sav(df: pd.DataFrame, path: str, *,
              column_labels: dict[str, str] | None = None,
              value_labels: dict[str, dict] | None = None,
              measure: dict[str, str] | None = None) -> None:
    """Test/sentetik veri üretimi için .sav yazıcı (etiketlerle birlikte)."""
    kwargs: dict[str, Any] = {}
    if column_labels:
        kwargs["column_labels"] = [column_labels.get(c, "") for c in df.columns]
    if value_labels:
        kwargs["variable_value_labels"] = value_labels
    if measure:
        kwargs["variable_measure"] = measure
    pyreadstat.write_sav(df, path, **kwargs)
