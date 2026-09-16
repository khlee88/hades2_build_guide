# -*- coding: utf-8 -*-
"""5단계 UI 패치 (페이블, 2026-09-16). app/src/app.js + app.css.

5-A 신 선택: 1개만 골라도 결과, 순위 대신 등급(필수/좋음/보통/패스)·역할 태그·동급 칩. 셀레네·카오스 제외.
5-B 런 종료: "새 런 시작"을 누르면 먼저 뜨는 차단형 1탭 시트 — 지역 버튼이 곧 기록+다음. 체력 제거. 비술 제거.
5-C 아르카나 5×5 격자 (grid_position은 이미 25장 전부 있음).
5-D "열린 빌드 방향" → "추천 빌드", 주요 신 표시, 첫 기념품.
"""
import io, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JS = os.path.join(ROOT, 'app', 'src', 'app.js'); CSS = os.path.join(ROOT, 'app', 'src', 'app.css')
def load(p): return io.open(p, encoding='utf-8').read()
def save(p, s): io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, old, new, n=1):
    c = s.count(old); assert c == n, ('anchor %d != %d: %r' % (c, n, old[:90])); return s.replace(old, new)

s = load(JS)
if 'endbtns' in s:
    print('app.js: 이미 적용됨'); sys.exit(0)

# ── 셀레네·카오스 제외 (사용자: 빌드 필수가 아니라 옵션, 상황 판단으로 충분) ──
s = rep(s, "'hermes', 'artemis', 'athena', 'dionysus', 'selene', 'chaos'];", "'hermes', 'artemis', 'athena', 'dionysus'];  // 셀레네·카오스는 5단계에서 제외 — 빌드 필수가 아닌 옵션")
s = rep(s, "    else if (String(UI.screen).indexOf('guest:') === 0) app.appendChild(guestSheet(UI.screen.slice(6)));\n", "")
i0 = s.index('  // 은혜 목록이 없는 신 — 문을 골라도 빈 목록이 뜨던 문제 (U6)')
i1 = s.index('\n  var pickSel = [], godTab')
s = s[:i0] + s[i1 + 1:]
s = rep(s, "          if (GUEST_INFO[r.id]) { UI.screen = 'guest:' + r.id; saveUI(); render(); return; }\n", "")
s = rep(s, "          if (GUEST_INFO[id]) { UI.screen = 'guest:' + id; saveUI(); render(); return; }\n", "")

# ── 5-B 체력 제거 ──
s = rep(s, "gods_seen: [], hp_state: 'mid', direction_lock: null }", "gods_seen: [], direction_lock: null }")
s = rep(s, "      t: 'pick', kind: kind, rg: st.region, hp: st.hp_state, ns: filledSlots(st),", "      t: 'pick', kind: kind, rg: st.region, ns: filledSlots(st),")
s = rep(s, "    var hp = { high: '●●●', mid: '●●○', low: '●○○' }[st.hp_state];\n", "")
s = rep(s, "      '<button class=\"tagx\" data-region>' + st.region + '지역</button><button class=\"tagx\" data-hp>' + hp + '</button>' +",
           "      '<button class=\"tagx\" data-region>' + st.region + '지역</button>' +")
s = rep(s, "    meta.querySelector('[data-hp]').onclick = function () { cycleHp(); };\n", "")
s = rep(s, """  function cycleHp() {
    var o = ['high', 'mid', 'low'], i = o.indexOf(RUN.state.hp_state);
    RUN.state.hp_state = o[(i + 1) % 3]; saveRun(); logPush({ t: 'hp', v: RUN.state.hp_state }); render();
  }
""", "")
s = rep(s, "    body.appendChild(seg('체력', [['high', '●●●'], ['mid', '●●○'], ['low', '●○○']], st.hp_state, function (v) { st.hp_state = v; saveRun(); logPush({ t: 'hp', v: v }); render(); }));\n", "")
# 비술 섹션 제거 (관리)
s = rep(s, """    body.appendChild(el('<h2>비술</h2>'));
    var hx = el('<div class="chips"></div>');
    DATA.hexes.forEach(function (h) {
      var b = el('<button class="chip" aria-pressed="' + (st.hex === h.id) + '">' + esc(h.name_ko) + '</button>');
      b.onclick = function () { st.hex = st.hex === h.id ? null : h.id; saveRun(); logPush({ t: 'hex', v: st.hex }); render(); };
      hx.appendChild(b);
    });
    body.appendChild(hx);
""", "")

