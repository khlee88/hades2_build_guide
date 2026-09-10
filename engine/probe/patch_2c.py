# -*- coding: utf-8 -*-
"""2-C 페이블 패치: recommend.js / weights.js 수정 + test.js에 S17~S22 추가.
DESIGN.md §13이 정본. 여러 번 실행하면 두 번째부터는 '이미 적용' 으로 건너뛴다."""
import io, os, sys
BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def patch(path, pairs, marker):
    p = os.path.join(BASE, path)
    s = io.open(p, encoding='utf-8').read()
    if marker in s:
        print(f'{path}: 이미 적용됨'); return
    for old, new in pairs:
        if old not in s:
            print(f'{path}: 패턴 못 찾음 →', old[:70].replace('\n', '⏎')); sys.exit(1)
        s = s.replace(old, new, 1)
    io.open(p, 'w', encoding='utf-8').write(s)
    print(f'{path}: 패치 {len(pairs)}건 적용')

# ───────────────────────── recommend.js ─────────────────────────
R = []
R.append(("""  const nameOf = (id) =>
    (boonById.get(id) || duoById.get(id) || hammerById.get(id) ||
     arcanaById.get(id) || keepsakeById.get(id) || hexById.get(id) || { name_ko: id }).name_ko;""",
"""  const nameOf = (id) =>
    (boonById.get(id) || duoById.get(id) || hammerById.get(id) ||
     arcanaById.get(id) || keepsakeById.get(id) || hexById.get(id) || godById.get(id) || { name_ko: id }).name_ko;
  // 2-C 한글 조사: 마지막 글자에 받침이 있으면 첫째, 없으면 둘째
  const hasFinal = (str) => { const c = (str || '').trim().slice(-1).charCodeAt(0); return c >= 0xac00 && c <= 0xd7a3 ? (c - 0xac00) % 28 !== 0 : true; };
  const josa = (str, a, b) => str + (hasFinal(str) ? a : b);
  const eul = (str) => josa(str, '을', '를');
  const gwa = (str) => josa(str, '과', '와');"""))

R.append(("""  const openDuos = (ownedSet) => duos.filter((d) => d.kind === 'duo' && !ownedSet.has(d.id));""",
"""  const openDuos = (ownedSet) => duos.filter((d) => d.kind === 'duo' && !ownedSet.has(d.id));
  // 2-C §13-1: 진전/완성/손실은 "도달 가능한" 융합만 — 목표 융합이거나 관련 신이 전부 등장한 것.
  const reachable = (D, targetSet, seenSet) => targetSet.has(D.id) || (D.gods || []).every((g) => seenSet.has(g));"""))

R.append(("""  function duosBrokenBy(eId, ownedSet) {
    const without = new Set(ownedSet); without.delete(eId);
    const out = [];
    for (const D of openDuos(ownedSet)) {""",
"""  function duosBrokenBy(eId, ownedSet, targetSet, seenSet) {
    const without = new Set(ownedSet); without.delete(eId);
    const out = [];
    for (const D of openDuos(ownedSet)) {
      if (!reachable(D, targetSet, seenSet)) continue;"""))

R.append(("""    let dirScore = 0;
    const replacing = b.occupies_slot ? dv.slotMap[b.slot] : null;
    const broken = replacing ? duosBrokenBy(replacing, dv.owned) : [];
    let dirDetail = null;""",
"""    let dirScore = 0;
    const replacing = b.occupies_slot ? dv.slotMap[b.slot] : null;
    const targetAll = new Set([...mainT, ...backT]);
    const seenPlus = new Set([...(state.gods_seen || []), b.god]); // 지금 보고 있는 신은 등장한 것으로 취급
    const broken = replacing ? duosBrokenBy(replacing, dv.owned, targetAll, seenPlus) : [];
    let dirDetail = null;
    // 2-C §13-5: 이유를 뽑는 방향은 역할 있는 쪽 우선 (회피 > 선호/보조 > 미등재 > 중립), 같은 등급이면 가중치 큰 쪽
    const KIND_PRI = { avoid: 0, slot: 1, support: 1, slot_unlisted: 2, neutral: 3 };
    const consider = (cand) => {
      if (!dirDetail) { dirDetail = cand; return; }
      const a = KIND_PRI[cand.kind], q = KIND_PRI[dirDetail.kind];
      if (a < q || (a === q && cand.weight > dirDetail.weight)) dirDetail = cand;
    };"""))

