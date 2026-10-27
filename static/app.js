let allItems = [];
let itemsById = {};
let equippedItems = {
  head: null,
  neck: null,
  shoulder: null,
  back: null,
  chest: null,
  wrist: null,
  hands: null,
  waist: null,
  legs: null,
  feet: null,
  finger1: null,
  finger2: null,
  trinket1: null,
  trinket2: null,
  main_hand: null,
  off_hand: null,
  relic: null
};

let paladinTrees = ["Holy", "Protection", "Retribution"];
let paladinTalents = [];
let readyBuilds = [];
let pkt = {};
let aktywnyBuild = 0;

const MAX_TALENT_POINTS = 51;

const SLOTS = [
  "head", "neck", "shoulder", "back", "chest", "wrist",
  "hands", "waist", "legs", "feet", "finger1", "finger2",
  "trinket1", "trinket2", "main_hand", "off_hand", "relic"
];

function getQualityColor(quality) {
  switch (quality) {
    case 5: return "var(--q-legendary)";
    case 4: return "var(--q-epic)";
    case 3: return "var(--q-rare)";
    case 2: return "var(--q-uncommon)";
    case 0: return "var(--q-poor)";
    default: return "var(--q-common)";
  }
}

function getSlotSymbol(slotKey) {
  switch (slotKey) {
    case "head": return "👑";
    case "neck": return "📿";
    case "shoulder": return "🛡";
    case "back": return "🧣";
    case "chest": return "🦺";
    case "wrist": return "⛓";
    case "hands": return "🧤";
    case "waist": return "🎗";
    case "legs": return "👖";
    case "feet": return "🥾";
    case "finger1":
    case "finger2": return "💍";
    case "trinket1":
    case "trinket2": return "🔮";
    case "main_hand": return "⚔";
    case "off_hand": return "🛡";
    case "relic": return "📖";
    default: return "📦";
  }
}

function getSlotDisplayTitle(slotKey) {
  switch (slotKey) {
    case "head": return "Head";
    case "neck": return "Neck";
    case "shoulder": return "Shoulders";
    case "back": return "Back";
    case "chest": return "Chest";
    case "wrist": return "Wrists";
    case "hands": return "Hands";
    case "waist": return "Waist";
    case "legs": return "Legs";
    case "feet": return "Feet";
    case "finger1": return "Ring 1";
    case "finger2": return "Ring 2";
    case "trinket1": return "Trinket 1";
    case "trinket2": return "Trinket 2";
    case "main_hand": return "Main Hand";
    case "off_hand": return "Off Hand";
    case "relic": return "Libram";
    default: return slotKey;
  }
}

function filterItemsForSlot(slotKey, query = "") {
  const q = query.trim().toLowerCase();
  return allItems.filter(item => {
    let match = false;
    if (slotKey === "main_hand") {
      match = ["two_hand", "one_hand", "main_hand"].includes(item.slot);
    } else if (slotKey === "off_hand") {
      match = ["off_hand", "shield", "one_hand"].includes(item.slot);
    } else if (slotKey === "finger1" || slotKey === "finger2") {
      match = item.slot === "finger";
    } else if (slotKey === "trinket1" || slotKey === "trinket2") {
      match = item.slot === "trinket";
    } else {
      match = item.slot === slotKey;
    }

    if (!match) return false;
    if (!q) return true;
    return item.name.toLowerCase().includes(q);
  });
}

function determineSlotForItem(item) {
  if (item.slot === "two_hand" || item.slot === "main_hand") return "main_hand";
  if (item.slot === "shield") return "off_hand";
  if (item.slot === "one_hand") {
    if (!equippedItems.main_hand) return "main_hand";
    return "off_hand";
  }
  if (item.slot === "finger") {
    if (!equippedItems.finger1) return "finger1";
    return "finger2";
  }
  if (item.slot === "trinket") {
    if (!equippedItems.trinket1) return "trinket1";
    return "trinket2";
  }
  return item.slot;
}

function getEquippedIds() {
  const ids = [];
  SLOTS.forEach(slotKey => {
    const id = equippedItems[slotKey];
    if (id && id !== 0 && itemsById[String(id)]) {
      ids.push(id);
    }
  });
  return ids;
}

