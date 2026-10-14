# -*- coding: utf-8 -*-
"""6-B 엔진 보조 (페이블, 2026-10-14).
1. 숨김 양상 전용 방향은 그 양상을 골랐을 때만 존재 — aspects가 전부 숨김 양상이고 현재 양상이 아니면 -Infinity.
   이유: 숨김 방향 4개를 추가하자 기존 4무기 런의 방향 가중치가 희석돼 S01(방향 3개)·S14(거대 분화구 2위)가 깨짐.
   "그 양상을 안 골랐는데 그 방향이 보험으로 떠 있는" 건 의미도 없다. 비숨김 전용 방향(카론·메데이아 등)은 종전처럼 낮은 F로 남긴다.
2. `keepsake_override`: 방향이 지정하면 첫 기념품을 그걸로 (셀레네 → 달빛보라, 페르세포네 → 금강석 파편).
3. 데이터: 투척·회수 루프의 aspects에서 페르세포네 제거(동점 의존 제거 — 페르세포네는 폭발 발아가 명확히 1위여야 함), 폭발 발아 keepsake_override.
4. 시나리오 S33~S36.
"""
import io, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RJ = os.path.join(ROOT, 'engine', 'recommend.js'); TJ = os.path.join(ROOT, 'engine', 'test.js'); BD = os.path.join(ROOT, 'data', 'build_directions.json')
def load(p): return io.open(p, encoding='utf-8').read()
def save(p, s): io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, old, new, n=1):
    c = s.count(old); assert c == n, ('anchor %d != %d: %r' % (c, n, old[:80])); return s.replace(old, new)

r = load(RJ)
if 'hiddenAspects' not in r:
    r = rep(r, "  const weaponById = new Map(weapons.map((w) => [w.id, w]));",
"""  const weaponById = new Map(weapons.map((w) => [w.id, w]));
  const hiddenAspects = new Set(weapons.flatMap((w) => (w.aspects || []).filter((a) => a.hidden).map((a) => a.id)));""")
    r = rep(r, "    if (d.requires_hammer && !dv.owned.has(d.requires_hammer)) return -Infinity;",
"""    if (d.requires_hammer && !dv.owned.has(d.requires_hammer)) return -Infinity;
    // 6-B: 숨김 양상 전용 방향은 그 양상을 골랐을 때만 존재한다 (다른 양상 런의 가중치를 희석하지 않도록)
    { const asp = d.aspects || []; if (asp.length && asp.every((a) => hiddenAspects.has(a)) && !asp.includes(state.aspect)) return -Infinity; }""")
    r = rep(r, """      const top = dirs[0].d;
      for (const g of mainGodsOf(top)) {
        const k = keepsakeByGod.get(g.id);""",
"""      const top = dirs[0].d;
      // 6-B: 방향이 기념품을 지정하면 그걸로 (셀레네 외투 = 달빛보라, 페르세포네 해골 = 금강석 파편)
      const ov = top.keepsake_override && keepsakeById.get(top.keepsake_override);
      if (ov && !(owned && !owned.includes(ov.id))) firstKeepsake = { id: ov.id, name_ko: ov.name_ko, god: ov.god || null, god_ko: ov.god ? nameOf(ov.god) : (ov.giver_ko || ''), effect: ov.effect, giver_ko: ov.giver_ko,
        reason: `추천 빌드 '${top.name_ko}'가 지정 — ${top.summary.slice(0, 40)}…` };
      for (const g of (firstKeepsake ? [] : mainGodsOf(top))) {
        const k = keepsakeByGod.get(g.id);""")
    save(RJ, r); print('recommend.js: 숨김 전용 방향 규칙 + keepsake_override')
else:
    print('recommend.js: 이미 적용됨')

bd = json.load(io.open(BD, encoding='utf-8'))
t = next(d for d in bd['weapons']['skull']['directions'] if d['id'] == 'skull_throw_retrieve')
if 'skull_persephone' in t['aspects']:
    t['aspects'] = ['skull_melinoe']
    b = next(d for d in bd['weapons']['skull']['directions'] if d['id'] == 'skull_blast_persephone')
    b['keepsake_override'] = 'adamant_shard'
    io.open(BD, 'w', encoding='utf-8', newline='\n').write(json.dumps(bd, ensure_ascii=False, indent=1) + '\n')
    print('build_directions.json: 투척·회수 aspects=[melinoe], 폭발 발아 keepsake_override=adamant_shard')

tj = load(TJ)
if "sc('S33'" not in tj:
    NEW = """

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
    check('열정 쇄도(질주, 핵심 칸)가 1위', rows[0].id === 'aphrodite_passion_rush', rows[0].id),
  ] };
});
"""
    tj = rep(tj, "\n// ── 실행 ────────────────────────────────────────────────", NEW + "\n// ── 실행 ────────────────────────────────────────────────")
    save(TJ, tj); print('test.js: S33~S36')
