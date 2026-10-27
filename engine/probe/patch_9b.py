# -*- coding: utf-8 -*-
"""9-B (오퍼스, 2026-10-27): 밤의 언약 진행 + 공포별 맹세 조합 (런 시작 화면).

사용자: "무기마다 공포를 어떻게 찍을지" → 공포 반영 추천은 경우가 많아, 언약 단위 안내로.
 - data/testaments.json (RESEARCH_9A): 무기별 언약 8개 수호자 순서, 공포→맹세 사다리(common + multi/aoe/heavy), 방향→스타일
 - 엔진 recommendTestament(weapon, aspect, done, dirId): 다음 언약(공포·수호자·지역·악몽·쉬움), 맹세 조합(합 = 공포), 피할 맹세(방향·양상 기준)
 - UI: 런 시작 화면 '밤의 언약' 카드 — 진행 n/8 · 악몽 n/14, 다음 언약, 맹세 조합, 피할 것, [−] [깼다 ✓] (PREFS.testaments[weapon], 로그 {t:'testament'})
"""
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RJ = os.path.join(ROOT, 'engine', 'recommend.js'); TJ = os.path.join(ROOT, 'engine', 'test.js'); JS = os.path.join(ROOT, 'app', 'src', 'app.js'); CSS = os.path.join(ROOT, 'app', 'src', 'app.css'); BJ = os.path.join(ROOT, 'app', 'build.js')
def load(p): return io.open(p, encoding='utf-8').read()
def save(p, s): io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, old, new, n=1):
    c = s.count(old); assert c == n, ('anchor %d != %d: %r' % (c, n, old[:80])); return s.replace(old, new)

b = load(BJ)
if 'testaments' not in b:
    b = rep(b, "  hexes: 'hexes.json', builds: 'build_directions.json', gods: 'gods.json',", "  hexes: 'hexes.json', builds: 'build_directions.json', gods: 'gods.json', testaments: 'testaments.json',")
    save(BJ, b); print('build.js: testaments')

r = load(RJ)
if 'recommendTestament' not in r:
    r = rep(r, "  function recommendKeepsake(state) {",
"""  // 9-B: 밤의 언약 — 다음 언약과 그 공포에 맞는 맹세 조합. done = 이 무기에서 깬 언약 수(0~8)
  const ROUTE_KO = { under: '지하', surface: '지상' };
  const STYLE_KO = { multi: '연사·다타 빌드', aoe: '광역 빌드', heavy: '한 방 빌드' };
  function recommendTestament(weapon, aspect, done, dirId) {
    const T = data.testaments; if (!T || !T.order[weapon]) return null;
    const n = Math.max(0, Math.min(8, done | 0));
    const fears = T.fears;
    const earned = fears.slice(0, n).reduce((a, f) => a + (T.nightmare_by_fear[String(f)] || 0), 0);
    const maxN = fears.reduce((a, f) => a + (T.nightmare_by_fear[String(f)] || 0), 0);
    const d = (builds.weapons[weapon] || { directions: [] }).directions.find((x) => x.id === dirId) || null;
    const style = (d && T.style_by_direction[d.id]) || 'multi';
    const avoid = [];
    if (d && d.omega_dependent) avoid.push('자만 — 마력을 많이 쓰는 빌드');
    if (style === 'heavy') avoid.push('방호 — 한 방이 통째로 막힘');
    if ((T.void_sensitive_aspects || []).includes(aspect)) avoid.push('공허 — 이 양상은 아르카나 의존');
    for (const x of T.avoid_always || []) if (!avoid.some((y) => y.startsWith(x))) avoid.push(x);
    const out = { weapon, done: n, total: fears.length, earned, max_nightmare: maxN, finished: n >= fears.length, style, style_ko: STYLE_KO[style], hubris_ok: !!(d && !d.omega_dependent), avoid, direction_ko: d ? d.name_ko : null };
    if (out.finished) return out;
    const fear = fears[n];
    const gid = T.order[weapon][n], g = T.guardians[gid];
    const steps = (T.ladder.common[String(fear)] || T.ladder[style][String(fear)] || []);
    const vows = steps.map(([id, rank]) => { const v = T.vows[id]; return { id, name_ko: v.name_ko, rank, fear: v.fear[rank - 1], effect: v.effect[rank - 1] }; });
    return { ...out, next: { k: n + 1, fear, guardian: gid, guardian_ko: g.name_ko, route: g.route, route_ko: ROUTE_KO[g.route], region: g.region, nightmare: T.nightmare_by_fear[String(fear)] || 0, easy: g.region === 1 && fear >= 8 },
      vows, sum: vows.reduce((a, v) => a + v.fear, 0) };
  }

  function recommendKeepsake(state) {""")
    r = rep(r, "  return { recommendRunStart, recommendArcana, recommendGods, recommendBoons, recommendHammers, recommendKeepsake, directionScores, buildChecklist, applyChoice, validateState, _internal: { directionWeights, derive } };",
               "  return { recommendRunStart, recommendArcana, recommendGods, recommendBoons, recommendHammers, recommendKeepsake, recommendTestament, directionScores, buildChecklist, applyChoice, validateState, _internal: { directionWeights, derive } };")
    save(RJ, r); print('recommend.js: recommendTestament')

