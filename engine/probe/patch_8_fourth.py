# -*- coding: utf-8 -*-
"""8-G (페이블, 2026-10-26): 4번째 신 택1 (`variants[].fourth`).
사용자: "헤라 공격+제우스 기술 카드의 신이 헤라>제우스>아프로디테인데 불벼락엔 헤스티아가 있어야 하지 않나? 짜릿한 접촉 또는 불벼락인지 애매."
→ 풀 4명이라 둘 다는 못 간다. 주요 신은 핵심 2명, 4번째 신 후보를 `fourth: [{god, duos}]`로 — 카드 "4번째 신 (택1): 아프로디테 → 짜릿한 접촉 / 헤스티아 → 불벼락".
엔진: effectiveDirection target_duos에 fourth 융합 포함(어느 쪽이 떠도 추적), 신 등급 역할 `4번째 신 후보 · 융합`, variantView.fourth, 체크리스트 fourth(등장·진행).
UI: 카드 줄, 체크리스트 블록.
"""
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RJ = os.path.join(ROOT, 'engine', 'recommend.js'); TJ = os.path.join(ROOT, 'engine', 'test.js'); JS = os.path.join(ROOT, 'app', 'src', 'app.js'); SC = os.path.join(ROOT, 'data', 'SCHEMA.md')
def load(p): return io.open(p, encoding='utf-8').read()
def save(p, s): io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, old, new, n=1):
    c = s.count(old); assert c == n, ('anchor %d != %d: %r' % (c, n, old[:80])); return s.replace(old, new)

r = load(RJ)
if 'fourthDuos' not in r:
    r = rep(r, "  const vshort = (name) =>", "  const fourthDuos = (v) => (v.fourth || []).flatMap((f) => f.duos || []);   // 8-G: 4번째 신 택1 융합\n  const vshort = (name) =>")
    r = rep(r, "      target_duos: uniq([...(v.target_duos || []), ...fin, ...(d.target_duos || [])]),",
               "      target_duos: uniq([...(v.target_duos || []), ...fin, ...fourthDuos(v), ...(d.target_duos || [])]),")
    # 신: 4번째 신 후보
    r = rep(r, "      if ((dv.variant.main_gods || []).includes(godId)) { score += W.GOD.TARGET_GOD; bd.target_god = W.GOD.TARGET_GOD; }",
"""      if ((dv.variant.main_gods || []).includes(godId)) { score += W.GOD.TARGET_GOD; bd.target_god = W.GOD.TARGET_GOD; }
      else { const f = (dv.variant.fourth || []).find((x) => x.god === godId); if (f && !(state.gods_seen || []).includes(godId)) { score += W.GOD.TARGET_GOD; bd.target_god = W.GOD.TARGET_GOD; fourthHit = f; } }""")
    r = rep(r, "    let targetNeed = null, targetCore = false;", "    let targetNeed = null, targetCore = false, fourthHit = null;")
    r = rep(r, "    else if (dv.variant && (dv.variant.main_gods || []).includes(godId)) roles.push('빌드 신');",
"""    else if (dv.variant && (dv.variant.main_gods || []).includes(godId)) roles.push('빌드 신');
    if (fourthHit) roles.unshift(`${(dv.variant.main_gods || []).length + 1}번째 신 후보 · ${(fourthHit.duos || []).map((x) => nameOf(x)).join('/')}`);""")
    r = rep(r, "    else if (targetNeed && (targetCore || !partnerDuo)) reason = `빌드 목표 '${targetNeed.name_ko}'이(가) 여기서 나옴${targetCore ? '' : ' (교체)'}`;",
"""    else if (targetNeed && (targetCore || !partnerDuo)) reason = `빌드 목표 '${targetNeed.name_ko}'이(가) 여기서 나옴${targetCore ? '' : ' (교체)'}`;
    else if (fourthHit && !partnerDuo) reason = `빌드의 ${(dv.variant.main_gods || []).length + 1}번째 신 후보 — ${(fourthHit.duos || []).map((x) => nameOf(x)).join('/')} 쪽으로 간다`;""")
    if "fourthHit && !partnerDuo" in r and "else if (fourthHit) tier = Math.max(tier, 2);" not in r:
        r = rep(r, "    else if (targetNeed) tier = 2;", "    else if (targetNeed) tier = 2;\n    else if (fourthHit) tier = Math.max(tier, 2);")
    # 표시
    r = rep(r, """      duo_needs: uniq([...(v.target_duos || []), ...(v.finisher && v.finisher.duo ? [v.finisher.duo] : [])]).map((id) => duoNeeds(id, new Set(v.must || []))).filter(Boolean),
    };""",
"""      duo_needs: uniq([...(v.target_duos || []), ...(v.finisher && v.finisher.duo ? [v.finisher.duo] : []), ...fourthDuos(v)]).map((id) => duoNeeds(id, new Set(v.must || []))).filter(Boolean),
      fourth_nth: (v.main_gods || []).length + 1,   // 8-H: 주요 신이 2명이면 3번째, 3명이면 4번째
      fourth_both: fourthBoth(v),   // 8-H: 둘 다 가능할 때 칸 배치 ("열정 쇄도(질주) + 염화 고리(마법)")
      fourth: (v.fourth || []).map((f) => ({ god: f.god, god_ko: nameOf(f.god), duos: (f.duos || []).map((id) => ({ id, name_ko: nameOf(id), tier: (D(id) || {}).power_tier || '?' })) })),
    };""")
    r = rep(r, """      finisher: view.finisher ? { ...view.finisher, ...(dprog(view.finisher.id) || {}), needs: duoNeeds(view.finisher.id, dv.owned) } : null,""",
"""      finisher: view.finisher ? { ...view.finisher, ...(dprog(view.finisher.id) || {}), needs: duoNeeds(view.finisher.id, dv.owned) } : null,
      fourth_nth: view.fourth_nth, fourth_both: view.fourth_both,
      fourth: view.fourth.map((f) => ({ ...f, seen: seen.has(f.god), duos: f.duos.map((d) => ({ ...d, ...(dprog(d.id) || {}), needs: duoNeeds(d.id, dv.owned) })) })),""")
    save(RJ, r); print('recommend.js: fourth')

