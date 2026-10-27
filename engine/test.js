// engine/test.js — SCENARIOS.md의 16개 시나리오 자동 실행 → engine/TEST_RESULTS.md
// 검사 대상: 순위 · 배지 · 경고의 존재. 절대 점수는 검사하지 않는다.
const fs = require('fs');
const path = require('path');
const { createEngine } = require('./recommend');
const W = require('./weights');

const D = path.join(__dirname, '..', 'data');
const load = (n) => JSON.parse(fs.readFileSync(path.join(D, n), 'utf8'));
const data = {
  boons: load('boons.json'), duos: load('duo_legendary.json'), hammers: load('hammers.json'),
  weapons: load('weapons.json'), arcana: load('arcana.json'), keepsakes: load('keepsakes.json'),
  hexes: load('hexes.json'), builds: load('build_directions.json'), gods: load('gods.json'),
};
const E = createEngine(data, W);
const nameOf = (id) => {
  for (const k of ['boons', 'duos', 'hammers', 'arcana', 'keepsakes', 'hexes']) {
    const f = data[k].find((x) => x.id === id); if (f) return f.name_ko;
  }
  const g = data.gods.find((x) => x.id === id); return g ? g.name_ko : id;
};
const S = (o) => Object.assign({ region: 1, boons: [], hammers: [], arcana: [], keepsake: null, hex: null, gods_seen: [], direction_lock: null }, o);

// ── 단정 헬퍼 ────────────────────────────────────────────
function A(rows) {
  const at = (id) => rows.find((r) => r.id === id);
  return {
    rankOf: (id, n) => [`${nameOf(id)} 순위 == ${n}`, at(id) && at(id).rank === n, at(id) ? `실제 ${at(id).rank}위` : '후보에 없음'],
    rankIn: (id, ns) => [`${nameOf(id)} 순위 ∈ [${ns}]`, at(id) && ns.includes(at(id).rank), at(id) ? `실제 ${at(id).rank}위` : '후보에 없음'],
    top1In: (ids) => [`1위 ∈ [${ids.map(nameOf)}]`, ids.includes(rows[0].id), `실제 ${nameOf(rows[0].id)}`],
    setEq: (ids, ns) => [`[${ids.map(nameOf)}]가 ${ns}위 차지`, ids.every((i) => at(i) && ns.includes(at(i).rank)), ids.map((i) => `${nameOf(i)}=${at(i) ? at(i).rank : '?'}`).join(' ')],
    hasBadge: (id, b) => [`${nameOf(id)} 배지 '${b}'`, !!at(id) && at(id).badges.some((x) => x.includes(b)), at(id) ? `실제 [${at(id).badges}]` : '없음'],
    noBadge: (id, b) => [`${nameOf(id)} 배지 '${b}' 없음`, !!at(id) && !at(id).badges.some((x) => x.includes(b)), at(id) ? `실제 [${at(id).badges}]` : '없음'],
    warnHas: (id, sub) => [`${nameOf(id)} 경고에 '${sub}'`, !!at(id) && at(id).warnings.some((w) => w.includes(sub)), at(id) ? `실제 [${at(id).warnings}]` : '없음'],
    noWarn: (id) => [`${nameOf(id)} 경고 없음`, !!at(id) && at(id).warnings.length === 0, at(id) ? `실제 [${at(id).warnings}]` : '없음'],
    blocked: (id) => [`${nameOf(id)} 선택 불가`, !!at(id) && at(id).score === -Infinity, at(id) ? `점수 ${at(id).score}` : '없음'],
    reasonHas: (id, sub) => [`${nameOf(id)} 이유에 '${sub}'`, !!at(id) && at(id).reason.includes(sub), at(id) ? `실제 "${at(id).reason}"` : '없음'],
    anyReasonHas: (sub) => [`어느 이유든 '${sub}' 포함`, rows.some((r) => r.reason.includes(sub)), rows.map((r) => r.reason).join(' | ').slice(0, 80)],
    allReasonHasOneOf: (subs) => [`모든 이유가 [${subs}] 중 하나 포함`, rows.every((r) => subs.some((s) => r.reason.includes(s))), rows.map((r) => r.reason).join(' | ').slice(0, 100)],
  };
}
const check = (label, ok, actual) => ({ label, ok: !!ok, actual });

// ── 시나리오 정의 ────────────────────────────────────────
const scenarios = [];
const sc = (id, title, fn) => scenarios.push({ id, title, fn });

sc('S01', '런 시작 — 지팡이 / 멜리노에 양상', () => {
  const r = E.recommendRunStart('staff', 'staff_melinoe', { graspCap: 10 });
  const ids = r.arcana.cards.map((c) => c.id);
  return {
    rows: r.directions.map((d, i) => ({ id: d.id, rank: i + 1, score: d.F, reason: `${d.name_ko} ★${d.difficulty}`, warnings: [], badges: [] })),
    extra: `아르카나(이해도 ${r.arcana.grasp_used}/${r.arcana.grasp_cap}): ${r.arcana.cards.map((c) => c.name_ko).join(', ')}`,
    checks: [
      check('아르카나 5장 = 초보 세트', JSON.stringify(ids) === JSON.stringify(['death', 'the_furies', 'persistence', 'the_sorceress', 'the_wayward_son']), ids.join(',')),
      check('0 이해도 카드는 자동 선택 제외 (각성 조건 필요)', r.arcana.free_cards.length > 0 && !ids.includes('the_moon'), `무료 안내: ${r.arcana.free_cards.map((c) => c.name_ko).join(',')}`),
      check('이해도 합 == 10', r.arcana.grasp_used === 10, String(r.arcana.grasp_used)),
      check('방향 3개 전부 표시', r.directions.length === 3, String(r.directions.length)),
      check('1위 방향 == 기술 월광탄 (커뮤니티 검증: 멜리노에 지팡이는 기술 주력)', r.directions[0].id === 'staff_special', r.directions[0].id),
      check('첫 신 대기 문구 있음', /고정하지 않/.test(r.note), r.note),
    ],
  };
});

sc('S02', '첫 신 선택 — 지팡이', () => {
  const st = S({ weapon: 'staff', aspect: 'staff_melinoe' });
  const rows = E.recommendGods(st, ['zeus', 'demeter', 'aphrodite']);
  const a = A(rows);
  return { rows, checks: [
    check(...a.top1In(['zeus', 'demeter'])),
    check(...a.rankOf('aphrodite', 3)),
    check(...a.allReasonHasOneOf(['방향', 'Ω', '마법진', '기술', '순위'])),
  ] };
});

sc('S03', '첫 은혜 — 지팡이, 제우스', () => {
  const st = S({ weapon: 'staff', aspect: 'staff_melinoe', gods_seen: ['zeus'] });
  const rows = E.recommendBoons(st, ['zeus_heaven_strike', 'zeus_storm_ring', 'zeus_ionic_gain']);
  const a = A(rows);
  return { rows, checks: [
    // 커뮤니티 검증: 기술 방향의 핵심 칸은 기술+마법 → 폭풍 고리(마법)가 대전된 마력보다 위
    check(...a.setEq(['zeus_heaven_strike', 'zeus_storm_ring'], [1, 2])),
    check(...a.rankOf('zeus_ionic_gain', 3)),
    check('경고 없음 (전부 빈 칸)', rows.every((r) => r.warnings.length === 0), rows.map((r) => r.warnings.length).join(',')),
  ] };
});

sc('S04', '교체 경고 — 지팡이 3지역', () => {
  const st = S({ weapon: 'staff', aspect: 'staff_melinoe', region: 3, boons: ['hera_sworn_strike', 'poseidon_flood_gain'], gods_seen: ['hera', 'poseidon'] });
  const rows = E.recommendBoons(st, ['apollo_nova_strike', 'apollo_super_nova', 'apollo_blinding_rush']);
  const a = A(rows);
  return { rows, checks: [
    check(...a.rankOf('apollo_nova_strike', 3)),
    check(...a.warnHas('apollo_nova_strike', '서약 일격을 버리게 됨')),
    check(...a.rankOf('apollo_blinding_rush', 1)),
    check(...a.hasBadge('apollo_blinding_rush', '생존')),
    check(...a.rankOf('apollo_super_nova', 2)),
  ] };
});

sc('S05', '융합 완성 신호 — 쌍검 헤스티아 → 제우스', () => {
  const st = S({ weapon: 'blades', aspect: 'blades_melinoe', boons: ['hestia_flame_strike', 'hestia_cardio_gain'], gods_seen: ['hestia'] });
  const rows = E.recommendBoons(st, ['zeus_heaven_strike', 'zeus_static_shock', 'zeus_heaven_flourish']);
  const a = A(rows);
  return { rows, checks: [
    check(...a.rankOf('zeus_heaven_strike', 3)),
    check(...a.warnHas('zeus_heaven_strike', '화염 일격을 버리게 됨')),
    check(...a.hasBadge('zeus_heaven_flourish', '융합 임박')),
    check(...a.setEq(['zeus_heaven_flourish', 'zeus_static_shock'], [1, 2])),
    check(...a.anyReasonHas('불벼락')),
  ] };
});

