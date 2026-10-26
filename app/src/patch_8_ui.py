# -*- coding: utf-8 -*-
"""8-D UI (페이블, 2026-10-26) — 빌드 카드.
1. 런 시작: 방향 카드 안에 커뮤니티 빌드 카드(강함 S/A/B · 신뢰 ◎○△ · 주요 신 · 필수 · 융합 · 끝내기 · 근거). [이 빌드로] 토글 → 시작 시 고정.
2. 홈: 고정한 빌드의 체크리스트(필수 ☑/☐ · 신 · 융합 진행 · 끝내기 · 보조/망치).
3. 관리: 빌드 변경/해제 칩.
4. 로그: run 헤더 bld, 변경 시 {t:'build', v}.
배지 '목표'·'목표 보조'·'끝내기'는 엔진이 주고 기존 badgeHtml이 그린다.
"""
import io, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JS = os.path.join(ROOT, 'app', 'src', 'app.js'); CSS = os.path.join(ROOT, 'app', 'src', 'app.css')
def load(p): return io.open(p, encoding='utf-8').read()
def save(p, s): io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, old, new, n=1):
    c = s.count(old); assert c == n, ('anchor %d != %d: %r' % (c, n, old[:90])); return s.replace(old, new)

s = load(JS)
if 'variantCard' in s:
    print('app.js: 이미 적용됨'); sys.exit(0)

# 상태에 variant
s = rep(s, "gods_seen: [], direction_lock: null }, pending_god: null, history: [] };",
           "gods_seen: [], direction_lock: null, variant: null }, pending_god: null, history: [] };")

# 공용: 빌드 카드 렌더
s = rep(s, "  function playstyleBox(dirId, weapon, phase, open) {",
"""  // 8-D: 빌드 카드. 커뮤니티 빌드를 합치지 않고 그대로 — 강함(S/A/B)·신뢰(◎ 출처 2+ 또는 실플레이 / ○ 출처 1 / △ 추론)
  var TRUST = { high: '◎', mid: '○', low: '△' };
  var godsHtml = function (gs, seenSet) { return gs.map(function (g, i) { return '<span style="color:' + (GC[g.id] || 'inherit') + ';font-weight:' + (i ? 400 : 700) + '">' + esc(g.name_ko) + (seenSet && seenSet[g.id] ? '<span class="xs">✓</span>' : '') + '</span>'; }).join(' <span class="dim">›</span> '); };
  // 8-G: 융합 조건 남은 것 — 마지막 하나만 남았으면 선택지를 전부, 아니면 "필요: 신 + 신 + …" 한 줄
  function needsLine(n) {
    var un = n.groups.filter(function (g) { return !g.met; });
    if (un.length === 1) { var g = un[0]; return el('<div class="xs dim" style="margin-left:8px">남음: ' + (g.god ? esc(g.god) + ' ' : '') + esc(g.options.join(' 또는 ')) + (g.more ? ' 외 ' + g.more : '') + '</div>'); }
    return el('<div class="xs dim" style="margin-left:8px">필요: ' + un.map(function (g) { return g.god ? esc(g.god) + ' 은혜' : esc(g.options.map(function (o) { return o.replace(/\\(.*\\)$/, ''); }).join('/')); }).join(' + ') + '</div>');
  }
  function variantCard(v, selected, onPick) {
    var c = el('<div class="vcard' + (selected ? ' sel' : '') + '">' +
      '<div class="row"><span class="vstr ' + v.strength + '">' + v.strength + '</span><b class="ell" style="flex:1">' + esc(v.name_ko) + '</b><span class="xs dim" title="신뢰도">' + (TRUST[v.trust] || '') + '</span></div>' +
      '<div class="xs" style="margin-top:4px">' + godsHtml(v.main_gods) + '</div>' +
      '<div class="xs" style="margin-top:3px"><span class="dim">필수</span> ' + v.must.map(function (m) { return esc(m.name_ko) + '<span class="dim">(' + esc(m.slot_ko) + ')</span>'; }).join(' · ') + '</div>' +
      (v.target_duos.length || v.finisher ? '<div class="xs" style="margin-top:3px"><span class="dim">융합</span> ' + v.target_duos.map(function (d) { return esc(d.name_ko) + '(' + d.tier + ')'; }).join(', ') +
        (v.finisher ? (v.target_duos.length ? ' <span class="dim">→</span> ' : '') + '<b>끝내기 ' + esc(v.finisher.name_ko) + '(' + v.finisher.tier + ')</b>' : '') + '</div>' : '') +
      '<details class="xs dim" style="margin-top:4px"><summary>근거 · 메모</summary><div style="margin-top:4px">' + esc(v.strength_note) + '</div><div style="margin-top:4px">' + esc(v.note) +
        (v.finisher ? '<div style="margin-top:4px">끝내기: ' + esc(v.finisher.note) + '</div>' : '') + '</div>' +
        (v.support.length ? '<div style="margin-top:4px">보조: ' + esc(v.support.map(function (x) { return x.name_ko; }).join(', ')) + '</div>' : '') +
        (v.hammers.length ? '<div style="margin-top:4px">망치: ' + esc(v.hammers.map(function (x) { return x.name_ko; }).join(', ')) + '</div>' : '') +
        '<div style="margin-top:4px">' + esc((v.sources || []).join(' / ')) + '</div></details>' +
      (onPick ? '<div class="row" style="justify-content:flex-end;margin-top:6px"><button class="tagx vpick">' + (selected ? '✓ 이 빌드로 시작' : '이 빌드로') + '</button></div>' : '') + '</div>');
    if (onPick) c.querySelector('.vpick').onclick = function () { onPick(v.id); };
    return c;
  }
  function playstyleBox(dirId, weapon, phase, open) {""")

