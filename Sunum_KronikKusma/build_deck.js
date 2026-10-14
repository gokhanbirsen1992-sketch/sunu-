// Kronik Tekrarlayan Kusması Olan Çocuğa Yaklaşım — deck üreticisi (pptxgenjs, yapılandırılmış deck)
// İçerik: research/slides.json (onaylı slides_content.md'den tools/parse_slides.py ile) — metin elle kopyalanmaz.
// Kaynak numaraları: references/ref_order.json (tools/build_refs.py). Konuşmacı notu YOK.
// Çalıştır: NODE_PATH=<node_modules> node build_deck.js
"use strict";
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");
const React = require("react");
const ReactDOMServer = require("react-dom/server");
const sharp = require("sharp");
const fa = require("react-icons/fa6");

const ROOT = __dirname;
const SKILL = process.env.PPTX_SKILL_DIR;
const { applyTheme } = require(path.join(SKILL, "scripts", "apply_theme.js"));

const SLIDES = JSON.parse(fs.readFileSync(path.join(ROOT, "research", "slides.json"), "utf8"));
const REFS = JSON.parse(fs.readFileSync(path.join(ROOT, "references", "ref_order.json"), "utf8"));
const REFN = Object.fromEntries(REFS.map((r) => [r.pmid, r.n]));
const S = Object.fromEntries(SLIDES.map((s) => [s.id, s]));

const THEME = {
	name: "Kronik Kusma",
	headFontFace: "Cambria",
	bodyFontFace: "Calibri",
	colors: {
		dk1: "1D2B33", lt1: "FFFFFF", dk2: "0E5A5F", lt2: "EAF4F2",
		accent1: "00938A", accent2: "D9573B", accent3: "E9B44C", accent4: "5B6B73",
		accent5: "BFDCD8", accent6: "F8E1D9", hlink: "0E5A5F", folHlink: "5B6B73",
	},
};
const HEX = THEME.colors; // yalnız hex isteyen seçenekler için

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
pres.author = "Kongre sunumu";
pres.title = "Kronik Tekrarlayan Kusması Olan Çocuğa Yaklaşım";
pres.subject = "Çocuk gastroenterolojisi";
const C = pres.SchemeColor;
const W = 13.333, H = 7.5, MX = 0.6;

// ---------- yerleşimler (layouts) ----------
pres.defineSlideMaster({
	title: "KAPAK",
	background: { color: C.text2 },
	objects: [
		{ placeholder: { options: { name: "title", type: "title", x: 0.8, y: 1.9, w: 11.7, h: 1.9, fontSize: 40, bold: true, color: C.background1, valign: "bottom", align: "left", margin: 0 }, text: "" } },
		{ placeholder: { options: { name: "sub", type: "body", x: 0.8, y: 4.0, w: 11.7, h: 0.7, fontSize: 22, color: C.accent5, margin: 0 }, text: "" } },
		{ placeholder: { options: { name: "meta", type: "body", x: 0.8, y: 5.6, w: 11.7, h: 0.9, fontSize: 16, color: C.background1, margin: 0 }, text: "" } },
	],
});
pres.defineSlideMaster({
	title: "ICERIK",
	background: { color: C.background1 },
	objects: [
		{ placeholder: { options: { name: "section", type: "body", x: MX, y: 0.25, w: 9.0, h: 0.32, fontSize: 12, bold: true, color: C.accent1, margin: 0 }, text: "" } },
		{ placeholder: { options: { name: "title", type: "title", x: MX, y: 0.58, w: 12.13, h: 1.0, fontSize: 26, bold: true, color: C.text1, valign: "top", align: "left", margin: 0 }, text: "" } },
		{ placeholder: { options: { name: "src", type: "body", x: MX, y: 6.98, w: 11.2, h: 0.3, fontSize: 10, color: C.accent4, margin: 0 }, text: "" } },
	],
	slideNumber: { x: 12.15, y: 6.98, w: 0.6, h: 0.3, fontSize: 10, color: HEX.accent4, align: "right" },
});
pres.defineSlideMaster({
	title: "KAYNAK",
	background: { color: C.background1 },
	objects: [
		{ placeholder: { options: { name: "title", type: "title", x: MX, y: 0.35, w: 12.13, h: 0.6, fontSize: 24, bold: true, color: C.text1, align: "left", margin: 0 }, text: "" } },
	],
	slideNumber: { x: 12.15, y: 6.98, w: 0.6, h: 0.3, fontSize: 10, color: HEX.accent4, align: "right" },
});
pres.defineSlideMaster({
	title: "KOYU",
	background: { color: C.text1 },
	objects: [
		{ placeholder: { options: { name: "title", type: "title", x: MX, y: 0.5, w: 12.13, h: 0.9, fontSize: 30, bold: true, color: C.background1, align: "left", margin: 0 }, text: "" } },
	],
});

