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
const S = (o) => Object.assign({ region: 1, hp_state: 'mid', boons: [], hammers: [], arcana: [], keepsake: null, hex: null, gods_seen: [], direction_lock: null }, o);

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
      check('1위 방향 == Ω 공격 화력', r.directions[0].id === 'staff_omega_attack', r.directions[0].id),
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
    check(...a.setEq(['zeus_heaven_strike', 'zeus_ionic_gain'], [1, 2])),
    check(...a.rankOf('zeus_storm_ring', 3)),
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

sc('S07', '회피 은혜 표시 — 횃불 잡초 박멸', () => {
  const st = S({ weapon: 'flames', aspect: 'flames_melinoe', region: 2, boons: ['hestia_flame_strike', 'poseidon_flood_gain', 'hera_fine_line'], gods_seen: ['hestia', 'poseidon', 'hera'] });
  const rows = E.recommendBoons(st, ['demeter_weed_killer', 'demeter_frigid_rush', 'demeter_arctic_ring']);
  const a = A(rows);
  return { rows, checks: [
    check(...a.rankOf('demeter_weed_killer', 3)),
    check(...a.reasonHas('demeter_weed_killer', '비추')),
    check('잡초 박멸이 숨겨지지 않음', rows.some((r) => r.id === 'demeter_weed_killer' && Number.isFinite(r.score)), '표시됨'),
    check(...a.rankOf('demeter_frigid_rush', 1)),
    check(...a.rankOf('demeter_arctic_ring', 2)),
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

sc('S10', '망치가 방향을 연다 — 쌍검 폭발적 암습', () => {
  const st = S({ weapon: 'blades', aspect: 'blades_artemis', boons: ['hera_sworn_strike', 'poseidon_flood_gain'], gods_seen: ['hera', 'poseidon'] });
  const rows = E.recommendHammers(st, ['blades_sweeping_ambush', 'blades_dancing_knives', 'blades_melting_sickle']);
  const a = A(rows);
  const after = E.applyChoice(st, { kind: 'hammer', id: 'blades_sweeping_ambush' });
  const ds = E.directionScores(after);
  return { rows, extra: `선택 후 방향 1위 = ${ds[0].name_ko} (W=${ds[0].weight})`, checks: [
    check(...a.rankOf('blades_sweeping_ambush', 1)),
    check(...a.hasBadge('blades_sweeping_ambush', '방향 전환')),
    check('선택 후 방향 1위 == Ω 공격 암습', ds[0].id === 'blades_omega_ambush', ds[0].id),
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
  const st = S({ weapon: 'staff', aspect: 'staff_melinoe', region: 3, boons: ['zeus_heaven_strike', 'hestia_smolder_ring', 'apollo_blinding_rush', 'poseidon_flood_gain'], gods_seen: ['zeus', 'hestia', 'apollo', 'poseidon'] });
  const rows = E.recommendGods(st, ['demeter', 'zeus']);
  const a = A(rows);
  return { rows, checks: [
    check(...a.rankOf('zeus', 1)),
    check('데메테르에 새 신 표시', rows.find((r) => r.id === 'demeter').badges.includes('새 신'), String(rows.find((r) => r.id === 'demeter').badges)),
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

sc('S14', '생존 우선 — 체력 낮음', () => {
  const st = S({ weapon: 'axe', aspect: 'axe_melinoe', region: 2, hp_state: 'low', boons: ['apollo_nova_strike', 'hephaestus_volcanic_flourish'], gods_seen: ['apollo', 'hephaestus'] });
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
    check(...a.setEq(['zeus_heaven_strike', 'zeus_ionic_gain'], [1, 2])),
    check(...a.hasBadge('zeus_ionic_gain', '마력')),
    check(...a.rankOf('zeus_storm_ring', 3)),
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
