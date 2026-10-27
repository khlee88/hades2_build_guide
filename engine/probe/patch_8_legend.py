# -*- coding: utf-8 -*-
"""8-N (오퍼스, 2026-10-27): 빌드 카드 — 전설 경로 (선택).

사용자: "전설이 필수인 빌드는 없지만, 빌드를 완성하면서 보조로 메인 딜의 전설을 노려도 좋지 않을까? 옵셔널하게"
data/variant_plan.py가 카드마다 plan.legendary를 계산 — 주요·후보 신의 전설 중 필수+융합 배치를 건드리지 않고 남은 칸·보조로 조건을 채울 수 있는 것,
정렬 = 추가로 받을 은혜 수 → 강함(S/A/B) → 메인 딜 신(공격·기술 필수의 신). 최대 3개.
 - 엔진: 전설 조건의 미충족 그룹을 채우는 은혜에 '전설 경로' +1.5 (필수·조건·보조보다 아래, 필수를 밀어내면 무효). 이유 "전설 '청천벽력'(S) 조건 — 선택, 1/3"
 - 카드: "전설(선택) 청천벽력(S) — 2개 더: …" (맨 위 1개, 나머지는 근거·메모 안)
 - 체크리스트: "전설(선택) 청천벽력 1/3 · 남음 …" 한 줄 + 접기 안에 나머지
"""
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RJ = os.path.join(ROOT, 'engine', 'recommend.js'); WJ = os.path.join(ROOT, 'engine', 'weights.js'); TJ = os.path.join(ROOT, 'engine', 'test.js'); JS = os.path.join(ROOT, 'app', 'src', 'app.js')
def load(p): return io.open(p, encoding='utf-8').read()
def save(p, s): io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, old, new, n=1):
    c = s.count(old); assert c == n, ('anchor %d != %d: %r' % (c, n, old[:80])); return s.replace(old, new)

w = load(WJ)
if 'TARGET_LEG' not in w:
    w = rep(w, "    BREAK_MUST: -8,", "    TARGET_LEG: 1.5,            // 8-N: 전설 경로(선택) — 보조 목표(2)보다 아래, 동점 깨기 수준\n    BREAK_MUST: -8,")
    save(WJ, w); print('weights.js: TARGET_LEG')

r = load(RJ)
if 'legView' not in r:
    r = rep(r, "  const dirOfVariant = (vid) =>",
"""  // 8-N: 전설 경로 — ownedSet 기준 진행도와 남은 선택지 (선택지는 plan이 계산한, 이 카드에서 가능한 것만)
  function legView(v, ownedSet) {
    return ((v.plan && v.plan.legendary) || []).map((L) => {
      const lb = boonById.get(L.id); const grps = (lb && lb.prereq && lb.prereq.all) || [];
      const groups = grps.map((grp, i) => {
        const have = (grp.any || []).filter((t) => tokenMet(t, ownedSet));
        const pg = (L.groups || [])[i] || {};
        return have.length ? { met: true, have: have.slice(0, 1).map((t) => nameOf(t)) } : { met: false, options: (pg.options || []).filter((x) => !ownedSet.has(x)).map((x) => nameOf(x)), ids: (pg.options || []).filter((x) => !ownedSet.has(x)) };
      });
      const met = groups.filter((g) => g.met).length;
      return { id: L.id, name_ko: nameOf(L.id), effect: lb ? lb.effect : '', tier: L.tier, god: L.god, god_ko: nameOf(L.god), main_dmg: !!L.main_dmg, need: L.need, groups, met, total: groups.length, owned: ownedSet.has(L.id) };
    });
  }
  const dirOfVariant = (vid) =>""")
    r = rep(r, "      god_roles: godRolesOf(v), fallbacks: fallbacksOf(v, dirOfVariant(v.id)),   // 8-K",
               "      god_roles: godRolesOf(v), fallbacks: fallbacksOf(v, dirOfVariant(v.id)),   // 8-K\n      legendary: legView(v, new Set([...(v.must || []), ...((v.plan && v.plan.extra) || [])])),   // 8-N: 전설 경로 (선택)")
    r = rep(r, "      support_after: view.support_after,", "      support_after: view.support_after,\n      legendary: legView(v, dv.owned),   // 8-N")
    # 은혜: 전설 경로
    r = rep(r, "      else if ((dv.variant.support || []).includes(b.id)) { targetKind = 'support'; flat += W.BOON.TARGET_SUPPORT; bd.target = W.BOON.TARGET_SUPPORT; badges.push('목표 보조'); }",
"""      else if ((dv.variant.support || []).includes(b.id)) { targetKind = 'support'; flat += W.BOON.TARGET_SUPPORT; bd.target = W.BOON.TARGET_SUPPORT; badges.push('목표 보조'); }
      else {   // 8-N: 전설 경로 (선택) — 미충족 그룹을 채울 때만
        const L = legView(dv.variant, dv.owned).find((x) => !x.owned && x.groups.some((g) => !g.met && (g.ids || []).includes(b.id)));
        if (L) { targetKind = 'leg'; condDuo = L; flat += W.BOON.TARGET_LEG; bd.target = W.BOON.TARGET_LEG; badges.push('전설 경로'); }
      }""")
    r = rep(r, "    else if (targetKind === 'support') reason = `빌드 '${vshort(dv.variant.name_ko)}' 보조`;",
               "    else if (targetKind === 'support') reason = `빌드 '${vshort(dv.variant.name_ko)}' 보조`;\n    else if (targetKind === 'leg') reason = `전설 '${condDuo.name_ko}'(${condDuo.tier}) 조건 — 선택, ${condDuo.met}/${condDuo.total}`;")
    save(RJ, r); print('recommend.js: 8-N')