function buildTooltipHtml(item) {
  const color = getQualityColor(item.quality);
  let slotLabel = item.slot.replace("_", " ").toUpperCase();
  if (item.slot === "two_hand") slotLabel = "Two-Hand";
  if (item.slot === "one_hand") slotLabel = "One-Hand";
  if (item.slot === "main_hand") slotLabel = "Main Hand";
  if (item.slot === "off_hand") slotLabel = "Off Hand";

  const sub = item.subclass || "";
  let iconHtml = "";
  if (item.icon) {
    iconHtml = `<img src="https://octowow.st/db/images/icons/medium/${item.icon.toLowerCase()}.jpg" class="tt-icon-img" alt="">`;
  }
  let html = `<div class="tt-icon-name-wrap">${iconHtml}<div class="tt-name" style="color: ${color};">${item.name}</div></div>`;
  html += `<div class="tt-bind">Binds when picked up</div>`;

  if (item.slot === "finger" || item.slot === "trinket" || item.id === 11815 || item.id === 13965) {
    html += `<div class="tt-bind">Unique</div>`;
  }

  html += `<div class="tt-slot-row"><span>${slotLabel}</span><span>${sub}</span></div>`;

  if (item.speed > 0) {
    const minDmg = Math.round(item.min_damage || (item.speed * item.dps * 0.7));
    const maxDmg = Math.round(item.max_damage || (item.speed * item.dps * 1.3));
    html += `<div class="tt-dmg-row"><span>${minDmg} - ${maxDmg} Damage</span><span>Speed ${item.speed.toFixed(2)}</span></div>`;
    html += `<div class="tt-dps-row">(${item.dps.toFixed(1)} damage per second)</div>`;
  }

  if (item.armor > 0) {
    html += `<div class="tt-armor">${item.armor} Armor</div>`;
  }

  if (item.strength > 0) html += `<div class="tt-stat">+${item.strength} Strength</div>`;
  if (item.agility > 0) html += `<div class="tt-stat">+${item.agility} Agility</div>`;
  if (item.stamina > 0) html += `<div class="tt-stat">+${item.stamina} Stamina</div>`;
  if (item.intellect > 0) html += `<div class="tt-stat">+${item.intellect} Intellect</div>`;
  if (item.spirit > 0) html += `<div class="tt-stat">+${item.spirit} Spirit</div>`;

  const reqLvl = item.req_level > 0 ? item.req_level : (item.item_level >= 50 ? 60 : item.item_level);
  html += `<div class="tt-req">Requires Level ${reqLvl}</div>`;

  if (item.ap > 0) {
    html += `<div class="tt-equip">Equip: Increases attack power by ${item.ap}.</div>`;
  }
  if (item.sp > 0) {
    html += `<div class="tt-equip">Equip: Increases damage and healing done by magical spells and effects by up to ${item.sp}.</div>`;
  }
  if (item.healing > 0 && item.sp === 0) {
    html += `<div class="tt-equip">Equip: Increases healing done by spells and effects by up to ${item.healing}.</div>`;
  }
  if (item.crit > 0) {
    html += `<div class="tt-equip">Equip: Improves your chance to get a critical strike by ${item.crit}%.</div>`;
  }
  if (item.hit > 0) {
    html += `<div class="tt-equip">Equip: Improves your chance to hit by ${item.hit}%.</div>`;
  }

  if ([60790, 60799, 60809].includes(item.id)) {
    html += `<div class="tt-set-title">Set of the Lost (0/3)</div>`;
    html += `<div class="tt-equip">(3) Set: Your harmful spells have a 4% chance to summon a Cathedral Minion that casts Soul Bolt for 20 sec.</div>`;
  } else if ([16951, 16952, 16953, 16954, 16955, 16956, 16957, 16958, 47024, 47016, 47022].includes(item.id)) {
    html += `<div class="tt-set-title">The Judgement Armor (0/8)</div>`;
    html += `<div class="tt-equip">(8) Set: Gives each of your weapon attacks and Judgements 3 additional instances of Holy damage.</div>`;
  }

  return html;
}

function positionTooltip(e) {
  const tt = document.getElementById("wow-tooltip");
  if (!tt || tt.style.display !== "block") return;

  const pad = 16;
  let x = e.clientX + pad;
  let y = e.clientY + pad;

  if (x + tt.offsetWidth > window.innerWidth) {
    x = e.clientX - tt.offsetWidth - pad;
  }
  if (y + tt.offsetHeight > window.innerHeight) {
    y = window.innerHeight - tt.offsetHeight - 8;
  }

  tt.style.left = `${Math.max(8, x)}px`;
  tt.style.top = `${Math.max(8, y)}px`;
}

function showItemTooltip(item, e) {
  const tt = document.getElementById("wow-tooltip");
  if (!tt || !item) return;

  tt.innerHTML = buildTooltipHtml(item);
  tt.style.display = "block";
  positionTooltip(e);
}

function hideTooltip() {
  const tt = document.getElementById("wow-tooltip");
  if (tt) tt.style.display = "none";
}

function closeSlotDropdown(slotKey) {
  const dropdown = document.getElementById(`dropdown-${slotKey}`);
  const wrap = document.querySelector(`.combobox-wrap[data-slot="${slotKey}"]`);
  if (dropdown) dropdown.style.display = "none";
  if (wrap) wrap.classList.remove("open");
}

function closeAllSlotDropdowns() {
  SLOTS.forEach(slotKey => closeSlotDropdown(slotKey));
}

function closeGlobalDropdown() {
  const gDropdown = document.getElementById("global-search-dropdown");
  if (gDropdown) gDropdown.style.display = "none";
}

