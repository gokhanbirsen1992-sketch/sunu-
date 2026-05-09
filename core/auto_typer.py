from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd
import numpy as np


VarType = Literal["continuous", "binary", "categorical", "ordinal", "id_or_text"]


@dataclass
class ColumnInfo:
    name: str
    var_type: VarType
    n_unique: int
    sample_values: list


def infer_var_type(s: pd.Series, max_categorical: int = 12) -> VarType:
    s_clean = s.dropna()
    if s_clean.empty:
        return "id_or_text"

    n_unique = s_clean.nunique()

    if n_unique == 2:
        return "binary"

    if pd.api.types.is_numeric_dtype(s):
        if n_unique <= max_categorical and pd.api.types.is_integer_dtype(s):
            return "ordinal"
        return "continuous"

    if pd.api.types.is_datetime64_any_dtype(s):
        return "continuous"

    if n_unique <= max_categorical:
        return "categorical"

    if n_unique > 0.9 * len(s_clean):
        return "id_or_text"

    return "categorical"


def profile_columns(df: pd.DataFrame, max_categorical: int = 12) -> list[ColumnInfo]:
    out: list[ColumnInfo] = []
    for col in df.columns:
        s = df[col]
        vt = infer_var_type(s, max_categorical=max_categorical)
        sample = s.dropna().unique()[:5].tolist()
        out.append(ColumnInfo(
            name=col,
            var_type=vt,
            n_unique=int(s.nunique(dropna=True)),
            sample_values=sample,
        ))
    return out


def to_dataframe(infos: list[ColumnInfo]) -> pd.DataFrame:
    return pd.DataFrame([{
        "column": i.name,
        "type": i.var_type,
        "n_unique": i.n_unique,
        "sample": ", ".join(map(str, i.sample_values)),
    } for i in infos])