# 런 시작: 방향 카드 안에 빌드 카드 + CTA 고정
s = rep(s, "  var startSel = { weapon: PREFS.last_weapon, aspect: PREFS.last_aspect };",
           "  var startSel = { weapon: PREFS.last_weapon, aspect: PREFS.last_aspect, variant: null };")
s = rep(s, """      var pb = playstyleBox(d.id, startSel.weapon, null, false);
      if (pb) dc.appendChild(pb);
      if (anyBadge && !badge) {""",
"""      var pb = playstyleBox(d.id, startSel.weapon, null, false);
      if (pb) dc.appendChild(pb);
      // 8-D: 커뮤니티 빌드 카드 — 고르면 그 빌드로 시작 (방향 고정 + 목표 배지 + 홈 체크리스트)
      if (d.variants && d.variants.length) {
        var vb = el('<div class="vlist"><div class="xs dim" style="margin-top:8px">커뮤니티 빌드 ' + d.variants.length + '개 — 하나를 고르면 그 빌드의 필수 은혜를 목표로 안내합니다</div></div>');
        d.variants.forEach(function (v) { vb.appendChild(variantCard(v, startSel.variant === v.id, function (id) { startSel.variant = startSel.variant === id ? null : id; rerenderStart(root, asSheet); })); });
        dc.appendChild(vb);
      }
      if (anyBadge && !badge) {""")
s = rep(s, """    var cta = el('<div class="cta"><button>이 무기로 시작</button></div>');
    cta.querySelector('button').onclick = function () {
      PREFS.last_weapon = startSel.weapon; PREFS.last_aspect = startSel.aspect; savePrefs();
      RUN = newRun(startSel.weapon, startSel.aspect); saveRun();
      logPush({ t: 'run', ts: nowKst(), w: RUN.state.weapon, asp: RUN.state.aspect, grasp: PREFS.grasp_cap,
        arc: (r.arcana.cards || []).map(function (c) { return c.id; }), eng: DATA.__build || null, sv: 1 });""",
"""    var selV = null; r.directions.forEach(function (d) { (d.variants || []).forEach(function (v) { if (v.id === startSel.variant) selV = v; }); });
    if (startSel.variant && !selV) startSel.variant = null;   // 무기·양상을 바꿔 그 빌드가 없어지면 해제
    var cta = el('<div class="cta"><button>' + (selV ? esc('\\'' + selV.name_ko.slice(0, 14) + '\\' 빌드로 시작') : '이 무기로 시작 (빌드 자유)') + '</button></div>');
    cta.querySelector('button').onclick = function () {
      PREFS.last_weapon = startSel.weapon; PREFS.last_aspect = startSel.aspect; savePrefs();
      RUN = newRun(startSel.weapon, startSel.aspect);
      if (selV) RUN.state = E.applyChoice(RUN.state, { kind: 'variant', id: selV.id });   // 8-D
      saveRun();
      logPush({ t: 'run', ts: nowKst(), w: RUN.state.weapon, asp: RUN.state.aspect, grasp: PREFS.grasp_cap, bld: RUN.state.variant || null,
        arc: (r.arcana.cards || []).map(function (c) { return c.id; }), eng: DATA.__build || null, sv: 1 });""")

# 홈: 체크리스트
s = rep(s, "      (st.direction_lock ? '<span class=\"tagx\">🔒 고정</span>' : '') + '</div>');",
           "      (st.variant ? '<span class=\"tagx\">🔒 빌드</span>' : st.direction_lock ? '<span class=\"tagx\">🔒 고정</span>' : '') + '</div>');")
