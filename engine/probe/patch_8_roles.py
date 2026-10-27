# -*- coding: utf-8 -*-
"""8-K (오퍼스, 2026-10-27): 빌드 카드 — 신별 역할 · 필수 대안 · 카드 기준 기념품.

사용자: "헤라는 왜 필수인가(불벼락은 제우스·헤스티아인데)" → 카드에 신 이름만 있어 역할이 안 읽혔다.
         "헤라 마력이 끝내 안 떠서 헤스티아 마력으로 갔다(티폰 클리어)" → 필수가 안 뜰 때 대안이 카드에 없었다.
1. variantView.god_roles: 주요 신(+후보 신)마다 그 신에게서 받을 필수·조건 은혜와 역할(칸 → 마력 공급/기본 딜/기술 딜/…, 융합 한쪽/조건)
2. variantView.fallbacks: 필수 칸 은혜마다 대안 2개 — 방향 칸 순위 중 이 카드 신의 것 → 그 외 이 카드 신의 같은 칸 은혜(방향 회피 제외)
3. recommendRunStart(opts.variant): 첫 기념품을 카드 기준으로 — Ω 의존이면 마력 필수의 신, 아니면 주요 신 1위. 이유는 기념품 데이터 효과 그대로("등장 확정" 문구 폐기)
4. recommendKeepsake: 카드 고정 시 아직 안 나온 신의 필수·조건 은혜를 먼저 — 조건 은혜(유일)가 우선 ("2지역에 헤스티아가 안 보이면 영원한 불씨")
"""
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RJ = os.path.join(ROOT, 'engine', 'recommend.js'); TJ = os.path.join(ROOT, 'engine', 'test.js'); JS = os.path.join(ROOT, 'app', 'src', 'app.js')
def load(p): return io.open(p, encoding='utf-8').read()
def save(p, s): io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, old, new, n=1):
    c = s.count(old); assert c == n, ('anchor %d != %d: %r' % (c, n, old[:80])); return s.replace(old, new)

