# -*- coding: utf-8 -*-
"""4-A (페이블): 아르카나 추천 재설계.
 1) arcana.json — 0 이해도 카드에 구조화된 각성 조건(awaken) 추가
 2) recommend.js — recommendArcana(weapon, aspect, graspCap) 신설, recommendRunStart가 사용
 3) validate.js — 0 이해도 카드는 awaken 필수
 4) test.js — S23/S24 추가
정본 설명은 engine/DESIGN.md §14."""
import io, os, sys, json
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = lambda *a: os.path.join(ROOT, *a)
def rd(p): return io.open(p, encoding='utf-8').read()
def wr(p, s): io.open(p, 'w', encoding='utf-8').write(s)
def sub(s, old, new, tag):
    if old not in s: print('패턴 못 찾음:', tag); sys.exit(1)
    return s.replace(old, new, 1)

# ── 1) arcana.json: 각성 조건 구조화 (격자 5×5, 인접 = 8방향) ──
A = json.load(io.open(P('data', 'arcana.json'), encoding='utf-8'))
AWAKEN = {
    'the_moon':    {'type': 'adjacent_any'},                 # 둘러싼 카드 중 하나 활성화
    'the_centaur': {'type': 'one_each_cost', 'costs': [1, 2, 3, 4, 5]},  # 비용 1~5 카드 각 1장
    'the_queen':   {'type': 'max_same_cost', 'max': 2},     # 같은 비용 카드 2장 이내
    'the_fates':   {'type': 'adjacent_all'},                 # 둘러싼 카드 전부 활성화
    'divinity':    {'type': 'full_other_line'},              # 다른 행/열 5장 전부 활성화
    'judgement':   {'type': 'max_total', 'max': 3},          # 총 3장 이내 활성화
}
for c in A:
    if c['id'] in AWAKEN: c['awaken'] = AWAKEN[c['id']]
    elif c['grasp'] == 0: print('awaken 누락:', c['id']); sys.exit(1)
wr(P('data', 'arcana.json'), json.dumps(A, ensure_ascii=False, indent=1))
print('arcana.json: awaken 6장 추가')

# ── 2) recommend.js ──
p = P('engine', 'recommend.js'); s = rd(p)
if 'function recommendArcana' in s:
    print('recommend.js: 이미 적용됨')