# ── 5-B 런 종료: 차단형 1탭 시트 ──
s = rep(s, "  var endSel = { route: 'under', res: 'died', upto: 1 };\n  function viewStart(asSheet) {\n    var root = document.createElement('div');\n",
"""  var endSel = { route: PREFS.last_route || 'under', res: 'died' };
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
""")
# 기존 결과 패널 + CTA 교체
i0 = s.index('    // 지난 런이 있으면 결과를 먼저 받는다 (탭 두세 번)')
i1 = s.index("    root.appendChild(cta);\n    return root;\n  }\n  function rerenderStart")
s = s[:i0] + """    var cta = el('<div class="cta"><button>이 무기로 시작</button></div>');
    cta.querySelector('button').onclick = function () {
      PREFS.last_weapon = startSel.weapon; PREFS.last_aspect = startSel.aspect; savePrefs();
      RUN = newRun(startSel.weapon, startSel.aspect); saveRun();
      logPush({ t: 'run', ts: nowKst(), w: RUN.state.weapon, asp: RUN.state.aspect, grasp: PREFS.grasp_cap,
        arc: (r.arcana.cards || []).map(function (c) { return c.id; }), eng: DATA.__build || null, sv: 1 });
      UI.screen = null; saveUI(); render();
    };
""" + s[i1:]

# ── 5-C 아르카나 격자 + (행,열) ──
s = rep(s, """    var ac = el('<div class="card tight"></div>');
    var arow = function (c, cls, tag) {
      return el('<div class="arow ' + (cls || '') + '"><span class="g">' + (c.grasp === 0 ? '0' : c.grasp) + '</span>' +
        '<div class="mid" style="flex:1;min-width:0"><div class="ell">' + esc(c.name_ko) + '</div>' +""",
"""    // 5-C: 게임 화면과 같은 5×5 격자. 각성 조건("둘러싼 카드")이 격자 없이는 읽히지 않는다
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
        '<div class="mid" style="flex:1;min-width:0"><div class="ell">' + esc(c.name_ko) + pos(c) + '</div>' +""")

# ── 5-D 첫 기념품 · 추천 빌드 · 주요 신 (비술 표시 제거) ──
i0 = s.index("    root.appendChild(el('<h2>기념품 · 비술</h2>'));")
i1 = s.index("    root.appendChild(el('<h2>열린 빌드 방향</h2>'));")
s = s[:i0] + """    root.appendChild(el('<h2>첫 기념품</h2>'));
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

""" + s[i1:]
s = rep(s, "    root.appendChild(el('<h2>열린 빌드 방향</h2>'));", "    root.appendChild(el('<h2>추천 빌드</h2>'));")
s = rep(s, """        '<div class="xs dim" style="margin-top:6px">핵심 칸: ' + esc(d.core_slots.join(' · ')) + '</div>' +""",
"""        '<div class="sm" style="margin-top:6px">주요 신: ' + d.main_gods.map(function (g, i) { return '<span style="color:' + (GC[g.id] || 'inherit') + ';font-weight:' + (i ? 400 : 700) + '">' + esc(g.name_ko) + '</span>'; }).join(' <span class="dim">›</span> ') + '</div>' +
        '<div class="xs dim" style="margin-top:4px">핵심 칸: ' + esc(d.core_slots.join(' · ')) + '</div>' +""")

