// SCHEMA.md 검증 규칙 구현. 실행: node data/validate.js
const fs = require('fs');
const path = require('path');

const load = (n) => JSON.parse(fs.readFileSync(path.join(__dirname, n), 'utf8'));
const gods = load('gods.json');
const boons = load('boons.json');
const duos = load('duo_legendary.json');
const weapons = load('weapons.json');
const arcana = load('arcana.json');
const keepsakes = load('keepsakes.json');
const hexes = load('hexes.json');
const hammers = load('hammers.json');
const builds = load('build_directions.json');

const SLOTS = ['attack', 'special', 'cast', 'sprint', 'dash', 'magick', 'passive', 'hex', 'infusion', 'legendary'];
const CURSES = ['blitz', 'scorch', 'froth', 'freeze', 'gust', 'daze', 'weak', 'glow', 'hitch', 'wounds', 'marked', 'morph', 'charm', 'shine', 'none'];
const CORE_GODS = ['zeus', 'hestia', 'poseidon', 'demeter', 'apollo', 'aphrodite', 'hephaestus', 'hera', 'ares'];
const CORE_SLOTS = ['attack', 'special', 'cast', 'sprint', 'magick'];

const errors = [];
const warns = [];
const err = (m) => errors.push(m);
const warn = (m) => warns.push(m);

// 1. id 유일성
for (const [name, arr] of [['gods', gods], ['boons', boons], ['duo_legendary', duos], ['weapons', weapons], ['arcana', arcana], ['keepsakes', keepsakes], ['hexes', hexes], ['hammers', hammers]]) {
  const seen = new Set();
  for (const o of arr) {
    if (!o.id) { err(`[${name}] id 누락: ${JSON.stringify(o).slice(0, 60)}`); continue; }
    if (seen.has(o.id)) err(`[${name}] id 중복: ${o.id}`);
    seen.add(o.id);
  }
}

const godIds = new Set(gods.map((g) => g.id));
const boonIds = new Set(boons.map((b) => b.id));
// 무기 양상 id도 유일해야 함
{
  const seen = new Set();
  for (const w of weapons) for (const a of w.aspects || []) {
    if (seen.has(a.id)) err(`[weapons] 양상 id 중복: ${a.id}`);
    seen.add(a.id);
  }
}

// 2. boons[].god 유효성
for (const b of boons) {
  if (!godIds.has(b.god)) err(`[boons] 알 수 없는 god: ${b.id} -> ${b.god}`);
  if (!SLOTS.includes(b.slot)) err(`[boons] 잘못된 slot: ${b.id} -> ${b.slot}`);
}

// 카테고리 토큰 해석
const RING = new Set(boons.filter((b) => (b.tags || []).includes('ring')).map((b) => b.id));
const STRIKE = new Set(boons.filter((b) => b.slot === 'attack').map((b) => b.id));
const resolvable = (tok) => {
  if (boonIds.has(tok)) return true;
  if (tok === 'cat:ring') return RING.size > 0;
  if (tok === 'cat:strike') return STRIKE.size > 0;
  if (tok.startsWith('god:')) return godIds.has(tok.slice(4));
  return false;
};

// 3. requires / prereq 안의 id 유효성
const checkCond = (cond, where) => {
  if (!cond) return;
  if (!Array.isArray(cond.all)) { err(`[${where}] requires에 all 배열 없음`); return; }
  for (const group of cond.all) {
    if (!Array.isArray(group.any) || group.any.length === 0) { err(`[${where}] any 그룹이 비어있음`); continue; }
    for (const tok of group.any) if (!resolvable(tok)) err(`[${where}] 해석 불가 참조: ${tok}`);
  }
};
for (const b of boons) checkCond(b.prereq, `boons/${b.id}`);
for (const d of duos) checkCond(d.requires, `duo_legendary/${d.id}`);

// 4. gods[].curse 유효성
for (const g of gods) {
  if (g.curse && !CURSES.includes(g.curse)) err(`[gods] 잘못된 curse: ${g.id} -> ${g.curse}`);
  if (g.curse2 && !CURSES.includes(g.curse2)) err(`[gods] 잘못된 curse2: ${g.id} -> ${g.curse2}`);
}
// 태그에 쓰인 저주명도 검사
for (const b of [...boons, ...duos]) {
  for (const t of b.tags || []) {
    const m = /^curse_(apply|scale):(.+)$/.exec(t);
    if (m && !CURSES.includes(m[2])) err(`[tags] 알 수 없는 저주: ${b.id} -> ${t}`);
  }
}