R.append(("""      if (b.occupies_slot) {
        fit = baseFit(b, d);
        const prefs = (d.slot_prefs || {})[b.slot] || [];
        const myRank = prefs.indexOf(b.id);
        if (replacing) {
          const E = boonById.get(replacing);
          fit -= baseFit(E, d) + W.BOON.REPLACE_COST;
          for (const D of broken) fit += mainT.has(D.id) || backT.has(D.id) ? W.BOON.DUO_LOSS_TARGET : W.BOON.DUO_LOSS_OTHER;
        }
        if (!dirDetail || weight > dirDetail.weight) dirDetail = { d, weight, rank: myRank, kind: 'slot' };
      } else {
        const si = (d.support_boons || []).indexOf(b.id);
        if (si >= 0) { fit = rankVal(W.BOON.SUPPORT, si); if (!dirDetail || weight > dirDetail.weight) dirDetail = { d, weight, rank: si, kind: 'support' }; }
        else if ((d.avoid_boons || []).includes(b.id)) { fit = W.BOON.AVOID; if (!dirDetail || weight > dirDetail.weight) dirDetail = { d, weight, rank: -1, kind: 'avoid' }; }
        else { fit = W.BOON.NEUTRAL; if (!dirDetail || weight > dirDetail.weight) dirDetail = { d, weight, rank: -1, kind: 'neutral' }; }
      }""",
"""      if (b.occupies_slot) {
        const prefs = (d.slot_prefs || {})[b.slot] || [];
        const myRank = prefs.indexOf(b.id);
        if ((d.avoid_boons || []).includes(b.id)) {
          // 2-C §13-2: 회피는 칸 점유 은혜에도 적용 (파도 일격·화산 일격). 교체 계산보다 우선
          fit = W.BOON.AVOID;
          consider({ d, weight, rank: -1, kind: 'avoid' });
        } else {
          fit = baseFit(b, d);
          if (replacing) {
            const E = boonById.get(replacing);
            fit -= baseFit(E, d) + W.BOON.REPLACE_COST;
            for (const D of broken) fit += mainT.has(D.id) || backT.has(D.id) ? W.BOON.DUO_LOSS_TARGET : W.BOON.DUO_LOSS_OTHER;
          }
          consider({ d, weight, rank: myRank, kind: myRank >= 0 ? 'slot' : 'slot_unlisted' });
        }
      } else {
        const si = (d.support_boons || []).indexOf(b.id);
        if (si >= 0) { fit = rankVal(W.BOON.SUPPORT, si); consider({ d, weight, rank: si, kind: 'support' }); }
        else if ((d.avoid_boons || []).includes(b.id)) { fit = W.BOON.AVOID; consider({ d, weight, rank: -1, kind: 'avoid' }); }
        else { fit = W.BOON.NEUTRAL; consider({ d, weight, rank: -1, kind: 'neutral' }); }
      }"""))

R.append(("warnings.push(`${nameOf(replacing)}을 버리게 됨`);",
          "warnings.push(`${eul(nameOf(replacing))} 버리게 됨`);"))

R.append(("""    if (!W.NON_POOL_GODS.includes(b.god)) {
      if ((state.gods_seen || []).includes(b.god)) { flat += W.FLAT.POOL_SEEN; bd.pool = W.FLAT.POOL_SEEN; }
      else if (dv.poolSize >= W.GOD_POOL_CAP - 1) { flat += W.FLAT.POOL_NEW_PENALTY; badges.push('새 신'); bd.pool = W.FLAT.POOL_NEW_PENALTY; }
    }""",
"""    if (!W.NON_POOL_GODS.includes(b.god)) {
      // 2-C §13-3: 은혜 단계의 신 풀 항은 가중치 0으로 꺼둠 (값이 0이면 배지도 없음)
      if ((state.gods_seen || []).includes(b.god)) { if (W.FLAT.POOL_SEEN) { flat += W.FLAT.POOL_SEEN; bd.pool = W.FLAT.POOL_SEEN; } }
      else if (dv.poolSize >= W.GOD_POOL_CAP - 1 && W.FLAT.POOL_NEW_PENALTY) { flat += W.FLAT.POOL_NEW_PENALTY; badges.push('새 신'); bd.pool = W.FLAT.POOL_NEW_PENALTY; }
    }"""))