function updateSlotVisual(slotKey) {
  const icon = document.getElementById(`icon-${slotKey}`);
  const input = document.getElementById(`input-${slotKey}`);
  if (!icon) return;

  const itemId = equippedItems[slotKey];
  const item = itemId ? itemsById[String(itemId)] : null;

  for (let q = 0; q <= 5; q++) {
    icon.classList.remove(`quality-${q}`);
  }

  if (item) {
    icon.classList.add(`quality-${item.quality}`);
    if (item.icon) {
      icon.style.backgroundImage = `url("https://octowow.st/db/images/icons/medium/${item.icon.toLowerCase()}.jpg")`;
      icon.classList.add("has-icon");
      icon.textContent = "";
    } else {
      icon.style.backgroundImage = "";
      icon.classList.remove("has-icon");
      icon.textContent = getSlotSymbol(slotKey);
    }
    if (input) {
      input.value = item.name;
      for (let q = 0; q <= 5; q++) {
        input.classList.remove(`q-${q}`);
      }
      input.classList.add(`q-${item.quality}`);
      input.title = item.name;
    }
  } else {
    icon.classList.add("quality-1");
    icon.style.backgroundImage = "";
    icon.classList.remove("has-icon");
    icon.textContent = getSlotSymbol(slotKey);
    if (input) {
      input.value = "";
      for (let q = 0; q <= 5; q++) {
        input.classList.remove(`q-${q}`);
      }
      input.title = "";
    }
  }
}

function equipItem(slotKey, itemId, runSim = true) {
  const item = itemId ? itemsById[String(itemId)] : null;
  if (item) {
    equippedItems[slotKey] = item.id;
  } else {
    equippedItems[slotKey] = null;
  }
  closeSlotDropdown(slotKey);
  updateSlotVisual(slotKey);
  if (runSim) {
    recalculateLiveStats();
    runSimulation();
  }
}

function unequipSlot(slotKey) {
  equipItem(slotKey, null, true);
}

function clearAllGear() {
  SLOTS.forEach(slotKey => {
    equippedItems[slotKey] = null;
    updateSlotVisual(slotKey);
    closeSlotDropdown(slotKey);
  });
  recalculateLiveStats();
  runSimulation();
}

function renderSlotDropdown(slotKey, query = "") {
  closeGlobalDropdown();
  SLOTS.forEach(k => {
    if (k !== slotKey) closeSlotDropdown(k);
  });

  const dropdown = document.getElementById(`dropdown-${slotKey}`);
  const wrap = document.querySelector(`.combobox-wrap[data-slot="${slotKey}"]`);
  if (!dropdown || !wrap) return;

  const filtered = filterItemsForSlot(slotKey, query);
  dropdown.innerHTML = "";

  const emptyOpt = document.createElement("div");
  emptyOpt.className = "combobox-item empty-opt";
  emptyOpt.textContent = `-- None (${getSlotDisplayTitle(slotKey)}) --`;
  emptyOpt.addEventListener("mousedown", (e) => {
    e.preventDefault();
    equipItem(slotKey, null);
  });
  dropdown.appendChild(emptyOpt);

  if (filtered.length === 0) {
    const noMatch = document.createElement("div");
    noMatch.className = "combobox-item empty-opt";
    noMatch.textContent = `No items found matching "${query}"`;
    dropdown.appendChild(noMatch);
  } else {
    const maxItems = 75;
    const slice = filtered.slice(0, maxItems);
    slice.forEach(item => {
      const itemEl = document.createElement("div");
      itemEl.className = `combobox-item q-${item.quality}`;

      const nameCell = document.createElement("div");
      nameCell.className = "item-name-cell";

      if (item.icon) {
        const img = document.createElement("img");
        img.src = `https://octowow.st/db/images/icons/medium/${item.icon.toLowerCase()}.jpg`;
        img.className = "item-opt-icon";
        img.alt = "";
        nameCell.appendChild(img);
      }

      const nameSpan = document.createElement("span");
      nameSpan.textContent = item.name;
      nameCell.appendChild(nameSpan);

      const subSpan = document.createElement("span");
      subSpan.className = "item-subtag";
      subSpan.textContent = `ilvl ${item.item_level}`;

      itemEl.appendChild(nameCell);
      itemEl.appendChild(subSpan);

      itemEl.addEventListener("mouseenter", (e) => showItemTooltip(item, e));
      itemEl.addEventListener("mouseleave", hideTooltip);
      itemEl.addEventListener("mousedown", (e) => {
        e.preventDefault();
        hideTooltip();
        equipItem(slotKey, item.id);
      });

      dropdown.appendChild(itemEl);
    });

    if (filtered.length > maxItems) {
      const countEl = document.createElement("div");
      countEl.className = "combobox-item empty-opt";
      countEl.textContent = `... and ${filtered.length - maxItems} more items (keep typing)`;
      dropdown.appendChild(countEl);
    }
  }

  wrap.classList.add("open");
  dropdown.style.display = "block";
}

