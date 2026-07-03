/* PaperForge paneli — vanilla JS, build adımı yok */
"use strict";

const $ = (sel) => document.querySelector(sel);
let currentJobId = null;
let eventSource = null;
let stageOrder = [];

/* ---------- yardımcılar ---------- */
async function api(path, opts = {}) {
  const resp = await fetch("/api" + path, opts);
  const data = await resp.json().catch(() => ({}));
  if (!resp.ok) throw new Error(data.detail || resp.statusText);
  return data;
}
function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function logLine(msg, cls = "") {
  const log = $("#log");
  const time = new Date().toLocaleTimeString("tr-TR");
  const div = document.createElement("div");
  if (cls) div.className = cls;
  div.textContent = `[${time}] ${msg}`;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
}
function addListItem(listSel, html) {
  const ul = $(listSel);
  ul.classList.remove("empty");
  const li = document.createElement("li");
  li.innerHTML = html;
  ul.appendChild(li);
  ul.scrollTop = ul.scrollHeight;
}

/* ---------- ayarlar ---------- */
async function refreshSettings() {
  try {
    const s = await api("/settings");
    const badge = $("#mode-badge");
    if (s.mode === "llm") {
      badge.textContent = "LLM modu aktif";
      badge.className = "badge llm";
    } else {
      badge.textContent = "Şablon modu (anahtar yok)";
      badge.className = "badge template";
    }
    document.querySelectorAll(".key-row").forEach((row) => {
      const p = row.dataset.provider;
      const st = row.querySelector(".key-status");
      if (s.providers[p]) { st.textContent = "✓ kayıtlı"; st.className = "key-status ok"; }
      else { st.textContent = ""; st.className = "key-status"; }
    });
  } catch (e) { /* sessiz */ }
}

document.querySelectorAll(".key-row").forEach((row) => {
  const provider = row.dataset.provider;
  const input = row.querySelector("input");
  const st = row.querySelector(".key-status");
  row.querySelector(".save-key").addEventListener("click", async () => {
    try {
      await api("/settings/keys", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ provider, key: input.value.trim() }),
      });
      input.value = "";
      await refreshSettings();
    } catch (e) { st.textContent = "✗ " + e.message; st.className = "key-status err"; }
  });
  row.querySelector(".test-key").addEventListener("click", async () => {
    st.textContent = "test ediliyor…"; st.className = "key-status";
    try {
      const r = await api("/settings/test-key", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ provider, key: input.value.trim() }),
      });
      if (r.ok) { st.textContent = `✓ çalışıyor (${r.model})`; st.className = "key-status ok"; }
      else { st.textContent = "✗ " + r.error; st.className = "key-status err"; }
    } catch (e) { st.textContent = "✗ " + e.message; st.className = "key-status err"; }
  });
});

/* ---------- katlanır kartlar ---------- */
document.querySelectorAll("[data-toggle]").forEach((el) => {
  el.addEventListener("click", () => $("#" + el.dataset.toggle).classList.toggle("hidden"));
});

/* ---------- yükleme ---------- */
const KIND_LABELS = {
  continuous: "Sürekli (ölçüm)", ordinal: "Sıralayıcı (Likert)", nominal: "Kategorik",
  binary: "İkili (2 grup)", id: "Kimlik (analiz dışı)", date: "Tarih (analiz dışı)", excluded: "Analiz dışı",
};
const ROLE_LABELS = { auto: "Otomatik", dv: "Bağımlı değişken", iv: "Bağımsız değişken", exclude: "Analize katma" };

$("#upload-btn").addEventListener("click", async () => {
  const file = $("#file-input").files[0];
  const status = $("#upload-status");
  if (!file) { status.textContent = "Önce bir dosya seçin."; status.className = "status-text err"; return; }
  status.textContent = "Yükleniyor…"; status.className = "status-text";
  const fd = new FormData();
  fd.append("file", file);
  fd.append("language", $("#language").value);
  fd.append("alpha", $("#alpha").value);
  fd.append("p_adjust", $("#p-adjust").value);
  fd.append("topic_hint", $("#topic").value);
  try {
    const data = await api("/jobs", { method: "POST", body: fd });
    currentJobId = data.job.id;
    stageOrder = data.stage_order;
    status.textContent = `✓ ${file.name} yüklendi (${data.job.variables.length} değişken).`;
    renderVarsTable(data.job.variables);
    $("#vars-card").classList.remove("hidden");
    $("#vars-card").scrollIntoView({ behavior: "smooth" });
  } catch (e) {
    status.textContent = "✗ " + e.message; status.className = "status-text err";
  }
});

