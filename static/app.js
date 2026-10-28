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
let questWeaponSkills = {};
let classEquipmentRules = {};

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

let rotationalSpells = [];
let rotationalSpellsByKey = {};
let activePriorityList = ["hammer_of_wrath", "crusader_holy_strike", "judgement", "consecration", "exorcism"];
let strikeRampCs = 3;
let strikeSustainHs = 1;
let strikeSustainCs = 1;
let enableCrusaderStrike = true;
let enableHolyStrike = true;
let disabledSpells = new Set();
let currentRotationMode = "priority_rotation";

function showSpellTooltip(spell, e) {
  const tip = document.getElementById("wow-tooltip");
  if (!tip || !spell) return;
  if (spell.tooltip_html) {
    tip.innerHTML = spell.tooltip_html;
  } else {
    tip.innerHTML = `
      <div class="tt-spell-wrap">
        <div class="tt-spell-header">
          <span class="tt-spell-name">${spell.name || "Spell"}</span>
          ${spell.rank ? `<span class="tt-spell-rank">${spell.rank}</span>` : ""}
        </div>
        <div class="tt-spell-desc">${spell.description_clean || spell.description || ""}</div>
      </div>
    `;
  }
  tip.style.display = "block";
  positionTooltip(e);
}

const INFO_DESCRIPTIONS = {
  weapon_skill: {
    title: "Weapon Skill & Glancing Blows (Turtle / Octo WoW)",
    desc: "Mechanika biegłości broni na serwerach Turtle / Octo WoW:<br><br>" +
          "&bull; <strong>Bazowa wartość:</strong> 300 na poziomie 60. Maksymalny twardy cap to <strong>315</strong>.<br>" +
          "&bull; <strong>Bonus do Trafienia (+Hit):</strong> Każde 5 punktów powyżej 300 zapewnia <strong>+1.0% Hit</strong> (+0.2% za punkt). 305 = +1.0%, 310 = +2.0%, 315 = +3.0%.<br>" +
          "&bull; <strong>Glancing Blows (Białe Ataki):</strong> Przeciwko bossom rajdowym (lvl 63) szansa na Glancing Blow wynosi stałe 40%. Przy 300 skillu uderzenie zadaje tylko 65% obrażeń (kara 35%).<br>" +
          "&bull; <strong>Skalowanie Glancing:</strong> Każdy punkt biegłości powyżej 300 liniowo podnosi obrażenia o <strong>+2%</strong>, aż do maksymalnego pułapu <strong>95% obrażeń</strong> (kara tylko 5%) przy 315 skillu!<br>" +
          "&bull; <strong>Unik Bossa (Dodge):</strong> Każdy punkt powyżej 300 obniża szansę na unik bossa o 0.1% (z 5.6% do 4.1%)."
  },
  combat_mode: {
    title: "Tryb Walki (Combat Mode)",
    desc: "Wybór sposobu symulacji bitewnej:<br><br>" +
          "&bull; <strong>Priority Rotation:</strong> Pełna symulacja z uwzględnieniem Global Cooldown (1.5s), indywidualnych cooldownów skilli oraz priorytetów z planera rotacji.<br>" +
          "&bull; <strong>Auto Attack Only:</strong> Symulacja wyłącznie uderzeń białych bronią wręcz oraz pasywnych efektów wybranej pieczęci (bez rzucania skilli)."
  },
  playstyle: {
    title: "Styl Gry Paladyna (Playstyle Mode)",
    desc: "Definiuje mechanikę, współczynniki i aktywną pieczęć:<br><br>" +
          "&bull; <strong>Auto-Detect:</strong> Samodzielnie rozpoznaje styl na podstawie założonego ekwipunku i talentów.<br>" +
          "&bull; <strong>Classic Retribution:</strong> Broń 2H, Strength/AP, Seal of Command (7 PPM) i Judgement of Command.<br>" +
          "&bull; <strong>Spellret:</strong> Szybka broń (1H/2H), Spell Power, Seal of Righteousness (Holy on-hit co swing) i wysoki scaling czarów.<br>" +
          "&bull; <strong>Nekrodyn:</strong> 4x Set of the Lost + T2. Generuje szkielety Lost Souls (230-279 Shadow Dmg) przy szkodliwych trafieniach zaklęciem."
  },
  execute_phase: {
    title: "Faza Egzekucji (<20% Execute Phase)",
    desc: "Gdy zdrowie bossa spada poniżej 20%, aktywowane są zdolności wykańczające:<br><br>" +
          "&bull; <strong>Hammer of Wrath (Paladyn):</strong> Rzut młotem omijający pancerz (~530 Holy dmg + 42.86% SP co 6s).<br>" +
          "&bull; <strong>Execute (Wojownik):</strong> Zamiana rage na natychmiastowe obrażenia fizyczne.<br>" +
          "&bull; Możesz włączyć/wyłączyć tę fazę przyciskiem lub dostosować procent czasu w ustawieniach (domyślnie 20%)."
  },
  boss_armor: {
    title: "Pancerz Bossa (Boss Armor)",
    desc: "Wartość pancerza przeciwnika:<br><br>" +
          "&bull; Standardowy boss rajdowy 63 poziomu posiada <strong>3731 pancerza</strong>, co redukuje fizyczne białe ataki oraz Crusader Strike o ok. <strong>40.4%</strong>.<br>" +
          "&bull; <em>Ważne:</em> Wszystkie obrażenia od czarów (Holy, Shadow, Fire) <strong>całkowicie ignorują pancerz bossa</strong>!"
  },
  rotation_planner: {
    title: "Planer Priorytetów i Wspólny Cooldown",
    desc: "Kolejka priorytetów zaklęć (Priority Queue):<br><br>" +
          "&bull; W każdym oknie GCD (1.5s) silnik sprawdza listę od góry do dołu i rzuca pierwszą gotową umiejętność.<br>" +
          "&bull; <strong>Kategoria 40 (Wspólny CD):</strong> Crusader Strike i Holy Strike dzielą wspólny 6-sekundowy cooldown! Silnik rzuca Crusader Strike, by nabić i utrzymać 3 stacki Zeal (+9% Haste), a w pozostałych oknach bije potężniejszym Holy Strike."
  },
  damage_types: {
    title: "Podział Typów Obrażeń (Damage Types)",
    desc: "Rozbicie całkowitego DPS postaci na 3 źródła:<br><br>" +
          "&bull; <span style='color: #e6cc80;'>Physical:</span> Białe ataki oraz Crusader Strike (redukowane pancerzem).<br>" +
          "&bull; <span style='color: #ffd100;'>Holy / Spell:</span> Holy Strike, pieczęcie, osądy, Consecration, Exorcism (omijają pancerz).<br>" +
          "&bull; <span style='color: #b070ff;'>Minions / Shadow:</span> Obrażenia zadawane przez szkielety z Set of the Lost."
  },
  magic_hits: {
    title: "Magiczne Trafienia (Harmful Spell Hits)",
    desc: "Łączna liczba bezpośrednich magicznych trafień w bossa.<br><br>" +
          "Zaliczają się do nich: ticki Consecration, uderzenia z Seal of Righteousness, Holy Strike, Judgement, Exorcism oraz procki T2.<br>" +
          "Jest to <strong>kluczowa statystyka dla Nekrodyna</strong>, ponieważ każde takie trafienie ma 4% szansy na przywołanie miniona!"
  },
  minion_mechanics: {
    title: "Mechanika Minionów z Set of the Lost",
    desc: "Zestaw 4 części <em>Set of the Lost</em> (Memento, Remains, Loop, Tome of the Lost):<br><br>" +
          "&bull; <strong>4% szansy</strong> przy każdym szkodliwym trafieniu zaklęciem na przywołanie szkieletu.<br>" +
          "&bull; Minion żyje <strong>20 sekund</strong> i rzuca <em>Soul Bolt</em> zadający 230-279 obrażeń Shadow (2.0s cast time).<br>" +
          "&bull; Przy częstotliwości ~2.4 magic hits/s generuje ok. <strong>1.9 aktywnego szkieletu</strong> w tym samym czasie (~246 dodatkowego DPS)!"
  },
  paladin_seals: {
    title: "Strategia Otwarcia (Opener) i Wybór Pieczęci",
    desc: "Zasady walki Paladynem w symulatorze:<br><br>" +
          "&bull; <strong>Opener Crusader:</strong> Zgodnie ze sztuką na początku walki Paladyn rzuca <em>Seal of the Crusader</em> i natychmiast osądza bossa (Judgement). Nakłada to stały debuff <strong>+140 Holy Damage Taken</strong> (zwiększany talentami i rękawicami), który wzmacnia wszystkie późniejsze obrażenia od magii Holy!<br>" +
          "&bull; <strong>Seal of Command:</strong> Wymaga talentu w Retribution. 7 PPM (8.5 z Libram of Ardour). 70% weapon dmg + 29% SP jako Holy.<br>" +
          "&bull; <strong>Seal of Righteousness:</strong> Bazowa pieczęć. Dodaje stałe Holy obrażenia przy każdym trafieniu bronią.<br>" +
          "&bull; <strong>Seal of Vengeance:</strong> Nakłada do 5 stacków Holy DoT, a przy 5 stackach każdy cios bronią zadaje dodatkowe 33% Holy weapon damage."
  }
};

