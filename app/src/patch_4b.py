# -*- coding: utf-8 -*-
"""4-B (오퍼스): 1차 실플레이 피드백 UI 5건. app/src/* 만 수정한다.
U1 글자 크기 / U2 이해도 스텝퍼 + 아르카나 표시 / U3 획득 경로 / U4 은혜 추천 트레이 / U5 신 테두리"""
import io, os, sys
SRC = os.path.dirname(os.path.abspath(__file__))
rd = lambda f: io.open(os.path.join(SRC, f), encoding='utf-8').read()
wr = lambda f, s: io.open(os.path.join(SRC, f), 'w', encoding='utf-8').write(s)
def sub(s, old, new, tag):
    if old not in s: print('패턴 못 찾음:', tag); sys.exit(1)
    return s.replace(old, new, 1)

# ══════════════════ app.css ══════════════════
c = rd('app.css')
if '--fs' in c:
    print('app.css: 이미 적용됨')
else:
    # U1: 루트 글자 크기를 뷰포트 비례로 + 사용자 배율. px 글자 → rem
    c = sub(c, """*{box-sizing:border-box; -webkit-tap-highlight-color:transparent}
body{margin:0}
#app{
  background:var(--bg); color:var(--text); min-height:100vh;
  font:16px/1.45 -apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Malgun Gothic","Noto Sans KR",sans-serif;
  overflow-x:hidden; padding-bottom:calc(160px + var(--safe-b));
}""",
"""*{box-sizing:border-box; -webkit-tap-highlight-color:transparent}
body{margin:0}
/* U1: 아티팩트 셸이 뷰포트를 데스크톱 폭으로 잡아도 글자가 작아지지 않게 vw 비례.
   사용자 배율(--fs)은 관리 > 글자 크기에서 조절한다. */
html{font-size:clamp(15px, 4.4vw, 22px)}
#app{
  --fs:1;
  background:var(--bg); color:var(--text); min-height:100vh;
  font:calc(1rem * var(--fs))/1.45 -apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Malgun Gothic","Noto Sans KR",sans-serif;
  overflow-x:hidden; padding-bottom:calc(160px + var(--safe-b));
}""", 'U1 root')
    for old, new in [
        ('h2{font-size:17px;', 'h2{font-size:1.06em;'),
        ('.dim{color:var(--dim)} .sm{font-size:13px} .xs{font-size:12px}', '.dim{color:var(--dim)} .sm{font-size:.82em} .xs{font-size:.75em}'),
        ('.top .t{font-weight:700; font-size:17px; flex:1}', '.top .t{font-weight:700; font-size:1.06em; flex:1}'),
        ('border-radius:10px; font-size:19px; color:var(--dim)}', 'border-radius:10px; font-size:1.2em; color:var(--dim)}'),
        ('.banner{background:#3a3210; color:#f0d78a; padding:8px 14px; font-size:13px;', '.banner{background:#3a3210; color:#f0d78a; padding:8px 14px; font-size:.82em;'),
        ('.slot .k{font-size:11px; color:var(--dim)}', '.slot .k{font-size:.7em; color:var(--dim)}'),
        ('.slot .v{font-size:11px;', '.slot .v{font-size:.72em;'),
        ('.prog{display:flex; align-items:center; gap:8px; margin-top:6px; font-size:13px}', '.prog{display:flex; align-items:center; gap:8px; margin-top:6px; font-size:.82em}'),
        ('font-size:16px; font-weight:600; display:flex; flex-direction:column;', 'font-size:1em; font-weight:600; display:flex; flex-direction:column;'),
        ('.dock .ic{font-size:20px}', '.dock .ic{font-size:1.25em}'),
        ('color:#1a1408; font-weight:700; font-size:17px}', 'color:#1a1408; font-weight:700; font-size:1.06em}'),
        ('border:1px solid var(--line); font-size:15px}\n.chip[aria-pressed', 'border:1px solid var(--line); font-size:.94em}\n.chip[aria-pressed'),
        ('border-radius:8px; background:var(--panel-2); border:1px solid var(--line); font-size:13px; font-weight:700}', 'border-radius:8px; background:var(--panel-2); border:1px solid var(--line); font-size:.82em; font-weight:700}'),
        ('.item .nm{font-size:15px}', '.item .nm{font-size:.94em}'),
        ('.item .ef{font-size:12px; color:var(--dim); margin-top:1px}', '.item .ef{font-size:.75em; color:var(--dim); margin-top:1px}'),
        ('.tagx{font-size:11px;', '.tagx{font-size:.7em;'),
        ('button.tagx{min-height:44px; min-width:44px; padding:0 12px; font-size:13px; border-radius:10px}', 'button.tagx{min-height:44px; min-width:44px; padding:0 12px; font-size:.82em; border-radius:10px}'),
        ('.god .n{font-size:12px;', '.god .n{font-size:.78em;'),
        ('.god .seen{font-size:10px; color:var(--good)}', '.god .seen{font-size:.68em; color:var(--good)}'),
        ('.rec .rk{font-size:12px; font-weight:700; color:var(--accent)}', '.rec .rk{font-size:.75em; font-weight:700; color:var(--accent)}'),
        ('.rec .sc{margin-left:auto; font-size:12px; color:var(--dim)}', '.rec .sc{margin-left:auto; font-size:.75em; color:var(--dim)}'),
        ('.rec .nm{font-size:18px;', '.rec .nm{font-size:1.13em;'),
        ('.rec.r1 .nm{font-size:22px}', '.rec.r1 .nm{font-size:1.38em}'),
        ('.rec .rs{font-size:14px; color:var(--text); margin-top:5px}', '.rec .rs{font-size:.88em; color:var(--text); margin-top:5px}'),
        ('.badge{font-size:12px;', '.badge{font-size:.75em;'),
        ('.warns div{font-size:13px; color:#ffb3b3; margin:2px 0}', '.warns div{font-size:.82em; color:#ffb3b3; margin:2px 0}'),
        ('border-radius:10px; padding:6px 8px; font-size:13px}', 'border-radius:10px; padding:6px 8px; font-size:.82em}'),
        ('.pick .rar{border:1px solid var(--line); border-radius:6px; padding:2px 6px; font-size:11px; color:var(--dim)}', '.pick .rar{border:1px solid var(--line); border-radius:6px; padding:2px 6px; font-size:.7em; color:var(--dim)}'),
        ('.pick .x{color:var(--dim); padding:0 4px; font-size:16px}', '.pick .x{color:var(--dim); padding:0 4px; font-size:1em}'),
        ('.wcard .n{font-size:16px; font-weight:700}', '.wcard .n{font-size:1em; font-weight:700}'),
        ('.wcard .a{font-size:12px; color:var(--dim); margin-top:3px}', '.wcard .a{font-size:.75em; color:var(--dim); margin-top:3px}'),
        ('border-radius:10px; padding:8px; font-size:12px; font-family:ui-monospace,monospace}', 'border-radius:10px; padding:8px; font-size:.75em; font-family:ui-monospace,monospace}'),
        ('border-radius:10px; padding:0 12px; font-size:15px}', 'border-radius:10px; padding:0 12px; font-size:.94em}'),
        ('border-radius:12px; padding:10px 12px; font-size:12px;', 'border-radius:12px; padding:10px 12px; font-size:.75em;'),
        ('.empty{text-align:center; color:var(--dim); font-size:14px; padding:26px 20px}', '.empty{text-align:center; color:var(--dim); font-size:.88em; padding:26px 20px}'),
    ]:
        c = sub(c, old, new, 'U1 ' + old[:28])

    # U5: 신 버튼 테두리 — 미선택 반투명, 선택 시 신 색 3px + 글로우 + 틴트
    c = sub(c, """.god{min-height:74px; border-radius:14px; background:var(--panel); border:2px solid var(--line);
  display:flex; flex-direction:column; align-items:center; justify-content:center; gap:3px; padding:6px 2px}""",
""".god{position:relative; min-height:74px; border-radius:14px; background:var(--panel);
  border:2px solid rgba(255,255,255,.14); display:flex; flex-direction:column; align-items:center;
  justify-content:center; gap:3px; padding:6px 2px; transition:none}
.god[data-gc]{border-color:var(--gcd)}
.god .ord{position:absolute; top:4px; right:6px; font-size:.7em; font-weight:700; color:var(--gc)}""", 'U5 god')
    c = sub(c, '.god[aria-pressed="true"]{background:var(--panel-2); box-shadow:0 0 0 2px var(--accent) inset}',
""".god[aria-pressed="true"]{border-width:3px; border-color:var(--gc); background:var(--gct);
  box-shadow:0 0 0 3px var(--gcg)}""", 'U5 pressed')

    # U2/U4 신규 클래스
    c += """
/* U2 이해도 스텝퍼 */
.stepper{display:flex; align-items:center; gap:10px}
.stepper button{width:48px; height:48px; border-radius:12px; background:var(--panel-2);
  border:1px solid var(--line); font-size:1.25em; font-weight:700}
.stepper button:disabled{opacity:.35}
.stepper .val{min-width:56px; text-align:center; font-size:1.25em; font-weight:700}
.atag{font-size:.68em; padding:2px 7px; border-radius:999px; border:1px solid var(--line); color:var(--dim); flex:0 0 auto}
.atag.핵심{color:var(--accent); border-color:var(--accent)}
.atag.무기{color:var(--info); border-color:var(--info)}
.atag.각성{color:var(--good); border-color:var(--good)}
.arow{display:flex; align-items:center; gap:8px; padding:7px 0; border-bottom:1px solid var(--line)}
.arow:last-child{border-bottom:none}
.arow .g{display:inline-flex; align-items:center; justify-content:center; width:26px; height:26px; flex:0 0 26px;
  border-radius:8px; background:var(--panel-2); border:1px solid var(--line); font-size:.8em; font-weight:700}
.arow.free .g{border-color:var(--good); color:var(--good)}
.giver{color:var(--accent); font-size:.72em}

/* U4 은혜 추천을 트레이 안으로 (하단 고정, 내부 스크롤) */
.tray{max-height:70vh; display:flex; flex-direction:column}
.tray .thead{display:flex; align-items:center; gap:8px; min-height:40px; padding:2px 0 6px; font-size:.82em; color:var(--dim)}
.tray .thead .caret{margin-left:auto; font-size:1em}
.tray .recs{overflow-y:auto; max-height:45vh; margin:0 -14px; padding:0 14px}
.crec{display:flex; align-items:flex-start; gap:8px; padding:9px 0; border-top:1px solid var(--line)}
.crec:first-child{border-top:none}
.crec .rk{flex:0 0 auto; font-size:.75em; font-weight:700; color:var(--dim); min-width:26px; padding-top:3px}
.crec.r1 .rk{color:var(--accent)}
.crec .mid{flex:1; min-width:0}
.crec .nm{display:flex; align-items:center; gap:6px; font-size:.94em; font-weight:600}
.crec.r1 .nm{font-size:1.13em; font-weight:700}
.crec .rs{font-size:.78em; color:var(--dim); margin-top:2px}
.crec .wn{font-size:.75em; color:#ffb3b3; margin-top:3px}
.crec .go{flex:0 0 auto; min-height:44px; padding:0 14px; border-radius:11px; background:var(--panel-2);
  border:1px solid var(--line); font-size:.82em; align-self:center}
.crec.r1 .go{background:var(--accent); color:#1a1408; font-weight:700; border-color:var(--accent)}
.crec.no{opacity:.5}
.crec .bdg{display:inline-block; font-size:.68em; padding:1px 6px; border-radius:999px; border:1px solid var(--duo); color:var(--duo)}
"""
    wr('app.css', c); print('app.css: U1/U5 + 신규 클래스')

