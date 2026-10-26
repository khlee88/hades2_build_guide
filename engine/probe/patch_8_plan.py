# -*- coding: utf-8 -*-
"""8-J 엔진·UI (오퍼스, 2026-10-26): 빌드 카드의 완성 배치(variants[].plan) 연결.

사용자: "모로스 천상 기예+서약 일격 카드가 헤라>제우스>헤스티아인데 헤스티아는 화력 보강만 — 그걸로 불벼락이 되나?"
→ 안 된다. 불벼락의 헤스티아 쪽 조건은 화염 일격·화염 기예·염화 고리 중 하나이고, 이 카드는 공격·기술·마력이 차서 **염화 고리(마법)뿐**.
data/variant_plan.py가 카드마다 "필수 + 빈 칸으로 목표 융합 조건을 동시에 채우는 배치"를 계산해 plan에 넣었다(26개가 사실상 필수).
여기서는 그 plan을:
  - 엔진: 조건 필수(cond_must) = 필수와 같은 대우(칸 1순위, '목표' 배지, 신 등급 '목표 · 은혜'). 선택지가 여럿인 조건 = '목표 조건' +2. 이유 "'불벼락' 조건 — 이 빌드에선 마법 칸 염화 고리뿐"
  - 카드: "필수 … + 융합 조건 염화 고리(마법)", 융합 줄은 이 카드에서 **실제로 가능한 선택지만**(유일이면 굵게 '유일'), 보조 선행 "(파도 일격 뒤)"
  - 체크리스트: 조건 행(☐ 염화 고리 · 불벼락 조건), 남은 조건도 plan 선택지로
"""
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RJ = os.path.join(ROOT, 'engine', 'recommend.js'); TJ = os.path.join(ROOT, 'engine', 'test.js'); JS = os.path.join(ROOT, 'app', 'src', 'app.js')
def load(p): return io.open(p, encoding='utf-8').read()
def save(p, s): io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, old, new, n=1):
    c = s.count(old); assert c == n, ('anchor %d != %d: %r' % (c, n, old[:80])); return s.replace(old, new)

