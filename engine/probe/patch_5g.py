# -*- coding: utf-8 -*-
"""5-G 후반 문 선택 (페이블, 2026-09-17). 런6 n=20→21 재현으로 확인된 결함.

E. 조건이 이미 다 찬 융합("뜨기만 하면 되는")을 신 등급이 전혀 안 봤다 — 파트너 판정이 `unmet === 1`만 보고 0은 건너뜀.
   그 융합은 그 두 신의 문에서만 뜬다. 런6 n=20에 S급 2개·A급 2개가 대기 중이었는데 제우스 '보통', 포세이돈 '패스'.
   신 풀이 4명으로 차면 이후 모든 문이 그 4명 중 하나이므로, 후반 문 선택은 거의 전적으로 이 값이다.
A. 정렬이 점수순이라 '필수'가 '패스' 아래에 왔다 → 등급 우선, 같은 등급 안에서 점수순. 동급(tie)도 같은 등급 안에서만.
B. 역할 문구가 찬 칸을 "핵심 기술 4순위 (교체)"로 자랑했다 — 현재 1순위를 4순위로 바꾸면 손해. 은혜 단계는 이미 "나을 게 없음"으로 안다.
   → 찬 칸은 현재보다 순위가 높을 때만 '업그레이드'로 치고, 아니면 역할·등급 어디에도 넣지 않는다.
C. 칸이 차면 '필수/좋음' 경로가 빈 칸 하나만 남아 붕괴 → 전설 진행도(사정권 2/3 = 좋음, 완성 = 필수), 보조는 메인+보험 방향 합산.
D. '패스' 문구가 문이 하나뿐일 때 조언이 안 됨 → "이 문뿐이면 들어가서 은혜를 보고 정한다".
"""
import io, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RJ = os.path.join(ROOT, 'engine', 'recommend.js'); WJ = os.path.join(ROOT, 'engine', 'weights.js'); TJ = os.path.join(ROOT, 'engine', 'test.js')
def load(p): return io.open(p, encoding='utf-8').read()
def save(p, s): io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, old, new, n=1):
    c = s.count(old); assert c == n, ('anchor %d != %d: %r' % (c, n, old[:90])); return s.replace(old, new)

w = load(WJ)
if 'DUO_READY' not in w:
    w = rep(w, "    TIE_GAP: 2,", """    DUO_READY: 8,               // 5-G: 조건이 다 찬 융합이 이 신의 문에서 뜰 수 있음 — 후반 문 선택의 최우선
    DUO_READY_S: 2,             //      그중 S급이면 추가
    LEG_READY: 8,               //      전설 조건 완성 — 마찬가지로 이 신 문에서만 뜸
    TIE_GAP: 2,""")
    save(WJ, w); print('weights.js: DUO_READY/LEG_READY')

r = load(RJ)
if 'readyDuos' in r:
    print('recommend.js: 이미 적용됨')