else:
    s = sub(s, """  function recommendRunStart(weapon, aspect, opts) {
    const o = opts || {};
    const graspCap = o.graspCap ?? builds.arcana_beginner_set.grasp;
    const owned = o.ownedKeepsakes || null;
    const set = builds.arcana_beginner_set;
    const picked = [], free = [], never = set.never_with || [];
    let spent = 0;
    for (const id of [...(set.cards || []), ...(set.upgrade_path || [])]) {
      const c = arcanaById.get(id); if (!c) continue;
      if (picked.includes(id) || free.some((f) => f.id === id)) continue;
      if (never.some((p) => p.includes(id) && p.some((q) => q !== id && picked.includes(q)))) continue;
      // 이해도 0 카드는 각성 조건을 충족해야 활성화된다. 조건 판정을 일반화할 수 없으므로
      // 자동 선택에 넣지 않고 "조건 충족 시 무료"로 따로 안내한다.
      if (c.grasp === 0) { free.push({ id, name_ko: c.name_ko, effect: c.effect, awaken_condition: c.awaken_condition }); continue; }
      if (spent + c.grasp > graspCap) continue;
      picked.push(id); spent += c.grasp;
    }
    const state = { weapon, aspect, region: 1, boons: [], hammers: [], gods_seen: [], hp_state: 'mid' };
    const { all } = directionWeights(state);
    return {
      weapon, aspect,
      arcana: { grasp_used: spent, grasp_cap: graspCap, cards: picked.map((id) => ({ id, name_ko: nameOf(id), grasp: arcanaById.get(id).grasp, effect: arcanaById.get(id).effect })), free_cards: free },""",
"""  // ── §14 아르카나 (4-A 재설계) ─────────────────────────
  // 격자 5×5. 인접 = 8방향. 각성 조건은 arcana[].awaken 구조체로 판정한다.
  const ARC_W = W.ARCANA || { PRIORITY: { 1: 6, 2: 3, 3: 1 }, DIRECTION_HIT: 2, DIR_WEIGHTS: [1, 0.6, 0.4], AWAKEN_LOOKAHEAD: 1.5 };
  const arcPos = (c) => (c.grid_position || [0, 0]);
  const arcAdjacent = (c) => {
    const [r, col] = arcPos(c);
    return arcana.filter((o) => { const [r2, c2] = arcPos(o); return o.id !== c.id && Math.abs(r2 - r) <= 1 && Math.abs(c2 - col) <= 1; });
  };
  function awakenMet(c, activeSet) {
    const a = c.awaken; if (!a) return false;
    const act = arcana.filter((o) => activeSet.has(o.id));
    if (a.type === 'adjacent_any') return arcAdjacent(c).some((o) => activeSet.has(o.id));
    if (a.type === 'adjacent_all') return arcAdjacent(c).every((o) => activeSet.has(o.id));
    if (a.type === 'one_each_cost') return (a.costs || []).every((k) => act.some((o) => o.grasp === k));
    if (a.type === 'max_same_cost') { const cnt = {}; for (const o of act) if (o.grasp > 0) cnt[o.grasp] = (cnt[o.grasp] || 0) + 1; return Object.values(cnt).every((n) => n <= a.max) && act.length > 0; }
    if (a.type === 'max_total') return act.length > 0 && act.length <= a.max;
    if (a.type === 'full_other_line') {
      const [r, col] = arcPos(c);
      for (let i = 1; i <= 5; i++) {
        if (i !== r && arcana.filter((o) => arcPos(o)[0] === i).every((o) => activeSet.has(o.id))) return true;
        if (i !== col && arcana.filter((o) => arcPos(o)[1] === i).every((o) => activeSet.has(o.id))) return true;
      }
      return false;
    }
    return false;
  }
  // 활성 집합에서 각성되는 0 이해도 카드를 고정점까지 추가
  function awakenClosure(activeSet) {
    const out = new Set(activeSet); let changed = true;
    while (changed) {
      changed = false;
      for (const c of arcana) if (c.grasp === 0 && !out.has(c.id) && awakenMet(c, out)) { out.add(c.id); changed = true; }
    }
    return out;
  }
  function recommendArcana(weapon, aspect, graspCap) {
    const cap = Math.max(0, graspCap ?? builds.arcana_beginner_set.grasp);
    const state = { weapon, aspect, region: 1, boons: [], hammers: [], gods_seen: [], hp_state: 'mid' };
    const { all } = directionWeights(state);
    const dirs = all.filter((x) => Number.isFinite(x.F)).map((x) => x.d);
    const never = builds.arcana_beginner_set.never_with || [];
    // 카드 기본 점수: 초보 우선순위 + 무기 방향 힌트 (방향 순위별 가중)
    const baseScore = (c) => {
      if (c.grasp === 0) return -Infinity;                       // 0 이해도는 직접 고르지 않음 (각성으로만)
      const pr = ARC_W.PRIORITY[c.beginner_priority];
      if (pr === undefined) return -Infinity;                    // 0 = 비추천
      let sc = pr;
      dirs.forEach((d, i) => { if ((d.arcana || []).includes(c.id)) sc += ARC_W.DIRECTION_HIT * (ARC_W.DIR_WEIGHTS[Math.min(i, ARC_W.DIR_WEIGHTS.length - 1)]); });
      return sc;
    };
    const picked = []; let spent = 0;
    const tagOf = {};
    const blocked = (id) => never.some((p) => p.includes(id) && p.some((q) => q !== id && picked.includes(q)));
    while (true) {
      let best = null, bestVal = -Infinity;
      const active = awakenClosure(new Set(picked));
      for (const c of arcana) {
        if (picked.includes(c.id) || active.has(c.id) || blocked(c.id)) continue;
        if (c.grasp <= 0 || spent + c.grasp > cap) continue;
        let v = baseScore(c); if (!Number.isFinite(v)) continue;
        // 이 카드를 켜면 각성되는 0 이해도 카드가 있으면 가산 (공짜 카드)
        const after = awakenClosure(new Set([...picked, c.id]));
        const newlyFree = [...after].filter((id) => !active.has(id) && arcanaById.get(id).grasp === 0).length;
        v += newlyFree * ARC_W.AWAKEN_LOOKAHEAD;
        v = v / Math.sqrt(c.grasp);                                // 비용 효율: 같은 점수면 싼 카드
        if (v > bestVal) { bestVal = v; best = c; }
      }
      if (!best) break;
      picked.push(best.id); spent += best.grasp;
      const inDir = dirs.some((d) => (d.arcana || []).includes(best.id));
      tagOf[best.id] = best.beginner_priority === 1 ? '핵심' : (inDir ? '무기 방향' : '보조');
    }
    const active = awakenClosure(new Set(picked));
    const awakened = [...active].filter((id) => !picked.includes(id));
    const lockedFree = arcana.filter((c) => c.grasp === 0 && !active.has(c.id))
      .map((c) => ({ id: c.id, name_ko: c.name_ko, effect: c.effect, awaken_condition: c.awaken_condition }));
    const card = (id, tag) => { const c = arcanaById.get(id); return { id, name_ko: c.name_ko, grasp: c.grasp, effect: c.effect, tag }; };
    // 다음 후보: 이해도가 더 있었으면 들어갔을 카드 2장
    const nextUp = arcana.filter((c) => c.grasp > 0 && !picked.includes(c.id) && !blocked(c.id) && Number.isFinite(baseScore(c)))
      .sort((a, b) => baseScore(b) / Math.sqrt(b.grasp) - baseScore(a) / Math.sqrt(a.grasp)).slice(0, 2)
      .map((c) => card(c.id, '이해도 +' + c.grasp + ' 필요'));
    return {
      grasp_used: spent, grasp_cap: cap, grasp_left: cap - spent,
      cards: picked.map((id) => card(id, tagOf[id])),
      awakened: awakened.map((id) => card(id, '각성 — 무료')),
      free_cards: lockedFree,
      next_up: nextUp,
    };
  }

  function recommendRunStart(weapon, aspect, opts) {
    const o = opts || {};
    const graspCap = o.graspCap ?? builds.arcana_beginner_set.grasp;
    const owned = o.ownedKeepsakes || null;
    const arc = recommendArcana(weapon, aspect, graspCap);
    const state = { weapon, aspect, region: 1, boons: [], hammers: [], gods_seen: [], hp_state: 'mid' };
    const { all } = directionWeights(state);
    return {
      weapon, aspect,
      arcana: arc,""", 'recommendRunStart 교체')
    s = sub(s, "      keepsakes: (builds.keepsake_plan.region1 || []).filter((k) => !owned || owned.includes(k)).map((id) => ({ id, name_ko: nameOf(id), effect: keepsakeById.get(id).effect })),",
                 "      keepsakes: (builds.keepsake_plan.region1 || []).filter((k) => !owned || owned.includes(k)).map((id) => { const k = keepsakeById.get(id); return { id, name_ko: k.name_ko, effect: k.effect, giver_ko: k.giver_ko }; }),", 'keepsakes giver')
    s = sub(s, "      hexes: (builds.hex_beginner || []).map((id) => ({ id, name_ko: nameOf(id), effect: hexById.get(id).effect, mana: hexById.get(id).mana_to_charge })),",
                 "      hexes: (builds.hex_beginner || []).map((id) => ({ id, name_ko: nameOf(id), effect: hexById.get(id).effect, mana: hexById.get(id).mana_to_charge, giver_ko: '셀레네' })),", 'hexes giver')
    s = sub(s, "  return { recommendRunStart, recommendGods,", "  return { recommendRunStart, recommendArcana, recommendGods,", 'export')
    wr(p, s); print('recommend.js: recommendArcana 추가')

