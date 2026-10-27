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
  relic: null,
  ranged: null
};

let currentEnchants = {};
let enchantsData = {};
let racesData = {};

let currentTrees = ["Holy", "Protection", "Retribution"];
let currentTalents = [];
let readyBuilds = [];
let pkt = {};
let aktywnyBuild = 0;

const MAX_TALENT_POINTS = 51;

const SLOTS = [
  "head", "neck", "shoulder", "back", "chest", "wrist",
  "hands", "waist", "legs", "feet", "finger1", "finger2",
  "trinket1", "trinket2", "main_hand", "off_hand", "relic", "ranged"
];

let currentClass = "paladin";
let currentRace = "human";
let bossHpPercent = 100.0;
let executePhasePercent = 20.0;
let activeEnchantSlot = null;

function getItemIconUrl(iconName) {
  if (!iconName) return "";
  return `https://octowow.st/db/images/icons/large/${iconName.toLowerCase()}.png`;
}

function getItemIconFallbackUrl(iconName) {
  if (!iconName) return "";
  return `https://wow.zamimg.com/images/wow/icons/large/${iconName.toLowerCase()}.jpg`;
}

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
    case "ranged": return "🏹";
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
    case "ranged": return "Ranged";
    default: return slotKey;
  }
}

function filterItemsForSlot(slotKey, query = "") {
  const q = query.trim().toLowerCase();
  return allItems.filter(item => {
    if (currentClass !== "all") {
      if (Array.isArray(item.classes) && item.classes.length > 0 && !item.classes.includes(currentClass)) {
        return false;
      }
      if (currentClass === "paladin" && ["dagger", "staff", "fist", "gun", "bow", "crossbow", "wand", "thrown"].includes(item.subclass)) {
        return false;
      }
      if (currentClass === "warrior" && ["wand", "relic", "libram"].includes(item.subclass)) {
        return false;
      }
    }

    let match = false;
    if (slotKey === "main_hand") {
      match = ["twohand", "onehand", "mainhand", "two_hand", "one_hand", "main_hand"].includes(item.slot);
    } else if (slotKey === "off_hand") {
      match = ["offhand", "onehand", "shield", "off_hand", "one_hand"].includes(item.slot);
    } else if (slotKey === "finger1" || slotKey === "finger2") {
      match = item.slot === "finger";
    } else if (slotKey === "trinket1" || slotKey === "trinket2") {
      match = item.slot === "trinket";
    } else if (slotKey === "relic") {
      match = item.slot === "relic";
    } else if (slotKey === "ranged") {
      match = item.slot === "ranged";
    } else {
      match = item.slot === slotKey;
    }

    if (!match) return false;
    if (!q) return true;
    return item.name.toLowerCase().includes(q);
  });
}