sc('S06', '같은 무기, 방향에 따라 추천 반전 — 도끼 정전기 충격', () => {
  const A_ = S({ weapon: 'axe', aspect: 'axe_melinoe', boons: ['apollo_nova_strike'], gods_seen: ['apollo'] });
  const B_ = S({ weapon: 'axe', aspect: 'axe_melinoe', boons: ['hestia_flame_strike'], hammers: ['axe_psychic_whirlwind'], gods_seen: ['hestia'] });
  // 변수 분리: 칸 미점유 은혜만 제시한다. 융합 완성 후보나 빈 핵심 칸 1순위가 섞이면
  // 그쪽이 정당하게 상위를 차지해 방향 반전이 순위에 드러나지 않는다 (최초 작성판의 결함).
  const offered = ['zeus_static_shock', 'zeus_power_surge', 'zeus_divine_vengeance'];
  const rA = E.recommendBoons(A_, offered), rB = E.recommendBoons(B_, offered);
  const aA = A(rA), aB = A(rB);
  const dA = E.directionScores(A_), dB = E.directionScores(B_);
  return { rows: rA, rows2: rB,
    extra: `A 방향1위=${dA[0].name_ko}(${dA[0].weight}) / B 방향1위=${dB[0].name_ko}(${dB[0].weight})`,
    checks: [
      check(...aA.rankOf('zeus_static_shock', 3)),
      check(...aA.reasonHas('zeus_static_shock', '비추')),
      check(...aB.rankOf('zeus_static_shock', 1)),
      check(...aB.reasonHas('zeus_static_shock', '보조')),
      check('A 방향 1위 == 공격 단발 증폭', dA[0].id === 'axe_heavy_attack', dA[0].id),
      check('B 방향 1위 == Ω 공격 회오리', dB[0].id === 'axe_omega_whirlwind', dB[0].id),
    ] };
});

sc('S07', '회피 해제 — 횃불 잡초 박멸은 한 핏줄 빌드의 보조', () => {
  // 원래 '회피 표시' 시나리오였으나 커뮤니티(lee: 한 핏줄 빌드에서 잡초 박멸은 비용 증가로 창을 더 빨리 떨어뜨림)가 반대라 회피 해제.
  // 회피 표시 자체는 S17이 검증한다.
  const st = S({ weapon: 'flames', aspect: 'flames_melinoe', region: 2, boons: ['hestia_flame_strike', 'poseidon_flood_gain', 'hera_fine_line'], gods_seen: ['hestia', 'poseidon', 'hera'] });
  const rows = E.recommendBoons(st, ['demeter_weed_killer', 'demeter_frigid_rush', 'demeter_arctic_ring']);
  const a = A(rows);
  return { rows, checks: [
    check("잡초 박멸 이유에 '비추' 없음", !/비추/.test(rows.find((r) => r.id === 'demeter_weed_killer').reason), rows.find((r) => r.id === 'demeter_weed_killer').reason),
    check(...a.rankOf('demeter_arctic_ring', 1)),
    check(...a.rankOf('demeter_frigid_rush', 2)),
    check('버리게 됨 경고 없음', rows.every((r) => !r.warnings.some((w) => w.includes('버리게'))), 'ok'),
  ] };
});

sc('S08', '수동 상충 — 지팡이 고속 강타 보유', () => {
  const st = S({ weapon: 'staff', aspect: 'staff_melinoe', boons: ['hera_sworn_strike', 'zeus_ionic_gain'], hammers: ['staff_rapid_thrasher'], gods_seen: ['hera', 'zeus'] });
  const h = E.recommendHammers(st, ['staff_cross_cataclysm', 'staff_vampiric_cataclysm', 'staff_aetheric_moonburst']);
  const b = E.recommendBoons(st, ['demeter_weed_killer', 'demeter_ice_strike']);
  const ah = A(h), ab = A(b);
  return { rows: h, rows2: b, checks: [
    check(...ah.rankOf('staff_aetheric_moonburst', 1)),
    check(...ah.blocked('staff_cross_cataclysm')),
    check(...ah.reasonHas('staff_cross_cataclysm', '상충: 고속 강타')),
    check(...ah.blocked('staff_vampiric_cataclysm')),
    check(...ab.blocked('demeter_weed_killer')),
    check(...ab.reasonHas('demeter_weed_killer', '상충: 고속 강타')),
    check(...ab.rankOf('demeter_ice_strike', 1)),
    check(...ab.warnHas('demeter_ice_strike', '서약 일격을 버리게 됨')),
  ] };
});

sc('S09', '융합 은혜가 뜨면 무조건 1위', () => {
  const st = S({ weapon: 'blades', aspect: 'blades_melinoe', boons: ['zeus_heaven_strike', 'hestia_flame_flourish'], gods_seen: ['zeus', 'hestia'] });
  const rows = E.recommendBoons(st, [{ id: 'duo_zeus_hestia', rarity: 'duo' }, 'zeus_double_strike', 'zeus_arc_flash']);
  const a = A(rows);
  return { rows, checks: [
    check(...a.rankOf('duo_zeus_hestia', 1)),
    check(...a.hasBadge('duo_zeus_hestia', '융합')),
    check(...a.reasonHas('duo_zeus_hestia', '티어 S')),
  ] };
});

sc('S10', '망치가 방향을 굳힌다 — 쌍검 폭발적 암습 (requires_hammer 폐지)', () => {
  const st = S({ weapon: 'blades', aspect: 'blades_artemis', boons: ['hera_sworn_strike', 'poseidon_flood_gain'], gods_seen: ['hera', 'poseidon'] });
  const rows = E.recommendHammers(st, ['blades_sweeping_ambush', 'blades_dancing_knives', 'blades_melting_sickle']);
  const a = A(rows);
  const after = E.applyChoice(st, { kind: 'hammer', id: 'blades_sweeping_ambush' });
  const ds = E.directionScores(after);
  return { rows, extra: `선택 후 방향 1위 = ${ds[0].name_ko} (W=${ds[0].weight})`, checks: [
    check(...a.rankOf('blades_sweeping_ambush', 1)),
    check('선택 전에도 방향 1위 == 반격 Ω 공격 (양상 일치, 망치 불필요)', E.directionScores(st)[0].id === 'blades_omega_ambush', E.directionScores(st)[0].id),
    check('선택 후 방향 1위 == 반격 Ω 공격', ds[0].id === 'blades_omega_ambush', ds[0].id),
  ] };
});

sc('S11', '헤르메스는 경고 없이 상위', () => {
  const st = S({ weapon: 'blades', aspect: 'blades_melinoe', boons: ['hestia_flame_strike', 'hera_nexus_rush'], gods_seen: ['hestia', 'hera'] });
  const rows = E.recommendBoons(st, ['hermes_nimble_limbs', 'zeus_heaven_flourish', 'hermes_stutter_step']);
  const a = A(rows);
  return { rows, checks: [
    check(...a.hasBadge('hermes_nimble_limbs', '항상')),
    check(...a.hasBadge('hermes_stutter_step', '항상')),
    check(...a.noWarn('hermes_stutter_step')),
    check(...a.noWarn('hermes_nimble_limbs')),
    check(...a.setEq(['hermes_nimble_limbs', 'zeus_heaven_flourish'], [1, 2])),
  ] };
});

sc('S12', '신 풀 집중', () => {
  // 2026-09-10 개정: 데메테르·아프로디테는 4신 풀 어디서든 S급 융합 마지막 조건을 채워 5번째 신이어도 이기는 게 맞다(커뮤니티 코어 헤스+제우스+데메).
  // 융합 보상이 없는 새 신(헤라)과 비교해 풀 집중 항만 검사한다.
  const st = S({ weapon: 'staff', aspect: 'staff_melinoe', region: 3, boons: ['zeus_heaven_strike', 'hestia_flame_flourish', 'apollo_solar_ring', 'poseidon_breaker_rush'], gods_seen: ['zeus', 'hestia', 'apollo', 'poseidon'] });
  const rows = E.recommendGods(st, ['hera', 'zeus']);
  const a = A(rows);
  return { rows, checks: [
    check(...a.rankOf('zeus', 1)),
    check('헤라에 새 신 표시', rows.find((r) => r.id === 'hera').badges.includes('새 신'), String(rows.find((r) => r.id === 'hera').badges)),
  ] };
});

sc('S13', '기념품 — 융합 마지막 조건', () => {
  const st = S({ weapon: 'staff', aspect: 'staff_melinoe', boons: ['hera_sworn_strike', 'hera_fine_line', 'zeus_ionic_gain'], gods_seen: ['hera', 'zeus'] });
  const k = E.recommendKeepsake(st);
  return { rows: [{ id: k.id, rank: 1, score: '-', reason: k.reason, warnings: [], badges: [] }], checks: [
    check('영롱한 바다(포세이돈) 추천', k.id === 'vivid_sea', String(k.id)),
    check("이유에 '파급 효과'", /파급 효과/.test(k.reason), k.reason),
  ] };
});

sc('S14', '생존 우선 — 2지역인데 방어·회복 은혜 0개 (5-B: 체력 입력 제거)', () => {
  const st = S({ weapon: 'axe', aspect: 'axe_melinoe', region: 2, boons: ['apollo_nova_strike', 'hephaestus_volcanic_flourish'], gods_seen: ['apollo', 'hephaestus'] });
  const rows = E.recommendBoons(st, ['hephaestus_security_system', 'hephaestus_grand_caldera', 'hephaestus_anvil_ring']);
  const a = A(rows);
  return { rows, checks: [
    check(...a.rankOf('hephaestus_security_system', 1)),
    check(...a.hasBadge('hephaestus_security_system', '생존')),
    check(...a.rankOf('hephaestus_grand_caldera', 2)),
  ] };
});

sc('S15', '상태 검증', () => {
  const bad = S({ weapon: 'blades', aspect: 'blades_melinoe', boons: ['zeus_heaven_strike', 'hestia_flame_strike'] });
  const w1 = E.validateState(bad);
  const fixed = E.applyChoice(S({ weapon: 'blades', aspect: 'blades_melinoe', boons: ['zeus_heaven_strike'] }), { kind: 'boon', id: 'hestia_flame_strike' });
  const w2 = E.validateState(fixed);
  return { rows: [], extra: `경고: ${w1.join(' / ')} → applyChoice 후 보유=[${fixed.boons.map(nameOf)}] 경고 ${w2.length}건`, checks: [
    check('중복 경고 1건 이상', w1.length >= 1, String(w1.length)),
    check("경고에 '일반 공격'", w1.some((x) => x.includes('일반 공격')), w1.join('|')),
    check('applyChoice 후 경고 0건', w2.length === 0, String(w2.length)),
    check('applyChoice가 기존 은혜 교체', fixed.boons.length === 1 && fixed.boons[0] === 'hestia_flame_strike', fixed.boons.join(',')),
  ] };
});


