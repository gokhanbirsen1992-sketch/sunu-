/* PaperForge Tur Rehberi — vanilla JS, build adımı yok.
   Uygulamayı bir tur rehberi gibi adım adım gezdirir; tur bittiğinde başa döner
   ve SINIRSIZ şekilde döngüye devam eder (kullanıcı çıkana dek). */
"use strict";

(() => {
  /* ---------- tur durakları ---------- */
  // reveal: tur sırasında geçici olarak görünür yapılacak gizli bölümler
  const STEPS = [
    {
      target: "header h1",
      title: "👋 PaperForge'a hoş geldiniz!",
      text: "Ben tur rehberinizim. SPSS verinizden APA formatında Word makalesine giden yolu " +
            "birlikte gezeceğiz. Tur bittiğinde başa döner ve <b>sınırsız</b> şekilde devam eder — " +
            "istediğiniz an <b>Esc</b> ile ya da ✕ düğmesiyle çıkabilirsiniz.",
    },
    {
      target: "#settings-card",
      reveal: ["#settings-body"],
      title: "⚙️ Ayarlar",
      text: "İlk durağımız ayarlar. Buraya <b>ücretsiz</b> bir yapay zekâ anahtarı girerseniz " +
            "Giriş/Tartışma bölümleri çok daha akıcı yazılır. Anahtar girmeseniz bile uygulama " +
            "<b>şablon modunda</b> eksiksiz bir taslak üretir.",
    },
    {
      target: "#mode-badge",
      reveal: ["#settings-body"],
      title: "🔖 Mod rozeti",
      text: "Bu rozet uygulamanın hangi modda çalıştığını gösterir: <b>LLM modu</b> (anahtar kayıtlı) " +
            "ya da <b>şablon modu</b> (anahtar yok). Anahtar kaydettiğinizde otomatik güncellenir.",
    },
    {
      target: '.key-row[data-provider="gemini"]',
      reveal: ["#settings-body"],
      title: "🔑 Anahtar girme ve test",
      text: "Önerilen sağlayıcı <b>Google Gemini</b> — kredi kartı istemez. Anahtarı yapıştırın, " +
            "<b>Kaydet</b> deyin, sonra <b>Test et</b> ile çalıştığını doğrulayın. Birden fazla " +
            "anahtar girerseniz kota dolunca otomatik olarak sıradakine geçilir.",
    },
    {
      target: "#upload-card",
      title: "1️⃣ Veri Yükleme",
      text: "Yolculuğun başlangıç noktası: SPSS (.sav/.zsav) veya .csv dosyanızı burada yüklersiniz. " +
            "Dosyanız yalnızca bu sunucuda işlenir.",
    },
    {
      target: "#file-input",
      title: "📁 Dosya seçimi",
      text: "Buradan veri dosyanızı seçin. SPSS etiketleri (değişken ve değer etiketleri) otomatik " +
            "okunur ve raporda kullanılır.",
    },
    {
      target: "#language",
      title: "🌐 Makale dili",
      text: "Makalenin <b>Türkçe</b> mi <b>İngilizce</b> mi yazılacağını seçin. İstatistik raporu ve " +
            "tüm bölümler seçtiğiniz dilde üretilir.",
    },
    {
      target: "#alpha",
      title: "📏 Anlamlılık düzeyi (α)",
      text: "Hangi p-değerinin \"anlamlı\" sayılacağını belirler. Sosyal bilimlerde yaygın seçim " +
            "<b>0.05</b>'tir; daha katı bir ölçüt isterseniz 0.01 seçin.",
    },
    {
      target: "#p-adjust",
      title: "🧮 Çoklu test düzeltmesi",
      text: "Çok sayıda test yapıldığında şans eseri anlamlı çıkma riski artar. <b>Holm</b> " +
            "(önerilen) veya <b>Benjamini-Hochberg</b> düzeltmesi bu riski kontrol altında tutar.",
    },
    {
      target: "#topic",
      title: "📝 Çalışmanın konusu",
      text: "Konunuzu 1-2 cümleyle yazın (örn. \"Hemşirelerde tükenmişlik ile iş doyumu ilişkisi\"). " +
            "Bu ipucu <b>literatür taramasının isabetini</b> belirgin şekilde artırır.",
    },
    {
      target: "#upload-btn",
      title: "⬆️ Yükle ve incele",
      text: "Bu düğme dosyayı sunucuya yükler; değişkenler otomatik tespit edilir ve bir sonraki " +
            "durağımız olan <b>Değişkenler</b> tablosu açılır.",
    },
    {
      target: "#vars-card",
      reveal: ["#vars-card"],
      title: "2️⃣ Değişkenler",
      text: "Yükleme sonrası burada her değişkenin otomatik tespit edilen <b>tipi</b> (sürekli, " +
            "Likert, kategorik…) ve <b>rolü</b> listelenir. Gerekirse düzeltin — örneğin Likert bir " +
            "maddeyi \"Sıralayıcı\" yapın; regresyon için bir değişkeni <b>Bağımlı değişken</b> " +
            "olarak işaretleyin.",
    },
    {
      target: "#start-btn",
      reveal: ["#vars-card"],
      title: "🚀 Analizi başlat",
      text: "Her şey hazır olduğunda bu düğme <b>ajan ordusunu</b> çalıştırır: temizlik, istatistik, " +
            "literatür, yazım, dil düzenleme, Reviewer 2 ve Word üretimi sırayla devreye girer.",
    },
    {
      target: "#pipeline-card",
      reveal: ["#pipeline-card"],
      title: "3️⃣ Pipeline — canlı izleme",
      text: "Analiz başlayınca 7 aşamalık boru hattını buradan <b>canlı</b> izlersiniz. Her aşama " +
            "kartında ajan çipleri gerçek zamanlı renklenir: 🤖 işçi üretir, 🔍 doğrulayıcı denetler, " +
            "⚖️ seçici en iyi taslağı seçer.",
    },
    {
      target: "#findings-list",
      reveal: ["#pipeline-card"],
      title: "📊 Anlamlı bulgular",
      text: "İstatistik aşaması tamamlandıkça anlamlı çıkan sonuçlar buraya <b>APA formatında</b> " +
            "düşer. Testler asla yapay zekâya hesaplatılmaz; SciPy/statsmodels ile deterministik " +
            "hesaplanır.",
    },
    {
      target: "#refs-list",
      reveal: ["#pipeline-card"],
      title: "📚 Bulunan kaynaklar",
      text: "Literatür ajanları OpenAlex, Crossref ve PubMed'i (ücretsiz, anahtarsız) tarar; bulunan " +
            "gerçek makaleler burada listelenir. <b>Uydurma kaynak yapısal olarak engellenir</b> — " +
            "yalnızca gerçekten bulunan kaynaklara atıf yapılır.",
    },
    {
      target: "#log",
      reveal: ["#pipeline-card"],
      title: "📜 Canlı günlük",
      text: "Perde arkasını merak edenler için: her ajanın ne yaptığı, hangi testin seçildiği ve " +
            "uyarılar buraya anlık akar.",
    },
    {
      target: "#result-card",
      reveal: ["#result-card"],
      title: "4️⃣ Sonuç",
      text: "Pipeline bitince turumuzun finali: <b>Word (.docx)</b> dosyanızı buradan indirirsiniz. " +
            "Ekinde veri temizleme raporu da bulunur. Unutmayın — üretilen makale bir <b>taslaktır</b>, " +
            "göndermeden önce mutlaka okuyun.",
    },
    {
      target: "#history-card",
      reveal: ["#history-body"],
      title: "🗂️ Geçmiş işler",
      text: "Önceki analizleriniz burada saklanır: tamamlananları yeniden indirebilir, hâlâ çalışan " +
            "bir işi \"izle\" bağlantısıyla tekrar canlı takibe alabilirsiniz.",
    },
    {
      target: "footer",
      title: "🏁 Turun sonu… ve yeniden başlangıç!",
      text: "Tebrikler, tüm durakları gezdiniz! İyi bir tur rehberi gibi ben de yorulmam: tur şimdi " +
            "<b>başa dönüyor</b> ve siz çıkana dek <b>sınırsız</b> döngüyle devam edecek. " +
            "Çıkmak için <b>Esc</b>, ✕ ya da karartılmış alana tıklamanız yeterli.",
    },
  ];

  const SPEEDS = { slow: 14000, normal: 9000, fast: 5000 };

  /* ---------- durum ---------- */
  const state = {
    active: false,
    idx: 0,
    lap: 1,          // kaçıncı turdayız — sınır yok
    playing: true,   // otomatik ilerleme (rehber anlatımı)
    speed: "normal",
    timer: null,
    revealed: [],    // [{el, hadHidden}]
  };

  /* ---------- DOM iskeleti ---------- */
  let backdrop, spot, tip;
  function buildDom() {
    backdrop = document.createElement("div");
    backdrop.className = "tour-backdrop";
    backdrop.addEventListener("click", stop);

    spot = document.createElement("div");
    spot.className = "tour-spot";

    tip = document.createElement("div");
    tip.className = "tour-tip";
    tip.setAttribute("role", "dialog");
    tip.setAttribute("aria-live", "polite");
    tip.innerHTML =
      '<div class="tour-tip-head">' +
        '<span class="tour-counter"></span>' +
        '<span class="tour-lap" title="Kaçıncı turda olduğunuz — sınır yok"></span>' +
        '<button class="tour-x" title="Turdan çık (Esc)" aria-label="Turdan çık">✕</button>' +
      "</div>" +
      '<h3 class="tour-title"></h3>' +
      '<p class="tour-text"></p>' +
      '<div class="tour-progress"><div class="tour-progress-bar"></div></div>' +
      '<div class="tour-controls">' +
        '<button class="btn small tour-prev" title="Önceki durak (←)">◀ Geri</button>' +
        '<button class="btn small tour-play" title="Otomatik anlatımı duraklat/sürdür (Boşluk)"></button>' +
        '<button class="btn small tour-next" title="Sonraki durak (→)">İleri ▶</button>' +
        '<select class="tour-speed" title="Anlatım hızı">' +
          '<option value="slow">🐢 Yavaş</option>' +
          '<option value="normal" selected>🚶 Normal</option>' +
          '<option value="fast">🐇 Hızlı</option>' +
        "</select>" +
      "</div>";

    tip.querySelector(".tour-x").addEventListener("click", stop);
    tip.querySelector(".tour-prev").addEventListener("click", () => go(state.idx - 1));
    tip.querySelector(".tour-next").addEventListener("click", () => go(state.idx + 1));
    tip.querySelector(".tour-play").addEventListener("click", togglePlay);
    tip.querySelector(".tour-speed").addEventListener("change", (e) => {
      state.speed = e.target.value;
      if (state.playing) armTimer(); // yeni hızla yeniden kur
      updateProgress();
    });

    document.body.append(backdrop, spot, tip);
  }

  /* ---------- gizli bölümleri geçici açma ---------- */
  function applyReveal(step) {
    restoreReveal();
    for (const sel of step.reveal || []) {
      const el = document.querySelector(sel);
      if (el && el.classList.contains("hidden")) {
        el.classList.remove("hidden");
        el.classList.add("tour-preview");
        state.revealed.push(el);
      }
    }
  }
  function restoreReveal() {
    for (const el of state.revealed) {
      el.classList.add("hidden");
      el.classList.remove("tour-preview");
    }
    state.revealed = [];
  }

  /* ---------- konumlandırma ---------- */
  function currentTarget() {
    return document.querySelector(STEPS[state.idx].target);
  }
  function position() {
    const el = currentTarget();
    if (!el) return;
    const r = el.getBoundingClientRect();
    const pad = 8;
    spot.style.top = r.top - pad + "px";
    spot.style.left = r.left - pad + "px";
    spot.style.width = r.width + pad * 2 + "px";
    spot.style.height = r.height + pad * 2 + "px";

    // balonu hedefin altına, sığmazsa üstüne yerleştir
    const tw = Math.min(400, window.innerWidth - 24);
    tip.style.width = tw + "px";
    const th = tip.offsetHeight || 220;
    let top = r.bottom + pad * 2 + 6;
    if (top + th > window.innerHeight - 12) top = r.top - pad - th - 14;
    if (top < 12) top = Math.max(12, (window.innerHeight - th) / 2);
    let left = r.left + r.width / 2 - tw / 2;
    left = Math.max(12, Math.min(left, window.innerWidth - tw - 12));
    tip.style.top = top + "px";
    tip.style.left = left + "px";
  }
  let rafPending = false;
  function schedulePosition() {
    if (rafPending || !state.active) return;
    rafPending = true;
    requestAnimationFrame(() => { rafPending = false; position(); });
  }

  /* ---------- adım gösterimi ---------- */
  function go(i) {
    if (!state.active) return;
    const n = STEPS.length;
    if (i >= n) { i = 0; state.lap += 1; }        // SONSUZ DÖNGÜ: başa sar, tur sayacını artır
    if (i < 0) { i = n - 1; state.lap = Math.max(1, state.lap - 1); }
    state.idx = i;

    const step = STEPS[i];
    applyReveal(step);
    const el = currentTarget();
    if (!el) { go(i + 1); return; }               // hedef yoksa durağı atla

    tip.querySelector(".tour-counter").textContent = `Durak ${i + 1}/${n}`;
    tip.querySelector(".tour-lap").textContent = `∞ ${state.lap}. tur`;
    tip.querySelector(".tour-title").textContent = step.title;
    tip.querySelector(".tour-text").innerHTML = step.text;

    el.scrollIntoView({ behavior: "smooth", block: "center" });
    position();
    // smooth scroll bitene dek konumu tazele
    let ticks = 0;
    const follow = setInterval(() => {
      schedulePosition();
      if (++ticks > 30) clearInterval(follow);
    }, 40);

    if (state.playing) armTimer();
    updateProgress();
  }

  /* ---------- otomatik anlatım (rehber modu) ---------- */
  function armTimer() {
    clearTimeout(state.timer);
    state.timer = setTimeout(() => go(state.idx + 1), SPEEDS[state.speed]);
  }
  function togglePlay() {
    state.playing = !state.playing;
    if (state.playing) armTimer(); else clearTimeout(state.timer);
    updatePlayBtn();
    updateProgress();
  }
  function updatePlayBtn() {
    tip.querySelector(".tour-play").textContent = state.playing ? "⏸ Duraklat" : "▶ Sürdür";
  }
  function updateProgress() {
    const bar = tip.querySelector(".tour-progress-bar");
    bar.style.animation = "none";
    // reflow ile animasyonu sıfırla
    void bar.offsetWidth;
    if (state.playing) {
      bar.style.animation = `tour-fill ${SPEEDS[state.speed]}ms linear forwards`;
    } else {
      bar.style.width = "0";
    }
  }

  /* ---------- başlat / durdur ---------- */
  function start() {
    if (state.active) return;
    if (!backdrop) buildDom();
    state.active = true;
    state.idx = 0;
    state.lap = 1;
    state.playing = true;
    document.body.classList.add("tour-on");
    backdrop.style.display = spot.style.display = tip.style.display = "block";
    updatePlayBtn();
    try { localStorage.setItem("pf_tour_seen", "1"); } catch (e) { /* gizli mod */ }
    const btn = document.getElementById("tour-btn");
    if (btn) btn.classList.remove("pulse");
    go(0);
  }
  function stop() {
    if (!state.active) return;
    state.active = false;
    clearTimeout(state.timer);
    restoreReveal();
    document.body.classList.remove("tour-on");
    backdrop.style.display = spot.style.display = tip.style.display = "none";
  }

  /* ---------- klavye ve yeniden konumlama ---------- */
  document.addEventListener("keydown", (e) => {
    if (!state.active) return;
    if (e.key === "Escape") { stop(); }
    else if (e.key === "ArrowRight") { e.preventDefault(); go(state.idx + 1); }
    else if (e.key === "ArrowLeft") { e.preventDefault(); go(state.idx - 1); }
    else if (e.key === " ") { e.preventDefault(); togglePlay(); }
  });
  window.addEventListener("resize", schedulePosition);
  window.addEventListener("scroll", schedulePosition, { passive: true });

  /* ---------- giriş düğmesi ---------- */
  function init() {
    const btn = document.getElementById("tour-btn");
    if (btn) {
      btn.addEventListener("click", start);
      let seen = null;
      try { seen = localStorage.getItem("pf_tour_seen"); } catch (e) { /* gizli mod */ }
      if (!seen) btn.classList.add("pulse"); // ilk ziyarette dikkat çek
    }
    // ?tur=1 ile otomatik başlat
    if (new URLSearchParams(location.search).get("tur") === "1") start();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();

  // dışarıya küçük bir API (konsoldan da yönetilebilir)
  window.PaperForgeTour = { start, stop, next: () => go(state.idx + 1), prev: () => go(state.idx - 1) };
})();