r = load(RJ)
if 'planMap' not in r:
    # effectiveDirection: 조건 필수도 칸 1순위·보조로
    r = rep(r, """    for (const id of v.must || []) { const b = boonById.get(id); if (!b || !b.occupies_slot) continue; sp[b.slot] = uniq([id, ...(sp[b.slot] || [])]); }
    const fin = v.finisher && v.finisher.duo ? [v.finisher.duo] : [];
    return { ...d, slot_prefs: sp, support_boons: uniq([...(v.support || []), ...(v.must || []).filter((id) => { const b = boonById.get(id); return b && !b.occupies_slot; }), ...(d.support_boons || [])]),""",
"""    const condMust = (v.plan && v.plan.cond_must) || [];   // 8-J: 융합 조건 중 이 카드에서 유일한 것 = 사실상 필수
    for (const id of [...(v.must || []), ...condMust]) { const b = boonById.get(id); if (!b || !b.occupies_slot) continue; if ((sp[b.slot] || [])[0] && (v.must || []).includes(sp[b.slot][0]) && !(v.must || []).includes(id)) continue; sp[b.slot] = uniq([id, ...(sp[b.slot] || [])]); }
    const fin = v.finisher && v.finisher.duo ? [v.finisher.duo] : [];
    return { ...d, slot_prefs: sp, support_boons: uniq([...(v.support || []), ...[...(v.must || []), ...condMust].filter((id) => { const b = boonById.get(id); return b && !b.occupies_slot; }), ...(d.support_boons || [])]),""")
    # planMap + duoNeeds(pmap)
    r = rep(r, "  // 8-F: 융합 조건을 \"가진 것 / 아직 필요한 것\"으로. ownedSet 기준. 선택지는 칸과 함께, 최대 4개\n  function duoNeeds(duoId, ownedSet) {",
"""  // 8-J: plan 그룹을 융합 조건 그룹 번호에 맞춘다. 목표·끝내기는 필수 기준, 후보 신은 필수+조건 배치 기준으로 미충족이던 그룹 순서
  function planMap(v, duoId, kind, god) {
    const P = v && v.plan; if (!P) return null;
    const D = duoById.get(duoId); if (!D) return null;
    const base = new Set(kind === 'fourth' ? [...(v.must || []), ...(P.extra || [])] : (v.must || []));
    const pg = (P.groups || []).filter((g) => g.duo === duoId && g.kind === kind && (g.god || null) === (god || null));
    const map = {}; let k = 0;
    (D.requires.all || []).forEach((grp, idx) => { if (!groupMet(grp, base)) { if (pg[k]) map[idx] = pg[k]; k++; } });
    return map;
  }
  const condDuoOf = (v, id) => { const g = ((v.plan && v.plan.groups) || []).find((x) => (x.options || []).length === 1 && x.options[0] === id && x.kind !== 'fourth'); return g ? g.duo : null; };
  // 8-F: 융합 조건을 "가진 것 / 아직 필요한 것"으로. ownedSet 기준. 선택지는 칸과 함께, 최대 4개 (8-J: pmap이 있으면 그 카드에서 가능한 선택지만)
  function duoNeeds(duoId, ownedSet, pmap) {""")
    r = rep(r, """      const gods = uniq(any.map(godOf).filter(Boolean));
      return { met: have.length > 0, have: have.map(tokName), god: gods.length === 1 ? nameOf(gods[0]) : null, options: any.slice(0, 4).map(tokName), more: Math.max(0, any.length - 4) };
    });""",
"""      const gods = uniq(any.map(godOf).filter(Boolean));
      const pg = pmap && pmap[idx];
      if (have.length === 0 && pg && (pg.options || []).length) {
        const ok = pg.options.filter((id) => !ownedSet.has(id));
        return { met: false, have: [], god: gods.length === 1 ? nameOf(gods[0]) : null, options: ok.map(tokName), more: 0, forced: ok.length === 1, pick: pg.pick ? tokName(pg.pick) : null, planned: true };
      }
      return { met: have.length > 0, have: have.map(tokName), god: gods.length === 1 ? nameOf(gods[0]) : null, options: any.slice(0, 4).map(tokName), more: Math.max(0, any.length - 4) };
    });""")
    r = rep(r, "    const groups = (D.requires.all || []).map((g) => {\n      const any = g.any || [];\n      const have = any.filter((t) => tokenMet(t, ownedSet));",
               "    const groups = (D.requires.all || []).map((g, idx) => {\n      const any = g.any || [];\n      const have = any.filter((t) => tokenMet(t, ownedSet));")
    # variantView: duo_needs를 plan 기준으로 + cond_must / support_after
    r = rep(r, "      duo_needs: uniq([...(v.target_duos || []), ...(v.finisher && v.finisher.duo ? [v.finisher.duo] : []), ...fourthDuos(v)]).map((id) => duoNeeds(id, new Set(v.must || []))).filter(Boolean),",
"""      duo_needs: [
        ...(v.target_duos || []).map((id) => duoNeeds(id, new Set(v.must || []), planMap(v, id, 'target'))),
        ...(v.finisher && v.finisher.duo ? [duoNeeds(v.finisher.duo, new Set(v.must || []), planMap(v, v.finisher.duo, 'finisher'))] : []),
        ...(v.fourth || []).flatMap((f) => (f.duos || []).map((id) => { const n = duoNeeds(id, new Set([...(v.must || []), ...((v.plan && v.plan.extra) || [])]), planMap(v, id, 'fourth', f.god)); return n ? { ...n, via: nameOf(f.god) } : null; })),
      ].filter(Boolean),
      // 8-J: 융합 조건 중 이 카드에서 유일한 은혜 = 사실상 필수
      cond_must: ((v.plan && v.plan.cond_must) || []).map((id) => { const b = boonById.get(id); const du = condDuoOf(v, id); return { id, name_ko: nameOf(id), slot_ko: b && b.occupies_slot ? SLOT_KO[b.slot] : '보조', god: b ? b.god : null, for_duo: du ? nameOf(du) : null }; }),
      support_after: Object.fromEntries(Object.entries((v.plan && v.plan.support_after) || {}).map(([k, ids]) => [k, ids.map((x) => nameOf(x))])),""")
    # 은혜 점수: 조건 필수 / 조건 택1
    r = rep(r, """      if ((dv.variant.must || []).includes(b.id)) { targetKind = 'must'; flat += W.BOON.TARGET_MUST; bd.target = W.BOON.TARGET_MUST; badges.unshift('목표'); }
      else if ((dv.variant.support || []).includes(b.id)) { targetKind = 'support'; flat += W.BOON.TARGET_SUPPORT; bd.target = W.BOON.TARGET_SUPPORT; badges.push('목표 보조'); }""",
"""      // 8-J: 융합 조건 — 그 융합의 미충족 그룹을 이 은혜가 채울 때만
      const P = dv.variant.plan || { groups: [], cond_must: [] };
      const condG = (P.groups || []).find((g) => (g.options || []).includes(b.id) && !dv.owned.has(g.duo) && unmetGroups(duoById.get(g.duo) || { requires: { all: [] } }, dv.owned).some((grp) => groupMet(grp, new Set([b.id]))));
      if ((dv.variant.must || []).includes(b.id)) { targetKind = 'must'; flat += W.BOON.TARGET_MUST; bd.target = W.BOON.TARGET_MUST; badges.unshift('목표'); }
      else if (condG && (P.cond_must || []).includes(b.id)) { targetKind = 'cond'; condDuo = condG; flat += W.BOON.TARGET_MUST; bd.target = W.BOON.TARGET_MUST; badges.unshift('목표'); }
      else if (condG) { targetKind = 'cond_opt'; condDuo = condG; flat += W.BOON.TARGET_SUPPORT; bd.target = W.BOON.TARGET_SUPPORT; badges.push('목표 조건'); }
      else if ((dv.variant.support || []).includes(b.id)) { targetKind = 'support'; flat += W.BOON.TARGET_SUPPORT; bd.target = W.BOON.TARGET_SUPPORT; badges.push('목표 보조'); }""")
    r = rep(r, "    let targetKind = null;\n    if (dv.variant) {", "    let targetKind = null, condDuo = null;\n    if (dv.variant) {")
    r = rep(r, "    else if (targetKind === 'must') reason = `빌드 '${vshort(dv.variant.name_ko)}' 필수${replacing ? ` — ${eul(nameOf(replacing))} 밀어냄` : ''}`;",
"""    else if (targetKind === 'must') reason = `빌드 '${vshort(dv.variant.name_ko)}' 필수${replacing ? ` — ${eul(nameOf(replacing))} 밀어냄` : ''}`;
    else if (targetKind === 'cond') reason = `'${nameOf(condDuo.duo)}' 조건 — 이 빌드에선 ${b.occupies_slot ? SLOT_KO[b.slot] + ' 칸 ' : ''}${b.name_ko}뿐`;
    else if (targetKind === 'cond_opt') reason = `'${nameOf(condDuo.duo)}' 조건 (택1: ${(condDuo.options || []).map((x) => nameOf(x)).join('·')})`;""")
    # 신 등급: 조건 필수도 목표
    r = rep(r, "      for (const id of dv.variant.must || []) {\n        const bb = boonById.get(id); if (!bb || bb.god !== godId || dv.owned.has(id) || blockReason(bb, state, dv, 'boon')) continue;",
               "      for (const id of [...(dv.variant.must || []), ...((dv.variant.plan && dv.variant.plan.cond_must) || [])]) {   // 8-J: 조건 필수 포함\n        const bb = boonById.get(id); if (!bb || bb.god !== godId || dv.owned.has(id) || blockReason(bb, state, dv, 'boon')) continue;")
    # 체크리스트
    r = rep(r, """      must, must_done: must.filter((m) => m.owned).length,""",
"""      must, must_done: must.filter((m) => m.owned).length,
      cond: view.cond_must.map((c) => ({ ...c, owned: dv.owned.has(c.id), filled_by: (() => { const b = boonById.get(c.id); return b && b.occupies_slot && dv.slotMap[b.slot] && dv.slotMap[b.slot] !== c.id ? nameOf(dv.slotMap[b.slot]) : null; })() })),
      support_after: view.support_after,""")
    r = rep(r, """      target_duos: view.target_duos.map((d) => ({ ...d, ...(dprog(d.id) || {}), needs: duoNeeds(d.id, dv.owned) })),
      finisher: view.finisher ? { ...view.finisher, ...(dprog(view.finisher.id) || {}), needs: duoNeeds(view.finisher.id, dv.owned) } : null,""",
"""      target_duos: view.target_duos.map((d) => ({ ...d, ...(dprog(d.id) || {}), needs: duoNeeds(d.id, dv.owned, planMap(v, d.id, 'target')) })),
      finisher: view.finisher ? { ...view.finisher, ...(dprog(view.finisher.id) || {}), needs: duoNeeds(view.finisher.id, dv.owned, planMap(v, view.finisher.id, 'finisher')) } : null,""")
    r = rep(r, "      fourth: view.fourth.map((f) => ({ ...f, seen: seen.has(f.god), duos: f.duos.map((d) => ({ ...d, ...(dprog(d.id) || {}), needs: duoNeeds(d.id, dv.owned) })) })),",
               "      fourth: view.fourth.map((f) => ({ ...f, seen: seen.has(f.god), duos: f.duos.map((d) => ({ ...d, ...(dprog(d.id) || {}), needs: duoNeeds(d.id, dv.owned, planMap(v, d.id, 'fourth', f.god)) })) })),")
    save(RJ, r); print('recommend.js: plan 연결')

