const fileInput = document.getElementById("file-input");
const targetInput = document.getElementById("target-input");
const btn = document.getElementById("analyze-btn");
const spinner = document.getElementById("spinner");
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
    setStatus("Lütfen bir dosya seçin.", true);
    return;
  }
  setStatus("Analiz ediliyor… biraz sürebilir.", false);
  spinner.classList.remove("hidden");
  btn.disabled = true;
  resultCard.classList.add("hidden");

  const form = new FormData();
  form.append("file", file);
  if (targetInput.value.trim()) form.append("target", targetInput.value.trim());

  try {
    const resp = await fetch("/api/analyze", { method: "POST", body: form });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.detail || "Analiz başarısız.");
    renderResult(data);
    setStatus("Tamamlandı.", false);
  } catch (err) {
    setStatus("Hata: " + err.message, true);
  } finally {
    spinner.classList.add("hidden");
    btn.disabled = false;
  }
});

function setStatus(msg, isErr) {
  statusText.textContent = msg;
  statusText.classList.toggle("err", !!isErr);
}

function renderResult(d) {
  const lines = [];
  lines.push(`<div class="result-line">📄 ${d.n_rows} satır, ${d.n_columns} değişken analiz edildi.</div>`);
  lines.push(`<div class="result-line">🧪 ${d.n_tests} istatistik testi çalıştırıldı, <b>${d.n_significant}</b> tanesi anlamlı.</div>`);
  if (d.clustering) {
    lines.push(`<div class="result-line">🔍 <b>${d.clustering.k}</b> gizli grup bulundu (silhouette=${d.clustering.silhouette.toFixed(2)}).</div>`);
  }
  if (d.n_anomalies != null) {
    lines.push(`<div class="result-line">⚠️ <b>${d.n_anomalies}</b> sıra dışı vaka işaretlendi.</div>`);
  }
  if (d.n_hidden_relationships) {
    lines.push(`<div class="result-line">🧩 <b>${d.n_hidden_relationships}</b> gizli ilişki bulundu.</div>`);
  }
  if (d.risk_score) {
    const auc = d.risk_score.auc != null ? d.risk_score.auc.toFixed(2) : "—";
    lines.push(`<div class="result-line">🩺 '${escapeHtml(d.risk_score.target)}' için risk skoru modeli kuruldu (AUC=${auc}).</div>`);
  }
  if (d.notes && d.notes.length) {
    lines.push(`<div class="result-line hint">${escapeHtml(d.notes.join(" "))}</div>`);
  }
  resultBody.innerHTML = lines.join("\n") +
    `<a class="btn secondary" style="display:block;text-align:center;text-decoration:none;margin-top:14px" href="/api/download/${d.report_id}">📥 Raporu İndir (.docx)</a>`;
  resultCard.classList.remove("hidden");
}
