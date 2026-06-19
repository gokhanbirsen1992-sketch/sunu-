"""Türkçe akademik sayı biçimlendirme.

Yerel biçim (ondalık VİRGÜL) ve yuvarlama kararları YALNIZCA burada verilir;
yazar-agentlar asla sayı biçimlemez, defterdeki hazır string'i kopyalar. Bu,
`verify-numeric`'in BİREBİR (exact) eşleşme yapabilmesi için kritiktir.

APA benzeri kurallar (Türkçe uyarlama):
  * Genel değerler 2 ondalık.
  * p değerleri 3 ondalık; çok küçükse "< 0,001".
  * Ondalık ayırıcı virgül; binlik ayırıcı kullanılmaz (belirsizlik olmasın).
  * Leading zero KORUNUR (0,18) — Türkçe dergilerde yaygın ve okunaklı.
"""

from __future__ import annotations


def fmt_num(x: float, decimals: int = 2) -> str:
    """Sayıyı `decimals` ondalıkla, virgüllü biçimde döndürür."""
    if x is None:
        return ""
    s = f"{float(x):.{decimals}f}"
    # -0,00 gibi negatif sıfırları normalize et
    if s.replace("-", "").replace("0", "").replace(",", "").replace(".", "") == "":
        s = s.lstrip("-")
    return s.replace(".", ",")


def fmt_int(x: float) -> str:
    """Tam sayı biçimi (binlik ayırıcısız)."""
    return str(int(round(float(x))))


def fmt_p(p: float) -> str:
    """p değeri biçimi. '< 0,001' veya 'p = 0,0xx' gövdesi için '0,0xx'."""
    if p is None:
        return ""
    if p < 0.001:
        return "< 0,001"
    return f"{float(p):.3f}".replace(".", ",")


def fmt_pct(x: float, decimals: int = 1) -> str:
    """Yüzde biçimi (yalnız sayı kısmı; % işareti metinde eklenir)."""
    return fmt_num(x, decimals)


def fmt_ci(low: float, high: float, decimals: int = 2) -> str:
    """Güven aralığı biçimi: 'a - b' (virgüllü ondalık, tireyle ayrılmış)."""
    return f"{fmt_num(low, decimals)} – {fmt_num(high, decimals)}"
