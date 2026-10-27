let klasa = "druid", pkt = {}, aktywnyBuild = -1;

function klucz(t){ return t.tree + "-" + t.row + "-" + t.col; }
function wTrzewku(tree){ let s=0; for(const t of DANE[klasa].t){ if(t.tree===tree) s += (pkt[klucz(t)]||0); } return s; }
function razem(){ let s=0; for(const k in pkt) s += pkt[k]; return s; }
function odblokowany(t){
  if (wTrzewku(t.tree) < 5*(t.row-1)) return false;
  if (t.req && pktReq(t.tree, t.req[0]) < t.req[1]) return false;  // strzalka-prereki
  return true;
}

function rysuj(){
  const box = document.getElementById("drzewka");
  box.innerHTML = "";
  DANE[klasa].trees.forEach((nazwa, i) => {
    const d = document.createElement("div");
    d.className = "drzewko";
    d.innerHTML = '<h2>' + nazwa + '</h2><div class="licz">' + wTrzewku(i) + ' pkt</div>';
    const g = document.createElement("div");
    g.className = "siatka";
    const wRzedzie = {};
    DANE[klasa].t.filter(t => t.tree === i).forEach(t => { wRzedzie[t.row] = Math.max(wRzedzie[t.row]||0, t.col); });
    const maxRow = Math.max(...Object.keys(wRzedzie).map(Number));
    for (let r = 1; r <= maxRow; r++) {
      for (let c = 1; c <= 4; c++) {
        const t = DANE[klasa].t.find(x => x.tree === i && x.row === r && x.col === c);
        const slot = document.createElement("div");
        slot.className = "slot";
        if (t) {
          const p = pkt[klucz(t)] || 0;
          const a = document.createElement("div");
          a.className = "tal" + (p >= t.ranks ? " pelny" : p > 0 ? " wybrany" : odblokowany(t) ? " dostepny" : "");
          a.style.backgroundImage = 'url("talents/icons/' + t.icon + '.png")';
          a.innerHTML = '<span class="rangi">' + p + '/' + t.ranks + '</span>';
          a.onclick = () => zmien(t, 1);
          a.oncontextmenu = e => { e.preventDefault(); zmien(t, -1); };
          a.onmousemove = e => tip(e, t);
          a.onmouseleave = () => document.getElementById("tip").style.display = "none";
          slot.appendChild(a);
        }
        g.appendChild(slot);
      }
    }
    d.appendChild(g);
    box.appendChild(d);
  });
  document.getElementById("wydane").textContent = razem();
  document.getElementById("poziom").textContent = Math.min(60, 9 + razem());
  zapiszUrl();
}

function zmien(t, d){
  const k = klucz(t), p = pkt[k] || 0;
  if (d > 0) {
    if (razem() >= MAX || p >= t.ranks || !odblokowany(t)) return;
    pkt[k] = p + 1;
  } else {
    if (p <= 0) return;
    pkt[k] = p - 1;
    // cofniecie nie moze zostawic wyzszego rzedu bez wymaganych punktow
    for (const x of DANE[klasa].t) {
      if (x.tree === t.tree && (pkt[klucz(x)]||0) > 0 && wTrzewku(x.tree) < 5*(x.row-1)) { pkt[k] = p; return; }
      // nie zdejmuj prereku ponizej progu, jesli zalezny talent (strzalka) jest wziety
      if (x.req && x.req[0] === t.name && x.tree === t.tree && (pkt[klucz(x)]||0) > 0 && (p-1) < x.req[1]) { pkt[k] = p; return; }
    }
  }
  rysuj();
}

// ----- Języki opisu (angielski zawsze na górze, wybrany język pod spodem) -----
const JEZYKI = [
  {code:"En", label:"EN", name:"English",    field:"desc"},
  {code:"Pl", label:"PL", name:"Polski",     field:"descPl"},
  {code:"De", label:"DE", name:"Deutsch",    field:"descDe"},
  {code:"Fr", label:"FR", name:"Français",   field:"descFr"},
  {code:"Es", label:"ES", name:"Español",    field:"descEs"},
  {code:"It", label:"IT", name:"Italiano",   field:"descIt"},
  {code:"Pt", label:"PT", name:"Português",  field:"descPt"},
  {code:"Ru", label:"RU", name:"Русский",    field:"descRu"},
];
let jezyk = "En";
try { jezyk = localStorage.getItem("octoLang") || "En"; } catch(e) {}

