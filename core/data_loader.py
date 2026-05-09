from __future__ import annotations

from pathlib import Path
from typing import IO

import pandas as pd


SUPPORTED_EXT = {".csv", ".tsv", ".xlsx", ".xls", ".sav", ".dta"}


def load_dataframe(file: IO | str | Path, filename: str | None = None) -> pd.DataFrame:
    name = filename or getattr(file, "name", None) or str(file)
    ext = Path(name).suffix.lower()

    if ext == ".csv":
        return pd.read_csv(file)
    if ext == ".tsv":
        return pd.read_csv(file, sep="\t")
    if ext in {".xlsx", ".xls"}:
        return pd.read_excel(file)
    if ext == ".sav":
        import pyreadstat
        path = file if isinstance(file, (str, Path)) else _to_temp(file, ".sav")
        df, meta = pyreadstat.read_sav(str(path), apply_value_formats=True)
        df.attrs["spss_meta"] = {
            "column_labels": dict(zip(meta.column_names, meta.column_labels or [])),
            "value_labels": meta.variable_value_labels or {},
        }
        return df
    if ext == ".dta":
        return pd.read_stata(file)
    raise ValueError(f"Unsupported file extension: {ext}. Supported: {SUPPORTED_EXT}")


def _to_temp(uploaded, suffix: str) -> Path:
    import tempfile
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    tmp.write(uploaded.read())
    tmp.flush()
    tmp.close()
    return Path(tmp.name)


def missing_summary(df: pd.DataFrame) -> pd.DataFrame:
    n = len(df)
    out = pd.DataFrame({
        "n_missing": df.isna().sum(),
        "pct_missing": (df.isna().sum() / n * 100).round(2),
        "n_unique": df.nunique(dropna=True),
        "dtype": df.dtypes.astype(str),
    })
    return out.sort_values("pct_missing", ascending=False)


def impute(df: pd.DataFrame, strategy: str = "median_mode") -> pd.DataFrame:
    out = df.copy()
    for col in out.columns:
        if out[col].isna().sum() == 0:
            continue
        if pd.api.types.is_numeric_dtype(out[col]):
            if strategy in {"median_mode", "median"}:
                out[col] = out[col].fillna(out[col].median())
            elif strategy == "mean":
                out[col] = out[col].fillna(out[col].mean())
        else:
            mode = out[col].mode(dropna=True)
            if len(mode):
                out[col] = out[col].fillna(mode.iloc[0])
    return out