function renderVarsTable(variables) {
  const tbody = $("#vars-table tbody");
  tbody.innerHTML = "";
  for (const v of variables) {
    const tr = document.createElement("tr");
    const kindSel = Object.entries(KIND_LABELS).map(([k, l]) =>
      `<option value="${k}" ${k === v.kind ? "selected" : ""}>${l}</option>`).join("");
    const roleSel = Object.entries(ROLE_LABELS).map(([k, l]) =>
      `<option value="${k}" ${k === v.role ? "selected" : ""}>${l}</option>`).join("");
    tr.innerHTML =
      `<td><b>${esc(v.name)}</b></td><td>${esc(v.label || "—")}</td>` +
      `<td>${v.n_missing}</td><td>${v.n_unique}</td>` +
      `<td><select data-var="${esc(v.name)}" data-field="kind">${kindSel}</select></td>` +
      `<td><select data-var="${esc(v.name)}" data-field="role">${roleSel}</select></td>`;
    tbody.appendChild(tr);
  }
}

/* ---------- başlatma ---------- */
$("#start-btn").addEventListener("click", async () => {
  if (!currentJobId) return;
  const overrides = {};
  document.querySelectorAll("#vars-table select").forEach((sel) => {
    const name = sel.dataset.var;
    overrides[name] = overrides[name] || {};
    overrides[name][sel.dataset.field] = sel.value;
  });
  $("#start-btn").disabled = true;
  try {
    await api(`/jobs/${currentJobId}/start`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ overrides }),
    });
    resetPipelineView();
    $("#pipeline-card").classList.remove("hidden");
    $("#pipeline-card").scrollIntoView({ behavior: "smooth" });
    connectEvents(currentJobId);
    loadHistory();
  } catch (e) {
    alert("Başlatılamadı: " + e.message);
  } finally {
    $("#start-btn").disabled = false;
  }
});

function resetPipelineView() {
  $("#stages").innerHTML = "";
  $("#log").innerHTML = "";
  ["#findings-list", "#refs-list"].forEach((s) => { $(s).innerHTML = ""; $(s).classList.add("empty"); });
  $("#result-card").classList.add("hidden");
  $("#result-body").innerHTML = "";
}

/* ---------- pipeline görselleştirme ---------- */
function ensureStageEl(stageId, name) {
  let el = document.getElementById("stage-" + stageId);
  if (!el) {
    el = document.createElement("div");
    el.className = "stage";
    el.id = "stage-" + stageId;
    el.innerHTML =
      `<div class="stage-head"><span class="dot"></span><span>${esc(name)}</span>` +
      `<span class="hint-inline attempt"></span></div>` +
      `<div class="stage-summary"></div><div class="agents"></div><div class="stage-warn"></div>`;
    $("#stages").appendChild(el);
  }
  return el;
}
function renderStagesFromOrder() {
  for (const [id, name] of stageOrder) ensureStageEl(id, name);
}
function setStageStatus(stageId, status, summary, attempts) {
  const el = document.getElementById("stage-" + stageId);
  if (!el) return;
  el.classList.remove("running", "passed", "failed");
  if (["running", "passed", "failed"].includes(status)) el.classList.add(status);
  if (summary) el.querySelector(".stage-summary").textContent = summary;
  if (attempts > 1) el.querySelector(".attempt").textContent = `(deneme ${attempts})`;
}
function upsertAgentChip(stageId, agent) {
  const el = document.getElementById("stage-" + stageId);
  if (!el) return;
  const box = el.querySelector(".agents");
  let chip = box.querySelector(`[data-agent="${agent.agent_id}"]`);
  if (!chip) {
    chip = document.createElement("span");
    chip.dataset.agent = agent.agent_id;
    box.appendChild(chip);
  }
  const icon = { worker: "🤖", validator: "🔍", selector: "⚖️" }[agent.role] || "🤖";
  chip.className = `chip ${agent.role} ${agent.status}`;
  chip.title = agent.detail || agent.name;
  chip.textContent = `${icon} ${agent.name}`;
}

function renderSnapshot(job) {
  renderStagesFromOrder();
  for (const [stageId, sr] of Object.entries(job.stages || {})) {
    setStageStatus(stageId, sr.status, sr.summary, sr.attempts);
    for (const agent of sr.agents || []) upsertAgentChip(stageId, agent);
    const warnEl = document.querySelector(`#stage-${stageId} .stage-warn`);
    if (warnEl && sr.warnings && sr.warnings.length)
      warnEl.textContent = "⚠ " + sr.warnings[sr.warnings.length - 1];
  }
  if (["completed", "failed", "cancelled"].includes(job.status)) showResult(job);
}