function dostepneJezyki(){
  const set = new Set();
  Object.values(DANE).forEach(k => k.t.forEach(t =>
    JEZYKI.forEach(j => { if (t[j.field]) set.add(j.code); })));
  return JEZYKI.filter(j => set.has(j.code));
}
function poleJez(){ const j = JEZYKI.find(x => x.code === jezyk); return j ? j.field : "descPl"; }
function renderLangMenu(){
  const dost = dostepneJezyki();
  if (dost.length && !dost.some(j => j.code === jezyk)) jezyk = dost[0].code;
  const m = document.getElementById("langMenu");
  m.innerHTML = "";
  dost.forEach(j => {
    const o = document.createElement("div");
    o.className = "langOpt" + (j.code === jezyk ? " on" : "");
    o.innerHTML = '<span class="langCode">' + j.label + '</span><span>' + j.name + '</span>';
    o.onclick = () => ustawJezyk(j.code);
    m.appendChild(o);
  });
  const cur = JEZYKI.find(j => j.code === jezyk) || dost[0];
  if (cur){ document.getElementById("curCode").textContent = cur.label;
            document.getElementById("curName").textContent = cur.name; }
  document.getElementById("langSel").style.display = dost.length ? "" : "none";
}
function przelaczMenu(e){ e.stopPropagation(); document.getElementById("langSel").classList.toggle("open"); }
function ustawJezyk(code){
  jezyk = code;
  try { localStorage.setItem("octoLang", code); } catch(e) {}
  document.getElementById("langSel").classList.remove("open");
  renderLangMenu();
  odswiezUI();
  rysuj();
  buildy();
  opisBuildu();
}
document.addEventListener("click", e => {
  const s = document.getElementById("langSel");
  if (s && !s.contains(e.target)) s.classList.remove("open");
});

function tip(e, t){
  const el = document.getElementById("tip");
  const p = pkt[klucz(t)] || 0;
  const enOpis = t.desc || ('<i>' + tr('noDesc') + '</i>');
  const dolny = (jezyk !== "En") ? (t[poleJez()] || "") : "";   // angielski zawsze na górze, wybrany język pod spodem
  el.innerHTML = '<h4>' + t.name + '</h4><div class="meta">' + tr('row') + ' ' + t.row + ' &middot; ' + p + '/' + t.ranks +
                 ' ' + tr('pts') + (odblokowany(t) ? '' :
                   (t.req && pktReq(t.tree, t.req[0]) < t.req[1]
                     ? ' &middot; ' + tr('requires') + ' ' + t.req[0] + ' (' + t.req[1] + '/' + t.req[1] + ')'
                     : ' &middot; ' + tr('requires') + ' ' + (5*(t.row-1)) + ' ' + tr('ptsInTree'))) + '</div>' +
                 '<div class="desc">' + enOpis + '</div>' +
                 (dolny ? '<div class="pl">' + dolny + '</div>' : '');
  el.style.display = "block";
  const x = Math.min(e.clientX + 16, window.innerWidth - 350);
  const y = Math.min(e.clientY + 16, window.innerHeight - el.offsetHeight - 10);
  el.style.left = x + "px"; el.style.top = y + "px";
}

function wyczysc(){ pkt = {}; aktywnyBuild = -1; buildy(); opisBuildu(); rysuj(); }