function renderGlobalDropdown(query) {
  closeAllSlotDropdowns();
  const gDropdown = document.getElementById("global-search-dropdown");
  if (!gDropdown) return;

  const q = query.trim().toLowerCase();
  if (!q) {
    gDropdown.style.display = "none";
    gDropdown.innerHTML = "";
    return;
  }

  const matches = allItems.filter(item => item.name.toLowerCase().includes(q));
  gDropdown.innerHTML = "";

  if (matches.length === 0) {
    const noEl = document.createElement("div");
    noEl.className = "global-item";
    noEl.style.color = "var(--text-dim)";
    noEl.style.fontStyle = "italic";
    noEl.textContent = `No items found matching "${query}"`;
    gDropdown.appendChild(noEl);
  } else {
    const maxGlobal = 60;
    const slice = matches.slice(0, maxGlobal);
    slice.forEach(item => {
      const targetSlot = determineSlotForItem(item);
      const itemEl = document.createElement("div");
      itemEl.className = "global-item";

      const leftDiv = document.createElement("div");
      leftDiv.className = "global-item-cell";

      const tagSpan = document.createElement("span");
      tagSpan.className = "slot-tag";
      tagSpan.textContent = getSlotDisplayTitle(targetSlot);
      leftDiv.appendChild(tagSpan);

      if (item.icon) {
        const img = document.createElement("img");
        img.src = `https://octowow.st/db/images/icons/medium/${item.icon.toLowerCase()}.jpg`;
        img.className = "item-opt-icon";
        img.alt = "";
        leftDiv.appendChild(img);
      }

      const nameSpan = document.createElement("span");
      nameSpan.className = `q-${item.quality}`;
      nameSpan.textContent = item.name;
      leftDiv.appendChild(nameSpan);

      const subSpan = document.createElement("span");
      subSpan.className = "item-subtag";
      subSpan.textContent = `ilvl ${item.item_level}`;

      itemEl.appendChild(leftDiv);
      itemEl.appendChild(subSpan);

      itemEl.addEventListener("mouseenter", (e) => showItemTooltip(item, e));
      itemEl.addEventListener("mouseleave", hideTooltip);
      itemEl.addEventListener("mousedown", (e) => {
        e.preventDefault();
        hideTooltip();
        equipItem(targetSlot, item.id);
        closeGlobalDropdown();
        document.getElementById("global-search").value = "";
      });

      gDropdown.appendChild(itemEl);
    });

    if (matches.length > maxGlobal) {
      const moreEl = document.createElement("div");
      moreEl.className = "global-item";
      moreEl.style.color = "var(--text-dim)";
      moreEl.style.fontStyle = "italic";
      moreEl.textContent = `... and ${matches.length - maxGlobal} more items (narrow query)`;
      gDropdown.appendChild(moreEl);
    }
  }

  gDropdown.style.display = "block";
}

function klucz(t) {
  return t.tree + "-" + t.row + "-" + t.col;
}

function wTrzewku(tree) {
  let s = 0;
  for (const t of paladinTalents) {
    if (t.tree === tree) s += (pkt[klucz(t)] || 0);
  }
  return s;
}

function razem() {
  let s = 0;
  for (const k in pkt) s += pkt[k];
  return s;
}

function pktReq(tree, reqName) {
  const t = paladinTalents.find(x => x.tree === tree && x.name === reqName);
  return t ? (pkt[klucz(t)] || 0) : 0;
}

function odblokowany(t) {
  if (wTrzewku(t.tree) < 5 * (t.row - 1)) return false;
  if (t.req && pktReq(t.tree, t.req[0]) < t.req[1]) return false;
  return true;
}

function zmienTalent(t, delta) {
  const k = klucz(t);
  const p = pkt[k] || 0;

  if (delta > 0) {
    if (razem() >= MAX_TALENT_POINTS || p >= t.ranks || !odblokowany(t)) return;
    pkt[k] = p + 1;
  } else {
    if (p <= 0) return;
    pkt[k] = p - 1;
    for (const x of paladinTalents) {
      if (x.tree === t.tree && (pkt[klucz(x)] || 0) > 0 && wTrzewku(x.tree) < 5 * (x.row - 1)) {
        pkt[k] = p;
        return;
      }
      if (x.req && x.req[0] === t.name && x.tree === t.tree && (pkt[klucz(x)] || 0) > 0 && (p - 1) < x.req[1]) {
        pkt[k] = p;
        return;
      }
    }
  }

  aktywnyBuild = -1;
  rysujDrzewka();
  renderBuildy();
  renderOpisBuildu();
  recalculateLiveStats();
  runSimulation();
}

function getTalentsAllocatedByName() {
  const map = {};
  for (const t of paladinTalents) {
    const p = pkt[klucz(t)] || 0;
    if (p > 0) {
      map[t.name] = p;
      const snakeKey = t.name.toLowerCase().replace(/[^a-z0-9]+/g, "_");
      map[snakeKey] = p;
    }
  }
  return map;
}

