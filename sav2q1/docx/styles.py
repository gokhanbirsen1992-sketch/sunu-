"""Word stil yardımcıları (Türkçe akademik biçim, tr-TR)."""

from __future__ import annotations

from docx.shared import Pt


def apply_base_styles(doc, font: str = "Times New Roman", size: int = 12,
                      line_spacing: float = 1.5) -> None:
    """Normal stile temel akademik biçimi uygula."""
    st = doc.styles["Normal"]
    st.font.name = font
    st.font.size = Pt(size)
    st.paragraph_format.line_spacing = line_spacing
    st.paragraph_format.space_after = Pt(6)