t = load(TJ)
if "sc('S55'" not in t:
    NEW = """

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
"""
    t = rep(t, "\n// ── 실행 ────────────────────────────────────────────────", NEW + "\n// ── 실행 ────────────────────────────────────────────────")
    save(TJ, t); print('test.js: S55')

s = load(JS)
if 'v.legendary' not in s:
    # 카드: 융합 줄 다음, 근거·메모 앞에 전설 1개
    s = rep(s, "      '<details class=\"xs dim\" style=\"margin-top:4px\"><summary>근거 · 메모</summary>",
"""      // 8-N: 전설 경로 (선택) — 맨 위 1개만, 나머지는 근거·메모 안
      (v.legendary && v.legendary.length ? '<div class="xs dim" style="margin-top:3px">' + legLine(v.legendary[0], true) + '</div>' : '') +
      '<details class="xs dim" style="margin-top:4px"><summary>근거 · 메모</summary>""")
    s = rep(s, "        '<div style=\"margin-top:4px\">' + esc((v.sources || []).join(' / ')) + '</div></details>' +",
               "        (v.legendary && v.legendary.length > 1 ? '<div style=\"margin-top:4px\">' + v.legendary.slice(1).map(function (L) { return legLine(L, false); }).join('<br>') + '</div>' : '') +\n        '<div style=\"margin-top:4px\">' + esc((v.sources || []).join(' / ')) + '</div></details>' +")
    s = rep(s, "  function variantCard(v, selected, onPick) {",
"""  // 8-N: 전설 한 줄 — "전설(선택) 청천벽력(S) 제우스 — 2개 더: 정전기 충격·전압 급증… + 전기 구이·후속 낙뢰…"
  function legLine(L, head, prog) {
    var left = L.groups.filter(function (g) { return !g.met; });
    return (head ? '<span class="dim">전설(선택)</span> ' : '') + '<b class="dimless">' + esc(L.name_ko) + '</b>(' + esc(L.tier) + ')' + (prog ? ' ' + L.met + '/' + L.total : '') + ' ' + esc(L.god_ko) + (L.main_dmg ? ' · 메인 딜 신' : '') +
      (L.owned ? ' — 획득' : left.length ? ' — ' + left.length + '개 더: ' + left.map(function (g) { return esc(g.options.slice(0, 3).join('·')) + (g.options.length > 3 ? '…' : ''); }).join(' + ') : ' — 조건 완성, ' + esc(L.god_ko) + ' 문에서 뜰 수 있음');
  }
  function variantCard(v, selected, onPick) {""")
    # 체크리스트: 보조 접기 위에 전설 1줄, 접기 안에 나머지
    s = rep(s, "      var sup = chk.support.filter(function (x) { return x.owned; }).length, hm = chk.hammers.filter(function (x) { return x.owned; }).length;",
"""      if (chk.legendary && chk.legendary.length) {   // 8-N: 전설 경로 (선택) — 진행이 가장 많은 것 1줄
        var lsort = chk.legendary.slice().sort(function (a, b) { return (b.owned - a.owned) || (b.met - a.met); });
        box.appendChild(el('<div class="xs dim" style="margin-top:6px">' + legLine(lsort[0], true, true) + '</div>'));
      }
      var sup = chk.support.filter(function (x) { return x.owned; }).length, hm = chk.hammers.filter(function (x) { return x.owned; }).length;""")
    save(JS, s); print('app.js: 전설 경로')

# 후속 정정 (같은 날): 카드 고정 시 방향 보조 문구가 전설 경로 문구를 가렸다(S55) — 'leg' 이유를 cond_opt 바로 뒤로 옮긴다
r = load(RJ)
LEGR = "    else if (targetKind === 'leg') reason = `전설 '${condDuo.name_ko}'(${condDuo.tier}) 조건 — 선택, ${condDuo.met}/${condDuo.total}`;"
if LEGR + '\n' in r and '전설 경로가 더 구체적' not in r:
    r = r.replace('\n' + LEGR, '')
    i = r.index("    else if (targetKind === 'cond_opt') reason ="); j = r.index('\n', i)
    r = r[:j + 1] + LEGR + '   // 8-N: 카드 고정 시 방향 보조 문구보다 전설 경로가 더 구체적\n' + r[j + 1:]
    save(RJ, r); print('recommend.js: leg 이유 순서')