t = load(TJ)
if "sc('S48'" not in t:
    NEW = """

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
"""
    t = rep(t, "\n// ── 실행 ────────────────────────────────────────────────", NEW + "\n// ── 실행 ────────────────────────────────────────────────")
    save(TJ, t); print('test.js: S48·S49')

s = load(JS)
if 'cond_must' not in s:
    # 카드: 필수 줄 뒤에 융합 조건
    s = rep(s, """      '<div class="xs" style="margin-top:3px"><span class="dim">필수</span> ' + v.must.map(function (m) { return esc(m.name_ko) + '<span class="dim">(' + esc(m.slot_ko) + ')</span>'; }).join(' · ') + '</div>' +""",
"""      '<div class="xs" style="margin-top:3px"><span class="dim">필수</span> ' + v.must.map(function (m) { return esc(m.name_ko) + '<span class="dim">(' + esc(m.slot_ko) + ')</span>'; }).join(' · ') +
        (v.cond_must && v.cond_must.length ? ' <span class="dim">+ 융합 조건</span> ' + v.cond_must.map(function (m) { return '<b>' + esc(m.name_ko) + '</b><span class="dim">(' + esc(m.slot_ko) + (m.for_duo ? ' · ' + esc(m.for_duo) : '') + ')</span>'; }).join(' · ') : '') + '</div>' +""")
    # 카드: 융합 줄 — plan 선택지, 유일 표시, 후보 신 경유
    s = rep(s, """        return '<div style="margin-top:2px"><b class="dimless">' + esc(n.name_ko) + '</b> = ' + n.groups.map(function (g) { return g.met ? esc(g.have[0]) + ' ✓' : '<span style="color:var(--text)">' + (g.god ? esc(g.god) + ' ' : '') + esc(g.options.join('·')) + (g.more ? ' 외 ' + g.more : '') + '</span>'; }).join(' + ') + '</div>'; }).join('') + '</div>' : '') +""",
"""        return '<div style="margin-top:2px"><b class="dimless">' + esc(n.name_ko) + '</b>' + (n.via ? '<span class="dim"> (' + esc(n.via) + ')</span>' : '') + ' = ' + n.groups.map(function (g) { return g.met ? esc(g.have[0]) + ' ✓' : '<span style="color:var(--text)">' + (g.god ? esc(g.god) + ' ' : '') + (g.forced ? '<b>' + esc(g.options[0]) + '</b> 유일' : esc(g.options.join('·')) + (g.more ? ' 외 ' + g.more : '') + (g.planned && g.options.length > 1 ? ' 중 하나' : '')) + '</span>'; }).join(' + ') + '</div>'; }).join('') + '</div>' : '') +""")
    # 카드 상세: 보조 선행
    s = rep(s, """        (v.support.length ? '<div style="margin-top:4px">보조: ' + esc(v.support.map(function (x) { return x.name_ko; }).join(', ')) + '</div>' : '') +""",
"""        (v.support.length ? '<div style="margin-top:4px">보조: ' + esc(v.support.map(function (x) { var af = v.support_after && v.support_after[x.id]; return x.name_ko + (af ? '(' + af.join('/') + ' 뒤)' : ''); }).join(', ')) + '</div>' : '') +""")
    # 체크리스트: 조건 행
    s = rep(s, """      box.appendChild(el('<div class="xs" style="margin-top:6px"><span class="dim">신</span> ' + godsHtml(chk.main_gods, seenSet) + '</div>'));""",
"""      (chk.cond || []).forEach(function (m) {   // 8-J: 융합 조건 중 이 빌드에서 유일한 은혜
        box.appendChild(el('<div class="chkrow' + (m.owned ? ' done' : '') + '"><span class="bx">' + (m.owned ? '☑' : '☐') + '</span><span class="ell">' + esc(m.name_ko) + '</span><span class="xs dim">' + esc(m.slot_ko) + (m.for_duo ? ' · ' + esc(m.for_duo) + ' 조건' : '') + (m.filled_by && !m.owned ? ' · 지금 ' + esc(m.filled_by) : '') + '</span></div>'));
      });
      box.appendChild(el('<div class="xs" style="margin-top:6px"><span class="dim">신</span> ' + godsHtml(chk.main_gods, seenSet) + '</div>'));""")
    s = rep(s, "      var box = el('<div class=\"chk\"><div class=\"row\"><span class=\"vstr ' + chk.strength + '\">' + chk.strength + '</span><b class=\"ell\" style=\"flex:1\">' + esc(chk.name_ko) + '</b><span class=\"xs dim\">필수 ' + chk.must_done + '/' + chk.must.length + '</span></div></div>');",
               "      var condDone = (chk.cond || []).filter(function (m) { return m.owned; }).length;\n      var box = el('<div class=\"chk\"><div class=\"row\"><span class=\"vstr ' + chk.strength + '\">' + chk.strength + '</span><b class=\"ell\" style=\"flex:1\">' + esc(chk.name_ko) + '</b><span class=\"xs dim\">필수 ' + (chk.must_done + condDone) + '/' + (chk.must.length + (chk.cond || []).length) + '</span></div></div>');")
    # needsLine: 유일 표시
    s = rep(s, "    if (un.length === 1) { var g = un[0]; return el('<div class=\"xs dim\" style=\"margin-left:8px\">남음: ' + (g.god ? esc(g.god) + ' ' : '') + esc(g.options.join(' 또는 ')) + (g.more ? ' 외 ' + g.more : '') + '</div>'); }",
               "    if (un.length === 1) { var g = un[0]; return el('<div class=\"xs dim\" style=\"margin-left:8px\">남음: ' + (g.god ? esc(g.god) + ' ' : '') + (g.forced ? '<b>' + esc(g.options[0]) + '</b> (이 빌드에선 유일)' : esc(g.options.join(' 또는 ')) + (g.more ? ' 외 ' + g.more : '')) + '</div>'); }")
    save(JS, s); print('app.js: plan 표시')
