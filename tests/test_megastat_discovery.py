"""MegaStat 7 katmanlı keşif (ML) katmanı testleri.

Her katmanın gerçekten iş yaptığını sentetik 'gizli örüntülü' verilerle doğrular:
Pearson'ın kaçırdığı U-şekilli ilişki, gizli kümeler, anomaliler, risk modeli.
"""
import numpy as np
import pandas as pd
import pytest

from megastat.discovery import kesif_analizi
from megastat.engine import analyze_dataframe


@pytest.fixture()
def gizli_oruntulu_veri() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    n = 200
    x = rng.normal(0, 2, n)
    # U-şekli: Pearson ~0 ama güçlü bağımlılık → katman 3 bunu bulmalı
    u_iliskili = x**2 + rng.normal(0, 0.4, n)
    # İki gizli küme → katman 6 bulmalı
    kume = rng.choice([0, 1], n)
    boy = np.where(kume == 1, 180, 160) + rng.normal(0, 3, n)
    kilo = np.where(kume == 1, 85, 60) + rng.normal(0, 4, n)
    # İkili sonuç: skora gerçekten bağlı → katman 7 risk modeli AUC yüksek olmalı
    skor = rng.normal(50, 10, n)
    hastalik = np.where(skor + rng.normal(0, 5, n) > 55, "var", "yok")
    # Belirgin anomaliler → katman 6 anomali bulmalı
    boy[:3] = [230.0, 231.0, 95.0]
    return pd.DataFrame({
        "x": x,
        "u_iliskili": u_iliskili,
        "boy": boy,
        "kilo": kilo,
        "skor": skor,
        "yas": rng.normal(40, 8, n),
        "hastalik": hastalik,
    })


@pytest.fixture()
def kesif(gizli_oruntulu_veri):
    say = ["x", "u_iliskili", "boy", "kilo", "skor", "yas"]
    return kesif_analizi(gizli_oruntulu_veri, say, ["hastalik"])


def test_dogrusal_olmayan_iliski_bulunur(kesif):
    """Katman 3: Pearson'ın göremediği U-şekilli x↔u_iliskili bağını MI yakalamalı."""
    assert kesif.calisti
    t = kesif.dogrusal_olmayan
    assert not t.empty, "hiç doğrusal-olmayan ilişki bulunamadı"
    ciftler = {frozenset((r["değişken 1"], r["değişken 2"])) for _, r in t.iterrows()}
    assert frozenset(("x", "u_iliskili")) in ciftler


def test_gbm_ongoru_calisir(kesif):
    """Katman 4: gradient boosting en az bir hedefi şansın üstünde öngörmeli."""
    t = kesif.gbm_onem
    assert not t.empty
    assert (t["öngörülebilir mi"] == "EVET ✓").any()


def test_gizli_kumeler_bulunur(kesif):
    """Katman 6a: boy/kilo'daki iki gizli alt grup yakalanmalı."""
    assert not kesif.kumeler.empty
    assert kesif.kume_ozet.get("küme sayısı", 0) >= 2


def test_anomaliler_bulunur(kesif):
    """Katman 6b: uç boy değerli satırlar sıra dışı vaka listesine girmeli."""
    assert not kesif.anomaliler.empty
    isaretli = set(kesif.anomaliler["satır (orijinal indeks)"])
    assert isaretli & {0, 1, 2}, "eklenen uç vakalardan hiçbiri işaretlenmedi"


def test_risk_modeli_calisir(kesif):
    """Katman 7: hastalık riski modeli kurulmalı ve ayırt edici olmalı (AUC>0.7)."""
    t = kesif.risk_modelleri
    assert not t.empty
    satir = t[t["sonuç değişkeni"] == "hastalik"].iloc[0]
    assert satir["AUC (çapraz doğrulama)"] > 0.7
    assert not kesif.riskli_vakalar.empty


def test_tanimsal_korelasyon_ayiklanir():
    """|r|≥0.95 çiftler 'beklenen' kutusuna gitmeli, keşif listesine değil."""
    rng = np.random.default_rng(1)
    n = 150
    a = rng.normal(0, 1, n)
    df = pd.DataFrame({
        "toplam": a,
        "kopya": a * 2 + rng.normal(0, 0.05, n),  # tanımsal: r≈1
        "bagimsiz": rng.normal(0, 1, n),
        "dorduncu": rng.normal(0, 1, n),
    })
    k = kesif_analizi(df, ["toplam", "kopya", "bagimsiz", "dorduncu"], [])
    assert k.calisti
    assert not k.gereksiz_korelasyonlar.empty
    g = k.gereksiz_korelasyonlar.iloc[0]
    assert {g["değişken 1"], g["değişken 2"]} == {"toplam", "kopya"}


def test_tam_analiz_kesif_dahil(gizli_oruntulu_veri):
    """Uçtan uca: analyze_dataframe keşif katmanını da içermeli, Excel'e girmeli."""
    import io

    from megastat.report import excel_raporu, metin_ozeti

    sonuc = analyze_dataframe(gizli_oruntulu_veri)
    assert sonuc.kesif is not None and sonuc.kesif.calisti
    assert sonuc.ozet.get("ML keşif bulgusu", 0) > 0

    ozet = metin_ozeti(sonuc)
    assert "ML KEŞİF KATMANI" in ozet

    tablolar = pd.read_excel(io.BytesIO(excel_raporu(sonuc)), sheet_name=None)
    assert "ML Keşif Özeti" in tablolar
    assert "Doğrusal-Olmayan İlişkiler" in tablolar
    assert "Risk Modelleri" in tablolar


def test_kucuk_veri_kesif_zarif_atlanir():
    df = pd.DataFrame({"a": np.arange(10, dtype=float), "b": np.arange(10, dtype=float) ** 2})
    k = kesif_analizi(df, ["a", "b"], [])
    assert not k.calisti
    assert "satır" in k.neden
