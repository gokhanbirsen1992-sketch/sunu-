"""MegaStat uçtan uca ve birim testleri."""
import io

import numpy as np
import pandas as pd
import pytest

from megastat.engine import ALFA, analyze_dataframe, degiskenleri_algila
from megastat.loader import load_bytes
from megastat.report import excel_raporu, metin_ozeti


@pytest.fixture()
def ornek_veri() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    n = 120
    grup = rng.choice(["Kontrol", "Deney"], size=n)
    cinsiyet = rng.choice(["Kadın", "Erkek"], size=n)
    egitim = rng.choice(["İlkokul", "Lise", "Üniversite"], size=n)
    yas = rng.normal(40, 10, size=n)
    # 'skor' grupla gerçekten ilişkili → anlamlı fark çıkmalı
    skor = rng.normal(50, 8, size=n) + np.where(grup == "Deney", 10, 0)
    # 'gelir' yaşla korelasyonlu → anlamlı korelasyon çıkmalı
    gelir = 1000 + 50 * yas + rng.normal(0, 100, size=n)
    return pd.DataFrame({
        "hasta_no": np.arange(1, n + 1),          # kimlik → atlanmalı
        "grup": grup,
        "cinsiyet": cinsiyet,
        "egitim": egitim,
        "yas": yas,
        "skor": skor,
        "gelir": gelir,
        "sabit": 1,                                # sabit → atlanmalı
        "likert": rng.integers(1, 6, size=n),      # 1-5 → kategorik sayılmalı
    })


def test_degisken_algilama(ornek_veri):
    degiskenler, atlanan = degiskenleri_algila(ornek_veri.copy())
    adlar = {d.ad: d.tip for d in degiskenler}
    assert adlar["yas"] == "sayisal"
    assert adlar["grup"] == "kategorik"
    assert adlar["likert"] == "kategorik"
    atlanan_adlar = {a["sutun"] for a in atlanan}
    assert "sabit" in atlanan_adlar
    assert "hasta_no" in atlanan_adlar


def test_tam_analiz(ornek_veri):
    sonuc = analyze_dataframe(ornek_veri)
    o = sonuc.ozet
    assert o["satır sayısı"] == 120
    assert o["korelasyon çifti"] == 3          # yas-skor, yas-gelir, skor-gelir
    assert o["grup karşılaştırması"] == 12     # 4 kategorik × 3 sayısal
    assert o["kategorik ilişki testi"] == 6    # C(4,2) kategorik çift
    assert o["hesaplanan istatistik (hücre) sayısı"] > 500

    # Gerçek etkiler FDR sonrası bile anlamlı olmalı
    kor = sonuc.korelasyonlar
    yas_gelir = kor[(kor["değişken 1"] == "yas") & (kor["değişken 2"] == "gelir")].iloc[0]
    assert yas_gelir["FDR p"] < ALFA
    grup_tablo = sonuc.grup_karsilastirmalari
    skor_grup = grup_tablo[
        (grup_tablo["sayısal değişken"] == "skor") & (grup_tablo["gruplayıcı"] == "grup")
    ].iloc[0]
    assert skor_grup["FDR p"] < ALFA
    assert abs(skor_grup["Cohen d"]) > 0.5


def test_duzeltme_sutunlari_var(ornek_veri):
    sonuc = analyze_dataframe(ornek_veri)
    for tablo in (sonuc.korelasyonlar, sonuc.grup_karsilastirmalari, sonuc.kategorik_iliskiler):
        for sutun in ("Bonferroni p", "Holm p", "FDR p", "FDR sonrası anlamlı"):
            assert sutun in tablo.columns


def test_excel_ve_ozet(ornek_veri):
    sonuc = analyze_dataframe(ornek_veri)
    rapor = excel_raporu(sonuc)
    assert rapor[:2] == b"PK"  # geçerli xlsx (zip) imzası
    tablolar = pd.read_excel(io.BytesIO(rapor), sheet_name=None)
    for sayfa in ("Özet", "Anlamlı Bulgular", "Korelasyonlar", "Grup Karşılaştırmaları"):
        assert sayfa in tablolar
    ozet = metin_ozeti(sonuc)
    assert "MegaStat" in ozet
    assert "anlamlı bulgu" in ozet


def test_kucuk_veri_cokmez():
    df = pd.DataFrame({"a": [1.0, 2.0], "b": ["x", "y"]})
    sonuc = analyze_dataframe(df)  # test üretmese de hata vermemeli
    assert sonuc.ozet["satır sayısı"] == 2


def test_csv_kodlama_geri_dusme():
    icerik = "ad;yaş\nAyşe;30\nÖmer;25\n".encode("cp1254")
    df = load_bytes(icerik, "veri.csv")
    assert list(df.columns) == ["ad", "yaş"]
    assert len(df) == 2


def test_web_uctan_uca(ornek_veri):
    from fastapi.testclient import TestClient

    from megastat.web import app

    istemci = TestClient(app)
    assert istemci.get("/").status_code == 200

    buf = io.BytesIO()
    ornek_veri.to_csv(buf, index=False)
    yanit = istemci.post(
        "/analiz", files={"dosya": ("veri.csv", buf.getvalue(), "text/csv")}
    )
    assert yanit.status_code == 200, yanit.text
    veri = yanit.json()
    assert "MegaStat" in veri["ozet_html"]
    indirme = istemci.get(veri["indir"])
    assert indirme.status_code == 200
    assert indirme.content[:2] == b"PK"
