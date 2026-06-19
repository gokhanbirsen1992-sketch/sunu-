"""SPSS → Makale Üretici — Windows masaüstü uygulaması (Tkinter, ek bağımlılık yok).

`.sav` seç → "Makale Üret" → Word (.docx) üretilir ve klasörü açılır. Tamamen
yerel; sunucu/anahtar gerekmez. İşi sav2q1.pipeline (deterministik) yapar.

PyInstaller ile tek-dosya .exe olarak paketlenir (bkz. .github/workflows/windows-build.yml).
"""

from __future__ import annotations

import datetime as dt
import os
import queue
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

BLUE = "#0b5cad"


def _output_root() -> Path:
    base = Path.home() / "SPSS_Makaleler"
    base.mkdir(parents=True, exist_ok=True)
    return base


class App:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.sav: str | None = None
        self.q: queue.Queue = queue.Queue()
        self.last_docx: str | None = None

        root.title("SPSS → Makale Üretici")
        root.geometry("660x560")
        root.configure(bg="#f4f6f9")

        tk.Label(root, text="📊 SPSS → Makale Üretici", font=("Segoe UI", 18, "bold"),
                 bg="#f4f6f9", fg=BLUE).pack(pady=(18, 2))
        tk.Label(root, text="SPSS .sav dosyanızdan Türkçe makale taslağı (Word) üretir — tamamen yerel.",
                 font=("Segoe UI", 10), bg="#f4f6f9", fg="#6b7785").pack()

        card = tk.Frame(root, bg="white", bd=0, highlightthickness=0)
        card.pack(fill="x", padx=20, pady=14)

        self.pick_btn = tk.Button(card, text="📎  SPSS .sav dosyası seç", font=("Segoe UI", 11, "bold"),
                                  fg=BLUE, bg="#eef2f7", relief="flat", padx=14, pady=10, command=self.pick)
        self.pick_btn.pack(pady=(16, 6), padx=16, fill="x")
        self.file_lbl = tk.Label(card, text="Henüz dosya seçilmedi", font=("Segoe UI", 10),
                                 bg="white", fg="#6b7785")
        self.file_lbl.pack()

        opt = tk.Frame(card, bg="white"); opt.pack(fill="x", padx=16, pady=(8, 0))
        self.pubmed = tk.BooleanVar(value=False)
        tk.Checkbutton(opt, text="Gerçek PubMed kaynakları ekle (internet)", variable=self.pubmed,
                       bg="white", fg="#6b7785", font=("Segoe UI", 10), command=self._toggle_topic).pack(anchor="w")
        self.topic = tk.Entry(opt, font=("Segoe UI", 10))
        self.topic_lbl = tk.Label(opt, text="Konu (PubMed için):", bg="white", fg="#6b7785", font=("Segoe UI", 9))

        self.go = tk.Button(card, text="Makale Üret", font=("Segoe UI", 13, "bold"), fg="white", bg=BLUE,
                            relief="flat", pady=12, state="disabled", command=self.run)
        self.go.pack(pady=14, padx=16, fill="x")

        self.prog = ttk.Progressbar(root, mode="indeterminate")
        self.log = tk.Text(root, height=10, font=("Consolas", 9), bg="#0f1722", fg="#d6e2f0",
                           relief="flat", padx=10, pady=8)
        self.log.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        self._log("Hazır. Bir .sav dosyası seçin.")

        self.open_btn = tk.Button(root, text="📂  Word'ü Aç", font=("Segoe UI", 11, "bold"), fg="white",
                                  bg="#1a8a4a", relief="flat", pady=10, command=self._open, state="disabled")
        self.open_btn.pack(fill="x", padx=20, pady=(0, 16))

        self.root.after(120, self._poll)

    def _toggle_topic(self) -> None:
        if self.pubmed.get():
            self.topic_lbl.pack(anchor="w", pady=(6, 0)); self.topic.pack(fill="x")
        else:
            self.topic_lbl.pack_forget(); self.topic.pack_forget()

    def pick(self) -> None:
        path = filedialog.askopenfilename(title="SPSS .sav seç", filetypes=[("SPSS veri", "*.sav")])
        if path:
            self.sav = path
            self.file_lbl.config(text="📄 " + os.path.basename(path), fg=BLUE)
            self.go.config(state="normal")

    def _log(self, msg: str) -> None:
        self.log.insert("end", msg + "\n"); self.log.see("end")

    def run(self) -> None:
        if not self.sav:
            return
        self.go.config(state="disabled"); self.pick_btn.config(state="disabled")
        self.open_btn.config(state="disabled")
        self.prog.pack(fill="x", padx=20, pady=(0, 8)); self.prog.start(12)
        rundir = _output_root() / dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        brief = {"topic": self.topic.get().strip()} if self.topic.get().strip() else None
        t = threading.Thread(target=self._work, args=(self.sav, str(rundir), brief, self.pubmed.get()), daemon=True)
        t.start()

    def _work(self, sav, rundir, brief, with_pubmed) -> None:
        try:
            from sav2q1.pipeline import generate_article    # tembel import (hata GUI'de görünür)
            res = generate_article(sav, rundir, brief=brief, with_pubmed=with_pubmed,
                                   log=lambda m: self.q.put(("log", m)))
            self.q.put(("done", res))
        except Exception as e:  # noqa: BLE001
            self.q.put(("error", str(e)))

    def _poll(self) -> None:
        try:
            while True:
                kind, payload = self.q.get_nowait()
                if kind == "log":
                    self._log("• " + payload)
                elif kind == "done":
                    self.prog.stop(); self.prog.pack_forget()
                    self.last_docx = payload["docx"]
                    self._log(f"✓ Tamamlandı — {payload['n_results']} sonuç, "
                              f"sayı doğrulama: {payload['gate'].get('numeric')}")
                    self._log(f"Konum: {payload['docx']}")
                    self.go.config(state="normal"); self.pick_btn.config(state="normal")
                    self.open_btn.config(state="normal")
                elif kind == "error":
                    self.prog.stop(); self.prog.pack_forget()
                    self._log("✗ Hata: " + payload)
                    self.go.config(state="normal"); self.pick_btn.config(state="normal")
        except queue.Empty:
            pass
        self.root.after(120, self._poll)

    def _open(self) -> None:
        if not self.last_docx:
            return
        folder = os.path.dirname(self.last_docx)
        try:
            os.startfile(self.last_docx)            # Windows: Word'ü aç
        except Exception:                            # noqa: BLE001
            try:
                os.startfile(folder)
            except Exception:                        # noqa: BLE001
                self._log("Klasör: " + folder)


def main() -> None:
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