function zapiszUrl(){
  // Przy otwarciu pliku z dysku (file://) czesc przegladarek blokuje zmiane adresu —
  // wtedy po prostu pomijamy zapis, kalkulator dziala dalej.
  try {
    const s = Object.entries(pkt).filter(([,v]) => v > 0).map(([k,v]) => k + ":" + v).join(",");
    const u = location.pathname + "?k=" + klasa + (s ? "&t=" + s : "");
    history.replaceState(null, "", u);
  } catch(e) {}
}
function czytajUrl(){
  const q = new URLSearchParams(location.search);
  if (q.get("k") && DANE[q.get("k")]) klasa = q.get("k");
  pkt = {};
  (q.get("t") || "").split(",").filter(Boolean).forEach(x => { const [k,v] = x.split(":"); pkt[k] = +v; });
  // jesli rozklad z adresu URL pokrywa sie z gotowym buildem, zaznacz go, zeby pokazac jego opis
  aktywnyBuild = -1;
  const lista = BUILDY[klasa] || [];
  const mam = Object.keys(pkt).filter(k => pkt[k] > 0).sort();
  for (let i = 0; i < lista.length; i++) {
    const bp = {};
    for (const key in lista[i].pkt) {
      const [tr, nazwa] = key.split("|");
      const t = DANE[klasa].t.find(x => x.tree === +tr && x.name === nazwa);
      if (t) bp[klucz(t)] = lista[i].pkt[key];
    }
    const kb = Object.keys(bp).filter(k => bp[k] > 0).sort();
    if (kb.length === mam.length && kb.every((k, j) => k === mam[j] && bp[k] === pkt[k])) { aktywnyBuild = i; break; }
  }
}

function menu(){
  const box = document.getElementById("klasy");
  box.innerHTML = "";
  Object.keys(DANE).forEach(c => {
    const b = document.createElement("button");
    b.className = "klasa" + (c === klasa ? " on" : "");
    b.innerHTML = '<img src="talents/icons/class_' + c + '.png" alt=""> ' + PL[c];
    b.onclick = () => { klasa = c; pkt = {}; aktywnyBuild = -1; menu(); buildy(); rysuj(); };
    box.appendChild(b);
  });
}

function buildy(){
  const el = document.getElementById("buildy");
  const lista = BUILDY[klasa] || [];
  if (!lista.length) {
    el.innerHTML = '<div class="opisB" style="margin-bottom:14px">' + tr('noBuild') + '</div>';
    return;
  }
  el.innerHTML = '<div class="listaB"><span class="etykieta">' + tr('ready') + '</span></div>';
  const row = el.querySelector(".listaB");
  lista.forEach((b, i) => {
    const g = document.createElement("button");
    g.className = "buildBtn" + (i === aktywnyBuild ? " on" : "");
    g.innerHTML = '<img src="talents/icons/' + b.ikona + '.png" alt=""><span>' + b.nazwa +
                  '</span><span class="tag tag-' + b.tryb.toLowerCase() + '">' + b.tryb + '</span>';
    g.onclick = () => { wczytajBuild(i); };
    row.appendChild(g);
  });
}

function wczytajBuild(i){
  const b = BUILDY[klasa][i];
  aktywnyBuild = i;
  pkt = {};
  for (const key in b.pkt) {
    const [tr, nazwa] = key.split("|");
    const t = DANE[klasa].t.find(x => x.tree === +tr && x.name === nazwa);
    if (t) pkt[klucz(t)] = b.pkt[key];
  }
  buildy(); rysuj(); opisBuildu();
}

function opisBuildu(){
  const el = document.getElementById("opisBuildu");
  if (aktywnyBuild < 0) { el.innerHTML = ""; return; }
  const b = BUILDY[klasa][aktywnyBuild];
  const bo = (jezyk === "Pl") ? b.opis : (b.opisEn || b.opis);            // PL po polsku, reszta po angielsku
  const bk = (jezyk === "Pl") ? b.kolejnosc : (b.kolejnoscEn || b.kolejnosc);
  const bu = (jezyk === "Pl") ? b.uwagi : (b.uwagiEn || b.uwagi);
  el.innerHTML = '<div class="opisB"><h3>' + b.nazwa + '</h3><p>' + bo + '</p>'
    + '<h4>' + tr('order') + '</h4><ol>' + bk.map(x => '<li>' + x + '</li>').join("") + '</ol>'
    + (bu.length ? '<h4>' + tr('notes') + '</h4>' + bu.map(x => '<div class="uwaga">' + x + '</div>').join("") : "")
    + '</div>';
}

czytajUrl(); renderLangMenu(); odswiezUI(); menu(); buildy(); rysuj(); opisBuildu();
