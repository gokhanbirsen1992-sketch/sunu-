"""sav2q1 — SPSS .sav dosyasından Q1 gönderimine uygun makale üretim sistemi.

Bu paket, makaleyi ÜRETEN deterministik çekirdeği (LLM içermez) barındırır:
istatistik motoru (`engine`), Word derleyici (`docx`), şemalar (`contracts`)
ve doğrulama araçları (`tools`). LLM tarafı (yazar/hakem alt-agentları ve
`/makale` orkestratörü) `.claude/` altında yaşar ve bu çekirdeği çağırır.

Tasarımın iki taşıyıcı kuralı:
  1) Sayıları üreten TEK yer istatistik motorudur (results_ledger.json).
  2) Atıflar yalnızca gerçek PMID/DOI ile evidence_store.json'da var olabilir.
"""

__version__ = "0.1.0"