t = load(TJ)
if "sc('S47'" not in t:
    NEW = """

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
"""
    t = rep(t, "\n// ── 실행 ────────────────────────────────────────────────", NEW + "\n// ── 실행 ────────────────────────────────────────────────")
    save(TJ, t); print('test.js: S47')

s = load(JS)
if 'v.fourth' not in s:
    s = rep(s, """      (v.target_duos.length || v.finisher ? '<div class="xs" style="margin-top:3px"><span class="dim">융합</span> ' + v.target_duos.map(function (d) { return esc(d.name_ko) + '(' + d.tier + ')'; }).join(', ') +
        (v.finisher ? (v.target_duos.length ? ' <span class="dim">→</span> ' : '') + '<b>끝내기 ' + esc(v.finisher.name_ko) + '(' + v.finisher.tier + ')</b>' : '') + '</div>' : '') +""",
"""      (v.target_duos.length || v.finisher ? '<div class="xs" style="margin-top:3px"><span class="dim">융합</span> ' + v.target_duos.map(function (d) { return esc(d.name_ko) + '(' + d.tier + ')'; }).join(', ') +
        (v.finisher ? (v.target_duos.length ? ' <span class="dim">→</span> ' : '') + '<b>끝내기 ' + esc(v.finisher.name_ko) + '(' + v.finisher.tier + ')</b>' : '') + '</div>' : '') +
      (v.fourth && v.fourth.length ? '<div class="xs" style="margin-top:3px"><span class="dim">' + v.fourth_nth + '번째 신 (' + (v.fourth_both ? '먼저 뜨는 쪽' : '택1') + ')</span> ' + v.fourth.map(function (f) { return '<span style="color:' + (GC[f.god] || 'inherit') + '">' + esc(f.god_ko) + '</span> → ' + f.duos.map(function (d) { return esc(d.name_ko) + '(' + d.tier + ')'; }).join(', '); }).join(' <span class="dim">/</span> ') + (v.fourth_both ? '<div class="dim">둘 다 가면 ' + (v.fourth_nth + 1) + '번째까지 — ' + esc(v.fourth_both) + '</div>' : '') + '</div>' : '') +""")
    s = rep(s, """      var sup = chk.support.filter(function (x) { return x.owned; }).length, hm = chk.hammers.filter(function (x) { return x.owned; }).length;""",
"""      // 8-G: 4번째 신 택1 — 등장한 쪽이 있으면 그쪽만 진행 바, 아니면 후보 나열
      if (chk.fourth && chk.fourth.length) {
        var seenF = chk.fourth.filter(function (f) { return f.seen; });
        if (!seenF.length || (chk.fourth_both && seenF.length < chk.fourth.length)) box.appendChild(el('<div class="xs" style="margin-top:6px"><span class="dim">' + chk.fourth_nth + '번째 신 (' + (chk.fourth_both ? '먼저 뜨는 쪽' : '택1') + ')</span> ' + chk.fourth.map(function (f) { return '<span style="color:' + (GC[f.god] || 'inherit') + '">' + esc(f.god_ko) + '</span> → ' + f.duos.map(function (d) { return esc(d.name_ko); }).join(', '); }).join(' <span class="dim">/</span> ') + '</div>'));
        seenF.forEach(function (f) { f.duos.forEach(function (d) {
          box.appendChild(el('<div class="prog"><span class="xs ell" style="width:112px">' + esc(d.name_ko) + '</span><div class="bar"><i style="width:' + (d.owned ? 100 : Math.round(d.satisfied / d.total * 100)) + '%"></i></div><span class="xs dim">' + (d.owned ? '획득' : d.satisfied + '/' + d.total + (d.satisfied === d.total ? ' 대기' : '')) + '</span></div>'));
          if (!d.owned && d.needs) box.appendChild(needsLine(d.needs));
        }); });
      }
      var sup = chk.support.filter(function (x) { return x.owned; }).length, hm = chk.hammers.filter(function (x) { return x.owned; }).length;""")
    save(JS, s); print('app.js: 4번째 신')

sc = load(SC)
if '`fourth`' not in sc:
    sc = rep(sc, "| `main_gods` | 신 id 3개, 순서 = 중요도 |", "| `main_gods` | 신 id 2~3개, 순서 = 중요도 |\n| `fourth` | 선택. `[{god, duos}]` — 4번째 신 **택1**. 주요 신 밖의 신이 필요한 융합은 여기(스크립트가 강제). 카드 \"4번째 신 (택1): 아프로디테 → 짜릿한 접촉 / 헤스티아 → 불벼락\" |")
    save(SC, sc); print('SCHEMA.md: fourth')
