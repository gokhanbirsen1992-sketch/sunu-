"""PWA ikonlarını üretir (matplotlib ile; ek bağımlılık yok).

Mavi yuvarlatılmış kare üzerine beyaz bar-grafik motifi. 180/192/512 px.
Çalıştırma: .venv/bin/python webapp/make_icons.py
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

OUT = Path(__file__).parent / "static"
BLUE = "#0b5cad"


def make(size: int) -> None:
    fig = plt.figure(figsize=(size / 100, size / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.add_patch(FancyBboxPatch((0.04, 0.04), 0.92, 0.92, boxstyle="round,pad=0,rounding_size=0.18",
                                facecolor=BLUE, edgecolor="none"))
    for x, h in [(0.26, 0.32), (0.44, 0.50), (0.62, 0.40)]:
        ax.add_patch(Rectangle((x, 0.24), 0.12, h, facecolor="white", edgecolor="none"))
    ax.plot([0.20, 0.80], [0.20, 0.20], color="white", lw=size * 0.02, solid_capstyle="round")
    fig.savefig(OUT / f"icon-{size}.png", dpi=100, transparent=False)
    plt.close(fig)


if __name__ == "__main__":
    for s in (180, 192, 512):
        make(s)
    print("ikonlar üretildi:", [str(p.name) for p in OUT.glob("icon-*.png")])