r = load(RJ)
if 'godRolesOf' not in r:
    r = rep(r, "  // 8-C: 빌드 카드 표시용\n  function variantView(v) {",
"""  // 8-K: 신별 역할 — 그 신에게서 받을 필수·조건 은혜와, 칸·융합으로 본 역할
  const ROLE_OF_SLOT = { magick: '마력 공급', attack: '기본 딜', special: '기술 딜', cast: '마법', sprint: '질주' };
  function godRolesOf(v) {
    const cond = (v.plan && v.plan.cond_must) || [];
    const duoIds = uniq([...(v.target_duos || []), ...(v.finisher && v.finisher.duo ? [v.finisher.duo] : [])]);
    const gods = uniq([...(v.main_gods || []), ...(v.fourth || []).map((f) => f.god)]);
    return gods.map((g) => {
      const fourth = (v.fourth || []).find((f) => f.god === g);
      const mine = [...(v.must || []), ...cond].filter((id) => (boonById.get(id) || {}).god === g);
      const roles = [];
      for (const id of mine) { const b = boonById.get(id); const w = b.occupies_slot ? ROLE_OF_SLOT[b.slot] : '보조 핵심'; if (cond.includes(id)) continue; if (!roles.includes(w)) roles.push(w); }
      for (const did of [...duoIds, ...(fourth ? fourth.duos : [])]) {
        const D = duoById.get(did); if (!D || !(D.gods || []).includes(g)) continue;
        const byCore = mine.some((id) => !cond.includes(id) && (D.requires.all || []).some((grp) => groupMet(grp, new Set([id]))));
        roles.push(`${D.name_ko} ${byCore ? '한쪽' : '조건'}`);
      }
      return { god: g, god_ko: nameOf(g), candidate: !!fourth,
        boons: mine.map((id) => { const b = boonById.get(id); return { id, name_ko: b.name_ko, slot_ko: b.occupies_slot ? SLOT_KO[b.slot] : '보조', cond: cond.includes(id) }; }), roles };
    });
  }
  // 8-K: 필수 칸 은혜가 안 뜰 때의 대안 — 방향 칸 순위 중 이 카드 신의 것, 그다음 이 카드 신의 같은 칸 은혜
  function fallbacksOf(v, d) {
    // 8-K: 데이터(plan.fallbacks)가 있으면 그것 — 융합 배치가 성립하는 대안만 계산돼 있다
    if (v.plan && v.plan.fallbacks) { const out = {}; for (const [m, alts] of Object.entries(v.plan.fallbacks)) if (alts.length) out[m] = alts.map((x) => ({ id: x, name_ko: nameOf(x), god_ko: nameOf(boonById.get(x).god) })); else out[m] = []; return out; }
    const gods = new Set([...(v.main_gods || []), ...(v.fourth || []).map((f) => f.god)]);
    const out = {};
    for (const id of v.must || []) {
      const b = boonById.get(id); if (!b || !b.occupies_slot) continue;
      const prefs = ((d && d.slot_prefs) || {})[b.slot] || [];
      const avoid = new Set((d && d.avoid_boons) || []);
      const cand = uniq([...prefs, ...boons.filter((x) => x.slot === b.slot && x.occupies_slot).map((x) => x.id)])
        .filter((x) => x !== id && !avoid.has(x) && gods.has((boonById.get(x) || {}).god));
      if (cand.length) out[id] = cand.slice(0, 2).map((x) => ({ id: x, name_ko: nameOf(x), god_ko: nameOf(boonById.get(x).god) }));
    }
    return out;
  }
  const dirOfVariant = (vid) => { const vr = variantById.get(vid); return vr ? vr.d : null; };
  // 8-C: 빌드 카드 표시용
  function variantView(v) {""")
    r = rep(r, "      // 8-J: 융합 조건 중 이 카드에서 유일한 은혜 = 사실상 필수",
               "      god_roles: godRolesOf(v), fallbacks: fallbacksOf(v, dirOfVariant(v.id)),   // 8-K\n      // 8-J: 융합 조건 중 이 카드에서 유일한 은혜 = 사실상 필수")
    # 첫 기념품: 카드 기준 + 문구
    r = rep(r, """      for (const g of (firstKeepsake ? [] : mainGodsOf(top))) {
        const k = keepsakeByGod.get(g.id);
        if (!k || (owned && !owned.includes(k.id))) continue;
        firstKeepsake = { id: k.id, name_ko: k.name_ko, god: g.id, god_ko: g.name_ko, effect: k.effect, giver_ko: k.giver_ko,
          reason: `추천 빌드 '${top.name_ko}'의 주요 신 ${g.name_ko} — 1지역부터 등장 확정` };
        break;
      }""",
"""      // 8-K: 빌드 카드를 골랐으면 그 카드 기준 — Ω 의존 방향이면 마력 필수의 신(1지역 1순위), 아니면 주요 신 1위
      const vr = o.variant && variantById.get(o.variant);
      if (!firstKeepsake && vr && vr.weapon === weapon) {
        const v = vr.v, vd = vr.d;
        const ovv = vd.keepsake_override && keepsakeById.get(vd.keepsake_override);
        const magickMust = (v.must || []).map((id) => boonById.get(id)).find((b) => b && b.slot === 'magick');
        const pickB = vd.omega_dependent && magickMust ? magickMust : boonById.get((v.must || [])[0]);
        const g = ovv ? null : (pickB && (v.main_gods || []).includes(pickB.god) ? pickB.god : (v.main_gods || [])[0]);
        const k = ovv || (g && keepsakeByGod.get(g));
        if (k && !(owned && !owned.includes(k.id))) firstKeepsake = { id: k.id, name_ko: k.name_ko, god: k.god || null, god_ko: k.god ? nameOf(k.god) : (k.giver_ko || ''), effect: k.effect, giver_ko: k.giver_ko,
          reason: ovv ? `빌드 '${vshort(v.name_ko)}'가 지정` : `빌드 '${vshort(v.name_ko)}'의 ${nameOf(g)} — ${pickB ? `${pickB.name_ko}(${SLOT_KO[pickB.slot] || '보조'}) 먼저` : '주요 신'} · ${k.effect}` };
      }
      for (const g of (firstKeepsake ? [] : mainGodsOf(top))) {
        const k = keepsakeByGod.get(g.id);
        if (!k || (owned && !owned.includes(k.id))) continue;
        firstKeepsake = { id: k.id, name_ko: k.name_ko, god: g.id, god_ko: g.name_ko, effect: k.effect, giver_ko: k.giver_ko,
          reason: `추천 빌드 '${top.name_ko}'의 주요 신 ${g.name_ko} · ${k.effect}` };
        break;
      }""")
    # 다음 지역 기념품: 카드 고정 시
    r = rep(r, """  function recommendKeepsake(state) {
    const ctx = directionWeights(state);
    const { dv, active } = ctx;
    const main = mainOf(active);""",
"""  function recommendKeepsake(state) {
    const ctx = directionWeights(state);
    const { dv, active } = ctx;
    const main = mainOf(active);
    // 8-K: 빌드 카드 — 아직 안 나온 신의 조건(유일)·필수 은혜를 먼저. "2지역에 헤스티아가 안 보이면 영원한 불씨"
    if (dv.variant) {
      const v = dv.variant, seen = new Set(state.gods_seen || []);
      const cond = (v.plan && v.plan.cond_must) || [];
      for (const id of [...cond, ...(v.must || [])]) {
        const b = boonById.get(id); if (!b || dv.owned.has(id) || seen.has(b.god)) continue;
        const k = keepsakeByGod.get(b.god); if (!k) continue;
        const du = cond.includes(id) ? condDuoOf(v, id) : null;
        return { id: k.id, name_ko: k.name_ko, reason: `빌드 '${vshort(v.name_ko)}'의 ${b.name_ko}(${b.occupies_slot ? SLOT_KO[b.slot] : '보조'}${du ? ' · ' + nameOf(du) + ' 조건' : ''}) — ${nameOf(b.god)}이(가) 아직 안 나옴` };
      }
    }""")
    save(RJ, r); print('recommend.js: 8-K')

