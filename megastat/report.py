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
    g2 = sonuc.gelismis
    if g2 is not None:
        e = g2.eslestirilmis
        if not e.empty and "FDR sonrası anlamlı" in e:
            for _, r in e[e["FDR sonrası anlamlı"] == "EVET ✓"].iterrows():
                satirlar.append({
                    "tür": "eşleştirilmiş fark",
                    "bulgu": f"{r['ölçüm 1']} vs {r['ölçüm 2']}",
                    "istatistik": (
                        f"{r['önerilen test']}; ort. fark = {r['ortalama fark']:.3f}, "
                        f"Cohen d_z = {r['Cohen d_z']:.3f}"
                    ),
                    "ham p": r["önerilen test p"],
                    "FDR p": r["FDR p"],
                    "n": r["n (çift)"],
                })
        lo = g2.lojistik
        if not lo.empty and "FDR sonrası anlamlı" in lo:
            for _, r in lo[lo["FDR sonrası anlamlı"] == "EVET ✓"].iterrows():
                satirlar.append({
                    "tür": "lojistik yordayıcı",
                    "bulgu": f"{r['sonuç değişkeni']}={r['olay (1) düzeyi']} ← {r['yordayıcı']}",
                    "istatistik": (
                        f"OR = {r['odds oranı (OR)']:.3f} "
                        f"(%95 GA {r['OR %95 GA alt']:.3f}–{r['OR %95 GA üst']:.3f}), "
                        f"model AUC = {r['model AUC']:.3f}"
                    ),
                    "ham p": r["p"],
                    "FDR p": r["FDR p"],
                    "n": r["n"],
                })
    f = sonuc.formuller
    if f is not None:
        eg = f.egriler
        if not eg.empty:
            secim = eg[eg["gizli formül mü"].str.startswith("EVET")
                       & (eg["FDR sonrası anlamlı"] == "EVET ✓")]
            for _, r in secim.iterrows():
                satirlar.append({
                    "tür": "gizli formül",
                    "bulgu": f"{r['bağımlı']} ← {r['yordayıcı']} ({r['en iyi model']})",
                    "istatistik": (
                        f"{r['denklem']} (düz. R²={r['en iyi düz. R²']:.3f}, "
                        f"doğrusal ötesi kazanç={r['doğrusal ötesi kazanç']:.3f})"
                    ),
                    "ham p": r["model p"],
                    "FDR p": r["FDR p"],
                    "n": r["n"],
                })
        et = f.etkilesimler
        if not et.empty and "FDR sonrası anlamlı" in et:
            for _, r in et[et["FDR sonrası anlamlı"] == "EVET ✓"].iterrows():
                satirlar.append({
                    "tür": "etkileşim (moderasyon)",
                    "bulgu": f"{r['bağımlı']} ← {r['X (yordayıcı)']} × {r['Z (moderatör)']}",
                    "istatistik": (
                        f"etkileşim B(std) = {r['etkileşim B (std)']:.3f}, "
                        f"ΔR² = {r['ΔR² (etkileşim katkısı)']:.3f}; {r['yorum']}"
                    ),
                    "ham p": r["p"],
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
        g2 = sonuc.gelismis
        if g2 is not None:
            sayfalar += [
                ("Eşleştirilmiş Testler", g2.eslestirilmis),
                ("Tekrarlı Ölçüm (Friedman)", g2.friedman),
                ("Uyum (Kappa-McNemar)", g2.uyum),
                ("Güvenilirlik (Alfa-Omega)", g2.guvenilirlik),
                ("Madde Analizi", g2.madde_analizi),
                ("Faktör Analizi (KMO)", g2.faktor_uygunluk),
                ("Faktör Yükleri", g2.faktor_yukler),
                ("Çoklu Regresyon", g2.coklu_regresyon),
                ("Lojistik Regresyon", g2.lojistik),
                ("ROC Analizi", g2.roc),
            ]
        f = sonuc.formuller
        if f is not None:
            sayfalar += [
                ("Gizli Formüller (Eğri)", f.egriler),
                ("Etkileşim (Moderasyon)", f.etkilesimler),
            ]
        for ad, tablo in sayfalar:
            if tablo.empty:
                pd.DataFrame([{"bilgi": "bu kategoride hesaplanacak test bulunamadı"}]).to_excel(
                    yazici, sheet_name=ad, index=False
                )
            else:
                tablo.to_excel(yazici, sheet_name=ad, index=False)

        # ── ML / Keşif katmanı sayfaları ──
        k = sonuc.kesif
        if k is not None and k.calisti:
            if k.one_cikanlar:
                pd.DataFrame({"ML Keşif Bulguları (öne çıkanlar)": k.one_cikanlar}).to_excel(
                    yazici, sheet_name="ML Keşif Özeti", index=False
                )
            kesif_sayfalar = [
                ("Doğrusal-Olmayan İlişkiler", k.dogrusal_olmayan),
                ("Öngörü (Gradient Boosting)", k.gbm_onem),
                ("Gizli Alt Gruplar", k.kumeler),
                ("Sıra Dışı Vakalar", k.anomaliler),
                ("Kısmi Korelasyon", k.kismi_korelasyon),
                ("Risk Modelleri", k.risk_modelleri),
                ("Riskli Vakalar", k.riskli_vakalar),
                ("Beklenen (Tanımsal) Korelasyon", k.gereksiz_korelasyonlar),
            ]
            for ad, tablo in kesif_sayfalar:
                if tablo is not None and not tablo.empty:
                    tablo.to_excel(yazici, sheet_name=ad[:31], index=False)

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
        f"Klasik istatistik hücresi: {o['hesaplanan istatistik (hücre) sayısı']:,}".replace(",", "."),
        f"TOPLAM hesaplama (klasik + ML, yaklaşık): "
        f"{o.get('TOPLAM hesaplama (yaklaşık)', 0):,}".replace(",", "."),
        f"Çalıştırılan test grupları: {o['korelasyon çifti']} korelasyon çifti, "
        f"{o['grup karşılaştırması']} grup karşılaştırması, "
        f"{o['post-hoc karşılaştırma']} post-hoc, {o['kategorik ilişki testi']} kategorik ilişki",
        f"Gelişmiş katman: {o.get('eşleştirilmiş test', 0)} eşleştirilmiş test, "
        f"{o.get('güvenilirlik analizi (ölçek)', 0)} güvenilirlik (Cronbach α), "
        f"{o.get('faktör analizi', 0)} faktör analizi, "
        f"{o.get('çoklu regresyon modeli', 0)} çoklu regresyon, "
        f"{o.get('lojistik regresyon modeli', 0)} lojistik regresyon, "
        f"{o.get('ROC analizi', 0)} ROC, {o.get('uyum testi (kappa/McNemar)', 0)} uyum testi",
        f"Gizli formül taraması: {o.get('eğri (formül) taraması', 0)} çiftte 7'şer model denendi → "
        f"{o.get('belirgin gizli formül', 0)} belirgin doğrusal-olmayan formül; "
        f"{o.get('etkileşim (moderasyon) modeli', 0)} etkileşim modeli",
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
    k = sonuc.kesif
    if k is not None:
        satirlar.append("")
        if not k.calisti:
            satirlar.append(f"ML keşif katmanı çalışmadı: {k.neden}")
        elif k.one_cikanlar:
            satirlar.append("── 🧠 ML KEŞİF KATMANI (Pearson'ın göremediği örüntüler) ──")
            satirlar.extend(f"{b}" for b in k.one_cikanlar)
            if not k.gereksiz_korelasyonlar.empty:
                satirlar.append(
                    f"ℹ️ {len(k.gereksiz_korelasyonlar)} apaçık/tanımsal korelasyon "
                    "(ör. birbirinin kopyası ölçümler) keşif listesinden ayıklandı — "
                    "Excel'de 'Beklenen (Tanımsal) Korelasyon' sayfasında."
                )
        else:
            satirlar.append(
                "🧠 ML keşif katmanı çalıştı; klasik testlerin ötesinde ek gizli örüntü bulunamadı."
            )
    if sonuc.atlanan_sutunlar:
        satirlar.append("")
        satirlar.append(f"Atlanan sütun: {len(sonuc.atlanan_sutunlar)} (ayrıntı Excel'de)")
    return "\n".join(satirlar)
