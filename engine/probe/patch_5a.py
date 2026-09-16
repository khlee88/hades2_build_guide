# -*- coding: utf-8 -*-
"""5단계 엔진 패치 (페이블, 2026-09-16).

5-A 신 선택: 순위 → 절대 등급(필수/좋음/보통/패스) + 역할 태그 + 동급(tie) 묶음.
     등급은 점수 구간이 아니라 이유 기반 — "패스"라고 한 신을 사용자가 실제로 버리므로 근거가 읽혀야 한다.
     범용 신(제우스) 편향은 가중치를 건드리지 않고 표시(등급·동급)로만 처리한다. 시나리오 24개를 흔들지 않기 위해.
5-B 체력(hp_state) 제거: 생존 가점은 "생존 은혜 0개 && (2지역 이상 || 칸 2개 이상)"으로 단순화.
5-D 런 시작: 방향별 주요 신(main_gods) + 첫 기념품(first_keepsake).
시나리오: S14 재설계, S25~S27 추가.
"""
import io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RJ = os.path.join(ROOT, 'engine', 'recommend.js')
WJ = os.path.join(ROOT, 'engine', 'weights.js')
TJ = os.path.join(ROOT, 'engine', 'test.js')

def load(p): return io.open(p, encoding='utf-8').read()
def save(p, s): io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, old, new, n=1):
    c = s.count(old); assert c == n, ('anchor %d != %d: %r' % (c, n, old[:80])); return s.replace(old, new)

# ── weights.js ───────────────────────────────────────────────────────────────
w = load(WJ)
if 'TIE_GAP' not in w:
    w = rep(w, "    KEEPSAKE_MATCH: 1,\n",
"""    KEEPSAKE_MATCH: 1,
    // 5-A (2026-09-16): 등급·동급 표시용. 점수 자체는 바꾸지 않는다
    TIE_GAP: 2,                 // 이 차이 미만이면 같은 군 — 첫 신은 상위 4~5신이 2점 이내라 순위에 변별이 없다
    OK_TOP: 3,                  // 채울 칸도 융합도 없을 때, 상위 은혜 평균이 이 이상이면 '보통', 아니면 '패스'
    MAIN_CORE: [4, 3, 2, 1.5],  // 방향별 '주요 신' 집계: 핵심 칸 선호 순위별
    MAIN_OTHER: [2, 1.5, 1, 0.75],
    MAIN_SUPPORT: [1, 0.75, 0.5, 0.5],
""")
    save(WJ, w); print('weights.js: GOD.TIE_GAP/OK_TOP/MAIN_* 추가')
else:
    print('weights.js: 이미 적용됨')

# ── recommend.js ─────────────────────────────────────────────────────────────
r = load(RJ)
if 'grade_ko' in r:
    print('recommend.js: 이미 적용됨')