function showInfoTooltip(key, e) {
  const tip = document.getElementById("wow-tooltip");
  const data = INFO_DESCRIPTIONS[key];
  if (!tip || !data) return;

  tip.innerHTML = `
    <div class="tt-info-wrap">
      <div class="tt-info-title">&#9432; ${data.title}</div>
      <div class="tt-info-desc">${data.desc}</div>
      <div class="tt-info-footer">Octo WoW Calculator Guide</div>
    </div>
  `;
  tip.style.display = "block";
  positionTooltip(e);
}

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
      if (currentClass === "paladin") {
        if (["dagger", "staff", "fist", "gun", "bow", "crossbow", "wand", "thrown"].includes(item.subclass)) {
          return false;
        }
        // Paladin cannot dual wield weapons in offhand
        if (slotKey === "off_hand") {
          const isWeapon = ["sword", "mace", "axe", "dagger", "fist", "one_hand_sword", "one_hand_mace", "one_hand_axe"].includes(item.subclass) || (item.speed > 0 && ["onehand", "one_hand", "offhand"].includes(item.slot));
          if (isWeapon && item.slot !== "shield" && item.subclass !== "shield") {
            return false;
          }
        }
        // Paladin can only equip Librams in relic / third slot
        if (slotKey === "relic" || slotKey === "ranged") {
          if (item.subclass !== "libram") {
            return false;
          }
        }
      }
      if (currentClass === "warrior") {
        if (["wand", "relic", "libram", "totem", "idol"].includes(item.subclass)) {
          return false;
        }
        if (slotKey === "relic") {
          return false;
        }
        if (slotKey === "ranged" && !["bow", "gun", "crossbow", "thrown", "misc"].includes(item.subclass)) {
          return false;
        }
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
    if (currentClass === "paladin") return "main_hand";
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
    if (currentClass === "paladin") {
      if (["dagger", "staff", "fist", "gun", "bow", "crossbow", "wand", "thrown"].includes(item.subclass)) {
        alert("Paladyn nie może używać tego typu broni (" + item.subclass + ")!");
        return;
      }
      if (slotKey === "off_hand") {
        const isWeapon = ["sword", "mace", "axe", "dagger", "fist", "one_hand_sword", "one_hand_mace", "one_hand_axe"].includes(item.subclass) || (item.speed > 0 && ["onehand", "one_hand", "offhand"].includes(item.slot));
        if (isWeapon && item.slot !== "shield" && item.subclass !== "shield") {
          alert("Paladyn nie posiada umiejętności walki dwiema brońmi (Dual Wield)!\nW lewej ręce dozwolona jest wyłącznie tarcza lub przedmiot trzymany (Off-hand).");
          return;
        }
      }
      if ((slotKey === "relic" || slotKey === "ranged") && item.subclass !== "libram") {
        alert("Paladyn może używać w tym slocie wyłącznie Libramów!");
        return;
      }
    }
    if (currentClass === "warrior") {
      if (["wand", "relic", "libram", "totem", "idol"].includes(item.subclass)) {
        alert("Wojownik nie może używać relikwii ani różdżek!");
        return;
      }
      if (slotKey === "relic") {
        alert("Wojownik nie posiada slotu na relikwie!");
        return;
      }
    }
  }

  // Auto-unequip off hand if 2-Handed weapon equipped
  if (item && (item.slot === "twohand" || item.slot === "two_hand") && slotKey === "main_hand") {
    if (equippedItems.off_hand) {
      equipItem("off_hand", null);
    }
  }
  if (slotKey === "off_hand" && itemId) {
    const mh = itemsById[String(equippedItems.main_hand)];
    if (mh && (mh.slot === "twohand" || mh.slot === "two_hand")) {
      equipItem("main_hand", null);
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
  s = s.replace(/Dreamsteel Belt Buckle \(\+10 Intellect\)/i, "Dreamsteel (+10 Int)");
  s = s.replace(/Mithril Belt Buckle \(\+6 Agility\)/i, "Mithril (+6 Agi)");
  s = s.replace(/Iron Belt Buckle \(\+25 Armor Penetration\)/i, "Iron (+25 ArP)");
  s = s.replace(/Truesilver Belt Buckle \(\+10 Healing \/ \+6 Spell Power\)/i, "Truesilver (+6 SP)");
  s = s.replace(/Thorium Belt Buckle \(\+4 All Resistances\)/i, "Thorium (+4 Res)");
  s = s.replace(/Dragonscale Belt Buckle \(\+10 Fire Resistance\)/i, "Dragonscale (+10 FR)");
  s = s.replace(/Bloody Belt Buckle \(-3% Crit\/DoT Dmg Taken\)/i, "Bloody (-3% Resil)");
  s = s.replace(/Ceremonial Belt Buckle \(\+4 Intellect\)/i, "Ceremonial (+4 Int)");
  s = s.replace(/Bronze Belt Buckle \(\+2 Stamina\)/i, "Bronze (+2 Sta)");
  s = s.replace(/Copper Belt Buckle \(\+1 Stamina\)/i, "Copper (+1 Sta)");
  s = s.replace(/Azerothian Ruby Gemstone \(\+6 Strength\)/i, "Ruby (+6 Str)");
  s = s.replace(/Delicate Emerald Gemstone \(\+6 Agility\)/i, "Emerald (+6 Agi)");
  s = s.replace(/Bold Ruby Gemstone \(\+12 Attack Power\)/i, "Bold Ruby (+12 AP)");
  s = s.replace(/Arcane Emerald Gemstone \(\+5 Spell Damage\)/i, "Arcane (+5 SP)");
  s = s.replace(/Shining Sapphire Gemstone \(\+6 Intellect\)/i, "Sapphire (+6 Int)");
  s = s.replace(/Tempered Azerothian Gemstone \(\+6 Stamina\)/i, "Tempered (+6 Sta)");
  s = s.replace(/Stunning Imperial Gemstone \(\+3 All Stats\)/i, "Imperial (+3 Stats)");
  s = s.replace(/Beautiful Diamond Gemstone \(\+12 Healing\)/i, "Diamond (+12 Heal)");
  s = s.replace(/Gleaming Jade Gemstone \(\+7 Healing\)/i, "Jade (+7 Heal)");
  s = s.replace(/Crystalized Topaz Gemstone \(\+9 Arcane Spell Damage\)/i, "Topaz (+9 Arc)");
  s = s.replace(/Graceful Agate Gemstone \(\+6 Spell Penetration\)/i, "Agate (+6 Pen)");
  s = s.replace(/Gorgeous Mountain Gemstone \(\+1% Block Chance\)/i, "Mountain (+1% Blk)");
  s = s.replace(/Glowing Ruby Gemstone \(\+1% Vampirism\)/i, "Ruby (+1% Vamp)");
  s = s.replace(/Pristine Quartz \(\+3 Stamina\)/i, "Quartz (+3 Sta)");
  s = s.replace(/Resilient Arcane Gemstone \(\+30 Armor\)/i, "Resilient (+30 Arm)");
  s = s.replace(/Gloomy Diamond Gemstone \(\+5 Fire Resistance\)/i, "Diamond (+5 FR)");
  s = s.replace(/Unstable Arcane Gemstone \(\+5 Arcane Resistance\)/i, "Arcane (+5 AR)");
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
    if (slotKey === "waist") {
      btn.textContent = "+ Buckle";
      btn.title = "Select Belt Buckle (Blacksmithing)";
    } else if (slotKey === "neck" || slotKey === "finger1" || slotKey === "finger2") {
      btn.textContent = "+ Gem";
      btn.title = "Select Gemstone (Jewelcrafting)";
    } else {
      btn.textContent = "+ Enchant";
      btn.title = "Select enchant";
    }
    btn.className = "slot-enchant-btn";
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
    const ohItem = itemsById[String(equippedItems.off_hand)];
    if (ohItem && (ohItem.slot === "shield" || ohItem.subclass === "shield")) {
      category = "shield";
    } else {
      category = "offhand";
    }
  } else if (slotKey === "relic" || slotKey === "trinket1" || slotKey === "trinket2") {
    alert("Przedmioty w tym slocie (np. Trinkety, Libramy, Totemy, Idole) nie posiadają zaklęć ani gemów w grze.");
    return;
  } else if (slotKey === "finger1" || slotKey === "finger2") {
    category = "finger";
  } else if (slotKey === "neck") {
    category = "neck";
  } else if (slotKey === "waist") {
    category = "waist";
  } else if (slotKey === "ranged") {
    category = "ranged";
  }

  renderEnchantPickerList(category, slotKey);

  const popover = document.getElementById("enchant-picker");
  popover.style.display = "flex";
  const titleEl = document.getElementById("ench-picker-title");
  if (titleEl) {
    if (slotKey === "waist") {
      titleEl.textContent = `Belt Buckle: ${getSlotDisplayTitle(slotKey)}`;
    } else if (slotKey === "neck" || slotKey === "finger1" || slotKey === "finger2") {
      titleEl.textContent = `Gemstone: ${getSlotDisplayTitle(slotKey)}`;
    } else {
      titleEl.textContent = `Enchant: ${getSlotDisplayTitle(slotKey)}`;
    }
  }

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
    if (ench.int) desc += `+${ench.int} Int `;
    if (ench.spi) desc += `+${ench.spi} Spi `;
    if (ench.ap) desc += `+${ench.ap} AP `;
    if (ench.sp) desc += `+${ench.sp} SP `;
    if (ench.healing) desc += `+${ench.healing} Heal `;
    if (ench.arp) desc += `+${ench.arp} ArP `;
    if (ench.armor) desc += `+${ench.armor} Armor `;
    if (ench.block) desc += `+${ench.block}% Block `;
    if (ench.resilience) desc += `-${ench.resilience}% Dmg Taken `;
    if (ench.vampirism) desc += `+${ench.vampirism}% Vampirism `;
    if (ench.crit) desc += `+${ench.crit}% Crit `;
    if (ench.hit) desc += `+${ench.hit}% Hit `;
    if (ench.haste) desc += `+${ench.haste}% Haste `;
    if (ench.bonusdmg) desc += `+${ench.bonusdmg} Dmg `;
    if (ench.ppm) desc += `${ench.ppm} PPM Proc `;
    if (ench.magicdmg) desc += `+${ench.magicdmg} Magic Dmg `;
    if (ench.fire) desc += `+${ench.fire} FR `;
    if (ench.frost) desc += `+${ench.frost} Frost `;
    if (ench.nature) desc += `+${ench.nature} Nature `;
    if (ench.shadow) desc += `+${ench.shadow} Shadow `;
    if (ench.arcane) desc += `+${ench.arcane} Arcane `;

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
  validatePaladinSealTalents();
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
    character_class: currentClass,
    quest_weapon_skills: questWeaponSkills
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
  const wsEl = document.getElementById("stat-weapon-skill");
  if (wsEl) {
    const ws = totals.effective_weapon_skill || 300;
    const wsHit = totals.weapon_skill_hit_bonus || 0;
    const glance = Math.round((totals.glance_damage_factor || 0.65) * 100);
    wsEl.textContent = `${ws} / 315 (+${wsHit.toFixed(1)}% Hit, ${glance}% Glance)`;
  }
  document.getElementById("stat-str").textContent = totals.strength || 0;
  document.getElementById("stat-agi").textContent = totals.agility || 0;
  document.getElementById("stat-sta").textContent = totals.stamina || 0;
  document.getElementById("stat-int").textContent = totals.intellect || 0;
  document.getElementById("stat-armor").textContent = totals.armor || 0;

  const setsContainer = document.getElementById("active-sets-list");
  const countEl = document.getElementById("active-sets-count");
  if (setsContainer && countEl) {
    const activeSets = totals.active_sets || {};
    const setKeys = Object.keys(activeSets);
    let setsWithBonuses = 0;
    setsContainer.innerHTML = "";
    if (setKeys.length === 0) {
      setsContainer.innerHTML = `<div class="no-sets-label">No set bonuses active</div>`;
      countEl.textContent = "0 Sets";
    } else {
      setKeys.forEach(k => {
        const s = activeSets[k];
        const itemDiv = document.createElement("div");
        itemDiv.className = "active-set-item";
        let bonusesHtml = "";
        if (s.active_bonuses && s.active_bonuses.length > 0) {
          setsWithBonuses++;
          s.active_bonuses.forEach(b => {
            bonusesHtml += `<div class="active-set-bonus-text">✦ ${b.text}</div>`;
          });
        } else {
          bonusesHtml = `<div class="active-set-bonus-text" style="color: var(--text-dim); font-style: italic;">No thresholds reached</div>`;
        }
        itemDiv.innerHTML = `
          <div class="active-set-header">
            <span class="active-set-name">${s.name}</span>
            <span class="active-set-count-tag">${s.equipped_count}/${s.total_pieces}</span>
          </div>
          ${bonusesHtml}
        `;
        setsContainer.appendChild(itemDiv);
      });
      countEl.textContent = `${setsWithBonuses} Active`;
    }
  }
}