else:
    # E: 완성 대기 융합 수집
    r = rep(r, """    let partner = 0; let partnerDuo = null; let otherDuo = null;""",
               """    let partner = 0; let partnerDuo = null; let otherDuo = null; const readyDuos = [];""")
    r = rep(r, """    for (const D of openDuos(dv.owned)) {
      const unmet = unmetGroups(D, dv.owned);
      if (unmet.length !== 1) continue;
      // ISSUES [P3] 허수 제거""",
"""    for (const D of openDuos(dv.owned)) {
      const unmet = unmetGroups(D, dv.owned);
      // 5-G E: 조건이 다 찼는데 아직 안 뜬 융합은 그 두 신의 문에서만 나온다. 런6에서 제우스 문에 S·A급이 대기 중인데 '보통'이었다
      if (unmet.length === 0) { if ((D.gods || []).includes(godId)) readyDuos.push(D); continue; }
      if (unmet.length !== 1) continue;
      // ISSUES [P3] 허수 제거""")
    r = rep(r, """    if (partner) { score += partner; bd.duo_partner = partner; }""",
"""    if (partner) { score += partner; bd.duo_partner = partner; }
    const TIER_ORD = { S: 3, A: 2, B: 1 };
    readyDuos.sort((a, b) => (TIER_ORD[b.power_tier] || 0) - (TIER_ORD[a.power_tier] || 0));
    if (readyDuos.length) { const v = W.GOD.DUO_READY + (readyDuos[0].power_tier === 'S' ? W.GOD.DUO_READY_S : 0); score += v; bd.duo_ready = v; }
    // 5-G C: 전설 진행도. 전설도 그 신의 문에서만 뜬다
    const legB = (boonsByGod.get(godId) || []).find((b) => b.slot === 'legendary');
    let legMet = 0, legTotal = 0;
    if (legB && legB.prereq && !dv.owned.has(legB.id)) { const gs = legB.prereq.all || []; legTotal = gs.length; legMet = gs.filter((g) => groupMet(g, dv.owned)).length; }
    const legReady = legTotal > 0 && legMet === legTotal;
    const legClose = legTotal > 0 && !legReady && legMet >= legTotal - 1 && legMet >= 1;
    if (legReady) { score += W.GOD.LEG_READY; bd.leg_ready = W.GOD.LEG_READY; }""")
    # B: bestFill — 찬 칸은 업그레이드일 때만
    r = rep(r, """      for (const b of pool) {
        if (!b.occupies_slot) continue;
        const prefs = (main.slot_prefs || {})[b.slot] || [];
        const i = prefs.indexOf(b.id);
        if (i < 0) continue;
        const cand = { slot: b.slot, rank: i + 1, core: (main.core_slots || []).includes(b.slot), empty: !dv.slotMap[b.slot] };
        if (better(cand, bestFill)) bestFill = cand;
      }
      const sup = pool.filter((b) => !b.occupies_slot && (main.support_boons || []).includes(b.id)).length;""",
"""      for (const b of pool) {
        if (!b.occupies_slot) continue;
        const prefs = (main.slot_prefs || {})[b.slot] || [];
        const i = prefs.indexOf(b.id);
        if (i < 0) continue;
        const cur = dv.slotMap[b.slot];
        // 5-G B: 찬 칸은 현재 은혜보다 선호 순위가 높을 때만 '업그레이드'. 낮으면 역할·등급 어디에도 안 넣는다 (은혜 단계가 "나을 게 없음"으로 판정하는 교체)
        if (cur) { const ci = prefs.indexOf(cur); const curRank = ci < 0 ? 99 : ci + 1; if (!(i + 1 < curRank)) continue; }
        const cand = { slot: b.slot, rank: i + 1, core: (main.core_slots || []).includes(b.slot), empty: !cur, upgrade: !!cur, curName: cur ? nameOf(cur) : null };
        if (better(cand, bestFill)) bestFill = cand;
      }
      // 5-G C: 보조는 메인뿐 아니라 보험 방향까지 — 런6 포세이돈 지하수 분출(보험 보조 2순위)이 0으로 세어져 '패스'가 됐다
      const sup = pool.filter((b) => !b.occupies_slot && active.some((x) => ((x.d.support_boons) || []).includes(b.id))).length;""")
    r = rep(r, """    if (bestFill) roles.unshift(`${bestFill.core ? '핵심 ' : ''}${SLOT_KO[bestFill.slot]} ${bestFill.rank}순위${bestFill.empty ? '' : ' (교체)'}`);
    if (partnerDuo) roles.unshift(`융합 파트너 · ${partnerDuo.name_ko}`);
    else if (otherDuo) roles.unshift(`융합 가능 · ${otherDuo.name_ko}`);""",
"""    if (bestFill) roles.unshift(bestFill.empty ? `${bestFill.core ? '핵심 ' : ''}${SLOT_KO[bestFill.slot]} ${bestFill.rank}순위`
                                                : `${SLOT_KO[bestFill.slot]} 업그레이드 (${bestFill.curName} → ${bestFill.rank}순위)`);
    if (legClose) roles.push(`전설 사정권 ${legMet}/${legTotal}`);
    if (partnerDuo) roles.unshift(`융합 파트너 · ${partnerDuo.name_ko}`);
    else if (otherDuo) roles.unshift(`융합 가능 · ${otherDuo.name_ko}`);
    if (legReady) roles.unshift(`전설 대기 · ${legB.name_ko}`);
    if (readyDuos.length) roles.unshift(`융합 대기 · ${readyDuos[0].name_ko}${readyDuos.length > 1 ? ` 외 ${readyDuos.length - 1}` : ''}`);""")
    r = rep(r, """    let tier;
    if (partnerDuo || (bestFill && bestFill.empty && bestFill.core && bestFill.rank === 1)) tier = 3;
    else if (bestFill && bestFill.empty && ((bestFill.core && bestFill.rank <= 3) || bestFill.rank === 1)) tier = 2;
    else if (hasAlways || otherDuo) tier = 2;""",
"""    let tier;
    if (readyDuos.length || legReady || partnerDuo || (bestFill && bestFill.empty && bestFill.core && bestFill.rank === 1)) tier = 3;
    else if (bestFill && bestFill.empty && ((bestFill.core && bestFill.rank <= 3) || bestFill.rank === 1)) tier = 2;
    else if ((bestFill && bestFill.upgrade) || legClose || hasAlways || otherDuo) tier = 2;""")
    r = rep(r, """    if (poolOver && !partnerDuo) tier = Math.max(0, tier - 1);""",
               """    if (poolOver && !partnerDuo && !readyDuos.length && !legReady) tier = Math.max(0, tier - 1);""")
    # D + E 이유
    r = rep(r, """    if (grade === 'pass') reason = poolOver ? '풀 밖 신인데 채울 핵심 칸도 융합도 없음 — 석류·재화 쪽이 낫습니다' : '지금 빌드에 맞는 칸이 없음 — 석류·재화 쪽이 낫습니다';
    else if (partnerDuo) reason = `'${partnerDuo.name_ko}' 마지막 조건을 채울 수 있음`;""",
"""    if (grade === 'pass') reason = (poolOver ? '풀 밖 신인데 채울 칸도 융합도 없음' : '지금 빌드에 맞는 칸이 없음') + ' — 석류·재화 문이 있으면 그쪽. 이 문뿐이면 들어가서 은혜를 보고 정한다';
    else if (readyDuos.length) reason = `'${readyDuos[0].name_ko}'${readyDuos.length > 1 ? ` 외 ${readyDuos.length - 1}개` : ''} 조건 완성 — 이 문에서 뜰 수 있음`;
    else if (legReady) reason = `전설 '${legB.name_ko}' 조건 완성 — 이 문에서 뜰 수 있음`;
    else if (partnerDuo) reason = `'${partnerDuo.name_ko}' 마지막 조건을 채울 수 있음`;
    else if (legClose && !(bestFill && bestFill.empty && bestFill.core)) reason = `전설 '${legB.name_ko}' ${legMet}/${legTotal} — 이 신 은혜 하나면 사정권`;""")
    # A: 등급 우선 정렬
    r = rep(r, """    const rows = ranked((offeredGodIds || []).map((g) => scoreGodEntry(state, g, ctx)));
    // 5-A: 점수 차 < TIE_GAP이면 같은 군(tie). 첫 신은 상위 4~5신이 2점 이내라 1·2·3위를 매기면 없는 정보를 있는 것처럼 보인다
    let g = 0;
    rows.forEach((x, i) => { if (i > 0 && Number.isFinite(x.score) && Number.isFinite(rows[i - 1].score) && rows[i - 1].score - x.score >= W.GOD.TIE_GAP) g++; x.tie = g; });
    return rows;""",
"""    // 5-G A: 등급 우선, 같은 등급 안에서 점수순. 점수순이면 '필수'(위험 지대 마지막 조건, 3.3점)가 '패스'(3.6점) 아래로 내려갔다
    const TIER_OF = { must: 3, good: 2, ok: 1, pass: 0 };
    const list = (offeredGodIds || []).map((g) => scoreGodEntry(state, g, ctx));
    list.sort((a, b) => ((TIER_OF[b.grade] ?? -1) - (TIER_OF[a.grade] ?? -1)) || compareEntries(a, b));
    const rows = list.map((x, i) => ({ ...x, rank: i + 1 }));
    // 5-A: 같은 등급이고 점수 차 < TIE_GAP이면 같은 군(tie). 등급이 바뀌면 새 군
    let g = 0;
    rows.forEach((x, i) => { if (i > 0 && (x.grade !== rows[i - 1].grade || !(Number.isFinite(x.score) && Number.isFinite(rows[i - 1].score) && rows[i - 1].score - x.score < W.GOD.TIE_GAP))) g++; x.tie = g; });
    return rows;""")
    save(RJ, r); print('recommend.js: 5-G E/A/B/C/D')