else:
    # 5-B 체력 제거
    r = rep(r, "    const survivalOn = state.hp_state === 'low' || ((state.region || 1) >= 2 && !hasSurvival);",
"""    // 5-B (2026-09-16): 체력 입력 제거. 생존 가점은 "생존 은혜가 하나도 없고 빌드가 어느 정도 찼을 때"만
    const survivalOn = !hasSurvival && ((state.region || 1) >= 2 || dv.slotBoonCount >= 2);""")
    r = rep(r, """    if (state.hp_state === 'low') {
      for (const k of ['luckier_tooth', 'ghost_onion']) if (keepsakeById.get(k)) return { id: k, name_ko: nameOf(k), reason: '체력이 낮음 — 생존 우선' };
    }
""", "")
    r = rep(r, "    const state = { weapon, aspect, region: 1, boons: [], hammers: [], gods_seen: [], hp_state: 'mid' };",
               "    const state = { weapon, aspect, region: 1, boons: [], hammers: [], gods_seen: [] };", 2)

    # 5-A 등급·역할
    r = rep(r, """    if (state.keepsake) { const k = keepsakeById.get(state.keepsake); if (k && k.god === godId) { score += W.GOD.KEEPSAKE_MATCH; bd.keepsake = W.GOD.KEEPSAKE_MATCH; } }

    let reason;
    if (partnerDuo) reason = `'${partnerDuo.name_ko}' 마지막 조건을 채울 수 있음`;""",
"""    if (state.keepsake) { const k = keepsakeById.get(state.keepsake); if (k && k.god === godId) { score += W.GOD.KEEPSAKE_MATCH; bd.keepsake = W.GOD.KEEPSAKE_MATCH; } }

    // ── 5-A: 절대 등급. 실제 결정은 "이 문 하나를 갈지 / 석류·재화를 갈지"라 순위(비교)로는 답이 안 된다.
    // 점수 구간이 아니라 이유로 매긴다 — 사용자가 '패스'를 믿고 문을 버리므로 근거가 읽혀야 한다.
    const roles = [];
    let bestFill = null;
    if (main) {
      const better = (x, y) => !y || (x.empty !== y.empty ? x.empty : x.core !== y.core ? x.core : x.rank < y.rank);
      for (const b of pool) {
        if (!b.occupies_slot) continue;
        const prefs = (main.slot_prefs || {})[b.slot] || [];
        const i = prefs.indexOf(b.id);
        if (i < 0) continue;
        const cand = { slot: b.slot, rank: i + 1, core: (main.core_slots || []).includes(b.slot), empty: !dv.slotMap[b.slot] };
        if (better(cand, bestFill)) bestFill = cand;
      }
      const sup = pool.filter((b) => !b.occupies_slot && (main.support_boons || []).includes(b.id)).length;
      if (sup) roles.push(`보조 ${sup}개`);
    }
    const hasAlways = pool.some((b) => (builds.always_take.boons || []).includes(b.id));
    if (bestFill) roles.unshift(`${bestFill.core ? '핵심 ' : ''}${SLOT_KO[bestFill.slot]} ${bestFill.rank}순위${bestFill.empty ? '' : ' (교체)'}`);
    if (partnerDuo) roles.unshift(`융합 파트너 · ${partnerDuo.name_ko}`);
    if (hasAlways) roles.push('항상 이득');
    const poolOver = bd.pool === W.GOD.POOL_NEW_PENALTY;
    if (poolOver) roles.push('풀 밖 신');
    let tier;
    if (partnerDuo || (bestFill && bestFill.empty && bestFill.core && bestFill.rank === 1)) tier = 3;
    else if (bestFill && bestFill.empty && ((bestFill.core && bestFill.rank <= 3) || bestFill.rank === 1)) tier = 2;
    else if (hasAlways) tier = 2;
    else if ((bestFill && bestFill.empty) || roles.some((x) => x.startsWith('보조')) || (topList.length && topList[0].score >= W.GOD.OK_TOP)) tier = 1;
    else tier = 0;
    if (poolOver && !partnerDuo) tier = Math.max(0, tier - 1);   // 3신 베이스 + 기념품 4번째가 정석(dc51882). 풀 밖 신은 한 단계 내린다
    const GRADES = ['pass', 'ok', 'good', 'must'];
    const GRADE_KO = { must: '필수', good: '좋음', ok: '보통', pass: '패스' };
    const grade = GRADES[tier];

    let reason;
    if (grade === 'pass') reason = poolOver ? '풀 밖 신인데 채울 핵심 칸도 융합도 없음 — 석류·재화 쪽이 낫습니다' : '지금 빌드에 맞는 칸이 없음 — 석류·재화 쪽이 낫습니다';
    else if (partnerDuo) reason = `'${partnerDuo.name_ko}' 마지막 조건을 채울 수 있음`;""")
    r = rep(r, "    return { id: godId, score: round(score), reason, warnings, badges, breakdown: bd, _replacing: false };\n  }\n\n  function recommendGods(state, offeredGodIds) {\n    const ctx = directionWeights(state);\n    return ranked((offeredGodIds || []).map((g) => scoreGodEntry(state, g, ctx)));\n  }",
"""    return { id: godId, score: round(score), reason, warnings, badges, breakdown: bd, grade, grade_ko: GRADE_KO[grade], roles, _replacing: false };
  }

  function recommendGods(state, offeredGodIds) {
    const ctx = directionWeights(state);
    const rows = ranked((offeredGodIds || []).map((g) => scoreGodEntry(state, g, ctx)));
    // 5-A: 점수 차 < TIE_GAP이면 같은 군(tie). 첫 신은 상위 4~5신이 2점 이내라 1·2·3위를 매기면 없는 정보를 있는 것처럼 보인다
    let g = 0;
    rows.forEach((x, i) => { if (i > 0 && Number.isFinite(x.score) && Number.isFinite(rows[i - 1].score) && rows[i - 1].score - x.score >= W.GOD.TIE_GAP) g++; x.tie = g; });
    return rows;
  }""")
    # 셀레네/카오스 분기는 두되(UI에서 제외) 등급 필드가 없으면 UI가 깨지므로 채워준다
    r = rep(r, "      return { id: godId, score: round(v), reason: state.hex ? '비술 강화 (별의 길)' : '비술 확보 — 아직 없음', warnings, badges, breakdown: { fixed: v } };",
               "      return { id: godId, score: round(v), reason: state.hex ? '비술 강화 (별의 길)' : '비술 확보 — 아직 없음', warnings, badges, breakdown: { fixed: v }, grade: 'ok', grade_ko: '보통', roles: ['비술'] };")
    r = rep(r, "      return { id: godId, score: round(W.GOD.CHAOS), reason: '저주 내용 확인 후 결정', warnings, badges, breakdown: { fixed: W.GOD.CHAOS } };",
               "      return { id: godId, score: round(W.GOD.CHAOS), reason: '저주 내용 확인 후 결정', warnings, badges, breakdown: { fixed: W.GOD.CHAOS }, grade: 'ok', grade_ko: '보통', roles: ['저주 후 축복'] };")

    # 5-D 주요 신 + 첫 기념품
    r = rep(r, """    const { all } = directionWeights(state);
    return {
      weapon, aspect,
      arcana: arc,""",
"""    const { all } = directionWeights(state);
    // 5-D (2026-09-16): 방향별 '주요 신' — 첫 기념품을 고르는 근거. 실플레이 5런에서 기념품 사용 0회·융합 2개가 나온 직접 원인
    const mainGodsOf = (d) => {
      const acc = new Map();
      const add = (g, v) => { if (!W.NON_POOL_GODS.includes(g)) acc.set(g, (acc.get(g) || 0) + v); };
      for (const [slot, prefs] of Object.entries(d.slot_prefs || {})) {
        const tbl = (d.core_slots || []).includes(slot) ? W.GOD.MAIN_CORE : W.GOD.MAIN_OTHER;
        prefs.forEach((id, i) => { const b = boonById.get(id); if (b) add(b.god, rankVal(tbl, i)); });
      }
      (d.support_boons || []).forEach((id, i) => { const b = boonById.get(id); if (b) add(b.god, rankVal(W.GOD.MAIN_SUPPORT, i)); });
      return [...acc.entries()].sort((a, b) => b[1] - a[1]).slice(0, 3).map(([g, v]) => ({ id: g, name_ko: nameOf(g), v: round(v) }));
    };
    const dirs = all.filter((x) => Number.isFinite(x.F));
    let firstKeepsake = null;
    if (dirs.length) {
      const top = dirs[0].d;
      for (const g of mainGodsOf(top)) {
        const k = keepsakeByGod.get(g.id);
        if (!k || (owned && !owned.includes(k.id))) continue;
        firstKeepsake = { id: k.id, name_ko: k.name_ko, god: g.id, god_ko: g.name_ko, effect: k.effect, giver_ko: k.giver_ko,
          reason: `추천 빌드 '${top.name_ko}'의 주요 신 ${g.name_ko} — 1지역부터 등장 확정` };
        break;
      }
    }
    return {
      weapon, aspect,
      arcana: arc,
      first_keepsake: firstKeepsake,""")
    r = rep(r, """      directions: all.filter((x) => Number.isFinite(x.F)).map((x) => ({
        id: x.d.id, name_ko: x.d.name_ko, difficulty: x.d.difficulty, F: round(x.F), summary: x.d.summary,""",
"""      directions: dirs.map((x) => ({
        id: x.d.id, name_ko: x.d.name_ko, difficulty: x.d.difficulty, F: round(x.F), summary: x.d.summary,
        main_gods: mainGodsOf(x.d),""")
    r = rep(r, "      note: '첫 신이 뜨기 전에는 방향을 고정하지 않습니다.',",
               "      note: '첫 신이 뜨기 전에는 빌드를 고정하지 않습니다. 주요 신의 기념품을 들면 그 빌드가 열립니다.',")
    save(RJ, r); print('recommend.js: 5-A 등급/역할/동급, 5-B 체력 제거, 5-D 주요 신/첫 기념품')

