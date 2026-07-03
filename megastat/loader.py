"""Veri dosyası yükleme: CSV, Excel (.xlsx/.xls) ve SPSS (.sav/.zsav).

CSV için kodlama sırayla denenir (utf-8 → utf-8-sig → cp1254 (Türkçe) → latin-1) ve
ayraç otomatik algılanır. SPSS için değer etiketleri uygulanır ki kategoriler okunur olsun.
"""
from __future__ import annotations

import io
from pathlib import Path

import pandas as pd

DESTEKLENEN_UZANTILAR = (".csv", ".txt", ".xlsx", ".xls", ".sav", ".zsav")

_CSV_KODLAMALAR = ("utf-8", "utf-8-sig", "cp1254", "latin-1")


def _read_csv_bytes(data: bytes) -> pd.DataFrame:
    son_hata: Exception | None = None
    for kodlama in _CSV_KODLAMALAR:
        try:
            # sep=None + engine="python": ayraç (virgül / noktalı virgül / tab) otomatik bulunur
            return pd.read_csv(io.BytesIO(data), sep=None, engine="python", encoding=kodlama)
        except (UnicodeDecodeError, pd.errors.ParserError) as exc:
            son_hata = exc
    raise ValueError(f"CSV dosyası okunamadı: {son_hata}")


def load_bytes(data: bytes, filename: str) -> pd.DataFrame:
    """Bellekteki dosya içeriğini (web yüklemesi) DataFrame'e çevirir."""
    suffix = Path(filename).suffix.lower()
    if suffix in (".csv", ".txt"):
        return _read_csv_bytes(data)
    if suffix in (".xlsx", ".xls"):
        return pd.read_excel(io.BytesIO(data))
    if suffix in (".sav", ".zsav"):
        import tempfile

        import pyreadstat

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
            tmp.write(data)
            tmp.flush()
            df, _meta = pyreadstat.read_sav(tmp.name, apply_value_formats=True)
        return df
    raise ValueError(
        f"Desteklenmeyen dosya türü: '{suffix}'. Desteklenenler: {', '.join(DESTEKLENEN_UZANTILAR)}"
    )


def load_dataset(path: str | Path) -> pd.DataFrame:
    """Diskteki dosyayı DataFrame'e çevirir."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Dosya bulunamadı: {path}")
    df = load_bytes(path.read_bytes(), path.name)
    if df.empty:
        raise ValueError("Dosya yüklendi ama içinde hiç satır yok.")
    return df
