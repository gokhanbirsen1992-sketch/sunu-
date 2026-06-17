"""Word → PDF dönüştürme çekirdeği.

İki motor desteklenir:

* ``libreoffice`` — Sistemde kurulu LibreOffice'i headless modda çalıştırır.
  En yüksek görsel doğruluk: ``.doc`` ve ``.docx``'i; tablo, resim ve
  biçimlendirmeyi olduğu gibi korur. Sistemde LibreOffice kurulu olmalıdır.
* ``python`` — Saf-Python yedeği (``python-docx`` + ``reportlab``). Hiçbir
  sistem bağımlılığı gerektirmez ama yalnızca metin, başlık ve tablo gibi
  temel içeriği aktarır (resimler atlanır). Yalnızca ``.docx`` destekler.

Varsayılan ``auto`` motoru önce LibreOffice'i dener, bulunamazsa Python
motoruna düşer.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Iterator, Optional

# Word girdisi olarak kabul edilen uzantılar.
WORD_EXTENSIONS = {".docx", ".doc"}
# Saf-Python motorunun okuyabildiği uzantılar (python-docx yalnızca .docx okur).
PYTHON_ENGINE_EXTENSIONS = {".docx"}

# LibreOffice çalıştırılabilirinin bilinen adları/yolları.
_LIBREOFFICE_CANDIDATES = (
    "soffice",
    "libreoffice",
    "soffice.bin",
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",  # macOS
    r"C:\Program Files\LibreOffice\program\soffice.exe",  # Windows
)


class ConversionError(Exception):
    """Bir dönüştürme işlemi başarısız olduğunda fırlatılır."""


def find_libreoffice() -> Optional[str]:
    """Kurulu LibreOffice çalıştırılabilirinin yolunu döndürür, yoksa ``None``."""
    for candidate in _LIBREOFFICE_CANDIDATES:
        found = shutil.which(candidate)
        if found:
            return found
        # Mutlak yol verilmişse doğrudan kontrol et.
        if "/" in candidate or "\\" in candidate:
            path = Path(candidate)
            if path.is_file():
                return str(path)
    return None


def iter_word_files(directory: Path, recursive: bool = False) -> Iterator[Path]:
    """Bir klasördeki Word dosyalarını verir.

    Geçici Office kilit dosyaları (``~$...``) atlanır.
    """
    pattern = "**/*" if recursive else "*"
    for path in sorted(directory.glob(pattern)):
        if (
            path.is_file()
            and path.suffix.lower() in WORD_EXTENSIONS
            and not path.name.startswith("~$")
        ):
            yield path


def _resolve_output_path(input_path: Path, output: Optional[Path]) -> Path:
    """Girdi yolu ve istenen çıktıdan nihai PDF yolunu hesaplar.

    * ``output`` yoksa: girdiyle aynı klasör/ad, ``.pdf`` uzantısıyla.
    * ``output`` var olan bir klasör ya da ``/`` ile bitiyorsa: o klasörün
      içinde girdi adıyla.
    * Aksi halde ``output`` doğrudan hedef dosya yolu kabul edilir.
    """
    if output is None:
        return input_path.with_suffix(".pdf")

    output = Path(output)
    treat_as_dir = output.is_dir() or str(output).endswith(("/", "\\"))
    if treat_as_dir:
        return output / (input_path.stem + ".pdf")
    if output.suffix.lower() != ".pdf":
        # Uzantısız verilmişse klasör gibi davran.
        return output / (input_path.stem + ".pdf")
    return output


def convert_file(
    input_path: str | Path,
    output_path: Optional[str | Path] = None,
    engine: str = "auto",
    overwrite: bool = False,
) -> Path:
    """Tek bir Word dosyasını PDF'e dönüştürür ve üretilen PDF yolunu döndürür.

    :param input_path: Kaynak ``.docx``/``.doc`` dosyası.
    :param output_path: Hedef PDF yolu ya da klasörü. Boşsa girdiyle aynı
        ad/klasör kullanılır.
    :param engine: ``"auto"`` | ``"libreoffice"`` | ``"python"``.
    :param overwrite: Hedef PDF zaten varsa üzerine yazılsın mı.
    :raises ConversionError: Girdi geçersizse ya da dönüştürme başarısızsa.
    """
    input_path = Path(input_path)
    if not input_path.exists():
        raise ConversionError(f"Girdi dosyası bulunamadı: {input_path}")
    if not input_path.is_file():
        raise ConversionError(f"Girdi bir dosya değil: {input_path}")
    if input_path.suffix.lower() not in WORD_EXTENSIONS:
        raise ConversionError(
            f"Desteklenmeyen uzantı '{input_path.suffix}'. "
            f"Beklenen: {', '.join(sorted(WORD_EXTENSIONS))}"
        )

    target = _resolve_output_path(input_path, Path(output_path) if output_path else None)
    if target.exists() and not overwrite:
        raise ConversionError(
            f"Hedef PDF zaten var: {target} (üzerine yazmak için overwrite kullanın)"
        )
    target.parent.mkdir(parents=True, exist_ok=True)

    if engine == "auto":
        soffice = find_libreoffice()
        if soffice:
            try:
                _convert_with_libreoffice(input_path, target, soffice)
            except ConversionError:
                # LibreOffice kurulu ama çalışmadı (ör. Writer bileşeni eksik).
                # Mümkünse saf-Python motoruna düş, değilse hatayı yükselt.
                if (
                    input_path.suffix.lower() in PYTHON_ENGINE_EXTENSIONS
                    and _python_engine_available()
                ):
                    _convert_with_python(input_path, target)
                else:
                    raise
        else:
            _convert_with_python(input_path, target)
    elif engine == "libreoffice":
        soffice = find_libreoffice()
        if not soffice:
            raise ConversionError(
                "LibreOffice bulunamadı. Kurun ya da '--engine python' kullanın."
            )
        _convert_with_libreoffice(input_path, target, soffice)
    elif engine == "python":
        _convert_with_python(input_path, target)
    else:
        raise ConversionError(f"Bilinmeyen motor: {engine}")

    return target


def _python_engine_available() -> bool:
    """Saf-Python motorunun bağımlılıkları (python-docx + reportlab) kurulu mu."""
    try:
        import docx  # noqa: F401
        import reportlab  # noqa: F401
    except ImportError:
        return False
    return True


def _convert_with_libreoffice(input_path: Path, output_path: Path, soffice: str) -> None:
    """LibreOffice'i headless modda kullanarak dönüştürür.

    LibreOffice çıktı dosyasının adını kendisi (girdi adı + ``.pdf``) belirler,
    bu yüzden geçici bir klasöre üretip istenen hedefe taşırız. Aynı anda açık
    bir LibreOffice oturumuyla çakışmamak için izole bir kullanıcı profili
    klasörü kullanılır.
    """
    with tempfile.TemporaryDirectory(prefix="word2pdf_") as tmp:
        tmp_dir = Path(tmp)
        out_dir = tmp_dir / "out"
        out_dir.mkdir()
        profile_dir = tmp_dir / "profile"
        profile_uri = profile_dir.as_uri()

        cmd = [
            soffice,
            "--headless",
            "--norestore",
            "--invisible",
            "--nodefault",
            "--nologo",
            f"-env:UserInstallation={profile_uri}",
            "--convert-to",
            "pdf",
            "--outdir",
            str(out_dir),
            str(input_path),
        ]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
            )
        except FileNotFoundError as exc:
            raise ConversionError(f"LibreOffice çalıştırılamadı: {soffice}") from exc
        except subprocess.TimeoutExpired as exc:
            raise ConversionError("LibreOffice dönüştürme zaman aşımına uğradı (300 sn).") from exc

        if result.returncode != 0:
            detail = (result.stderr or result.stdout or "").strip()
            raise ConversionError(f"LibreOffice hata verdi: {detail or 'bilinmeyen hata'}")

        produced = out_dir / (input_path.stem + ".pdf")
        if not produced.exists():
            # Bazı sürümler farklı adlandırabilir; klasördeki tek PDF'i al.
            pdfs = list(out_dir.glob("*.pdf"))
            if not pdfs:
                detail = (result.stdout or result.stderr or "").strip()
                raise ConversionError(
                    f"LibreOffice PDF üretmedi. Çıktı: {detail or 'yok'}"
                )
            produced = pdfs[0]

        # shutil.move farklı dosya sistemleri arasında da çalışır.
        if output_path.exists():
            output_path.unlink()
        shutil.move(str(produced), str(output_path))


def _convert_with_python(input_path: Path, output_path: Path) -> None:
    """python-docx + reportlab ile saf-Python dönüştürme (yedek motor).

    Metin, başlıklar, kalın/italik biçimlendirme ve tablolar aktarılır.
    Resimler ve gelişmiş düzen öğeleri bu motorda atlanır.
    """
    if input_path.suffix.lower() not in PYTHON_ENGINE_EXTENSIONS:
        raise ConversionError(
            f"Python motoru yalnızca .docx destekler; '{input_path.suffix}' için "
            "LibreOffice motorunu kullanın."
        )
    try:
        import docx  # type: ignore
        from docx.document import Document as _DocxDocument  # type: ignore
        from docx.oxml.ns import qn  # type: ignore
        from docx.oxml.table import CT_Tbl  # type: ignore
        from docx.oxml.text.paragraph import CT_P  # type: ignore
        from docx.table import Table as _DocxTable  # type: ignore
        from docx.text.paragraph import Paragraph as _DocxParagraph  # type: ignore
        from reportlab.lib import colors  # type: ignore
        from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT  # type: ignore
        from reportlab.lib.pagesizes import A4  # type: ignore
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet  # type: ignore
        from reportlab.lib.units import cm  # type: ignore
        from reportlab.platypus import (  # type: ignore
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )
    except ImportError as exc:  # pragma: no cover - ortam bağımlı
        raise ConversionError(
            "Python motoru için 'python-docx' ve 'reportlab' gerekli. "
            "Kurmak için: pip install -r word2pdf/requirements.txt"
        ) from exc

    from xml.sax.saxutils import escape

    font_normal, font_bold = _register_unicode_font()

    document = docx.Document(str(input_path))

    # --- Stiller ---
    base = getSampleStyleSheet()
    body_style = ParagraphStyle(
        "Body",
        parent=base["Normal"],
        fontName=font_normal,
        fontSize=11,
        leading=15,
    )
    heading_sizes = {1: 17, 2: 15, 3: 13, 4: 12}

    def heading_style(level: int) -> "ParagraphStyle":
        return ParagraphStyle(
            f"Heading{level}",
            parent=body_style,
            fontName=font_bold,
            fontSize=heading_sizes.get(level, 12),
            leading=heading_sizes.get(level, 12) + 4,
            spaceBefore=10,
            spaceAfter=6,
        )

    align_map = {0: TA_LEFT, 1: TA_CENTER, 2: TA_RIGHT, 3: TA_JUSTIFY}

    def runs_to_markup(paragraph) -> str:
        """Bir paragrafın run'larını reportlab mini-markup metnine çevirir."""
        parts: list[str] = []
        for run in paragraph.runs:
            text = run.text
            if not text:
                continue
            text = escape(text).replace("\t", "    ").replace("\n", "<br/>")
            if run.bold:
                text = f"<b>{text}</b>"
            if run.italic:
                text = f"<i>{text}</i>"
            if run.underline:
                text = f"<u>{text}</u>"
            parts.append(text)
        return "".join(parts)

    def iter_block_items(parent):
        """Belge gövdesindeki paragraf ve tabloları sırayla verir."""
        if isinstance(parent, _DocxDocument):
            parent_elm = parent.element.body
        else:  # tablo hücresi
            parent_elm = parent._tc
        for child in parent_elm.iterchildren():
            if isinstance(child, CT_P):
                yield _DocxParagraph(child, parent)
            elif isinstance(child, CT_Tbl):
                yield _DocxTable(child, parent)

    available_width = A4[0] - 4 * cm  # 2cm sol + 2cm sağ kenar boşluğu

    flowables = []
    for block in iter_block_items(document):
        if isinstance(block, _DocxParagraph):
            style_name = (block.style.name or "").lower() if block.style else ""
            markup = runs_to_markup(block)
            if not markup.strip():
                flowables.append(Spacer(1, 8))
                continue
            if style_name.startswith("title"):
                style = heading_style(1)
            elif style_name.startswith("heading"):
                level = _heading_level(style_name)
                style = heading_style(level)
            else:
                style = ParagraphStyle(
                    "BodyAligned",
                    parent=body_style,
                    alignment=align_map.get(
                        int(block.alignment) if block.alignment is not None else 0,
                        TA_LEFT,
                    ),
                )
            flowables.append(Paragraph(markup, style))
            flowables.append(Spacer(1, 4))
        elif isinstance(block, _DocxTable):
            data = []
            for row in block.rows:
                cells = []
                for cell in row.cells:
                    cell_markup = "<br/>".join(
                        runs_to_markup(p) or "&nbsp;" for p in cell.paragraphs
                    )
                    cells.append(Paragraph(cell_markup or "&nbsp;", body_style))
                data.append(cells)
            if not data:
                continue
            ncols = max(len(r) for r in data)
            # Satırları eşit sütun sayısına tamamla.
            for r in data:
                while len(r) < ncols:
                    r.append(Paragraph("&nbsp;", body_style))
            col_width = available_width / ncols
            table = Table(data, colWidths=[col_width] * ncols)
            table.setStyle(
                TableStyle(
                    [
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 4),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                        ("TOPPADDING", (0, 0), (-1, -1), 3),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
                    ]
                )
            )
            flowables.append(table)
            flowables.append(Spacer(1, 8))

    if not flowables:
        flowables.append(Paragraph("(Boş belge)", body_style))

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=input_path.stem,
    )
    try:
        doc.build(flowables)
    except Exception as exc:  # noqa: BLE001 - reportlab çeşitli hatalar fırlatabilir
        raise ConversionError(f"PDF oluşturulamadı: {exc}") from exc