# ── test.js ──────────────────────────────────────────────────────────────────
t = load(TJ)
if "sc('S25'" in t:
    print('test.js: 이미 적용됨'); sys.exit(0)
t = rep(t, "const S = (o) => Object.assign({ region: 1, hp_state: 'mid', boons: [],", "const S = (o) => Object.assign({ region: 1, boons: [],")
t = rep(t, """sc('S14', '생존 우선 — 체력 낮음', () => {
  const st = S({ weapon: 'axe', aspect: 'axe_melinoe', region: 2, hp_state: 'low', boons:""",
"""sc('S14', '생존 우선 — 2지역인데 방어·회복 은혜 0개 (5-B: 체력 입력 제거)', () => {
  const st = S({ weapon: 'axe', aspect: 'axe_melinoe', region: 2, boons:""")
NEW = """

// ── 5-A 신 선택: 등급·동급 (2026-09-16) ─────────────────
sc('S25', '신 1개 go/no-go — 풀 4명 찬 뒤 뜬 아레스는 패스', () => {
  const st = S({ weapon: 'staff', aspect: 'staff_melinoe', region: 2,
    boons: ['hestia_flame_flourish', 'demeter_arctic_ring', 'zeus_heaven_strike', 'apollo_lucid_gain'], gods_seen: ['hestia', 'demeter', 'zeus', 'apollo'] });
  const rows = E.recommendGods(st, ['ares']);
  const r = rows[0];
  return { rows, checks: [
    check('신 1개만 넣어도 결과가 나옴', rows.length === 1, String(rows.length)),
    check("등급 '패스'", r.grade === 'pass', r.grade_ko),
    check("이유에 '석류·재화'", /석류|재화/.test(r.reason), r.reason),
    check("역할에 '풀 밖 신'", r.roles.includes('풀 밖 신'), r.roles.join(',')),
  ] };
});

sc('S26', '신 1개 go/no-go — 융합 마지막 조건이면 필수', () => {
  const st = S({ weapon: 'blades', aspect: 'blades_melinoe', boons: ['hestia_flame_strike', 'hestia_cardio_gain'], gods_seen: ['hestia'] });
  const rows = E.recommendGods(st, ['zeus']);
  const r = rows[0];
  return { rows, checks: [
    check("등급 '필수'", r.grade === 'must', r.grade_ko),
    check("역할에 '융합 파트너'", r.roles.some((x) => x.startsWith('융합 파트너')), r.roles.join(',')),
    check("이유에 '불벼락'", /불벼락/.test(r.reason), r.reason),
  ] };
});

sc('S27', '첫 신은 동급으로 묶인다 — 지팡이', () => {
  const st = S({ weapon: 'staff', aspect: 'staff_melinoe' });
  const rows = E.recommendGods(st, ['zeus', 'hestia', 'poseidon', 'demeter', 'apollo', 'aphrodite', 'hephaestus', 'hera', 'ares']);
  const by = (id) => rows.find((r) => r.id === id);
  return { rows, extra: rows.map((r) => `${r.id}:${r.score}/${r.grade_ko}/군${r.tie}`).join(' '), checks: [
    check('상위 3신이 같은 군', rows[0].tie === rows[1].tie && rows[1].tie === rows[2].tie, rows.slice(0, 3).map((r) => r.tie).join(',')),
    check('맨 아래 신은 다른 군', rows[rows.length - 1].tie > rows[0].tie, String(rows[rows.length - 1].tie)),
    check("헤스티아(핵심 기술 1순위) = 필수", by('hestia').grade === 'must', by('hestia').grade_ko + ' ' + by('hestia').roles.join(',')),
    check("데메테르(핵심 마법 1순위) = 필수", by('demeter').grade === 'must', by('demeter').grade_ko),
    check("제우스(비핵심 공격 1순위) = 좋음, 필수 아님", by('zeus').grade === 'good', by('zeus').grade_ko + ' ' + by('zeus').roles.join(',')),
  ] };
});

sc('S28', '런 시작 — 추천 빌드마다 주요 신, 첫 기념품은 1위 빌드 주요 신의 것', () => {
  const r = E.recommendRunStart('staff', 'staff_melinoe', { graspCap: 10 });
  const d0 = r.directions[0];
  return { rows: r.directions.map((d, i) => ({ id: d.id, rank: i + 1, score: d.F, reason: d.main_gods.map((g) => g.name_ko).join(' > '), warnings: [], badges: [] })),
    extra: `첫 기념품: ${r.first_keepsake && r.first_keepsake.name_ko} (${r.first_keepsake && r.first_keepsake.god_ko})`,
    checks: [
      check('모든 방향에 주요 신 3명', r.directions.every((d) => d.main_gods.length === 3), r.directions.map((d) => d.main_gods.length).join(',')),
      check("기술 월광탄 주요 신 1위 = 헤스티아", d0.main_gods[0].id === 'hestia', d0.main_gods.map((g) => g.id).join('>')),
      check('첫 기념품 = 영원한 불씨(헤스티아)', r.first_keepsake && r.first_keepsake.id === 'everlasting_ember', String(r.first_keepsake && r.first_keepsake.id)),
    ] };
});
"""
t = rep(t, "\n// ── 실행 ────────────────────────────────────────────────", NEW + "\n// ── 실행 ────────────────────────────────────────────────")
save(TJ, t); print('test.js: S14 개정, S25~S28 추가')
