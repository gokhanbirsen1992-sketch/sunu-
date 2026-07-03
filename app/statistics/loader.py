"""SPSS .sav (ve yedek olarak .csv) dosyalarını DataFrame + metadata olarak yükler."""
from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_dataset(path: str | Path) -> tuple[pd.DataFrame, dict]:
    """Veri + metadata döndürür.

    metadata: {"labels": {col: label}, "value_labels": {col: {value: label}},
               "measures": {col: "nominal"|"ordinal"|"scale"|"unknown"}}
    """
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".sav":
        import pyreadstat

        df, meta = pyreadstat.read_sav(str(path), apply_value_formats=False)
        labels = {}
        if meta.column_labels:
            labels = {
                name: (lab if lab else None)
                for name, lab in zip(meta.column_names, meta.column_labels)
            }
        value_labels = {
            col: {str(k): str(v) for k, v in mapping.items()}
            for col, mapping in (meta.variable_value_labels or {}).items()
        }
        measures = dict(meta.variable_measure or {})
        return df, {"labels": labels, "value_labels": value_labels, "measures": measures}
    if suffix == ".csv":
        df = pd.read_csv(path)
        return df, {"labels": {}, "value_labels": {}, "measures": {}}
    raise ValueError(f"Desteklenmeyen dosya türü: {suffix} (yalnızca .sav ve .csv)")
