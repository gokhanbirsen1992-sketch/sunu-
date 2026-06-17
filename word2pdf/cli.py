"""word2pdf komut satırı arayüzü."""

from __future__ import annotations

from pathlib import Path

import click

from .converter import (
    ConversionError,
    convert_file,
    find_libreoffice,
    iter_word_files,
)


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument("input_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "-o",
    "--output",
    type=click.Path(path_type=Path),
    default=None,
    help="Çıktı PDF yolu (tek dosya) veya çıktı klasörü (toplu dönüştürme).",
)
@click.option(
    "-e",
    "--engine",
    type=click.Choice(["auto", "libreoffice", "python"]),
    default="auto",
    show_default=True,
    help="Dönüştürme motoru. auto: önce LibreOffice, yoksa python.",
)
@click.option(
    "-r",
    "--recursive",
    is_flag=True,
    help="Klasör verildiğinde alt klasörleri de tara.",
)
@click.option(
    "-f",
    "--overwrite",
    is_flag=True,
    help="Var olan PDF dosyalarının üzerine yaz.",
)
def main(
    input_path: Path,
    output: Path | None,
    engine: str,
    recursive: bool,
    overwrite: bool,
) -> None:
    """Word (.docx/.doc) dosyalarını PDF'e dönüştürür.

    INPUT_PATH bir dosya veya klasör olabilir. Klasör verilirse içindeki tüm
    Word dosyaları dönüştürülür.

    \b
    Örnekler:
      python -m word2pdf rapor.docx
      python -m word2pdf rapor.docx -o ciktilar/rapor.pdf
      python -m word2pdf belgeler/ -o pdfler/ -r
      python -m word2pdf rapor.docx --engine python
    """
    if engine in ("auto", "libreoffice"):
        soffice = find_libreoffice()
        if engine == "libreoffice" and not soffice:
            raise click.ClickException(
                "LibreOffice bulunamadı. Kurun ya da '--engine python' kullanın."
            )

    # Dönüştürülecek dosyaların listesini hazırla.
    if input_path.is_dir():
        files = list(iter_word_files(input_path, recursive=recursive))
        if not files:
            raise click.ClickException(
                f"'{input_path}' içinde Word dosyası bulunamadı."
            )
        if output is not None and (output.is_dir() or not output.suffix):
            output.mkdir(parents=True, exist_ok=True)
    else:
        files = [input_path]

    is_batch = len(files) > 1 or input_path.is_dir()
    succeeded = 0
    failed = 0

    for src in files:
        # Toplu modda çıktı bir klasördür; tek dosyada doğrudan hedef olabilir.
        target = output
        if is_batch and output is not None:
            target = output / (src.stem + ".pdf")
        try:
            result = convert_file(
                src, target, engine=engine, overwrite=overwrite
            )
        except ConversionError as exc:
            failed += 1
            click.secho(f"  ✗ {src.name}: {exc}", fg="red", err=True)
            continue
        succeeded += 1
        click.secho(f"  ✓ {src.name} → {result}", fg="green")

    if is_batch:
        click.echo()
        summary = f"Tamamlandı: {succeeded} başarılı"
        if failed:
            summary += f", {failed} başarısız"
        click.secho(summary, fg="cyan", bold=True)

    if failed and not succeeded:
        raise SystemExit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