t = load(TJ)
if "testaments: load('testaments.json')" not in t:
    t = rep(t, "  hexes: load('hexes.json'), builds: load('build_directions.json'), gods: load('gods.json'),", "  hexes: load('hexes.json'), builds: load('build_directions.json'), gods: load('gods.json'), testaments: load('testaments.json'),")
if "sc('S56'" not in t:
    NEW = """

// ── 9-B 밤의 언약 (2026-10-27) ──────────────────────────
sc('S56', '밤의 언약 — 모든 무기·스타일·공포에서 맹세 합 = 요구 공포, 횃불 4번째 = 공포 8 헤카테(쉬움), 피할 맹세', () => {
  const bad = [];
  for (const w of ['staff', 'blades', 'flames', 'axe', 'skull', 'coat']) for (const d of data.builds.weapons[w].directions) for (let k = 0; k < 8; k++) {
    const t = E.recommendTestament(w, (d.aspects || [])[0], k, d.id);
    if (t.sum !== t.next.fear) bad.push(`${d.id} #${k + 1}: ${t.sum}≠${t.next.fear}`);
  }
  const fl = E.recommendTestament('flames', 'flames_moros', 3, 'flames_omega_special_orbit');
  const done = E.recommendTestament('flames', 'flames_moros', 8, 'flames_omega_special_orbit');
  const axe = E.recommendTestament('axe', 'axe_melinoe', 7, 'axe_heavy_attack');
  const sup = E.recommendTestament('flames', 'flames_supay', 0, 'flames_supay_auto');
  return { rows: fl.vows.map((v, i) => ({ id: v.id, rank: i + 1, score: v.fear, reason: v.name_ko + ' ' + v.rank + ' — ' + v.effect, warnings: [], badges: [] })), checks: [
    check('22방향 × 8언약 전부 맹세 합 = 공포', bad.length === 0, bad.slice(0, 5).join(' / ')),
    check('횃불 4번째 = 공포 8 · 헤카테 · 지하 1지역 · 쉬움 · 악몽 1', fl.next.k === 4 && fl.next.fear === 8 && fl.next.guardian === 'hecate' && fl.next.easy && fl.next.nightmare === 1, JSON.stringify(fl.next)),
    check('모로스 회전 불꽃 = 광역 빌드, 자만 피함(Ω 의존)', fl.style === 'aoe' && fl.avoid.some((x) => /^자만/.test(x)), fl.style + ' ' + fl.avoid.join(',')),
    check('8/8 완료 → 악몽 14/14', done.finished && done.earned === 14 && done.max_nightmare === 14, JSON.stringify({ e: done.earned, m: done.max_nightmare })),
    check('도끼 단발 = 한 방 빌드, 방호 피함, 자만 가능', axe.style === 'heavy' && axe.avoid.some((x) => /^방호/.test(x)) && axe.hubris_ok, axe.avoid.join(',')),
    check('수파이 = 공허 피함(아르카나 의존)', sup.avoid.some((x) => /^공허 — 이 양상/.test(x)), sup.avoid.join(',')),
  ] };
});
"""
    t = rep(t, "\n// ── 실행 ────────────────────────────────────────────────", NEW + "\n// ── 실행 ────────────────────────────────────────────────")
save(TJ, t); print('test.js: S56')

