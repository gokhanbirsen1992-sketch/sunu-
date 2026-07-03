const fileInput = document.getElementById("file-input");
const dvInput = document.getElementById("dv-input");
const langInput = document.getElementById("lang-input");
const alphaInput = document.getElementById("alpha-input");
const btn = document.getElementById("analyze-btn");
const statusText = document.getElementById("status-text");
const resultCard = document.getElementById("result-card");
const resultBody = document.getElementById("result-body");

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

btn.addEventListener("click", async () => {
  const file = fileInput.files[0];
  if (!file) {
    statusText.textContent = "Lütfen bir dosya seçin.";
    statusText.classList.add("err");
    return;
  }
  statusText.classList.remove("err");
  statusText.textContent = "Analiz ediliyor… (büyük dosyalarda biraz sürebilir)";
  btn.disabled = true;
  resultCard.classList.add("hidden");

  const form = new FormData();
  form.append("file", file);
  if (dvInput.value.trim()) form.append("dv", dvInput.value.trim());
  form.append("lang", langInput.value);
  form.append("alpha", alphaInput.value || "0.05");

  try {
    const resp = await fetch("/api/standalone/analyze", { method: "POST", body: form });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.detail || "Analiz başarısız.");
    renderResult(data);
    statusText.textContent = "Tamamlandı.";
  } catch (err) {
    statusText.textContent = "Hata: " + err.message;
    statusText.classList.add("err");
  } finally {
    btn.disabled = false;
  }
});

function renderResult(d) {
  const lines = [];
  lines.push(`<p>${d.n_rows_before} satır yüklendi → temizlik sonrası ${d.n_rows_after} satır.</p>`);
  lines.push(`<p>${d.n_tests} klasik istatistik testi çalıştırıldı, <b>${d.n_significant}</b> tanesi anlamlı.</p>`);
  if (d.clustering) {
    lines.push(`<p>🔍 <b>${d.clustering.k}</b> gizli grup bulundu (silhouette skoru = ${d.clustering.silhouette.toFixed(2)}).</p>`);
  }
  if (d.n_anomalies != null) {
    lines.push(`<p>⚠️ <b>${d.n_anomalies}</b> sıra dışı (anormal) vaka işaretlendi.</p>`);
  }
  if (d.n_hidden_relationships) {
    lines.push(`<p>🧩 <b>${d.n_hidden_relationships}</b> gizli ilişki bulundu (klasik korelasyonun kaçırdığı/hiç test etmediği).</p>`);
  }
  if (d.risk_score) {
    const auc = d.risk_score.auc != null ? d.risk_score.auc.toFixed(2) : "—";
    lines.push(`<p>🩺 '${escapeHtml(d.risk_score.dv)}' için risk skoru modeli kuruldu (AUC=${auc}).</p>`);
  }
  if (d.skipped_reasons && d.skipped_reasons.length) {
    lines.push(`<p class="hint">Atlanan analizler: ${escapeHtml(d.skipped_reasons.join(" "))}</p>`);
  }
  lines.push(`<a class="btn primary big" href="/api/standalone/download/${d.report_id}">📥 Raporu İndir (.docx)</a>`);
  resultBody.innerHTML = lines.join("\n");
  resultCard.classList.remove("hidden");
}
