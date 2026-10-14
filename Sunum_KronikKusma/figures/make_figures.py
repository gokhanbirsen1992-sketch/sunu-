#!/usr/bin/env python3
"""Sunum şekilleri (şematik). Palet dataviz validator ile doğrulandı: teal 00938A, mercan D9573B.
Çıktı: figures/fig_patern.png, figures/fig_cvs_kriter.png (300 dpi).
Kaynak numaraları references/ref_order.json'dan okunur (elle numara yok)."""
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "figures"
TEAL, CORAL, INK, MUTED, GRID = "#00938A", "#D9573B", "#1D2B33", "#5B6B73", "#D5DEDC"
REF = {r["pmid"]: r["n"] for r in json.loads((ROOT / "references" / "ref_order.json").read_text())}

for f in font_manager.findSystemFonts():
    if "Carlito" in f:
        font_manager.fontManager.addfont(f)
plt.rcParams.update({
    "font.family": "Carlito", "font.size": 13, "axes.edgecolor": GRID, "axes.labelcolor": MUTED,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False, "axes.spines.right": False,
})


def fig_patern():
    fig, axes = plt.subplots(2, 1, figsize=(6.2, 4.6), sharex=True, gridspec_kw={"hspace": 0.45})
    days = range(1, 91)
    # Kronik: neredeyse her gün düşük yoğunluk (şematik)
    chronic = [1.2 + 0.6 * ((d * 7) % 5) / 4 if d % 6 else 0 for d in days]
    # Siklik: aralıklı, yüksek yoğunluklu ataklar; arada sıfır (şematik)
    cyclic = [0.0] * 90
    for start, peak in ((8, 12), (37, 11), (66, 13)):
        for i, v in enumerate((peak * 0.55, peak, peak * 0.6)):
            cyclic[start + i] = v
    for ax, ys, col, name in ((axes[0], chronic, TEAL, "Kronik patern"), (axes[1], cyclic, CORAL, "Siklik patern")):
        ax.bar(list(days), ys, width=0.75, color=col, linewidth=0)
        ax.axhline(4, color=INK, linestyle=(0, (4, 3)), linewidth=1.2)
        ax.set_ylim(0, 14.5)
        ax.set_yticks([0, 4, 8, 12])
        ax.grid(axis="y", color=GRID, linewidth=0.6)
        ax.set_axisbelow(True)
        ax.set_title(name, loc="left", color=INK, fontsize=15, fontweight="bold")
        ax.text(90.5, 4.4, "≥4 kusma/saat", ha="right", va="bottom", color=INK, fontsize=12,
                bbox=dict(facecolor="white", edgecolor="none", pad=1.5))
    axes[0].text(46, 9.6, "neredeyse her gün, düşük yoğunluk", ha="center", color=MUTED, fontsize=12,
                 bbox=dict(facecolor="white", edgecolor="none", pad=1.5))
    axes[1].annotate("", xy=(36.5, 8.6), xytext=(11.5, 8.6), arrowprops=dict(arrowstyle="<->", color=MUTED, lw=1.1))
    axes[1].text(24, 9.6, "ataklar arası iyilik", ha="center", color=MUTED, fontsize=12,
                 bbox=dict(facecolor="white", edgecolor="none", pad=1.5))
    axes[1].set_xlabel("Gün")
    fig.text(0.02, 0.5, "Pik yoğunluk (kusma/saat)", rotation=90, va="center", color=MUTED, fontsize=13)
    fig.text(0.99, 0.005, f"Şematik çizim, hasta verisi değil · eşikler [{REF['8604272']}]",
             ha="right", va="bottom", color=MUTED, fontsize=10.5, style="italic")
    fig.subplots_adjust(left=0.11, right=0.98, top=0.93, bottom=0.14)
    fig.savefig(OUT / "fig_patern.png", dpi=300)
    plt.close(fig)


def fig_cvs_kriter():
    fig, ax = plt.subplots(figsize=(6.2, 2.7))
    ax.set_xlim(0, 365)
    ax.set_ylim(0, 3)
    ax.axhline(0.6, color=TEAL, linewidth=3, solid_capstyle="round")
    episodes = [(30, 3), (110, 2), (190, 4), (290, 1.5)]
    for x, w in episodes:
        ax.add_patch(plt.Rectangle((x, 0.6), w * 4, 1.6, color=CORAL, linewidth=0))
    ax.text(32, 2.45, "≥4 ayrı atak / 12 ay", color=INK, fontsize=13, fontweight="bold")
    ax.text(192, 2.45, "her atak 2 saat–7 gün", color=INK, fontsize=13, fontweight="bold")
    ax.annotate("", xy=(108, 1.2), xytext=(44, 1.2), arrowprops=dict(arrowstyle="<->", color=MUTED, lw=1.1))
    ax.text(76, 1.35, "≥1 hafta ara", ha="center", color=MUTED, fontsize=12)
    ax.text(150, 0.15, "ataklar arası bazal sağlığa dönüş", ha="center", color=TEAL, fontsize=12)
    ax.set_xticks([0, 91, 182, 273, 365], ["0", "3", "6", "9", "12"])
    ax.set_xlabel("ay", labelpad=2)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    fig.text(0.99, 0.01, f"Şematik · Rome V [{REF['41713704']}]", ha="right", va="bottom",
             color=MUTED, fontsize=10.5, style="italic")
    fig.subplots_adjust(left=0.03, right=0.97, top=0.95, bottom=0.27)
    fig.savefig(OUT / "fig_cvs_kriter.png", dpi=300)
    plt.close(fig)


if __name__ == "__main__":
    fig_patern()
    fig_cvs_kriter()
    print("şekiller yazıldı")