# ══════════════════ app.js ══════════════════
j = rd('app.js')
if 'font_scale' in j:
    print('app.js: 이미 적용됨'); sys.exit(0)

# PREFS에 font_scale, grasp_cap 기본 20
j = sub(j, "var PREFS = ls('h2.prefs.v1') || { owned_keepsakes: [], grasp_cap: 10, left_hand: false, show_score: true, last_weapon: 'staff', last_aspect: 'staff_melinoe' };",
"""var PREFS = ls('h2.prefs.v1') || {};
  PREFS = Object.assign({ owned_keepsakes: [], grasp_cap: 10, left_hand: false, show_score: true, font_scale: 1, last_weapon: 'staff', last_aspect: 'staff_melinoe' }, PREFS);""", 'prefs')

# U1: 글자 배율 적용 + U5용 색 헬퍼
j = sub(j, "  function el(html) { var d = document.createElement('div'); d.innerHTML = html; return d.firstElementChild; }",
"""  function el(html) { var d = document.createElement('div'); d.innerHTML = html; return d.firstElementChild; }
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
  }""", 'helpers')

j = sub(j, "  var app = document.getElementById('app');\n  function render() {\n    app.innerHTML = '';",
        "  var app = document.getElementById('app');\n  function render() {\n    app.innerHTML = ''; applyFontScale();", 'render fs')

