"""Otomatik planlayıcı testleri — generality'yi kilitler."""

import numpy as np
import pandas as pd

from sav2q1.engine import planner
from sav2q1.engine.io_sav import read_sav
from sav2q1.engine.profile import profile_dataset
from sav2q1.tests.synth import make_synthetic


def test_autoplan_on_synthetic(tmp_path):
    sav = tmp_path / "n.sav"
    make_synthetic(str(sav))
    prof = profile_dataset(read_sav(str(sav)))
    plan = planner.build_plan(prof)

    assert plan["group_var"] == "grup"                       # ad eşleşmesiyle bulundu
    assert "id" in plan["id_vars"]                            # kimlik dışlandı
    cmps = [s for s in plan["steps"] if "compare" in s["type"]]
    outcomes = {s["outcome"] for s in cmps}
    assert "stres" in outcomes and "yas" in outcomes         # sürekli değişkenler karşılaştırıldı
    assert all(s["type"] == "group_compare" for s in cmps)   # grup 2 düzeyli
    assert any(s["type"] == "categorical" for s in plan["steps"])  # cinsiyet×grup


def test_pii_and_float_id_handling():
    # Tam-sayı benzersiz -> kimlik; ondalık benzersiz -> sürekli (kimlik DEĞİL)
    n = 80
    rng = np.random.default_rng(0)
    df = pd.DataFrame({
        "kayitno": np.arange(1, n + 1),                       # int benzersiz -> id
        "HastaAdiSoyadi": [f"x{i}" for i in range(n)],        # string -> id + PII adı
        "insulin": rng.uniform(1, 140, n),                    # float benzersiz -> sürekli
        "grup": rng.integers(0, 3, n),                        # 3 düzey -> grup
        "olcum": rng.normal(50, 10, n),
    })
    import pyreadstat
    import tempfile, os
    path = os.path.join(tempfile.mkdtemp(), "t.sav")
    pyreadstat.write_sav(df, path)
    prof = profile_dataset(read_sav(path))
    plan = planner.build_plan(prof)

    assert "kayitno" in plan["id_vars"]
    assert "HastaAdiSoyadi" in plan["id_vars"]
    # insülin kimlik DEĞİL: karşılaştırmalarda yer almalı
    outcomes = {s.get("outcome") for s in plan["steps"] if "compare" in s["type"]}
    assert "insulin" in outcomes