// ---------- yardımcılar ----------
function compress(nums) {
	const a = [...new Set(nums)].sort((x, y) => x - y);
	const out = [];
	for (let i = 0; i < a.length; i++) {
		let j = i;
		while (j + 1 < a.length && a[j + 1] === a[j] + 1) j++;
		out.push(j - i >= 2 ? `${a[i]}–${a[j]}` : j > i ? `${a[i]},${a[j]}` : `${a[i]}`);
		i = j;
	}
	return out.join(",");
}
const pm = (...pmids) => pmids.map((p) => {
	if (!REFN[p]) throw new Error(`ref_order.json'da yok: ${p}`);
	return REFN[p];
});

// runs → pptxgenjs metin nesneleri
function textObjs(runs, base) {
	const out = [];
	for (const r of runs) {
		const citeColor = base.color === C.background1 ? C.background1 : C.accent4;
		if (r.cite) out.push({ text: `[${compress(r.cite)}]`, options: { ...base, bold: false, superscript: true, color: citeColor } });
		else if (r.t) out.push({ text: r.t, options: { ...base, bold: !!(r.b || base.bold) } });
	}
	return out;
}
// paragraflar (her biri runs) → tek metin dizisi
function paras(list, base, para) {
	const out = [];
	list.forEach((runs, i) => {
		const objs = textObjs(runs, base);
		objs.forEach((o, k) => {
			// paragraf seçenekleri yalnız ilk parçaya: pptxgenjs bullet taşıyan her parçada yeni paragraf açar
			if (k === 0) Object.assign(o.options, para || {});
			if (k === objs.length - 1 && i < list.length - 1) o.options.breakLine = true;
		});
		out.push(...objs);
	});
	return out;
}
const plain = (runs) => runs.map((r) => (r.cite ? "" : r.t || "")).join("").trim();
// runs'ı bir ayraçta (" · ", "; ", "→") böl
function splitRuns(runs, sep) {
	const parts = [[]];
	for (const r of runs) {
		if (r.cite) { parts[parts.length - 1].push(r); continue; }
		const bits = r.t.split(sep);
		bits.forEach((b, i) => {
			if (i > 0) parts.push([]);
			if (b) parts[parts.length - 1].push({ t: b, b: r.b });
		});
	}
	return parts.map((p) => p.filter((r) => r.cite || r.t.trim())).filter((p) => p.length);
}
function trimRuns(runs) {
	const r = runs.map((x) => ({ ...x }));
	if (r.length && r[0].t) {
		r[0].t = r[0].t.replace(/^\s+/, "");
		r[0].t = r[0].t.charAt(0).toLocaleUpperCase("tr-TR") + r[0].t.slice(1);
	}
	return r;
}
function stripPrefix(runs, re) {
	const r = runs.map((x) => ({ ...x }));
	if (r[0] && r[0].t) r[0].t = r[0].t.replace(re, "");
	return r;
}

const iconCache = {};
async function icon(name, hex, px = 256) {
	const key = `${name}-${hex}`;
	if (iconCache[key]) return iconCache[key];
	const svg = ReactDOMServer.renderToStaticMarkup(React.createElement(fa[name], { size: px, color: `#${hex}` }));
	const buf = await sharp(Buffer.from(svg)).png().toBuffer();
	iconCache[key] = "image/png;base64," + buf.toString("base64");
	return iconCache[key];
}

let objId = 0;
const oid = (n) => `${n}-${++objId}`;