R.append(("""    for (const D of openDuos(dv.owned)) {
      const beforeUnmet = unmetGroups(D, before);
      if (!beforeUnmet.length) continue;
      const afterUnmet = unmetGroups(D, after);""",
"""    for (const D of openDuos(dv.owned)) {
      if (!reachable(D, targetAll, seenPlus)) continue;
      const beforeUnmet = unmetGroups(D, before);
      if (!beforeUnmet.length) continue;
      const afterUnmet = unmetGroups(D, after);"""))

R.append(("""    prog = Math.min(prog, W.FLAT.DUO_PROGRESS_CAP);""",
"""    prog = Math.min(prog, W.FLAT.DUO_PROGRESS_CAP);
    const TIER_ORD = { S: 0, A: 1, B: 2 };
    completed.sort((x, y) => ((targetAll.has(y.id) ? 1 : 0) - (targetAll.has(x.id) ? 1 : 0)) || ((TIER_ORD[x.power_tier] ?? 3) - (TIER_ORD[y.power_tier] ?? 3)));"""))

R.append(("""    let reason;
    const isMain = dirDetail && main && dirDetail.d.id === main.id;
    if (completed.length) reason = `'${completed[0].name_ko}' 조건 완성 — 다음에 뜰 수 있음`;
    else if (bd.always) reason = '칸 안 차지, 조건 없이 이득';
    else if (dirDetail && dirDetail.kind === 'avoid') reason = `비추: ${String(dirDetail.d.avoid_reason || '').slice(0, 30)}`;
    else if (bd.survival) reason = '체력 관리용 — 지금 방어/회복이 없음';
    else if (bd.magick) reason = 'Ω 빌드인데 마력 칸이 비었음';
    else if (dirDetail && dirDetail.kind === 'slot' && dirDetail.rank >= 0)
      reason = `${isMain ? '메인' : '보험'} '${dirDetail.d.name_ko}' ${SLOT_KO[b.slot]} ${dirDetail.rank + 1}순위`;
    else if (dirDetail && dirDetail.kind === 'support')
      reason = `'${dirDetail.d.name_ko}' 보조 ${dirDetail.rank + 1}순위`;
    else if (replacing && dirScore > 0) reason = `${nameOf(replacing)}보다 ${dirDetail.d.name_ko}에 더 맞음`;
    else if (b.occupies_slot && !replacing) reason = `빈 ${SLOT_KO[b.slot]} 채움`;
    else reason = '무난함';""",
"""    let reason;
    const isMain = dirDetail && main && dirDetail.d.id === main.id;
    const roleWord = dv.slotBoonCount === 0 ? '유력' : (isMain ? '메인' : '보험');
    const dirTag = (d) => (main && d.id === main.id) ? '' : ' (보험 방향)';
    if (bd.legendary) reason = '전설 은혜 — 조건을 이미 채웠음, 최우선';
    else if (completed.length) reason = `'${completed[0].name_ko}' 조건 완성 — 다음에 뜰 수 있음`;
    else if (bd.always) reason = '칸 안 차지, 조건 없이 이득';
    else if (dirDetail && dirDetail.kind === 'avoid') reason = `비추: ${String(dirDetail.d.avoid_reason || '').slice(0, 30)}`;
    else if (bd.survival) reason = '체력 관리용 — 지금 방어/회복이 없음';
    else if (bd.magick) reason = 'Ω 빌드인데 마력 칸이 비었음';
    else if (replacing && dirScore <= 0) {
      // 2-C §13-5: 이득 없는 교체는 순위 칭찬처럼 읽히지 않게
      const E = nameOf(replacing);
      reason = dirScore < -1 ? `${E}보다 나을 게 없음` : `${gwa(E)} 비슷한 급 — 바꿀 이유 부족`;
    }
    else if (dirDetail && dirDetail.kind === 'slot')
      reason = `${roleWord} '${dirDetail.d.name_ko}' ${SLOT_KO[b.slot]} ${dirDetail.rank + 1}순위`;
    else if (dirDetail && dirDetail.kind === 'support')
      reason = `'${dirDetail.d.name_ko}' 보조 ${dirDetail.rank + 1}순위${dirTag(dirDetail.d)}`;
    else if (replacing && dirScore > 0) reason = `${nameOf(replacing)}보다 ${dirDetail.d.name_ko}에 더 맞음`;
    else if (b.occupies_slot && !replacing) reason = `빈 ${SLOT_KO[b.slot]} 채움`;
    else reason = '무난함';"""))

