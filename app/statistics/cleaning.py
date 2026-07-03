"""Veri temizleme: kopyalar, sabit sütunlar, aşırı eksik satırlar, aykırı değerler."""
from __future__ import annotations

import pandas as pd

from app.models import CleaningReport, VariableInfo

IQR_FACTOR = 3.0  # yalnızca uç (extreme) aykırı değerler işaretlenir
HIGH_MISSING_ROW_RATIO = 0.5


def clean(df: pd.DataFrame, variables: list[VariableInfo]) -> tuple[pd.DataFrame, CleaningReport]:
    report = CleaningReport(rows_before=len(df))
    df = df.copy()

    # 1) Birebir kopya satırlar
    dup_mask = df.duplicated()
    report.duplicates_removed = int(dup_mask.sum())
    if report.duplicates_removed:
        df = df[~dup_mask]
        report.actions.append(f"{report.duplicates_removed} birebir kopya satır silindi.")

    analysis_vars = [v for v in variables if v.kind in ("continuous", "ordinal", "nominal", "binary")]
    analysis_cols = [v.name for v in analysis_vars if v.name in df.columns]

    # 2) Sabit sütunlar
    for v in list(analysis_vars):
        if v.name in df.columns and df[v.name].dropna().nunique() <= 1:
            report.constant_columns.append(v.name)
            v.kind = "excluded"
    if report.constant_columns:
        report.actions.append(
            "Sabit (tek değerli) sütunlar analiz dışı bırakıldı: " + ", ".join(report.constant_columns)
        )
        analysis_cols = [c for c in analysis_cols if c not in report.constant_columns]

    # 3) Analiz değişkenlerinin yarısından fazlası eksik olan satırlar
    if analysis_cols:
        missing_ratio = df[analysis_cols].isna().mean(axis=1)
        high_missing = missing_ratio > HIGH_MISSING_ROW_RATIO
        report.high_missing_rows_removed = int(high_missing.sum())
        if report.high_missing_rows_removed:
            df = df[~high_missing]
            report.actions.append(
                f"Analiz değişkenlerinin >%50'si eksik olan {report.high_missing_rows_removed} satır çıkarıldı."
            )

    # 4) Sürekli değişkenlerde uç aykırı değerler (3×IQR dışı) eksik değere çevrilir
    for v in analysis_vars:
        if v.kind != "continuous" or v.name not in df.columns:
            continue
        col = pd.to_numeric(df[v.name], errors="coerce")
        q1, q3 = col.quantile(0.25), col.quantile(0.75)
        iqr = q3 - q1
        if iqr == 0 or pd.isna(iqr):
            continue
        lo, hi = q1 - IQR_FACTOR * iqr, q3 + IQR_FACTOR * iqr
        mask = (col < lo) | (col > hi)
        n_out = int(mask.sum())
        if n_out:
            report.outliers[v.name] = n_out
            df.loc[mask, v.name] = pd.NA
            df[v.name] = pd.to_numeric(df[v.name], errors="coerce")
    if report.outliers:
        total = sum(report.outliers.values())
        report.actions.append(
            f"{total} uç aykırı değer (3×IQR dışı) eksik veri olarak işaretlendi: "
            + ", ".join(f"{k} ({n})" for k, n in report.outliers.items())
        )

    # 5) Eksik veri özeti
    for c in analysis_cols:
        n_miss = int(df[c].isna().sum())
        if n_miss:
            report.missing_summary[c] = n_miss

    report.rows_after = len(df)
    if not report.actions:
        report.actions.append("Veri temiz görünüyor; müdahale gerekmedi.")
    report.actions.append(
        f"Nihai veri seti: {report.rows_after} satır. Testler değişken bazında mevcut veriyle (pairwise) yürütülür."
    )
    return df, report


def apply_value_labels(df: pd.DataFrame, variables: list[VariableInfo]) -> pd.DataFrame:
    """Nominal/binary değişkenlerde ham kodları (1.0) etiketlere (Kadın) çevirir."""
    df = df.copy()
    for v in variables:
        if v.kind not in ("nominal", "binary") or not v.value_labels or v.name not in df.columns:
            continue
        labels = dict(v.value_labels)

        def _map(x):
            if pd.isna(x):
                return x
            for key in (str(x), str(int(x)) if isinstance(x, float) and float(x).is_integer() else None):
                if key is not None and key in labels:
                    return labels[key]
            return x

        df[v.name] = df[v.name].map(_map)
    return df
