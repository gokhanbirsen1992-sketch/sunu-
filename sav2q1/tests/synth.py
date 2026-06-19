"""Sentetik sağlık/hemşirelik .sav üretimi (testler + script paylaşır).

GERÇEK hasta verisi DEĞİLDİR; sabit-seed kurgusal veri.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from sav2q1.engine.io_sav import write_sav

SEED = 2026
N = 220


def make_synthetic(out_path: str, seed: int = SEED, n: int = N) -> str:
    rng = np.random.default_rng(seed)

    grup = rng.integers(1, 3, size=n)
    cinsiyet = rng.choice([1, 2], size=n, p=[0.62, 0.38])
    yas = np.clip(rng.normal(41, 11, size=n), 18, 75).round().astype(int)
    egitim = rng.choice([1, 2, 3, 4], size=n, p=[0.15, 0.4, 0.3, 0.15])
    kronik = rng.choice([0, 1], size=n, p=[0.7, 0.3])
    stres = np.clip(42 + np.where(grup == 2, 5.0, 0.0) + rng.normal(0, 8, size=n), 10, 70).round(1)
    lin = -6 + 0.12 * stres + 0.4 * kronik
    tukenmislik = (rng.random(n) < 1 / (1 + np.exp(-lin))).astype(int)
    latent = rng.normal(0, 1, size=n)
    items = {f"olcek{i}": np.clip(np.round(3 + 0.9 * latent + rng.normal(0, 0.8, size=n)), 1, 5).astype(int)
             for i in range(1, 11)}

    df = pd.DataFrame({"id": np.arange(1, n + 1), "grup": grup, "cinsiyet": cinsiyet,
                       "yas": yas, "egitim": egitim, "kronik": kronik, "stres": stres,
                       "tukenmislik": tukenmislik, **items})

    column_labels = {"id": "Katılımcı no", "grup": "Çalışma grubu", "cinsiyet": "Cinsiyet",
                     "yas": "Yaş (yıl)", "egitim": "Öğrenim düzeyi", "kronik": "Kronik hastalık varlığı",
                     "stres": "Algılanan Stres Ölçeği puanı", "tukenmislik": "Tükenmişlik (var/yok)",
                     **{f"olcek{i}": f"Ölçek maddesi {i}" for i in range(1, 11)}}
    value_labels = {"grup": {1: "Müdahale", 2: "Kontrol"}, "cinsiyet": {1: "Kadın", 2: "Erkek"},
                    "egitim": {1: "İlkokul", 2: "Lise", 3: "Lisans", 4: "Lisansüstü"},
                    "kronik": {0: "Yok", 1: "Var"}, "tukenmislik": {0: "Yok", 1: "Var"}}
    measure = {"id": "nominal", "grup": "nominal", "cinsiyet": "nominal", "yas": "scale",
               "egitim": "ordinal", "kronik": "nominal", "stres": "scale", "tukenmislik": "nominal",
               **{f"olcek{i}": "ordinal" for i in range(1, 11)}}

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_sav(df, str(out), column_labels=column_labels, value_labels=value_labels, measure=measure)
    return str(out)
