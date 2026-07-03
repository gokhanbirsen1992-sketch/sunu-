"""Sentetik SPSS veri seti fixture'ları."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest


def make_synthetic_df(n: int = 120, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    gender = rng.choice([1.0, 2.0], size=n)
    group3 = rng.choice([1.0, 2.0, 3.0], size=n)
    # cinsiyete göre gerçek fark: kadınlarda daha yüksek kaygı
    anxiety = rng.normal(50, 10, n) + (gender == 1.0) * 6
    satisfaction = 100 - 0.6 * anxiety + rng.normal(0, 8, n)  # negatif korelasyon
    income = np.exp(rng.normal(8, 1.4, n))  # güçlü çarpık (lognormal)
    likert = rng.integers(1, 6, n).astype(float)
    smoker = rng.choice([0.0, 1.0], size=n, p=[0.7, 0.3])

    df = pd.DataFrame(
        {
            "id": np.arange(1, n + 1, dtype=float),
            "cinsiyet": gender,
            "grup": group3,
            "kaygi": anxiety,
            "doyum": satisfaction,
            "gelir": income,
            "memnuniyet": likert,
            "sigara": smoker,
        }
    )
    # eksik ve aykırı değer enjeksiyonu
    df.loc[3:6, "kaygi"] = np.nan
    df.loc[10, "gelir"] = df["gelir"].max() * 30  # uç aykırı
    df.loc[[20, 21], :] = df.loc[[5, 6], :].values  # kopya satırlar
    return df


SYN_META = {
    "column_labels": [
        "Katılımcı No", "Cinsiyet", "Deney Grubu", "Kaygı Puanı",
        "Yaşam Doyumu", "Aylık Gelir", "Genel Memnuniyet", "Sigara Kullanımı",
    ],
    "variable_value_labels": {
        "cinsiyet": {1.0: "Kadın", 2.0: "Erkek"},
        "grup": {1.0: "Kontrol", 2.0: "Deney A", 3.0: "Deney B"},
        "sigara": {0.0: "Hayır", 1.0: "Evet"},
    },
    "variable_measure": {
        "id": "scale", "cinsiyet": "nominal", "grup": "nominal", "kaygi": "scale",
        "doyum": "scale", "gelir": "scale", "memnuniyet": "ordinal", "sigara": "nominal",
    },
}


@pytest.fixture()
def synthetic_df() -> pd.DataFrame:
    return make_synthetic_df()


@pytest.fixture()
def sav_path(tmp_path, synthetic_df):
    import pyreadstat

    path = tmp_path / "veri.sav"
    pyreadstat.write_sav(
        synthetic_df, str(path),
        column_labels=SYN_META["column_labels"],
        variable_value_labels=SYN_META["variable_value_labels"],
        variable_measure=SYN_META["variable_measure"],
    )
    return path