s = rep(s, "    card.appendChild(sl);\n",
"""    card.appendChild(sl);
    // 8-D: 고정한 빌드의 체크리스트 — "지금 뭐가 빠졌나"
    var chk = E.buildChecklist(engSt(st));
    if (chk) {
      var seenSet = {}; st.gods_seen.forEach(function (g) { seenSet[g] = 1; });
      var box = el('<div class="chk"><div class="row"><span class="vstr ' + chk.strength + '">' + chk.strength + '</span><b class="ell" style="flex:1">' + esc(chk.name_ko) + '</b><span class="xs dim">필수 ' + chk.must_done + '/' + chk.must.length + '</span></div></div>');
      chk.must.forEach(function (m) {
        box.appendChild(el('<div class="chkrow' + (m.owned ? ' done' : '') + '"><span class="bx">' + (m.owned ? '☑' : '☐') + '</span><span class="ell">' + esc(m.name_ko) + '</span><span class="xs dim">' + esc(m.slot_ko) + (m.filled_by && !m.owned ? ' · 지금 ' + esc(m.filled_by) : '') + '</span></div>'));
      });
      box.appendChild(el('<div class="xs" style="margin-top:6px"><span class="dim">신</span> ' + godsHtml(chk.main_gods, seenSet) + '</div>'));
      chk.target_duos.concat(chk.finisher ? [Object.assign({ fin: true }, chk.finisher)] : []).forEach(function (d) {
        if (d.total === undefined) return;
        box.appendChild(el('<div class="prog"><span class="xs ell" style="width:112px">' + (d.fin ? '끝내기 ' : '') + esc(d.name_ko) + '</span>' +
          '<div class="bar"><i style="width:' + (d.owned ? 100 : Math.round(d.satisfied / d.total * 100)) + '%"></i></div>' +
          '<span class="xs dim">' + (d.owned ? '획득' : d.satisfied + '/' + d.total + (d.satisfied === d.total ? ' 대기' : '')) + '</span></div>'));
      });
      var sup = chk.support.filter(function (x) { return x.owned; }).length, hm = chk.hammers.filter(function (x) { return x.owned; }).length;
      var det = el('<details class="xs dim" style="margin-top:6px"><summary>보조 ' + sup + '/' + chk.support.length + (chk.hammers.length ? ' · 망치 ' + hm + '/' + chk.hammers.length : '') + ' · 메모</summary></details>');
      det.appendChild(el('<div style="margin-top:4px">' + chk.support.map(function (x) { return (x.owned ? '☑ ' : '☐ ') + esc(x.name_ko); }).join(' · ') + '</div>'));
      if (chk.hammers.length) det.appendChild(el('<div style="margin-top:4px">망치: ' + chk.hammers.map(function (x) { return (x.owned ? '☑ ' : '☐ ') + esc(x.name_ko); }).join(' · ') + '</div>'));
      det.appendChild(el('<div style="margin-top:4px">' + esc(chk.note) + (chk.finisher ? '<br>끝내기: ' + esc(chk.finisher.note) : '') + '</div>'));
      box.appendChild(det);
      card.appendChild(box);
    }
""")

# 관리: 빌드 변경/해제
s = rep(s, """    body.appendChild(dl);

    body.appendChild(el('<h2>보유 목록</h2>'));""",
"""    body.appendChild(dl);

    // 8-D: 빌드 카드 변경/해제 (무기·양상의 모든 변형)
    body.appendChild(el('<h2>빌드 카드</h2>'));
    var vl = el('<div class="chips"></div>');
    var rs = E.recommendRunStart(st.weapon, st.aspect, { graspCap: PREFS.grasp_cap });
    rs.directions.forEach(function (d) {
      (d.variants || []).forEach(function (v) {
        var b = el('<button class="chip" aria-pressed="' + (st.variant === v.id) + '"><span class="vstr ' + v.strength + '">' + v.strength + '</span> ' + esc(v.name_ko) + '</button>');
        b.onclick = function () { var id = st.variant === v.id ? null : v.id; RUN.state = E.applyChoice(RUN.state, { kind: 'variant', id: id }); saveRun(); logPush({ t: 'build', v: id }); render(); };
        vl.appendChild(b);
      });
    });
    body.appendChild(vl);
    body.appendChild(el('<div class="wrap xs dim">빌드를 고르면 방향이 고정되고 그 빌드의 필수 은혜가 목표 배지로 올라옵니다. 다시 누르면 해제</div>'));

    body.appendChild(el('<h2>보유 목록</h2>'));""")
save(JS, s); print('app.js: 8-D 빌드 카드')

c = load(CSS)
if '.vcard' not in c:
    c = c.rstrip('\\n') + """

/* 8-D 빌드 카드 · 체크리스트 */
.vcard{border:1px solid var(--line); border-radius:10px; padding:8px 10px; margin-top:8px; background:var(--panel-2)}
.vcard.sel{border-color:var(--accent); box-shadow:0 0 0 1px var(--accent) inset}
.vcard .row{gap:8px}
.vstr{font-size:.72em; font-weight:800; border-radius:6px; padding:1px 6px; color:#1a1408; background:var(--dim)}
.vstr.S{background:#7ed491} .vstr.A{background:var(--accent)} .vstr.B{background:#9aa0a6}
.vcard .vpick{min-height:36px; padding:0 12px; font-size:.85em}
.chk{margin-top:10px; padding:10px; border:1px solid var(--line); border-radius:12px; background:var(--panel-2)}
.chkrow{display:flex; align-items:center; gap:8px; min-height:30px; font-size:.95em}
.chkrow .bx{width:1.2em; color:var(--accent)}
.chkrow.done{color:var(--dim)} .chkrow.done .ell{text-decoration:line-through}
.chip .vstr{margin-right:2px}
.badge.b-목표,.badge.b-끝내기{color:var(--accent); border-color:var(--accent); font-weight:700}
.badge.b-목표보조{color:var(--accent); border-color:var(--accent)}
"""
    save(CSS, c); print('app.css: 빌드 카드')
