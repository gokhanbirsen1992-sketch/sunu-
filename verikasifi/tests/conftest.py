import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
import pytest


def make_synthetic_df(n: int = 150, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    grup_a = rng.normal(0, 1, size=(n // 2, 3))
    grup_b = rng.normal(6, 1, size=(n - n // 2, 3))
    x1 = np.concatenate([grup_a[:, 0], grup_b[:, 0]])
    x2 = np.concatenate([grup_a[:, 1], grup_b[:, 1]])
    x3 = np.concatenate([grup_a[:, 2], grup_b[:, 2]])

    cinsiyet = rng.choice(["Kadın", "Erkek"], n)
    skor = x1 * 0.5 + rng.normal(0, 2, n) + (cinsiyet == "Kadın") * 3
    kategori = rng.choice(["A", "B", "C"], n)
    sonuc = rng.choice(["Evet", "Hayır"], n, p=[0.35, 0.65])

    df = pd.DataFrame({
        "x1": x1, "x2": x2, "x3": x3,
        "skor": skor,
        "cinsiyet": cinsiyet,
        "kategori": kategori,
        "sonuc": sonuc,
    })
    df.loc[5:8, "skor"] = np.nan
    return df


@pytest.fixture()
def synthetic_df() -> pd.DataFrame:
    return make_synthetic_df()
