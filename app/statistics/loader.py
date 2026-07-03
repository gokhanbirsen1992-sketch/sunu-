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
    if suffix in (".sav", ".zsav"):
        df, meta = _read_sav_with_fallbacks(path)
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
    if suffix in (".xlsx", ".xls"):
        df = pd.read_excel(path)
        return df, {"labels": {}, "value_labels": {}, "measures": {}}
    raise ValueError(f"Desteklenmeyen dosya türü: {suffix} (.sav, .csv, .xlsx veya .xls kullanın)")


def _read_sav_with_fallbacks(path: Path):
    """SPSS dosyasını okur; Türkçe/eski dosyalardaki kodlama sorunlarında
    yaygın kodlamalarla yeniden dener."""
    import pyreadstat

    last_error: Exception | None = None
    for encoding in (None, "WINDOWS-1254", "LATIN1", "WINDOWS-1252"):
        try:
            kwargs = {"apply_value_formats": False}
            if encoding:
                kwargs["encoding"] = encoding
            return pyreadstat.read_sav(str(path), **kwargs)
        except Exception as exc:
            last_error = exc
    raise ValueError(
        "SPSS dosyası okunamadı. Dosya bozuk olabilir veya çok eski bir SPSS sürümüyle "
        "kaydedilmiş olabilir. Çözüm: SPSS'te dosyayı açıp Dosya → Farklı Kaydet → "
        "'SPSS Statistics (*.sav)' biçimiyle yeniden kaydedin ve tekrar yükleyin. "
        f"(Teknik ayrıntı: {last_error})"
    ) from last_error