function determineSlotForItem(item) {
  if (item.slot === "twohand" || item.slot === "mainhand" || item.slot === "two_hand" || item.slot === "main_hand") return "main_hand";
  if (item.slot === "shield") return "off_hand";
  if (item.slot === "onehand" || item.slot === "one_hand") {
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
  if (item.slot === "relic") return "relic";
  if (item.slot === "ranged") return "ranged";
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
  if (item.slot === "twohand" || item.slot === "two_hand") slotLabel = "Two-Hand";
  if (item.slot === "onehand" || item.slot === "one_hand") slotLabel = "One-Hand";
  if (item.slot === "mainhand" || item.slot === "main_hand") slotLabel = "Main Hand";
  if (item.slot === "offhand" || item.slot === "off_hand") slotLabel = "Off Hand";
  if (item.slot === "relic") slotLabel = "Relic";
  if (item.slot === "ranged") slotLabel = "Ranged";

  const sub = item.subclass ? (item.subclass.charAt(0).toUpperCase() + item.subclass.slice(1).replace("_", " ")) : "";
  let iconHtml = "";
  if (item.icon) {
    iconHtml = `<img src="${getItemIconUrl(item.icon)}" onerror="this.onerror=null;this.src='${getItemIconFallbackUrl(item.icon)}';" class="tt-icon-img" alt="">`;
  }
  let html = `<div class="tt-icon-name-wrap">${iconHtml}<div class="tt-name" style="color: ${color};">${item.name}</div></div>`;

  if (item.bonding === 1) {
    html += `<div class="tt-bind">Binds when picked up</div>`;
  } else if (item.bonding === 2) {
    html += `<div class="tt-bind">Binds when equipped</div>`;
  } else if (item.bonding === 3) {
    html += `<div class="tt-bind">Binds when used</div>`;
  }

  if (item.unique) {
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

  const res = item.resistances || {};
  if (res.holy > 0) html += `<div class="tt-stat">+${res.holy} Holy Resistance</div>`;
  if (res.fire > 0) html += `<div class="tt-stat">+${res.fire} Fire Resistance</div>`;
  if (res.nature > 0) html += `<div class="tt-stat">+${res.nature} Nature Resistance</div>`;
  if (res.frost > 0) html += `<div class="tt-stat">+${res.frost} Frost Resistance</div>`;
  if (res.shadow > 0) html += `<div class="tt-stat">+${res.shadow} Shadow Resistance</div>`;
  if (res.arcane > 0) html += `<div class="tt-stat">+${res.arcane} Arcane Resistance</div>`;

  if (item.durability > 0) {
    html += `<div class="tt-durability">Durability ${item.durability} / ${item.durability}</div>`;
  }

  if (item.classes && item.classes.length && item.classes.length < 9) {
    const classStr = item.classes.map(c => c.charAt(0).toUpperCase() + c.slice(1)).join(", ");
    html += `<div class="tt-classes">Classes: ${classStr}</div>`;
  }

  if (item.req_level > 0) {
    html += `<div class="tt-req-level">Requires Level ${item.req_level}</div>`;
  }

  (item.spells || []).forEach(sp => {
    if (sp.text) {
      html += `<div class="tt-equip">${sp.text}</div>`;
    }
  });

  if (item.set) {
    const s = item.set;
    const rawPieces = s.pieces || [];
    const seenPieceNames = new Set();
    const cleanPieces = [];
    rawPieces.forEach(pId => {
      const pItem = itemsById[String(pId)];
      const pName = pItem ? pItem.name : `Item #${pId}`;
      if (!seenPieceNames.has(pName) && cleanPieces.length < 9) {
        seenPieceNames.add(pName);
        cleanPieces.push({ id: pId, name: pName });
      }
    });

    let countEquipped = 0;
    const currentEquippedSet = new Set(getEquippedIds().map(String));
    cleanPieces.forEach(p => {
      if (currentEquippedSet.has(String(p.id))) countEquipped++;
    });

    html += `<div class="tt-set-block">`;
    html += `<div class="tt-set-title">${s.name} (${countEquipped}/${cleanPieces.length})</div>`;
    cleanPieces.forEach(p => {
      const isEquipped = currentEquippedSet.has(String(p.id));
      html += `<div class="tt-set-piece ${isEquipped ? 'equipped' : ''}">${p.name}</div>`;
    });

    (s.bonuses || []).forEach(b => {
      const active = countEquipped >= b.threshold;
      html += `<div class="tt-set-bonus ${active ? 'active' : ''}">${b.text}</div>`;
    });
    html += `</div>`;
  }

  return html;
}

function showItemTooltip(item, e) {
  const tip = document.getElementById("wow-tooltip");
  if (!tip) return;
  tip.innerHTML = buildTooltipHtml(item);
  tip.style.display = "block";
  positionTooltip(e);
}

function positionTooltip(e) {
  const tip = document.getElementById("wow-tooltip");
  if (!tip || tip.style.display !== "block") return;

  const pad = 16;
  let x = e.clientX + pad;
  let y = e.clientY + pad;

  if (x + tip.offsetWidth > window.innerWidth) {
    x = e.clientX - tip.offsetWidth - pad;
  }
  if (y + tip.offsetHeight > window.innerHeight) {
    y = window.innerHeight - tip.offsetHeight - 10;
  }

  tip.style.left = `${Math.max(8, x)}px`;
  tip.style.top = `${Math.max(8, y)}px`;
}

function hideTooltip() {
  const tip = document.getElementById("wow-tooltip");
  if (tip) tip.style.display = "none";
}

function equipItem(slotKey, itemId) {
  const item = itemsById[String(itemId)];
  if (item && currentClass !== "all") {
    if (Array.isArray(item.classes) && item.classes.length > 0 && !item.classes.includes(currentClass)) {
      return;
    }
    if (currentClass === "paladin" && ["dagger", "staff", "fist", "gun", "bow", "crossbow", "wand", "thrown"].includes(item.subclass)) {
      return;
    }
    if (currentClass === "warrior" && ["wand", "relic", "libram"].includes(item.subclass)) {
      return;
    }
  }
  equippedItems[slotKey] = itemId;

  const card = document.querySelector(`.slot-card[data-slot="${slotKey}"]`) ||
    document.querySelector(`.weapon-card[data-slot="${slotKey}"]`) ||
    (slotKey === "relic" || slotKey === "ranged" ? document.getElementById("slot-card-third") : null);

  if (card) {
    const input = card.querySelector(".combobox-input");
    const iconDiv = card.querySelector(".slot-icon");

    if (item) {
      if (input) {
        input.value = item.name;
        input.className = `combobox-input q-${item.quality}`;
      }
      if (iconDiv) {
        iconDiv.className = `slot-icon quality-${item.quality}`;
        if (item.icon) {
          iconDiv.innerHTML = `<img src="${getItemIconUrl(item.icon)}" onerror="this.onerror=null;this.src='${getItemIconFallbackUrl(item.icon)}';" alt="" class="item-loaded-icon">`;
        } else {
          iconDiv.textContent = getSlotSymbol(slotKey);
        }
        iconDiv.onmouseenter = (e) => showItemTooltip(item, e);
        iconDiv.onmousemove = (e) => positionTooltip(e);
        iconDiv.onmouseleave = hideTooltip;
      }
    } else {
      if (input) {
        input.value = "";
        input.className = "combobox-input";
      }
      if (iconDiv) {
        iconDiv.className = "slot-icon quality-1";
        iconDiv.textContent = getSlotSymbol(slotKey);
        iconDiv.onmouseenter = null;
        iconDiv.onmousemove = null;
        iconDiv.onmouseleave = null;
      }
    }
  }

  updateEnchantButtonDisplay(slotKey);
  recalculateLiveStats();
  runSimulation();
}

function clearSlot(slotKey) {
  equipItem(slotKey, null);
  delete currentEnchants[slotKey];
  updateEnchantButtonDisplay(slotKey);
}

function clearAllGear() {
  SLOTS.forEach(slotKey => {
    equippedItems[slotKey] = null;
    delete currentEnchants[slotKey];
    equipItem(slotKey, null);
  });
}

function shortenEnchantName(name) {
  if (!name) return "+ Enchant";
  let s = name.replace(/\s*\(\+?\d+%\s*Hit\)/i, " (+Hit)");
  s = s.replace(/Arcanum of Rapidity/i, "Rapidity (+1% Haste)");
  s = s.replace(/Arcanum of Voracity/i, "Voracity (+8)");
  s = s.replace(/Arcanum of Focus/i, "Focus (+8 SP)");
  s = s.replace(/Greater Stats/i, "+4 Stats");
  s = s.replace(/Superior Agility/i, "+15 Agi");
  s = s.replace(/Superior Strength/i, "+9 Str");
  s = s.replace(/Greater Agility/i, "+7 Agi");
  s = s.replace(/Crusader/i, "Crusader");
  return s;
}

function updateEnchantButtonDisplay(slotKey) {
  const btn = document.querySelector(`.slot-enchant-btn[data-slot="${slotKey}"]`) ||
    (slotKey === "relic" || slotKey === "ranged" ? document.getElementById("btn-ench-third") : null);
  if (!btn) return;

  const enchId = currentEnchants[slotKey];
  if (enchId) {
    let enchObj = null;
    for (const cat in enchantsData) {
      const found = enchantsData[cat].find(e => e.id === enchId);
      if (found) { enchObj = found; break; }
    }
    const label = enchObj ? shortenEnchantName(enchObj.name) : "Enchanted";
    btn.textContent = `✨ ${label}`;
    btn.className = "slot-enchant-btn has-enchant";
    btn.title = enchObj ? `${enchObj.name} (Click to change/remove)` : "Click to change/remove";
  } else {
    btn.textContent = "+ Enchant";
    btn.className = "slot-enchant-btn";
    btn.title = "Select enchant";
  }
}

function openEnchantPicker(slotKey, btnEl) {
  activeEnchantSlot = slotKey;
  let category = slotKey;
  if (slotKey === "main_hand") {
    const mhItem = itemsById[String(equippedItems.main_hand)];
    if (mhItem && (mhItem.slot === "twohand" || mhItem.slot === "two_hand")) {
      category = "twohand";
    } else {
      category = "mainhand";
    }
  } else if (slotKey === "off_hand") {
    category = "offhand";
  } else if (slotKey === "relic" || slotKey === "ranged") {
    category = "ranged";
  } else if (slotKey === "finger1" || slotKey === "finger2") {
    category = "finger";
  } else if (slotKey === "trinket1" || slotKey === "trinket2") {
    category = "trinket";
  }

  renderEnchantPickerList(category, slotKey);

  const popover = document.getElementById("enchant-picker");
  popover.style.display = "flex";
  const titleEl = document.getElementById("ench-picker-title");
  if (titleEl) titleEl.textContent = `Enchant: ${getSlotDisplayTitle(slotKey)}`;

  const rect = btnEl.getBoundingClientRect();
  let left = rect.left + window.scrollX;
  let top = rect.bottom + window.scrollY + 4;
  if (left + 300 > window.innerWidth) {
    left = window.innerWidth - 310;
  }
  popover.style.left = `${Math.max(10, left)}px`;
  popover.style.top = `${top}px`;

  const searchInput = document.getElementById("ench-picker-search");
  if (searchInput) {
    searchInput.value = "";
    searchInput.focus();
  }
}

function renderEnchantPickerList(category, slotKey, filterText = "") {
  const container = document.getElementById("ench-picker-list");
  if (!container) return;
  container.innerHTML = "";

  const list = enchantsData[category] || [];
  const q = filterText.toLowerCase().trim();

  const clearOpt = document.createElement("div");
  clearOpt.className = "ench-clear-option";
  clearOpt.textContent = "✖ Remove Current Enchant";
  clearOpt.addEventListener("click", () => {
    delete currentEnchants[slotKey];
    updateEnchantButtonDisplay(slotKey);
    document.getElementById("enchant-picker").style.display = "none";
    recalculateLiveStats();
    runSimulation();
  });
  container.appendChild(clearOpt);

  const filtered = list.filter(e => !q || e.name.toLowerCase().includes(q));

  if (!filtered.length) {
    const empty = document.createElement("div");
    empty.style.padding = "8px";
    empty.style.color = "var(--text-dim)";
    empty.style.fontStyle = "italic";
    empty.textContent = "No enchants available for this slot.";
    container.appendChild(empty);
    return;
  }

  filtered.forEach(ench => {
    const item = document.createElement("div");
    const isActive = currentEnchants[slotKey] === ench.id;
    item.className = "ench-picker-item" + (isActive ? " active-ench" : "");

    let desc = "";
    if (ench.str) desc += `+${ench.str} Str `;
    if (ench.agi) desc += `+${ench.agi} Agi `;
    if (ench.sta) desc += `+${ench.sta} Sta `;
    if (ench.ap) desc += `+${ench.ap} AP `;
    if (ench.crit) desc += `+${ench.crit}% Crit `;
    if (ench.hit) desc += `+${ench.hit}% Hit `;
    if (ench.haste) desc += `+${ench.haste}% Haste `;
    if (ench.bonusdmg) desc += `+${ench.bonusdmg} Dmg `;
    if (ench.ppm) desc += `${ench.ppm} PPM Proc `;
    if (ench.magicdmg) desc += `+${ench.magicdmg} Magic Dmg `;

    item.innerHTML = `
      <div style="font-weight: 600;">${ench.name}</div>
      ${desc ? `<div class="ench-item-desc">${desc}</div>` : ""}
    `;

    item.addEventListener("click", () => {
      currentEnchants[slotKey] = ench.id;
      updateEnchantButtonDisplay(slotKey);
      document.getElementById("enchant-picker").style.display = "none";
      recalculateLiveStats();
      runSimulation();
    });

    container.appendChild(item);
  });
}

function openDropdownForSlot(slotKey) {
  closeAllDropdowns();
  const dropdown = document.getElementById(`dropdown-${slotKey}`) ||
    (slotKey === "relic" || slotKey === "ranged" ? document.getElementById("dropdown-third") : null);
  const input = document.getElementById(`input-${slotKey}`) ||
    (slotKey === "relic" || slotKey === "ranged" ? document.getElementById("input-third") : null);
  if (!dropdown || !input) return;

  const query = input.value.trim();
  const matches = filterItemsForSlot(slotKey, query);
  renderDropdownItems(dropdown, slotKey, matches);
  dropdown.style.display = "block";
}

function renderDropdownItems(dropdown, slotKey, items) {
  dropdown.innerHTML = "";
  if (items.length === 0) {
    const noEl = document.createElement("div");
    noEl.className = "combobox-item";
    noEl.style.color = "var(--text-dim)";
    noEl.style.fontStyle = "italic";
    noEl.textContent = "No matching items";
    dropdown.appendChild(noEl);
    return;
  }

  const maxItems = 40;
  const slice = items.slice(0, maxItems);
  slice.forEach(item => {
    const itemEl = document.createElement("div");
    itemEl.className = "combobox-item";

    const leftDiv = document.createElement("div");
    leftDiv.className = "combobox-item-left";

    if (item.icon) {
      const img = document.createElement("img");
      img.src = getItemIconUrl(item.icon);
      img.onerror = function() {
        this.onerror = null;
        this.src = getItemIconFallbackUrl(item.icon);
      };
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
    if (item.set && item.set.name) {
      subSpan.textContent = `ilvl ${item.item_level} · ${item.set.name}`;
    } else {
      subSpan.textContent = `ilvl ${item.item_level}`;
    }

    itemEl.appendChild(leftDiv);
    itemEl.appendChild(subSpan);

    itemEl.addEventListener("mouseenter", (e) => showItemTooltip(item, e));
    itemEl.addEventListener("mouseleave", hideTooltip);
    itemEl.addEventListener("mousedown", (e) => {
      e.preventDefault();
      hideTooltip();
      equipItem(slotKey, item.id);
      closeAllDropdowns();
    });

    dropdown.appendChild(itemEl);
  });

  if (items.length > maxItems) {
    const moreEl = document.createElement("div");
    moreEl.className = "combobox-item";
    moreEl.style.color = "var(--text-dim)";
    moreEl.style.fontStyle = "italic";
    moreEl.textContent = `... and ${items.length - maxItems} more items (keep typing)`;
    dropdown.appendChild(moreEl);
  }
}

function closeAllDropdowns() {
  document.querySelectorAll(".combobox-dropdown").forEach(dd => {
    dd.style.display = "none";
  });
}

function closeGlobalDropdown() {
  const g = document.getElementById("global-search-dropdown");
  if (g) g.style.display = "none";
}

function handleGlobalSearch(query) {
  const gDropdown = document.getElementById("global-search-dropdown");
  if (!gDropdown) return;
  const q = query.trim().toLowerCase();
  if (!q) {
    gDropdown.style.display = "none";
    return;
  }

  const matches = allItems.filter(it => it.name.toLowerCase().includes(q));
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
        img.src = getItemIconUrl(item.icon);
        img.onerror = function() {
          this.onerror = null;
          this.src = getItemIconFallbackUrl(item.icon);
        };
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
        const gs = document.getElementById("global-search");
        if (gs) gs.value = "";
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
  for (const t of currentTalents) {
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
  const t = currentTalents.find(x => x.tree === tree && x.name === reqName);
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
    for (const x of currentTalents) {
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
  for (const t of currentTalents) {
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

  currentTrees.forEach((nazwa, i) => {
    const d = document.createElement("div");
    d.className = "drzewko";
    d.innerHTML = `<h2>${nazwa}</h2><div class="licz">${wTrzewku(i)} pkt</div>`;

    const g = document.createElement("div");
    g.className = "siatka";

    const treeTalents = currentTalents.filter(t => t.tree === i);
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
          const cleanIcon = t.icon.toLowerCase().replace(/\.png$/, "").replace(/\.jpg$/, "");
          a.style.backgroundImage = `url("/static/icons/talents/${cleanIcon}.png")`;
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
  const treeName = currentTrees[t.tree];

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
    const cleanIcon = (b.ikona || "inv_misc_questionmark").toLowerCase().replace(/\.png$/, "").replace(/\.jpg$/, "");
    btn.innerHTML = `
      <img src="/static/icons/talents/${cleanIcon}.png" alt="">
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

  for (const k in b.pkt) {
    const [treeStr, tName] = k.split("|");
    const treeIdx = parseInt(treeStr, 10);
    const tal = currentTalents.find(t => t.tree === treeIdx && t.name === tName);
    if (tal) {
      pkt[klucz(tal)] = b.pkt[k];
    }
  }

  rysujDrzewka();
  renderBuildy();
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
  const opis = b.opisEn || b.opis || "";
  const kol = b.kolejnoscEn || b.kolejnosc || [];
  const uw = b.uwagiEn || b.uwagi || [];

  let html = `
    <div class="boxOpis">
      <h3>${b.nazwa}</h3>
      <p class="wstep">${opis}</p>
  `;

  if (kol.length > 0) {
    html += `<h4>Leveling order</h4><ol class="kroki">`;
    kol.forEach(k => { html += `<li>${k}</li>`; });
    html += `</ol>`;
  }

  if (uw.length > 0) {
    html += `<h4>Build notes</h4><ul class="uwagi">`;
    uw.forEach(u => { html += `<li>${u}</li>`; });
    html += `</ul>`;
  }

  html += `</div>`;
  el.innerHTML = html;
}

function recalculateLiveStats() {
  const equippedIds = getEquippedIds();
  const payload = {
    equipped_items: equippedIds,
    enchants: currentEnchants,
    race: currentRace,
    character_class: currentClass
  };

  fetch("/api/gear_totals", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  })
  .then(res => res.json())
  .then(totals => {
    updateStatsDisplay(totals);
  })
  .catch(err => {
    console.error("Failed to calculate gear totals:", err);
  });
}

function updateStatsDisplay(totals) {
  const speed = totals.main_weapon_speed > 0 ? totals.main_weapon_speed.toFixed(2) : "2.00";
  document.getElementById("stat-speed").textContent = `${speed}s`;
  document.getElementById("stat-ap").textContent = `${totals.total_attack_power || totals.attack_power || 0} AP`;
  document.getElementById("stat-sp").textContent = `${totals.spell_power || 0} SP`;
  document.getElementById("stat-healing").textContent = `${totals.healing || 0} Heal`;
  document.getElementById("stat-crit").textContent = `${(totals.total_melee_crit || totals.crit || 0).toFixed(1)}%`;
  document.getElementById("stat-hit").textContent = `${(totals.hit || 0).toFixed(1)}%`;
  document.getElementById("stat-str").textContent = totals.strength || 0;
  document.getElementById("stat-agi").textContent = totals.agility || 0;
  document.getElementById("stat-sta").textContent = totals.stamina || 0;
  document.getElementById("stat-int").textContent = totals.intellect || 0;
  document.getElementById("stat-armor").textContent = totals.armor || 0;
}

function runSimulation() {
  const equippedIds = getEquippedIds();
  const durationInput = document.getElementById("cfg-duration");
  const duration = durationInput ? parseFloat(durationInput.value) || 60 : 60;
  const haste = parseFloat(document.getElementById("cfg-haste")?.value || 0);
  const armor = parseFloat(document.getElementById("cfg-armor")?.value || 3731);
  const judge = parseFloat(document.getElementById("cfg-judge")?.value || 10);
  const consec = document.getElementById("cfg-consec")?.checked ?? true;
  const exorcism = parseFloat(document.getElementById("cfg-exorcism")?.value || 15);
  const allocatedTalents = getTalentsAllocatedByName();

  const payload = {
    equipped_items: equippedIds,
    fight_duration: duration,
    haste_percent: haste,
    target_armor: armor,
    judgement_interval: judge,
    consecration: consec,
    exorcism_interval: exorcism,
    character_class: currentClass,
    talents: allocatedTalents,
    boss_hp_percent: bossHpPercent,
    execute_phase_percent: executePhasePercent,
    race: currentRace,
    enchants: currentEnchants
  };

  fetch("/api/simulate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  })
  .then(res => res.json())
  .then(result => {
    renderSimulationResults(result);
  })
  .catch(err => {
    console.error("Simulation request failed:", err);
  });
}

function renderSimulationResults(data) {
  document.getElementById("res-total-dps").textContent = data.total_dps ? data.total_dps.toFixed(2) : "0.00";
  document.getElementById("res-total-dmg").textContent = `Total Damage: ${Math.round(data.total_damage || 0).toLocaleString()}`;
  document.getElementById("res-own-dps").textContent = data.own_dps ? data.own_dps.toFixed(2) : "0.00";

  const totalDps = data.total_dps || 1;
  const ownShare = Math.round(((data.own_dps || 0) / totalDps) * 100);
  const minionShare = 100 - ownShare;

  document.getElementById("res-own-share").textContent = `${ownShare}% of total damage`;

  const infoEl = document.getElementById("sim-scenario-info");
  if (infoEl) {
    const isDw = data.is_dual_wield ? " (DW)" : (data.is_two_handed ? " (2H)" : "");
    infoEl.textContent = `Duration: ${data.fight_duration}s | ${data.character_class.toUpperCase()}${isDw} (${data.race}) | Boss HP: ${data.boss_hp_percent}% | Execute: ${data.execute_duration_seconds}s`;
  }

  const minionCard = document.getElementById("card-minion-dps");
  const minionBreakdownCard = document.getElementById("card-minion-breakdown");
  const shareBarWrap = document.getElementById("share-bar-wrap");

  if (data.has_minions && data.minion_dps > 0) {
    if (minionCard) minionCard.style.display = "block";
    if (minionBreakdownCard) minionBreakdownCard.style.display = "block";
    if (shareBarWrap) shareBarWrap.style.display = "block";

    document.getElementById("res-minion-dps").textContent = data.minion_dps.toFixed(2);
    document.getElementById("res-minion-range").textContent = `Range: [${data.minion_dps_min.toFixed(2)} - ${data.minion_dps_max.toFixed(2)}]`;
    document.getElementById("bar-lbl-own").textContent = `${ownShare}%`;
    document.getElementById("bar-lbl-minion").textContent = `${minionShare}%`;
    document.getElementById("share-own-bar").style.width = `${ownShare}%`;
    document.getElementById("share-minion-bar").style.width = `${minionShare}%`;
    document.getElementById("b-active-minions").textContent = data.expected_active_minions.toFixed(2);
  } else {
    if (minionCard) minionCard.style.display = "none";
    if (minionBreakdownCard) minionBreakdownCard.style.display = "none";
    if (shareBarWrap) shareBarWrap.style.display = "none";
  }

  const breakdownTitle = document.getElementById("breakdown-title");
  if (breakdownTitle) {
    breakdownTitle.innerHTML = `&#9876; ${data.character_class.toUpperCase()} ATTACK BREAKDOWN`;
  }

  const breakdownContainer = document.getElementById("breakdown-list-own");
  if (breakdownContainer) {
    breakdownContainer.innerHTML = "";
    const bd = data.own_damage_breakdown || {};

    const labelMap = {
      white_melee_dps: "White Auto-Attacks",
      bloodthirst_dps: "Bloodthirst (Instant)",
      mortal_strike_dps: "Mortal Strike (Instant)",
      whirlwind_dps: "Whirlwind (Cleave)",
      heroic_strike_dps: "Heroic Strike (Queued)",
      execute_dps: "Execute (<20% Phase)",
      deep_wounds_bleed_dps: "Deep Wounds (Bleed)",
      seal_dps: "Seal of Righteousness",
      judgement_dps: "Judgement of Righteousness",
      consecration_dps: "Consecration (Holy Tick)",
      exorcism_dps: "Exorcism",
      hammer_of_wrath_dps: "Hammer of Wrath (<20% Execute)",
      judgement_8set_holy_dps: "T2 8-Piece Holy Shock Proc",
      judgement_3set_holy_dps: "Judgement 3-Piece Holy Damage",
      judgement_8set_smite_dps: "Judgement 8-Piece Smite Proc",
      lawbringer_8set_holy_dps: "Lawbringer 8-Piece Holy Radiance"
    };

    for (const [key, dpsVal] of Object.entries(bd)) {
      if (dpsVal <= 0) continue;
      const row = document.createElement("div");
      row.className = "b-item";
      const lbl = labelMap[key] || key.replace(/_/g, " ").replace("dps", "DPS");
      const share = data.own_dps > 0 ? Math.round((dpsVal / data.own_dps) * 100) : 0;
      row.innerHTML = `<span>${lbl}:</span><strong>${dpsVal.toFixed(2)} DPS <span class="share-tag">${share}%</span></strong>`;
      breakdownContainer.appendChild(row);
    }
  }

  const bSwings = document.getElementById("b-exact-swings");
  if (bSwings) bSwings.textContent = data.exact_melee_swings || 0;

  const bSkill = document.getElementById("b-weapon-skill");
  if (bSkill) bSkill.textContent = data.weapon_skill || 300;

  const rowFlurry = document.getElementById("stat-row-flurry");
  const bFlurry = document.getElementById("b-flurry-uptime");
  if (rowFlurry && bFlurry) {
    if (data.character_class === "warrior") {
      rowFlurry.style.display = "flex";
      bFlurry.textContent = `${data.flurry_uptime_percent || 0.0}%`;
    } else {
      rowFlurry.style.display = "none";
    }
  }

  const rowMagic = document.getElementById("stat-row-magic");
  const bMagicHits = document.getElementById("b-magic-hits");
  if (rowMagic && bMagicHits) {
    if (data.character_class === "paladin") {
      rowMagic.style.display = "flex";
      bMagicHits.textContent = data.total_magic_hits || 0;
    } else {
      rowMagic.style.display = "none";
    }
  }

  const bArmorReduc = document.getElementById("b-armor-reduc");
  if (bArmorReduc) {
    const targetArmor = parseFloat(document.getElementById("cfg-armor")?.value || 3731);
    const reduction = (targetArmor / (targetArmor + 5500)) * 100;
    bArmorReduc.textContent = `${reduction.toFixed(1)}%`;
  }

  const bSimCrit = document.getElementById("b-sim-crit");
  if (bSimCrit) bSimCrit.textContent = `${(data.total_crit_percent || 0).toFixed(1)}%`;
}

function loadRacesForClass(cls) {
  const races = racesData[cls] || [];
  const sel = document.getElementById("race-select");
  if (!sel) return;
  sel.innerHTML = "";
  races.forEach(r => {
    const opt = document.createElement("option");
    opt.value = r.id;
    opt.textContent = `${r.name} (${r.racial_text.split(",")[0]})`;
    sel.appendChild(opt);
  });
  if (races.length > 0) {
    currentRace = races[0].id;
    sel.value = currentRace;
  }
}

function loadTalentsForClass(cls) {
  fetch(`/api/talents?class=${cls}`)
    .then(res => res.json())
    .then(data => {
      currentTrees = data.trees || [];
      currentTalents = data.talents || [];
      readyBuilds = data.builds || [];
      pkt = {};
      aktywnyBuild = 0;

      if (readyBuilds.length > 0) {
        wczytajBuild(0);
      } else {
        rysujDrzewka();
        renderBuildy();
        renderOpisBuildu();
      }
    })
    .catch(err => {
      console.error("Failed to load talents:", err);
    });
}

function switchClass(newClass) {
  currentClass = newClass.toLowerCase().trim();

  const crestTitle = document.getElementById("crest-title");
  const crestIcon = document.getElementById("crest-icon");
  const crestSub = document.getElementById("crest-sub");
  if (crestTitle) crestTitle.textContent = currentClass.toUpperCase();
  if (crestIcon) crestIcon.innerHTML = currentClass === "warrior" ? "⚔" : "&#9876;";
  if (crestSub) crestSub.textContent = `Level 60 ${currentClass.charAt(0).toUpperCase() + currentClass.slice(1)} Sheet`;

  const thirdSlotCard = document.getElementById("slot-card-third");
  const thirdSlotTitle = document.getElementById("third-slot-title");
  const thirdInput = document.getElementById("input-third");
  const thirdIcon = document.getElementById("icon-third");

  if (thirdSlotCard && thirdSlotTitle && thirdInput) {
    if (currentClass === "warrior") {
      thirdSlotCard.setAttribute("data-slot", "ranged");
      thirdSlotTitle.textContent = "Ranged Weapon";
      thirdInput.setAttribute("data-slot", "ranged");
      thirdInput.placeholder = "Search bows, guns, crossbows...";
      if (thirdIcon) thirdIcon.textContent = getSlotSymbol("ranged");
    } else {
      thirdSlotCard.setAttribute("data-slot", "relic");
      thirdSlotTitle.textContent = "Libram / Relic";
      thirdInput.setAttribute("data-slot", "relic");
      thirdInput.placeholder = "Search librams...";
      if (thirdIcon) thirdIcon.textContent = getSlotSymbol("relic");
    }
  }

  const judgeItem = document.getElementById("setting-judge-item");
  const exoItem = document.getElementById("setting-exorcism-item");
  const palChecks = document.getElementById("setting-paladin-checks");
  if (judgeItem) judgeItem.style.display = currentClass === "paladin" ? "flex" : "none";
  if (exoItem) exoItem.style.display = currentClass === "paladin" ? "flex" : "none";
  if (palChecks) palChecks.style.display = currentClass === "paladin" ? "flex" : "none";

  loadRacesForClass(currentClass);
  loadTalentsForClass(currentClass);

  fetch(`/api/items?class=${currentClass}`)
    .then(res => res.json())
    .then(data => {
      allItems = data.items || [];
      itemsById = {};
      allItems.forEach(it => { itemsById[String(it.id)] = it; });
      SLOTS.forEach(slotKey => {
        const id = equippedItems[slotKey];
        if (id) {
          const it = itemsById[String(id)];
          if (!it || (currentClass !== "all" && Array.isArray(it.classes) && it.classes.length > 0 && !it.classes.includes(currentClass))) {
            unequipItem(slotKey);
          } else if (currentClass === "paladin" && ["dagger", "staff", "fist", "gun", "bow", "crossbow", "wand", "thrown"].includes(it.subclass)) {
            unequipItem(slotKey);
          } else if (currentClass === "warrior" && ["wand", "relic", "libram"].includes(it.subclass)) {
            unequipItem(slotKey);
          }
        }
      });
      recalculateLiveStats();
      runSimulation();
    })
    .catch(err => {
      console.error("Failed to fetch class items:", err);
    });
}

document.addEventListener("DOMContentLoaded", () => {
  fetch("/api/races")
    .then(res => res.json())
    .then(data => {
      racesData = data;
      loadRacesForClass(currentClass);
    });

  fetch("/api/enchants")
    .then(res => res.json())
    .then(data => {
      enchantsData = data;
    });

  fetch(`/api/items?class=${currentClass}`)
    .then(res => res.json())
    .then(data => {
      allItems = data.items || [];
      itemsById = {};
      allItems.forEach(it => { itemsById[String(it.id)] = it; });
    });

  loadTalentsForClass(currentClass);

  const raceSelect = document.getElementById("race-select");
  if (raceSelect) {
    raceSelect.addEventListener("change", (e) => {
      currentRace = e.target.value;
      recalculateLiveStats();
      runSimulation();
    });
  }

  const classSelect = document.getElementById("class-select");
  if (classSelect) {
    classSelect.addEventListener("change", (e) => {
      switchClass(e.target.value);
    });
  }

  document.querySelectorAll(".nav-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".nav-tab").forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
      tab.classList.add("active");
      const targetId = `content-${tab.dataset.tab}`;
      const content = document.getElementById(targetId);
      if (content) content.classList.add("active");
    });
  });

  document.querySelectorAll(".slot-card, .weapon-card").forEach(card => {
    const slotKey = card.getAttribute("data-slot");
    const input = card.querySelector(".combobox-input");
    const arrow = card.querySelector(".combobox-arrow");

    if (input) {
      input.addEventListener("focus", () => {
        const curSlot = card.getAttribute("data-slot") || slotKey;
        openDropdownForSlot(curSlot);
      });
      input.addEventListener("input", (e) => {
        const curSlot = card.getAttribute("data-slot") || slotKey;
        const matches = filterItemsForSlot(curSlot, e.target.value);
        const dropdown = card.querySelector(".combobox-dropdown");
        if (dropdown) {
          renderDropdownItems(dropdown, curSlot, matches);
          dropdown.style.display = "block";
        }
      });
    }

    if (arrow) {
      arrow.addEventListener("click", (e) => {
        e.stopPropagation();
        const curSlot = card.getAttribute("data-slot") || slotKey;
        const dropdown = card.querySelector(".combobox-dropdown");
        if (dropdown && dropdown.style.display === "block") {
          dropdown.style.display = "none";
        } else {
          openDropdownForSlot(curSlot);
        }
      });
    }

    const enchBtn = card.querySelector(".slot-enchant-btn");
    if (enchBtn) {
      enchBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        const curSlot = card.getAttribute("data-slot") || slotKey;
        openEnchantPicker(curSlot, enchBtn);
      });
    }
  });

  document.querySelectorAll(".slot-clear").forEach(btn => {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const parentCard = btn.closest(".slot-card, .weapon-card");
      const slotKey = parentCard ? parentCard.getAttribute("data-slot") : btn.getAttribute("data-clear");
      clearSlot(slotKey);
    });
  });

  const btnEnchThird = document.getElementById("btn-ench-third");
  if (btnEnchThird) {
    btnEnchThird.addEventListener("click", (e) => {
      e.stopPropagation();
      const thirdCard = document.getElementById("slot-card-third");
      const curSlot = thirdCard ? thirdCard.getAttribute("data-slot") : "relic";
      openEnchantPicker(curSlot, btnEnchThird);
    });
  }

  const btnClearThird = document.getElementById("btn-clear-third");
  if (btnClearThird) {
    btnClearThird.addEventListener("click", (e) => {
      e.stopPropagation();
      const thirdCard = document.getElementById("slot-card-third");
      const curSlot = thirdCard ? thirdCard.getAttribute("data-slot") : "relic";
      clearSlot(curSlot);
    });
  }

  const enchPickerClose = document.getElementById("ench-picker-close");
  if (enchPickerClose) {
    enchPickerClose.addEventListener("click", () => {
      document.getElementById("enchant-picker").style.display = "none";
    });
  }

  const enchPickerSearch = document.getElementById("ench-picker-search");
  if (enchPickerSearch) {
    enchPickerSearch.addEventListener("input", (e) => {
      if (!activeEnchantSlot) return;
      let category = activeEnchantSlot;
      if (activeEnchantSlot === "main_hand") {
        const mhItem = itemsById[String(equippedItems.main_hand)];
        category = (mhItem && (mhItem.slot === "twohand" || mhItem.slot === "two_hand")) ? "twohand" : "mainhand";
      } else if (activeEnchantSlot === "off_hand") {
        category = "offhand";
      } else if (activeEnchantSlot === "relic" || activeEnchantSlot === "ranged") {
        category = "ranged";
      }
      renderEnchantPickerList(category, activeEnchantSlot, e.target.value);
    });
  }

  const globalSearch = document.getElementById("global-search");
  if (globalSearch) {
    globalSearch.addEventListener("input", (e) => {
      handleGlobalSearch(e.target.value);
    });
    globalSearch.addEventListener("focus", (e) => {
      if (e.target.value.trim()) handleGlobalSearch(e.target.value);
    });
  }

  const clearSearchBtn = document.getElementById("clear-search-btn");
  if (clearSearchBtn) {
    clearSearchBtn.addEventListener("click", () => {
      if (globalSearch) globalSearch.value = "";
      closeGlobalDropdown();
    });
  }

  const btnClearGear = document.getElementById("btn-clear-gear");
  if (btnClearGear) {
    btnClearGear.addEventListener("click", clearAllGear);
  }

  const btnResetTalents = document.getElementById("btn-reset-talents");
  if (btnResetTalents) {
    btnResetTalents.addEventListener("click", () => {
      pkt = {};
      aktywnyBuild = -1;
      rysujDrzewka();
      renderBuildy();
      renderOpisBuildu();
      recalculateLiveStats();
      runSimulation();
    });
  }

  const btnCalculate = document.getElementById("btn-calculate");
  if (btnCalculate) {
    btnCalculate.addEventListener("click", () => {
      recalculateLiveStats();
      runSimulation();
    });
  }

  document.querySelectorAll(".btn-dur").forEach(btn => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".btn-dur").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const d = btn.getAttribute("data-dur");
      const input = document.getElementById("cfg-duration");
      if (input) input.value = d;
      runSimulation();
    });
  });

  const durationInput = document.getElementById("cfg-duration");
  if (durationInput) {
    durationInput.addEventListener("change", () => {
      document.querySelectorAll(".btn-dur").forEach(b => {
        b.classList.toggle("active", b.getAttribute("data-dur") === durationInput.value);
      });
      runSimulation();
    });
  }

  const quickHpInput = document.getElementById("cfg-boss-hp-quick");
  const settingsHpInput = document.getElementById("cfg-boss-hp-settings");
  const btnToggleExec = document.getElementById("btn-toggle-exec");

  if (quickHpInput) {
    quickHpInput.addEventListener("change", () => {
      bossHpPercent = Math.max(1, Math.min(100, parseFloat(quickHpInput.value) || 100));
      quickHpInput.value = bossHpPercent;
      if (settingsHpInput) settingsHpInput.value = bossHpPercent;
      if (btnToggleExec) btnToggleExec.classList.toggle("active", bossHpPercent <= 20);
      runSimulation();
    });
  }

  if (settingsHpInput) {
    settingsHpInput.addEventListener("change", () => {
      bossHpPercent = Math.max(1, Math.min(100, parseFloat(settingsHpInput.value) || 100));
      settingsHpInput.value = bossHpPercent;
      if (quickHpInput) quickHpInput.value = bossHpPercent;
      if (btnToggleExec) btnToggleExec.classList.toggle("active", bossHpPercent <= 20);
      runSimulation();
    });
  }

  if (btnToggleExec) {
    btnToggleExec.addEventListener("click", () => {
      if (bossHpPercent > 20) {
        bossHpPercent = 20;
        btnToggleExec.classList.add("active");
      } else {
        bossHpPercent = 100;
        btnToggleExec.classList.remove("active");
      }
      if (quickHpInput) quickHpInput.value = bossHpPercent;
      if (settingsHpInput) settingsHpInput.value = bossHpPercent;
      runSimulation();
    });
  }

  const execPhaseInput = document.getElementById("cfg-exec-phase");
  if (execPhaseInput) {
    execPhaseInput.addEventListener("change", () => {
      executePhasePercent = Math.max(0, Math.min(100, parseFloat(execPhaseInput.value) || 20));
      execPhaseInput.value = executePhasePercent;
      runSimulation();
    });
  }

  ["cfg-armor", "cfg-haste", "cfg-judge", "cfg-exorcism"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener("change", runSimulation);
  });

  const consecCheckbox = document.getElementById("cfg-consec");
  if (consecCheckbox) consecCheckbox.addEventListener("change", runSimulation);

  document.addEventListener("click", (e) => {
    if (!e.target.closest(".combobox-wrap") && !e.target.closest(".combobox-arrow")) {
      closeAllDropdowns();
    }
    if (!e.target.closest(".search-box")) {
      closeGlobalDropdown();
    }
    if (!e.target.closest("#enchant-picker") && !e.target.closest(".slot-enchant-btn")) {
      const p = document.getElementById("enchant-picker");
      if (p) p.style.display = "none";
    }
  });

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeAllDropdowns();
      closeGlobalDropdown();
      hideTooltip();
      hideTalentTip();
      const p = document.getElementById("enchant-picker");
      if (p) p.style.display = "none";
    }
  });
});