function loadRotationalSpells() {
  fetch("/api/spells?class=paladin")
    .then(res => res.json())
    .then(data => {
      rotationalSpells = data.rotational_spells || [];
      rotationalSpellsByKey = {};
      rotationalSpells.forEach(s => {
        rotationalSpellsByKey[s.key] = s;
      });
      renderPriorityList();
    })
    .catch(err => {
      console.error("Failed to load rotational spells:", err);
    });
}

function renderPriorityList() {
  const container = document.getElementById("priority-spells-list");
  if (!container) return;
  container.innerHTML = "";

  const spellMap = {};
  rotationalSpells.forEach(s => { spellMap[s.key] = s; });

  // Normalize legacy keys: ensure crusader_strike and holy_strike are consolidated into crusader_holy_strike
  const cleanedPriority = [];
  let hasStrike = false;
  activePriorityList.forEach(k => {
    if (k === "crusader_strike" || k === "holy_strike" || k === "crusader_holy_strike" || k === "strike_category_40") {
      if (!hasStrike) {
        cleanedPriority.push("crusader_holy_strike");
        hasStrike = true;
      }
    } else if (k && !cleanedPriority.includes(k)) {
      cleanedPriority.push(k);
    }
  });
  activePriorityList = cleanedPriority;

  const allKeys = [...activePriorityList];
  rotationalSpells.forEach(s => {
    if (s.key === "crusader_strike" || s.key === "holy_strike") {
      if (!allKeys.includes("crusader_holy_strike")) {
        allKeys.push("crusader_holy_strike");
      }
    } else if (!allKeys.includes(s.key) && s.category !== "seal") {
      allKeys.push(s.key);
      disabledSpells.add(s.key);
    }
  });

  allKeys.forEach((key, index) => {
    // 1. UNIFIED ROW: Crusader Strike & Holy Strike (Shared Category 40 Cooldown)
    if (key === "crusader_holy_strike") {
      const csSpell = spellMap["crusader_strike"] || {
        name: "Crusader Strike",
        icon: "spell_holy_crusaderstrike",
        cooldown: 6.0,
        mana_cost: 120,
        rank: "Rank 1"
      };
      const hsSpell = spellMap["holy_strike"] || {
        name: "Holy Strike",
        icon: "spell_holy_holysmite",
        cooldown: 6.0,
        mana_cost: 90,
        rank: "Rank 1"
      };

      const isEnabled = !disabledSpells.has("crusader_holy_strike");
      const item = document.createElement("div");
      item.className = `priority-item shared-strike-item ${isEnabled ? "active" : "disabled"}`;
      item.setAttribute("data-spell-key", "crusader_holy_strike");

      const csIconUrl = getItemIconUrl(csSpell.icon) || getItemIconFallbackUrl(csSpell.icon);
      const hsIconUrl = getItemIconUrl(hsSpell.icon) || getItemIconFallbackUrl(hsSpell.icon);

      item.innerHTML = `
        <div class="priority-col-rank">
          <span class="rank-badge">${index + 1}</span>
        </div>
        <div class="priority-col-info shared-info-col">
          <div class="shared-strike-header">
            <div class="shared-icons-duo">
              <img class="spell-thumb cs-icon-thumb" src="${csIconUrl}" onerror="this.src='${getItemIconFallbackUrl(csSpell.icon)}'" alt="Crusader Strike" title="Crusader Strike">
              <span class="shared-plus">+</span>
              <img class="spell-thumb hs-icon-thumb" src="${hsIconUrl}" onerror="this.src='${getItemIconFallbackUrl(hsSpell.icon)}'" alt="Holy Strike" title="Holy Strike">
            </div>
            <div class="spell-text-wrap">
              <div class="spell-title-row">
                <strong class="spell-name">Crusader Strike &amp; Holy Strike</strong>
                <span class="shared-category-badge" title="Zdolności dzielą Kategorię 40 w Spell.dbc - użycie jednej nakłada 6.0s wspólnego cooldownu!">Wspólny Cooldown: 6.0s (Kat. 40)</span>
              </div>
              <div class="spell-scaling-note">
                Crusader: 100% Wpn + 160 (Fizyczne, +3% Haste z Zeal) &bull; Holy: 100% Wpn + 137 + 20% SP (Holy, ignoruje pancerz)
              </div>
            </div>
          </div>

          <!-- Konfiguracja sekwencji rotacyjnej w jednym wierszu -->
          <div class="shared-strike-rot-box">
            <div class="rot-phase-row">
              <div class="phase-tag ramp-tag">1. Rozgrzewka (Ramp-up)</div>
              <div class="phase-controls">
                <span class="phase-txt">Na początku walki rzuć:</span>
                <input type="number" id="input-strike-ramp-cs" class="strike-seq-input" value="${strikeRampCs}" min="0" max="10" step="1">
                <span class="phase-unit">&times; Crusader Strike</span>
                <span class="phase-hint">(budowanie 3 ładunków Zeal: +9% Haste)</span>
              </div>
            </div>
            <div class="rot-phase-row">
              <div class="phase-tag sustain-tag">2. Stała Rotacja (Pełny Haste)</div>
              <div class="phase-controls">
                <span class="phase-txt">Gdy masz pełny haste, rzucaj na przemian:</span>
                <div class="seq-subgrid">
                  <span class="sub-item">
                    <input type="number" id="input-strike-sustain-hs" class="strike-seq-input" value="${strikeSustainHs}" min="0" max="10" step="1">
                    <span class="phase-unit">&times; Holy Strike</span>
                  </span>
                  <span class="phase-arrow">&rarr;</span>
                  <span class="sub-item">
                    <input type="number" id="input-strike-sustain-cs" class="strike-seq-input" value="${strikeSustainCs}" min="0" max="10" step="1">
                    <span class="phase-unit">&times; Crusader Strike</span>
                  </span>
                </div>
                <span class="phase-hint">(cyklicznie odświeża Zeal przed wygaśnięciem)</span>
              </div>
            </div>
          </div>
        </div>
        <div class="priority-col-cd">
          <div class="cd-line">6.0s Shared CD</div>
          <div class="cost-line">120 / 90 Mana &bull; Instant</div>
          <div class="shared-subnote">Współdzielony timer</div>
        </div>
        <div class="priority-col-actions">
          <button type="button" class="btn-pri-move btn-pri-up" title="Przesuń wyżej w kolejce priorytetów" ${index === 0 ? "disabled" : ""}>&uarr;</button>
          <button type="button" class="btn-pri-move btn-pri-down" title="Przesuń niżej w kolejce priorytetów" ${index === allKeys.length - 1 ? "disabled" : ""}>&darr;</button>
          <label class="pri-check-wrap" title="Włącz lub wyłącz uderzenia współdzielone w symulacji">
            <input type="checkbox" class="pri-toggle-check" ${isEnabled ? "checked" : ""}>
            <span class="pri-check-custom"></span>
          </label>
        </div>
      `;

      // Tooltips for individual spell icons
      const csIcon = item.querySelector(".cs-icon-thumb");
      if (csIcon) {
        csIcon.style.cursor = "help";
        csIcon.addEventListener("mouseenter", (e) => showSpellTooltip(csSpell, e));
        csIcon.addEventListener("mousemove", (e) => positionTooltip(e));
        csIcon.addEventListener("mouseleave", hideTooltip);
      }
      const hsIcon = item.querySelector(".hs-icon-thumb");
      if (hsIcon) {
        hsIcon.style.cursor = "help";
        hsIcon.addEventListener("mouseenter", (e) => showSpellTooltip(hsSpell, e));
        hsIcon.addEventListener("mousemove", (e) => positionTooltip(e));
        hsIcon.addEventListener("mouseleave", hideTooltip);
      }

      // Input listeners for sequence configuration
      const rampInp = item.querySelector("#input-strike-ramp-cs");
      if (rampInp) {
        rampInp.addEventListener("change", (e) => {
          strikeRampCs = Math.max(0, parseInt(e.target.value, 10) || 0);
          e.target.value = strikeRampCs;
          runSimulation();
        });
      }
      const susHsInp = item.querySelector("#input-strike-sustain-hs");
      if (susHsInp) {
        susHsInp.addEventListener("change", (e) => {
          strikeSustainHs = Math.max(0, parseInt(e.target.value, 10) || 0);
          e.target.value = strikeSustainHs;
          runSimulation();
        });
      }
      const susCsInp = item.querySelector("#input-strike-sustain-cs");
      if (susCsInp) {
        susCsInp.addEventListener("change", (e) => {
          strikeSustainCs = Math.max(0, parseInt(e.target.value, 10) || 0);
          e.target.value = strikeSustainCs;
          runSimulation();
        });
      }

      // Actions buttons
      const upBtn = item.querySelector(".btn-pri-up");
      if (upBtn) {
        upBtn.addEventListener("click", () => {
          if (index > 0) {
            const temp = activePriorityList[index];
            activePriorityList[index] = activePriorityList[index - 1];
            activePriorityList[index - 1] = temp;
            renderPriorityList();
            runSimulation();
          }
        });
      }
      const downBtn = item.querySelector(".btn-pri-down");
      if (downBtn) {
        downBtn.addEventListener("click", () => {
          if (index < activePriorityList.length - 1) {
            const temp = activePriorityList[index];
            activePriorityList[index] = activePriorityList[index + 1];
            activePriorityList[index + 1] = temp;
            renderPriorityList();
            runSimulation();
          }
        });
      }
      const check = item.querySelector(".pri-toggle-check");
      if (check) {
        check.addEventListener("change", (e) => {
          if (e.target.checked) {
            disabledSpells.delete("crusader_holy_strike");
          } else {
            disabledSpells.add("crusader_holy_strike");
          }
          renderPriorityList();
          runSimulation();
        });
      }

      container.appendChild(item);
      return;
    }

    // 2. STANDARD ROTATIONAL SPELL ROW
    const s = spellMap[key];
    if (!s) return;

    const isEnabled = !disabledSpells.has(key);
    const item = document.createElement("div");
    item.className = `priority-item ${isEnabled ? "active" : "disabled"}`;
    item.setAttribute("data-spell-key", key);

    const iconUrl = getItemIconUrl(s.icon) || getItemIconFallbackUrl(s.icon);

    let cdText = `${s.cooldown}s CD`;
    if (key === "holy_strike") cdText = "6.0s CD (Holy Dmg)";
    if (key === "judgement") cdText = "8-10s CD";
    if (key === "consecration") cdText = "8.0s CD (8s AoE)";
    if (key === "exorcism") cdText = "10-15s CD";
    if (key === "hammer_of_wrath") cdText = "6.0s CD (<20% HP)";

    let statText = "";
    if (s.ap_coef > 0 && s.bonus_flat > 0) {
      statText = `${Math.round(s.ap_coef * 100)}% Wpn + ${s.bonus_flat}`;
    } else if (s.spell_power_coef > 0) {
      statText = `${Math.round(s.avg_damage)} Base + ${(s.spell_power_coef * 100).toFixed(1)}% SP`;
    } else {
      statText = s.description ? s.description.substring(0, 45) + "..." : "";
    }

    item.innerHTML = `
      <div class="priority-col-rank">
        <span class="rank-badge">${index + 1}</span>
      </div>
      <div class="priority-col-info">
        <img class="spell-thumb" src="${iconUrl}" onerror="this.src='${getItemIconFallbackUrl(s.icon)}'" alt="${s.name}">
        <div class="spell-text-wrap">
          <div class="spell-title-row">
            <strong class="spell-name">${s.name}</strong>
            ${s.rank ? `<span class="spell-rank-badge">${s.rank}</span>` : ""}
          </div>
          <div class="spell-scaling-note">${statText}</div>
        </div>
      </div>
      <div class="priority-col-cd">
        <div class="cd-line">${cdText}</div>
        <div class="cost-line">${s.mana_cost ? `${s.mana_cost} Mana` : "0 Mana"} &bull; ${s.cast_time > 0 ? `${s.cast_time}s Cast` : "Instant"}</div>
      </div>
      <div class="priority-col-actions">
        <button type="button" class="btn-pri-move btn-pri-up" title="Move Up in priority queue" ${index === 0 ? "disabled" : ""}>&uarr;</button>
        <button type="button" class="btn-pri-move btn-pri-down" title="Move Down in priority queue" ${index === allKeys.length - 1 ? "disabled" : ""}>&darr;</button>
        <label class="pri-check-wrap" title="Enable or disable ability in simulation">
          <input type="checkbox" class="pri-toggle-check" ${isEnabled ? "checked" : ""}>
          <span class="pri-check-custom"></span>
        </label>
      </div>
    `;

    const infoCol = item.querySelector(".priority-col-info");
    if (infoCol) {
      infoCol.style.cursor = "help";
      infoCol.addEventListener("mouseenter", (e) => showSpellTooltip(s, e));
      infoCol.addEventListener("mousemove", (e) => positionTooltip(e));
      infoCol.addEventListener("mouseleave", hideTooltip);
    }

    const upBtn = item.querySelector(".btn-pri-up");
    if (upBtn) {
      upBtn.addEventListener("click", () => {
        if (index > 0) {
          const temp = activePriorityList[index];
          activePriorityList[index] = activePriorityList[index - 1];
          activePriorityList[index - 1] = temp;
          renderPriorityList();
          runSimulation();
        }
      });
    }

    const downBtn = item.querySelector(".btn-pri-down");
    if (downBtn) {
      downBtn.addEventListener("click", () => {
        if (index < activePriorityList.length - 1) {
          const temp = activePriorityList[index];
          activePriorityList[index] = activePriorityList[index + 1];
          activePriorityList[index + 1] = temp;
          renderPriorityList();
          runSimulation();
        }
      });
    }

    const check = item.querySelector(".pri-toggle-check");
    if (check) {
      check.addEventListener("change", (e) => {
        if (e.target.checked) {
          disabledSpells.delete(key);
        } else {
          disabledSpells.add(key);
        }
        renderPriorityList();
        runSimulation();
      });
    }

    container.appendChild(item);
  });
}

