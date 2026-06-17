"""word2pdf grafik arayüzü (Tkinter).

Çift tıklayıp pencereyle kullanılan basit bir Word → PDF uygulaması:
dosyaları seç, "Dönüştür"e bas, PDF'ler hazır. Terminal/komut gerektirmez.

Çalıştırmak için:
    python -m word2pdf.gui
ya da kök dizindeki ``word2pdf_app.pyw`` dosyasına çift tıkla.
"""

from __future__ import annotations

import queue
import threading
from pathlib import Path

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .converter import (
    WORD_EXTENSIONS,
    ConversionError,
    convert_file,
    find_libreoffice,
    iter_word_files,
)

# Arayüzdeki motor adı -> convert_file motor değeri
ENGINE_LABELS = {
    "Otomatik (önerilen)": "auto",
    "LibreOffice (yüksek kalite)": "libreoffice",
    "Basit / Python": "python",
}


class Word2PdfApp:
    """Tek pencerelik Word → PDF dönüştürme uygulaması."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.files: list[Path] = []
        self.output_dir: Path | None = None
        self.events: "queue.Queue[tuple]" = queue.Queue()
        self._running = False
        self._build_ui()

    # ----------------------------------------------------------------- UI --
    def _build_ui(self) -> None:
        self.root.title("Word → PDF Dönüştürücü")
        self.root.geometry("600x520")
        self.root.minsize(520, 460)

        pad = {"padx": 10, "pady": 6}
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill="both", expand=True)

        ttk.Label(
            main,
            text="Word → PDF Dönüştürücü",
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            main,
            text="Word dosyalarını (.docx / .doc) seç ve PDF'e çevir.",
            foreground="#555",
        ).pack(anchor="w", pady=(0, 8))

        # --- Dosya ekleme düğmeleri ---
        btn_row = ttk.Frame(main)
        btn_row.pack(fill="x")
        ttk.Button(btn_row, text="Dosya Ekle…", command=self.add_files).pack(
            side="left"
        )
        ttk.Button(btn_row, text="Klasör Ekle…", command=self.add_folder).pack(
            side="left", padx=6
        )
        ttk.Button(btn_row, text="Listeyi Temizle", command=self.clear_files).pack(
            side="left"
        )

        # --- Dosya listesi ---
        list_frame = ttk.Frame(main)
        list_frame.pack(fill="both", expand=True, pady=8)
        self.listbox = tk.Listbox(list_frame, activestyle="none")
        scroll = ttk.Scrollbar(
            list_frame, orient="vertical", command=self.listbox.yview
        )
        self.listbox.configure(yscrollcommand=scroll.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # --- Seçenekler ---
        opts = ttk.LabelFrame(main, text="Seçenekler", padding=8)
        opts.pack(fill="x", pady=4)

        eng_row = ttk.Frame(opts)
        eng_row.pack(fill="x", pady=2)
        ttk.Label(eng_row, text="Dönüştürme motoru:").pack(side="left")
        self.engine_var = tk.StringVar(value="Otomatik (önerilen)")
        engine_combo = ttk.Combobox(
            eng_row,
            textvariable=self.engine_var,
            values=list(ENGINE_LABELS.keys()),
            state="readonly",
            width=28,
        )
        engine_combo.pack(side="left", padx=6)

        self.overwrite_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            opts,
            text="Var olan PDF'lerin üzerine yaz",
            variable=self.overwrite_var,
        ).pack(anchor="w", pady=2)

        out_row = ttk.Frame(opts)
        out_row.pack(fill="x", pady=2)
        ttk.Button(
            out_row, text="Çıktı Klasörü…", command=self.choose_output
        ).pack(side="left")
        self.output_label = ttk.Label(
            out_row, text="Çıktı: kaynak dosyayla aynı klasör", foreground="#555"
        )
        self.output_label.pack(side="left", padx=8)

        # --- Dönüştür düğmesi ---
        self.convert_btn = ttk.Button(
            main, text="PDF'e Dönüştür", command=self.start_conversion
        )
        self.convert_btn.pack(fill="x", pady=(8, 4))

        # --- İlerleme + durum ---
        self.progress = ttk.Progressbar(main, mode="determinate")
        self.progress.pack(fill="x")
        self.status = ttk.Label(main, text=self._engine_hint(), foreground="#333")
        self.status.pack(anchor="w", pady=(4, 0))

    def _engine_hint(self) -> str:
        if find_libreoffice():
            return "Hazır. LibreOffice bulundu (yüksek kalite dönüştürme)."
        return "Hazır. LibreOffice yok — basit (Python) motoru kullanılacak."

    # -------------------------------------------------------------- Eylemler --
    def add_files(self) -> None:
        paths = filedialog.askopenfilenames(
            title="Word dosyalarını seç",
            filetypes=[
                ("Word belgeleri", "*.docx *.doc"),
                ("Tüm dosyalar", "*.*"),
            ],
        )
        self._add_paths(Path(p) for p in paths)

    def add_folder(self) -> None:
        folder = filedialog.askdirectory(title="Word dosyalarını içeren klasörü seç")
        if not folder:
            return
        self._add_paths(iter_word_files(Path(folder), recursive=True))

    def _add_paths(self, paths) -> None:
        added = 0
        for path in paths:
            path = Path(path)
            if path.suffix.lower() in WORD_EXTENSIONS and path not in self.files:
                self.files.append(path)
                self.listbox.insert("end", f"  {path.name}")
                added += 1
        if added:
            self.status.config(text=f"{len(self.files)} dosya seçili.")

    def clear_files(self) -> None:
        self.files.clear()
        self.listbox.delete(0, "end")
        self.status.config(text=self._engine_hint())

    def choose_output(self) -> None:
        folder = filedialog.askdirectory(title="PDF'lerin kaydedileceği klasör")
        if folder:
            self.output_dir = Path(folder)
            self.output_label.config(text=f"Çıktı: {folder}")
        else:
            self.output_dir = None
            self.output_label.config(text="Çıktı: kaynak dosyayla aynı klasör")

    # ----------------------------------------------------- Dönüştürme akışı --
    def start_conversion(self) -> None:
        if self._running:
            return
        if not self.files:
            messagebox.showwarning("Dosya yok", "Önce en az bir Word dosyası ekle.")
            return

        self._running = True
        self.convert_btn.config(state="disabled")
        self.progress.config(maximum=len(self.files), value=0)
        engine = ENGINE_LABELS[self.engine_var.get()]
        overwrite = self.overwrite_var.get()

        worker = threading.Thread(
            target=self._worker,
            args=(list(self.files), self.output_dir, engine, overwrite),
            daemon=True,
        )
        worker.start()
        self.root.after(100, self._poll_events)

    def _worker(self, files, output_dir, engine, overwrite) -> None:
        """Arka planda çalışır; UI'yi olay kuyruğu üzerinden günceller."""
        succeeded = failed = 0
        for index, src in enumerate(files, start=1):
            self.events.put(("progress", index, len(files), src.name))
            try:
                result = convert_file(
                    src, output_dir, engine=engine, overwrite=overwrite
                )
            except ConversionError as exc:
                failed += 1
                self.events.put(("fail", src.name, str(exc)))
            except Exception as exc:  # noqa: BLE001 - beklenmeyen hatayı da göster
                failed += 1
                self.events.put(("fail", src.name, f"Beklenmeyen hata: {exc}"))
            else:
                succeeded += 1
                self.events.put(("ok", src.name, str(result)))
        self.events.put(("done", succeeded, failed))

    def _poll_events(self) -> None:
        """UI iş parçacığında kuyruğu boşaltıp arayüzü günceller."""
        try:
            while True:
                event = self.events.get_nowait()
                kind = event[0]
                if kind == "progress":
                    _, index, total, name = event
                    self.progress.config(value=index - 1)
                    self.status.config(text=f"Dönüştürülüyor ({index}/{total}): {name}")
                elif kind == "ok":
                    _, name, _result = event
                    self._mark(name, "✓")
                elif kind == "fail":
                    _, name, msg = event
                    self._mark(name, "✗")
                    self.status.config(text=f"Hata: {name} — {msg}")
                elif kind == "done":
                    _, succeeded, failed = event
                    self._finish(succeeded, failed)
                    return
        except queue.Empty:
            pass
        self.root.after(100, self._poll_events)

    def _mark(self, name: str, symbol: str) -> None:
        """Listede ilgili dosyanın yanına ✓/✗ koyar."""
        for i in range(self.listbox.size()):
            text = self.listbox.get(i)
            if text.strip().lstrip("✓✗ ").startswith(name):
                self.listbox.delete(i)
                self.listbox.insert(i, f"{symbol} {name}")
                break

    def _finish(self, succeeded: int, failed: int) -> None:
        self._running = False
        self.convert_btn.config(state="normal")
        self.progress.config(value=self.progress["maximum"])
        summary = f"Tamamlandı: {succeeded} başarılı"
        if failed:
            summary += f", {failed} başarısız"
        self.status.config(text=summary)
        if failed:
            messagebox.showwarning("Bitti", summary)
        else:
            messagebox.showinfo("Bitti", summary)


def main() -> None:
    root = tk.Tk()
    # Yüksek DPI ekranlarda daha okunaklı (Windows).
    try:
        from ctypes import windll  # type: ignore

        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:  # noqa: BLE001 - yalnızca Windows'ta vardır
        pass
    Word2PdfApp(root)
    root.mainloop()


if __name__ == "__main__":  # pragma: no cover
    main()
