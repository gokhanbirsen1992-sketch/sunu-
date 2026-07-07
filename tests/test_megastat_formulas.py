"""MegaStat gizli formül katmanı (formulas.py) testleri."""
import io

import numpy as np
import pandas as pd
import pytest

from megastat.engine import ALFA, analyze_dataframe
from megastat.formulas import formul_analizi
from megastat.report import excel_raporu, metin_ozeti


@pytest.fixture()
def formul_veri() -> pd.DataFrame:
    """Bilinen gizli formüller içeren veri: logaritmik, karesel ve etkileşim."""
    rng = np.random.default_rng(11)
    n = 250
    doz = rng.uniform(1, 50, n)
    yas = rng.uniform(20, 70, n)
    stres = rng.uniform(0, 10, n)
    destek = rng.uniform(0, 10, n)
    return pd.DataFrame({
        "doz": doz,
        "yas": yas,
        "stres": stres,
        "destek": destek,
        # logaritmik gizli formül: etki = 5 + 8·ln(doz)
        "etki": 5 + 8 * np.log(doz) + rng.normal(0, 2, n),
        # karesel gizli formül: performans yaşla önce artar sonra düşer
        "performans": 20 + 4 * yas - 0.045 * yas ** 2 + rng.normal(0, 3, n),
        # etkileşim: stresin tükenmişlik etkisini destek zayıflatır
        "tukenmislik": 10 + 3 * stres - 0.25 * stres * destek + rng.normal(0, 2, n),
        # düz doğrusal kontrol: gizli formül ÇIKMAMALI
        "kontrol": 2 * yas + rng.normal(0, 5, n),
    })


def test_gizli_formuller_bulunur(formul_veri):
    atlanan: list[dict[str, str]] = []
    say = list(formul_veri.columns)
    f = formul_analizi(formul_veri, say, [], atlanan)
    eg = f.egriler
    assert not eg.empty

    def satir(bagimli, yordayici):
        m = eg[((eg["bağımlı"] == bagimli) & (eg["yordayıcı"] == yordayici))
               | ((eg["bağımlı"] == yordayici) & (eg["yordayıcı"] == bagimli))]
        return m.iloc[0]

    # Logaritmik formül yakalanmalı ve denklem yazılmalı
    log_satir = satir("etki", "doz")
    assert log_satir["gizli formül mü"].startswith("EVET")
    assert log_satir["en iyi model"] in ("logaritmik", "güç")  # ikisi de eğriseldir
    assert "=" in log_satir["denklem"]
    assert log_satir["doğrusal ötesi kazanç"] > 0.05

    # Karesel formül yakalanmalı
    kare_satir = satir("performans", "yas")
    assert kare_satir["gizli formül mü"].startswith("EVET")
    assert kare_satir["en iyi model"] in ("karesel", "kübik")

    # Düz doğrusal ilişkide gizli formül İDDİA EDİLMEMELİ
    kontrol_satir = satir("kontrol", "yas")
    assert kontrol_satir["gizli formül mü"].startswith("hayır")


def test_etkilesim_bulunur(formul_veri):
    atlanan: list[dict[str, str]] = []
    say = list(formul_veri.columns)
    f = formul_analizi(formul_veri, say, [], atlanan)
    et = f.etkilesimler
    assert not et.empty
    hedef = et[(et["bağımlı"] == "tukenmislik")
               & (et["X (yordayıcı)"].isin(["stres", "destek"]))
               & (et["Z (moderatör)"].isin(["stres", "destek"]))].iloc[0]
    assert hedef["FDR p"] < ALFA          # gerçek etkileşim FDR sonrası ayakta
    assert hedef["etkileşim B (std)"] < 0  # destek etkiyi zayıflatıyor
    assert "zayıflıyor" in hedef["yorum"]


def test_ikili_kategorik_moderator(formul_veri):
    veri = formul_veri.copy()
    rng = np.random.default_rng(5)
    veri["cinsiyet"] = rng.choice(["K", "E"], len(veri))
    atlanan: list[dict[str, str]] = []
    f = formul_analizi(veri, [c for c in formul_veri.columns], ["cinsiyet"], atlanan)
    assert (f.etkilesimler["Z (moderatör)"].str.contains("cinsiyet")
            | f.etkilesimler["X (yordayıcı)"].str.contains("cinsiyet")).any()


def test_uctan_uca_formul_katmani(formul_veri):
    sonuc = analyze_dataframe(formul_veri, kesif_yap=False)
    assert sonuc.formuller is not None
    o = sonuc.ozet
    assert o["eğri (formül) taraması"] > 0
    assert o["belirgin gizli formül"] >= 2      # log + karesel
    assert o["etkileşim (moderasyon) modeli"] > 0

    rapor = excel_raporu(sonuc)
    tablolar = pd.read_excel(io.BytesIO(rapor), sheet_name=None)
    assert "Gizli Formüller (Eğri)" in tablolar
    assert "Etkileşim (Moderasyon)" in tablolar

    ozet = metin_ozeti(sonuc)
    assert "Gizli formül taraması" in ozet

    # Belirgin gizli formüller Anlamlı Bulgular sayfasına da düşmeli
    anlamli = tablolar["Anlamlı Bulgular"]
    assert (anlamli["tür"] == "gizli formül").any()
    assert (anlamli["tür"] == "etkileşim (moderasyon)").any()


def test_kucuk_veri_formul_katmani_cokmez():
    df = pd.DataFrame({"a": np.arange(5, dtype=float), "b": np.arange(5, dtype=float) ** 2})
    sonuc = analyze_dataframe(df, kesif_yap=False)  # hata vermemeli
    assert sonuc.ozet["satır sayısı"] == 5