function syncRotationMode(newMode) {
  currentRotationMode = newMode;
  const selMain = document.getElementById("cfg-rotation-mode");
  const selQuick = document.getElementById("cfg-rotation-mode-quick");
  const selSettings = document.getElementById("cfg-rotation-mode-settings");
  if (selMain) selMain.value = newMode;
  if (selQuick) selQuick.value = newMode;
  if (selSettings) selSettings.value = newMode;

  const autoNotice = document.getElementById("rotation-auto-notice");
  const queueWrap = document.getElementById("priority-queue-wrap");
  if (autoNotice) {
    autoNotice.style.display = newMode === "auto_attack_only" ? "flex" : "none";
  }
  if (queueWrap) {
    queueWrap.classList.toggle("mode-auto-dimmed", newMode === "auto_attack_only");
  }

  runSimulation();
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
    paladin_build: "auto",
    talents: allocatedTalents,
    boss_hp_percent: bossHpPercent,
    execute_phase_percent: executePhasePercent,
    race: currentRace,
    enchants: currentEnchants,
    rotation_mode: currentRotationMode,
    priority_list: activePriorityList.filter(k => !disabledSpells.has(k)),
    strike_ramp_cs: strikeRampCs,
    strike_sustain_hs: strikeSustainHs,
    strike_sustain_cs: strikeSustainCs,
    enable_crusader_strike: !disabledSpells.has("crusader_holy_strike") && enableCrusaderStrike,
    enable_holy_strike: !disabledSpells.has("crusader_holy_strike") && enableHolyStrike,
    quest_weapon_skills: questWeaponSkills,
    primary_seal: document.getElementById("cfg-primary-seal")?.value || "auto",
    apply_crusader_first: document.getElementById("cfg-opener-crusader")?.checked ?? true
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

let breakdownViewMode = "dps";
let breakdownSortDesc = true;
let lastSimulationData = null;

function validatePaladinSealTalents() {
  const sealSelect = document.getElementById("cfg-primary-seal");
  const warnEl = document.getElementById("seal-talent-warning");
  if (!sealSelect) return;

  const allocated = getTalentsAllocatedByName();
  const hasSocTalent = (allocated["Seal of Command"] || 0) > 0;

  const optCommand = document.getElementById("opt-seal-command");
  if (optCommand) {
    if (hasSocTalent) {
      optCommand.textContent = "Seal of Command (Talent aktywny)";
      optCommand.style.color = "#77ff77";
    } else {
      optCommand.textContent = "Seal of Command (Wymaga talentu w Retribution)";
      optCommand.style.color = "#ff8888";
    }
  }

  if (warnEl) {
    if (sealSelect.value === "command" && !hasSocTalent) {
      warnEl.style.display = "block";
    } else {
      warnEl.style.display = "none";
    }
  }
}

function setBreakdownViewMode(mode) {
  breakdownViewMode = mode;
  document.getElementById("btn-bd-mode-dps")?.classList.toggle("active", mode === "dps");
  document.getElementById("btn-bd-mode-damage")?.classList.toggle("active", mode === "damage");
  if (lastSimulationData) {
    renderAttackBreakdown(lastSimulationData);
  }
}

function toggleBreakdownSort() {
  breakdownSortDesc = !breakdownSortDesc;
  const btn = document.getElementById("btn-bd-sort-btn");
  if (btn) {
    if (breakdownSortDesc) {
      btn.innerHTML = "&#8693; Sort: Najwy\u017csze &darr;";
      btn.classList.add("active-sort");
    } else {
      btn.innerHTML = "&#8693; Sort: Domy\u015blne";
      btn.classList.remove("active-sort");
    }
  }
  if (lastSimulationData) {
    renderAttackBreakdown(lastSimulationData);
  }
}

function renderAttackBreakdown(data) {
  const breakdownContainer = document.getElementById("breakdown-list-own");
  if (!breakdownContainer || !data) return;
  breakdownContainer.innerHTML = "";

  let sources = [];
  if (data.damage_sources && data.damage_sources.length > 0) {
    sources = data.damage_sources.map(s => ({ ...s }));
  } else {
    const bd = data.own_damage_breakdown || {};
    const totalDps = data.total_dps || data.own_dps || 1;
    for (const [key, dpsVal] of Object.entries(bd)) {
      if (dpsVal <= 0) continue;
      const dmgVal = dpsVal * (data.fight_duration || 60);
      const pct = Math.round((dpsVal / totalDps) * 1000) / 10;
      sources.push({
        id: key,
        name: key.replace(/_/g, " ").replace("dps", "DPS"),
        category: "General",
        color: "#c9a227",
        dps: dpsVal,
        damage: dmgVal,
        percent: pct,
        spell_key: null,
        is_minion: false,
        is_proc: false
      });
    }
  }

  // Filter out negligible values
  sources = sources.filter(s => (s.dps > 0.001 || s.damage > 0.001));

  // Sort if requested
  if (breakdownSortDesc) {
    if (breakdownViewMode === "dps") {
      sources.sort((a, b) => b.dps - a.dps);
    } else {
      sources.sort((a, b) => b.damage - a.damage);
    }
  }

  const maxVal = sources.reduce((m, s) => Math.max(m, breakdownViewMode === "dps" ? s.dps : s.damage), 1);

  sources.forEach(src => {
    const row = document.createElement("div");
    row.className = "attack-row";

    const catTag = src.category ? src.category.toLowerCase() : "general";
    const tagClass = `tag-${catTag}`;

    const valDisplay = breakdownViewMode === "dps"
      ? `${src.dps.toFixed(2)} DPS`
      : `${Math.round(src.damage).toLocaleString()} DMG`;

    const barPercent = Math.min(100, Math.max(2, (((breakdownViewMode === "dps" ? src.dps : src.damage) / maxVal) * 100)));

    row.innerHTML = `
      <div class="attack-row-main">
        <div class="attack-row-info">
          <span class="attack-type-tag ${tagClass}">${src.category || "Skill"}</span>
          <span class="attack-name-text" title="${src.name}">${src.name}</span>
        </div>
        <div class="attack-row-values">
          <span class="attack-val-num">${valDisplay}</span>
          <span class="attack-val-pct">${src.percent.toFixed(1)}%</span>
        </div>
      </div>
      <div class="attack-bar-bg">
        <div class="attack-bar-fill" style="width: ${barPercent}%; background: ${src.color || '#c9a227'};"></div>
      </div>
    `;

    const spellKey = src.spell_key;
    if (spellKey && rotationalSpellsByKey[spellKey]) {
      const sp = rotationalSpellsByKey[spellKey];
      row.style.cursor = "help";
      row.addEventListener("mouseenter", (e) => showSpellTooltip(sp, e));
      row.addEventListener("mousemove", (e) => positionTooltip(e));
      row.addEventListener("mouseleave", hideTooltip);
    }

    breakdownContainer.appendChild(row);
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

  const wsEl = document.getElementById("stat-weapon-skill");
  if (wsEl && (data.effective_weapon_skill || data.gear_summary?.effective_weapon_skill)) {
    const ws = data.effective_weapon_skill || data.gear_summary.effective_weapon_skill;
    const wsHit = data.weapon_skill_hit_bonus ?? data.gear_summary?.weapon_skill_hit_bonus ?? 0;
    const glance = Math.round((data.glance_damage_factor ?? data.gear_summary?.glance_damage_factor ?? 0.65) * 100);
    wsEl.textContent = `${ws} / 315 (+${wsHit.toFixed(1)}% Hit, ${glance}% Glance)`;
  }

  const infoEl = document.getElementById("sim-scenario-info");
  if (infoEl) {
    const isDw = data.is_dual_wield ? " (DW)" : (data.is_two_handed ? " (2H)" : "");
    infoEl.textContent = `Duration: ${data.fight_duration}s | ${data.character_class.toUpperCase()}${isDw} (${data.race}) | Boss HP: ${data.boss_hp_percent}% | Execute: ${data.execute_duration_seconds}s`;
  }

  const buildBadge = document.getElementById("res-build-badge");
  if (buildBadge) {
    if (data.character_class === "paladin" && data.paladin_build_name) {
      buildBadge.textContent = data.paladin_build_name;
      buildBadge.style.display = "inline-flex";
      buildBadge.className = `build-badge build-${data.paladin_build || "retribution"}`;
    } else {
      buildBadge.style.display = "none";
    }
  }

  const rotBadge = document.getElementById("res-rot-badge");
  if (rotBadge) {
    if (data.character_class === "paladin") {
      rotBadge.textContent = data.rotation_mode_name || "Priority Rotation";
      rotBadge.style.display = "inline-flex";
      rotBadge.className = `rot-badge rot-${data.rotation_mode || "priority_rotation"}`;
    } else {
      rotBadge.style.display = "none";
    }
  }

  const castsCard = document.getElementById("card-rotation-breakdown");
  const castsList = document.getElementById("breakdown-list-casts");
  if (castsCard && castsList) {
    if (data.character_class === "paladin") {
      castsCard.style.display = "block";
      castsList.innerHTML = "";

      if (data.rotation_mode === "auto_attack_only") {
        const autoRow = document.createElement("div");
        autoRow.className = "b-item highlight-auto";
        autoRow.innerHTML = `<span>Tryb Walki:</span><strong class="warn">Tylko Auto Attacki (Umiejetnosci wylaczone)</strong>`;
        castsList.appendChild(autoRow);
        const sealRow = document.createElement("div");
        sealRow.className = "b-item";
        sealRow.innerHTML = `<span>Aktywna Pieczec:</span><strong>${data.paladin_build === "retribution" ? "Seal of Command (7 PPM)" : "Seal of Righteousness (On-Hit)"}</strong>`;
        castsList.appendChild(sealRow);
      } else {
        if (data.strike_sequence) {
          const seqRow = document.createElement("div");
          seqRow.className = "b-item highlight-strike-seq";
          seqRow.innerHTML = `<span>Sekwencja Uderzeń:</span><strong class="gold">${data.strike_sequence.ramp_cs}x CS (Ramp) &bull; ${data.strike_sequence.sustain_hs}x HS : ${data.strike_sequence.sustain_cs}x CS (Sustain)</strong>`;
          castsList.appendChild(seqRow);
        }

        const casts = data.ability_casts || {};
        const zealText = data.zeal_haste_percent !== undefined ? `+${data.zeal_haste_percent}%` : "+9%";
        const castLabelMap = {
          crusader_strike: `Crusader Strike (Śr. Zeal Haste: ${zealText})`,
          holy_strike: "Holy Strike (Broń Holy Dmg)",
          judgement: "Judgement Casts",
          judgement_of_the_crusader: "Opener: Judgement of the Crusader (+Holy Debuff)",
          consecration: "Consecration Casts",
          consecration_ticks: "Consecration Holy Ticks",
          exorcism: "Exorcism Casts",
          hammer_of_wrath: "Hammer of Wrath Casts (<20%)",
          holy_shock: "Holy Shock Casts"
        };

        if (data.primary_seal_name) {
          const sealRow = document.createElement("div");
          sealRow.className = "b-item";
          sealRow.innerHTML = `<span>Aktywna Piecz\u0119\u0107:</span><strong class="magic">${data.primary_seal_name}</strong>`;
          castsList.appendChild(sealRow);
        }

        if (data.seal_fallback_reason) {
          const fbRow = document.createElement("div");
          fbRow.className = "b-item";
          fbRow.innerHTML = `<span style="color: #ff9999;">Uwaga Piecz\u0119ci:</span><strong style="color: #ff9999; font-size: 11px;">${data.seal_fallback_reason}</strong>`;
          castsList.appendChild(fbRow);
        }

        for (const [key, num] of Object.entries(casts)) {
          if (num > 0 || ["crusader_strike", "holy_strike", "judgement", "consecration"].includes(key)) {
            const row = document.createElement("div");
            row.className = "b-item";
            row.innerHTML = `<span>${castLabelMap[key] || key}:</span><strong>${num}</strong>`;
            const sp = rotationalSpellsByKey[key];
            if (sp) {
              row.style.cursor = "help";
              row.addEventListener("mouseenter", (e) => showSpellTooltip(sp, e));
              row.addEventListener("mousemove", (e) => positionTooltip(e));
              row.addEventListener("mouseleave", hideTooltip);
            }
            castsList.appendChild(row);
          }
        }

        if (data.mana_stats) {
          const manaRow = document.createElement("div");
          manaRow.className = "b-item b-item-mana";
          manaRow.innerHTML = `<span>Zuzycie many:</span><strong class="magic">${data.mana_stats.total_mana_spent} (${data.mana_stats.mana_per_second}/s)</strong>`;
          castsList.appendChild(manaRow);
        }
      }
    } else {
      castsCard.style.display = "none";
    }
  }

  const dtRow = document.getElementById("damage-types-row");
  const dtb = data.damage_type_breakdown;
  if (dtRow && dtb) {
    dtRow.style.display = "flex";
    const elPhysVal = document.getElementById("dt-phys-val");
    const elPhysPct = document.getElementById("dt-phys-pct");
    const elHolyVal = document.getElementById("dt-holy-val");
    const elHolyPct = document.getElementById("dt-holy-pct");
    if (elPhysVal) elPhysVal.textContent = `${dtb.physical_dps.toFixed(2)} DPS`;
    if (elPhysPct) elPhysPct.textContent = `(${dtb.physical_percent}%)`;
    if (elHolyVal) elHolyVal.textContent = `${dtb.holy_spell_dps.toFixed(2)} DPS`;
    if (elHolyPct) elHolyPct.textContent = `(${dtb.holy_spell_percent}%)`;

    const shadowPill = document.getElementById("dt-shadow-pill");
    if (shadowPill) {
      if (dtb.minion_shadow_dps > 0 || (data.has_minions && data.minion_dps > 0)) {
        shadowPill.style.display = "inline-flex";
        const elShadVal = document.getElementById("dt-shadow-val");
        const elShadPct = document.getElementById("dt-shadow-pct");
        if (elShadVal) elShadVal.textContent = `${dtb.minion_shadow_dps.toFixed(2)} DPS`;
        if (elShadPct) elShadPct.textContent = `(${dtb.minion_shadow_percent}%)`;
      } else {
        shadowPill.style.display = "none";
      }
    }
  } else if (dtRow) {
    dtRow.style.display = "none";
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
    document.getElementById("b-active-minions").textContent = (data.expected_active_minions || 0).toFixed(2);
    const bProcs = document.getElementById("b-procs-sec");
    if (bProcs) bProcs.textContent = `${(data.procs_per_second || 0).toFixed(3)} / sec`;
  } else {
    if (minionCard) minionCard.style.display = "none";
    if (minionBreakdownCard) minionBreakdownCard.style.display = "none";
    if (shareBarWrap) shareBarWrap.style.display = "none";
  }

  const breakdownTitle = document.getElementById("breakdown-title");
  if (breakdownTitle) {
    breakdownTitle.innerHTML = `&#9876; ${data.character_class.toUpperCase()} ATTACK BREAKDOWN`;
  }

  lastSimulationData = data;
  renderAttackBreakdown(data);

  const bSwings = document.getElementById("b-exact-swings");
  if (bSwings) bSwings.textContent = data.exact_melee_swings || 0;

  const bSkill = document.getElementById("b-weapon-skill");
  if (bSkill) {
    const ws = data.weapon_skill || data.effective_weapon_skill || 300;
    bSkill.textContent = `${ws} / 315`;
  }
  renderWeaponSkillsDropdown(data.equipped_weapon_skills || []);

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

let isWsDropdownOpen = false;

function toggleWeaponSkillDropdown(e) {
  if (e && e.target && e.target.classList.contains("ws-quest-chk")) return;
  const details = document.getElementById("ws-dropdown-details");
  const chevron = document.getElementById("ws-chevron");
  if (!details) return;
  isWsDropdownOpen = !isWsDropdownOpen;
  details.style.display = isWsDropdownOpen ? "flex" : "none";
  if (chevron) {
    if (isWsDropdownOpen) chevron.classList.add("open");
    else chevron.classList.remove("open");
  }
}

function renderWeaponSkillsDropdown(equippedSkills) {
  const container = document.getElementById("ws-dropdown-details");
  if (!container) return;
  container.innerHTML = "";

  if (!equippedSkills || equippedSkills.length === 0) {
    container.innerHTML = `<div class="ws-empty-hint">Brak założonej broni. Załóż broń wręcz lub dystansową, aby sprawdzić biegłość.</div>`;
    return;
  }

  const slotLabels = {
    main_hand: "Broń Główna (MH)",
    off_hand: "Broń Druga (OH)",
    ranged: "Broń Dystansowa (Ranged)"
  };

  equippedSkills.forEach(item => {
    const card = document.createElement("div");
    card.className = "ws-item-card";

    const sBadge = slotLabels[item.slot] || item.slot;
    const isCapped = item.skill >= 315;
    const glancePct = Math.round((item.glance_damage_factor || 0.70) * 100);
    const hitBonus = (item.hit_bonus || 0).toFixed(1);

    card.innerHTML = `
      <div class="ws-item-header">
        <span class="ws-slot-badge">${sBadge}</span>
        <span class="ws-subclass-badge">${item.subclass_display || item.subclass}</span>
        <strong class="ws-skill-val ${isCapped ? 'ws-capped' : ''}">${item.skill} / ${item.cap || 315}</strong>
      </div>
      <div class="ws-item-name" title="${item.item_name}">${item.item_name}</div>
      <div class="ws-stats-row">
        <span title="Kara Glancing Blows: ${glancePct}% obrażeń (300 skill: 70%, +2%/punkt, cap 100% przy 315)">
          Glance dmg: <strong>${glancePct}%</strong>
        </span>
        <span title="+1% Hit za każde 5 pkt biegłości powyżej 300">
          Hit Bonus: <strong>+${hitBonus}%</strong>
        </span>
      </div>
      <div class="ws-breakdown-sub">
        Bazowe: ${item.base_skill}
        ${item.racial_bonus ? ` | Racial: +${item.racial_bonus}` : ''}
        ${item.item_bonus ? ` | Ekwipunek: +${item.item_bonus}` : ''}
        ${item.talent_bonus ? ` | Talenty: +${item.talent_bonus}` : ''}
        ${item.quest_bonus ? ` | Quest: +${item.quest_bonus}` : ''}
      </div>
      <label class="ws-quest-toggle" title="Zaznacz, jeśli wykonałeś zadanie na +5 biegłości dla tej broni na Octo WoW">
        <input type="checkbox" class="ws-quest-chk" data-type="${item.weapon_type_key}" data-subclass="${item.subclass}" data-slot="${item.slot}" ${item.quest_active ? 'checked' : ''}>
        <span>⭐ +5 Quest Bonus (${item.subclass_display || item.subclass} Octo WoW)</span>
      </label>
    `;

    const chk = card.querySelector(".ws-quest-chk");
    if (chk) {
      chk.addEventListener("click", (e) => e.stopPropagation());
      chk.addEventListener("change", (e) => {
        const typeKey = e.target.getAttribute("data-type");
        const subKey = e.target.getAttribute("data-subclass");
        const slotKey = e.target.getAttribute("data-slot");
        const isChecked = e.target.checked;
        if (typeKey) questWeaponSkills[typeKey] = isChecked;
        if (subKey) questWeaponSkills[subKey] = isChecked;
        if (slotKey) questWeaponSkills[slotKey] = isChecked;
        recalculateLiveStats();
        runSimulation();
      });
    }

    container.appendChild(card);
  });
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

  const rotTabBtn = document.getElementById("tab-btn-rotation");
  if (rotTabBtn) {
    rotTabBtn.style.display = currentClass === "paladin" ? "inline-block" : "none";
  }

  const thirdSlotCard = document.getElementById("slot-card-third");
  const thirdSlotTitle = document.getElementById("third-slot-title");
  const thirdInput = document.getElementById("input-third");
  const thirdIcon = document.getElementById("icon-third");

  const btnEnchThird = document.getElementById("btn-ench-third");
  if (thirdSlotCard && thirdSlotTitle && thirdInput) {
    if (currentClass === "warrior") {
      thirdSlotCard.setAttribute("data-slot", "ranged");
      thirdSlotTitle.textContent = "Ranged Weapon";
      thirdInput.setAttribute("data-slot", "ranged");
      thirdInput.placeholder = "Search bows, guns, crossbows...";
      if (thirdIcon) thirdIcon.textContent = getSlotSymbol("ranged");
      if (btnEnchThird) {
        btnEnchThird.style.display = "inline-flex";
        btnEnchThird.setAttribute("data-slot", "ranged");
        btnEnchThird.title = "Select Scope (Ranged)";
      }
    } else {
      thirdSlotCard.setAttribute("data-slot", "relic");
      thirdSlotTitle.textContent = "Libram / Relic";
      thirdInput.setAttribute("data-slot", "relic");
      thirdInput.placeholder = "Search librams...";
      if (thirdIcon) thirdIcon.textContent = getSlotSymbol("relic");
      if (btnEnchThird) {
        btnEnchThird.style.display = "none";
        delete currentEnchants["relic"];
        delete currentEnchants["ranged"];
      }
    }
  }

  const judgeItem = document.getElementById("setting-judge-item");
  const exoItem = document.getElementById("setting-exorcism-item");
  const palChecks = document.getElementById("setting-paladin-checks");
  const palSealBox = document.getElementById("paladin-seal-config-box");
  if (judgeItem) judgeItem.style.display = currentClass === "paladin" ? "flex" : "none";
  if (exoItem) exoItem.style.display = currentClass === "paladin" ? "flex" : "none";
  if (palChecks) palChecks.style.display = currentClass === "paladin" ? "flex" : "none";
  if (palSealBox) palSealBox.style.display = currentClass === "paladin" ? "block" : "none";

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
          } else if (currentClass === "paladin" && slotKey === "off_hand" && (it.subclass !== "shield" && it.slot !== "shield" && (it.speed > 0 || ["sword", "mace", "axe"].includes(it.subclass)))) {
            unequipItem(slotKey);
          } else if (currentClass === "paladin" && (slotKey === "relic" || slotKey === "ranged") && it.subclass !== "libram") {
            unequipItem(slotKey);
          } else if (currentClass === "warrior" && (slotKey === "relic" || ["wand", "libram", "totem", "idol"].includes(it.subclass))) {
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

  fetch("/api/class_equipment_rules")
    .then(res => res.json())
    .then(rules => {
      classEquipmentRules = rules;
    })
    .catch(() => {});

  loadTalentsForClass(currentClass);
  loadRotationalSpells();

  const rowSkill = document.getElementById("stat-row-skill");
  if (rowSkill) {
    rowSkill.addEventListener("click", toggleWeaponSkillDropdown);
  }

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
        const ohItem = itemsById[String(equippedItems.off_hand)];
        category = (ohItem && (ohItem.slot === "shield" || ohItem.subclass === "shield")) ? "shield" : "offhand";
      } else if (activeEnchantSlot === "relic" || activeEnchantSlot === "ranged") {
        category = "ranged";
      } else if (activeEnchantSlot === "finger1" || activeEnchantSlot === "finger2") {
        category = "finger";
      } else if (activeEnchantSlot === "neck") {
        category = "neck";
      } else if (activeEnchantSlot === "waist") {
        category = "waist";
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

  const rotMain = document.getElementById("cfg-rotation-mode");
  const rotQuick = document.getElementById("cfg-rotation-mode-quick");
  const rotSettings = document.getElementById("cfg-rotation-mode-settings");
  if (rotMain) {
    rotMain.addEventListener("change", (e) => syncRotationMode(e.target.value));
  }
  if (rotQuick) {
    rotQuick.addEventListener("change", (e) => syncRotationMode(e.target.value));
  }
  if (rotSettings) {
    rotSettings.addEventListener("change", (e) => syncRotationMode(e.target.value));
  }

  const btnResetRot = document.getElementById("btn-reset-rotation");
  if (btnResetRot) {
    btnResetRot.addEventListener("click", () => {
      activePriorityList = ["hammer_of_wrath", "crusader_holy_strike", "judgement", "consecration", "exorcism"];
      strikeRampCs = 3;
      strikeSustainHs = 1;
      strikeSustainCs = 1;
      disabledSpells.clear();
      renderPriorityList();
      runSimulation();
    });
  }

  // Attack Breakdown toolbar buttons
  document.getElementById("btn-bd-mode-dps")?.addEventListener("click", () => setBreakdownViewMode("dps"));
  document.getElementById("btn-bd-mode-damage")?.addEventListener("click", () => setBreakdownViewMode("damage"));
  document.getElementById("btn-bd-sort-btn")?.addEventListener("click", toggleBreakdownSort);

  // Paladin Seal & Opener controls
  document.getElementById("cfg-primary-seal")?.addEventListener("change", () => {
    validatePaladinSealTalents();
    runSimulation();
  });
  document.getElementById("cfg-opener-crusader")?.addEventListener("change", () => {
    runSimulation();
  });

  document.querySelectorAll(".info-circle").forEach(circle => {
    const infoKey = circle.getAttribute("data-info");
    if (!infoKey) return;
    circle.addEventListener("mouseenter", (e) => showInfoTooltip(infoKey, e));
    circle.addEventListener("mousemove", (e) => positionTooltip(e));
    circle.addEventListener("mouseleave", hideTooltip);
    circle.addEventListener("focus", (e) => showInfoTooltip(infoKey, e));
    circle.addEventListener("blur", hideTooltip);
  });

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
