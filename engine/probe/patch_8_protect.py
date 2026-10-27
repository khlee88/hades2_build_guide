# -*- coding: utf-8 -*-
"""8-L (오퍼스, 2026-10-27): 빌드 카드 보호 — 카드 밖 목표 차단 · 필수를 지우는 선택 비추.

모로스 천상 기예+서약 일격 카드를 고정한 시뮬레이션에서 발견:
 (1) 제우스 문 '필수 · 융합 파트너 여왕의 강권', 헤라 문 '융합 대기 · 왕의 강권' — 보험 방향(공격 꾹)의 목표가 새어 들어옴.
     여왕의 강권은 제우스 은혜(천상 기예), 왕의 강권은 헤라 은혜(서약 일격·천부적 마력)를 지운다 = 이 카드를 부순다.
 (2) 헤스티아 문에서 염화 고리가 안 뜨면 화염 일격이 1위 — 불벼락 조건은 채우지만 필수 서약 일격을 버린다.
규칙:
 - 카드 고정 시 신 등급의 목표 융합 = 카드의 목표·끝내기·후보 융합만 (방향 합집합 X)
 - 강권류("X 은혜 전부 포기")가 카드의 필수·조건 은혜를 지우면 '빌드 파괴' — 융합 후보로 뜨면 비추, 신 등급의 대기·파트너·가능에서 제외, 진전·완성 가산 없음. 카드의 끝내기면 예외
 - 카드의 필수·조건 은혜를 밀어내는 교체 = BREAK_MUST −8 + 경고 '빌드 필수 ○○을 버림' + 이유 '비추'
"""
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RJ = os.path.join(ROOT, 'engine', 'recommend.js'); WJ = os.path.join(ROOT, 'engine', 'weights.js'); TJ = os.path.join(ROOT, 'engine', 'test.js')
def load(p): return io.open(p, encoding='utf-8').read()
def save(p, s): io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, old, new, n=1):
    c = s.count(old); assert c == n, ('anchor %d != %d: %r' % (c, n, old[:80])); return s.replace(old, new)

w = load(WJ)
if 'BREAK_MUST' not in w:
    w = rep(w, "    TARGET_SUPPORT: 2,", "    TARGET_SUPPORT: 2,\n    BREAK_MUST: -8,             // 8-L: 카드 고정 시 필수·조건 은혜를 밀어내는 교체 / 필수를 지우는 강권 융합")
    save(WJ, w); print('weights.js: BREAK_MUST')