// 5. 핵심 슬롯 배타성 — 5칸에는 신 1명의 은혜만 장착 가능
//    (a) 핵심 신 9명은 슬롯당 정확히 1개
for (const g of CORE_GODS) {
  for (const s of CORE_SLOTS) {
    const n = boons.filter((b) => b.god === g && b.slot === s);
    if (n.length === 0) err(`[커버리지] ${g}에 ${s} 슬롯 은혜 없음`);
    else if (n.length > 1) err(`[슬롯 배타] ${g}가 ${s} 슬롯에 ${n.length}개: ${n.map((x) => x.id).join(', ')}`);
  }
}
//    (b) 핵심 슬롯을 차지하는 은혜는 핵심 신 9명의 것뿐 (헤르메스·아르테미스는 칸 미점유)
for (const b of boons) {
  const inCore = CORE_SLOTS.includes(b.slot);
  if (inCore && !CORE_GODS.includes(b.god)) err(`[슬롯 배타] ${b.god}는 핵심 슬롯을 점유할 수 없음: ${b.id} (${b.slot})`);
  if (b.occupies_slot !== (inCore && CORE_GODS.includes(b.god))) err(`[슬롯 배타] occupies_slot 값 불일치: ${b.id}`);
}
//    (c) 칸 점유 은혜의 conflicts는 같은 슬롯의 다른 점유 은혜를 반드시 전부 포함
for (const s of CORE_SLOTS) {
  const ids = boons.filter((b) => b.occupies_slot && b.slot === s).map((b) => b.id);
  for (const b of boons.filter((x) => x.occupies_slot && x.slot === s)) {
    const have = new Set(b.conflicts || []);
    for (const i of ids) if (i !== b.id && !have.has(i)) err(`[슬롯 배타] ${b.id}의 conflicts에 같은 칸 ${i} 누락`);
  }
}
// 6. 듀오 커버리지: 핵심 신 9명 모든 쌍
for (let i = 0; i < CORE_GODS.length; i++) {
  for (let j = i + 1; j < CORE_GODS.length; j++) {
    const a = CORE_GODS[i], b = CORE_GODS[j];
    const found = duos.some((d) => d.kind === 'duo' && d.gods.includes(a) && d.gods.includes(b));
    if (!found) warn(`[융합 누락] ${a} + ${b}`);
  }
}
// 전설 은혜 커버리지
for (const g of CORE_GODS) {
  if (!duos.some((d) => d.kind === 'legendary' && d.gods[0] === g)) warn(`[전설 누락] ${g}`);
}

// duo에 등장하는 신 id 유효성
for (const d of duos) for (const g of d.gods) if (!godIds.has(g)) err(`[duo_legendary] 알 수 없는 god: ${d.id} -> ${g}`);

// keepsakes god_favor 연결 검사
for (const k of keepsakes) {
  if (k.kind === 'god_favor' && k.god && !godIds.has(k.god) && k.god !== 'athena') warn(`[keepsakes] gods.json에 없는 신: ${k.id} -> ${k.god}`);
}
// hexes godsent 연결 검사
for (const h of hexes) if (h.godsent_god && !godIds.has(h.godsent_god)) err(`[hexes] 알 수 없는 신: ${h.id} -> ${h.godsent_god}`);

// 6-b. 다이달로스 망치 검증
const weaponIds = new Set(weapons.map((w) => w.id));
const aspectIds = new Set();
for (const w of weapons) for (const a of w.aspects || []) aspectIds.add(a.id);
const hammerIds = new Set(hammers.map((h) => h.id));
const AFFECTS = ['attack', 'special', 'cast', 'dash', 'sprint', 'magick', 'omega_attack', 'omega_special', 'omega_cast'];
for (const h of hammers) {
  if (!weaponIds.has(h.weapon)) err(`[hammers] 알 수 없는 무기: ${h.id} -> ${h.weapon}`);
  for (const a of h.affects || []) if (!AFFECTS.includes(a)) err(`[hammers] 잘못된 affects: ${h.id} -> ${a}`);
  if (h.aspect_only && !aspectIds.has(h.aspect_only)) err(`[hammers] 알 수 없는 양상(aspect_only): ${h.id} -> ${h.aspect_only}`);
  for (const a of h.aspect_excluded || []) if (!aspectIds.has(a)) err(`[hammers] 알 수 없는 양상(aspect_excluded): ${h.id} -> ${a}`);
  for (const c of h.conflicts || []) {
    const other = hammers.find((x) => x.id === c);
    if (other && other.weapon !== h.weapon) err(`[hammers] 다른 무기와 상충 지정: ${h.id} -> ${c}`);
  }
}
// 초반 4무기는 각각 망치가 있어야 함
for (const w of weapons.filter((x) => x.unlock_order <= 4)) {
  const n = hammers.filter((h) => h.weapon === w.id).length;
  if (n === 0) err(`[커버리지] ${w.id}에 망치 업그레이드 없음`);
  else if (n < 10) warn(`[망치 부족] ${w.id}: ${n}개`);
}

