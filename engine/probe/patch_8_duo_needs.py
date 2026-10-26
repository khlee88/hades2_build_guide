# -*- coding: utf-8 -*-
"""8-F (페이블, 2026-10-26): 빌드 카드·체크리스트에 융합 **조건 은혜** 표시.
사용자: "헤라 공격+제우스 기술 카드의 필수(서약 일격·천상 기예·천부적 마력)만으로 짜릿한 접촉이 뜨나? 아프로디테에서 갑자기 뜨나?"
→ 안 뜬다. 융합은 두 신의 지정 은혜를 각각 가진 뒤 그 신 문에서만. 카드가 조건의 절반(상대 신 은혜)을 안 보여줬다.
엔진: variantView에 duo_needs(must 기준 충족/미충족 그룹 + 선택지), buildChecklist는 보유 기준으로 남은 그룹.
UI: 카드 "조건" 줄, 체크리스트 융합 행 아래 "남음: …".
"""
import io, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RJ = os.path.join(ROOT, 'engine', 'recommend.js'); TJ = os.path.join(ROOT, 'engine', 'test.js'); JS = os.path.join(ROOT, 'app', 'src', 'app.js')
def load(p): return io.open(p, encoding='utf-8').read()
def save(p, s): io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, old, new, n=1):
    c = s.count(old); assert c == n, ('anchor %d != %d: %r' % (c, n, old[:80])); return s.replace(old, new)

r = load(RJ)
if 'duoNeeds' not in r:
    r = rep(r, "  // 8-C: 빌드 카드 표시용\n  function variantView(v) {",
"""  // 8-F: 융합 조건을 "가진 것 / 아직 필요한 것"으로. ownedSet 기준. 선택지는 칸과 함께, 최대 4개
  function duoNeeds(duoId, ownedSet) {
    const D = duoById.get(duoId); if (!D) return null;
    const tokName = (t) => {
      if (t === 'cat:ring') return '아무 고리(마법)';
      if (t === 'cat:strike') return '아무 일격(공격)';
      if (t.startsWith('god:')) return `${nameOf(t.slice(4))} 은혜`;
      const b = boonById.get(t); return b ? `${b.name_ko}(${b.occupies_slot ? SLOT_KO[b.slot] : '보조'})` : t;
    };
    const godOf = (t) => { const b = boonById.get(t); return b ? b.god : (t.startsWith('god:') ? t.slice(4) : null); };
    const groups = (D.requires.all || []).map((g) => {
      const any = g.any || [];
      const have = any.filter((t) => tokenMet(t, ownedSet));
      const gods = uniq(any.map(godOf).filter(Boolean));
      return { met: have.length > 0, have: have.map(tokName), god: gods.length === 1 ? nameOf(gods[0]) : null, options: any.slice(0, 4).map(tokName), more: Math.max(0, any.length - 4) };
    });
    return { id: duoId, name_ko: D.name_ko, tier: D.power_tier, groups, met: groups.filter((g) => g.met).length, total: groups.length };
  }
  // 8-C: 빌드 카드 표시용
  function variantView(v) {""")
    r = rep(r, """      hammers: (v.hammers || []).map((id) => ({ id, name_ko: nameOf(id) })),
    };
  }""",
"""      hammers: (v.hammers || []).map((id) => ({ id, name_ko: nameOf(id) })),
      // 8-F: must만 가진 상태에서 융합 조건이 어디까지 차는가 — 카드가 "상대 신 은혜가 더 필요함"을 보이게
      duo_needs: uniq([...(v.target_duos || []), ...(v.finisher && v.finisher.duo ? [v.finisher.duo] : [])]).map((id) => duoNeeds(id, new Set(v.must || []))).filter(Boolean),
    };
  }""")
    r = rep(r, """      target_duos: view.target_duos.map((d) => ({ ...d, ...(dprog(d.id) || {}) })),
      finisher: view.finisher ? { ...view.finisher, ...(dprog(view.finisher.id) || {}) } : null,""",
"""      target_duos: view.target_duos.map((d) => ({ ...d, ...(dprog(d.id) || {}), needs: duoNeeds(d.id, dv.owned) })),
      finisher: view.finisher ? { ...view.finisher, ...(dprog(view.finisher.id) || {}), needs: duoNeeds(view.finisher.id, dv.owned) } : null,""")
    save(RJ, r); print('recommend.js: duoNeeds')

