/* 하데스2 빌드 길잡이 — UI (ui/SPEC.md 3-A 구현)
   엔진은 window.createHadesEngine / window.HADES_WEIGHTS 를 그대로 쓴다. 수정하지 않는다. */
(function () {
  'use strict';
  var DATA = JSON.parse(document.getElementById('h2-data').textContent);
  var W = window.HADES_WEIGHTS;
  var E = window.createHadesEngine(DATA, W);

  // ── 인덱스 ─────────────────────────────────────────────
  var IX = {};
  ['boons', 'duos', 'hammers', 'weapons', 'arcana', 'keepsakes', 'hexes', 'gods'].forEach(function (k) {
    IX[k] = {}; DATA[k].forEach(function (o) { IX[k][o.id] = o; });
  });
  var ASP = {};
  DATA.weapons.forEach(function (w) { (w.aspects || []).forEach(function (a) { ASP[a.id] = a; }); });
  var ent = function (id) { return IX.boons[id] || IX.duos[id] || IX.hammers[id] || IX.keepsakes[id] || IX.hexes[id] || IX.arcana[id] || IX.gods[id] || ASP[id] || null; };
  var nm = function (id) { var o = ent(id); return o ? o.name_ko : id; };

  var SLOTS = ['attack', 'special', 'cast', 'sprint', 'magick'];
  var SK = { attack: '공', special: '기', cast: '마', sprint: '질', magick: '력' };
  var SKO = W.SLOT_KO;
  var GC = { zeus: '#f2d16b', hestia: '#ff8a3d', poseidon: '#4aa3ff', demeter: '#7ed491', apollo: '#ffd166', aphrodite: '#ff7eb6', hephaestus: '#c97b4a', hera: '#b58cff', ares: '#e05252', hermes: '#c0c7d1', artemis: '#5fbf8a', selene: '#a9c4ff', chaos: '#c76bd9' };
  var GOD_ORDER = ['zeus', 'hestia', 'poseidon', 'demeter', 'apollo', 'aphrodite', 'hephaestus', 'hera', 'ares', 'hermes', 'artemis', 'selene', 'chaos'];
  var RAR = ['common', 'rare', 'epic', 'heroic'];
  var RAR_KO = { common: '일반', rare: '희귀', epic: '특별', heroic: '영웅' };

  // ── 저장 ───────────────────────────────────────────────
  var saveFail = false;
  function ls(k, v) {
    try {
      if (v === undefined) { var s = localStorage.getItem(k); return s ? JSON.parse(s) : null; }
      localStorage.setItem(k, JSON.stringify(v)); return true;
    } catch (e) { saveFail = true; return v === undefined ? null : false; }
  }
  var PREFS = ls('h2.prefs.v1') || { owned_keepsakes: [], grasp_cap: 10, left_hand: false, show_score: true, last_weapon: 'staff', last_aspect: 'staff_melinoe' };
  var UI = ls('h2.ui.v1') || { screen: null, god_tab: null };
  var RUN = ls('h2.run.v1');
  var savePrefs = function () { ls('h2.prefs.v1', PREFS); };
  var saveUI = function () { ls('h2.ui.v1', UI); };
  var saveRun = function () { ls('h2.run.v1', RUN); };

  function newRun(weapon, aspect) {
    return { state: { weapon: weapon, aspect: aspect, region: 1, boons: [], hammers: [], arcana: [], keepsake: null, hex: null, gods_seen: [], hp_state: 'mid', direction_lock: null }, pending_god: null, history: [] };
  }
  function pushHistory(label) {
    RUN.history.unshift({ ts: Date.now(), label: label, snap: JSON.stringify(RUN.state) });
    if (RUN.history.length > 10) RUN.history.length = 10;
  }
  function undo() {
    if (!RUN.history.length) return toast('되돌릴 기록이 없습니다');
    RUN.state = JSON.parse(RUN.history.shift().snap); saveRun(); render();
  }

  // ── 유틸 ───────────────────────────────────────────────
  var esc = function (s) { return String(s == null ? '' : s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };
  var toastT;
  function toast(msg) {
    var t = document.getElementById('toast'); t.textContent = msg; t.hidden = false;
    clearTimeout(toastT); toastT = setTimeout(function () { t.hidden = true; }, 2600);
  }
  function slotChip(o) {
    if (o && o.kind === 'duo') return '<span class="slotchip duo">융</span>';
    if (o && (o.slot === 'legendary' || o.kind === 'legendary')) return '<span class="slotchip leg">전</span>';
    var s = o && SK[o.slot] ? SK[o.slot] : '·';
    return '<span class="slotchip">' + s + '</span>';
  }
  function badgeHtml(b) {
    var key = b.indexOf('방향 전환') === 0 ? '전환' : b.replace(/\s/g, '');
    return '<span class="badge b-' + esc(key) + '">' + esc(b) + '</span>';
  }
  function el(html) { var d = document.createElement('div'); d.innerHTML = html; return d.firstElementChild; }

  // ── 화면 전환 ──────────────────────────────────────────
  var sheet = null;
  function openSheet(name) { UI.screen = name; saveUI(); history.pushState({ sheet: name }, ''); render(); }
  function closeSheet() { if (UI.screen) { UI.screen = null; saveUI(); render(); } }
  window.addEventListener('popstate', function () { if (UI.screen) { UI.screen = null; saveUI(); render(); } });

  // ── 렌더 ───────────────────────────────────────────────
  var app = document.getElementById('app');
  function render() {
    app.innerHTML = '';
    if (!RUN) { app.appendChild(viewStart()); return; }
    app.appendChild(viewHome());
    if (UI.screen === 'gods') app.appendChild(viewGods());
    else if (UI.screen === 'boons') app.appendChild(viewPick('boon'));
    else if (UI.screen === 'hammers') app.appendChild(viewPick('hammer'));
    else if (UI.screen === 'manage') app.appendChild(viewManage());
    else if (UI.screen === 'start') app.appendChild(wrapSheet('새 런 시작', viewStart(true)));
  }
  function wrapSheet(title, inner) {
    var s = el('<div class="sheet"><div class="top"><button class="iconbtn" data-close>✕</button><div class="t">' + esc(title) + '</div></div><div class="body"></div></div>');
    s.querySelector('[data-close]').onclick = closeSheet;
    s.querySelector('.body').appendChild(inner);
    return s;
  }

  // ── 1. 런 시작 ─────────────────────────────────────────
  var startSel = { weapon: PREFS.last_weapon, aspect: PREFS.last_aspect };
  function viewStart(asSheet) {
    var root = document.createElement('div');
    if (!asSheet) root.appendChild(el('<div class="top"><div class="t">하데스2 빌드 길잡이</div></div>'));
    if (saveFail) root.appendChild(el('<div class="banner">저장이 안 됩니다 — 이 탭을 닫으면 사라져요</div>'));

    root.appendChild(el('<h2>무기</h2>'));
    var wg = el('<div class="wgrid"></div>');
    DATA.weapons.forEach(function (w) {
      var ready = w.unlock_order <= 4;
      var b = el('<button class="wcard" ' + (ready ? '' : 'disabled') + ' aria-pressed="' + (startSel.weapon === w.id) + '">' +
        '<div class="n">' + esc(w.name_ko) + '</div><div class="a">' + esc(ready ? (w.alias_ko || '') : '준비 중') + '</div></button>');
      if (ready) b.onclick = function () { startSel.weapon = w.id; startSel.aspect = w.aspects[0].id; rerenderStart(root, asSheet); };
      wg.appendChild(b);
    });
    root.appendChild(wg);

    var wp = IX.weapons[startSel.weapon];
    root.appendChild(el('<h2>양상</h2>'));
    var ch = el('<div class="chips"></div>');
    wp.aspects.forEach(function (a) {
      var locked = !!a.hidden;
      var b = el('<button class="chip" aria-pressed="' + (startSel.aspect === a.id) + '">' + esc(a.name_ko) + (locked ? ' 🔒' : '') + '</button>');
      b.onclick = locked ? function () { toast('숨겨진 양상 — 해금 후 사용'); } : function () { startSel.aspect = a.id; rerenderStart(root, asSheet); };
      ch.appendChild(b);
    });
    root.appendChild(ch);
    root.appendChild(el('<div class="wrap sm dim">' + esc(wp.beginner_note || '') + '</div>'));

    var r = E.recommendRunStart(startSel.weapon, startSel.aspect, { graspCap: PREFS.grasp_cap, ownedKeepsakes: PREFS.owned_keepsakes.length ? PREFS.owned_keepsakes : null });

    root.appendChild(el('<h2>아르카나 (이해도 ' + r.arcana.grasp_used + '/' + r.arcana.grasp_cap + ')</h2>'));
    var ac = el('<div class="card tight"></div>');
    r.arcana.cards.forEach(function (c) {
      ac.appendChild(el('<div class="row" style="padding:6px 0"><span class="slotchip">' + c.grasp + '</span><div class="mid" style="flex:1;min-width:0"><div class="ell">' + esc(c.name_ko) + '</div><div class="xs dim ell">' + esc(c.effect) + '</div></div></div>'));
    });
    root.appendChild(ac);
    if (r.arcana.free_cards.length) {
      var det = el('<details class="card tight"><summary class="sm dim">각성 조건 충족 시 무료 (' + r.arcana.free_cards.length + '장)</summary></details>');
      r.arcana.free_cards.forEach(function (c) {
        det.appendChild(el('<div style="padding:6px 0"><div class="sm">' + esc(c.name_ko) + '</div><div class="xs dim">' + esc(c.awaken_condition || '') + '</div></div>'));
      });
      root.appendChild(det);
    }

    root.appendChild(el('<h2>기념품 · 비술</h2>'));
    var kc = el('<div class="card tight"></div>');
    r.keepsakes.slice(0, 3).forEach(function (k) { kc.appendChild(el('<div style="padding:5px 0"><div class="sm">' + esc(k.name_ko) + '</div><div class="xs dim ell">' + esc(k.effect) + '</div></div>')); });
    r.hexes.slice(0, 2).forEach(function (h) { kc.appendChild(el('<div style="padding:5px 0"><div class="sm">' + esc(h.name_ko) + ' <span class="xs dim">마력 ' + h.mana + '</span></div><div class="xs dim ell">' + esc(h.effect) + '</div></div>')); });
    root.appendChild(kc);

    root.appendChild(el('<h2>열린 빌드 방향</h2>'));
    root.appendChild(el('<div class="wrap sm dim">' + esc(r.note) + '</div>'));
    r.directions.forEach(function (d) {
      root.appendChild(el('<div class="card"><div class="row"><b>' + esc(d.name_ko) + '</b><span class="xs dim">★' + d.difficulty + '</span></div>' +
        '<div class="sm dim" style="margin-top:4px">' + esc(d.summary) + '</div>' +
        '<div class="xs dim" style="margin-top:6px">핵심 칸: ' + esc(d.core_slots.join(' · ')) + '</div>' +
        '<div class="xs dim">' + esc(d.first_picks.join(' / ')) + '</div>' +
        (d.target_duos.length ? '<div class="xs dim">노리는 융합: ' + esc(d.target_duos.join(', ')) + '</div>' : '') +
        (d.key_hammers.length ? '<div class="xs dim">망치: ' + esc(d.key_hammers.join(', ')) + '</div>' : '') + '</div>'));
    });

    var cta = el('<div class="cta"><button>이 무기로 시작</button></div>');
    cta.querySelector('button').onclick = function () {
      if (RUN && RUN.state.boons.length && !confirm('진행 중인 런이 사라집니다. 새로 시작할까요?')) return;
      PREFS.last_weapon = startSel.weapon; PREFS.last_aspect = startSel.aspect; savePrefs();
      RUN = newRun(startSel.weapon, startSel.aspect); saveRun(); UI.screen = null; saveUI(); render();
    };
    root.appendChild(cta);
    return root;
  }
  function rerenderStart(root, asSheet) {
    var fresh = viewStart(asSheet); root.replaceWith(fresh);
    if (!asSheet) { app.innerHTML = ''; app.appendChild(fresh); }
  }

  // ── 2. 홈 ──────────────────────────────────────────────
  function viewHome() {
    var st = RUN.state;
    var root = document.createElement('div');
    var wp = IX.weapons[st.weapon];
    var top = el('<div class="top"><div class="t">' + esc(wp.name_ko) + '</div>' +
      '<button class="iconbtn" data-undo title="되돌리기">↶</button></div>');
    top.querySelector('[data-undo]').onclick = undo;
    root.appendChild(top);
    if (saveFail) root.appendChild(el('<div class="banner">저장이 안 됩니다 — 이 탭을 닫으면 사라져요</div>'));

    var warn = E.validateState(st);
    if (warn.length) root.appendChild(el('<div class="banner">' + esc(warn.join(' · ')) + '</div>'));

    var ds = E.directionScores(st);
    var card = el('<div class="card"></div>');
    var hp = { high: '●●●', mid: '●●○', low: '●○○' }[st.hp_state];
    var meta = el('<div class="row sm dim"><span>' + esc((IX.weapons[st.weapon].aspects.find(function (a) { return a.id === st.aspect; }) || {}).name_ko || '') + '</span>' +
      '<button class="tagx" data-region>' + st.region + '지역</button><button class="tagx" data-hp>' + hp + '</button>' +
      (st.direction_lock ? '<span class="tagx">🔒 고정</span>' : '') + '</div>');
    meta.querySelector('[data-region]').onclick = function () { openSheet('manage'); };
    meta.querySelector('[data-hp]').onclick = function () { cycleHp(); };
    card.appendChild(meta);

    if (ds.length) {
      var m = ds[0];
      card.appendChild(el('<div style="margin-top:8px"><div class="row"><b>' + esc(m.name_ko) + '</b>' +
        '<span class="xs dim">' + Math.round(m.weight * 100) + '%</span>' +
        (ds[1] ? '<span class="xs dim" style="margin-left:auto">보험 ' + esc(ds[1].name_ko) + '</span>' : '') + '</div>' +
        '<div class="bar"><i style="width:' + Math.round(m.weight * 100) + '%"></i></div></div>'));
    } else card.appendChild(el('<div class="sm dim" style="margin-top:8px">아직 방향 정보가 없습니다</div>'));

    var smap = {};
    st.boons.forEach(function (id) { var b = IX.boons[id]; if (b && b.occupies_slot) smap[b.slot] = b; });
    var sl = el('<div class="slots"></div>');
    var core = ds.length ? (ds[0].filled || []) : [];
    SLOTS.forEach(function (s) {
      var b = smap[s], f = core.find(function (x) { return x.slot === s; });
      var cls = 'slot ' + (b ? 'filled' : 'empty') + (f && f.core ? ' core' : '');
      var style = b ? ' style="--gc:' + GC[b.god] + '"' : '';
      sl.appendChild(el('<div class="' + cls + '"' + style + '><div class="k">' + SK[s] + '</div>' +
        '<div class="v">' + esc(b ? b.name_ko : '빈 칸') + '</div></div>'));
    });
    card.appendChild(sl);

    if (ds.length) {
      var det = el('<details style="margin-top:8px"><summary class="sm dim">다음에 원하는 것 · 융합 진행도</summary></details>');
      var nw = ds[0].next_wants.slice(0, 3).map(function (x) { return x.slot_ko + ' ' + x.name_ko; }).join(' · ');
      det.appendChild(el('<div class="sm" style="margin-top:6px">' + esc(nw || '핵심 칸이 다 찼습니다') + '</div>'));
      ds[0].duo_progress.slice(0, 3).forEach(function (d) {
        det.appendChild(el('<div class="prog"><span class="xs" style="width:96px" class="ell">' + esc(d.name_ko) + '</span>' +
          '<div class="bar"><i style="width:' + Math.round(d.satisfied / d.total * 100) + '%"></i></div>' +
          '<span class="xs dim">' + d.satisfied + '/' + d.total + '</span></div>'));
      });
      card.appendChild(det);
    }
    root.appendChild(card);

    var owned = st.boons.length + st.hammers.length;
    root.appendChild(el('<div class="wrap xs dim">보유 은혜 ' + st.boons.length + ' · 망치 ' + st.hammers.length + ' · 만난 신 ' + st.gods_seen.length + '</div>'));

    var A = ['gods', '신 선택', '⚱'], B = ['boons', '은혜 선택', '✦'], C = ['hammers', '망치 선택', '🔨'], D = ['manage', '관리', '⚙'];
    var order = PREFS.left_hand ? [B, A, D, C] : [A, B, C, D];
    var dock = el('<div class="dock"></div>');
    order.forEach(function (o) {
      var b = el('<button class="' + (o[0] === 'boons' ? 'primary' : '') + '"><span class="ic">' + o[2] + '</span>' + o[1] + '</button>');
      b.onclick = function () { openSheet(o[0]); };
      dock.appendChild(b);
    });
    root.appendChild(dock);
    return root;
  }
  function cycleHp() {
    var o = ['high', 'mid', 'low'], i = o.indexOf(RUN.state.hp_state);
    RUN.state.hp_state = o[(i + 1) % 3]; saveRun(); render();
  }

  // ── 3. 신 선택 ─────────────────────────────────────────
  var godSel = [];
  function viewGods() {
    var body = document.createElement('div');
    body.appendChild(el('<div class="wrap sm dim" style="padding-top:10px">문 위에 뜬 신을 2개 이상 골라 주세요</div>'));
    var grid = el('<div class="gods"></div>');
    var out = el('<div></div>');
    var btns = {};
    GOD_ORDER.forEach(function (id) {
      var seen = RUN.state.gods_seen.indexOf(id) >= 0;
      var b = el('<button class="god" aria-pressed="false" style="border-color:' + GC[id] + '">' +
        '<span class="dot" style="background:' + GC[id] + '"></span><span class="n">' + esc(nm(id)) + '</span>' +
        (seen ? '<span class="seen">✓ 받음</span>' : '') + '</button>');
      b.onclick = function () {
        var i = godSel.indexOf(id);
        if (i >= 0) godSel.splice(i, 1); else godSel.push(id);
        refresh();
      };
      btns[id] = b; grid.appendChild(b);
    });
    body.appendChild(grid); body.appendChild(out);

    function refresh() {
      GOD_ORDER.forEach(function (id) { btns[id].setAttribute('aria-pressed', godSel.indexOf(id) >= 0); });
      out.innerHTML = '';
      if (godSel.length < 2) { out.appendChild(el('<div class="empty">신을 2개 이상 골라 주세요</div>')); return; }
      E.recommendGods(RUN.state, godSel).forEach(function (r, i) {
        out.appendChild(recCard(r, i, function () {
          RUN.pending_god = r.id; pickSel = []; godTab = r.id;
          UI.screen = 'boons'; saveUI(); saveRun(); render();
        }, '이 문으로'));
      });
    }
    refresh();
    return wrapSheet('신 선택', body);
  }

  // ── 4·5. 은혜 / 망치 선택 ──────────────────────────────
  var pickSel = [], godTab = null, searchOn = false, searchQ = '';
  function viewPick(kind) {
    var isBoon = kind === 'boon';
    if (isBoon && RUN.pending_god) { godTab = RUN.pending_god; RUN.pending_god = null; saveRun(); }
    if (isBoon && !godTab) godTab = UI.god_tab || RUN.state.gods_seen[RUN.state.gods_seen.length - 1] || 'zeus';
    var body = document.createElement('div');
    var listBox = el('<div class="list"></div>');
    var recBox = el('<div></div>');
    var trayBox = el('<div class="tray"></div>');

    if (isBoon) {
      var top = el('<div class="row" style="padding:8px 14px 0"><div class="sm dim" style="flex:1">게임에 뜬 은혜를 2~3개 탭</div><button class="iconbtn" data-s>🔍</button></div>');
      top.querySelector('[data-s]').onclick = function () { searchOn = !searchOn; if (!searchOn) searchQ = ''; draw(); };
      body.appendChild(top);
      var sbox = el('<div class="wrap" style="padding-bottom:8px"></div>');
      body.appendChild(sbox);
      var tabs = el('<div class="chips"></div>');
      GOD_ORDER.forEach(function (id) {
        var b = el('<button class="chip" aria-pressed="' + (godTab === id) + '" style="border-color:' + GC[id] + '">' + esc(nm(id)) + '</button>');
        b.onclick = function () { godTab = id; UI.god_tab = id; saveUI(); searchQ = ''; draw(); };
        tabs.appendChild(b);
      });
      body.appendChild(tabs);
      body._sbox = sbox;
    } else {
      body.appendChild(el('<div class="wrap sm dim" style="padding:10px 14px 4px">게임에 뜬 다이달로스 망치를 2~3개 탭</div>'));
    }
    body.appendChild(listBox);
    body.appendChild(recBox);

    function candidates() {
      if (!isBoon) return DATA.hammers.filter(function (h) { return h.weapon === RUN.state.weapon; });
      if (searchQ) {
        var q = searchQ.trim();
        return DATA.boons.filter(function (b) { return b.name_ko.indexOf(q) >= 0; })
          .concat(DATA.duos.filter(function (d) { return d.name_ko.indexOf(q) >= 0; })).slice(0, 40);
      }
      var bs = DATA.boons.filter(function (b) { return b.god === godTab; });
      var ord = function (b) { var i = SLOTS.indexOf(b.slot); return i >= 0 ? i : (b.slot === 'passive' ? 5 : b.slot === 'infusion' ? 6 : 7); };
      bs.sort(function (a, b) { return ord(a) - ord(b); });
      var ds = DATA.duos.filter(function (d) { return d.gods.indexOf(godTab) >= 0; });
      return bs.concat(ds);
    }

    function draw() {
      if (isBoon) {
        var sb = body._sbox; sb.innerHTML = '';
        if (searchOn) {
          var inp = el('<input type="search" placeholder="은혜 이름 검색" value="' + esc(searchQ) + '">');
          inp.oninput = function () { searchQ = inp.value; drawList(); };
          sb.appendChild(inp);
        }
      }
      drawList(); drawTray(); drawRec();
    }
    function drawList() {
      listBox.innerHTML = '';
      var owned = RUN.state.boons.concat(RUN.state.hammers);
      candidates().forEach(function (o) {
        var picked = pickSel.some(function (p) { return p.id === o.id; });
        var isOwned = owned.indexOf(o.id) >= 0;
        var sub = o.kind === 'duo' ? '융합 (' + o.gods.map(nm).join('·') + ')' : (o.effect || '');
        // 현재 양상에서 등장하지 않는 망치는 흐리게 + 사유 표시 (SPEC 3-5)
        var aspOnly = o.aspect_only && o.aspect_only !== RUN.state.aspect;
        var aspEx = (o.aspect_excluded || []).indexOf(RUN.state.aspect) >= 0;
        var extra = isOwned ? '<span class="tagx">보유</span>'
          : aspOnly ? '<span class="tagx">' + esc(nm(o.aspect_only)) + ' 전용</span>'
          : aspEx ? '<span class="tagx">이 양상 제외</span>' : '';
        var b = el('<button class="item ' + (isOwned || aspOnly || aspEx ? 'off' : '') + '" aria-pressed="' + picked + '">' + slotChip(o) +
          '<div class="mid"><div class="nm ell">' + esc(o.name_ko) + '</div><div class="ef ell">' + esc(sub) + '</div></div>' + extra + '</button>');
        b.onclick = function () {
          var i = pickSel.findIndex(function (p) { return p.id === o.id; });
          if (i >= 0) pickSel.splice(i, 1);
          else {
            if (pickSel.length >= 3) pickSel.shift();
            pickSel.push({ id: o.id, rarity: o.kind === 'duo' ? 'duo' : (o.slot === 'legendary' ? 'legendary' : 'common') });
          }
          draw();
        };
        listBox.appendChild(b);
      });
      if (!listBox.children.length) listBox.appendChild(el('<div class="empty">해당하는 항목이 없습니다</div>'));
    }
    function drawTray() {
      trayBox.innerHTML = '';
      var picks = el('<div class="picks"></div>');
      if (!pickSel.length) picks.appendChild(el('<span class="sm dim">아직 고른 게 없습니다</span>'));
      pickSel.forEach(function (p, i) {
        var fixed = p.rarity === 'duo' || p.rarity === 'legendary';
        var c = el('<span class="pick">' + esc(nm(p.id)) +
          (fixed ? '' : '<button class="rar">' + RAR_KO[p.rarity] + '</button>') + '<button class="x">✕</button></span>');
        if (!fixed) c.querySelector('.rar').onclick = function () { p.rarity = RAR[(RAR.indexOf(p.rarity) + 1) % 4]; draw(); };
        c.querySelector('.x').onclick = function () { pickSel.splice(i, 1); draw(); };
        picks.appendChild(c);
      });
      trayBox.appendChild(picks);
    }
    function drawRec() {
      recBox.innerHTML = '';
      if (pickSel.length < 2) { recBox.appendChild(el('<div class="empty">2개 이상 고르면 바로 추천이 나옵니다</div>')); return; }
      var rows = isBoon ? E.recommendBoons(RUN.state, pickSel) : E.recommendHammers(RUN.state, pickSel.map(function (p) { return p.id; }));
      rows.forEach(function (r, i) {
        recBox.appendChild(recCard(r, i, function () {
          pushHistory((isBoon ? '은혜' : '망치') + ' ' + nm(r.id));
          var rar = (pickSel.find(function (p) { return p.id === r.id; }) || {}).rarity;
          RUN.state = E.applyChoice(RUN.state, { kind: isBoon ? 'boon' : 'hammer', id: r.id, rarity: rar });
          pickSel = []; saveRun(); closeSheet();
        }, '이걸로 결정'));
      });
    }
    draw();
    var s = wrapSheet(isBoon ? '은혜 선택' : '망치 선택', body);
    s.appendChild(trayBox);
    return s;
  }

  function recCard(r, i, onDecide, label) {
    var no = !isFinite(r.score);
    var c = el('<div class="rec ' + (i === 0 && !no ? 'r1' : '') + ' ' + (no ? 'no' : '') + '">' +
      '<div class="hd"><span class="rk">' + (r.rank || i + 1) + '위</span>' +
      (PREFS.show_score && !no ? '<span class="sc">' + r.score + '</span>' : '') + '</div>' +
      '<div class="nm">' + slotChip(ent(r.id)) + '<span class="ell">' + esc(nm(r.id)) + '</span></div>' +
      '<div class="rs">' + esc(r.reason) + '</div>' +
      ((r.badges && r.badges.length) ? '<div class="bg">' + r.badges.map(badgeHtml).join('') + '</div>' : '') +
      ((r.warnings && r.warnings.length) ? '<div class="warns">' + r.warnings.map(function (w) { return '<div>⚠ ' + esc(w) + '</div>'; }).join('') + '</div>' : '') +
      (no ? '' : '<div class="act"><button>' + esc(label) + '</button></div>') + '</div>');
    if (!no) c.querySelector('.act button').onclick = onDecide;
    if (r.breakdown) {
      var t;
      var start = function () { t = setTimeout(function () { toast(nm(r.id) + ' → ' + JSON.stringify(r.breakdown)); }, 500); };
      var stop = function () { clearTimeout(t); };
      c.addEventListener('touchstart', start, { passive: true }); c.addEventListener('touchend', stop);
      c.addEventListener('mousedown', start); c.addEventListener('mouseup', stop); c.addEventListener('mouseleave', stop);
    }
    return c;
  }

  // ── 6. 관리 ────────────────────────────────────────────
  function viewManage() {
    var st = RUN.state, body = document.createElement('div');
    function seg(label, opts, cur, cb) {
      var r = el('<div class="mrow"><div class="lb">' + esc(label) + '</div></div>');
      var s = el('<div class="seg" style="flex:1.4"></div>');
      opts.forEach(function (o) {
        var b = el('<button aria-pressed="' + (cur === o[0]) + '">' + esc(o[1]) + '</button>');
        b.onclick = function () { cb(o[0]); };
        s.appendChild(b);
      });
      r.appendChild(s); return r;
    }
    body.appendChild(seg('체력', [['high', '●●●'], ['mid', '●●○'], ['low', '●○○']], st.hp_state, function (v) { st.hp_state = v; saveRun(); render(); }));
    body.appendChild(seg('지역', [[1, '1'], [2, '2'], [3, '3'], [4, '4']], st.region, function (v) { st.region = v; saveRun(); render(); }));

    var k = E.recommendKeepsake(st);
    if (k && k.id) {
      var kc = el('<div class="card"><div class="xs dim">다음 지역 기념품 추천</div><div class="row" style="margin-top:4px"><b style="flex:1">' + esc(k.name_ko) + '</b><button class="tagx" data-k>이걸로</button></div><div class="sm dim" style="margin-top:4px">' + esc(k.reason) + '</div></div>');
      kc.querySelector('[data-k]').onclick = function () { pushHistory('기념품 ' + k.name_ko); st.keepsake = k.id; saveRun(); render(); };
      body.appendChild(kc);
    }

    body.appendChild(el('<h2>비술</h2>'));
    var hx = el('<div class="chips"></div>');
    DATA.hexes.forEach(function (h) {
      var b = el('<button class="chip" aria-pressed="' + (st.hex === h.id) + '">' + esc(h.name_ko) + '</button>');
      b.onclick = function () { st.hex = st.hex === h.id ? null : h.id; saveRun(); render(); };
      hx.appendChild(b);
    });
    body.appendChild(hx);

    body.appendChild(el('<h2>방향 고정</h2>'));
    var dl = el('<div class="chips"></div>');
    E.directionScores(st).forEach(function (d) {
      var b = el('<button class="chip" aria-pressed="' + (st.direction_lock === d.id) + '">' + esc(d.name_ko) + '</button>');
      b.onclick = function () { st.direction_lock = st.direction_lock === d.id ? null : d.id; saveRun(); render(); };
      dl.appendChild(b);
    });
    body.appendChild(dl);

    body.appendChild(el('<h2>보유 목록</h2>'));
    var ol = el('<div class="list"></div>');
    st.boons.concat(st.hammers).forEach(function (id) {
      var r = el('<div class="item"><div class="mid"><div class="nm ell">' + esc(nm(id)) + '</div></div><button class="tagx">✕</button></div>');
      r.querySelector('button').onclick = function () {
        pushHistory('제거 ' + nm(id));
        st.boons = st.boons.filter(function (x) { return x !== id; });
        st.hammers = st.hammers.filter(function (x) { return x !== id; });
        saveRun(); render();
      };
      ol.appendChild(r);
    });
    if (!ol.children.length) ol.appendChild(el('<div class="empty">아직 없습니다</div>'));
    body.appendChild(ol);

    body.appendChild(el('<h2>기록</h2>'));
    var hl = el('<div class="list"></div>');
    RUN.history.forEach(function (h) { hl.appendChild(el('<div class="item"><div class="mid sm ell">' + esc(h.label) + '</div></div>')); });
    if (!hl.children.length) hl.appendChild(el('<div class="empty">아직 없습니다</div>'));
    body.appendChild(hl);

    body.appendChild(el('<h2>설정</h2>'));
    body.appendChild(seg('왼손 모드', [[false, '끔'], [true, '켬']], PREFS.left_hand, function (v) { PREFS.left_hand = v; savePrefs(); render(); }));
    body.appendChild(seg('점수 표시', [[true, '켬'], [false, '끔']], PREFS.show_score, function (v) { PREFS.show_score = v; savePrefs(); render(); }));
    body.appendChild(seg('이해도 상한', [[10, '10'], [15, '15'], [20, '20'], [30, '30']], PREFS.grasp_cap, function (v) { PREFS.grasp_cap = v; savePrefs(); render(); }));

    body.appendChild(el('<h2>런 내보내기 / 불러오기</h2>'));
    var ta = el('<div class="wrap"><textarea spellcheck="false">' + esc(JSON.stringify(RUN)) + '</textarea></div>');
    var imp = el('<div class="wrap"><button class="tagx" style="padding:10px 14px">붙여넣은 내용으로 불러오기</button></div>');
    imp.querySelector('button').onclick = function () {
      try { var o = JSON.parse(ta.querySelector('textarea').value); if (!o.state || !o.state.weapon) throw 0; RUN = o; saveRun(); toast('불러왔습니다'); render(); }
      catch (e) { toast('형식이 올바르지 않습니다'); }
    };
    body.appendChild(ta); body.appendChild(imp);

    var nb = el('<button class="danger">새 런 시작</button>');
    nb.onclick = function () { UI.screen = 'start'; saveUI(); render(); };
    body.appendChild(nb);
    // 재배포를 반복하므로 어느 빌드를 쓰는 중인지 알 수 있게 표시 (피드백용)
    body.appendChild(el('<div class="wrap xs dim" style="padding:14px 14px 24px; text-align:center">빌드 ' +
      esc(DATA.__build || '?') + ' · 은혜 ' + DATA.boons.length + ' · 융합 ' + DATA.duos.length + ' · 망치 ' + DATA.hammers.length + '</div>'));
    return wrapSheet('관리', body);
  }

  // ── 시작 ───────────────────────────────────────────────
  if (RUN && (!RUN.state || !RUN.state.weapon)) RUN = null;
  if (RUN && UI.screen === 'start') UI.screen = null;
  render();
})();