// 6-c. 상충(conflicts) 전 파일 통합 검사: id 존재 + 양방향 대칭
{
  const ALL = new Map();
  for (const o of [...boons, ...duos, ...hammers, ...arcana]) ALL.set(o.id, o);
  for (const o of ALL.values()) {
    for (const c of o.conflicts || []) {
      if (!ALL.has(c)) { err(`[상충] 알 수 없는 id: ${o.id} -> ${c}`); continue; }
      if (!(ALL.get(c).conflicts || []).includes(o.id)) err(`[상충] 단방향: ${o.id} -> ${c} (역방향 누락)`);
    }
    if (o.boon_conflicts) err(`[상충] 폐기된 필드 boon_conflicts 사용: ${o.id}`);
  }
}
// 6-d. 전설 은혜: boons.json의 prereq와 duo_legendary.json의 requires가 같아야 함
for (const d of duos.filter((x) => x.kind === 'legendary')) {
  const b = boons.find((x) => x.god === d.gods[0] && x.slot === 'legendary');
  if (!b) { warn(`[전설] boons.json에 ${d.gods[0]} 전설 없음`); continue; }
  if (JSON.stringify(b.prereq) !== JSON.stringify(d.requires)) err(`[전설] 조건 불일치: ${b.id} vs ${d.id}`);
}
// 6-e. 폐기된 태그
for (const b of boons) if ((b.tags || []).includes('duo_gateway')) err(`[태그] 폐기된 duo_gateway 사용: ${b.id}`);