function srcLine(slide, s, extra = []) {
	const nums = [...new Set([...(s ? s.cites : []), ...extra])];
	slide.addText(nums.length ? `Kaynak no: ${compress(nums)} · tam liste sondaki kaynak slaytlarında` : " ", { placeholder: "src" });
}
function dipnot(slide, s, y = 6.45, w = 12.13) {
	if (!s.dipnot) return;
	slide.addText(textObjs(s.dipnot, { fontSize: 11, italic: true, color: C.accent4 }), {
		x: MX, y, w, h: 0.42, margin: 0, valign: "top", isTextBox: true, objectName: oid("dipnot"),
	});
}
function chip(slide, text, x, y, w, kind = "amber") {
	const fill = { amber: C.accent3, slate: C.accent4, coral: C.accent2, teal: C.accent1 }[kind];
	const color = kind === "amber" ? C.text1 : C.background1;
	slide.addText(text, {
		shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.08, x, y, w, h: 0.36, fill: { color: fill },
		fontSize: 11, bold: true, color, align: "center", valign: "middle", margin: 2, isTextBox: true, objectName: oid("etiket"),
	});
}
// sağ panel: anahtar sayı kartı
function keyFigure(slide, s, num, cap, y = 1.75) {
	const body = s.bullets.map(plain).join(" ");
	if (!body.includes(num)) throw new Error(`${s.id}: anahtar sayı '${num}' slayt metninde yok (yeni iddia yasak)`);
	slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 8.75, y, w: 3.98, h: 2.55, rectRadius: 0.12, fill: { color: C.background2 }, line: { type: "none" }, objectName: oid("kart") });
	slide.addText(num, { x: 8.95, y: y + 0.25, w: 3.58, h: 1.15, fontSize: num.length > 7 ? 34 : 48, bold: true, color: C.text2, fontFace: THEME.headFontFace, margin: 0, align: "left", valign: "middle", isTextBox: true, objectName: oid("sayi") });
	slide.addText(cap, { x: 8.95, y: y + 1.45, w: 3.58, h: 0.95, fontSize: 14, color: C.text1, margin: 0, valign: "top", isTextBox: true, objectName: oid("sayi-alt") });
}
async function iconCard(slide, name, label, y = 1.75, kind = "teal") {
	const hex = kind === "coral" ? HEX.accent2 : HEX.accent1;
	slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 8.75, y, w: 3.98, h: 2.55, rectRadius: 0.12, fill: { color: kind === "coral" ? C.accent6 : C.background2 }, line: { type: "none" }, objectName: oid("kart") });
	slide.addImage({ data: await icon(name, hex), x: 9.0, y: y + 0.3, w: 1.0, h: 1.0, altText: label, objectName: oid("ikon") });
	slide.addText(label, { x: 8.95, y: y + 1.45, w: 3.58, h: 0.95, fontSize: 15, bold: true, color: C.text1, margin: 0, valign: "top", isTextBox: true, objectName: oid("ikon-alt") });
}
function etiketChips(slide, s, y = 4.5) {
	if (!s.etiket) return;
	slide.addText(`Kanıt notu: ${s.etiket}`, {
		x: 8.75, y, w: 3.98, h: 0.9, fontSize: 12, color: C.text1, fill: { color: "FDF3DC" }, margin: 6,
		valign: "top", isTextBox: true, objectName: oid("kanit-notu"),
	});
}
function bulletsBox(slide, list, opt = {}) {
	const base = { fontSize: opt.fontSize || 22, color: C.text1 };
	slide.addText(paras(list, base, { bullet: opt.numbered ? { type: "number" } : { indent: 20 }, paraSpaceAfter: opt.space || 18 }), {
		x: opt.x || MX, y: opt.y || 1.75, w: opt.w || 7.85, h: opt.h || 4.55, valign: "top", margin: 0, isTextBox: true, objectName: oid("govde"),
	});
}
function newSlide(master, section) {
	return pres.addSlide({ masterName: master, sectionTitle: section });
}
function head(slide, s, section) {
	slide.addText(section, { placeholder: "section" });
	slide.addText(s.title, { placeholder: "title" });
}
function table(slide, rows, colW, opt = {}) {
	const tbl = rows.map((row, ri) => row.map((cell) => ({
		text: cell.length ? textObjs(cell, { fontSize: opt.fontSize || 15, color: ri === 0 ? C.background1 : C.text1, bold: ri === 0 }) : [{ text: " ", options: { fontSize: opt.fontSize || 15 } }],
		options: { fill: { color: ri === 0 ? (opt.headFill || C.text2) : ri % 2 ? C.background1 : C.background2 }, valign: "middle", margin: [4, 8, 4, 8] },
	})));
	slide.addTable(tbl, { x: MX, y: opt.y || 1.75, w: colW.reduce((a, b) => a + b, 0), colW, rowH: opt.rowH, border: { type: "solid", pt: 0.75, color: HEX.accent5 }, objectName: oid("tablo") });
}

// ---------- bölümler ----------
const SEC = [
	[["S1", "S2"], "Açılış"],
	[["S3", "S4", "S5", "S6", "S7"], "1 · Patern ve tanım"],
	[["S8", "S9", "S10", "S11", "S12"], "2 · Öykü ve muayene"],
	[["S13", "S14", "S15", "S16", "S17", "S18", "S19"], "3 · Organik ayırıcı tanı"],
	[["S20", "S21", "S22", "S23", "S24", "S25", "S26", "S27"], "4 · Basamaklı tetkik"],
	[["S28", "S29", "S30", "S31", "S32"], "5 · Fonksiyonel tanı: Rome V"],
	[["S33", "S34", "S35", "S36", "S37", "S38", "S39", "S40"], "6 · Yönetim"],
	[["S41"], "Kapanış"],
];
const secOf = Object.fromEntries(SEC.flatMap(([ids, name]) => ids.map((i) => [i, name])));

