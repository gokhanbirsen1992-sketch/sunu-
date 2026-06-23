"""img2pdf dönüştürücü için testler."""

import pytest
from PIL import Image

from img2pdf.converter import pdfe_cevir, resimleri_topla


def _resim_olustur(yol, boyut=(60, 40), renk=(120, 60, 200), mod="RGB"):
    Image.new(mod, boyut, renk).save(yol)
    return yol


def test_tek_resim_pdf_olusturur(tmp_path):
    foto = _resim_olustur(tmp_path / "a.jpg")
    cikti = pdfe_cevir([str(foto)], str(tmp_path / "out.pdf"))
    assert cikti.exists()
    assert cikti.suffix == ".pdf"
    assert cikti.stat().st_size > 0


def test_birden_fazla_resim_birlesir(tmp_path):
    a = _resim_olustur(tmp_path / "a.jpg")
    b = _resim_olustur(tmp_path / "b.png", renk=(10, 200, 90))
    cikti = pdfe_cevir([str(a), str(b)], str(tmp_path / "out.pdf"))
    assert cikti.exists()


def test_klasor_girdisi(tmp_path):
    klasor = tmp_path / "fotolar"
    klasor.mkdir()
    _resim_olustur(klasor / "1.jpg")
    _resim_olustur(klasor / "2.jpg")
    cikti = pdfe_cevir([str(klasor)], str(tmp_path / "album.pdf"))
    assert cikti.exists()


def test_klasor_alfabetik_sirali(tmp_path):
    klasor = tmp_path / "k"
    klasor.mkdir()
    _resim_olustur(klasor / "b.jpg")
    _resim_olustur(klasor / "a.jpg")
    yollar = resimleri_topla([str(klasor)])
    assert [p.name for p in yollar] == ["a.jpg", "b.jpg"]


def test_seffaf_png(tmp_path):
    foto = _resim_olustur(
        tmp_path / "s.png", renk=(255, 0, 0, 128), mod="RGBA"
    )
    cikti = pdfe_cevir([str(foto)], str(tmp_path / "out.pdf"))
    assert cikti.exists()


def test_pdf_uzantisi_otomatik_eklenir(tmp_path):
    foto = _resim_olustur(tmp_path / "a.jpg")
    cikti = pdfe_cevir([str(foto)], str(tmp_path / "uzantisiz"))
    assert cikti.suffix == ".pdf"


def test_olmayan_yol_hata(tmp_path):
    with pytest.raises(FileNotFoundError):
        pdfe_cevir([str(tmp_path / "yok.jpg")], str(tmp_path / "out.pdf"))


def test_desteklenmeyen_tur_hata(tmp_path):
    metin = tmp_path / "not.txt"
    metin.write_text("merhaba")
    with pytest.raises(ValueError):
        pdfe_cevir([str(metin)], str(tmp_path / "out.pdf"))