// 6-f. build_directions.json — 모든 참조 id가 실제로 존재해야 함
{
  const ids = {
    boon: new Set(boons.map((b) => b.id)), duo: new Set(duos.map((d) => d.id)),
    hammer: new Set(hammers.map((h) => h.id)), arcana: new Set(arcana.map((a) => a.id)),
    keepsake: new Set(keepsakes.map((k) => k.id)), hex: new Set(hexes.map((h) => h.id)),
    weapon: new Set(weapons.map((w) => w.id)), aspect: new Set(weapons.flatMap((w) => (w.aspects || []).map((a) => a.id))),
  };
  const chk = (list, set, kind, where) => (list || []).forEach((x) => { if (!set.has(x)) err(`[빌드방향] ${where}: 알 수 없는 ${kind} id ${x}`); });
  chk(builds.always_take.boons, ids.boon, '은혜', 'always_take');
  chk(builds.survival_kit.passive, ids.boon, '은혜', 'survival_kit.passive');
  for (const [slot, l] of Object.entries(builds.survival_kit.slot)) {
    chk(l, ids.boon, '은혜', `survival_kit.slot.${slot}`);
    l.forEach((x) => { const b = boons.find((y) => y.id === x); if (b && b.slot !== slot) err(`[빌드방향] survival_kit.slot.${slot}에 ${slot} 칸이 아닌 은혜 ${x}(${b.slot})`); });
  }
  chk(builds.survival_kit.duos, ids.duo, '융합', 'survival_kit.duos');
  chk(builds.arcana_beginner_set.cards, ids.arcana, '아르카나', 'arcana_beginner_set');
  chk(builds.arcana_beginner_set.upgrade_path, ids.arcana, '아르카나', 'arcana_beginner_set.upgrade_path');
  chk(builds.keepsake_plan.region1, ids.keepsake, '기념품', 'keepsake_plan.region1');
  chk(builds.keepsake_plan.boss_region, ids.keepsake, '기념품', 'keepsake_plan.boss_region');
  chk(builds.hex_beginner, ids.hex, '비술', 'hex_beginner');
  {
    const g = builds.arcana_beginner_set.grasp;
    const sum = builds.arcana_beginner_set.cards.reduce((acc, id) => acc + (arcana.find((a) => a.id === id)?.grasp ?? 0), 0);
    if (sum > g) err(`[빌드방향] 아르카나 초기 세트 이해도 초과: ${sum} > ${g}`);
  }
  for (const [wid, w] of Object.entries(builds.weapons)) {
    if (!ids.weapon.has(wid)) { err(`[빌드방향] 알 수 없는 무기 ${wid}`); continue; }
    const dirIds = new Set(w.directions.map((d) => d.id));
    for (const [god, dl] of Object.entries(w.first_god_map)) {
      if (!godIds.has(god)) err(`[빌드방향] ${wid}.first_god_map: 알 수 없는 신 ${god}`);
      dl.forEach((x) => { if (!dirIds.has(x)) err(`[빌드방향] ${wid}.first_god_map.${god}: 알 수 없는 방향 ${x}`); });
    }
    for (const g of CORE_GODS) if (!w.first_god_map[g]) warn(`[빌드방향] ${wid}.first_god_map에 ${g} 없음`);
    for (const d of w.directions) {
      const where = `${wid}/${d.id}`;
      for (const [slot, l] of Object.entries(d.slot_prefs)) {
        chk(l, ids.boon, '은혜', `${where}.slot_prefs.${slot}`);
        l.forEach((x) => { const b = boons.find((y) => y.id === x); if (b && b.slot !== slot) err(`[빌드방향] ${where}.slot_prefs.${slot}에 ${slot} 칸이 아닌 은혜 ${x}(${b.slot})`); });
      }
      for (const s of d.core_slots) if (!d.slot_prefs[s]) err(`[빌드방향] ${where}: core_slot ${s}에 slot_prefs 없음`);
      chk(d.support_boons, ids.boon, '은혜', `${where}.support_boons`);
      d.support_boons.forEach((x) => { const b = boons.find((y) => y.id === x); if (b && b.occupies_slot) err(`[빌드방향] ${where}.support_boons에 칸 점유 은혜 ${x} — slot_prefs로 옮길 것`); });
      chk(d.avoid_boons, ids.boon, '은혜', `${where}.avoid_boons`);
      chk(d.target_duos, ids.duo, '융합', `${where}.target_duos`);
      chk(d.hammers, ids.hammer, '망치', `${where}.hammers`);
      d.hammers.forEach((x) => { const h = hammers.find((y) => y.id === x); if (h && h.weapon !== wid) err(`[빌드방향] ${where}.hammers에 다른 무기 망치 ${x}`); });
      if (d.requires_hammer && !ids.hammer.has(d.requires_hammer)) err(`[빌드방향] ${where}.requires_hammer 알 수 없음`);
      chk(d.arcana, ids.arcana, '아르카나', `${where}.arcana`);
      chk(d.aspects, ids.aspect, '양상', `${where}.aspects`);
      d.aspects.forEach((x) => { if (!x.startsWith(wid + '_')) err(`[빌드방향] ${where}.aspects에 다른 무기 양상 ${x}`); });
      // 회피 은혜가 선호 목록에 동시에 있으면 모순
      const pref = new Set([...Object.values(d.slot_prefs).flat(), ...d.support_boons]);
      d.avoid_boons.forEach((x) => { if (pref.has(x)) err(`[빌드방향] ${where}: ${x}가 선호와 회피에 동시 존재`); });
    }
  }
}

// 6-g. 아르카나: 0 이해도 카드는 구조화된 awaken 조건 필수, grid_position 필수
for (const a of arcana) {
  if (!Array.isArray(a.grid_position) || a.grid_position.length !== 2) err(`[arcana] grid_position 없음: ${a.id}`);
  if (a.grasp === 0 && !(a.awaken && a.awaken.type)) err(`[arcana] 0 이해도 카드에 awaken 없음: ${a.id}`);
}

// 7. verified 통계
const all = [...gods, ...boons, ...duos, ...weapons, ...arcana, ...keepsakes, ...hexes, ...hammers];
const unverified = all.filter((o) => o.verified === false).length;

console.log('='.repeat(50));
console.log(`신 ${gods.length} / 은혜 ${boons.length} / 융합·전설 ${duos.length} / 무기 ${weapons.length} / 아르카나 ${arcana.length} / 기념품 ${keepsakes.length} / 비술 ${hexes.length} / 망치 ${hammers.length}`);
console.log(`미검증(verified:false) ${unverified} / 전체 ${all.length} = ${Math.round((unverified / all.length) * 100)}%`);
console.log('='.repeat(50));
if (warns.length) { console.log(`\n경고 ${warns.length}건:`); warns.forEach((w) => console.log('  ! ' + w)); }
if (errors.length) { console.log(`\n오류 ${errors.length}건:`); errors.forEach((e) => console.log('  X ' + e)); process.exitCode = 1; }
else console.log('\n오류 0건');
