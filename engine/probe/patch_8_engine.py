# -*- coding: utf-8 -*-
"""8-C 엔진 (페이블, 2026-10-26) — 빌드 카드(variant) 고정.

state.variant = 변형 id. 고정하면:
 1. 그 방향이 direction_lock(0.7/0.3)이 되고, 방향의 slot_prefs 맨 앞에 변형의 must, support 맨 앞에 변형 support, target_duos 맨 앞에 변형 융합(+끝내기)이 온다
    → 기존 채점 로직이 그대로 "이 빌드 기준"이 된다 (effectiveDirection).
 2. 은혜: must → 배지 '목표' +TARGET_MUST, support → '목표 보조' +TARGET_SUPPORT, 끝내기 융합 → 배지 '끝내기'.
 3. 신: 그 신의 must 은혜가 아직 없고 채울 수 있으면 역할 `목표 · 은혜`, 핵심 빈 칸이면 '필수', 아니면 '좋음' 이상. main_gods는 역할 '빌드 신' +TARGET_GOD.
 4. buildChecklist(state): 홈 체크리스트 — must/support/융합/끝내기/망치/신 보유 여부.
 5. recommendRunStart: 방향마다 variants (양상 필터), applyChoice({kind:'variant', id}), validateState.
"""
import io, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RJ = os.path.join(ROOT, 'engine', 'recommend.js'); WJ = os.path.join(ROOT, 'engine', 'weights.js'); TJ = os.path.join(ROOT, 'engine', 'test.js')
def load(p): return io.open(p, encoding='utf-8').read()
def save(p, s): io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, old, new, n=1):
    c = s.count(old); assert c == n, ('anchor %d != %d: %r' % (c, n, old[:80])); return s.replace(old, new)

w = load(WJ)
if 'TARGET_MUST' not in w:
    w = rep(w, "    SYNERGY: { CURSE_SCALE: 3, CURSE_APPLY: 1.5, OMEGA: 2, CAST: 2, SPRINT: 1.5, BOSS: 1, CAP: 3 },",
"""    SYNERGY: { CURSE_SCALE: 3, CURSE_APPLY: 1.5, OMEGA: 2, CAST: 2, SPRINT: 1.5, BOSS: 1, CAP: 3 },
    // 8-C (2026-10-26): 빌드 카드 고정 시 목표 은혜. must는 이미 그 방향 칸 1순위(10)가 되므로 +5는 "같은 칸 2순위(8)+5 > 1순위 10"을 보장하는 크기 — 목표가 아닌 1순위를 이긴다
    TARGET_MUST: 5,
    TARGET_SUPPORT: 2,""")
    w = rep(w, "    DUO_OFFER_RATE: 0.23,", "    DUO_OFFER_RATE: 0.23,\n    TARGET_GOD: 2,              // 8-C: 빌드 카드의 주요 신")
    save(WJ, w); print('weights.js: TARGET_*')