# weights.js: 아르카나 상수
p = P('engine', 'weights.js'); s = rd(p)
if 'ARCANA:' not in s:
    s = sub(s, "  // ── §5 신 풀 ─────────────────────────────────────────", """  // ── §14 아르카나 (4-A) ───────────────────────────────
  ARCANA: {
    PRIORITY: { 1: 6, 2: 3, 3: 1 },   // beginner_priority → 기본 점수. 0(비추천)은 후보 제외
    DIRECTION_HIT: 2,                 // 무기 방향의 arcana 힌트에 있으면 가산 (방향 순위 가중 곱)
    DIR_WEIGHTS: [1, 0.6, 0.4],       // 방향 1·2·3위 가중
    AWAKEN_LOOKAHEAD: 1.5,            // 이 카드를 켜면 0 이해도 카드가 각성될 때 가산
  },

  // ── §5 신 풀 ─────────────────────────────────────────""", 'weights ARCANA')
    wr(p, s); print('weights.js: ARCANA 추가')

# ── 3) validate.js ──
p = P('data', 'validate.js'); s = rd(p)
if 'awaken' not in s:
    s = sub(s, "// 7. verified 통계", """// 6-g. 아르카나: 0 이해도 카드는 구조화된 awaken 조건 필수, grid_position 필수
for (const a of arcana) {
  if (!Array.isArray(a.grid_position) || a.grid_position.length !== 2) err(`[arcana] grid_position 없음: ${a.id}`);
  if (a.grasp === 0 && !(a.awaken && a.awaken.type)) err(`[arcana] 0 이해도 카드에 awaken 없음: ${a.id}`);
}

// 7. verified 통계""", 'validate arcana')
    wr(p, s); print('validate.js: 아르카나 규칙 추가')