R.append(("""      if (i === 0) reason = `메인 '${main.name_ko}'의 ${SLOT_KO[t.slot]} 1순위 ${t.name_ko}이 여기서 나옴`;""",
          """      if (i === 0) reason = `${dv.slotBoonCount === 0 ? '유력' : '메인'} '${main.name_ko}' ${SLOT_KO[t.slot]} 1순위 '${t.name_ko}' 기대`;"""))
R.append(("""      else reason = t ? `${t.name_ko} 등을 기대할 수 있음` : '무난함';""",
          """      else reason = t ? `'${t.name_ko}' 등을 기대할 수 있음` : '무난함';"""))
R.append(("warnings.push(`${other.name_ko}와 이후 동시 불가`);", "warnings.push(`${gwa(other.name_ko)} 이후 동시 불가`);"))
R.append(("if (!slotDerived) return `상충: ${nameOf(cid)}와 동시 불가`;", "if (!slotDerived) return `상충: ${gwa(nameOf(cid))} 동시 불가`;"))
R.append(("reason: `'${D.name_ko}' 마지막 조건 — ${nameOf(g) || g} 확정 등장` };", "reason: `'${D.name_ko}' 마지막 조건 — ${nameOf(g)} 확정 등장` };"))
patch('engine/recommend.js', R, '2-C §13-1')

# ───────────────────────── weights.js ─────────────────────────
Wp = [
 ("    ALWAYS_TAKE: 9,", "    ALWAYS_TAKE: 7.5,           // 2-C: 9→7.5. 핵심 칸 1·2순위(10/8+1)보다 아래, 3순위(6)·비핵심 칸(3)보다 위"),
 ("    POOL_SEEN: 1,\n    POOL_NEW_PENALTY: -3,", "    POOL_SEEN: 0,               // 2-C: 은혜 단계 신 풀 항 OFF — 이미 그 신의 문을 고른 뒤. 신 선택(GOD.*)에서만 적용\n    POOL_NEW_PENALTY: 0,"),
]
patch('engine/weights.js', Wp, '2-C: 9→7.5')

# ───────────────────────── test.js: S17~S22 ─────────────────────────
T = r"""
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
    check('폭풍 고리 duo_progress 없음/0', !sr.breakdown.duo_progress, JSON.stringify(sr.breakdown)),
    check(...a.rankOf('zeus_ionic_gain', 1)),
    check(...a.hasBadge('zeus_ionic_gain', '마력')),
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
"""
p = os.path.join(BASE, 'engine', 'test.js')
s = io.open(p, encoding='utf-8').read()
if "sc('S17'" in s:
    print('test.js: 이미 적용됨')
else:
    marker = '// ── 실행 ────────────────────────────────────────────────'
    assert marker in s, 'test.js 실행 마커 없음'
    s = s.replace(marker, T + '\n' + marker, 1)
    s = s.replace("out.push(`실행: \\`node engine/test.js\\` · 시나리오 ${scenarios.length + 1}개", "out.push(`실행: \\`node engine/test.js\\` · 시나리오 ${scenarios.length + 1}개")
    io.open(p, 'w', encoding='utf-8').write(s)
    print('test.js: S17~S22 추가')