function rysujDrzewka() {
  const box = document.getElementById("drzewka");
  if (!box) return;
  box.innerHTML = "";

  paladinTrees.forEach((nazwa, i) => {
    const d = document.createElement("div");
    d.className = "drzewko";
    d.innerHTML = `<h2>${nazwa}</h2><div class="licz">${wTrzewku(i)} pkt</div>`;

    const g = document.createElement("div");
    g.className = "siatka";

    const treeTalents = paladinTalents.filter(t => t.tree === i);
    let maxRow = 7;
    treeTalents.forEach(t => {
      if (t.row > maxRow) maxRow = t.row;
    });

    for (let r = 1; r <= maxRow; r++) {
      for (let c = 1; c <= 4; c++) {
        const t = treeTalents.find(x => x.row === r && x.col === c);
        const slot = document.createElement("div");
        slot.className = "slot";

        if (t) {
          const p = pkt[klucz(t)] || 0;
          const a = document.createElement("div");
          const isPelny = p >= t.ranks;
          const isWybrany = p > 0 && !isPelny;
          const isDostepny = p === 0 && odblokowany(t) && razem() < MAX_TALENT_POINTS;

          let statusClass = "";
          if (isPelny) statusClass = " pelny";
          else if (isWybrany) statusClass = " wybrany";
          else if (isDostepny) statusClass = " dostepny";

          a.className = "tal" + statusClass;
          a.style.backgroundImage = `url("/static/icons/talents/${t.icon}.png")`;
          a.innerHTML = `<span class="rangi">${p}/${t.ranks}</span>`;

          a.addEventListener("click", () => zmienTalent(t, 1));
          a.addEventListener("contextmenu", (e) => {
            e.preventDefault();
            zmienTalent(t, -1);
          });
          a.addEventListener("mousemove", (e) => tipTalent(e, t));
          a.addEventListener("mouseleave", hideTalentTip);

          slot.appendChild(a);
        }

        g.appendChild(slot);
      }
    }

    d.appendChild(g);
    box.appendChild(d);
  });

  const spent = razem();
  const remaining = Math.max(0, MAX_TALENT_POINTS - spent);

  const wydaneEl = document.getElementById("wydane");
  const poziomEl = document.getElementById("poziom");
  const countTabEl = document.getElementById("tab-talent-count");

  if (wydaneEl) wydaneEl.textContent = spent;
  if (poziomEl) poziomEl.textContent = Math.min(60, 9 + spent);
  if (countTabEl) countTabEl.textContent = remaining;
}

function tipTalent(e, t) {
  const el = document.getElementById("talent-tip");
  if (!el) return;

  const p = pkt[klucz(t)] || 0;
  const enOpis = t.desc || "";
  const dolny = t.descPl || "";
  const treeName = paladinTrees[t.tree];

  let reqText = "";
  if (!odblokowany(t)) {
    if (t.req && pktReq(t.tree, t.req[0]) < t.req[1]) {
      reqText = ` &middot; <span style="color: #ff6666;">Requires ${t.req[0]} (${pktReq(t.tree, t.req[0])}/${t.req[1]})</span>`;
    } else {
      reqText = ` &middot; <span style="color: #ff6666;">Requires ${5 * (t.row - 1)} points in ${treeName}</span>`;
    }
  }

  el.innerHTML = `
    <h4>${t.name}</h4>
    <div class="meta">Row ${t.row} &middot; ${p}/${t.ranks} points${reqText}</div>
    <div class="desc">${enOpis}</div>
    ${dolny ? `<div class="pl">${dolny}</div>` : ""}
    <div style="margin-top: 8px; padding-top: 6px; border-top: 1px solid var(--border-muted); color: var(--text-dim); font-size: 11px;">
      Left-click to learn &middot; Right-click to unlearn
    </div>
  `;

  el.style.display = "block";
  positionTalentTip(e);
}

function positionTalentTip(e) {
  const el = document.getElementById("talent-tip");
  if (!el || el.style.display !== "block") return;

  const pad = 16;
  let x = e.clientX + pad;
  let y = e.clientY + pad;

  if (x + el.offsetWidth > window.innerWidth) {
    x = e.clientX - el.offsetWidth - pad;
  }
  if (y + el.offsetHeight > window.innerHeight) {
    y = window.innerHeight - el.offsetHeight - 10;
  }

  el.style.left = `${Math.max(8, x)}px`;
  el.style.top = `${Math.max(8, y)}px`;
}

function hideTalentTip() {
  const el = document.getElementById("talent-tip");
  if (el) el.style.display = "none";
}

function renderBuildy() {
  const el = document.getElementById("buildy");
  if (!el) return;

  if (!readyBuilds || !readyBuilds.length) {
    el.innerHTML = "";
    return;
  }

  el.innerHTML = `<div class="listaB"><span class="etykieta">Ready builds:</span></div>`;
  const row = el.querySelector(".listaB");

  readyBuilds.forEach((b, i) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "buildBtn" + (i === aktywnyBuild ? " on" : "");
    btn.innerHTML = `
      <img src="/static/icons/talents/${b.ikona}.png" alt="">
      <span>${b.nazwa}</span>
      <span class="tag tag-${(b.tryb || 'pve').toLowerCase()}">${b.tryb || 'PvE'}</span>
    `;
    btn.addEventListener("click", () => wczytajBuild(i));
    row.appendChild(btn);
  });
}