// Standart sağ panel tanımları (anahtar sayı slayt metninde geçmek ZORUNDA — keyFigure denetler)
const KF = {
	S1: [">4 hafta", "UEG/ESNM eşiği; pediatriye özgü değil"],
	S2: ["%28,0", "çocukta ≥1 DGBI (4 ülke, n=7718)"],
	S3: ["%53,2", "akalazyalı çocuklarda kusma (n=126)"],
	S5: ["%88", "siklik paternde idiyopatik SKS (n=225)"],
	S6: ["%40", "adolesanda disotonomi semptomları (3. basamak, n=100)"],
	S8: ["~%90", "SKS'de prodrom"],
	S9: ["%75", "posterior fossa tümöründe bulantı-kusma"],
	S11: ["%38", "organik tanılıların başlangıçta bayraksız oranı (tüm DGBI)"],
	S12: ["%15–59", "SKS'de anksiyete (ölçüm aracı ve yaşa göre)"],
	S19: ["%48,5–66,7", "gastroparezi/FD'li çocuklarda ARFID taraması pozitif"],
	S24: ["%7,0", "alarm bulgusuz EGD'de yönetim değişikliği (n=287)"],
	S25: ["%22", "pediatrik 4. saat retansiyonun 95. persentili"],
	S27: ["6125 $", "hasta başı ortalama fatura (2015, 3. basamak)"],
	S28: ["%43", "GFD'ye uyumlu çölyaklı çocuklarda DGBI (n=191)"],
	S33: ["%73,9", "yaşam tarzı uyumu; başarıyı öngördürüyor (Türkiye, n=119)"],
	S34: ["güçlü öneri", "migren öyküsünde antimigren ajan (NASPGHAN 2025)"],
	S35: ["%65,6", "amitriptilinle tam remisyon (RCT, n=64, plasebosuz)"],
	S36: ["%80", "PENFS yanıtı (kontrolsüz, n=30)"],
	S37: ["%23", "yalnız danışmanlıkla düzelen ruminasyon"],
	S38: ["%60 vs %55", "hipnoterapi vs standart tedavi, 12. ay"],
};
const IC = {
	S13: ["FaTriangleExclamation", "Safralı kusma: aksi kanıtlanana dek obstrüksiyon", "coral"],
	S15: ["FaMicroscope", "Mukoza normal görünse de biyopsi"],
	S16: ["FaBrain", "KİBAS bulgusu yokluğu tümörü dışlamaz"],
	S17: ["FaFlask", "Atak anındaki biyokimya ipucu verir"],
	S18: ["FaStethoscope", "ACTH + kortizol eşzamanlı"],
	S23: ["FaXRay", "Zamanlama: US atak sırasında"],
	S39: ["FaHospital", "Doğrulanmış pediatrik yatış kriteri yok"],
};

async function stdSlide(id) {
	const s = S[id];
	const slide = newSlide("ICERIK", secOf[id]);
	head(slide, s, secOf[id]);
	bulletsBox(slide, s.bullets);
	if (KF[id]) keyFigure(slide, s, ...KF[id]);
	else if (IC[id]) await iconCard(slide, IC[id][0], IC[id][1], 1.75, IC[id][2]);
	etiketChips(slide, s);
	dipnot(slide, s);
	srcLine(slide, s);
	return slide;
}