# U2 + U3: 런 시작 화면의 아르카나 / 기념품·비술
j = sub(j, """    root.appendChild(el('<h2>아르카나 (이해도 ' + r.arcana.grasp_used + '/' + r.arcana.grasp_cap + ')</h2>'));
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
    root.appendChild(kc);""",
"""    var A = r.arcana;
    root.appendChild(el('<h2>아르카나 (사용 ' + A.grasp_used + ' / 상한 ' + A.grasp_cap +
      (A.grasp_left > 0 ? ', 남음 ' + A.grasp_left : '') + ')</h2>'));
    var gc = el('<div class="card tight"><div class="row"><div class="mid" style="flex:1"><div class="sm">내 이해도 상한</div><div class="xs dim">재의 제단에서 넋으로 1씩 올린다 (10~30)</div></div></div></div>');
    gc.querySelector('.row').appendChild(stepper(PREFS.grasp_cap, 10, 30, function (v) {
      PREFS.grasp_cap = v; savePrefs(); rerenderStart(root, asSheet);
    }));
    root.appendChild(gc);

    var ac = el('<div class="card tight"></div>');
    var arow = function (c, cls, tag) {
      return el('<div class="arow ' + (cls || '') + '"><span class="g">' + (c.grasp === 0 ? '0' : c.grasp) + '</span>' +
        '<div class="mid" style="flex:1;min-width:0"><div class="ell">' + esc(c.name_ko) + '</div>' +
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

    root.appendChild(el('<h2>기념품 · 비술</h2>'));
    var kc = el('<div class="card tight"></div>');
    r.keepsakes.slice(0, 3).forEach(function (k) {
      kc.appendChild(el('<div style="padding:6px 0"><div class="sm">' + esc(k.name_ko) +
        (k.giver_ko ? ' <span class="giver">(' + esc(k.giver_ko) + '에게 넥타르)</span>' : '') +
        '</div><div class="xs dim ell">' + esc(k.effect) + '</div></div>'));
    });
    r.hexes.slice(0, 2).forEach(function (h) {
      kc.appendChild(el('<div style="padding:6px 0"><div class="sm">' + esc(h.name_ko) +
        ' <span class="giver">(셀레네 · 밤마다 1개)</span> <span class="xs dim">마력 ' + h.mana + '</span>' +
        '</div><div class="xs dim ell">' + esc(h.effect) + '</div></div>'));
    });
    root.appendChild(kc);""", 'U2/U3 start')