function wczytajBuild(i) {
  if (!readyBuilds[i]) return;
  const b = readyBuilds[i];
  aktywnyBuild = i;
  pkt = {};

  for (const key in b.pkt) {
    const parts = key.split("|");
    const tr = parseInt(parts[0], 10);
    const nazwa = parts[1];
    const t = paladinTalents.find(x => x.tree === tr && x.name === nazwa);
    if (t) {
      pkt[klucz(t)] = b.pkt[key];
    }
  }

  renderBuildy();
  rysujDrzewka();
  renderOpisBuildu();
  recalculateLiveStats();
  runSimulation();
}

function renderOpisBuildu() {
  const el = document.getElementById("opisBuildu");
  if (!el) return;

  if (aktywnyBuild < 0 || !readyBuilds[aktywnyBuild]) {
    el.innerHTML = "";
    return;
  }

  const b = readyBuilds[aktywnyBuild];
  const opisText = b.opisEn || b.opis || "";
  const kol = b.kolejnoscEn || b.kolejnosc || [];
  const uw = b.uwagiEn || b.uwagi || [];

  el.innerHTML = `
    <div class="opisB">
      <h3>${b.nazwa} (${b.tryb || 'PvE'})</h3>
      <p>${opisText}</p>
      ${kol.length ? `<h4>Recommended Order</h4><ol>${kol.map(x => `<li>${x}</li>`).join("")}</ol>` : ""}
      ${uw.length ? `<h4>Notes</h4>${uw.map(x => `<div class="uwaga">${x}</div>`).join("")}` : ""}
    </div>
  `;
}

function resetAllTalents() {
  pkt = {};
  aktywnyBuild = -1;
  renderBuildy();
  rysujDrzewka();
  renderOpisBuildu();
  recalculateLiveStats();
  runSimulation();
}

async function recalculateLiveStats() {
  const equippedIds = getEquippedIds();
  try {
    const res = await fetch("/api/gear_totals", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ equipped_items: equippedIds })
    });
    const totals = await res.json();

    const talents = getTalentsAllocatedByName();
    const dStr = talents["Divine Strength"] || 0;
    const dInt = talents["Divine Intellect"] || 0;
    const kings = talents["Blessing of Kings"] ? 1.10 : 1.0;
    const conv = talents["Conviction"] || 0;
    const prec = talents["Precision"] || 0;

    const effectiveStr = Math.round(totals.strength * (1.0 + (0.02 * dStr)) * kings);
    const effectiveInt = Math.round(totals.intellect * (1.0 + (0.02 * dInt)) * kings);
    const effectiveAgi = Math.round(totals.agility * kings);
    const effectiveSta = Math.round(totals.stamina * kings);

    const totalAp = Math.round((totals.attack_power * kings) + (effectiveStr * 2));
    const totalCrit = (totals.crit + (effectiveAgi / 20.0) + conv).toFixed(1);
    const totalHit = (totals.hit + prec).toFixed(1);
    const spd = totals.main_weapon_speed > 0 ? `${totals.main_weapon_speed.toFixed(2)}s` : "2.00s";

    document.getElementById("stat-speed").textContent = spd;
    document.getElementById("stat-ap").textContent = `${totalAp} AP`;
    document.getElementById("stat-sp").textContent = `${totals.spell_power} SP`;
    document.getElementById("stat-healing").textContent = `${totals.healing} Heal`;
    document.getElementById("stat-crit").textContent = `${totalCrit}%`;
    document.getElementById("stat-hit").textContent = `${totalHit}%`;
    document.getElementById("stat-str").textContent = effectiveStr;
    document.getElementById("stat-agi").textContent = effectiveAgi;
    document.getElementById("stat-sta").textContent = effectiveSta;
    document.getElementById("stat-int").textContent = effectiveInt;
    document.getElementById("stat-armor").textContent = totals.armor;
  } catch (err) {
    console.error(err);
  }
}

