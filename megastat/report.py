"""Analiz sonuçlarını çok sayfalı Excel (.xlsx) raporuna ve metin özetine dönüştürür."""
from __future__ import annotations

import io
from typing import Any

import numpy as np
import pandas as pd

from megastat.engine import ALFA, AnalysisResult


def _anlamli_bulgular(sonuc: AnalysisResult) -> pd.DataFrame:
    """FDR düzeltmesi sonrası anlamlı kalan tüm bulguları tek tabloda toplar."""
    satirlar: list[dict[str, Any]] = []
    k = sonuc.korelasyonlar
    if not k.empty:
        for _, r in k[k["FDR sonrası anlamlı"] == "EVET ✓"].iterrows():
            satirlar.append({
                "tür": "korelasyon",
                "bulgu": f"{r['değişken 1']} ↔ {r['değişken 2']}",
                "istatistik": f"Pearson r = {r['Pearson r']:.3f} ({r['ilişki gücü']})",
                "ham p": r["Pearson p"],
                "FDR p": r["FDR p"],
                "n": r["n"],
            })
    g = sonuc.grup_karsilastirmalari
    if not g.empty:
        for _, r in g[g["FDR sonrası anlamlı"] == "EVET ✓"].iterrows():
            satirlar.append({
                "tür": "grup farkı",
                "bulgu": f"{r['sayısal değişken']} — {r['gruplayıcı']} gruplarına göre",
                "istatistik": f"{r['önerilen test']}; etki: {r.get('etki yorumu', '')}",
                "ham p": r["önerilen test p"],
                "FDR p": r["FDR p"],
                "n": r["toplam n"],
            })
    c = sonuc.kategorik_iliskiler
    if not c.empty:
        for _, r in c[c["FDR sonrası anlamlı"] == "EVET ✓"].iterrows():
            satirlar.append({
                "tür": "kategorik ilişki",
                "bulgu": f"{r['değişken 1']} ↔ {r['değişken 2']}",
                "istatistik": f"ki-kare = {r['ki-kare']:.3f}, Cramér V = {r['Cramér V']:.3f}",
                "ham p": r["ki-kare p"],
                "FDR p": r["FDR p"],
                "n": r["n"],
            })
    tablo = pd.DataFrame(satirlar)
    if not tablo.empty:
        tablo = tablo.sort_values("FDR p").reset_index(drop=True)
    return tablo


def excel_raporu(sonuc: AnalysisResult) -> bytes:
    """Tüm tabloları çok sayfalı .xlsx dosyasına yazar, bayt olarak döndürür."""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as yazici:
        ozet = pd.DataFrame(
            [{"özellik": k, "değer": v} for k, v in sonuc.ozet.items()]
        )
        ozet.to_excel(yazici, sheet_name="Özet", index=False)

        anlamli = _anlamli_bulgular(sonuc)
        (anlamli if not anlamli.empty else pd.DataFrame(
            [{"bilgi": f"FDR düzeltmesi sonrası p<{ALFA} olan bulgu yok"}]
        )).to_excel(yazici, sheet_name="Anlamlı Bulgular", index=False)

        degisken_tablo = pd.DataFrame([
            {"değişken": d.ad, "tip": d.tip, "n": d.n, "eksik": d.eksik, "benzersiz": d.benzersiz}
            for d in sonuc.degiskenler
        ])
        if sonuc.atlanan_sutunlar:
            degisken_tablo = pd.concat(
                [degisken_tablo, pd.DataFrame(sonuc.atlanan_sutunlar).rename(
                    columns={"sutun": "değişken", "neden": "atlanma nedeni"})],
                ignore_index=True,
            )
        degisken_tablo.to_excel(yazici, sheet_name="Değişkenler", index=False)

        sayfalar = [
            ("Betimsel (Sayısal)", sonuc.betimsel_sayisal),
            ("Betimsel (Kategorik)", sonuc.betimsel_kategorik),
            ("Korelasyonlar", sonuc.korelasyonlar),
            ("Grup Karşılaştırmaları", sonuc.grup_karsilastirmalari),
            ("Post-Hoc", sonuc.posthoc),
            ("Kategorik İlişkiler", sonuc.kategorik_iliskiler),
        ]
        for ad, tablo in sayfalar:
            if tablo.empty:
                pd.DataFrame([{"bilgi": "bu kategoride hesaplanacak test bulunamadı"}]).to_excel(
                    yazici, sheet_name=ad, index=False
                )
            else:
                tablo.to_excel(yazici, sheet_name=ad, index=False)

        if sonuc.atlanan_testler:
            pd.DataFrame(sonuc.atlanan_testler).to_excel(
                yazici, sheet_name="Atlanan Testler", index=False
            )
    return buf.getvalue()


def metin_ozeti(sonuc: AnalysisResult, en_fazla_bulgu: int = 25) -> str:
    """Konsol / web için okunabilir Türkçe özet."""
    o = sonuc.ozet
    satirlar = [
        "═══ MegaStat Analiz Özeti ═══",
        f"Veri: {o['satır sayısı']} satır × {o['sütun sayısı']} sütun "
        f"({o['sayısal değişken']} sayısal, {o['kategorik değişken']} kategorik değişken kullanıldı)",
        f"Hesaplanan istatistik sayısı: {o['hesaplanan istatistik (hücre) sayısı']:,}".replace(",", "."),
        f"Çalıştırılan test grupları: {o['korelasyon çifti']} korelasyon çifti, "
        f"{o['grup karşılaştırması']} grup karşılaştırması, "
        f"{o['post-hoc karşılaştırma']} post-hoc, {o['kategorik ilişki testi']} kategorik ilişki",
        f"FDR düzeltmesi sonrası anlamlı bulgu: {o['FDR sonrası anlamlı bulgu']}",
        "",
    ]
    anlamli = _anlamli_bulgular(sonuc)
    if anlamli.empty:
        satirlar.append(
            f"Çoklu test düzeltmesi (FDR) sonrası p<{ALFA} kalan bulgu yok. "
            "Ham p-değerleri Excel raporundaki tablolarda."
        )
    else:
        satirlar.append(f"── En güçlü {min(en_fazla_bulgu, len(anlamli))} bulgu (FDR p'ye göre) ──")
        for _, r in anlamli.head(en_fazla_bulgu).iterrows():
            fdr = r["FDR p"]
            fdr_s = f"{fdr:.2e}" if (isinstance(fdr, float) and not np.isnan(fdr)) else "?"
            satirlar.append(f"• [{r['tür']}] {r['bulgu']} — {r['istatistik']} (FDR p={fdr_s}, n={r['n']})")
    if sonuc.atlanan_sutunlar:
        satirlar.append("")
        satirlar.append(f"Atlanan sütun: {len(sonuc.atlanan_sutunlar)} (ayrıntı Excel'de)")
    return "\n".join(satirlar)