def _heading_level(style_name: str) -> int:
    """'heading 2' gibi bir stil adından başlık seviyesini çıkarır."""
    digits = "".join(ch for ch in style_name if ch.isdigit())
    try:
        return int(digits) if digits else 1
    except ValueError:
        return 1


def _register_unicode_font() -> tuple[str, str]:
    """Unicode (Türkçe) destekli bir TTF font kaydeder.

    DejaVuSans bulunursa kaydedilip kullanılır (ç, ğ, ı, ö, ş, ü tam destekli).
    Bulunamazsa reportlab'ın yerleşik Helvetica'sına düşülür — bu durumda bazı
    Türkçe karakterler düzgün görünmeyebilir.

    :return: ``(normal_font_adı, kalın_font_adı)``
    """
    from reportlab.pdfbase import pdfmetrics  # type: ignore
    from reportlab.pdfbase.ttfonts import TTFont  # type: ignore

    regular_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        r"C:\Windows\Fonts\arial.ttf",
    ]
    bold_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
        r"C:\Windows\Fonts\arialbd.ttf",
    ]

    regular = next((p for p in regular_candidates if Path(p).is_file()), None)
    if not regular:
        # Unicode font yok: yerleşik fontlara düş.
        return "Helvetica", "Helvetica-Bold"

    bold = next((p for p in bold_candidates if Path(p).is_file()), regular)

    try:
        if "W2P-Normal" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont("W2P-Normal", regular))
        if "W2P-Bold" not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont("W2P-Bold", bold))
    except Exception:  # noqa: BLE001 - font kaydı başarısızsa güvenli geri dönüş
        return "Helvetica", "Helvetica-Bold"

    return "W2P-Normal", "W2P-Bold"
