"""Komut satırı arayüzü: python analyze.py veri.xlsx"""
from __future__ import annotations

import argparse
import sys

from standalone_stats.report import analyze


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="analyze.py",
        description=(
            "Excel/CSV/SPSS veri dosyanız için tam istatistik testi + keşifsel örüntü "
            "(gizli grup, sıra dışı vaka, gizli ilişki, risk skoru) raporu üretir. "
            "PaperForge web uygulamasından bağımsız çalışır; makale yazmaz, literatür taramaz."
        ),
    )
    parser.add_argument("input", help="Veri dosyası (.xlsx, .xls, .csv, .sav)")
    parser.add_argument("--out", help="Çıktı .docx dosya yolu (varsayılan: <girdi>_rapor.docx)")
    parser.add_argument(
        "--dv", metavar="SUTUN",
        help="İkili (binary) sonuç değişkeni (ör. hasta/sağlıklı) — işaretlenirse risk skoru hesaplanır",
    )
    parser.add_argument("--lang", choices=["tr", "en"], default="tr", help="Rapor dili (varsayılan: tr)")
    parser.add_argument("--alpha", type=float, default=0.05, help="Anlamlılık düzeyi (varsayılan: 0.05)")
    parser.add_argument(
        "--p-adjust", choices=["none", "holm", "fdr_bh"], default="holm",
        help="Çoklu test p-değeri düzeltme yöntemi (varsayılan: holm)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        result = analyze(
            args.input, out_path=args.out, dv=args.dv, lang=args.lang,
            alpha=args.alpha, p_adjust=args.p_adjust,
        )
    except (ValueError, FileNotFoundError) as exc:
        print(f"Hata: {exc}", file=sys.stderr)
        return 1

    n_sig = sum(1 for f in result.findings if f.significant)
    print(f"{result.n_rows_before} satır yüklendi → temizlik sonrası {result.n_rows_after} satır.")
    print(f"{len(result.findings)} klasik istatistik testi çalıştırıldı, {n_sig} tanesi anlamlı (α={args.alpha}).")

    d = result.discovery
    if d.clustering:
        print(f"{d.clustering.k} gizli grup bulundu (silhouette skoru = {d.clustering.silhouette:.2f}).")
    if d.anomalies:
        print(f"{d.anomalies.n_flagged} sıra dışı (anormal) vaka işaretlendi.")
    n_hidden = sum(1 for p in d.mutual_info if p.hidden)
    if n_hidden:
        print(f"{n_hidden} gizli ilişki bulundu (klasik korelasyonun kaçırdığı/hiç test etmediği).")
    if d.risk_score:
        auc = d.risk_score.auc_logreg if d.risk_score.auc_logreg is not None else d.risk_score.auc_rf
        auc_txt = f"AUC={auc:.2f}" if auc is not None else "AUC hesaplanamadı"
        print(f"'{d.risk_score.dv}' için risk skoru modeli kuruldu ({auc_txt}).")
    for reason in d.skipped_reasons:
        print(f"Atlandı: {reason}")

    print(f"\nRapor kaydedildi: {result.out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