# ── 4) test.js: S23/S24 ──
p = P('engine', 'test.js'); s = rd(p)
if "sc('S23'" not in s:
    T = r"""
// ── 4-A 추가: 아르카나 ───────────────────────────────────
sc('S23', '아르카나 — 이해도 10은 기존 초보 세트와 동일', () => {
  const r = E.recommendArcana('staff', 'staff_melinoe', 10);
  const ids = r.cards.map((c) => c.id).sort();
  return { rows: r.cards.map((c, i) => ({ id: c.id, rank: i + 1, score: c.grasp, reason: c.tag, warnings: [], badges: [] })),
    extra: `사용 ${r.grasp_used}/${r.grasp_cap} · 각성 ${r.awakened.map((c) => c.name_ko).join(',') || '없음'} · 다음: ${r.next_up.map((c) => c.name_ko).join(', ')}`,
    checks: [
      check('핵심 5장 포함', ['death', 'the_furies', 'persistence', 'the_sorceress', 'the_wayward_son'].every((x) => ids.includes(x)), ids.join(',')),
      check('이해도 초과 없음', r.grasp_used <= 10, String(r.grasp_used)),
      check('0 이해도 카드는 직접 선택 안 함', r.cards.every((c) => c.grasp > 0), 'ok'),
      check('용력·죽음 동시 없음', !(ids.includes('strength') && ids.includes('death')), ids.join(',')),
    ] };
});

sc('S24', '아르카나 — 이해도 20이면 무기별로 달라지고 각성 카드가 붙는다', () => {
  const rs = E.recommendArcana('staff', 'staff_melinoe', 20);
  const rb = E.recommendArcana('blades', 'blades_melinoe', 20);
  const ra = E.recommendArcana('axe', 'axe_melinoe', 20);
  const ids = (r) => r.cards.map((c) => c.id).sort().join(',');
  const anyAwaken = [rs, rb, ra].some((r) => r.awakened.length > 0);
  return { rows: rs.cards.map((c, i) => ({ id: c.id, rank: i + 1, score: c.grasp, reason: c.tag, warnings: [], badges: [] })),
    extra: `지팡이 ${rs.grasp_used}/20 [${rs.cards.map((c) => c.name_ko).join(', ')}] 각성[${rs.awakened.map((c) => c.name_ko)}]\n쌍검 ${rb.grasp_used}/20 [${rb.cards.map((c) => c.name_ko).join(', ')}]\n도끼 ${ra.grasp_used}/20 [${ra.cards.map((c) => c.name_ko).join(', ')}]`,
    checks: [
      check('이해도 20 중 18 이상 사용', rs.grasp_used >= 18 && rb.grasp_used >= 18 && ra.grasp_used >= 18, `${rs.grasp_used}/${rb.grasp_used}/${ra.grasp_used}`),
      check('무기별 세트가 전부 같지는 않음', !(ids(rs) === ids(rb) && ids(rb) === ids(ra)), ids(rs) === ids(rb) ? '지팡이=쌍검' : '다름'),
      check('어느 무기든 각성 카드 1장 이상 (0 이해도 활용)', anyAwaken, [rs, rb, ra].map((r) => r.awakened.length).join('/')),
      check('비추천(priority 0) 카드 없음', [rs, rb, ra].every((r) => r.cards.every((c) => (data.arcana.find((a) => a.id === c.id) || {}).beginner_priority !== 0)), 'ok'),
    ] };
});
"""
    marker = '// ── 실행 ────────────────────────────────────────────────'
    s = sub(s, marker, T + '\n' + marker, 'test marker')
    wr(p, s); print('test.js: S23/S24 추가')