t = load(TJ)
if "sc('S46'" not in t:
    NEW = """

sc('S46', '융합 조건 표시 — 헤라 공격+제우스 기술 카드: 짜릿한 접촉은 천상 기예로 절반, 아프로디테 은혜가 더 필요', () => {
  const m = E.recommendRunStart('flames', 'flames_melinoe', { graspCap: 27 });
  const v = m.directions.find((d) => d.id === 'flames_omega_attack_spam').variants.find((x) => x.id === 'flames_hold_zeus_special');
  const spark = v.duo_needs.find((n) => n.id === 'duo_zeus_aphrodite');
  const st = E.applyChoice(S({ weapon: 'flames', aspect: 'flames_melinoe', boons: ['hera_sworn_strike', 'zeus_heaven_flourish', 'hera_born_gain'], gods_seen: ['hera', 'zeus'] }), { kind: 'variant', id: 'flames_hold_zeus_special' });
  const c = E.buildChecklist(st);
  const cs = c.target_duos.find((d) => d.id === 'duo_zeus_aphrodite');
  return { rows: v.duo_needs.map((n, i) => ({ id: n.id, rank: i + 1, score: n.met, reason: n.groups.map((g) => (g.met ? '✓' : '✗') + (g.god || '') + ':' + g.options.join('/')).join(' | '), warnings: [], badges: [] })), checks: [
    check('카드: 짜릿한 접촉 1/2 (제우스 쪽만 충족)', spark && spark.met === 1 && spark.total === 2, JSON.stringify(spark && spark.groups.map((g) => g.met))),
    check("미충족 그룹의 신 = 아프로디테, 선택지에 '황홀 고리(마법)'", spark.groups.some((g) => !g.met && g.god === '아프로디테' && g.options.some((o) => /황홀 고리\\(마법\\)/.test(o))), JSON.stringify(spark.groups.find((g) => !g.met))),
    check('체크리스트: 보유 기준으로도 1/2, 남은 쪽은 아프로디테', cs.needs.met === 1 && cs.needs.groups.find((g) => !g.met).god === '아프로디테', JSON.stringify(cs.needs)),
    check('헤라 집중 카드: 파급 효과는 필수만으로 3/3', m.directions.find((d) => d.id === 'flames_omega_attack_spam').variants.find((x) => x.id === 'flames_hold_hera').duo_needs.find((n) => n.id === 'duo_poseidon_hera').met === 3, ''),
  ] };
});
"""
    t = rep(t, "\n// ── 실행 ────────────────────────────────────────────────", NEW + "\n// ── 실행 ────────────────────────────────────────────────")
    save(TJ, t); print('test.js: S46')

s = load(JS)
if 'duo_needs' not in s:
    # 카드: 융합 줄 아래 조건
    s = rep(s, """      '<details class="xs dim" style="margin-top:4px"><summary>근거 · 메모</summary>""",
"""      (v.duo_needs && v.duo_needs.length ? '<div class="xs dim" style="margin-top:3px">' + v.duo_needs.map(function (n) {
        return '<div style="margin-top:2px"><b class="dimless">' + esc(n.name_ko) + '</b> = ' + n.groups.map(function (g) { return g.met ? esc(g.have[0]) + ' ✓' : '<span style="color:var(--text)">' + (g.god ? esc(g.god) + ' ' : '') + esc(g.options.join('·')) + (g.more ? ' 외 ' + g.more : '') + '</span>'; }).join(' + ') + '</div>'; }).join('') + '</div>' : '') +
      '<details class="xs dim" style="margin-top:4px"><summary>근거 · 메모</summary>""")
    # 체크리스트: 융합 행 아래 남은 조건
    s = rep(s, """        box.appendChild(el('<div class="prog"><span class="xs ell" style="width:112px">' + (d.fin ? '끝내기 ' : '') + esc(d.name_ko) + '</span>' +
          '<div class="bar"><i style="width:' + (d.owned ? 100 : Math.round(d.satisfied / d.total * 100)) + '%"></i></div>' +
          '<span class="xs dim">' + (d.owned ? '획득' : d.satisfied + '/' + d.total + (d.satisfied === d.total ? ' 대기' : '')) + '</span></div>'));""",
"""        box.appendChild(el('<div class="prog"><span class="xs ell" style="width:112px">' + (d.fin ? '끝내기 ' : '') + esc(d.name_ko) + '</span>' +
          '<div class="bar"><i style="width:' + (d.owned ? 100 : Math.round(d.satisfied / d.total * 100)) + '%"></i></div>' +
          '<span class="xs dim">' + (d.owned ? '획득' : d.satisfied + '/' + d.total + (d.satisfied === d.total ? ' 대기' : '')) + '</span></div>'));
        // 8-F: 남은 조건 — "어느 신의 어떤 은혜를 받아야 열리나"
        if (!d.owned && d.needs) d.needs.groups.filter(function (g) { return !g.met; }).forEach(function (g) {
          box.appendChild(el('<div class="xs dim" style="margin-left:8px">남음: ' + (g.god ? esc(g.god) + ' ' : '') + esc(g.options.join(' 또는 ')) + (g.more ? ' 외 ' + g.more : '') + '</div>'));
        });
        if (!d.owned && d.satisfied === d.total) box.appendChild(el('<div class="xs dim" style="margin-left:8px">조건 완성 — ' + esc(d.name_ko) + '의 두 신 문에서 뜰 수 있음 (약 1/4)</div>'));""")
    save(JS, s); print('app.js: 융합 조건 표시')