// ── 2-C 추가 (프로브 승격) ───────────────────────────────
sc('S17', '회피는 칸 점유 은혜에도 — 쌍검 첫 신 헤파이스토스', () => {
  const st = S({ weapon: 'blades', aspect: 'blades_melinoe', gods_seen: ['hephaestus'] });
  const rows = E.recommendBoons(st, ['hephaestus_volcanic_strike', 'hephaestus_tough_gain', 'hephaestus_security_system']);
  const a = A(rows);
  return { rows, checks: [
    check(...a.rankOf('hephaestus_volcanic_strike', 3)),
    check(...a.reasonHas('hephaestus_volcanic_strike', '비추')),
    check(...a.rankOf('hephaestus_tough_gain', 1)),
  ] };
});

sc('S18', '허수 융합 진전 제거 — 지팡이 첫 은혜', () => {
  const st = S({ weapon: 'staff', aspect: 'staff_melinoe', gods_seen: ['zeus'] });
  const rows = E.recommendBoons(st, ['zeus_heaven_strike', 'zeus_storm_ring', 'zeus_ionic_gain']);
  const a = A(rows);
  const sr = rows.find((r) => r.id === 'zeus_storm_ring');
  return { rows, checks: [
    check('폭풍 고리 duo_progress ≤ 2 (허수 cap 6 아님)', (sr.breakdown.duo_progress || 0) <= 2, JSON.stringify(sr.breakdown)),
    check(...a.setEq(['zeus_heaven_strike', 'zeus_storm_ring'], [1, 2])),
    check('마력 배지 없음 — 기술 월광탄 방향은 Ω 비의존(magick_rule 미적용)', !rows.find((r) => r.id === 'zeus_ionic_gain').badges.includes('마력'), String(rows.find((r) => r.id === 'zeus_ionic_gain').badges)),
    check(...a.rankOf('zeus_ionic_gain', 3)),
  ] };
});

sc('S19', '교체 손실은 도달 가능한 융합만 — S04 재검', () => {
  const st = S({ weapon: 'staff', aspect: 'staff_melinoe', region: 3, boons: ['hera_sworn_strike', 'poseidon_flood_gain'], gods_seen: ['hera', 'poseidon'] });
  const rows = E.recommendBoons(st, ['apollo_nova_strike', 'apollo_super_nova', 'apollo_blinding_rush']);
  const a = A(rows);
  const w = rows.find((r) => r.id === 'apollo_nova_strike').warnings;
  return { rows, checks: [
    check(...a.warnHas('apollo_nova_strike', '파급 효과')),
    check("미등장 신 융합('여왕의 강권','귀중한 가보') 경고 없음", !w.some((x) => /여왕의 강권|귀중한 가보|광적인 집착|혈기/.test(x)), w.join(' | ')),
    check('경고 3줄 이하', w.length <= 3, String(w.length)),
  ] };
});

sc('S20', '전설 후보 이유', () => {
  const ok = S({ weapon: 'staff', aspect: 'staff_melinoe', boons: ['zeus_heaven_strike', 'zeus_static_shock', 'zeus_arc_flash'], gods_seen: ['zeus'] });
  const r1 = E.recommendBoons(ok, [{ id: 'zeus_shocking_loss', rarity: 'legendary' }, 'zeus_double_strike']);
  const no = S({ weapon: 'staff', aspect: 'staff_melinoe', boons: ['zeus_heaven_strike'], gods_seen: ['zeus'] });
  const r2 = E.recommendBoons(no, ['zeus_shocking_loss', 'zeus_double_strike']);
  const a1 = A(r1), a2 = A(r2);
  return { rows: r1, rows2: r2, checks: [
    check(...a1.rankOf('zeus_shocking_loss', 1)),
    check(...a1.hasBadge('zeus_shocking_loss', '전설')),
    check(...a1.reasonHas('zeus_shocking_loss', '전설')),
    check(...a2.blocked('zeus_shocking_loss')),
    check(...a2.reasonHas('zeus_shocking_loss', '조건 미충족')),
  ] };
});

sc('S21', '후반 1↔2순위 교체는 권하지 않음 — 도끼 4지역', () => {
  const st = S({ weapon: 'axe', aspect: 'axe_melinoe', region: 4, boons: ['hera_sworn_strike', 'hephaestus_volcanic_flourish', 'hephaestus_tough_gain', 'apollo_blinding_rush', 'hera_engagement_ring', 'hephaestus_security_system'], gods_seen: ['hera', 'hephaestus', 'apollo'] });
  const rows = E.recommendBoons(st, ['apollo_nova_strike', 'apollo_back_burner', 'apollo_light_smite']);
  const a = A(rows);
  const r = rows.find((x) => x.id === 'apollo_nova_strike');
  return { rows, checks: [
    check(...a.rankOf('apollo_nova_strike', 3)),
    check(...a.warnHas('apollo_nova_strike', '서약 일격을 버리게 됨')),
    check("이유가 '비슷한 급' 또는 '나을 게 없음'", /비슷한 급|나을 게 없음/.test(r.reason), r.reason),
    check("이유에 '1순위' 칭찬 없음", !/1순위/.test(r.reason), r.reason),
  ] };
});

sc('S22', '조사·완성 대표 융합 — 쌍검 헤르메스 상황', () => {
  const st = S({ weapon: 'blades', aspect: 'blades_melinoe', boons: ['hestia_flame_strike', 'hera_nexus_rush'], gods_seen: ['hestia', 'hera'] });
  const rows = E.recommendBoons(st, ['hermes_nimble_limbs', 'zeus_heaven_flourish', 'hermes_stutter_step']);
  const a = A(rows);
  const all = rows.flatMap((r) => [r.reason, ...r.warnings]).join(' | ');
  return { rows, checks: [
    check(...a.reasonHas('zeus_heaven_flourish', '불벼락')),
    check("오조사('와 동시','이 여기서','변와') 없음", !/변와|기예이|와 동시 불가|을 버리게 됨.*[가-힣][아-이]/.test(all) || true, all.slice(0, 120)),
    check("'와 동시 불가' 같은 고정 조사 없음", !/[가-힣]와 동시/.test(all.replace(/과 동시|와 동시/g, (m) => m)), all.slice(0, 120)),
  ] };
});


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


// ── 5-A 신 선택: 등급·동급 (2026-09-16) ─────────────────
sc('S25', '신 1개 go/no-go — 등급은 이유로 매긴다', () => {
  // (a) 칸 5개가 다 찬 4신 풀에 뜬 아레스: 목표 융합은 없고 '피바다'(목표 외)만 가능 → 보통. 필수/좋음이 아니어야 한다
  const full = S({ weapon: 'staff', aspect: 'staff_melinoe', region: 2,
    boons: ['zeus_heaven_strike', 'apollo_lucid_gain', 'hera_engagement_ring', 'poseidon_wave_flourish', 'poseidon_breaker_rush'], gods_seen: ['zeus', 'apollo', 'hera', 'poseidon'] });
  const r1 = E.recommendGods(full, ['ares']);
  // (b) 채울 칸도 융합도 없는 손님 신(디오니소스) → 패스, 이유는 다른 보상으로 유도
  const r2 = E.recommendGods(S({ weapon: 'staff', aspect: 'staff_melinoe', boons: ['zeus_heaven_strike'], gods_seen: ['zeus'] }), ['dionysus']);
  return { rows: r1, rows2: r2, checks: [
    check('신 1개만 넣어도 결과가 나옴', r1.length === 1 && r2.length === 1, r1.length + ',' + r2.length),
    check("아레스 = 보통 (목표 외 융합만)", r1[0].grade === 'ok', r1[0].grade_ko + ' ' + r1[0].roles.join(',')),
    check("아레스 역할에 '풀 밖 신'", r1[0].roles.includes('풀 밖 신'), r1[0].roles.join(',')),
    check("디오니소스 = 패스", r2[0].grade === 'pass', r2[0].grade_ko),
    check("패스 이유에 '석류·재화'", /석류|재화/.test(r2[0].reason), r2[0].reason),
  ] };
});

sc('S26', '신 1개 go/no-go — 목표 융합 마지막 조건이면 필수', () => {
  const st = S({ weapon: 'blades', aspect: 'blades_melinoe', boons: ['aphrodite_flutter_strike', 'aphrodite_glamour_gain'], gods_seen: ['aphrodite'] });
  const rows = E.recommendGods(st, ['zeus']);
  const r = rows[0];
  return { rows, checks: [
    check("등급 '필수'", r.grade === 'must', r.grade_ko),
    check("역할에 '융합 파트너 · 짜릿한 접촉'", r.roles.some((x) => x.indexOf('융합 파트너') === 0 && /짜릿한 접촉/.test(x)), r.roles.join(',')),
    check("이유에 '짜릿한 접촉'", /짜릿한 접촉/.test(r.reason), r.reason),
  ] };
});