r = load(RJ)
if 'effectiveDirection' not in r:
    # 인덱스 + effectiveDirection
    r = rep(r, "  const keepsakeByGod = new Map();\n  for (const k of keepsakes) if (k.kind === 'god_favor' && k.god) keepsakeByGod.set(k.god, k);",
"""  const keepsakeByGod = new Map();
  for (const k of keepsakes) if (k.kind === 'god_favor' && k.god) keepsakeByGod.set(k.god, k);
  // 8-C: 빌드 카드(variant) 인덱스
  const variantById = new Map();
  for (const [wid, wd] of Object.entries(builds.weapons || {})) for (const d of wd.directions || []) for (const v of d.variants || []) variantById.set(v.id, { weapon: wid, d, v });
  const uniq = (arr) => [...new Set(arr)];
  // 변형을 고정하면 방향의 칸 순위·보조·융합 맨 앞에 변형의 것을 둔다 — 기존 채점이 그대로 "이 빌드 기준"이 된다
  const vshort = (name) => String(name || '').split(' — ')[0].slice(0, 16);   // 이유 문구용 짧은 빌드명
  function effectiveDirection(d, v) {
    const sp = {};
    for (const [slot, prefs] of Object.entries(d.slot_prefs || {})) sp[slot] = prefs.slice();
    for (const id of v.must || []) { const b = boonById.get(id); if (!b || !b.occupies_slot) continue; sp[b.slot] = uniq([id, ...(sp[b.slot] || [])]); }
    const fin = v.finisher && v.finisher.duo ? [v.finisher.duo] : [];
    return { ...d, slot_prefs: sp, support_boons: uniq([...(v.support || []), ...(v.must || []).filter((id) => { const b = boonById.get(id); return b && !b.occupies_slot; }), ...(d.support_boons || [])]),
      target_duos: uniq([...(v.target_duos || []), ...fin, ...(d.target_duos || [])]), hammers: v.hammers && v.hammers.length ? uniq([...v.hammers, ...(d.hammers || [])]) : d.hammers, _variant: v };
  }""")
    r = rep(r, """    const seen = (state.gods_seen || []).filter((g) => !W.NON_POOL_GODS.includes(g));
    return {
      owned, slotMap,
      firstGod: (state.gods_seen || [])[0] || null,
      slotBoonCount: CORE.filter((s) => slotMap[s]).length,
      poolSize: new Set(seen).size,
      dirs: (builds.weapons[state.weapon] || { directions: [], first_god_map: {} }),
    };""",
"""    const seen = (state.gods_seen || []).filter((g) => !W.NON_POOL_GODS.includes(g));
    let dirs = (builds.weapons[state.weapon] || { directions: [], first_god_map: {} });
    const vr = state.variant && variantById.get(state.variant);
    const variant = vr && vr.weapon === state.weapon ? vr : null;
    if (variant) dirs = { ...dirs, directions: (dirs.directions || []).map((d) => (d.id === variant.d.id ? effectiveDirection(d, variant.v) : d)) };
    return {
      owned, slotMap,
      firstGod: (state.gods_seen || [])[0] || null,
      slotBoonCount: CORE.filter((s) => slotMap[s]).length,
      poolSize: new Set(seen).size,
      dirs,
      variant: variant ? variant.v : null, variantDir: variant ? variant.d.id : null,
    };""")
    r = rep(r, """    let active;
    if (state.direction_lock) {
      const locked = list.find((x) => x.d.id === state.direction_lock);
      const backup = finite.find((x) => x.d.id !== state.direction_lock);""",
"""    let active;
    const lockId = state.direction_lock || dv.variantDir;   // 8-C: 빌드 카드 고정 = 방향 고정
    if (lockId) {
      const locked = list.find((x) => x.d.id === lockId);
      const backup = finite.find((x) => x.d.id !== lockId);""")
    # 은혜: 융합 후보 끝내기 배지
    r = rep(r, """      flat += W.FLAT.DUO_CANDIDATE + tier(D ? D.power_tier : '?');
      badges.push('융합');
      bd.duo_candidate = flat;
      const out = { id, score: round(flat), reason: `융합 은혜 — 무조건 최우선 (티어 ${D ? D.power_tier : '?'})`, warnings, badges, breakdown: bd };
      return out;""",
"""      flat += W.FLAT.DUO_CANDIDATE + tier(D ? D.power_tier : '?');
      badges.push('융합');
      bd.duo_candidate = flat;
      const fin = dv.variant && dv.variant.finisher && dv.variant.finisher.duo === id;   // 8-C
      if (fin) { badges.push('끝내기'); flat += W.BOON.TARGET_MUST; bd.target = W.BOON.TARGET_MUST; }
      const out = { id, score: round(flat), reason: fin ? `빌드 끝내기 — ${String(dv.variant.finisher.note || '').slice(0, 40)}` : `융합 은혜 — 무조건 최우선 (티어 ${D ? D.power_tier : '?'})`, warnings, badges, breakdown: bd };
      return out;""")
    r = rep(r, """    if ((b.tags || []).includes('beginner_safe')) { flat += W.FLAT.BEGINNER_SAFE; bd.beginner = W.FLAT.BEGINNER_SAFE; }

    const score = dirScore + flat;""",
"""    if ((b.tags || []).includes('beginner_safe')) { flat += W.FLAT.BEGINNER_SAFE; bd.beginner = W.FLAT.BEGINNER_SAFE; }
    // 8-C: 빌드 카드 목표
    let targetKind = null;
    if (dv.variant) {
      if ((dv.variant.must || []).includes(b.id)) { targetKind = 'must'; flat += W.BOON.TARGET_MUST; bd.target = W.BOON.TARGET_MUST; badges.unshift('목표'); }
      else if ((dv.variant.support || []).includes(b.id)) { targetKind = 'support'; flat += W.BOON.TARGET_SUPPORT; bd.target = W.BOON.TARGET_SUPPORT; badges.push('목표 보조'); }
    }

    const score = dirScore + flat;""")
    r = rep(r, """    if (bd.legendary) reason = '전설 은혜 — 조건을 이미 채웠음, 최우선';
    else if (completed.length) reason = `'${completed[0].name_ko}' 조건 완성 — 다음에 뜰 수 있음`;""",
"""    if (bd.legendary) reason = '전설 은혜 — 조건을 이미 채웠음, 최우선';
    else if (targetKind === 'must') reason = `빌드 '${vshort(dv.variant.name_ko)}' 필수${replacing ? ` — ${eul(nameOf(replacing))} 밀어냄` : ''}`;
    else if (completed.length) reason = `'${completed[0].name_ko}' 조건 완성 — 다음에 뜰 수 있음`;""")
    r = rep(r, """    else if (dirDetail && dirDetail.kind === 'synergy')
      reason = `'${dirDetail.d.name_ko}' 시너지: ${dirDetail.why.join(' · ')}${dirTag(dirDetail.d)}`;""",
"""    else if (dirDetail && dirDetail.kind === 'synergy')
      reason = `'${dirDetail.d.name_ko}' 시너지: ${dirDetail.why.join(' · ')}${dirTag(dirDetail.d)}`;
    else if (targetKind === 'support') reason = `빌드 '${vshort(dv.variant.name_ko)}' 보조`;""")
    # 신: 목표 은혜
    r = rep(r, """    if (state.keepsake) { const k = keepsakeById.get(state.keepsake); if (k && k.god === godId) { score += W.GOD.KEEPSAKE_MATCH; bd.keepsake = W.GOD.KEEPSAKE_MATCH; } }
""",
"""    if (state.keepsake) { const k = keepsakeById.get(state.keepsake); if (k && k.god === godId) { score += W.GOD.KEEPSAKE_MATCH; bd.keepsake = W.GOD.KEEPSAKE_MATCH; } }
    // 8-C: 빌드 카드 — 이 신의 목표 은혜가 아직 없고 채울 수 있으면
    let targetNeed = null, targetCore = false;
    if (dv.variant) {
      for (const id of dv.variant.must || []) {
        const bb = boonById.get(id); if (!bb || bb.god !== godId || dv.owned.has(id) || blockReason(bb, state, dv, 'boon')) continue;
        const empty = !bb.occupies_slot || !dv.slotMap[bb.slot];
        if (!targetNeed || (empty && !targetCore)) { targetNeed = bb; targetCore = empty; }
      }
      if ((dv.variant.main_gods || []).includes(godId)) { score += W.GOD.TARGET_GOD; bd.target_god = W.GOD.TARGET_GOD; }
    }
""")
    r = rep(r, "    if (readyDuos.length) roles.unshift(`융합 대기 · ${readyDuos[0].name_ko}${readyDuos.length > 1 ? ` 외 ${readyDuos.length - 1}` : ''}`);",
"""    if (readyDuos.length) roles.unshift(`융합 대기 · ${readyDuos[0].name_ko}${readyDuos.length > 1 ? ` 외 ${readyDuos.length - 1}` : ''}`);
    if (targetNeed) roles.unshift(`목표 · ${targetNeed.name_ko}`);
    else if (dv.variant && (dv.variant.main_gods || []).includes(godId)) roles.push('빌드 신');""")
    r = rep(r, """    const coreFirst = !!(bestFill && bestFill.empty && bestFill.core && bestFill.rank === 1);
    if (partnerDuo || coreFirst) tier = 3;""",
"""    const coreFirst = !!(bestFill && bestFill.empty && bestFill.core && bestFill.rank === 1);
    if (partnerDuo || coreFirst || (targetNeed && targetCore)) tier = 3;
    else if (targetNeed) tier = 2;""")
    r = rep(r, "    else if (partnerDuo) reason = `'${partnerDuo.name_ko}' 마지막 조건을 채울 수 있음`;",
"""    else if (targetNeed && (targetCore || !partnerDuo)) reason = `빌드 목표 '${targetNeed.name_ko}'이(가) 여기서 나옴${targetCore ? '' : ' (교체)'}`;
    else if (partnerDuo) reason = `'${partnerDuo.name_ko}' 마지막 조건을 채울 수 있음`;""")
    # 런 시작: variants
    r = rep(r, """        target_duos: (x.d.target_duos || []).slice(0, 2).map((id) => nameOf(id)),
        key_hammers: (x.d.hammers || []).slice(0, 2).map((id) => nameOf(id)),
      })),""",
"""        target_duos: (x.d.target_duos || []).slice(0, 2).map((id) => nameOf(id)),
        key_hammers: (x.d.hammers || []).slice(0, 2).map((id) => nameOf(id)),
        // 8-C: 커뮤니티 빌드 카드 (양상 전용은 그 양상에서만)
        variants: (x.d.variants || []).filter((v) => !v.aspects || v.aspects.includes(aspect)).map((v) => variantView(v)),
      })),""")
    r = rep(r, """  function recommendKeepsake(state) {""",
"""  // 8-C: 빌드 카드 표시용
  function variantView(v) {
    const D = (id) => duoById.get(id);
    return {
      id: v.id, name_ko: v.name_ko, trust: v.trust, strength: v.strength, strength_note: v.strength_note, note: v.note, aspects: v.aspects || null, sources: v.sources || [],
      main_gods: (v.main_gods || []).map((g) => ({ id: g, name_ko: nameOf(g) })),
      must: (v.must || []).map((id) => { const b = boonById.get(id); return { id, name_ko: nameOf(id), slot: b ? b.slot : null, slot_ko: b && b.occupies_slot ? SLOT_KO[b.slot] : '보조', god: b ? b.god : null }; }),
      support: (v.support || []).map((id) => ({ id, name_ko: nameOf(id), god: (boonById.get(id) || {}).god || null })),
      target_duos: (v.target_duos || []).map((id) => ({ id, name_ko: nameOf(id), tier: (D(id) || {}).power_tier || '?' })),
      finisher: v.finisher && v.finisher.duo ? { id: v.finisher.duo, name_ko: nameOf(v.finisher.duo), tier: (D(v.finisher.duo) || {}).power_tier || '?', note: v.finisher.note || '' } : null,
      hammers: (v.hammers || []).map((id) => ({ id, name_ko: nameOf(id) })),
    };
  }
  // 8-C: 홈 체크리스트 — 고정한 빌드 기준으로 무엇을 가졌고 무엇이 남았나
  function buildChecklist(state) {
    const dv = derive(state);
    if (!dv.variant) return null;
    const v = dv.variant, view = variantView(v);
    const seen = new Set(state.gods_seen || []);
    const dprog = (id) => { const D = duoById.get(id); if (!D) return null; const total = (D.requires.all || []).length; return { satisfied: total - unmetGroups(D, dv.owned).length, total, owned: dv.owned.has(id) }; };
    const must = view.must.map((m) => ({ ...m, owned: dv.owned.has(m.id), filled_by: m.slot && dv.slotMap[m.slot] && dv.slotMap[m.slot] !== m.id ? nameOf(dv.slotMap[m.slot]) : null }));
    return {
      id: v.id, name_ko: v.name_ko, strength: v.strength, trust: v.trust, direction: dv.variantDir, direction_ko: nameOf(dv.variantDir) === dv.variantDir ? ((dv.dirs.directions || []).find((d) => d.id === dv.variantDir) || {}).name_ko : nameOf(dv.variantDir),
      main_gods: view.main_gods.map((g) => ({ ...g, seen: seen.has(g.id) })),
      must, must_done: must.filter((m) => m.owned).length,
      support: view.support.map((s) => ({ ...s, owned: dv.owned.has(s.id) })),
      target_duos: view.target_duos.map((d) => ({ ...d, ...(dprog(d.id) || {}) })),
      finisher: view.finisher ? { ...view.finisher, ...(dprog(view.finisher.id) || {}) } : null,
      hammers: view.hammers.map((h) => ({ ...h, owned: dv.owned.has(h.id) })),
      note: v.note,
    };
  }

  function recommendKeepsake(state) {""")
    r = rep(r, """    } else if (choice.kind === 'keepsake') next.keepsake = choice.id;
    else if (choice.kind === 'hex') next.hex = choice.id;
    return next;""",
"""    } else if (choice.kind === 'keepsake') next.keepsake = choice.id;
    else if (choice.kind === 'hex') next.hex = choice.id;
    else if (choice.kind === 'variant') {   // 8-C: 빌드 카드 고정/해제
      const vr = choice.id && variantById.get(choice.id);
      next.variant = vr ? choice.id : null;
      next.direction_lock = vr ? vr.d.id : null;
    }
    return next;""")
    r = rep(r, """    if (state.aspect && !(weaponById.get(state.weapon) || { aspects: [] }).aspects.some((a) => a.id === state.aspect)) out.push(`무기와 맞지 않는 양상: ${state.aspect}`);
    return out;""",
"""    if (state.aspect && !(weaponById.get(state.weapon) || { aspects: [] }).aspects.some((a) => a.id === state.aspect)) out.push(`무기와 맞지 않는 양상: ${state.aspect}`);
    if (state.variant) { const vr = variantById.get(state.variant); if (!vr) out.push(`알 수 없는 빌드: ${state.variant}`); else if (vr.weapon !== state.weapon) out.push(`다른 무기의 빌드: ${vr.v.name_ko}`); }
    return out;""")
    r = rep(r, "  return { recommendRunStart, recommendArcana, recommendGods, recommendBoons, recommendHammers, recommendKeepsake, directionScores, applyChoice, validateState, _internal: { directionWeights, derive } };",
               "  return { recommendRunStart, recommendArcana, recommendGods, recommendBoons, recommendHammers, recommendKeepsake, directionScores, buildChecklist, applyChoice, validateState, _internal: { directionWeights, derive } };")
    save(RJ, r); print('recommend.js: 8-C variant')
else:
    print('recommend.js: 이미 적용됨')

t = load(TJ)
if "sc('S41'" not in t:
    NEW = """

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
"""
    t = rep(t, "\n// ── 실행 ────────────────────────────────────────────────", NEW + "\n// ── 실행 ────────────────────────────────────────────────")
    save(TJ, t); print('test.js: S41~S45')