# ── 5-A 신 선택: 1개 허용, 등급·역할·동급 ──
s = rep(s, "문 위에 뜬 신을 2개 이상 골라 주세요</div>'));", "문 위에 뜬 신을 골라 주세요 — 하나만 떠도 됩니다. 등급이 <b>패스</b>면 석류·재화 문이 낫습니다</div>'));")
s = rep(s, """      if (godSel.length < 2) { out.appendChild(el('<div class="empty">신을 2개 이상 골라 주세요</div>')); return; }
      var grows = E.recommendGods(RUN.state, godSel);
      var gcs = closeSet(grows);
      grows.forEach(function (r, i) {
        out.appendChild(recCard(r, i, function () {""",
"""      if (!godSel.length) { out.appendChild(el('<div class="empty">문에 뜬 신을 눌러 주세요</div>')); return; }
      var grows = E.recommendGods(RUN.state, godSel);
      // 5-A: 점수 차 2 미만은 같은 군 — 첫 신처럼 변별이 없을 때 1·2·3위 대신 '동급' 칩
      var topTie = grows.filter(function (x) { return x.tie === grows[0].tie; }).length > 1;
      grows.forEach(function (r, i) {
        out.appendChild(recCard(r, i, function () {""")
s = rep(s, "        }, '이 문으로', gcs[r.id]));", "        }, '이 문으로', topTie && r.tie === grows[0].tie));")
# recCard: 등급 표시
s = rep(s, """    var c = el('<div class="rec ' + (i === 0 && !no ? 'r1' : '') + ' ' + (no ? 'no' : '') + '">' +
      '<div class="hd"><span class="rk">' + (r.rank || i + 1) + '위</span>' +""",
"""    var grade = r.grade || null;
    var c = el('<div class="rec ' + (i === 0 && !no && grade !== 'pass' ? 'r1' : '') + ' ' + (no ? 'no' : '') + (grade === 'pass' ? ' pass' : '') + '">' +
      '<div class="hd"><span class="rk' + (grade ? ' grade-' + grade : '') + '">' + (grade ? esc(r.grade_ko) : (r.rank || i + 1) + '위') + '</span>' +
      (r.roles && r.roles.length ? '<span class="roles xs dim ell">' + esc(r.roles.slice(0, 2).join(' · ')) + '</span>' : '') +""")
save(JS, s); print('app.js: 5단계 UI 반영')

c = load(CSS)
if '.agrid' not in c:
    c = c.rstrip('\n') + """

/* ── 5단계 (2026-09-16) ── */
.agrid{display:grid; grid-template-columns:repeat(5,1fr); gap:4px; padding:0 14px 10px}
.acell{min-height:52px; border:1px solid var(--line); border-radius:8px; padding:4px 2px; text-align:center; display:flex; flex-direction:column; justify-content:center; gap:2px; background:var(--panel-2); color:var(--dim)}
.acell .n{font-size:.6em; line-height:1.15; word-break:keep-all}
.acell .g{font-size:.58em; opacity:.75}
.acell.sel{background:var(--panel); color:var(--text); border-color:var(--accent); border-width:2px; font-weight:700}
.acell.free{border-style:dashed; color:var(--text)}
.rec .roles{margin-left:6px; min-width:0; flex:1}
.rk.grade-must{color:#7ed491} .rk.grade-good{color:var(--accent)} .rk.grade-ok{color:var(--dim)} .rk.grade-pass{color:#e05252}
.rec.pass{opacity:.72}
.endbtns{display:grid; grid-template-columns:repeat(5,1fr); gap:8px; padding:10px 14px}
.endbtns button{min-height:64px; border-radius:12px; background:var(--panel-2); border:1px solid var(--line); display:flex; flex-direction:column; align-items:center; justify-content:center; gap:2px; font-weight:700}
.endbtns button .big{font-size:1.4em}
.endbtns button[aria-pressed="true"]{border-color:var(--accent); border-width:2px; background:var(--panel)}
.endbtns button.clear{border-color:#7ed491; color:#7ed491}
"""
    save(CSS, c); print('app.css: 격자·등급·종료 버튼 스타일 추가')