# U5: 신 버튼
j = sub(j, """      var b = el('<button class="god" aria-pressed="false" style="border-color:' + GC[id] + '">' +
        '<span class="dot" style="background:' + GC[id] + '"></span><span class="n">' + esc(nm(id)) + '</span>' +
        (seen ? '<span class="seen">✓ 받음</span>' : '') + '</button>');""",
"""      var b = el('<button class="god" data-gc aria-pressed="false" style="--gc:' + GC[id] + '; --gcd:' + rgba(GC[id], .45) +
        '; --gcg:' + rgba(GC[id], .3) + '; --gct:' + rgba(GC[id], .12) + '">' +
        '<span class="ord"></span><span class="dot" style="background:' + GC[id] + '"></span>' +
        '<span class="n">' + esc(nm(id)) + '</span>' +
        (seen ? '<span class="seen">✓ 받음</span>' : '') + '</button>');""", 'U5 god btn')
j = sub(j, """      GOD_ORDER.forEach(function (id) { btns[id].setAttribute('aria-pressed', godSel.indexOf(id) >= 0); });""",
"""      var ORD = ['①', '②', '③', '④'];
      GOD_ORDER.forEach(function (id) {
        var i = godSel.indexOf(id);
        btns[id].setAttribute('aria-pressed', i >= 0);
        btns[id].querySelector('.ord').textContent = i >= 0 ? (ORD[i] || (i + 1)) : '';
      });""", 'U5 ord')

