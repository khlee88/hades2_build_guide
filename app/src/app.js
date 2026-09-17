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
  var ent = function (id) { return IX.boons[id] || IX.duos[id] || IX.hammers[id] || IX.keepsakes[id] || IX.hexes[id] || IX.arcana[id] || IX.gods[id] || ASP[id] || IX.weapons[id] || null; };
  var nm = function (id) { var o = ent(id); return o ? o.name_ko : id; };

  var SLOTS = ['attack', 'special', 'cast', 'sprint', 'magick'];
  var SK = { attack: '공', special: '기', cast: '마', sprint: '질', magick: '력' };
  var SKO = W.SLOT_KO;
  var GC = { zeus: '#f2d16b', hestia: '#ff8a3d', poseidon: '#4aa3ff', demeter: '#7ed491', apollo: '#ffd166', aphrodite: '#ff7eb6', hephaestus: '#c97b4a', hera: '#b58cff', ares: '#e05252', hermes: '#c0c7d1', artemis: '#5fbf8a', athena: '#d9d2b0', dionysus: '#9b59b6', selene: '#a9c4ff', chaos: '#c76bd9' };
  var GOD_ORDER = ['zeus', 'hestia', 'poseidon', 'demeter', 'apollo', 'aphrodite', 'hephaestus', 'hera', 'ares', 'hermes', 'artemis', 'athena', 'dionysus'];  // 셀레네·카오스는 5단계에서 제외 — 빌드 필수가 아닌 옵션
  // 1·2위 점수차가 이 값 미만이면 엔진이 사실상 구분 못 한 것으로 보고 '취향' 표시.
  // 근거: 시나리오 20개 점수차 분포가 0~2.5와 8 이상으로 갈리고 그 사이가 비어 있다.
  var CLOSE_GAP = 2;
  function closeSet(rows) {
    var s = {};
    var fin = rows.filter(function (r) { return isFinite(r.score); });
    if (fin.length < 2) return s;
    var top = fin[0].score;
    var near = fin.filter(function (r) { return top - r.score < CLOSE_GAP; });
    if (near.length >= 2) near.forEach(function (r) { s[r.id] = true; });
    return s;
  }
  var CLOSE_CHIP = '<span class="close">비슷함 · 취향</span>';

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
  var PREFS = ls('h2.prefs.v1') || {};
  PREFS = Object.assign({ owned_keepsakes: [], grasp_cap: 10, left_hand: false, show_score: true, font_scale: 1, last_weapon: 'staff', last_aspect: 'staff_melinoe' }, PREFS);
  var UI = ls('h2.ui.v1') || { screen: null, god_tab: null };
  var RUN = ls('h2.run.v1');
  var savePrefs = function () { ls('h2.prefs.v1', PREFS); };
  var saveUI = function () { ls('h2.ui.v1', UI); };
  var saveRun = function () { ls('h2.run.v1', RUN); };

  // ── 선택 로그 (h2.log.v1) ────────────────────────────
  // 매 선택마다 자동 누적. 내보내기 전까지 이 폰 안에만 있다.
  // 새 런 시작 화면에서 직전 런을 통째로 버릴 수 있고, 관리 화면에서 런별/전체 삭제할 수 있다.
  var LOG = ls('h2.log.v1') || [];
  var saveLog = function () { ls('h2.log.v1', LOG); };
  function nowKst() { return new Date(Date.now() + 9 * 36e5).toISOString().slice(0, 19).replace('T', ' '); }
  function ridNew() {
    var d = new Date(Date.now() + 9 * 36e5).toISOString();
    return d.slice(2, 4) + d.slice(5, 7) + d.slice(8, 10) + '-' + d.slice(11, 13) + d.slice(14, 16) +
      '-' + Math.random().toString(36).slice(2, 6);
  }
  function logPush(ev) {
    if (!RUN || !RUN.rid) return;
    ev.id = RUN.rid; ev.n = (RUN.seq = (RUN.seq || 0) + 1);
    LOG.push(ev); saveLog(); saveRun();
  }
  function logRuns() {  // [{rid, picks, end}] 최신 순
    var m = {}, order = [];
    LOG.forEach(function (e) {
      if (!m[e.id]) { m[e.id] = { rid: e.id, picks: 0, end: null, w: null, asp: null }; order.push(e.id); }
      var r = m[e.id];
      if (e.t === 'pick') r.picks++;
      else if (e.t === 'end') r.end = e;
      else if (e.t === 'run') { r.w = e.w; r.asp = e.asp; }
    });
    return order.map(function (id) { return m[id]; }).reverse();
  }
  function logDrop(rid) { LOG = LOG.filter(function (e) { return e.id !== rid; }); saveLog(); }
  function filledSlots(st) {
    var n = 0;
    (st.boons || []).forEach(function (id) { var b = IX.boons[id]; if (b && b.occupies_slot) n++; });
    return n;
  }
  // 제시된 것 전부를 남긴다 — 고른 것만 남기면 "3택 중 선택" 모델을 못 만든다
  function logPick(kind, rows, chosenId) {
    if (!RUN || !RUN.rid) return;
    var st = RUN.state;
    logPush({
      t: 'pick', kind: kind, rg: st.region, ns: filledSlots(st),
      dir: E.directionScores(st).slice(0, 2).map(function (d) { return [d.id, d.weight]; }),
      off: rows.map(function (r) {
        var o = { i: r.id, s: isFinite(r.score) ? r.score : null, k: r.rank || null, b: r.breakdown || {} };
        var p = pickSel.find(function (x) { return x.id === r.id; });
        if (p && p.rarity) o.r = p.rarity;
        if (r._replacing) o.rep = 1;
        return o;
      }),
      c: chosenId,
    });
  }

  function newRun(weapon, aspect) {
    return { rid: ridNew(), seq: 0, state: { weapon: weapon, aspect: aspect, region: 1, boons: [], hammers: [], arcana: [], keepsake: null, hex: null, gods_seen: [], direction_lock: null }, pending_god: null, history: [] };
  }
  function pushHistory(label) {
    RUN.history.unshift({ ts: Date.now(), label: label, snap: JSON.stringify(RUN.state) });
    if (RUN.history.length > 10) RUN.history.length = 10;
  }
  function undo() {
    if (!RUN.history.length) return toast('되돌릴 기록이 없습니다');
    RUN.state = JSON.parse(RUN.history.shift().snap); saveRun(); logPush({ t: 'undo' }); render();
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
  // 운용 가이드. phase: 'early' | 'late' | null — 지금 단계를 강조 (홈에서 채운 칸 수로 판단)
  var PS_ROWS = [['loop', '기본 루프'], ['key', '기억할 것'], ['cast', '마법진'], ['early', '초반 · 칸 2개 이하'], ['late', '완성 후'], ['avoid', '하지 말 것']];
  function playstyleBox(dirId, weapon, phase, open) {
    var d = ((DATA.builds.weapons[weapon] || {}).directions || []).find(function (x) { return x.id === dirId; });
    var ps = d && d.playstyle; if (!ps) return null;
    var det = el('<details class="ps"' + (open ? ' open' : '') + '><summary><span>운용법</span>' +
      (phase ? '<span class="tagx">' + (phase === 'early' ? '지금은 초반' : '빌드 완성') + '</span>' : '') + '</summary></details>');
    PS_ROWS.forEach(function (r) {
      if (!ps[r[0]]) return;
      var hot = phase && (r[0] === phase);
      var dim = phase && ((r[0] === 'early' && phase === 'late') || (r[0] === 'late' && phase === 'early'));
      det.appendChild(el('<div class="psrow' + (hot ? ' hot' : '') + (dim ? ' dimmed' : '') + '"><div class="lb">' + esc(r[1]) + '</div><div class="tx">' + esc(ps[r[0]]) + '</div></div>'));
    });
    return det;
  }
  // ── 신·무기 심볼 (인라인 SVG, 24x24 viewBox) ─────────
  // f: 채움 경로 / s: 선 경로. 색은 currentColor라 신 색이 그대로 들어간다.
  var SYM = {
    zeus:       { f: 'M13 2 5 14h5l-2 8 9-13h-5z' },                                     // 벼락
    hestia:     { f: 'M12 22c3.6 0 6-2.6 6-6 0-4-4-6-4-10 0 0-2.6 1.8-2.6 4.4C11.4 9 10 8 10 7c-1.8 1.8-2.6 4.4-2.6 7 0 3.4 2.4 6 4.6 6z' },  // 불꽃
    poseidon:   { s: 'M12 2v20M7 9v2a5 5 0 0 0 10 0V9M7 9V6M17 9V6' },                    // 삼지창
    demeter:    { s: 'M12 22V3.5', f: 'M12 10.2c-2.7 0-3.8-1.9-3.8-3.8 1.9 0 3.8 1 3.8 3.8zM12 10.2c2.7 0 3.8-1.9 3.8-3.8-1.9 0-3.8 1-3.8 3.8zM12 15.4c-2.7 0-3.8-1.9-3.8-3.8 1.9 0 3.8 1 3.8 3.8zM12 15.4c2.7 0 3.8-1.9 3.8-3.8-1.9 0-3.8 1-3.8 3.8z' },  // 밀 이삭
    apollo:     { s: 'M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2.1 2.1M16.9 16.9 19 19M19 5l-2.1 2.1M7.1 16.9 5 19', c: [12, 12, 4] },  // 태양
    aphrodite:  { f: 'M12 20.5S4.5 15.6 4.5 10.6A4.1 4.1 0 0 1 12 8.2a4.1 4.1 0 0 1 7.5 2.4c0 5-7.5 9.9-7.5 9.9z' },  // 하트
    hephaestus: { s: 'M7 21.5 10.9 11.6M17 21.5 13.1 11.6M10.9 10.4 9.2 5.4M13.1 10.4l1.7-5', f: 'M9.6 2.2h4.8v3.4H9.6z', c: [12, 11, 1.5] },  // 집게로 쇳덩이를 집은 모양
    hera:       { s: 'M6 20.5h4.2v-2a6.8 6.8 0 1 1 3.6 0v2H18' },                         // 오메가
    ares:       { s: 'M12 21.5V5M12 5 10 8.4M12 5l2 3.4M8.4 11.2h7.2', f: 'M8.2 11.6c-2.2 1.3-2.7 3.6-1 5.2.3-1.8 1.1-2.5 2.8-3zM15.8 11.6c2.2 1.3 2.7 3.6 1 5.2-.3-1.8-1.1-2.5-2.8-3z' },  // 양옆 불꽃 검
    hermes:     { f: 'M21.2 4.2c-6 .2-10.9 2.5-13.9 6.6-1.1 1.5-2 3.2-2.6 5.1 2-.1 3.8-.4 5.4-1-.7-.8-1.2-1.7-1.4-2.6 1.6.8 3.2 1.1 4.8 1-.7-.8-1.2-1.7-1.5-2.7 1.9.8 3.6.9 5.2.6-.8-.8-1.4-1.7-1.7-2.7 1.9.5 3.5.4 4.7-.1-.3-1.4-.4-2.8-.2-4.2z' },  // 날개
    artemis:    { s: 'M6 3a12 12 0 0 1 0 18M6 12h13M15 8l4 4-4 4' },                      // 활과 화살
    selene:     { f: 'M16.5 2.5a9.5 9.5 0 1 0 5 13.4 7.6 7.6 0 0 1-5-13.4z' },            // 초승달
    chaos:      { s: 'M12 13.5a2 2 0 1 1-1.4-3.4 5 5 0 1 1 5 5 8 8 0 1 1-8-8' },          // 소용돌이
    athena:     { s: 'M12 2.6 4.6 5.5v5.9c0 4.6 3.1 8.6 7.4 10 4.3-1.4 7.4-5.4 7.4-10V5.5z', f: 'M12 8.4 9.5 13.2h5z' },  // 방패
    dionysus:   { s: 'M12.4 8.6V4.4c1.7-.7 3.2-.7 4.2-.3', f: 'M9.2 9.4a1.75 1.75 0 1 1 0 3.5 1.75 1.75 0 0 1 0-3.5zm5.6 0a1.75 1.75 0 1 1 0 3.5 1.75 1.75 0 0 1 0-3.5zM12 12.9a1.75 1.75 0 1 1 0 3.5 1.75 1.75 0 0 1 0-3.5zm-2.5 3.6a1.75 1.75 0 1 1 0 3.5 1.75 1.75 0 0 1 0-3.5zm5 0a1.75 1.75 0 1 1 0 3.5 1.75 1.75 0 0 1 0-3.5z' },  // 포도송이
    staff:      { s: 'M4 20 15.5 8.5M12 4l1-2 1 2 2 1-2 1-1 2-1-2-2-1z', c: [17.5, 6, 3] },// 지팡이
    blades:     { s: 'M7.5 21 4 6l5 2.5zM16.5 21 20 6l-5 2.5z' },                          // 쌍검
    flames:     { s: 'M12 17.5V22', f: 'M12 2.5c2.2 3.6 5.6 5 5.6 8.6 0 3.2-2.5 5.4-5.6 5.4s-5.6-2.2-5.6-5.4c0-1.7.6-3.1 1.5-4.3.1 1.5.9 2.3 1.8 2.3 1.1 0 1.7-.9 1.7-2.4 0-1.6.3-3 .6-4.2z' },  // 횃불
    axe:        { s: 'M6.5 21 16 6', f: 'M11.5 5.2c4.6-2.4 9.5.4 9.5 4.6 0 2.6-1.8 4.6-4.4 5.2-.3-4-2.2-7.4-5.1-9.8z' },  // 도끼
  };
  function sym(id, size) {
    var d = SYM[id]; if (!d) return '';
    return '<svg class="sym" viewBox="0 0 24 24" width="' + size + '" height="' + size + '" fill="none" ' +
      'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      (d.c ? '<circle cx="' + d.c[0] + '" cy="' + d.c[1] + '" r="' + d.c[2] + '"/>' : '') +
      (d.f ? '<path d="' + d.f + '" fill="currentColor" stroke="none"/>' : '') +
      (d.s ? '<path d="' + d.s + '"/>' : '') + '</svg>';
  }
  function applyFontScale() { document.getElementById('app').style.setProperty('--fs', PREFS.font_scale || 1); }
  // #rrggbb → rgba(...) (U5 테두리·글로우·틴트)
  function rgba(hex, a) {
    var h = String(hex).replace('#', '');
    return 'rgba(' + parseInt(h.slice(0, 2), 16) + ',' + parseInt(h.slice(2, 4), 16) + ',' + parseInt(h.slice(4, 6), 16) + ',' + a + ')';
  }
  function stepper(val, min, max, onChange) {
    var s = el('<div class="stepper"><button data-m>−</button><div class="val">' + val + '</div><button data-p>+</button></div>');
    var m = s.querySelector('[data-m]'), p = s.querySelector('[data-p]');
    if (val <= min) m.disabled = true;
    if (val >= max) p.disabled = true;
    m.onclick = function () { onChange(Math.max(min, val - 1)); };
    p.onclick = function () { onChange(Math.min(max, val + 1)); };
    return s;
  }

  // ── 화면 전환 ──────────────────────────────────────────
  var sheet = null;
  function openSheet(name) { UI.screen = name; saveUI(); history.pushState({ sheet: name }, ''); render(); }
  // X로 닫을 때도 pushState로 쌓인 이력을 되감는다. 안 그러면 열고 닫을수록 뒤로가기가 밀린다 (U8)
  function closeSheet(fromPop) {
    if (!UI.screen) return;
    if (!fromPop && history.state && history.state.sheet) { history.back(); return; } // popstate가 렌더를 맡는다
    UI.screen = null; saveUI(); render();
  }
  window.addEventListener('popstate', function () { closeSheet(true); });

  // ── 렌더 ───────────────────────────────────────────────
  var app = document.getElementById('app');
  function render() {
    app.innerHTML = ''; applyFontScale();
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
    // closeSheet를 그대로 넘기면 MouseEvent가 fromPop 인자로 들어가 되감기를 건너뛴다
    s.querySelector('[data-close]').onclick = function () { closeSheet(); };
    s.querySelector('.body').appendChild(inner);
    return s;
  }

  // ── 1. 런 시작 ─────────────────────────────────────────
  var startSel = { weapon: PREFS.last_weapon, aspect: PREFS.last_aspect };
  // 지난 런 결과. 여기서만 결과 라벨이 생긴다 — 안 넣으면 그 런은 클리어율 통계에서 빠진다
  // (선택 기록 자체는 남으므로 가중치 학습에는 그대로 쓰인다)
  var endSel = { route: PREFS.last_route || 'under', res: 'died' };
  // 5-B: 결과 입력은 건너뛸 수 없게, 대신 1탭. 지역 버튼을 누르는 것 자체가 기록 + 다음.
  // 기본값(1지역)으로 빠져나가는 경로가 있으면 로그가 오염된다 (실플레이 5런 중 4런).
  function viewEnd(prev, asSheet) {
    var root = document.createElement('div');
    if (!asSheet) root.appendChild(el('<div class="top"><div class="t">하데스2 빌드 길잡이</div></div>'));
    var picks = LOG.filter(function (e) { return e.id === prev.rid && e.t === 'pick' && e.kind !== 'god'; }).length;
    var n = prev.state.boons.length + prev.state.hammers.length;
    var est = Math.max(prev.state.region || 1, Math.min(4, 1 + Math.floor(n / 7)));   // 보상 6~8개당 1지역, 수동 지역이 더 크면 그것
    root.appendChild(el('<h2>지난 런, 어디까지 갔나요?</h2>'));
    root.appendChild(el('<div class="wrap sm dim">' + esc(nm(prev.state.weapon)) + ' · 은혜·망치 ' + n + '개 · 선택 ' + picks + '회 → <b>' + est + '지역</b>으로 추정</div>'));
    var chipRow = function (opts, cur, cb) {
      var cs = el('<div class="chips" style="padding-top:4px;padding-bottom:4px"></div>');
      opts.forEach(function (o) {
        var b = el('<button class="chip" aria-pressed="' + (cur === o[0]) + '">' + esc(o[1]) + '</button>');
        b.onclick = function () { cb(o[0]); rerenderStart(root, asSheet); };
        cs.appendChild(b);
      });
      return cs;
    };
    root.appendChild(chipRow([['under', '지하 (크로노스)'], ['surface', '지상 (티폰)']], endSel.route, function (v) { endSel.route = v; PREFS.last_route = v; savePrefs(); }));
    root.appendChild(chipRow([['died', '죽었다'], ['quit', '죽지 않고 그만뒀다']], endSel.res, function (v) { endSel.res = v; }));
    var finish = function (rgv, res) {
      logPush({ t: 'end', ts: nowKst(), route: endSel.route, res: res, rg: rgv });
      RUN.endDone = true; saveRun(); rerenderStart(root, asSheet);
    };
    var bt = el('<div class="endbtns"></div>');
    [1, 2, 3, 4].forEach(function (k) {
      var b = el('<button aria-pressed="' + (k === est) + '"><span class="big">' + k + '</span><span class="xs">지역</span></button>');
      b.onclick = function () { var rgv = []; for (var i = 1; i < k; i++) rgv.push(1); rgv.push(endSel.res === 'quit' ? null : 0); finish(rgv, endSel.res); };
      bt.appendChild(b);
    });
    var cl = el('<button class="clear"><span class="big">완주</span><span class="xs">클리어</span></button>');
    cl.onclick = function () { finish([1, 1, 1, 1], 'clear'); };
    bt.appendChild(cl);
    root.appendChild(bt);
    var skip = el('<div class="wrap" style="text-align:center;padding-top:4px"><button class="tagx" style="padding:10px 14px">이 런은 기록하지 않기 (조작 실수 등)</button></div>');
    skip.querySelector('button').onclick = function () { logDrop(prev.rid); RUN.endDone = true; saveRun(); toast('지난 런 기록을 지웠습니다'); rerenderStart(root, asSheet); };
    root.appendChild(skip);
    return root;
  }
  function viewStart(asSheet) {
    var prevRun = (RUN && RUN.rid && RUN.state.boons.length && !RUN.endDone) ? RUN : null;
    if (prevRun) return viewEnd(prevRun, asSheet);
    var root = document.createElement('div');
    if (!asSheet) root.appendChild(el('<div class="top"><div class="t">하데스2 빌드 길잡이</div></div>'));
    if (saveFail) root.appendChild(el('<div class="banner">저장이 안 됩니다 — 이 탭을 닫으면 사라져요</div>'));

    root.appendChild(el('<h2>무기</h2>'));
    var wg = el('<div class="wgrid"></div>');
    DATA.weapons.forEach(function (w) {
      var ready = w.unlock_order <= 4;
      var b = el('<button class="wcard" ' + (ready ? '' : 'disabled') + ' aria-pressed="' + (startSel.weapon === w.id) + '">' +
        '<div class="n"><span class="gi wi">' + sym(w.id, 20) + '</span>' + esc(w.name_ko) + '</div>' +
        '<div class="a">' + esc(ready ? (w.alias_ko || '') : '준비 중') + '</div></button>');
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

    var A = r.arcana;
    root.appendChild(el('<h2>아르카나 (사용 ' + A.grasp_used + ' / 상한 ' + A.grasp_cap +
      (A.grasp_left > 0 ? ', 남음 ' + A.grasp_left : '') + ')</h2>'));
    var gc = el('<div class="card tight"><div class="row"><div class="mid" style="flex:1"><div class="sm">내 이해도 상한</div><div class="xs dim">재의 제단에서 넋으로 1씩 올린다 (10~30)</div></div></div></div>');
    gc.querySelector('.row').appendChild(stepper(PREFS.grasp_cap, 10, 30, function (v) {
      PREFS.grasp_cap = v; savePrefs(); rerenderStart(root, asSheet);
    }));
    root.appendChild(gc);

    // 5-C: 게임 화면과 같은 5×5 격자. 각성 조건("둘러싼 카드")이 격자 없이는 읽히지 않는다
    var selIds = {}; A.cards.forEach(function (c) { selIds[c.id] = 'sel'; }); A.awakened.forEach(function (c) { selIds[c.id] = 'free'; });
    var grid = el('<div class="agrid"></div>');
    var cells = {};
    DATA.arcana.forEach(function (c) { var gp = c.grid_position || [0, 0]; cells[gp[0] + ',' + gp[1]] = c; });
    for (var rr = 1; rr <= 5; rr++) for (var cc = 1; cc <= 5; cc++) {
      var c = cells[rr + ',' + cc];
      var cell = el('<div class="acell ' + (c ? (selIds[c.id] || '') : '') + '">' +
        (c ? '<span class="n">' + esc(c.name_ko) + '</span><span class="g">' + (c.grasp === 0 ? '각성' : c.grasp) + '</span>' : '') + '</div>');
      grid.appendChild(cell);
    }
    root.appendChild(grid);
    var pos = function (c) { var a = IX.arcana[c.id]; var gp = a && a.grid_position; return gp ? ' <span class="xs dim">(' + gp[0] + ',' + gp[1] + ')</span>' : ''; };
    var ac = el('<div class="card tight"></div>');
    var arow = function (c, cls, tag) {
      return el('<div class="arow ' + (cls || '') + '"><span class="g">' + (c.grasp === 0 ? '0' : c.grasp) + '</span>' +
        '<div class="mid" style="flex:1;min-width:0"><div class="ell">' + esc(c.name_ko) + pos(c) + '</div>' +
        '<div class="xs dim ell">' + esc(c.effect) + '</div></div>' +
        (tag ? '<span class="atag ' + tag[0] + '">' + esc(tag[1]) + '</span>' : '') + '</div>');
    };
    A.cards.forEach(function (c) {
      var t = c.tag === '핵심' ? ['핵심', '핵심'] : c.tag === '무기 방향' ? ['무기', '무기 방향'] : ['', '보조'];
      ac.appendChild(arow(c, '', t));
    });
    A.awakened.forEach(function (c) { ac.appendChild(arow(c, 'free', ['각성', '각성 · 무료'])); });
    if (!A.cards.length) ac.appendChild(el('<div class="empty">이해도를 올려 주세요</div>'));
    root.appendChild(ac);

    if (A.next_up.length) {
      var nu = el('<details class="card tight"><summary class="sm dim">이해도를 더 올리면 (' + A.next_up.length + '장)</summary></details>');
      A.next_up.forEach(function (c) { nu.appendChild(arow(c, '', ['', c.tag])); });
      root.appendChild(nu);
    }
    if (A.free_cards.length) {
      var det = el('<details class="card tight"><summary class="sm dim">아직 잠긴 무료 카드 (' + A.free_cards.length + '장)</summary></details>');
      A.free_cards.forEach(function (c) {
        det.appendChild(el('<div class="arow"><span class="g">0</span><div class="mid" style="flex:1;min-width:0"><div class="ell">' + esc(c.name_ko) + '</div><div class="xs dim">' + esc(c.awaken_condition || '') + '</div></div></div>'));
      });
      root.appendChild(det);
    }

    root.appendChild(el('<h2>첫 기념품</h2>'));
    var kc = el('<div class="card tight"></div>');
    if (r.first_keepsake) {
      var fk = r.first_keepsake;
      kc.appendChild(el('<div style="padding:6px 0"><div class="row"><b style="flex:1">' + esc(fk.name_ko) + '</b><span class="tagx" style="color:' + (GC[fk.god] || 'inherit') + '">' + esc(fk.god_ko) + '</span></div>' +
        '<div class="sm" style="margin-top:4px">' + esc(fk.reason) + '</div>' +
        (fk.giver_ko ? '<div class="xs dim">' + esc(fk.giver_ko) + '에게 넥타르로 획득</div>' : '') + '</div>'));
    }
    r.keepsakes.slice(0, 2).forEach(function (k) {
      kc.appendChild(el('<div style="padding:6px 0;border-top:1px solid var(--line)"><div class="sm dim">대안 · ' + esc(k.name_ko) +
        (k.giver_ko ? ' <span class="giver">(' + esc(k.giver_ko) + ')</span>' : '') + '</div><div class="xs dim ell">' + esc(k.effect) + '</div></div>'));
    });
    root.appendChild(kc);

    root.appendChild(el('<h2>추천 빌드</h2>'));
    root.appendChild(el('<div class="wrap sm dim">' + esc(r.note) + '</div>'));
    r.directions.forEach(function (d) {
      var dc = el('<div class="card"><div class="row"><b>' + esc(d.name_ko) + '</b><span class="xs dim">★' + d.difficulty + '</span></div>' +
        '<div class="sm dim" style="margin-top:4px">' + esc(d.summary) + '</div>' +
        '<div class="sm" style="margin-top:6px">주요 신: ' + d.main_gods.map(function (g, i) { return '<span style="color:' + (GC[g.id] || 'inherit') + ';font-weight:' + (i ? 400 : 700) + '">' + esc(g.name_ko) + '</span>'; }).join(' <span class="dim">›</span> ') + '</div>' +
        '<div class="xs dim" style="margin-top:4px">핵심 칸: ' + esc(d.core_slots.join(' · ')) + '</div>' +
        '<div class="xs dim">' + esc(d.first_picks.join(' / ')) + '</div>' +
        (d.target_duos.length ? '<div class="xs dim">노리는 융합: ' + esc(d.target_duos.join(', ')) + '</div>' : '') +
        (d.key_hammers.length ? '<div class="xs dim">망치: ' + esc(d.key_hammers.join(', ')) + '</div>' : '') + '</div>');
      var pb = playstyleBox(d.id, startSel.weapon, null, false);
      if (pb) dc.appendChild(pb);
      root.appendChild(dc);
    });

    var cta = el('<div class="cta"><button>이 무기로 시작</button></div>');
    cta.querySelector('button').onclick = function () {
      PREFS.last_weapon = startSel.weapon; PREFS.last_aspect = startSel.aspect; savePrefs();
      RUN = newRun(startSel.weapon, startSel.aspect); saveRun();
      logPush({ t: 'run', ts: nowKst(), w: RUN.state.weapon, asp: RUN.state.aspect, grasp: PREFS.grasp_cap,
        arc: (r.arcana.cards || []).map(function (c) { return c.id; }), eng: DATA.__build || null, sv: 1 });
      UI.screen = null; saveUI(); render();
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
    var top = el('<div class="top"><div class="t"><span class="gi wi">' + sym(wp.id, 19) + '</span>' + esc(wp.name_ko) + '</div>' +
      '<button class="iconbtn" data-undo title="되돌리기">↶</button></div>');
    top.querySelector('[data-undo]').onclick = undo;
    root.appendChild(top);
    if (saveFail) root.appendChild(el('<div class="banner">저장이 안 됩니다 — 이 탭을 닫으면 사라져요</div>'));

    var warn = E.validateState(st);
    if (warn.length) root.appendChild(el('<div class="banner">' + esc(warn.join(' · ')) + '</div>'));

    var ds = E.directionScores(st);
    var card = el('<div class="card"></div>');
    var meta = el('<div class="row sm dim"><span>' + esc((IX.weapons[st.weapon].aspects.find(function (a) { return a.id === st.aspect; }) || {}).name_ko || '') + '</span>' +
      '<button class="tagx" data-region>' + st.region + '지역</button>' +
      (st.direction_lock ? '<span class="tagx">🔒 고정</span>' : '') + '</div>');
    meta.querySelector('[data-region]').onclick = function () { openSheet('manage'); };
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
      // 운용법 — 게임 중에 보는 게 진짜 용도. 채운 칸으로 초반/완성 후를 강조한다 (사용자: 초반에 완성 후 운용을 해서 죽음 저항을 다 씀)
      var ns = filledSlots(st);
      var psb = playstyleBox(ds[0].id, st.weapon, ns <= 2 ? 'early' : 'late', false);
      if (psb) { psb.style.marginTop = '8px'; card.appendChild(psb); }
    }
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

  // ── 3. 신 선택 ─────────────────────────────────────────
  var godSel = [];
  function viewGods() {
    var body = document.createElement('div');
    body.appendChild(el('<div class="wrap sm dim" style="padding-top:10px">문 위에 뜬 신을 골라 주세요 — 하나만 떠도 됩니다. 등급이 <b>패스</b>면 석류·재화 문이 낫습니다</div>'));
    var grid = el('<div class="gods"></div>');
    var out = el('<div></div>');
    var btns = {};
    GOD_ORDER.forEach(function (id) {
      var seen = RUN.state.gods_seen.indexOf(id) >= 0;
      var b = el('<button class="god" data-gc aria-pressed="false" style="--gc:' + GC[id] + '; --gcd:' + rgba(GC[id], .45) +
        '; --gcg:' + rgba(GC[id], .3) + '; --gct:' + rgba(GC[id], .12) + '">' +
        '<span class="ord"></span><span class="gi" style="color:' + GC[id] + '">' + sym(id, 24) + '</span>' +
        '<span class="n">' + esc(nm(id)) + '</span>' +
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
      var ORD = ['①', '②', '③', '④'];
      GOD_ORDER.forEach(function (id) {
        var i = godSel.indexOf(id);
        btns[id].setAttribute('aria-pressed', i >= 0);
        btns[id].querySelector('.ord').textContent = i >= 0 ? (ORD[i] || (i + 1)) : '';
      });
      out.innerHTML = '';
      if (!godSel.length) { out.appendChild(el('<div class="empty">문에 뜬 신을 눌러 주세요</div>')); return; }
      var grows = E.recommendGods(RUN.state, godSel);
      // 5-A: 점수 차 2 미만은 같은 군 — 첫 신처럼 변별이 없을 때 1·2·3위 대신 '동급' 칩
      var topTie = grows.filter(function (x) { return x.tie === grows[0].tie; }).length > 1;
      grows.forEach(function (r, i) {
        out.appendChild(recCard(r, i, function () {
          logPick('god', grows, r.id);
          RUN.pending_god = r.id; pickSel = []; godTab = r.id;
          UI.screen = 'boons'; saveUI(); saveRun(); render();
        }, '이 문으로', topTie && r.tie === grows[0].tie));
      });
    }
    refresh();
    return wrapSheet('신 선택', body);
  }

  // ── 4·5. 은혜 / 망치 선택 ──────────────────────────────
  var pickSel = [], godTab = null, searchOn = false, searchQ = '', trayOpen = true;
  function viewPick(kind) {
    var isBoon = kind === 'boon';
    if (isBoon && RUN.pending_god) { godTab = RUN.pending_god; RUN.pending_god = null; saveRun(); }
    if (isBoon && !godTab) godTab = UI.god_tab || RUN.state.gods_seen[RUN.state.gods_seen.length - 1] || 'zeus';
    var body = document.createElement('div');
    var listBox = el('<div class="list"></div>');
    var trayBox = el('<div class="tray"></div>');

    if (isBoon) {
      var top = el('<div class="row" style="padding:8px 14px 0"><div class="sm dim" style="flex:1">게임에 뜬 은혜를 2~3개 탭</div><button class="iconbtn" data-s>🔍</button></div>');
      top.querySelector('[data-s]').onclick = function () { searchOn = !searchOn; if (!searchOn) searchQ = ''; draw(); };
      body.appendChild(top);
      var sbox = el('<div class="wrap" style="padding-bottom:8px"></div>');
      body.appendChild(sbox);
      var tabs = el('<div class="chips"></div>');
      GOD_ORDER.forEach(function (id) {
        var b = el('<button class="chip" aria-pressed="' + (godTab === id) + '" style="border-color:' + GC[id] + '">' +
          '<span class="gi" style="color:' + GC[id] + '">' + sym(id, 17) + '</span>' + esc(nm(id)) + '</button>');
        b.onclick = function () {
          godTab = id; UI.god_tab = id; saveUI(); searchQ = ''; draw();
        };
        tabs.appendChild(b);
      });
      body.appendChild(tabs);
      body._sbox = sbox;
    } else {
      body.appendChild(el('<div class="wrap sm dim" style="padding:10px 14px 4px">게임에 뜬 다이달로스 망치를 2~3개 탭</div>'));
    }
    body.appendChild(listBox);

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
      drawList(); drawTray();
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
    var lastRows = [];
    function drawTray() {
      trayBox.innerHTML = '';
      // 추천을 트레이 안에 넣어 목록을 스크롤하면서도 순위가 늘 보이게 한다 (U4)
      if (pickSel.length >= 2) {
        var hd = el('<button class="thead"><span>추천 ' + pickSel.length + '개 비교</span><span class="caret">' + (trayOpen ? '▾' : '▴') + '</span></button>');
        hd.onclick = function () { trayOpen = !trayOpen; draw(); };
        trayBox.appendChild(hd);
        if (trayOpen) {
          var box = el('<div class="recs"></div>');
          var rows = isBoon ? E.recommendBoons(RUN.state, pickSel) : E.recommendHammers(RUN.state, pickSel.map(function (p) { return p.id; }));
          lastRows = rows;
          var cs = closeSet(rows);
          rows.forEach(function (r, i) { box.appendChild(compactRec(r, i, isBoon, cs[r.id])); });
          trayBox.appendChild(box);
        }
      }
      var picks = el('<div class="picks"></div>');
      if (!pickSel.length) picks.appendChild(el('<span class="sm dim">목록에서 2개 이상 고르면 여기에 순위가 나옵니다</span>'));
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
    function compactRec(r, i, isBoon, isClose) {
      var no = !isFinite(r.score);
      var w = r.warnings || [];
      var mainBadge = (r.badges || []).filter(function (b) { return b !== '항상'; })[0] || '';
      var row = el('<div class="crec ' + (i === 0 && !no ? 'r1' : '') + ' ' + (no ? 'no' : '') + '">' +
        '<span class="rk">' + (r.rank || i + 1) + '위</span>' +
        '<div class="mid"><div class="nm">' + slotChip(ent(r.id)) + '<span class="ell">' + esc(nm(r.id)) + '</span>' +
        (mainBadge ? '<span class="bdg">' + esc(mainBadge) + '</span>' : '') +
        (isClose ? CLOSE_CHIP : '') + '</div>' +
        '<div class="rs ell">' + esc(r.reason) + '</div>' +
        (w.length ? '<div class="wn ell">⚠ ' + esc(w[0]) + (w.length > 1 ? ' +' + (w.length - 1) : '') + '</div>' : '') +
        '</div>' + (no ? '' : '<button class="go">결정</button>') + '</div>');
      if (!no) row.querySelector('.go').onclick = function () {
        logPick(isBoon ? 'boon' : 'hammer', lastRows.length ? lastRows : [r], r.id);
        pushHistory((isBoon ? '은혜' : '망치') + ' ' + nm(r.id));
        var rar = (pickSel.find(function (p) { return p.id === r.id; }) || {}).rarity;
        RUN.state = E.applyChoice(RUN.state, { kind: isBoon ? 'boon' : 'hammer', id: r.id, rarity: rar });
        pickSel = []; saveRun(); closeSheet();
      };
      return row;
    }
    draw();
    var s = wrapSheet(isBoon ? '은혜 선택' : '망치 선택', body);
    s.appendChild(trayBox);
    return s;
  }

  function recCard(r, i, onDecide, label, isClose) {
    var no = !isFinite(r.score);
    var grade = r.grade || null;
    var c = el('<div class="rec ' + (i === 0 && !no && grade !== 'pass' ? 'r1' : '') + ' ' + (no ? 'no' : '') + (grade === 'pass' ? ' pass' : '') + '">' +
      '<div class="hd"><span class="rk' + (grade ? ' grade-' + grade : '') + '">' + (grade ? esc(r.grade_ko) : (r.rank || i + 1) + '위') + '</span>' +
      (r.roles && r.roles.length ? '<span class="roles xs dim ell">' + esc(r.roles.slice(0, 2).join(' · ')) + '</span>' : '') +
      (PREFS.show_score && !no ? '<span class="sc">' + r.score + '</span>' : '') + '</div>' +
      '<div class="nm">' + slotChip(ent(r.id)) + '<span class="ell">' + esc(nm(r.id)) + '</span>' +
      (isClose ? CLOSE_CHIP : '') + '</div>' +
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
    body.appendChild(seg('지역', [[1, '1'], [2, '2'], [3, '3'], [4, '4']], st.region, function (v) { st.region = v; saveRun(); logPush({ t: 'rg', v: v }); render(); }));

    var k = E.recommendKeepsake(st);
    if (k && k.id) {
      var kc = el('<div class="card"><div class="xs dim">다음 지역 기념품 추천</div><div class="row" style="margin-top:4px"><b style="flex:1">' + esc(k.name_ko) + '</b><button class="tagx" data-k>이걸로</button></div><div class="sm dim" style="margin-top:4px">' + esc(k.reason) + '</div></div>');
      kc.querySelector('[data-k]').onclick = function () { pushHistory('기념품 ' + k.name_ko); st.keepsake = k.id; saveRun(); logPush({ t: 'keep', v: k.id }); render(); };
      body.appendChild(kc);
    }


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
        pushHistory('제거 ' + nm(id)); logPush({ t: 'rm', v: id });
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
    var gr = el('<div class="mrow"><div class="lb">이해도 상한<div class="xs dim">재의 제단에서 넋으로 1씩</div></div></div>');
    gr.appendChild(stepper(PREFS.grasp_cap, 10, 30, function (v) { PREFS.grasp_cap = v; savePrefs(); render(); }));
    body.appendChild(gr);
    body.appendChild(seg('글자 크기', [[1, '보통'], [1.15, '크게'], [1.3, '더 크게'], [1.5, '최대']], PREFS.font_scale, function (v) { PREFS.font_scale = v; savePrefs(); render(); }));

    body.appendChild(el('<h2>런 내보내기 / 불러오기</h2>'));
    var ta = el('<div class="wrap"><textarea spellcheck="false">' + esc(JSON.stringify(RUN)) + '</textarea></div>');
    var imp = el('<div class="wrap"><button class="tagx" style="padding:10px 14px">붙여넣은 내용으로 불러오기</button></div>');
    imp.querySelector('button').onclick = function () {
      try { var o = JSON.parse(ta.querySelector('textarea').value); if (!o.state || !o.state.weapon) throw 0; RUN = o; saveRun(); toast('불러왔습니다'); render(); }
      catch (e) { toast('형식이 올바르지 않습니다'); }
    };
    body.appendChild(ta); body.appendChild(imp);

    body.appendChild(el('<h2>선택 기록</h2>'));
    var runs = logRuns(), nPick = LOG.filter(function (e) { return e.t === 'pick'; }).length;
    var kbs = Math.round(JSON.stringify(LOG).length / 1024);
    body.appendChild(el('<div class="wrap sm dim">' + runs.length + '런 · ' + nPick + '선택 · ' + kbs + 'KB' +
      (kbs > 3500 ? ' <b>— 용량이 찼습니다. 내보낸 뒤 지워 주세요</b>' : '') + '</div>'));

    function logText() { return LOG.map(function (e) { return JSON.stringify(e); }).join('\n'); }
    function logName() {
      var d = new Date(Date.now() + 9 * 36e5).toISOString();
      return 'hades2_log_' + d.slice(0, 4) + d.slice(5, 7) + d.slice(8, 10) + '_' + d.slice(11, 13) + d.slice(14, 16) + '.jsonl';
    }
    var eb = el('<div class="wrap" style="display:flex;gap:8px">' +
      '<button class="tagx" style="flex:1;padding:12px" data-dl>파일로 저장</button>' +
      '<button class="tagx" style="flex:1;padding:12px" data-cp>복사</button></div>');
    eb.querySelector('[data-dl]').onclick = function () {
      if (!LOG.length) return toast('기록이 없습니다');
      // Pages는 일반 웹페이지라 다운로드가 된다 (Artifact 샌드박스에서만 막혔던 것)
      try {
        var a = document.createElement('a'), u = URL.createObjectURL(new Blob([logText()], { type: 'application/json' }));
        a.href = u; a.download = logName(); document.body.appendChild(a); a.click();
        setTimeout(function () { URL.revokeObjectURL(u); a.remove(); }, 1000);
        toast(logName() + ' 저장');
      } catch (e) { toast('저장 실패 — 복사를 써 주세요'); }
    };
    eb.querySelector('[data-cp]').onclick = function () {
      if (!LOG.length) return toast('기록이 없습니다');
      var t = logText();
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(t).then(function () { toast('복사했습니다'); }, function () { toast('복사 실패'); });
      else { var ta2 = document.createElement('textarea'); ta2.value = t; document.body.appendChild(ta2); ta2.select(); try { document.execCommand('copy'); toast('복사했습니다'); } catch (e) { toast('복사 실패'); } ta2.remove(); }
    };
    body.appendChild(eb);

    var rl = el('<div class="list"></div>');
    runs.forEach(function (R) {
      var res = R.end ? ({ clear: '클리어', died: '사망', quit: '중단' }[R.end.res] || R.end.res) +
        ' ' + (R.end.rg || []).length + '지역' : '결과 미입력';
      var it = el('<div class="item"><div class="mid"><div class="nm ell">' + esc(R.w ? nm(R.w) : R.rid) +
        '<span class="xs dim"> · ' + R.picks + '선택 · ' + esc(res) + '</span></div>' +
        '<div class="ef ell">' + esc(R.rid) + '</div></div><button class="tagx">✕</button></div>');
      it.querySelector('button').onclick = function () {
        if (!confirm('이 런의 기록을 지울까요?')) return;
        logDrop(R.rid); toast('지웠습니다'); render();
      };
      rl.appendChild(it);
    });
    if (!rl.children.length) rl.appendChild(el('<div class="empty">아직 없습니다</div>'));
    body.appendChild(rl);

    var cl = el('<div class="wrap"><button class="tagx" style="padding:10px 14px">기록 전체 지우기</button></div>');
    cl.querySelector('button').onclick = function () {
      if (!LOG.length) return toast('기록이 없습니다');
      var noEnd = runs.filter(function (R) { return !R.end; }).length;
      if (!confirm('기록 ' + runs.length + '런을 전부 지웁니다.' +
        (noEnd ? '\n결과 미입력 ' + noEnd + '런이 있습니다.' : '') +
        '\n내보내기를 먼저 했는지 확인하세요. 되돌릴 수 없습니다.')) return;
      LOG = []; saveLog(); toast('전부 지웠습니다'); render();
    };
    body.appendChild(cl);

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