t = load(TJ)
if "sc('S29'" in t:
    print('test.js: 이미 적용됨'); sys.exit(0)
# S27 개정: 등급 우선 정렬이므로 상위 2 = 필수(헤스티아·데메테르)이고 같은 군, 제우스(좋음)는 그 뒤
t = rep(t, """    check('상위 3신이 같은 군', rows[0].tie === rows[1].tie && rows[1].tie === rows[2].tie, rows.slice(0, 3).map((r) => r.tie).join(',')),
    check('맨 아래 신은 다른 군', rows[rows.length - 1].tie > rows[0].tie, String(rows[rows.length - 1].tie)),""",
"""    check('상위 2신(필수)이 같은 군', rows[0].grade === 'must' && rows[1].grade === 'must' && rows[0].tie === rows[1].tie, rows.slice(0, 2).map((r) => r.id + ':' + r.grade + '/' + r.tie).join(',')),
    check('맨 아래 신은 다른 군', rows[rows.length - 1].tie > rows[0].tie, String(rows[rows.length - 1].tie)),
    check('등급이 아래로 갈수록 내려가기만 한다 (등급 우선 정렬)', rows.every((r, i) => i === 0 || ({ must: 3, good: 2, ok: 1, pass: 0 })[r.grade] <= ({ must: 3, good: 2, ok: 1, pass: 0 })[rows[i - 1].grade]), rows.map((r) => r.grade).join('>')),""")