t = load(TJ)
if "sc('S50'" not in t:
    NEW = """

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
"""
    t = rep(t, "\n// ── 실행 ────────────────────────────────────────────────", NEW + "\n// ── 실행 ────────────────────────────────────────────────")
    save(TJ, t); print('test.js: S50·S51')

s = load(JS)
if 'god_roles' not in s:
    s = rep(s, "      '<div class=\"xs\" style=\"margin-top:4px\">' + godsHtml(v.main_gods) + '</div>' +",
"""      // 8-K: 신별 역할 — "헤라는 왜?"가 읽히게
      '<div class="xs" style="margin-top:4px">' + (v.god_roles || []).map(function (g) {
        return '<div style="margin-top:2px"><span style="color:' + (GC[g.god] || 'inherit') + ';font-weight:700">' + esc(g.god_ko) + '</span>' + (g.candidate ? '<span class="dim">(후보)</span>' : '') +
          (g.boons.length ? ' ' + g.boons.map(function (b) { return esc(b.name_ko); }).join('·') : '') + (g.roles.length ? ' <span class="dim">— ' + esc(g.roles.join(' · ')) + '</span>' : '') + '</div>'; }).join('') + '</div>' +""")
    s = rep(s, "        (v.cond_must && v.cond_must.length ? ' <span class=\"dim\">+ 융합 조건</span> ' + v.cond_must.map(function (m) { return '<b>' + esc(m.name_ko) + '</b><span class=\"dim\">(' + esc(m.slot_ko) + (m.for_duo ? ' · ' + esc(m.for_duo) : '') + ')</span>'; }).join(' · ') : '') + '</div>' +",
"""        (v.cond_must && v.cond_must.length ? ' <span class="dim">+ 융합 조건</span> ' + v.cond_must.map(function (m) { return '<b>' + esc(m.name_ko) + '</b><span class="dim">(' + esc(m.slot_ko) + (m.for_duo ? ' · ' + esc(m.for_duo) : '') + ')</span>'; }).join(' · ') : '') + '</div>' +
      // 8-K: 필수가 안 뜰 때
      (v.fallbacks && Object.keys(v.fallbacks).length ? '<div class="xs dim" style="margin-top:3px">안 뜨면 ' + v.must.filter(function (m) { return v.fallbacks[m.id]; }).map(function (m) { var al = v.fallbacks[m.id]; return esc(m.name_ko) + ' → ' + (al.length ? al.map(function (x) { return esc(x.name_ko) + '(' + esc(x.god_ko) + ')'; }).join('·') : '<span style="color:var(--text)">대안 없음 — 꼭 받는다</span>'); }).join(' / ') + '</div>' : '') +""")
    s = rep(s, "    var r = E.recommendRunStart(startSel.weapon, startSel.aspect, { graspCap: PREFS.grasp_cap, ownedKeepsakes: PREFS.owned_keepsakes.length ? PREFS.owned_keepsakes : null });",
               "    var r = E.recommendRunStart(startSel.weapon, startSel.aspect, { graspCap: PREFS.grasp_cap, ownedKeepsakes: PREFS.owned_keepsakes.length ? PREFS.owned_keepsakes : null, variant: startSel.variant });   // 8-K: 카드 기준 첫 기념품")
    save(JS, s); print('app.js: 역할·대안·기념품')