# U4: 추천을 트레이 안으로
j = sub(j, """    var listBox = el('<div class="list"></div>');
    var recBox = el('<div></div>');
    var trayBox = el('<div class="tray"></div>');""",
"""    var listBox = el('<div class="list"></div>');
    var trayBox = el('<div class="tray"></div>');""", 'U4 boxes')
j = sub(j, "    body.appendChild(listBox);\n    body.appendChild(recBox);\n", "    body.appendChild(listBox);\n", 'U4 append')
j = sub(j, "      drawList(); drawTray(); drawRec();\n    }", "      drawList(); drawTray();\n    }", 'U4 draw')
j = sub(j, """    function drawTray() {
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
    }""",
"""    function drawTray() {
      trayBox.innerHTML = '';
      // 추천을 트레이 안에 넣어 목록을 스크롤하면서도 순위가 늘 보이게 한다 (U4)
      if (pickSel.length >= 2) {
        var hd = el('<button class="thead"><span>추천 ' + pickSel.length + '개 비교</span><span class="caret">' + (trayOpen ? '▾' : '▴') + '</span></button>');
        hd.onclick = function () { trayOpen = !trayOpen; draw(); };
        trayBox.appendChild(hd);
        if (trayOpen) {
          var box = el('<div class="recs"></div>');
          var rows = isBoon ? E.recommendBoons(RUN.state, pickSel) : E.recommendHammers(RUN.state, pickSel.map(function (p) { return p.id; }));
          rows.forEach(function (r, i) { box.appendChild(compactRec(r, i, isBoon)); });
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
    function compactRec(r, i, isBoon) {
      var no = !isFinite(r.score);
      var w = r.warnings || [];
      var mainBadge = (r.badges || []).filter(function (b) { return b !== '항상'; })[0] || '';
      var row = el('<div class="crec ' + (i === 0 && !no ? 'r1' : '') + ' ' + (no ? 'no' : '') + '">' +
        '<span class="rk">' + (r.rank || i + 1) + '위</span>' +
        '<div class="mid"><div class="nm">' + slotChip(ent(r.id)) + '<span class="ell">' + esc(nm(r.id)) + '</span>' +
        (mainBadge ? '<span class="bdg">' + esc(mainBadge) + '</span>' : '') + '</div>' +
        '<div class="rs ell">' + esc(r.reason) + '</div>' +
        (w.length ? '<div class="wn ell">⚠ ' + esc(w[0]) + (w.length > 1 ? ' +' + (w.length - 1) : '') + '</div>' : '') +
        '</div>' + (no ? '' : '<button class="go">결정</button>') + '</div>');
      if (!no) row.querySelector('.go').onclick = function () {
        pushHistory((isBoon ? '은혜' : '망치') + ' ' + nm(r.id));
        var rar = (pickSel.find(function (p) { return p.id === r.id; }) || {}).rarity;
        RUN.state = E.applyChoice(RUN.state, { kind: isBoon ? 'boon' : 'hammer', id: r.id, rarity: rar });
        pickSel = []; saveRun(); closeSheet();
      };
      return row;
    }""", 'U4 tray')
j = sub(j, "  var pickSel = [], godTab = null, searchOn = false, searchQ = '';",
        "  var pickSel = [], godTab = null, searchOn = false, searchQ = '', trayOpen = true;", 'trayOpen')

# U2/U1: 관리 화면 — 이해도 세그먼트 → 스텝퍼, 글자 크기 추가
j = sub(j, "    body.appendChild(seg('이해도 상한', [[10, '10'], [15, '15'], [20, '20'], [30, '30']], PREFS.grasp_cap, function (v) { PREFS.grasp_cap = v; savePrefs(); render(); }));",
"""    var gr = el('<div class="mrow"><div class="lb">이해도 상한<div class="xs dim">재의 제단에서 넋으로 1씩</div></div></div>');
    gr.appendChild(stepper(PREFS.grasp_cap, 10, 30, function (v) { PREFS.grasp_cap = v; savePrefs(); render(); }));
    body.appendChild(gr);
    body.appendChild(seg('글자 크기', [[1, '보통'], [1.15, '크게'], [1.3, '아주 크게']], PREFS.font_scale, function (v) { PREFS.font_scale = v; savePrefs(); render(); }));""", 'U2 manage')

wr('app.js', j); print('app.js: U1~U5 적용')