s = load(JS)
if 'testamentCard' not in s:
    s = rep(s, "  PREFS = Object.assign({ owned_keepsakes: [], grasp_cap: 10,", "  PREFS = Object.assign({ testaments: {}, owned_keepsakes: [], grasp_cap: 10,")
    s = rep(s, "    root.appendChild(el('<h2>추천 빌드</h2>'));",
"""    // 9-B: 밤의 언약 — 이 무기의 다음 언약과 맹세 조합. 빌드를 골랐으면 그 빌드의 방향, 아니면 1위 방향 기준
    var tDir = (r.directions[0] || {}).id;
    r.directions.forEach(function (d) { (d.variants || []).forEach(function (v) { if (v.id === startSel.variant) tDir = d.id; }); });
    var tc = testamentCard(startSel.weapon, startSel.aspect, tDir, function () { rerenderStart(root, asSheet); });
    if (tc) { root.appendChild(el('<h2>밤의 언약</h2>')); root.appendChild(tc); }
    root.appendChild(el('<h2>추천 빌드</h2>'));""")
    s = rep(s, "  function variantCard(v, selected, onPick) {",
"""  // 9-B: 밤의 언약 카드
  function testamentCard(weapon, aspect, dirId, rerender) {
    var done = (PREFS.testaments || {})[weapon] || 0;
    var t = E.recommendTestament(weapon, aspect, done, dirId);
    if (!t) return null;
    var c = el('<div class="card tight tcard"></div>');
    c.appendChild(el('<div class="row"><b style="flex:1">' + esc(nm(weapon)) + '</b><span class="xs dim">' + t.done + '/' + t.total + ' 완료 · 악몽 ' + t.earned + '/' + t.max_nightmare + '</span></div>'));
    if (t.finished) c.appendChild(el('<div class="sm" style="margin-top:6px">이 무기의 언약 8개를 모두 깼습니다</div>'));
    else {
      var nx = t.next;
      c.appendChild(el('<div class="sm" style="margin-top:6px"><span class="dim">다음 ' + nx.k + '번째</span> <b>공포 ' + nx.fear + '</b> · ' + esc(nx.guardian_ko) + ' <span class="dim">(' + esc(nx.route_ko) + ' ' + nx.region + '지역)</span> · 악몽 ' + nx.nightmare +
        (nx.easy ? ' <span class="tagx asp only">쉬움 — 1지역 수호자</span>' : '') + '</div>'));
      c.appendChild(el('<div class="xs" style="margin-top:4px"><span class="dim">맹세</span> ' + t.vows.map(function (v) { return '<b>' + esc(v.name_ko) + ' ' + v.rank + '</b><span class="dim">(' + esc(v.effect) + ')</span>'; }).join(' · ') + ' <span class="dim">= 공포 ' + t.sum + '</span></div>'));
      c.appendChild(el('<div class="xs dim" style="margin-top:3px">' + esc(t.style_ko) + (t.direction_ko ? ' (' + esc(t.direction_ko) + ')' : '') + ' 기준' + (t.hubris_ok ? ' · Ω를 안 쓰면 자만을 방호·소요 대신 넣어도 됨' : '') + '</div>'));
    }
    c.appendChild(el('<div class="xs dim" style="margin-top:3px">피할 것: ' + esc(t.avoid.join(' · ')) + '</div>'));
    c.appendChild(el('<div class="xs dim" style="margin-top:3px">밤의 언약 = 이 무기로, 공포 이상으로, 그 수호자를 잡으면 달성 · 악몽은 양상 강화(일반 5 · 숨김 9)</div>'));
    var row = el('<div class="row" style="justify-content:flex-end;gap:8px;margin-top:8px"><button class="tagx tbtn" data-m>−</button>' + (t.finished ? '' : '<button class="tagx tbtn primary" data-p>깼다 ✓</button>') + '</div>');
    var setN = function (v) { PREFS.testaments = PREFS.testaments || {}; PREFS.testaments[weapon] = Math.max(0, Math.min(8, v)); savePrefs(); logPush({ t: 'testament', w: weapon, v: PREFS.testaments[weapon] }); rerender(); };
    row.querySelector('[data-m]').onclick = function () { if (done > 0) setN(done - 1); };
    if (!t.finished) row.querySelector('[data-p]').onclick = function () { setN(done + 1); };
    c.appendChild(row);
    return c;
  }
  function variantCard(v, selected, onPick) {""")
    save(JS, s); print('app.js: 밤의 언약 카드')

c = load(CSS)
if '.tcard' not in c:
    c = c.rstrip('\n') + """

/* 9-B 밤의 언약 */
.tcard .tbtn{min-height:44px; min-width:44px; padding:0 14px; font-size:.9em}
.tcard .tbtn.primary{color:var(--accent); border-color:var(--accent)}
"""
    save(CSS, c); print('app.css: tcard')
