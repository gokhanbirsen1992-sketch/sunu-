"""Resimleri (JPG/PNG/...) tek bir PDF dosyasında birleştiren araç.

Pillow kütüphanesini kullanır. Her resim PDF'te ayrı bir sayfa olur.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image

# Pillow'un PDF olarak kaydedebildiği yaygın resim uzantıları.
DESTEKLENEN_UZANTILAR = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".gif",
    ".tif",
    ".tiff",
    ".webp",
}


def resimleri_topla(girdiler: list[str]) -> list[Path]:
    """Verilen dosya ve klasör yollarından desteklenen resimleri toplar.

    - Bir yol klasörse: içindeki resimler isme göre sıralı eklenir.
    - Bir yol dosyaysa: doğrudan eklenir.

    Resimler verildikleri sıraya göre PDF'e dizilir; klasör içindekiler
    alfabetik sıralanır (ör. foto1.jpg, foto2.jpg, foto10.jpg değil — bkz README).
    """
    yollar: list[Path] = []
    for girdi in girdiler:
        p = Path(girdi).expanduser()
        if not p.exists():
            raise FileNotFoundError(f"Yol bulunamadı: {p}")
        if p.is_dir():
            klasordekiler = sorted(
                cocuk
                for cocuk in p.iterdir()
                if cocuk.is_file() and cocuk.suffix.lower() in DESTEKLENEN_UZANTILAR
            )
            if not klasordekiler:
                raise ValueError(f"Klasörde desteklenen resim yok: {p}")
            yollar.extend(klasordekiler)
        elif p.suffix.lower() in DESTEKLENEN_UZANTILAR:
            yollar.append(p)
        else:
            raise ValueError(f"Desteklenmeyen dosya türü: {p.name}")

    if not yollar:
        raise ValueError("Dönüştürülecek hiçbir resim bulunamadı.")
    return yollar


def _rgb_ye_cevir(resim: Image.Image) -> Image.Image:
    """PDF için resmi RGB'ye çevirir (şeffaflığı beyaz zemine basar)."""
    if resim.mode in ("RGBA", "LA", "P"):
        resim = resim.convert("RGBA")
        zemin = Image.new("RGB", resim.size, (255, 255, 255))
        zemin.paste(resim, mask=resim.split()[-1])
        return zemin
    if resim.mode != "RGB":
        return resim.convert("RGB")
    return resim


def pdfe_cevir(girdiler: list[str], cikti: str, kalite: int = 90) -> Path:
    """Resimleri tek bir PDF'te birleştirir ve çıktı yolunu döndürür."""
    resim_yollari = resimleri_topla(girdiler)

    sayfalar: list[Image.Image] = []
    for yol in resim_yollari:
        with Image.open(yol) as ham:
            ham.load()  # veriyi dosya kapanmadan belleğe al
            sayfalar.append(_rgb_ye_cevir(ham))

    cikti_yolu = Path(cikti).expanduser()
    if cikti_yolu.suffix.lower() != ".pdf":
        cikti_yolu = cikti_yolu.with_suffix(".pdf")
    cikti_yolu.parent.mkdir(parents=True, exist_ok=True)

    ilk, *digerleri = sayfalar
    ilk.save(
        cikti_yolu,
        "PDF",
        save_all=True,
        append_images=digerleri,
        quality=kalite,
    )
    return cikti_yolu