function showResult(job) {
  const card = $("#result-card");
  const body = $("#result-body");
  card.classList.remove("hidden");
  if (job.status === "completed") {
    const warns = (job.warnings || []).map((w) => `<li>${esc(w)}</li>`).join("");
    body.innerHTML =
      `<div class="result-ok"><h3>✅ Makale hazır!</h3>` +
      `<p>${job.findings ? job.findings.filter((f) => f.significant).length : 0} anlamlı bulgu, ` +
      `${job.n_references || 0} akademik kaynak kullanıldı.</p>` +
      `<a class="btn primary" href="/api/jobs/${job.id}/download">⬇️ Word Dosyasını İndir (.docx)</a>` +
      (warns ? `<ul class="warn-list">${warns}</ul>` : "") +
      `<p class="hint" style="margin-top:10px">Lütfen makaleyi göndermeden önce dikkatle okuyun; ` +
      `otomatik üretilen içerik yazar denetimi gerektirir.</p></div>`;
  } else if (job.status === "failed") {
    body.innerHTML = `<div class="result-err"><h3>❌ İş başarısız</h3><p>${esc(job.error || "Bilinmeyen hata")}</p></div>`;
  } else {
    body.innerHTML = `<div class="result-err"><h3>⏹️ İş iptal edildi</h3></div>`;
  }
  card.scrollIntoView({ behavior: "smooth" });
}

/* ---------- SSE ---------- */
function connectEvents(jobId) {
  if (eventSource) eventSource.close();
  eventSource = new EventSource(`/api/jobs/${jobId}/events`);
  eventSource.onmessage = (msg) => {
    let ev;
    try { ev = JSON.parse(msg.data); } catch { return; }
    switch (ev.type) {
      case "snapshot":
        if (ev.stage_order) stageOrder = ev.stage_order;
        renderSnapshot(ev.job);
        break;
      case "stage_started":
        setStageStatus(ev.stage_id, "running", null, ev.attempt);
        logLine(`▶ ${ev.name} başladı (deneme ${ev.attempt})`);
        break;
      case "stage_finished":
        setStageStatus(ev.stage_id, ev.status, ev.summary, ev.attempts);
        logLine(`${ev.status === "passed" ? "✔" : "✖"} Aşama bitti: ${ev.summary || ev.stage_id}`,
                ev.status === "passed" ? "" : "err");
        break;
      case "agent_update":
        upsertAgentChip(ev.stage_id, ev.agent);
        break;
      case "stage_progress":
        logLine("… " + ev.message);
        break;
      case "finding":
        addListItem("#findings-list", `✅ ${esc(ev.finding.apa_tr || ev.finding.apa_en || ev.finding.id)}`);
        logLine(`★ Anlamlı bulgu: ${ev.finding.id}`);
        break;
      case "reference_found":
        addListItem("#refs-list",
          `${esc(ev.reference.title)}<br><span class="ref-meta">${esc(ev.reference.journal || "")} ` +
          `(${ev.reference.year || "?"}) · ${esc(ev.reference.source)}</span>`);
        break;
      case "log":
        logLine(ev.message, ev.level === "warn" ? "warn" : "");
        break;
      case "job_finished":
        logLine(ev.status === "completed" ? "🎉 Pipeline tamamlandı!" : `Pipeline bitti: ${ev.status}`,
                ev.status === "completed" ? "" : "err");
        loadHistory();
        break;
      case "heartbeat":
        break;
    }
  };
  eventSource.onerror = () => { /* EventSource otomatik yeniden bağlanır; snapshot durumu tazeler */ };
}

/* ---------- geçmiş ---------- */
async function loadHistory() {
  try {
    const jobs = await api("/jobs");
    const ul = $("#history-list");
    ul.innerHTML = "";
    if (!jobs.length) { ul.classList.add("empty"); return; }
    ul.classList.remove("empty");
    const STATUS_TR = { completed: "✅ tamamlandı", failed: "❌ başarısız", running: "⏳ çalışıyor",
                        pending: "🕐 bekliyor", cancelled: "⏹️ iptal" };
    for (const j of jobs) {
      const li = document.createElement("li");
      const dl = j.output ? ` — <a href="/api/jobs/${j.id}/download">indir</a>` : "";
      const watch = j.status === "running" ? ` — <a href="#" data-watch="${j.id}">izle</a>` : "";
      li.innerHTML = `<b>${esc(j.filename)}</b> · ${new Date(j.created_at).toLocaleString("tr-TR")} · ` +
        `${STATUS_TR[j.status] || j.status}${dl}${watch}`;
      ul.appendChild(li);
    }
    ul.querySelectorAll("[data-watch]").forEach((a) => {
      a.addEventListener("click", (e) => {
        e.preventDefault();
        currentJobId = a.dataset.watch;
        resetPipelineView();
        $("#pipeline-card").classList.remove("hidden");
        connectEvents(currentJobId);
      });
    });
  } catch (e) { /* sessiz */ }
}

/* ---------- başlangıç ---------- */
refreshSettings();
loadHistory();