// ---------- özel slaytlar ----------
function kapak() {
	const slide = newSlide("KAPAK", "Açılış");
	slide.addText("Kronik Tekrarlayan Kusması Olan Çocuğa Yaklaşım", { placeholder: "title" });
	slide.addText("Patern → kırmızı bayrak → basamaklı tetkik → Rome V", { placeholder: "sub" });
	slide.addText("[Konuşmacı adı, unvan · Kurum]   ·   [Kongre adı · Tarih]", { placeholder: "meta" });
}
async function yolHaritasi() {
	const slide = newSlide("ICERIK", "Açılış");
	slide.addText("Açılış", { placeholder: "section" });
	slide.addText("Yol haritası: altı adımda kronik tekrarlayan kusma", { placeholder: "title" });
	const items = [
		["FaWaveSquare", "Patern ve tanım"], ["FaUserDoctor", "Öykü ve muayene"], ["FaMagnifyingGlass", "Organik ayırıcı tanı"],
		["FaVial", "Basamaklı tetkik"], ["FaBookMedical", "Fonksiyonel tanı: Rome V"], ["FaPrescriptionBottleMedical", "Yönetim"],
	];
	for (let i = 0; i < 6; i++) {
		const col = i % 3, row = Math.floor(i / 3);
		const x = MX + col * 4.1, y = 1.8 + row * 2.45;
		slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 3.85, h: 2.15, rectRadius: 0.12, fill: { color: C.background2 }, line: { type: "none" }, objectName: oid("karo") });
		slide.addImage({ data: await icon(items[i][0], HEX.accent1), x: x + 0.3, y: y + 0.3, w: 0.75, h: 0.75, altText: items[i][1], objectName: oid("ikon") });
		slide.addText(`${i + 1}`, { x: x + 2.85, y: y + 0.2, w: 0.75, h: 0.75, fontSize: 36, bold: true, color: C.accent1, fontFace: THEME.headFontFace, align: "right", margin: 0, isTextBox: true, objectName: oid("no") });
		slide.addText(items[i][1], { x: x + 0.3, y: y + 1.25, w: 3.3, h: 0.7, fontSize: 20, bold: true, color: C.text1, margin: 0, valign: "top", isTextBox: true, objectName: oid("karo-yazi") });
	}
	slide.addText(" ", { placeholder: "src" });
}
function sekilSlayt(id, img) {
	const s = S[id];
	const slide = newSlide("ICERIK", secOf[id]);
	head(slide, s, secOf[id]);
	bulletsBox(slide, s.bullets, { w: 6.0, fontSize: 17 });
	slide.addImage({ path: path.join(ROOT, "figures", img), x: 6.85, y: 1.7, w: 5.88, h: 4.36, altText: "Şematik patern çizimi", objectName: oid("sekil") });
	dipnot(slide, s);
	srcLine(slide, s);
}
function yasHaritasi() {
	const id = "S7", s = S[id];
	const slide = newSlide("ICERIK", secOf[id]);
	head(slide, s, secOf[id]);
	const cols = s.bullets.slice(0, 3);
	cols.forEach((runs, i) => {
		const x = MX + i * 4.1;
		const header = runs[0].t.replace(/:$/, "");
		const items = splitRuns(runs.slice(1), "; ").map(trimRuns);
		slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.75, w: 3.85, h: 3.55, rectRadius: 0.12, fill: { color: C.background2 }, line: { type: "none" }, objectName: oid("yas-kart") });
		slide.addText(header, { x: x + 0.25, y: 1.9, w: 3.4, h: 0.5, fontSize: 20, bold: true, color: C.text2, fontFace: THEME.headFontFace, margin: 0, isTextBox: true, objectName: oid("yas-baslik") });
		slide.addText(paras(items, { fontSize: 17, color: C.text1 }, { bullet: { indent: 16 }, paraSpaceAfter: 10 }), {
			x: x + 0.25, y: 2.5, w: 3.4, h: 2.7, valign: "top", margin: 0, isTextBox: true, objectName: oid("yas-govde"),
		});
	});
	const last = s.bullets[3];
	slide.addText(textObjs(last, { fontSize: 17, color: C.background1, bold: false }), {
		shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.1, x: MX, y: 5.5, w: 12.13, h: 0.7, fill: { color: C.accent2 },
		valign: "middle", margin: [4, 14, 4, 14], isTextBox: true, objectName: oid("her-yas"),
	});
	dipnot(slide, s, 6.38);
	srcLine(slide, s);
}
function tabloSlayt(id, colW, opt = {}) {
	const s = S[id];
	const slide = newSlide("ICERIK", secOf[id]);
	head(slide, s, secOf[id]);
	table(slide, s.table, colW, opt);
	dipnot(slide, s, opt.dipY || 6.38);
	srcLine(slide, s, s.cites_line ? s.cites_line.flatMap((r) => r.cite || []) : []);
}
function acilDallar() {
	const id = "S20", s = S[id];
	const slide = newSlide("ICERIK", secOf[id]);
	head(slide, s, secOf[id]);
	s.bullets.forEach((runs, i) => {
		const col = i % 2, row = Math.floor(i / 2);
		const x = MX + col * 6.13, y = 1.75 + row * 2.2;
		const [trig, act] = splitRuns(runs, "→");
		slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: 5.95, h: 2.0, rectRadius: 0.12, fill: { color: C.accent6 }, line: { type: "none" }, objectName: oid("acil-kart") });
		slide.addText(textObjs(trimRuns(trig), { fontSize: 17, bold: true, color: C.text1 }), { x: x + 0.3, y: y + 0.18, w: 5.4, h: 0.85, valign: "top", margin: 0, isTextBox: true, objectName: oid("acil-tetik") });
		slide.addText([{ text: "→ ", options: { fontSize: 18, bold: true, color: C.accent2 } }, ...textObjs(trimRuns(act), { fontSize: 18, bold: true, color: C.accent2 })], { x: x + 0.3, y: y + 1.05, w: 5.4, h: 0.8, valign: "top", margin: 0, isTextBox: true, objectName: oid("acil-eylem") });
	});
	dipnot(slide, s, 6.25);
	srcLine(slide, s);
}
function kritikOrnek() {
	const id = "S22", s = S[id];
	const slide = newSlide("ICERIK", secOf[id]);
	head(slide, s, secOf[id]);
	const heads = ["Ne zaman?", "Kan", "İdrar"];
	s.bullets.slice(0, 3).forEach((runs, i) => {
		const x = MX + i * 4.1;
		const body = stripPrefix(runs, /^(Ne zaman|Kan|İdrar):\s*/);
		slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.75, w: 3.85, h: 3.2, rectRadius: 0.12, fill: { color: C.background2 }, line: { type: "none" }, objectName: oid("kit-kart") });
		slide.addText(heads[i], { x: x + 0.25, y: 1.9, w: 3.4, h: 0.5, fontSize: 20, bold: true, color: C.text2, fontFace: THEME.headFontFace, margin: 0, isTextBox: true, objectName: oid("kit-baslik") });
		slide.addText(textObjs(trimRuns(body), { fontSize: 19, color: C.text1 }), { x: x + 0.25, y: 2.5, w: 3.4, h: 2.35, valign: "top", margin: 0, isTextBox: true, objectName: oid("kit-govde") });
	});
	slide.addText(textObjs(s.bullets[3], { fontSize: 18, bold: true, color: C.background1 }), {
		shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.1, x: MX, y: 5.15, w: 7.9, h: 0.75, fill: { color: C.accent1 }, valign: "middle", margin: [4, 14, 4, 14], isTextBox: true, objectName: oid("dekstroz"),
	});
	slide.addText("Dekstroz tanı için geciktirilmez", {
		shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.1, x: 8.75, y: 5.15, w: 3.98, h: 0.75, fill: { color: C.accent2 }, fontSize: 17, bold: true, color: C.background1, align: "center", valign: "middle", margin: 4, isTextBox: true, objectName: oid("uyari"),
	});
	dipnot(slide, s, 6.15);
	srcLine(slide, s);
}
function algoritma() {
	const id = "S26", s = S[id];
	const slide = newSlide("ICERIK", secOf[id]);
	slide.addText(secOf[id], { placeholder: "section" });
	slide.addText("Tek sayfa basamaklı algoritma", { placeholder: "title" });
	const box = (x, y, w, h, title, body, cites, kind) => {
		const fill = { coral: C.accent6, teal: C.background2, amber: "FDF3DC", gray: "F1F3F4" }[kind];
		const line = kind === "amber" ? { color: HEX.accent3, width: 1.5, dashType: "dash" } : { type: "none" };
		slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.1, fill: { color: fill }, line, objectName: oid("algo-kutu") });
		slide.addText([
			{ text: title, options: { fontSize: 15, bold: true, color: kind === "coral" ? C.accent2 : C.text2, breakLine: true } },
			{ text: body, options: { fontSize: 14, color: C.text1 } },
			{ text: ` [${compress(cites)}]`, options: { fontSize: 14, superscript: true, color: C.accent4 } },
		], { x: x + 0.15, y: y + 0.08, w: w - 0.3, h: h - 0.16, valign: "top", margin: 0, isTextBox: true, objectName: oid("algo-yazi") });
	};
	const arrow = (x, y1, y2) => slide.addShape(pres.shapes.LINE, { x, y: y1, w: 0, h: y2 - y1, line: { color: HEX.accent4, width: 1.5, endArrowType: "triangle" }, objectName: oid("ok") });
	const X = MX, FW = 12.13;
	box(X, 1.6, FW, 0.85, "Basamak 0 · Acil (aynı saat)", "Safralı kusma + karın bulgusu → acil grafi + cerrahi · Ensefalopati → glukoz, kan gazı, amonyak · Na↓/glukoz↓ → ACTH + kortizol · Nörolojik bulgu → beyin MR", pm("23818085", "2769545", "22642880", "26678622", "33224097", "25957977"), "coral");
	arrow(X + FW / 2, 2.45, 2.65);
	const w3 = (FW - 0.4) / 3;
	box(X, 2.65, w3, 1.1, "Basamak 1 · Siklik patern", "Kan + idrar tarama, üst GİS pasaj grafisi", pm("40836301"), "teal");
	box(X + w3 + 0.2, 2.65, w3, 1.1, "Basamak 1 · Kronik günlük (ÇIKARIM)", "Endoskopi + biyopsi öncelikli; anatomi için grafi", pm("8604272", "36056317"), "amber");
	box(X + 2 * (w3 + 0.2), 2.65, w3, 1.1, "Basamak 1 · Eforsuz regürjitasyon", "Öğün sonrası gözlem; atipikse HRIM-empedans", pm("41713704"), "teal");
	arrow(X + FW / 2, 3.75, 3.95);
	box(X, 3.95, FW, 0.85, "Basamak 2 · Bayrağa göre hedefe yönelik", "Metabolik bayrak → atakta kritik örnek (dekstrozu geciktirmeden) · Ataklar arası üst GİS yakınması → endoskopi · Aralıklı UPJ şüphesi → atak sırasında US", pm("41713704", "26678622", "33224097", "16396871"), "teal");
	arrow(X + FW / 2, 4.8, 5.0);
	box(X, 5.0, FW, 0.6, "Basamak 3 · Bayrak ya da 2 ayda yanıtsızlık (SKS)", "  Tanıyı testlerle destekle", pm("41713704"), "gray");
	arrow(X + FW / 4, 5.6, 5.8);
	arrow(X + 3 * FW / 4, 5.6, 5.8);
	box(X, 5.8, FW / 2 - 0.1, 0.95, "Rome V pozitif tanı", "SKS · ruminasyon · KBS · FD", pm("41713704"), "teal");
	box(X + FW / 2 + 0.1, 5.8, FW / 2 - 0.1, 0.95, "Kronik günlük kusma (ÇIKARIM)", "Rome V pediatrikte karşılığı yok → araştırmayı sürdür", pm("41713704"), "amber");
	srcLine(slide, s, pm("23818085", "2769545", "22642880", "26678622", "33224097", "25957977", "40836301", "8604272", "36056317", "41713704", "16396871"));
}
function kriterSKS() {
	const id = "S30", s = S[id];
	const slide = newSlide("ICERIK", secOf[id]);
	head(slide, s, secOf[id]);
	slide.addText(paras(s.numbered, { fontSize: 17, color: C.text1 }, { bullet: { type: "number" }, paraSpaceAfter: 8 }), {
		x: MX, y: 1.7, w: 6.1, h: 3.2, valign: "top", margin: 0, isTextBox: true, objectName: oid("kriter"),
	});
	slide.addImage({ path: path.join(ROOT, "figures", "fig_cvs_kriter.png"), x: 6.95, y: 1.75, w: 5.78, h: 2.52, altText: "SKS kriter zaman çizelgesi (şematik)", objectName: oid("sekil") });
	slide.addText([
		{ text: `${s.gri_title}: `, options: { fontSize: 14, bold: true, color: C.text2 } },
		...textObjs(s.gri, { fontSize: 14, color: C.text1 }),
	], { shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.1, x: MX, y: 5.05, w: 12.13, h: 1.25, fill: { color: "F1F3F4" }, valign: "top", margin: [6, 12, 6, 12], isTextBox: true, objectName: oid("gri") });
	srcLine(slide, s);
}
function ucSutun() {
	const id = "S31", s = S[id];
	const slide = newSlide("ICERIK", secOf[id]);
	head(slide, s, secOf[id]);
	s.bullets.slice(0, 3).forEach((runs, i) => {
		const x = MX + i * 4.1;
		const header = runs[0].t.replace(/:$/, "");
		const items = splitRuns(runs.slice(1), "; ").map(trimRuns);
		slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y: 1.75, w: 3.85, h: 3.6, rectRadius: 0.12, fill: { color: C.background2 }, line: { type: "none" }, objectName: oid("rome-kart") });
		slide.addText(header, { x: x + 0.25, y: 1.9, w: 3.4, h: 0.5, fontSize: 20, bold: true, color: C.text2, fontFace: THEME.headFontFace, margin: 0, isTextBox: true, objectName: oid("rome-baslik") });
		slide.addText(paras(items, { fontSize: 17, color: C.text1 }, { bullet: { indent: 16 }, paraSpaceAfter: 8 }), { x: x + 0.25, y: 2.45, w: 3.4, h: 2.8, valign: "top", margin: 0, isTextBox: true, objectName: oid("rome-govde") });
	});
	const band = stripPrefix(s.bullets[3], /^Alt şerit:\s*/);
	slide.addText(textObjs(band, { fontSize: 17, color: C.text1 }), {
		shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.1, x: MX, y: 5.5, w: 12.13, h: 0.72, fill: { color: "FDF3DC" }, line: { color: HEX.accent3, width: 1.5, dashType: "dash" },
		valign: "middle", margin: [4, 14, 4, 14], isTextBox: true, objectName: oid("band"),
	});
	dipnot(slide, s, 6.36);
	srcLine(slide, s);
}
function khs() {
	const id = "S32", s = S[id];
	const slide = newSlide("ICERIK", secOf[id]);
	head(slide, s, secOf[id]);
	bulletsBox(slide, s.bullets.slice(0, 2), { w: 12.13, h: 2.0 });
	const parts = splitRuns(s.bullets[2], " · ");
	parts.forEach((runs, i) => {
		const x = MX + i * 4.1;
		const kind = i === 2 ? "slate" : "teal";
		slide.addText(textObjs(trimRuns(runs), { fontSize: 17, bold: true, color: C.background1 }), {
			shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.12, x, y: 4.1, w: 3.85, h: 1.5, fill: { color: kind === "slate" ? C.accent4 : C.text2 },
			align: "center", valign: "middle", margin: 8, isTextBox: true, objectName: oid("siniflama"),
		});
	});
	srcLine(slide, s);
}
function profilaksi() {
	const id = "S35", s = S[id];
	const slide = newSlide("ICERIK", secOf[id]);
	head(slide, s, secOf[id]);
	bulletsBox(slide, s.bullets, { h: 3.6 });
	keyFigure(slide, s, ...KF[id]);
	slide.addText([
		{ text: "Tarihsel · ", options: { fontSize: 15, bold: true, color: C.accent4 } },
		...textObjs(s.gri, { fontSize: 15, color: C.accent4 }),
	], { shape: pres.shapes.ROUNDED_RECTANGLE, rectRadius: 0.1, x: MX, y: 5.45, w: 12.13, h: 0.7, fill: { color: "F1F3F4" }, valign: "middle", margin: [4, 14, 4, 14], isTextBox: true, objectName: oid("tarihsel") });
	srcLine(slide, s);
}
async function mesajlar() {
	const s = S.S41;
	const slide = newSlide("KOYU", "Kapanış");
	slide.addText(s.title, { placeholder: "title" });
	s.numbered.forEach((runs, i) => {
		const y = 1.65 + i * 1.0;
		slide.addText(`${i + 1}`, { shape: pres.shapes.OVAL, x: MX, y, w: 0.72, h: 0.72, fill: { color: C.accent1 }, fontSize: 22, bold: true, color: C.background1, align: "center", valign: "middle", margin: 0, isTextBox: true, objectName: oid("mesaj-no") });
		slide.addText(textObjs(runs, { fontSize: 21, color: C.background1 }), { x: MX + 1.0, y, w: 11.1, h: 0.72, valign: "middle", margin: 0, isTextBox: true, objectName: oid("mesaj") });
	});
}
function kaynaklar() {
	const per = 20, slides = Math.ceil(REFS.length / per);
	for (let k = 0; k < slides; k++) {
		const slide = newSlide("KAYNAK", "Kaynaklar");
		slide.addText(`Kaynaklar (${k + 1}/${slides})`, { placeholder: "title" });
		const chunk = REFS.slice(k * per, (k + 1) * per);
		[chunk.slice(0, per / 2), chunk.slice(per / 2)].forEach((col, ci) => {
			if (!col.length) return;
			const objs = col.map((r, i) => ({ text: `${r.n}. ${r.text}`, options: { fontSize: 10, color: C.text1, paraSpaceAfter: 4, breakLine: i < col.length - 1 } }));
			slide.addText(objs, { x: MX + ci * 6.2, y: 1.05, w: 5.95, h: 5.85, valign: "top", margin: 0, isTextBox: true, objectName: oid("kaynak") });
		});
	}
}
function tesekkur() {
	const slide = newSlide("KOYU", "Kaynaklar");
	slide.addText("Teşekkürler", { placeholder: "title" });
	slide.addText("Sorular ve tartışma", {
		x: MX, y: 1.7, w: 12.13, h: 0.9, fontSize: 24, color: C.accent5, margin: 0, isTextBox: true, objectName: oid("not"),
	});
}