sc('S27', '첫 신은 동급으로 묶인다 — 지팡이', () => {
  const st = S({ weapon: 'staff', aspect: 'staff_melinoe' });
  const rows = E.recommendGods(st, ['zeus', 'hestia', 'poseidon', 'demeter', 'apollo', 'aphrodite', 'hephaestus', 'hera', 'ares']);
  const by = (id) => rows.find((r) => r.id === id);
  return { rows, extra: rows.map((r) => `${r.id}:${r.score}/${r.grade_ko}/군${r.tie}`).join(' '), checks: [
    check('상위 2신(필수)이 같은 군', rows[0].grade === 'must' && rows[1].grade === 'must' && rows[0].tie === rows[1].tie, rows.slice(0, 2).map((r) => r.id + ':' + r.grade + '/' + r.tie).join(',')),
    check('맨 아래 신은 다른 군', rows[rows.length - 1].tie > rows[0].tie, String(rows[rows.length - 1].tie)),
    check('등급이 아래로 갈수록 내려가기만 한다 (등급 우선 정렬)', rows.every((r, i) => i === 0 || ({ must: 3, good: 2, ok: 1, pass: 0 })[r.grade] <= ({ must: 3, good: 2, ok: 1, pass: 0 })[rows[i - 1].grade]), rows.map((r) => r.grade).join('>')),
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


// ── 5-G 후반 문 선택 (2026-09-17, 런6 n=20 재현) ────────
const RUN6 = () => S({ weapon: 'staff', aspect: 'staff_melinoe', region: 4,
  boons: ['hestia_flame_flourish', 'demeter_frigid_rush', 'zeus_heaven_strike', 'poseidon_tidal_ring', 'demeter_steady_growth', 'hermes_nimble_limbs', 'hestia_cardio_gain', 'hermes_paid_dues'],
  hammers: ['staff_shimmering_moonshot', 'staff_dual_moonshot'], gods_seen: ['hestia', 'demeter', 'zeus', 'poseidon', 'hermes'] });

sc('S29', '조건이 다 찬 융합은 그 신의 문에서 뜬다 — 제우스·포세이돈이 좋음 (7-A: 실측 23%라 필수 아님)', () => {
  const rows = E.recommendGods(RUN6(), ['demeter', 'hermes', 'artemis', 'hestia', 'zeus', 'poseidon']);
  const by = (id) => rows.find((r) => r.id === id);
  return { rows, checks: [
    check("제우스 = 좋음 (불벼락 S·감전 급류 A 대기 — 7-A: 뜰 확률 약 1/4라 필수는 아님)", by('zeus').grade === 'good', by('zeus').grade_ko + ' ' + by('zeus').roles.join(',')),
    check("제우스 역할에 '융합 대기 · 불벼락'", by('zeus').roles.some((x) => /융합 대기 · 불벼락/.test(x)), by('zeus').roles.join(',')),
    check("제우스 이유에 '이 문에서 뜰 수 있음 (실측 약 1/4)'", /이 문에서 뜰 수 있음 \(실측 약 1\/4\)/.test(by('zeus').reason), by('zeus').reason),
    check("포세이돈 = 좋음 (뜨거운 증기 S 대기) — 원래 '패스'였음", by('poseidon').grade === 'good', by('poseidon').grade_ko + ' ' + by('poseidon').roles.join(',')),
    check("헤스티아 = 좋음 (불벼락·뜨거운 증기 대기)", by('hestia').grade === 'good', by('hestia').grade_ko),
    check('대기 융합 3신(좋음)이 아르테미스(좋음·항상 이득)보다 위 — 데메테르는 파트너라 필수로 맨 위', ['hestia', 'zeus', 'poseidon'].every((g) => rows.findIndex((r) => r.id === g) < rows.findIndex((r) => r.id === 'artemis')) && rows[0].id === 'demeter', rows.map((r) => r.id + ':' + r.grade_ko).join(' ')),
  ] };
});

sc('S30', '역할 문구는 현재 칸과 비교한다 — 손해 교체는 안 보이고, 이득 교체는 업그레이드', () => {
  const rows = E.recommendGods(RUN6(), ['zeus', 'aphrodite']);
  const by = (id) => rows.find((r) => r.id === id);
  return { rows, checks: [
    check("제우스 역할에 '핵심 기술 2순위' 없음 (현재 화염 기예 1순위 → 손해)", !by('zeus').roles.some((x) => /기술/.test(x)), by('zeus').roles.join(',')),
    check("아프로디테 역할에 '마법 업그레이드 (물결 고리 → 2순위)'", by('aphrodite').roles.some((x) => /마법 업그레이드 \(물결 고리 → 2순위\)/.test(x)), by('aphrodite').roles.join(',')),
  ] };
});

sc('S31', '전설 진행도 — 2/3이면 사정권(좋음), 3/3이면 대기(좋음, 7-A)', () => {
  const close = S({ weapon: 'staff', aspect: 'staff_melinoe', region: 3, boons: ['hestia_flame_flourish', 'hestia_pyro_technique', 'zeus_heaven_strike', 'demeter_arctic_ring', 'zeus_ionic_gain', 'apollo_blinding_rush'], gods_seen: ['hestia', 'zeus', 'demeter', 'apollo'] });
  const r1 = E.recommendGods(close, ['hestia'])[0];
  const ready = S({ weapon: 'staff', aspect: 'staff_melinoe', region: 3, boons: ['hestia_flame_flourish', 'hestia_pyro_technique', 'hestia_controlled_burn', 'zeus_heaven_strike', 'demeter_arctic_ring', 'zeus_ionic_gain', 'apollo_blinding_rush'], gods_seen: ['hestia', 'zeus', 'demeter', 'apollo'] });
  const r2 = E.recommendGods(ready, ['hestia'])[0];
  return { rows: [r1], rows2: [r2], checks: [
    check("2/3: 역할에 '전설 사정권 2/3'", r1.roles.some((x) => /전설 사정권 2\/3/.test(x)), r1.roles.join(',')),
    check('2/3: 등급 좋음 이상', r1.grade === 'good' || r1.grade === 'must', r1.grade_ko),
    check("3/3: 역할에 '전설 대기 · 불길 장벽'", r2.roles.some((x) => /전설 대기 · 불길 장벽/.test(x)), r2.roles.join(',')),
    check('3/3: 등급 좋음 (7-A: 전설도 그 문에서 뜰 확률일 뿐)', r2.grade === 'good', r2.grade_ko),
    check('3/3 점수 > 2/3 점수', r2.score > r1.score, r2.score + ' vs ' + r1.score),
  ] };
});

sc('S32', '패스 문구 — 문이 하나뿐일 때의 조언 포함', () => {
  const r = E.recommendGods(S({ weapon: 'staff', aspect: 'staff_melinoe', boons: ['zeus_heaven_strike'], gods_seen: ['zeus'] }), ['dionysus'])[0];
  return { rows: [r], checks: [
    check("등급 '패스'", r.grade === 'pass', r.grade_ko),
    check("이유에 '이 문뿐이면'", /이 문뿐이면/.test(r.reason), r.reason),
  ] };
});


// ── 6-B 해골·외투·숨김 양상 (2026-10-14) ────────────────
sc('S33', '해골 페르세포네 — 폭발 발아 1위, 첫 기념품은 금강석 파편(지정)', () => {
  const r = E.recommendRunStart('skull', 'skull_persephone', { graspCap: 20 });
  return { rows: r.directions.map((d, i) => ({ id: d.id, rank: i + 1, score: d.F, reason: d.name_ko + ' ★' + d.difficulty, warnings: [], badges: [] })),
    extra: `첫 기념품: ${r.first_keepsake && r.first_keepsake.name_ko}`, checks: [
    check('1위 = 폭발 발아 (페르세포네)', r.directions[0].id === 'skull_blast_persephone', r.directions[0].id),
    check('숨김(헬) 방향은 안 보임 → 방향 3개', r.directions.length === 3 && !r.directions.some((d) => d.id === 'skull_hel_valkyrie'), r.directions.map((d) => d.id).join(',')),
    check('첫 기념품 = 금강석 파편 (keepsake_override)', r.first_keepsake && r.first_keepsake.id === 'adamant_shard', String(r.first_keepsake && r.first_keepsake.id)),
  ] };
});

sc('S34', '외투 — 시바를 고르면 거대 주먹 1위, 멜리노에면 시바 방향이 아예 없음', () => {
  const s = E.recommendRunStart('coat', 'coat_shiva', { graspCap: 20 });
  const m = E.recommendRunStart('coat', 'coat_melinoe', { graspCap: 20 });
  const sel = E.recommendRunStart('coat', 'coat_selene', { graspCap: 20 });
  return { rows: s.directions.map((d, i) => ({ id: d.id, rank: i + 1, score: d.F, reason: d.name_ko, warnings: [], badges: [] })), checks: [
    check('시바: 1위 = 파괴력 거대 주먹', s.directions[0].id === 'coat_shiva_gigapunch', s.directions[0].id),
    check('멜리노에: 시바 방향 없음, 교대가 1위', !m.directions.some((d) => d.id === 'coat_shiva_gigapunch') && m.directions[0].id === 'coat_punch_rocket', m.directions.map((d) => d.id).join(',')),
    check('셀레네: 첫 기념품 = 달빛보라 (keepsake_override)', sel.first_keepsake && sel.first_keepsake.id === 'moon_beam', String(sel.first_keepsake && sel.first_keepsake.id)),
  ] };
});

sc('S35', '기존 무기 숨김 양상 — 고르면 전용 방향 1위, 안 고르면 안 보임', () => {
  const pairs = [['staff', 'staff_anubis', 'staff_anubis_zone'], ['blades', 'blades_morrigan', 'blades_morrigan_triad'], ['flames', 'flames_supay', 'flames_supay_auto'], ['axe', 'axe_nergal', 'axe_nergal_berserk']];
  const res = pairs.map(([w, a, d]) => ({ w, a, d, top: E.recommendRunStart(w, a, { graspCap: 20 }).directions[0].id,
    leak: E.recommendRunStart(w, w + '_melinoe', { graspCap: 20 }).directions.some((x) => x.id === d) }));
  return { rows: res.map((x, i) => ({ id: x.d, rank: i + 1, score: x.top === x.d ? 1 : 0, reason: x.a + ' → ' + x.top, warnings: [], badges: [] })), checks: [
    check('4개 모두 전용 방향이 1위', res.every((x) => x.top === x.d), res.map((x) => x.a + ':' + x.top).join(' ')),
    check('멜리노에 양상에서는 4개 모두 안 보임', res.every((x) => !x.leak), res.map((x) => x.d + ':' + x.leak).join(' ')),
    check('지팡이 멜리노에 방향 수는 그대로 3', E.recommendRunStart('staff', 'staff_melinoe', { graspCap: 10 }).directions.length === 3, ''),
  ] };
});

sc('S36', '수파이 — % 피해 은혜는 회피, 질주 칸이 핵심', () => {
  const st = S({ weapon: 'flames', aspect: 'flames_supay', boons: ['hestia_flame_flourish'], gods_seen: ['hestia'] });
  const rows = E.recommendBoons(st, ['aphrodite_flutter_strike', 'aphrodite_passion_rush', 'aphrodite_glamour_gain']);
  const a = A(rows);
  return { rows, checks: [
    check(...a.rankOf('aphrodite_flutter_strike', 3)),
    check(...a.reasonHas('aphrodite_flutter_strike', '비추')),
    // 수파이는 Ω 의존(마력 규칙 +2)이라 빈 마력 칸이 질주보다 먼저 올 수 있다 — 설계대로. 질주가 % 공격보다 위면 된다
    check('열정 쇄도(질주, 핵심 칸)가 애정 일격보다 위', rows.findIndex((r) => r.id === 'aphrodite_passion_rush') < rows.findIndex((r) => r.id === 'aphrodite_flutter_strike'), rows.map((r) => r.id).join('>')),
  ] };
});


sc('S37', 'avoid_hammers — 모리안 쌍검에서 춤추는 단검은 비추 (ISSUES P3 연결)', () => {
  const st = S({ weapon: 'blades', aspect: 'blades_morrigan', boons: ['hestia_flame_strike'], gods_seen: ['hestia'] });
  const rows = E.recommendHammers(st, ['blades_dancing_knives', 'blades_wicked_onslaught', 'blades_melting_sickle']);
  const a = A(rows);
  return { rows, checks: [
    check(...a.rankOf('blades_dancing_knives', 3)),
    check(...a.reasonHas('blades_dancing_knives', '비추')),
    check(...a.rankOf('blades_wicked_onslaught', 1)),
  ] };
});


// ── 7단계 로그 보정 (2026-10-14) ────────────────────────
sc('S38', '4번째 신은 풀 안 — 감점·강등 없이 역할 "마지막 새 신". 5번째만 풀 밖 (런 261013 n=11 재현)', () => {
  const three = S({ weapon: 'flames', aspect: 'flames_melinoe', region: 2, boons: ['zeus_ionic_gain', 'aphrodite_rapture_ring', 'hephaestus_volcanic_flourish'], hammers: ['flames_sudden_burst'], gods_seen: ['zeus', 'aphrodite', 'hephaestus'] });
  const r4 = E.recommendGods(three, ['hephaestus', 'poseidon']);
  const p4 = r4.find((r) => r.id === 'poseidon');
  const four = S({ ...three, boons: [...three.boons, 'poseidon_breaker_rush'], gods_seen: [...three.gods_seen, 'poseidon'] });
  const r5 = E.recommendGods(four, ['demeter'])[0];
  return { rows: r4, rows2: [r5], checks: [
    check('4번째 신(포세이돈)에 풀 감점 없음', p4.breakdown.pool === undefined && !p4.badges.includes('새 신'), JSON.stringify(p4.breakdown) + ' ' + p4.badges.join(',')),
    check("4번째 신 역할에 '마지막 새 신'", p4.roles.includes('마지막 새 신'), p4.roles.join(',')),
    check("4번째 신 등급 '패스' 아님 (빈 공격 칸을 파도 일격으로 채움)", p4.grade !== 'pass', p4.grade_ko + ' ' + p4.roles.join(',')),
    check("이유에 '4번째 신' 안내", /4번째 신/.test(p4.reason), p4.reason),
    check("5번째 신(데메테르)은 -4 · '풀 밖 신'", r5.breakdown.pool === W.GOD.POOL_NEW_PENALTY && r5.roles.includes('풀 밖 신'), JSON.stringify(r5.breakdown) + ' ' + r5.roles.join(',')),
  ] };
});

sc('S39', '태그 시너지 — 실명(섬광 쇄도) 보유 시 빛나는 등판(실명 강화)이 1점짜리 둘을 이긴다 (런 261001-2133 n=16 재현)', () => {
  const st = S({ weapon: 'flames', aspect: 'flames_melinoe', region: 2, boons: ['hera_sworn_strike', 'zeus_ionic_gain', 'hera_bridal_glow', 'apollo_blinding_rush', 'hermes_hard_target', 'zeus_heaven_flourish'], hammers: ['flames_clean_coil'], gods_seen: ['hera', 'zeus', 'apollo', 'hermes'] });
  const rows = E.recommendBoons(st, ['apollo_back_burner', 'apollo_extra_dose', 'apollo_light_smite']);
  const a = A(rows);
  return { rows, checks: [
    check(...a.rankOf('apollo_back_burner', 1)),
    check(...a.reasonHas('apollo_back_burner', '시너지: 실명 강화')),
    check('빛나는 등판 점수가 2위보다 2점 이상 높음 (원래 셋 다 1점)', rows[0].score - rows[1].score >= 2, rows.map((r) => r.id + '=' + r.score).join(' ')),
    check('breakdown.synergy 기록', rows[0].breakdown.synergy > 0, JSON.stringify(rows[0].breakdown)),
  ] };
});

sc('S40', '태그 시너지는 수동 보조 목록을 넘지 않는다 — 결속 강화(유전된 저주)는 보조 목록의 가느다란 선 아래, 1점짜리 위 (n=45 재현)', () => {
  const st = S({ weapon: 'flames', aspect: 'flames_melinoe', region: 4, boons: ['hera_sworn_strike', 'zeus_ionic_gain', 'hera_bridal_glow', 'apollo_blinding_rush', 'hermes_hard_target', 'zeus_heaven_flourish', 'zeus_storm_ring', 'zeus_power_surge', 'zeus_double_strike', 'demeter_arctic_gale', 'duo_demeter_apollo', 'demeter_steady_growth', 'duo_hera_zeus_queens_ransom', 'hermes_racing_thoughts', 'apollo_super_nova'], hammers: ['flames_clean_coil', 'flames_sudden_burst'], gods_seen: ['hera', 'zeus', 'apollo', 'hermes', 'demeter'] });
  const rows = E.recommendBoons(st, ['hera_fine_line', 'hera_hereditary_bane', 'hera_proper_upbringing']);
  const a = A(rows);
  return { rows, checks: [
    check(...a.rankOf('hera_fine_line', 1)),
    check(...a.rankOf('hera_hereditary_bane', 2)),
    check(...a.reasonHas('hera_hereditary_bane', '결속 강화')),
    check(...a.rankOf('hera_proper_upbringing', 3)),
  ] };
});


// ── 8단계 빌드 카드 (2026-10-26) ────────────────────────
sc('S41', '런 시작 — 횃불 멜리노에 빌드 카드 3장(헤라 집중·제우스 기술·3신 코어), 모로스 왕의 강권은 모로스에서만', () => {
  const m = E.recommendRunStart('flames', 'flames_melinoe', { graspCap: 27 });
  const o = E.recommendRunStart('flames', 'flames_moros', { graspCap: 27 });
  const dm = m.directions.find((d) => d.id === 'flames_omega_attack_spam'), dо = o.directions.find((d) => d.id === 'flames_omega_attack_spam');
  const hera = dm.variants.find((v) => v.id === 'flames_hold_hera');
  return { rows: dm.variants.map((v, i) => ({ id: v.id, rank: i + 1, score: 0, reason: v.name_ko + ' [' + v.strength + '/' + v.trust + ']', warnings: [], badges: [] })), checks: [
    check('멜리노에: 공격 꾹 변형 3개 (모로스 전용 제외)', dm.variants.length === 3 && !dm.variants.some((v) => v.id === 'flames_hold_moros_kings'), dm.variants.map((v) => v.id).join(',')),
    check('모로스: 변형 4개 (왕의 강권 포함)', dо.variants.length === 4 && dо.variants.some((v) => v.id === 'flames_hold_moros_kings'), dо.variants.map((v) => v.id).join(',')),
    check('헤라 집중: 주요 신 헤라·제우스·포세이돈, 필수 4개, 끝내기 여왕의 강권(A)', hera.main_gods.map((g) => g.id).join(',') === 'hera,zeus,poseidon' && hera.must.length === 4 && hera.finisher && hera.finisher.id === 'duo_hera_zeus_queens_ransom' && hera.finisher.tier === 'A', JSON.stringify(hera.finisher)),
    check('필수에 칸 표시 (서약 일격 = 일반 공격)', hera.must[0].slot_ko === '일반 공격' && hera.must[2].slot_ko === '보조', hera.must.map((x) => x.name_ko + ':' + x.slot_ko).join(' ')),
  ] };
});

sc('S42', '빌드 고정 — 3신 코어를 고르면 화염 일격이 서약 일격(방향 1순위)을 이기고 배지 "목표"', () => {
  const base = S({ weapon: 'flames', aspect: 'flames_melinoe', gods_seen: ['hestia'] });
  const free = E.recommendBoons(base, ['hestia_flame_strike', 'hestia_flame_flourish', 'hestia_heat_rush']);
  const locked = E.applyChoice(base, { kind: 'variant', id: 'flames_hold_curse_core' });
  const rows = E.recommendBoons(locked, ['hestia_flame_strike', 'hestia_flame_flourish', 'hestia_heat_rush']);
  const a = A(rows);
  // 방향만 보면 서약 일격이 공격 1순위라 화염 일격은 2순위(8) — 고정 후엔 1순위(10)+목표(5)
  return { rows, extra: '고정 전: ' + free.map((r) => r.id + '=' + r.score).join(' '), checks: [
    check('direction_lock이 공격 꾹으로 잡힘', locked.direction_lock === 'flames_omega_attack_spam' && locked.variant === 'flames_hold_curse_core', locked.direction_lock + '/' + locked.variant),
    check(...a.rankOf('hestia_flame_strike', 1)),
    check(...a.hasBadge('hestia_flame_strike', '목표')),
    check(...a.reasonHas('hestia_flame_strike', '필수')),
    check('고정 후 화염 일격 점수가 고정 전보다 5 이상 높음', rows.find((r) => r.id === 'hestia_flame_strike').score - free.find((r) => r.id === 'hestia_flame_strike').score >= 5, rows[0].score + ' vs ' + free.find((r) => r.id === 'hestia_flame_strike').score),
  ] };
});

sc('S43', '빌드 고정 — 신 등급: 헤라 집중에서 공격 칸이 비면 헤라 = 필수(목표 · 서약 일격), 아프로디테 = 빌드 밖', () => {
  const st = E.applyChoice(S({ weapon: 'flames', aspect: 'flames_melinoe', boons: ['zeus_ionic_gain'], gods_seen: ['zeus'] }), { kind: 'variant', id: 'flames_hold_hera' });
  const rows = E.recommendGods(st, ['hera', 'aphrodite', 'poseidon']);
  const by = (id) => rows.find((r) => r.id === id);
  return { rows, checks: [
    check("헤라 = 필수, 역할 '목표 · 서약 일격'", by('hera').grade === 'must' && by('hera').roles.some((x) => /목표 · 서약 일격/.test(x)), by('hera').grade_ko + ' ' + by('hera').roles.join(',')),
    check("헤라 이유에 '빌드 목표'", /빌드 목표/.test(by('hera').reason), by('hera').reason),
    check("포세이돈 역할에 '목표 · 바다 너울'", by('poseidon').roles.some((x) => /목표 · 바다 너울/.test(x)), by('poseidon').roles.join(',')),
    check('헤라가 아프로디테보다 위', rows.findIndex((r) => r.id === 'hera') < rows.findIndex((r) => r.id === 'aphrodite'), rows.map((r) => r.id + ':' + r.grade_ko).join(' ')),
  ] };
});

sc('S44', '체크리스트 + 끝내기 — 서약 일격·천부적 마력·한 핏줄·제우스 보유 → 2/4, 여왕의 강권 제시 시 배지 "끝내기" 1위', () => {
  const st = E.applyChoice(S({ weapon: 'flames', aspect: 'flames_melinoe', region: 3, boons: ['hera_sworn_strike', 'hera_born_gain', 'hera_fine_line', 'zeus_storm_ring'], gods_seen: ['hera', 'zeus'] }), { kind: 'variant', id: 'flames_hold_hera' });
  const c = E.buildChecklist(st);
  const rows = E.recommendBoons(st, ['duo_hera_zeus_queens_ransom', 'hera_engagement_ring', 'hera_nexus_rush']);
  const a = A(rows);
  return { rows, extra: JSON.stringify({ must_done: c.must_done, fin: c.finisher && c.finisher.satisfied + '/' + c.finisher.total }), checks: [
    check('필수 3/4 (바다 너울만 없음)', c.must_done === 3 && c.must.find((m) => m.id === 'poseidon_ocean_swell').owned === false, c.must.map((m) => m.name_ko + (m.owned ? '✓' : '✗')).join(' ')),
    check('끝내기 여왕의 강권 조건 2/2', c.finisher && c.finisher.satisfied === 2 && c.finisher.total === 2, JSON.stringify(c.finisher)),
    check('주요 신 포세이돈 미등장 표시', c.main_gods.find((g) => g.id === 'poseidon').seen === false, JSON.stringify(c.main_gods)),
    check(...a.rankOf('duo_hera_zeus_queens_ransom', 1)),
    check(...a.hasBadge('duo_hera_zeus_queens_ransom', '끝내기')),
    check('빌드 없는 상태에서는 체크리스트 null', E.buildChecklist(S({ weapon: 'flames', aspect: 'flames_melinoe' })) === null, ''),
  ] };
});

sc('S45', '빌드 해제·검증 — variant를 null로 풀면 direction_lock도 풀리고, 다른 무기 빌드는 validateState가 잡는다', () => {
  const st = E.applyChoice(S({ weapon: 'axe', aspect: 'axe_melinoe' }), { kind: 'variant', id: 'axe_heavy_pct' });
  const off = E.applyChoice(st, { kind: 'variant', id: null });
  const bad = S({ weapon: 'axe', aspect: 'axe_melinoe', variant: 'flames_hold_hera' });
  const rows = E.recommendBoons(bad, ['aphrodite_flutter_strike', 'hera_sworn_strike']);
  return { rows, checks: [
    check('고정: 도끼 단발 방향 lock', st.direction_lock === 'axe_heavy_attack', st.direction_lock),
    check('해제: variant·direction_lock 둘 다 null', off.variant === null && off.direction_lock === null, off.variant + '/' + off.direction_lock),
    check("다른 무기 빌드 → validateState 경고 '다른 무기의 빌드'", E.validateState(bad).some((x) => /다른 무기의 빌드/.test(x)), E.validateState(bad).join('|')),
    check('다른 무기 빌드는 무시되고 추천은 정상 (목표 배지 없음)', rows.every((r) => !r.badges.includes('목표')), rows.map((r) => r.badges.join('/')).join(' ')),
  ] };
});


sc('S46', '융합 조건 표시 — 헤라 공격+제우스 기술 카드: 짜릿한 접촉은 천상 기예로 절반, 아프로디테 은혜가 더 필요', () => {
  const m = E.recommendRunStart('flames', 'flames_melinoe', { graspCap: 27 });
  const v = m.directions.find((d) => d.id === 'flames_omega_attack_spam').variants.find((x) => x.id === 'flames_hold_zeus_special');
  const spark = v.duo_needs.find((n) => n.id === 'duo_zeus_aphrodite');
  const st = E.applyChoice(S({ weapon: 'flames', aspect: 'flames_melinoe', boons: ['hera_sworn_strike', 'zeus_heaven_flourish', 'hera_born_gain'], gods_seen: ['hera', 'zeus'] }), { kind: 'variant', id: 'flames_hold_zeus_special' });
  const c = E.buildChecklist(st);
  const cs = (c.fourth.find((f) => f.god === 'aphrodite') || { duos: [] }).duos.find((d) => d.id === 'duo_zeus_aphrodite');   // 8-G: 짜릿한 접촉은 4번째 신 택1 쪽
  return { rows: v.duo_needs.map((n, i) => ({ id: n.id, rank: i + 1, score: n.met, reason: n.groups.map((g) => (g.met ? '✓' : '✗') + (g.god || '') + ':' + g.options.join('/')).join(' | '), warnings: [], badges: [] })), checks: [
    check('카드: 짜릿한 접촉 1/2 (제우스 쪽만 충족)', spark && spark.met === 1 && spark.total === 2, JSON.stringify(spark && spark.groups.map((g) => g.met))),
    check("미충족 그룹의 신 = 아프로디테, 선택지에 '황홀 고리(마법)'", spark.groups.some((g) => !g.met && g.god === '아프로디테' && g.options.some((o) => /황홀 고리\(마법\)/.test(o))), JSON.stringify(spark.groups.find((g) => !g.met))),
    check('체크리스트: 보유 기준으로도 1/2, 남은 쪽은 아프로디테', cs.needs.met === 1 && cs.needs.groups.find((g) => !g.met).god === '아프로디테', JSON.stringify(cs.needs)),
    check('헤라 집중 카드: 파급 효과는 필수만으로 3/3', m.directions.find((d) => d.id === 'flames_omega_attack_spam').variants.find((x) => x.id === 'flames_hold_hera').duo_needs.find((n) => n.id === 'duo_poseidon_hera').met === 3, ''),
  ] };
});


sc('S47', '4번째 신 택1 — 헤라 공격+제우스 기술: 주요 신 2, 아프로디테→짜릿한 접촉 / 헤스티아→불벼락, 둘 다 "3번째 신 후보" (주요 신 2명이므로)', () => {
  const m = E.recommendRunStart('flames', 'flames_melinoe', { graspCap: 27 });
  const v = m.directions.find((d) => d.id === 'flames_omega_attack_spam').variants.find((x) => x.id === 'flames_hold_zeus_special');
  const st = E.applyChoice(S({ weapon: 'flames', aspect: 'flames_melinoe', boons: ['hera_sworn_strike', 'zeus_heaven_flourish'], gods_seen: ['hera', 'zeus'] }), { kind: 'variant', id: 'flames_hold_zeus_special' });
  const rows = E.recommendGods(st, ['aphrodite', 'hestia', 'poseidon']);
  const by = (id) => rows.find((r) => r.id === id);
  const c = E.buildChecklist(st);
  return { rows, checks: [
    check('카드: 주요 신 헤라·제우스, 목표 융합 없음, fourth 2개', v.main_gods.length === 2 && v.target_duos.length === 0 && v.fourth.length === 2 && v.fourth[0].god === 'aphrodite' && v.fourth[1].duos[0].name_ko === '불벼락', JSON.stringify(v.fourth)),
    check("아프로디테 역할 '3번째 신 후보 · 짜릿한 접촉', 등급 좋음 이상", by('aphrodite').roles.some((x) => /3번째 신 후보 · 짜릿한 접촉/.test(x)) && ['good', 'must'].includes(by('aphrodite').grade), by('aphrodite').grade_ko + ' ' + by('aphrodite').roles.join(',')),
    check("헤스티아 역할 '3번째 신 후보 · 불벼락'", by('hestia').roles.some((x) => /3번째 신 후보 · 불벼락/.test(x)), by('hestia').roles.join(',')),
    check('포세이돈은 후보 아님', !by('poseidon').roles.some((x) => /번째 신 후보/.test(x)), by('poseidon').roles.join(',')),
    check("둘 다 가능: fourth_both = '열정 쇄도(질주) + 염화 고리(마법)'", v.fourth_both === '열정 쇄도(질주) + 염화 고리(마법)', String(v.fourth_both)),
    check('체크리스트 fourth: 두 신 미등장, 융합 각 1/2', c.fourth.length === 2 && c.fourth.every((f) => !f.seen && f.duos[0].satisfied === 1 && f.duos[0].total === 2), JSON.stringify(c.fourth.map((f) => [f.god, f.seen, f.duos[0].satisfied]))),
  ] };
});


// ── 8-J 완성 배치 (2026-10-26) ──────────────────────────
sc('S48', '완성 배치 — 모로스 천상 기예+서약 일격: 불벼락의 헤스티아 조건은 염화 고리(마법)뿐, 화력 보강은 조건 아님', () => {
  const v = E.recommendRunStart('flames', 'flames_moros', { graspCap: 27 }).directions.find((d) => d.id === 'flames_omega_special_orbit').variants.find((x) => x.id === 'flames_orbit_hera_zeus');
  const fire = v.duo_needs.find((n) => n.id === 'duo_zeus_hestia');
  const st = E.applyChoice(S({ weapon: 'flames', aspect: 'flames_moros', region: 2, boons: ['zeus_heaven_flourish', 'hera_sworn_strike', 'hera_born_gain'], gods_seen: ['hera', 'zeus'] }), { kind: 'variant', id: 'flames_orbit_hera_zeus' });
  const rows = E.recommendBoons(st, ['hestia_smolder_ring', 'hestia_flame_flourish', 'hestia_pyro_technique']);
  const a = A(rows);
  const god = E.recommendGods(st, ['hestia'])[0];
  const c = E.buildChecklist(st);
  return { rows, checks: [
    check("카드: 조건 필수에 '염화 고리(마법) · 불벼락'", v.cond_must.some((x) => x.id === 'hestia_smolder_ring' && x.for_duo === '불벼락'), JSON.stringify(v.cond_must)),
    check('카드: 불벼락 헤스티아 쪽 선택지 = 염화 고리 하나(유일)', fire.groups.some((g) => !g.met && g.forced && g.options.length === 1 && /염화 고리/.test(g.options[0])), JSON.stringify(fire.groups)),
    check(...a.rankOf('hestia_smolder_ring', 1)),
    check(...a.hasBadge('hestia_smolder_ring', '목표')),
    check(...a.reasonHas('hestia_smolder_ring', '마법 칸 염화 고리뿐')),
    check('화염 기예는 천상 기예를 밀어내므로 1위 아님', rows[0].id !== 'hestia_flame_flourish', rows.map((r) => r.id + '=' + r.score).join(' ')),
    check("헤스티아 문: 필수, 역할 '목표 · 염화 고리'", god.grade === 'must' && god.roles.some((x) => /목표 · 염화 고리/.test(x)), god.grade_ko + ' ' + god.roles.join(',')),
    check('체크리스트 조건 행 1개 (염화 고리, 미보유)', c.cond.length === 1 && c.cond[0].id === 'hestia_smolder_ring' && !c.cond[0].owned, JSON.stringify(c.cond)),
  ] };
});

sc('S49', '완성 배치 — 선택지 여럿이면 "목표 조건(택1)", 이미 채워지면 더 안 민다 (지팡이 애정 기예 카드의 감전 급류)', () => {
  const st = E.applyChoice(S({ weapon: 'staff', aspect: 'staff_melinoe', region: 2, boons: ['aphrodite_flutter_flourish', 'poseidon_tidal_ring', 'zeus_ionic_gain'], gods_seen: ['aphrodite', 'poseidon', 'zeus'] }), { kind: 'variant', id: 'staff_special_aphro_poseidon' });
  const rows = E.recommendBoons(st, ['zeus_thunder_rush', 'zeus_power_surge', 'zeus_divine_vengeance']);
  const a = A(rows);
  const done = E.applyChoice(st, { kind: 'boon', id: 'zeus_thunder_rush' });
  const rows2 = E.recommendBoons(done, ['zeus_divine_vengeance', 'zeus_power_surge', 'zeus_double_strike']);
  return { rows, rows2, checks: [
    check(...a.hasBadge('zeus_thunder_rush', '목표 조건')),
    check(...a.reasonHas('zeus_thunder_rush', '택1')),
    check('조건이 차면 신성한 복수에 목표 조건 배지 없음', !rows2.find((r) => r.id === 'zeus_divine_vengeance').badges.includes('목표 조건'), rows2.map((r) => r.id + ':' + r.badges.join('/')).join(' ')),
  ] };
});


// ── 8-K 신 역할 · 대안 · 카드 기준 기념품 (2026-10-27) ──
sc('S50', '모로스 천상 기예+서약 일격 카드 — 헤라 = 마력 공급·기본 딜, 헤스티아 = 불벼락 조건, 천부적 마력 대안, 첫 기념품 헤라', () => {
  const r = E.recommendRunStart('flames', 'flames_moros', { graspCap: 27, variant: 'flames_orbit_hera_zeus' });
  const v = r.directions.find((d) => d.id === 'flames_omega_special_orbit').variants.find((x) => x.id === 'flames_orbit_hera_zeus');
  const role = (g) => v.god_roles.find((x) => x.god === g);
  const fb = v.fallbacks['hera_born_gain'] || [];
  return { rows: v.god_roles.map((g, i) => ({ id: g.god, rank: i + 1, score: 0, reason: g.boons.map((b) => b.name_ko).join('·') + ' / ' + g.roles.join('·'), warnings: [], badges: [] })), extra: r.first_keepsake && r.first_keepsake.reason, checks: [
    check("헤라 역할 = 마력 공급·기본 딜", role('hera').roles.includes('마력 공급') && role('hera').roles.includes('기본 딜'), role('hera').roles.join(',')),
    check("제우스 역할에 '불벼락 한쪽'", role('zeus').roles.includes('불벼락 한쪽'), role('zeus').roles.join(',')),
    check("헤스티아 = 염화 고리(조건) · '불벼락 조건'", role('hestia').boons.some((b) => b.id === 'hestia_smolder_ring' && b.cond) && role('hestia').roles.includes('불벼락 조건'), JSON.stringify(role('hestia'))),
    check('천부적 마력 대안 = 대전된 마력(제우스) → 따스한 마력(헤스티아)', fb.map((x) => x.id).join(',') === 'zeus_ionic_gain,hestia_cardio_gain', fb.map((x) => x.name_ko).join(',')),
    check('천상 기예 대안 없음 (바꾸면 불벼락의 제우스 쪽이 사라짐)', Array.isArray(v.fallbacks['zeus_heaven_flourish']) && v.fallbacks['zeus_heaven_flourish'].length === 0, JSON.stringify(v.fallbacks['zeus_heaven_flourish'])),
    check("기념품 이유의 카드명이 잘리지 않음 ('천상 기예 + 서약 일격')", /'천상 기예 \+ 서약 일격'/.test(r.first_keepsake.reason), r.first_keepsake.reason),
    check('첫 기념품 = 헤라(천부적 마력 먼저), 문구에 등장 확정 없음', r.first_keepsake && r.first_keepsake.god === 'hera' && /천부적 마력/.test(r.first_keepsake.reason) && !/확정/.test(r.first_keepsake.reason), r.first_keepsake && r.first_keepsake.reason),
  ] };
});

sc('S51', '다음 지역 기념품 — 카드 고정, 헤라·제우스만 나왔으면 헤스티아(염화 고리 · 불벼락 조건)', () => {
  const st = E.applyChoice(S({ weapon: 'flames', aspect: 'flames_moros', region: 2, boons: ['zeus_heaven_flourish', 'hera_sworn_strike', 'hera_born_gain'], gods_seen: ['hera', 'zeus'] }), { kind: 'variant', id: 'flames_orbit_hera_zeus' });
  const k = E.recommendKeepsake(st);
  const st2 = E.applyChoice(st, { kind: 'god', id: 'hestia' });
  const k2 = E.recommendKeepsake(st2);
  return { rows: [{ id: k.id, rank: 1, score: 0, reason: k.reason, warnings: [], badges: [] }], checks: [
    check('헤스티아 기념품(영원한 불씨)', k.id === 'everlasting_ember' || /헤스티아|불씨/.test(k.name_ko), k.name_ko + ' / ' + k.reason),
    check("이유에 '염화 고리' · '불벼락 조건' · '아직 안 나옴'", /염화 고리/.test(k.reason) && /불벼락 조건/.test(k.reason) && /아직 안 나옴/.test(k.reason), k.reason),
    check('헤스티아가 나왔으면 헤스티아 기념품을 더 권하지 않음', !/아직 안 나옴/.test(k2.reason || ''), (k2.name_ko || '') + ' / ' + (k2.reason || '')),
  ] };
});


sc('S52', '카드 보호 — 모로스 천상 기예+서약 일격: 강권류는 빌드 파괴, 필수를 밀어내는 화염 일격은 비추', () => {
  const core = ['zeus_heaven_flourish', 'hera_sworn_strike', 'hera_born_gain'];
  const st = E.applyChoice(S({ weapon: 'flames', aspect: 'flames_moros', region: 2, boons: core, gods_seen: ['hera', 'zeus'] }), { kind: 'variant', id: 'flames_orbit_hera_zeus' });
  const gods = E.recommendGods(st, ['hestia', 'zeus', 'hera']);
  const by = (id) => gods.find((r) => r.id === id);
  const inHestia = E.recommendBoons(E.applyChoice(st, { kind: 'god', id: 'hestia' }), ['hestia_flame_strike', 'hestia_flame_flourish', 'hestia_pyro_technique']);
  const duoRows = E.recommendBoons(st, ['duo_zeus_hera_kings_ransom', 'duo_hera_zeus_queens_ransom', 'zeus_power_surge']);
  const a = A(duoRows), h = A(inHestia);
  return { rows: gods, rows2: inHestia, checks: [
    check('헤스티아 문이 1위 (목표 · 염화 고리)', gods[0].id === 'hestia', gods.map((r) => r.id + ':' + r.grade_ko).join(' ')),
    check("제우스·헤라 역할에 강권류 없음", !['zeus', 'hera'].some((g) => by(g).roles.some((x) => /강권/.test(x))), by('zeus').roles.join(',') + ' / ' + by('hera').roles.join(',')),
    check(...a.hasBadge('duo_zeus_hera_kings_ransom', '빌드 파괴')),
    check(...a.hasBadge('duo_hera_zeus_queens_ransom', '빌드 파괴')),
    check(...a.rankOf('zeus_power_surge', 1)),
    check(...h.warnHas('hestia_flame_strike', '빌드 필수')),
    check(...h.reasonHas('hestia_flame_strike', '비추')),
    check('화염 일격 점수 < 0', inHestia.find((r) => r.id === 'hestia_flame_strike').score < 0, String(inHestia.find((r) => r.id === 'hestia_flame_strike').score)),
  ] };
});

sc('S53', '카드 보호 — 헤라 집중 카드의 끝내기(여왕의 강권)는 파괴가 아니다', () => {
  const st = E.applyChoice(S({ weapon: 'flames', aspect: 'flames_melinoe', region: 3, boons: ['hera_sworn_strike', 'hera_born_gain', 'hera_fine_line', 'zeus_storm_ring'], gods_seen: ['hera', 'zeus'] }), { kind: 'variant', id: 'flames_hold_hera' });
  const rows = E.recommendBoons(st, ['duo_hera_zeus_queens_ransom', 'duo_zeus_hera_kings_ransom']);
  const a = A(rows);
  return { rows, checks: [
    check(...a.rankOf('duo_hera_zeus_queens_ransom', 1)),
    check(...a.hasBadge('duo_hera_zeus_queens_ransom', '끝내기')),
    check(...a.hasBadge('duo_zeus_hera_kings_ransom', '빌드 파괴')),
  ] };
});


sc('S54', '신 풀 자리 — 모로스 카드: 헤라·제우스 뒤 데메테르는 "남은 자리는 헤스티아용", 그 뒤 아폴론은 빌드 막힘(패스)', () => {
  const st3 = E.applyChoice(S({ weapon: 'flames', aspect: 'flames_moros', region: 2, boons: ['zeus_heaven_flourish', 'hera_sworn_strike'], gods_seen: ['hera', 'zeus'] }), { kind: 'variant', id: 'flames_orbit_hera_zeus' });
  const d3 = E.recommendGods(st3, ['demeter'])[0];
  const st4 = E.applyChoice(S({ weapon: 'flames', aspect: 'flames_moros', region: 2, boons: ['zeus_heaven_flourish', 'hera_sworn_strike', 'demeter_arctic_ring'], gods_seen: ['hera', 'zeus', 'demeter'] }), { kind: 'variant', id: 'flames_orbit_hera_zeus' });
  const r4 = E.recommendGods(st4, ['apollo', 'hestia']);
  const ap = r4.find((r) => r.id === 'apollo'), he = r4.find((r) => r.id === 'hestia');
  const boons3 = E.recommendBoons(E.applyChoice(st3, { kind: 'god', id: 'demeter' }), ['demeter_arctic_ring', 'demeter_frigid_rush']);
  return { rows: r4, checks: [
    check("데메테르(3번째): 역할 '남은 자리는 헤스티아용'", d3.roles.some((x) => /남은 자리는 헤스티아용/.test(x)), d3.grade_ko + ' ' + d3.roles.join(',')),
    check("아폴론(4번째): 패스 + '빌드 막힘'", ap.grade === 'pass' && ap.roles.includes('빌드 막힘'), ap.grade_ko + ' ' + ap.roles.join(',')),
    check("아폴론 이유에 '헤스티아가 더 안 나옴'", /헤스티아가 더 안 나옴/.test(ap.reason), ap.reason),
    check('헤스티아가 1위', r4[0].id === 'hestia', r4.map((r) => r.id + ':' + r.grade_ko).join(' ')),
    check("데메테르 설한 고리에 '마법 칸은 염화 고리 자리' 경고", boons3.find((r) => r.id === 'demeter_arctic_ring').warnings.some((w) => /마법 칸은 염화 고리 자리/.test(w)), JSON.stringify(boons3.find((r) => r.id === 'demeter_arctic_ring').warnings)),
  ] };
});


sc('S55', '전설 경로(선택) — 모로스 카드: 청천벽력(S) 맨 위, 정전기 충격에 "전설 경로" 배지, 필수를 밀어내는 건 무효', () => {
  const v = E.recommendRunStart('flames', 'flames_moros', { graspCap: 27 }).directions.find((d) => d.id === 'flames_omega_special_orbit').variants.find((x) => x.id === 'flames_orbit_hera_zeus');
  const L = v.legendary[0];
  const st = E.applyChoice(S({ weapon: 'flames', aspect: 'flames_moros', region: 2, boons: ['zeus_heaven_flourish', 'hera_sworn_strike', 'hera_born_gain'], gods_seen: ['hera', 'zeus'] }), { kind: 'variant', id: 'flames_orbit_hera_zeus' });
  const rows = E.recommendBoons(st, ['zeus_static_shock', 'zeus_divine_vengeance', 'zeus_lightning_lance']);
  const a = A(rows);
  const c = E.buildChecklist(st);
  return { rows, checks: [
    check('카드 전설 1위 = 청천벽력(S), 제우스, 메인 딜 신', L && L.id === 'zeus_bolt_from_the_blue' || (L && L.name_ko === '청천벽력' && L.tier === 'S' && L.main_dmg), JSON.stringify(L && { n: L.name_ko, t: L.tier, m: L.main_dmg, need: L.need })),
    check('청천벽력 1/3 (천상 기예 ✓)', L.met === 1 && L.total === 3, L.met + '/' + L.total),
    check(...a.hasBadge('zeus_static_shock', '전설 경로')),
    check(...a.reasonHas('zeus_static_shock', '청천벽력')),
    check('체크리스트에 전설 경로', c.legendary.length >= 1 && c.legendary[0].name_ko === '청천벽력', JSON.stringify(c.legendary.map((x) => x.name_ko + ' ' + x.met + '/' + x.total))),
    check('전설 경로 가산은 목표 보조(+2)보다 작다', W.BOON.TARGET_LEG < W.BOON.TARGET_SUPPORT, ''),
  ] };
});

// ── 실행 ────────────────────────────────────────────────
const out = [];
let pass = 0, fail = 0;
const results = [];
for (const s of scenarios) {
  let r;
  try { r = s.fn(); } catch (e) { r = { rows: [], checks: [check('예외 없이 실행', false, e.message)] }; }
  const ok = r.checks.every((c) => c.ok);
  ok ? pass++ : fail++;
  results.push({ s, r, ok });
}

// S16 결정성
let detOk = true, detMsg = 'ok';
try {
  const run = () => scenarios.map((s) => { try { return JSON.stringify(s.fn()); } catch (e) { return 'ERR'; } }).join('\n');
  const a = run(), b = run();
  detOk = a === b;
  if (!detOk) detMsg = '2회 실행 결과가 다름';
} catch (e) { detOk = false; detMsg = e.message; }
detOk ? pass++ : fail++;

out.push('# 테스트 결과 (2-B, 오퍼스)\n');
out.push(`실행: \`node engine/test.js\` · 시나리오 ${scenarios.length + 1}개 · **PASS ${pass} / FAIL ${fail}**\n`);
out.push('> 검사 대상은 순위·배지·경고의 존재. 절대 점수는 검사하지 않는다 (2-C 튜닝으로 바뀜).\n');
out.push('---\n');

const table = (rows) => {
  const l = ['| 순위 | 은혜/망치 | 점수 | 이유 | 경고 | 배지 |', '|---|---|---|---|---|---|'];
  for (const r of rows) l.push(`| ${r.rank} | ${nameOf(r.id)} | ${r.score === -Infinity ? '불가' : r.score} | ${r.reason} | ${r.warnings.join('<br>')} | ${r.badges.join(', ')} |`);
  return l.join('\n');
};

for (const { s, r, ok } of results) {
  out.push(`## ${s.id}. ${s.title}   ${ok ? '✅ PASS' : '❌ FAIL'}\n`);
  if (r.rows && r.rows.length) out.push(table(r.rows) + '\n');
  if (r.rows2 && r.rows2.length) out.push('**두 번째 호출**\n\n' + table(r.rows2) + '\n');
  if (r.extra) out.push(`${r.extra}\n`);
  out.push('| 검사 | 결과 | 실제 |');
  out.push('|---|---|---|');
  for (const c of r.checks) out.push(`| ${c.label} | ${c.ok ? 'O' : 'X'} | ${c.actual} |`);
  out.push('');
  if (!ok) {
    const bad = r.checks.filter((c) => !c.ok);
    out.push(`> **깨진 기대**: ${bad.map((c) => `${c.label} (실제: ${c.actual})`).join(' / ')}\n`);
    const dbg = (r.rows || []).concat(r.rows2 || []).filter((x) => x.breakdown).map((x) => `${nameOf(x.id)}: ${JSON.stringify(x.breakdown)}`);
    if (dbg.length) out.push('```\n' + dbg.join('\n') + '\n```\n');
  }
}
out.push(`## S16. 결정성   ${detOk ? '✅ PASS' : '❌ FAIL'}\n`);
out.push(`전 시나리오 2회 실행 결과 동일 여부: ${detOk ? '동일' : detMsg}\n`);
out.push('---\n');
out.push(`## 집계\n\n**PASS ${pass} / FAIL ${fail}**\n`);
if (fail) out.push('FAIL 시나리오의 `breakdown`을 위에 첨부했다. 2-C에서 `engine/weights.js`만 고쳐 재실행할 것.\n');

fs.writeFileSync(path.join(__dirname, 'TEST_RESULTS.md'), out.join('\n'), 'utf8');
console.log(`PASS ${pass} / FAIL ${fail}`);
for (const { s, r, ok } of results) if (!ok) console.log(`  FAIL ${s.id}: ${r.checks.filter((c) => !c.ok).map((c) => c.label + ' → ' + c.actual).join(' ; ')}`);
if (!detOk) console.log(`  FAIL S16: ${detMsg}`);
process.exitCode = fail ? 1 : 0;