r = load(RJ)
if 'destroysCard' not in r:
    r = rep(r, "  const dirOfVariant = (vid) =>",
"""  // 8-L: 강권류 — 효과 문구 "X 은혜 전부 포기"의 X. 카드의 필수·조건 은혜가 X의 것이면 그 융합은 카드를 부순다 (끝내기면 예외)
  const loseGodOf = (D) => { const eff = (D && D.effect) || ''; for (const g of gods) if (eff.startsWith(`${g.name_ko} 은혜 전부 포기`)) return g.id; return null; };
  const cardKeep = (v) => [...(v.must || []), ...((v.plan && v.plan.cond_must) || [])];
  function destroysCard(D, v) {
    if (!v || !D) return null;
    if (v.finisher && v.finisher.duo === D.id) return null;
    const lg = loseGodOf(D); if (!lg) return null;
    const lost = cardKeep(v).filter((id) => (boonById.get(id) || {}).god === lg);
    return lost.length ? { god: lg, lost } : null;
  }
  const cardDuoSet = (v) => new Set([...(v.target_duos || []), ...(v.finisher && v.finisher.duo ? [v.finisher.duo] : []), ...(v.fourth || []).flatMap((f) => f.duos || [])]);
  const dirOfVariant = (vid) =>""")
    # 은혜: 융합 후보가 카드를 부수면 비추
    r = rep(r, """      flat += W.FLAT.DUO_CANDIDATE + tier(D ? D.power_tier : '?');
      badges.push('융합');
      bd.duo_candidate = flat;""",
"""      const brk = dv.variant && destroysCard(D, dv.variant);   // 8-L
      if (brk) {
        bd.break_must = W.BOON.BREAK_MUST;
        return { id, score: round(W.BOON.BREAK_MUST), reason: `비추: 빌드를 부숨 — ${nameOf(brk.god)} 은혜(${brk.lost.map((x) => nameOf(x)).join('·')})가 사라짐`, warnings: [`${brk.lost.map((x) => nameOf(x)).join('·')} 사라짐`], badges: ['빌드 파괴'], breakdown: bd };
      }
      flat += W.FLAT.DUO_CANDIDATE + tier(D ? D.power_tier : '?');
      badges.push('융합');
      bd.duo_candidate = flat;""")
    # 은혜: 진전·완성에서 카드 파괴 융합 제외
    r = rep(r, """    for (const D of openDuos(dv.owned)) {
      if (!reachable(D, targetAll, seenPlus)) continue;
      const beforeUnmet = unmetGroups(D, before);""",
"""    for (const D of openDuos(dv.owned)) {
      if (!reachable(D, targetAll, seenPlus)) continue;
      if (dv.variant && destroysCard(D, dv.variant)) continue;   // 8-L
      const beforeUnmet = unmetGroups(D, before);""")
    # 은혜: 필수를 밀어내는 교체
    r = rep(r, """    if (replacing) {
      warnings.push(`${eul(nameOf(replacing))} 버리게 됨`);""",
"""    const breaksMust = !!(replacing && dv.variant && cardKeep(dv.variant).includes(replacing) && !cardKeep(dv.variant).includes(b.id));   // 8-L
    if (breaksMust) warnings.push(`빌드 필수 ${eul(nameOf(replacing))} 버림`);
    if (replacing) {
      warnings.push(`${eul(nameOf(replacing))} 버리게 됨`);""")
    r = rep(r, "    const score = dirScore + flat;\n\n    // ── 이유 템플릿",
               "    if (breaksMust) { flat += W.BOON.BREAK_MUST; bd.break_must = W.BOON.BREAK_MUST; }\n    const score = dirScore + flat;\n\n    // ── 이유 템플릿")
    r = rep(r, "    if (bd.legendary) reason = '전설 은혜 — 조건을 이미 채웠음, 최우선';",
               "    if (bd.legendary) reason = '전설 은혜 — 조건을 이미 채웠음, 최우선';\n    else if (breaksMust) reason = `비추: 빌드 필수 ${eul(nameOf(replacing))} 밀어냄`;")
    # 신: 카드 고정 시 목표 = 카드 융합만, 파괴 융합 제외
    r = rep(r, "    const targets = new Set([...((main && main.target_duos) || []), ...((backup && backup.target_duos) || [])]);",
               "    // 8-L: 카드 고정 시 목표 융합 = 카드의 것만 (보험 방향 목표가 새면 여왕의 강권처럼 카드를 부수는 융합이 '필수'가 된다)\n    const targets = dv.variant ? cardDuoSet(dv.variant) : new Set([...((main && main.target_duos) || []), ...((backup && backup.target_duos) || [])]);")
    r = rep(r, """    for (const D of openDuos(dv.owned)) {
      const unmet = unmetGroups(D, dv.owned);""",
"""    for (const D of openDuos(dv.owned)) {
      if (dv.variant && destroysCard(D, dv.variant)) continue;   // 8-L
      const unmet = unmetGroups(D, dv.owned);""")
    save(RJ, r); print('recommend.js: 8-L')

t = load(TJ)
if "sc('S52'" not in t:
    NEW = """

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
"""
    t = rep(t, "\n// ── 실행 ────────────────────────────────────────────────", NEW + "\n// ── 실행 ────────────────────────────────────────────────")
    save(TJ, t); print('test.js: S52·S53')