// ---------- akış ----------
(async () => {
	pres.addSection({ title: "Açılış" });
	kapak();
	await yolHaritasi();
	let lastSec = "Açılış";
	const order = SLIDES.map((s) => s.id).filter((i) => /^S\d+$/.test(i));
	for (const id of order) {
		const sec = secOf[id];
		if (!sec) continue;
		if (sec !== lastSec) { pres.addSection({ title: sec }); lastSec = sec; }
		if (id === "S4") sekilSlayt(id, "fig_patern.png");
		else if (id === "S7") yasHaritasi();
		else if (id === "S10") tabloSlayt(id, [8.33, 3.8], { fontSize: 19, rowH: 0.62 });
		else if (id === "S14") {
			const slide = await stdSlide(id); // sağda üç mini-sayı
			[["%50", "SMA sendromunda kusma"], ["57/72", "duplikasyonda ağrı"], ["%73,8", "akalazyada disfaji"]].forEach(([n, c], i) => {
				if (!S[id].bullets.map(plain).join(" ").includes(n)) throw new Error(`S14 sayı yok: ${n}`);
				const y = 1.75 + i * 1.5;
				slide.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 8.75, y, w: 3.98, h: 1.3, rectRadius: 0.1, fill: { color: C.background2 }, line: { type: "none" }, objectName: oid("mini-kart") });
				slide.addText(n, { x: 8.95, y: y + 0.12, w: 1.75, h: 1.05, fontSize: 30, bold: true, color: C.text2, fontFace: THEME.headFontFace, margin: 0, valign: "middle", isTextBox: true, objectName: oid("mini-sayi") });
				slide.addText(c, { x: 10.75, y: y + 0.12, w: 1.85, h: 1.05, fontSize: 14, color: C.text1, margin: 0, valign: "middle", isTextBox: true, objectName: oid("mini-alt") });
			});
		}
		else if (id === "S20") acilDallar();
		else if (id === "S21") tabloSlayt(id, [2.6, 6.05, 3.48], { fontSize: 18, rowH: 0.8 });
		else if (id === "S22") kritikOrnek();
		else if (id === "S26") algoritma();
		else if (id === "S29") tabloSlayt(id, [3.4, 8.73], { fontSize: 18, rowH: 0.7 });
		else if (id === "S30") kriterSKS();
		else if (id === "S31") ucSutun();
		else if (id === "S32") khs();
		else if (id === "S35") profilaksi();
		else if (id === "S40") tabloSlayt(id, [2.4, 3.1, 3.6, 3.03], { fontSize: 18, rowH: 0.68 });
		else if (id === "S41") await mesajlar();
		else await stdSlide(id);
	}
	pres.addSection({ title: "Kaynaklar" });
	kaynaklar();
	tesekkur();
	const out = path.join(ROOT, "output", "KronikKusmaYaklasim.pptx");
	await pres.writeFile({ fileName: out });
	await applyTheme(out, THEME);
	console.log("yazıldı:", out);
})().catch((e) => { console.error(e); process.exit(1); });
