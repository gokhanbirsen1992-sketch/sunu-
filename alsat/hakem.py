"""Reviewer 2 motoru — deterministik, düşmanca hakem denetimi (LLM'siz).

Yedi denetim (H1–H7), backtest literatürünün bilinen tuzaklarını hedefler
(bkz. LITERATUR.md §4). Her eleştiri, döngü motorunun uygulayabileceği
makine-eylemli bir düzeltme önerisi taşır.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from alsat import olcutler

# Eşikler — savunulabilir, sabit (tur içinde değişmez)
GECIKME_SISME_ORANI = 1.30   # H1: gecikmesiz Sharpe / gecikmeli Sharpe bu oranı aşarsa şüphe
KOMSU_COKUS_ORANI = 0.50     # H2: komşu medyan Sharpe, seçilenin bu oranının altındaysa aşırı uyum
DSR_ENGEL = 0.50             # H5: şanstan ayırt edilemez
DSR_HEDEF = 0.95             # H5/K2: güçlü kanıt eşiği (Bailey-LdP 2014)
OOS_BOZULMA_ORANI = 0.30     # H6: OOS Sharpe < IS Sharpe'ın bu oranı → ret
DUSUS_IYILESME_ORANI = 0.80  # H7/K4: |strateji düşüşü| < 0.8×|satın-al-tut düşüşü| hedefi


@dataclass
class Elestiri:
    kural: str            # "H1".."H7"
    baslik: str
    siddet: str           # "engel" | "uyari" | "bilgi"
    bulgu: str
    oneri: dict | None = None  # ör. {"eylem": "vol_filtre"}


@dataclass
class HakemGirdisi:
    """Döngü motorunun hakeme sunduğu kanıt dosyası (tek tur, birleşik OOS)."""

    oos_net: pd.Series                 # birleşik (semboller ortalaması) OOS net getiri
    oos_ozsermaye: pd.Series
    bh_net: pd.Series                  # satın-al-tut kıyası (birleşik)
    bh_ozsermaye: pd.Series
    is_sharpe: float                   # seçilen spekin eğitim pencerelerindeki ort. Sharpe
    n_deneme_kum: int                  # kümülatif denenen aday sayısı (turlar arası birikir)
    sembol_oos: dict[str, pd.Series]   # sembol → OOS net getiri
    gecikmesiz_sharpe: float           # H1: sinyal aynı gün uygulansaydı OOS Sharpe
    komsu_sharpelar: list[float]       # H2: komşu parametrelerin OOS Sharpe'ları
    stres_2x_getiri: float             # H3: 2× maliyette OOS toplam getiri
    stres_4x_getiri: float             # H3: 4× maliyette OOS toplam getiri
    deneme_sharpe_std: float | None = None  # H5: denemeler arası günlük Sharpe std (ampirik)
    ekler: dict = field(default_factory=dict)


def incele(g: HakemGirdisi) -> list[Elestiri]:
    """H1–H7 denetimlerini çalıştırır, eleştiri listesi döndürür."""
    e: list[Elestiri] = []
    oos_sharpe = olcutler.sharpe(g.oos_net)

    # H1 — ileri-bakış / uygulama gecikmesi duyarlılığı
    if oos_sharpe > 0 and g.gecikmesiz_sharpe > oos_sharpe * GECIKME_SISME_ORANI:
        e.append(Elestiri(
            "H1", "Uygulama gecikmesi duyarlılığı", "uyari",
            f"Sinyal aynı gün uygulansaydı Sharpe {g.gecikmesiz_sharpe:.2f} olurdu "
            f"(gecikmeli: {oos_sharpe:.2f}). Kural, kapanışa çok yakın bilgiye dayanıyor; "
            "gerçek işlemde kayma bu farkı yer.",
            {"eylem": "devir_azalt"},
        ))

    # H2 — parametre hassasiyeti (aşırı uyum)
    if g.komsu_sharpelar:
        komsu_medyan = float(pd.Series(g.komsu_sharpelar).median())
        if oos_sharpe > 0 and komsu_medyan < oos_sharpe * KOMSU_COKUS_ORANI:
            e.append(Elestiri(
                "H2", "Parametre hassasiyeti", "engel",
                f"Seçilen parametrede OOS Sharpe {oos_sharpe:.2f}, komşu parametrelerin "
                f"medyanı {komsu_medyan:.2f}. Performans dar bir parametre tepeciğine "
                "bağlı — klasik aşırı uyum işareti (Bailey ve ark. 2014).",
                {"eylem": "sadelestir"},
            ))

    # H3 — işlem maliyeti stresi
    if g.stres_2x_getiri <= 0:
        e.append(Elestiri(
            "H3", "Maliyet stresi (2×)", "engel",
            f"Maliyet varsayımı ikiye katlanınca OOS toplam getiri {g.stres_2x_getiri:.1%}. "
            "Kârlılık maliyet varsayımına bağımlı (Park-Irwin 2007; Han ve ark. 2023).",
            {"eylem": "devir_azalt"},
        ))
    elif g.stres_4x_getiri <= 0:
        e.append(Elestiri(
            "H3", "Maliyet stresi (4×)", "uyari",
            f"Maliyet 4× iken OOS getiri {g.stres_4x_getiri:.1%} — güvenlik payı sınırlı.",
            {"eylem": "devir_azalt"},
        ))

    # H4 — rejim sağlamlığı (semboller arası + dönem içi tutarlılık)
    zayif_semboller = [s for s, net in g.sembol_oos.items() if olcutler.sharpe(net) <= 0]
    if zayif_semboller:
        e.append(Elestiri(
            "H4", "Rejim/varlık sağlamlığı", "engel",
            f"OOS Sharpe şu sembollerde ≤ 0: {', '.join(zayif_semboller)}. "
            "Kural varlıklar arasında genellemiyor (Hudson-Urquhart 2021 ihtiyatı).",
            {"eylem": "vol_filtre"},
        ))
    else:
        yari = len(g.oos_net) // 2
        s1 = olcutler.sharpe(g.oos_net.iloc[:yari])
        s2 = olcutler.sharpe(g.oos_net.iloc[yari:])
        if min(s1, s2) < 0 and max(s1, s2) > 1.0:
            e.append(Elestiri(
                "H4", "Dönemsel tutarsızlık", "uyari",
                f"OOS'un iki yarısında Sharpe {s1:.2f} / {s2:.2f} — performans tek "
                "döneme yığılmış olabilir.",
                {"eylem": "vol_filtre"},
            ))

    # H5 — çoklu test / veri madenciliği düzeltmesi
    dsr = olcutler.deflated_sharpe(g.oos_net, g.n_deneme_kum, g.deneme_sharpe_std)
    if dsr < DSR_ENGEL:
        e.append(Elestiri(
            "H5", "Veri madenciliği (DSR)", "engel",
            f"{g.n_deneme_kum} kümülatif deneme sonrası DSR {dsr:.2f} < {DSR_ENGEL} — "
            "sonuç şanstan ayırt edilemiyor (White 2000; Bailey-LdP 2014).",
            {"eylem": "aday_azalt"},
        ))
    elif dsr < DSR_HEDEF:
        e.append(Elestiri(
            "H5", "Veri madenciliği (DSR)", "uyari",
            f"DSR {dsr:.2f} — kayda değer ama {DSR_HEDEF} güçlü-kanıt eşiğinin altında.",
            {"eylem": "aday_azalt"},
        ))

    # H6 — IS→OOS bozulması
    if g.is_sharpe > 0 and oos_sharpe < g.is_sharpe * OOS_BOZULMA_ORANI:
        e.append(Elestiri(
            "H6", "Örneklem-dışı bozulma", "engel",
            f"IS Sharpe {g.is_sharpe:.2f} → OOS Sharpe {oos_sharpe:.2f} "
            f"(oran {oos_sharpe / g.is_sharpe:.0%} < {OOS_BOZULMA_ORANI:.0%}). "
            "Eğitimdeki başarı örneklem dışına taşınmıyor.",
            {"eylem": "topluluk"},
        ))

    # H7 — satın-al-tut kıyası (riske göre)
    bh_sharpe = olcutler.sharpe(g.bh_net)
    dd_s = abs(olcutler.maks_dusus(g.oos_ozsermaye))
    dd_bh = abs(olcutler.maks_dusus(g.bh_ozsermaye))
    dusus_iyilesti = dd_s < dd_bh * DUSUS_IYILESME_ORANI
    if oos_sharpe <= bh_sharpe and not dusus_iyilesti:
        e.append(Elestiri(
            "H7", "Satın-al-tut'a üstünlük yok", "engel",
            f"OOS Sharpe {oos_sharpe:.2f} ≤ satın-al-tut {bh_sharpe:.2f} ve maks düşüş "
            f"({dd_s:.0%}) satın-al-tut'unkinden ({dd_bh:.0%}) anlamlı iyi değil. "
            "Bu kuralı kullanmanın gerekçesi yok.",
            {"eylem": "vol_filtre"},
        ))
    elif dusus_iyilesti and oos_sharpe > 0:
        e.append(Elestiri(
            "H7", "Düşüş koruması", "bilgi",
            f"Maks düşüş {dd_s:.0%} — satın-al-tut'un {dd_bh:.0%} düşüşüne karşı belirgin "
            "koruma (Hudson-Urquhart 2021 ile uyumlu).",
        ))

    return e


def engel_var(elestiriler: list[Elestiri]) -> bool:
    return any(x.siddet == "engel" for x in elestiriler)