NEW = """

// ── 5-G 후반 문 선택 (2026-09-17, 런6 n=20 재현) ────────
const RUN6 = () => S({ weapon: 'staff', aspect: 'staff_melinoe', region: 4,
  boons: ['hestia_flame_flourish', 'demeter_frigid_rush', 'zeus_heaven_strike', 'poseidon_tidal_ring', 'demeter_steady_growth', 'hermes_nimble_limbs', 'hestia_cardio_gain', 'hermes_paid_dues'],
  hammers: ['staff_shimmering_moonshot', 'staff_dual_moonshot'], gods_seen: ['hestia', 'demeter', 'zeus', 'poseidon', 'hermes'] });

sc('S29', '조건이 다 찬 융합은 그 신의 문에서 뜬다 — 제우스·포세이돈이 필수', () => {
  const rows = E.recommendGods(RUN6(), ['demeter', 'hermes', 'artemis', 'hestia', 'zeus', 'poseidon']);
  const by = (id) => rows.find((r) => r.id === id);
  return { rows, checks: [
    check("제우스 = 필수 (불벼락 S·감전 급류 A 대기)", by('zeus').grade === 'must', by('zeus').grade_ko + ' ' + by('zeus').roles.join(',')),
    check("제우스 역할에 '융합 대기 · 불벼락'", by('zeus').roles.some((x) => /융합 대기 · 불벼락/.test(x)), by('zeus').roles.join(',')),
    check("제우스 이유에 '이 문에서 뜰 수 있음'", /이 문에서 뜰 수 있음/.test(by('zeus').reason), by('zeus').reason),
    check("포세이돈 = 필수 (뜨거운 증기 S 대기) — 원래 '패스'였음", by('poseidon').grade === 'must', by('poseidon').grade_ko + ' ' + by('poseidon').roles.join(',')),
    check("헤스티아 = 필수 (불벼락·뜨거운 증기 대기)", by('hestia').grade === 'must', by('hestia').grade_ko),
    check('필수 3신이 헤르메스(좋음)보다 위', rows.findIndex((r) => r.id === 'hermes') > 2, rows.map((r) => r.id + ':' + r.grade_ko).join(' ')),
  ] };
});

sc('S30', '역할 문구는 현재 칸과 비교한다 — 손해 교체는 안 보이고, 이득 교체는 업그레이드', () => {
  const rows = E.recommendGods(RUN6(), ['zeus', 'aphrodite']);
  const by = (id) => rows.find((r) => r.id === id);
  return { rows, checks: [
    check("제우스 역할에 '핵심 기술 2순위' 없음 (현재 화염 기예 1순위 → 손해)", !by('zeus').roles.some((x) => /기술/.test(x)), by('zeus').roles.join(',')),
    check("아프로디테 역할에 '마법 업그레이드 (물결 고리 → 2순위)'", by('aphrodite').roles.some((x) => /마법 업그레이드 \\(물결 고리 → 2순위\\)/.test(x)), by('aphrodite').roles.join(',')),
  ] };
});

sc('S31', '전설 진행도 — 2/3이면 사정권(좋음), 3/3이면 대기(필수)', () => {
  const close = S({ weapon: 'staff', aspect: 'staff_melinoe', region: 3, boons: ['hestia_flame_flourish', 'hestia_pyro_technique', 'zeus_heaven_strike', 'demeter_arctic_ring', 'zeus_ionic_gain', 'apollo_blinding_rush'], gods_seen: ['hestia', 'zeus', 'demeter', 'apollo'] });
  const r1 = E.recommendGods(close, ['hestia'])[0];
  const ready = S({ weapon: 'staff', aspect: 'staff_melinoe', region: 3, boons: ['hestia_flame_flourish', 'hestia_pyro_technique', 'hestia_controlled_burn', 'zeus_heaven_strike', 'demeter_arctic_ring', 'zeus_ionic_gain', 'apollo_blinding_rush'], gods_seen: ['hestia', 'zeus', 'demeter', 'apollo'] });
  const r2 = E.recommendGods(ready, ['hestia'])[0];
  return { rows: [r1], rows2: [r2], checks: [
    check("2/3: 역할에 '전설 사정권 2/3'", r1.roles.some((x) => /전설 사정권 2\\/3/.test(x)), r1.roles.join(',')),
    check('2/3: 등급 좋음 이상', r1.grade === 'good' || r1.grade === 'must', r1.grade_ko),
    check("3/3: 역할에 '전설 대기 · 불길 장벽'", r2.roles.some((x) => /전설 대기 · 불길 장벽/.test(x)), r2.roles.join(',')),
    check('3/3: 등급 필수', r2.grade === 'must', r2.grade_ko),
  ] };
});

sc('S32', '패스 문구 — 문이 하나뿐일 때의 조언 포함', () => {
  const r = E.recommendGods(S({ weapon: 'staff', aspect: 'staff_melinoe', boons: ['zeus_heaven_strike'], gods_seen: ['zeus'] }), ['dionysus'])[0];
  return { rows: [r], checks: [
    check("등급 '패스'", r.grade === 'pass', r.grade_ko),
    check("이유에 '이 문뿐이면'", /이 문뿐이면/.test(r.reason), r.reason),
  ] };
});
"""
t = rep(t, "\n// ── 실행 ────────────────────────────────────────────────", NEW + "\n// ── 실행 ────────────────────────────────────────────────")
save(TJ, t); print('test.js: S27 개정, S29~S32 추가')
