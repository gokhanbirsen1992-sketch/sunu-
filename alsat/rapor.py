"""Rapor katmanı — Excel (çok sayfalı) + konsol metin özeti (megastat kalıbı)."""

from __future__ import annotations

import io

import pandas as pd

from alsat.dongu import DonguSonucu

_K_ACIKLAMA = {
    "K1_oos_sharpe": "OOS net Sharpe > 0.5 ve her sembolde > 0",
    "K2_dsr": "Deflated Sharpe Ratio ≥ 0.95 (kümülatif deneme düzeltmeli)",
    "K3_maliyet_2x": "2× işlem maliyetinde OOS toplam getiri > 0",
    "K4_dusus": "OOS maks düşüş, satın-al-tut düşüşünün %80'inden iyi",
    "K5_engel_yok": "Hakem (H1–H7) engel düzeyinde eleştiri bırakmadı",
}


def _tur_ozet_df(sonuc: DonguSonucu) -> pd.DataFrame:
    satirlar = []
    for t in sonuc.turlar:
        o = t.olcutler
        satirlar.append({
            "tur": t.tur_no, "aday": t.aday_sayisi, "kumulatif_deneme": t.kum_deneme,
            "secilen": t.secilen.etiket, "oos_sharpe": o["sharpe"],
            "oos_yillik_getiri": o["yillik_getiri"], "maks_dusus": o["maks_dusus"],
            "dsr": o["dsr"], "bootstrap_p": o["bootstrap_p"],
            "is_sharpe": o.get("is_sharpe"), "stres_2x_getiri": o.get("stres_2x_getiri"),
            "engel_sayisi": sum(1 for e in t.elestiriler if e.siddet == "engel"),
            "kabul": "EVET" if t.kabul else "hayır",
            "sonraki_tur_eylemleri": ", ".join(t.eylemler) or "-",
        })
    return pd.DataFrame(satirlar)


def _elestiri_df(sonuc: DonguSonucu) -> pd.DataFrame:
    satirlar = []
    for t in sonuc.turlar:
        for e in t.elestiriler:
            satirlar.append({"tur": t.tur_no, "kural": e.kural, "baslik": e.baslik,
                             "siddet": e.siddet, "bulgu": e.bulgu,
                             "oneri": (e.oneri or {}).get("eylem", "-")})
    return pd.DataFrame(satirlar)


def _kabul_df(sonuc: DonguSonucu) -> pd.DataFrame:
    t = sonuc.turlar[sonuc.final_tur_no - 1]
    return pd.DataFrame([
        {"kriter": k, "aciklama": _K_ACIKLAMA[k], "saglandi": "✓" if v else "✗"}
        for k, v in t.kabul_durumu.items()
    ])


def excel_raporu(sonuc: DonguSonucu) -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as yazici:
        _tur_ozet_df(sonuc).to_excel(yazici, sheet_name="Turlar", index=False)
        _elestiri_df(sonuc).to_excel(yazici, sheet_name="Elestiriler", index=False)
        _kabul_df(sonuc).to_excel(yazici, sheet_name="KabulKriterleri", index=False)
        for t in sonuc.turlar:
            if t.aday_tablosu is not None:
                t.aday_tablosu.to_excel(yazici, sheet_name=f"Tur{t.tur_no}_Adaylar",
                                        index=False)
        egri = pd.DataFrame({"satin_al_tut": sonuc.bh_ozsermaye})
        for t in sonuc.turlar:
            if t.oos_ozsermaye is not None:
                egri[f"tur{t.tur_no}"] = t.oos_ozsermaye
        egri.rename_axis("tarih").reset_index().to_excel(
            yazici, sheet_name="OzsermayeEgrileri", index=False)
        secimler = pd.DataFrame([
            {"tur": t.tur_no, "test_yili": y, "secilen": et}
            for t in sonuc.turlar for y, et in t.yillik_secimler.items()
        ])
        secimler.to_excel(yazici, sheet_name="YillikSecimler", index=False)
    return buf.getvalue()


def metin_ozeti(sonuc: DonguSonucu) -> str:
    p: list[str] = []
    p.append("=" * 72)
    p.append("ALSAT — Reviewer 2 döngüsü sonucu")
    p.append(f"Semboller: {', '.join(sonuc.semboller)} | maliyet: "
             f"{sonuc.ayarlar['maliyet_bps']:.0f} bps | eğitim ≥ "
             f"{sonuc.ayarlar['egitim_yil']} yıl, test: takvim yılı (walk-forward)")
    p.append("=" * 72)
    for t in sonuc.turlar:
        o = t.olcutler
        p.append(f"\nTUR {t.tur_no} — {t.aday_sayisi} aday "
                 f"(kümülatif deneme: {t.kum_deneme})")
        p.append(f"  Seçilen: {t.secilen.etiket}")
        p.append(f"  OOS: Sharpe {o['sharpe']:.2f} | yıllık getiri "
                 f"{o['yillik_getiri']:.1%} | maks düşüş {o['maks_dusus']:.0%} | "
                 f"DSR {o['dsr']:.2f} | bootstrap p {o['bootstrap_p']:.3f}")
        for e in t.elestiriler:
            isaret = {"engel": "✗", "uyari": "!", "bilgi": "i"}[e.siddet]
            p.append(f"  [{isaret}] {e.kural} {e.baslik}: {e.bulgu}")
        if t.eylemler:
            p.append(f"  → Post-mortem düzeltmeleri: {', '.join(t.eylemler)}")
        p.append(f"  Kabul: {'EVET' if t.kabul else 'hayır '}"
                 f"({sum(t.kabul_durumu.values())}/5 kriter)")
    p.append("\n" + "=" * 72)
    bh = sonuc.bh_olcutler
    p.append(f"Kıyas (satın-al-tut, aynı OOS dönemi): Sharpe {bh['sharpe']:.2f} | "
             f"yıllık {bh['yillik_getiri']:.1%} | maks düşüş {bh['maks_dusus']:.0%}")
    durum = "KABUL EDİLDİ" if sonuc.kabul_edildi else "KABUL EDİLMEDİ (en iyi aday raporlandı)"
    p.append(f"FİNAL ({durum}, tur {sonuc.final_tur_no}): {sonuc.final_spek.etiket}")
    p.append("Uyarı: geçmiş performans gelecek getiri garantisi değildir; bu çıktı "
             "yatırım tavsiyesi olmayan bir araştırma raporudur.")
    return "\n".join(p)