async function runSimulation() {
  const btn = document.getElementById("btn-calculate");
  btn.disabled = true;

  const equippedIds = getEquippedIds();
  const payload = {
    equipped_items: equippedIds,
    fight_duration: parseFloat(document.getElementById("cfg-duration").value) || 60.0,
    haste_percent: parseFloat(document.getElementById("cfg-haste").value) || 0.0,
    target_armor: parseFloat(document.getElementById("cfg-armor").value) || 3731.0,
    judgement_interval: parseFloat(document.getElementById("cfg-judge").value) || 10.0,
    exorcism_interval: parseFloat(document.getElementById("cfg-exorcism").value) || 15.0,
    t2_bonus_active: document.getElementById("cfg-t2").checked,
    lost_set_active: document.getElementById("cfg-lost").checked,
    consecration: document.getElementById("cfg-consec").checked,
    talents: getTalentsAllocatedByName()
  };

  try {
    const res = await fetch("/api/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const result = await res.json();
    renderSimulationResults(result);
  } catch (err) {
    console.error(err);
  } finally {
    btn.disabled = false;
  }
}

function renderSimulationResults(data) {
  document.getElementById("res-total-dps").textContent = data.total_dps.toFixed(2);
  document.getElementById("res-total-dmg").textContent = `Total Damage: ${Math.round(data.total_damage).toLocaleString("en-US")}`;
  document.getElementById("res-own-dps").textContent = data.own_dps.toFixed(2);

  const ownSharePct = data.total_dps > 0 ? ((data.own_dps / data.total_dps) * 100).toFixed(1) : 100;
  document.getElementById("res-own-share").textContent = `${ownSharePct}% of total damage`;

  const minionCard = document.getElementById("card-minion-dps");
  const shareBarWrap = document.getElementById("share-bar-wrap");
  const minionBreakdown = document.getElementById("card-minion-breakdown");

  if (data.has_minions && data.minion_dps > 0) {
    minionCard.style.display = "block";
    shareBarWrap.style.display = "block";
    minionBreakdown.style.display = "block";

    document.getElementById("res-minion-dps").textContent = data.minion_dps.toFixed(2);
    document.getElementById("res-minion-range").textContent = `Range: [${data.minion_dps_min.toFixed(2)} - ${data.minion_dps_max.toFixed(2)}]`;

    const minionSharePct = (100 - parseFloat(ownSharePct)).toFixed(1);
    document.getElementById("bar-lbl-own").textContent = `${ownSharePct}%`;
    document.getElementById("bar-lbl-minion").textContent = `${minionSharePct}%`;
    document.getElementById("share-own-bar").style.width = `${ownSharePct}%`;
    document.getElementById("share-minion-bar").style.width = `${minionSharePct}%`;

    document.getElementById("b-active-minions").textContent = data.expected_active_minions.toFixed(2);
    document.getElementById("b-procs-sec").textContent = `${data.procs_per_second.toFixed(3)} / sec`;
  } else {
    minionCard.style.display = "none";
    shareBarWrap.style.display = "none";
    minionBreakdown.style.display = "none";
  }

  document.getElementById("sim-scenario-info").textContent = `Duration: ${data.fight_duration}s | Weapon: ${data.weapon_name} (${data.base_weapon_speed}s) | Swings: ${data.exact_melee_swings}`;

  const b = data.own_damage_breakdown;
  document.getElementById("breakdown-list-own").innerHTML = `
    <div class="b-item"><span>White Melee Swings:</span><strong>${(b.white_melee_dps || 0).toFixed(2)} DPS</strong></div>
    <div class="b-item"><span>Seal of Righteousness:</span><strong>${(b.seal_dps || 0).toFixed(2)} DPS</strong></div>
    <div class="b-item"><span>Judgement of Righteousness:</span><strong>${(b.judgement_dps || 0).toFixed(2)} DPS</strong></div>
    <div class="b-item"><span>Tier 2 Holy (3x Bonus Hits):</span><strong style="color: var(--gold-text);">${(b.t2_holy_dps || 0).toFixed(2)} DPS</strong></div>
    <div class="b-item"><span>Consecration:</span><strong>${(b.consecration_dps || 0).toFixed(2)} DPS</strong></div>
    <div class="b-item"><span>Exorcism:</span><strong>${(b.exorcism_dps || 0).toFixed(2)} DPS</strong></div>
  `;

  document.getElementById("b-exact-swings").textContent = data.exact_melee_swings;
  document.getElementById("b-magic-hits").textContent = data.total_magic_hits;
  document.getElementById("b-magic-rate").textContent = `${data.magic_hits_per_second.toFixed(3)} / sec`;
  document.getElementById("b-sim-crit").textContent = `${data.total_crit_percent.toFixed(1)}%`;
}

function setupEventListeners() {
  window.addEventListener("mousemove", (e) => {
    positionTooltip(e);
    positionTalentTip(e);
  });

  document.querySelectorAll(".nav-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".nav-tab").forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));

      tab.classList.add("active");
      const targetId = `content-${tab.dataset.tab}`;
      const targetContent = document.getElementById(targetId);
      if (targetContent) targetContent.classList.add("active");
    });
  });

  SLOTS.forEach(slotKey => {
    const input = document.getElementById(`input-${slotKey}`);
    const arrowBtn = document.querySelector(`.combobox-arrow[data-slot="${slotKey}"]`);
    const clearBtn = document.querySelector(`.slot-clear[data-clear="${slotKey}"]`);
    const icon = document.getElementById(`icon-${slotKey}`);

    if (input) {
      input.addEventListener("focus", () => {
        input.select();
        renderSlotDropdown(slotKey, "");
      });

      input.addEventListener("input", () => {
        renderSlotDropdown(slotKey, input.value);
      });

      input.addEventListener("click", () => {
        renderSlotDropdown(slotKey, input.value);
      });

      input.addEventListener("mouseenter", (e) => {
        const wrap = document.querySelector(`.combobox-wrap[data-slot="${slotKey}"]`);
        if (wrap && wrap.classList.contains("open")) return;
        const itemId = equippedItems[slotKey];
        const item = itemId ? itemsById[String(itemId)] : null;
        if (item) showItemTooltip(item, e);
      });

      input.addEventListener("mouseleave", hideTooltip);
    }

    if (arrowBtn) {
      arrowBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        const dropdown = document.getElementById(`dropdown-${slotKey}`);
        const isOpen = dropdown && dropdown.style.display === "block";
        if (isOpen) {
          closeSlotDropdown(slotKey);
        } else {
          if (input) input.focus();
          renderSlotDropdown(slotKey, "");
        }
      });
    }

    if (clearBtn) {
      clearBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        unequipSlot(slotKey);
      });
    }

    if (icon) {
      icon.addEventListener("mouseenter", (e) => {
        const itemId = equippedItems[slotKey];
        const item = itemId ? itemsById[String(itemId)] : null;
        if (item) showItemTooltip(item, e);
      });
      icon.addEventListener("mouseleave", hideTooltip);
      icon.addEventListener("click", () => {
        if (input) input.focus();
        renderSlotDropdown(slotKey, "");
      });
    }
  });

  const globalSearch = document.getElementById("global-search");
  const clearSearchBtn = document.getElementById("clear-search-btn");

  if (globalSearch) {
    globalSearch.addEventListener("input", () => {
      renderGlobalDropdown(globalSearch.value);
    });

    globalSearch.addEventListener("focus", () => {
      if (globalSearch.value.trim().length > 0) {
        renderGlobalDropdown(globalSearch.value);
      }
    });
  }

  if (clearSearchBtn) {
    clearSearchBtn.addEventListener("click", () => {
      globalSearch.value = "";
      closeGlobalDropdown();
    });
  }

  document.addEventListener("click", (e) => {
    if (!e.target.closest(".combobox-wrap")) {
      closeAllSlotDropdowns();
    }
    if (!e.target.closest(".search-box")) {
      closeGlobalDropdown();
    }
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeAllSlotDropdowns();
      closeGlobalDropdown();
      hideTooltip();
      hideTalentTip();
    }
  });

  document.getElementById("btn-clear-gear").addEventListener("click", clearAllGear);
  document.getElementById("btn-calculate").addEventListener("click", runSimulation);
  document.getElementById("btn-reset-talents").addEventListener("click", resetAllTalents);

  document.querySelectorAll(".btn-dur").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".btn-dur").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      document.getElementById("cfg-duration").value = btn.dataset.dur;
      runSimulation();
    });
  });

  document.getElementById("cfg-duration").addEventListener("change", e => {
    const val = e.target.value;
    document.querySelectorAll(".btn-dur").forEach(b => {
      b.classList.toggle("active", b.dataset.dur === String(val));
    });
    runSimulation();
  });

  ["cfg-armor", "cfg-haste", "cfg-judge", "cfg-exorcism", "cfg-t2", "cfg-lost", "cfg-consec"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener("change", runSimulation);
  });
}

async function initializeApp() {
  try {
    const [itemsRes, talentsRes] = await Promise.all([
      fetch("/api/items"),
      fetch("/api/paladin_talents")
    ]);

    const itemsData = await itemsRes.json();
    allItems = itemsData.items || [];
    itemsById = {};
    allItems.forEach(it => {
      itemsById[String(it.id)] = it;
    });

    const talentsData = await talentsRes.json();
    paladinTrees = talentsData.trees || ["Holy", "Protection", "Retribution"];
    paladinTalents = talentsData.talents || [];
    readyBuilds = talentsData.builds || [];

    setupEventListeners();

    if (readyBuilds.length > 0) {
      wczytajBuild(0);
    } else {
      rysujDrzewka();
    }

    const starterLoadout = {
      head: 47024,
      neck: 60790,
      shoulder: 16953,
      back: 13340,
      chest: 16958,
      wrist: 16951,
      hands: 60799,
      waist: 16952,
      legs: 47022,
      feet: 16957,
      finger1: 17063,
      finger2: 19397,
      trinket1: 60809,
      trinket2: 11815,
      main_hand: 11684,
      off_hand: 12602,
      relic: 58240
    };

    Object.entries(starterLoadout).forEach(([sKey, sId]) => {
      if (itemsById[String(sId)]) {
        equipItem(sKey, sId, false);
      }
    });

    await recalculateLiveStats();
    await runSimulation();
  } catch (err) {
    console.error("Initialization error:", err);
  }
}

document.addEventListener("DOMContentLoaded", initializeApp);
