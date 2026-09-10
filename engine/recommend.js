// engine/recommend.js — 하데스 2 빌드 추천 엔진 (2-B)
// 순수 함수. 난수 없음. 같은 입력 → 같은 출력. 외부 의존 없음.
// 설계 정본: engine/DESIGN.md / 상수: engine/weights.js

function createEngine(data, W) {
  const { boons, duos, hammers, weapons, arcana, keepsakes, hexes, builds, gods } = data;
  const CORE = W.CORE_SLOTS;
  const SLOT_KO = W.SLOT_KO;

  // ── 인덱스 ────────────────────────────────────────────
  const boonById = new Map(boons.map((b) => [b.id, b]));
  const duoById = new Map(duos.map((d) => [d.id, d]));
  const hammerById = new Map(hammers.map((h) => [h.id, h]));
  const weaponById = new Map(weapons.map((w) => [w.id, w]));
  const arcanaById = new Map(arcana.map((a) => [a.id, a]));
  const keepsakeById = new Map(keepsakes.map((k) => [k.id, k]));
  const hexById = new Map(hexes.map((h) => [h.id, h]));
  const godById = new Map(gods.map((g) => [g.id, g]));
  const boonsByGod = new Map();
  for (const b of boons) {
    if (!boonsByGod.has(b.god)) boonsByGod.set(b.god, []);
    boonsByGod.get(b.god).push(b);
  }
  const keepsakeByGod = new Map();
  for (const k of keepsakes) if (k.kind === 'god_favor' && k.god) keepsakeByGod.set(k.god, k);

  const nameOf = (id) =>
    (boonById.get(id) || duoById.get(id) || hammerById.get(id) ||
     arcanaById.get(id) || keepsakeById.get(id) || hexById.get(id) || godById.get(id) || { name_ko: id }).name_ko;
  // 2-C 한글 조사: 마지막 글자에 받침이 있으면 첫째, 없으면 둘째
  const hasFinal = (str) => { const c = (str || '').trim().slice(-1).charCodeAt(0); return c >= 0xac00 && c <= 0xd7a3 ? (c - 0xac00) % 28 !== 0 : true; };
  const josa = (str, a, b) => str + (hasFinal(str) ? a : b);
  const eul = (str) => josa(str, '을', '를');
  const gwa = (str) => josa(str, '과', '와');
  const tier = (t) => W.FLAT.DUO_TIER[t] ?? 0;
  const rankVal = (table, i) => (i < 0 ? null : table[Math.min(i, table.length - 1)]);
  const round = (n) => (Number.isFinite(n) ? Number(n.toFixed(W.SCORE_PRECISION)) : n);

  // ── 상태 파생 ─────────────────────────────────────────
  function derive(state) {
    const owned = new Set([...(state.boons || []), ...(state.hammers || [])]);
    const slotMap = {};
    for (const s of CORE) slotMap[s] = null;
    for (const id of state.boons || []) {
      const b = boonById.get(id);
      if (b && b.occupies_slot) slotMap[b.slot] = id; // 중복은 나중 것이 남는다 (validateState가 경고)
    }
    const seen = (state.gods_seen || []).filter((g) => !W.NON_POOL_GODS.includes(g));
    return {
      owned, slotMap,
      firstGod: (state.gods_seen || [])[0] || null,
      slotBoonCount: CORE.filter((s) => slotMap[s]).length,
      poolSize: new Set(seen).size,
      dirs: (builds.weapons[state.weapon] || { directions: [], first_god_map: {} }),
    };
  }

  // ── 조건 토큰 해석 ────────────────────────────────────
  function tokenMet(tok, ownedSet) {
    if (tok === 'cat:ring') {
      for (const id of ownedSet) { const b = boonById.get(id); if (b && (b.tags || []).includes('ring')) return true; }
      return false;
    }
    if (tok === 'cat:strike') {
      for (const id of ownedSet) { const b = boonById.get(id); if (b && b.slot === 'attack') return true; }
      return false;
    }
    if (tok.startsWith('god:')) {
      const g = tok.slice(4);
      for (const id of ownedSet) { const b = boonById.get(id); if (b && b.god === g) return true; }
      return false;
    }
    return ownedSet.has(tok);
  }
  const groupMet = (grp, ownedSet) => (grp.any || []).some((t) => tokenMet(t, ownedSet));
  const condMet = (cond, ownedSet) => !cond || (cond.all || []).every((g) => groupMet(g, ownedSet));
  const unmetGroups = (duo, ownedSet) => (duo.requires.all || []).filter((g) => !groupMet(g, ownedSet));

  // 융합 목록: 아직 보유하지 않은 것만
  const openDuos = (ownedSet) => duos.filter((d) => d.kind === 'duo' && !ownedSet.has(d.id));
  // 2-C §13-1: 진전/완성/손실은 "도달 가능한" 융합만 — 목표 융합이거나 관련 신이 전부 등장한 것.
  const reachable = (D, targetSet, seenSet) => targetSet.has(D.id) || (D.gods || []).every((g) => seenSet.has(g));

  // ── §2 방향 적합도 F_d ────────────────────────────────
  function directionF(state, dv, d) {
    if (d.requires_hammer && !dv.owned.has(d.requires_hammer)) return -Infinity;
    let F = W.F.BASE;
    for (const [slot, prefs] of Object.entries(d.slot_prefs || {})) {
      const filled = dv.slotMap[slot];
      if (!filled) continue;
      const i = prefs.indexOf(filled);
      if (i < 0) continue;
      const table = (d.core_slots || []).includes(slot) ? W.F.CORE_SLOT_FILLED : W.F.OTHER_SLOT_FILLED;
      F += rankVal(table, i);
    }
    for (const id of d.support_boons || []) if (dv.owned.has(id)) F += W.F.SUPPORT_OWNED;
    for (const id of d.hammers || []) if (dv.owned.has(id)) F += W.F.HAMMER_OWNED;
    if (d.requires_hammer && dv.owned.has(d.requires_hammer)) F += W.F.REQUIRES_HAMMER_OWNED;
    for (const id of d.avoid_boons || []) if (dv.owned.has(id)) F += W.F.AVOID_OWNED;
    if (state.aspect && (d.aspects || []).includes(state.aspect)) F += W.F.ASPECT_MATCH;
    if (dv.firstGod) {
      const order = dv.dirs.first_god_map[dv.firstGod] || [];
      const i = order.indexOf(d.id);
      if (i >= 0) F += rankVal(W.F.FIRST_GOD, i);
    }
    F += W.F.DIFFICULTY_PENALTY * ((d.difficulty || 1) - 1);
    return F;
  }

  // 활성 방향 + 정규화 가중치
  function directionWeights(state) {
    const dv = derive(state);
    const list = (dv.dirs.directions || []).map((d) => ({ d, F: directionF(state, dv, d) }));
    list.sort((a, b) => b.F - a.F || (a.d.id < b.d.id ? -1 : 1));
    const finite = list.filter((x) => Number.isFinite(x.F));

    let active;
    if (state.direction_lock) {
      const locked = list.find((x) => x.d.id === state.direction_lock);
      const backup = finite.find((x) => x.d.id !== state.direction_lock);
      const out = [];
      if (locked) out.push({ ...locked, weight: W.CONVERGE.LOCK_MAIN });
      if (backup) out.push({ ...backup, weight: W.CONVERGE.LOCK_BACKUP });
      return { dv, all: list, active: out };
    }
    let keep = finite.length;
    if (dv.slotBoonCount >= W.CONVERGE.STAGE_C_MIN_SLOTS) keep = W.CONVERGE.STAGE_C_KEEP;
    else if (dv.slotBoonCount >= W.CONVERGE.STAGE_B_MIN_SLOTS) keep = W.CONVERGE.STAGE_B_KEEP;
    active = finite.slice(0, keep);

    const clamped = active.map((x) => Math.max(0, x.F));
    const sum = clamped.reduce((a, b) => a + b, 0);
    const out = active.map((x, i) => ({
      ...x, weight: sum > 0 ? clamped[i] / sum : (active.length ? 1 / active.length : 0),
    }));
    return { dv, all: list, active: out };
  }

  const mainOf = (act) => (act[0] ? act[0].d : null);
  const backupOf = (act) => (act[1] ? act[1].d : null);

  // ── §3-1 선택 불가 판정 ───────────────────────────────
  // 슬롯 유래 상충(= 같은 칸 점유 은혜)은 "교체"이므로 불가가 아니다.
  function blockReason(entity, state, dv, kind) {
    if (dv.owned.has(entity.id)) return '이미 보유';
    for (const cid of entity.conflicts || []) {
      if (!dv.owned.has(cid)) continue;
      const other = boonById.get(cid);
      const slotDerived = kind === 'boon' && entity.occupies_slot && other && other.occupies_slot && other.slot === entity.slot;
      if (!slotDerived) return `상충: ${gwa(nameOf(cid))} 동시 불가`;
    }
    if (kind === 'boon' && entity.prereq && !condMet(entity.prereq, dv.owned)) return '조건 미충족';
    if (kind === 'hammer') {
      if (entity.aspect_only && entity.aspect_only !== state.aspect) return `${nameOf(entity.aspect_only)} 전용`;
      if ((entity.aspect_excluded || []).includes(state.aspect)) return '이 양상에서는 등장하지 않음';
    }
    return null;
  }

  // ── §3-2 base ────────────────────────────────────────
  function baseFit(b, d) {
    const prefs = (d.slot_prefs || {})[b.slot] || [];
    const i = prefs.indexOf(b.id);
    if (i >= 0) return rankVal(W.BOON.SLOT_PREF, i);
    return (d.core_slots || []).includes(b.slot) ? W.BOON.CORE_SLOT_OTHER : W.BOON.NON_CORE_SLOT;
  }

  // 교체로 사라지는 은혜 E가 유일하게 충족하던 미완성 융합들
  function duosBrokenBy(eId, ownedSet, targetSet, seenSet) {
    const without = new Set(ownedSet); without.delete(eId);
    const out = [];
    for (const D of openDuos(ownedSet)) {
      if (!reachable(D, targetSet, seenSet)) continue;
      const before = unmetGroups(D, ownedSet).length;
      const after = unmetGroups(D, without).length;
      if (after > before) out.push(D);
    }
    return out;
  }

  // ── §3 은혜 후보 점수 ─────────────────────────────────
  function scoreBoonEntry(state, cand, ctx) {
    const { dv, active } = ctx;
    const main = mainOf(active), backup = backupOf(active);
    const id = cand.id;
    const duoEnt = duoById.get(id);
    const b = boonById.get(id);
    const entity = b || duoEnt;
    if (!entity) return { id, score: -Infinity, reason: '알 수 없는 id', warnings: [], badges: [], breakdown: {} };

    const warnings = [], badges = [], bd = {};
    const blocked = blockReason(entity, state, dv, b ? 'boon' : 'duo');
    if (blocked) return { id, score: -Infinity, reason: blocked, warnings, badges, breakdown: {} };

    const targetsOf = (d) => new Set((d && d.target_duos) || []);
    const mainT = targetsOf(main), backT = targetsOf(backup);

    // ── 융합/전설 후보 자체
    let flat = 0;
    const rarity = cand.rarity || (b && b.slot === 'legendary' ? 'legendary' : 'common');
    if (duoEnt || rarity === 'duo') {
      const D = duoEnt || null;
      flat += W.FLAT.DUO_CANDIDATE + tier(D ? D.power_tier : '?');
      badges.push('융합');
      bd.duo_candidate = flat;
      const out = { id, score: round(flat), reason: `융합 은혜 — 무조건 최우선 (티어 ${D ? D.power_tier : '?'})`, warnings, badges, breakdown: bd };
      return out;
    }
    if (rarity === 'legendary' || b.slot === 'legendary') {
      flat += W.FLAT.LEGENDARY_CANDIDATE;
      badges.push('전설');
      bd.legendary = W.FLAT.LEGENDARY_CANDIDATE;
    }

    // ── 방향 의존 항
    let dirScore = 0;
    const replacing = b.occupies_slot ? dv.slotMap[b.slot] : null;
    const targetAll = new Set([...mainT, ...backT]);
    const seenPlus = new Set([...(state.gods_seen || []), b.god]); // 지금 보고 있는 신은 등장한 것으로 취급
    const broken = replacing ? duosBrokenBy(replacing, dv.owned, targetAll, seenPlus) : [];
    let dirDetail = null;
    // 2-C §13-5(개정): 이유는 DESIGN §3-4 원문대로 "기여 절댓값이 가장 큰 방향"에서 뽑는다.
    // 중립(neutral)은 역할 있는 방향이 하나도 없을 때만. (역할 우선 규칙은 보험 방향의 회피가
    // 메인 방향의 보조 1순위를 덮어써 1위 후보에 '비추'가 붙는 모순을 만들어 폐기 — S06)
    const consider = (cand) => {
      const contrib = Math.abs((cand.weight || 0) * (cand.fit ?? 0));
      const isNeutral = cand.kind === 'neutral';
      if (!dirDetail) { dirDetail = { ...cand, contrib }; return; }
      const curNeutral = dirDetail.kind === 'neutral';
      if (curNeutral && !isNeutral) { dirDetail = { ...cand, contrib }; return; }
      if (!curNeutral && isNeutral) return;
      if (contrib > dirDetail.contrib || (contrib === dirDetail.contrib && cand.weight > dirDetail.weight)) dirDetail = { ...cand, contrib };
    };
    for (const { d, weight } of active) {
      let fit;
      if (b.occupies_slot) {
        const prefs = (d.slot_prefs || {})[b.slot] || [];
        const myRank = prefs.indexOf(b.id);
        if ((d.avoid_boons || []).includes(b.id)) {
          // 2-C §13-2: 회피는 칸 점유 은혜에도 적용 (파도 일격·화산 일격). 교체 계산보다 우선
          fit = W.BOON.AVOID;
          consider({ d, weight, rank: -1, kind: 'avoid', fit });
        } else {
          fit = baseFit(b, d);
          if (replacing) {
            const E = boonById.get(replacing);
            fit -= baseFit(E, d) + W.BOON.REPLACE_COST;
            for (const D of broken) fit += mainT.has(D.id) || backT.has(D.id) ? W.BOON.DUO_LOSS_TARGET : W.BOON.DUO_LOSS_OTHER;
          }
          consider({ d, weight, rank: myRank, kind: myRank >= 0 ? 'slot' : 'slot_unlisted', fit });
        }
      } else {
        const si = (d.support_boons || []).indexOf(b.id);
        if (si >= 0) { fit = rankVal(W.BOON.SUPPORT, si); consider({ d, weight, rank: si, kind: 'support', fit }); }
        else if ((d.avoid_boons || []).includes(b.id)) { fit = W.BOON.AVOID; consider({ d, weight, rank: -1, kind: 'avoid', fit }); }
        else { fit = W.BOON.NEUTRAL; consider({ d, weight, rank: -1, kind: 'neutral', fit }); }
      }
      dirScore += weight * fit;
    }
    bd.direction = round(dirScore);

    if (replacing) {
      warnings.push(`${eul(nameOf(replacing))} 버리게 됨`);
      // 목표 융합을 앞으로 정렬하고 최대 2건만 이름을 보인다 (폰 화면 가독성)
      const sorted = [...broken].sort((a, b) => (mainT.has(b.id) || backT.has(b.id) ? 1 : 0) - (mainT.has(a.id) || backT.has(a.id) ? 1 : 0));
      const SHOW = 2;
      for (const D of sorted.slice(0, SHOW)) warnings.push(`진행 중 융합 '${D.name_ko}' 무효화`);
      if (sorted.length > SHOW) warnings.push(`그 외 융합 ${sorted.length - SHOW}건도 무효화`);
    }

    // ── §3-3 방향 무관 항
    if ((builds.always_take.boons || []).includes(b.id)) { flat += W.FLAT.ALWAYS_TAKE; badges.push('항상'); bd.always = W.FLAT.ALWAYS_TAKE; }

    const hasSurvival = [...dv.owned].some((x) => { const o = boonById.get(x); return o && (o.tags || []).some((t) => W.SURVIVAL_TAGS.includes(t)); });
    const survivalOn = state.hp_state === 'low' || ((state.region || 1) >= 2 && !hasSurvival);
    if (survivalOn) {
      const pi = (builds.survival_kit.passive || []).indexOf(b.id);
      let sv = 0;
      if (pi >= 0) sv += rankVal(W.FLAT.SURVIVAL_PASSIVE, pi);
      if (b.occupies_slot && ((builds.survival_kit.slot || {})[b.slot] || []).includes(b.id)) sv += W.FLAT.SURVIVAL_SLOT;
      if (sv > 0) { flat += sv; badges.push('생존'); bd.survival = sv; }
    }

    if (main && main.omega_dependent && !dv.slotMap.magick && b.slot === 'magick') {
      const mv = (state.region || 1) >= 2 ? W.FLAT.MAGICK_RULE_REGION2 : W.FLAT.MAGICK_RULE_REGION1;
      flat += mv; badges.push('마력'); bd.magick = mv;
    }

    // 융합 진전 / 완성
    // 교체가 일어나면 사라지는 은혜를 뺀 상태를 기준으로 판정해야 한다 (DESIGN §12)
    const before = new Set(dv.owned);
    if (replacing) before.delete(replacing);
    const after = new Set(before); after.add(b.id);
    let prog = 0, comp = 0; const completed = [];
    for (const D of openDuos(dv.owned)) {
      if (!reachable(D, targetAll, seenPlus)) continue;
      const beforeUnmet = unmetGroups(D, before);
      if (!beforeUnmet.length) continue;
      const afterUnmet = unmetGroups(D, after);
      if (afterUnmet.length === 0) {
        comp += mainT.has(D.id) || backT.has(D.id) ? W.FLAT.DUO_COMPLETE_TARGET : W.FLAT.DUO_COMPLETE_OTHER;
        completed.push(D);
      } else if (afterUnmet.length < beforeUnmet.length) {
        prog += mainT.has(D.id) || backT.has(D.id) ? W.FLAT.DUO_PROGRESS_TARGET : W.FLAT.DUO_PROGRESS_OTHER;
      }
    }
    prog = Math.min(prog, W.FLAT.DUO_PROGRESS_CAP);
    const TIER_ORD = { S: 0, A: 1, B: 2 };
    completed.sort((x, y) => ((targetAll.has(y.id) ? 1 : 0) - (targetAll.has(x.id) ? 1 : 0)) || ((TIER_ORD[x.power_tier] ?? 3) - (TIER_ORD[y.power_tier] ?? 3)));
    if (prog) { flat += prog; bd.duo_progress = prog; }
    if (comp) { flat += comp; badges.push('융합 임박'); bd.duo_complete = comp; }

    const rv = W.FLAT.RARITY[rarity] || 0;
    if (rv) { flat += rv; bd.rarity = rv; }

    if (!W.NON_POOL_GODS.includes(b.god)) {
      // 2-C §13-3: 은혜 단계의 신 풀 항은 가중치 0으로 꺼둠 (값이 0이면 배지도 없음)
      if ((state.gods_seen || []).includes(b.god)) { if (W.FLAT.POOL_SEEN) { flat += W.FLAT.POOL_SEEN; bd.pool = W.FLAT.POOL_SEEN; } }
      else if (dv.poolSize >= W.GOD_POOL_CAP - 1 && W.FLAT.POOL_NEW_PENALTY) { flat += W.FLAT.POOL_NEW_PENALTY; badges.push('새 신'); bd.pool = W.FLAT.POOL_NEW_PENALTY; }
    }
    if ((b.tags || []).includes('beginner_safe')) { flat += W.FLAT.BEGINNER_SAFE; bd.beginner = W.FLAT.BEGINNER_SAFE; }

    const score = dirScore + flat;

    // ── 이유 템플릿 (DESIGN.md §3-4 우선순위)
    let reason;
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
    else reason = '무난함';

    return { id, score: round(score), reason, warnings, badges, breakdown: bd, _dirRank: dirDetail ? dirDetail.rank : -1, _replacing: !!replacing };
  }

  // 동점 처리: 배지 우선순위 → 빈 칸 채우기 → id 사전순
  const BADGE_ORDER = ['융합', '전설', '융합 임박', '생존', '마력'];
  function compareEntries(a, b) {
    if (b.score !== a.score) return b.score - a.score;
    const bp = (x) => { for (let i = 0; i < BADGE_ORDER.length; i++) if (x.badges.includes(BADGE_ORDER[i])) return i; return 99; };
    if (bp(a) !== bp(b)) return bp(a) - bp(b);
    if (!!a._replacing !== !!b._replacing) return a._replacing ? 1 : -1;
    return a.id < b.id ? -1 : 1;
  }
  const ranked = (list) => { list.sort(compareEntries); return list.map((x, i) => ({ ...x, rank: i + 1 })); };

  // ── 공개 API ──────────────────────────────────────────
  function recommendBoons(state, offered) {
    const ctx = directionWeights(state);
    const list = (offered || []).map((o) => scoreBoonEntry(state, typeof o === 'string' ? { id: o } : o, ctx));
    return ranked(list);
  }

  function scoreGodEntry(state, godId, ctx) {
    const { dv, active } = ctx;
    const main = mainOf(active), backup = backupOf(active);
    const badges = [], warnings = [], bd = {};
    const g = godById.get(godId);
    if (!g) return { id: godId, score: -Infinity, reason: '알 수 없는 신', warnings, badges, breakdown: bd };

    if (godId === 'selene') {
      const v = state.hex ? W.GOD.SELENE_HAS_HEX : W.GOD.SELENE_NO_HEX;
      return { id: godId, score: round(v), reason: state.hex ? '비술 강화 (별의 길)' : '비술 확보 — 아직 없음', warnings, badges, breakdown: { fixed: v } };
    }
    if (godId === 'chaos') {
      return { id: godId, score: round(W.GOD.CHAOS), reason: '저주 내용 확인 후 결정', warnings, badges, breakdown: { fixed: W.GOD.CHAOS } };
    }

    const pool = (boonsByGod.get(godId) || []).filter((b) => !blockReason(b, state, dv, 'boon'));
    const scored = pool.map((b) => scoreBoonEntry(state, { id: b.id }, ctx)).filter((x) => Number.isFinite(x.score));
    scored.sort((a, b) => b.score - a.score);
    const topList = scored.slice(0, W.GOD.TOP_N);
    let score = topList.length ? topList.reduce((a, x) => a + x.score, 0) / topList.length : 0;
    bd.top = round(score);

    // 융합 마지막 조건 파트너
    let partner = 0; let partnerDuo = null;
    const targets = [...new Set([...((main && main.target_duos) || []), ...((backup && backup.target_duos) || [])])];
    for (const did of targets) {
      const D = duoById.get(did);
      if (!D || dv.owned.has(did)) continue;
      const unmet = unmetGroups(D, dv.owned);
      if (unmet.length !== 1) continue;
      const canFill = (unmet[0].any || []).some((t) => { const bb = boonById.get(t); return bb && bb.god === godId; });
      if (canFill && partner < W.GOD.DUO_PARTNER_CAP) { partner += W.GOD.DUO_PARTNER; if (!partnerDuo) partnerDuo = D; }
    }
    if (partner) { score += partner; bd.duo_partner = partner; }

    if (!W.NON_POOL_GODS.includes(godId)) {
      if ((state.gods_seen || []).includes(godId)) { score += W.GOD.POOL_SEEN; bd.pool = W.GOD.POOL_SEEN; }
      else if (dv.poolSize >= W.GOD_POOL_CAP - 1) { score += W.GOD.POOL_NEW_PENALTY; badges.push('새 신'); bd.pool = W.GOD.POOL_NEW_PENALTY; }
    }

    let firstInfo = null;
    if (!(state.gods_seen || []).length) {
      const order = dv.dirs.first_god_map[godId] || [];
      if (order.length) {
        // 2-C §13-7: '쉬운 길이 열리는가'가 의도 — 첫 항목만 보면 first_god_map 순서에 의존하므로 아무 방향이나 난이도 1이면 인정
        const opened = order.map((x) => (dv.dirs.directions || []).find((d) => d.id === x)).filter(Boolean);
        let fv = 0;
        if (opened.some((d) => (d.difficulty || 1) === 1)) fv += W.GOD.FIRST_EASY_DIRECTION;
        if (order.length >= 2) fv += W.GOD.FIRST_MULTI_DIRECTION;
        if (fv) { score += fv; bd.first_god = fv; }
        firstInfo = { count: order.length, names: order.map((x) => (dv.dirs.directions.find((d) => d.id === x) || {}).name_ko).filter(Boolean) };
      }
    }
    if (state.keepsake) { const k = keepsakeById.get(state.keepsake); if (k && k.god === godId) { score += W.GOD.KEEPSAKE_MATCH; bd.keepsake = W.GOD.KEEPSAKE_MATCH; } }

    let reason;
    if (partnerDuo) reason = `'${partnerDuo.name_ko}' 마지막 조건을 채울 수 있음`;
    else if (topList.length && main) {
      const t = boonById.get(topList[0].id);
      const prefs = (main.slot_prefs || {})[t && t.slot] || [];
      const i = t ? prefs.indexOf(t.id) : -1;
      if (i === 0) reason = `${dv.slotBoonCount === 0 ? '유력' : '메인'} '${main.name_ko}' ${SLOT_KO[t.slot]} 1순위 '${t.name_ko}' 기대`;
      else if (firstInfo) reason = `첫 신으로 무난 (${firstInfo.count}개 방향 열림: ${firstInfo.names.join(', ')})`;
      else if (bd.pool === W.GOD.POOL_SEEN) reason = '이미 은혜 받은 신 — 풀 집중';
      else reason = t ? `'${t.name_ko}' 등을 기대할 수 있음` : '무난함';
    } else if (firstInfo) reason = `첫 신으로 무난 (${firstInfo.count}개 방향 열림: ${firstInfo.names.join(', ')})`;
    else reason = '무난함';

    return { id: godId, score: round(score), reason, warnings, badges, breakdown: bd, _replacing: false };
  }

  function recommendGods(state, offeredGodIds) {
    const ctx = directionWeights(state);
    return ranked((offeredGodIds || []).map((g) => scoreGodEntry(state, g, ctx)));
  }

  function recommendHammers(state, offeredIds) {
    const ctx = directionWeights(state);
    const { dv, all, active } = ctx;
    const main = mainOf(active);
    const list = (offeredIds || []).map((oid) => {
      const h = hammerById.get(oid);
      const warnings = [], badges = [], bd = {};
      if (!h) return { id: oid, score: -Infinity, reason: '알 수 없는 id', warnings, badges, breakdown: bd };
      const blocked = blockReason(h, state, dv, 'hammer');
      if (blocked) return { id: oid, score: -Infinity, reason: blocked, warnings, badges, breakdown: bd };

      let fitSum = 0, detail = null;
      for (const { d, weight } of active) {
        const i = (d.hammers || []).indexOf(h.id);
        const fit = i >= 0 ? rankVal(W.HAMMER.FIT, i) : W.HAMMER.NOT_LISTED;
        fitSum += weight * fit;
        if (i >= 0 && (!detail || weight > detail.weight)) detail = { d, weight, rank: i };
      }
      bd.direction = round(fitSum);
      let score = fitSum;

      let unlock = null;
      for (const x of all) {
        if (Number.isFinite(x.F)) continue;
        if (x.d.requires_hammer === h.id) { unlock = x.d; break; }
      }
      if (unlock) { score += W.HAMMER.DIRECTION_UNLOCK; badges.push(`방향 전환: ${unlock.name_ko}`); bd.unlock = W.HAMMER.DIRECTION_UNLOCK; }

      const liveSlots = new Set([...(main ? main.core_slots || [] : []), ...CORE.filter((s) => dv.slotMap[s])]);
      if ((h.affects || []).some((a) => liveSlots.has(a) || liveSlots.has(a.replace(/^omega_/, '')))) { score += W.HAMMER.AFFECTS_MATCH; bd.affects = W.HAMMER.AFFECTS_MATCH; }

      const bp = W.HAMMER.BEGINNER_PRIORITY[h.beginner_priority] ?? 0;
      if (bp) { score += bp; bd.beginner = bp; }

      for (const cid of h.conflicts || []) {
        if (dv.owned.has(cid)) continue;
        const other = hammerById.get(cid);
        if (other && other.weapon === h.weapon && main && (main.hammers || []).includes(cid)) {
          score += W.HAMMER.BLOCKS_FUTURE; bd.blocks = (bd.blocks || 0) + W.HAMMER.BLOCKS_FUTURE;
          warnings.push(`${gwa(other.name_ko)} 이후 동시 불가`);
        }
      }

      let reason;
      if (unlock) reason = `'${unlock.name_ko}' 방향을 열어줌`;
      else if (detail) reason = `'${detail.d.name_ko}' 망치 ${detail.rank + 1}순위`;
      else if (bp > 0) reason = h.notes ? String(h.notes).slice(0, 34) : '초보에게 무난';
      else reason = '무난함';
      return { id: oid, score: round(score), reason, warnings, badges, breakdown: bd, _replacing: false };
    });
    return ranked(list);
  }

  // ── §14 아르카나 (4-A 재설계) ─────────────────────────
  // 격자 5×5. 인접 = 8방향. 각성 조건은 arcana[].awaken 구조체로 판정한다.
  const ARC_W = W.ARCANA || { CORE_BASE: 1000, CORE_DECAY: 0.5, PRIORITY: { 1: 6, 2: 3, 3: 1 }, DIRECTION_HIT: 2, DIR_WEIGHTS: [1, 0.6, 0.4], AWAKEN_LOOKAHEAD: 1.5 };
  const arcPos = (c) => (c.grid_position || [0, 0]);
  const arcAdjacent = (c) => {
    const [r, col] = arcPos(c);
    return arcana.filter((o) => { const [r2, c2] = arcPos(o); return o.id !== c.id && Math.abs(r2 - r) <= 1 && Math.abs(c2 - col) <= 1; });
  };
  function awakenMet(c, activeSet) {
    const a = c.awaken; if (!a) return false;
    const act = arcana.filter((o) => activeSet.has(o.id));
    if (a.type === 'adjacent_any') return arcAdjacent(c).some((o) => activeSet.has(o.id));
    if (a.type === 'adjacent_all') return arcAdjacent(c).every((o) => activeSet.has(o.id));
    if (a.type === 'one_each_cost') return (a.costs || []).every((k) => act.some((o) => o.grasp === k));
    if (a.type === 'max_same_cost') { const cnt = {}; for (const o of act) if (o.grasp > 0) cnt[o.grasp] = (cnt[o.grasp] || 0) + 1; return Object.values(cnt).every((n) => n <= a.max) && act.length > 0; }
    if (a.type === 'max_total') return act.length > 0 && act.length <= a.max;
    if (a.type === 'full_other_line') {
      const [r, col] = arcPos(c);
      for (let i = 1; i <= 5; i++) {
        if (i !== r && arcana.filter((o) => arcPos(o)[0] === i).every((o) => activeSet.has(o.id))) return true;
        if (i !== col && arcana.filter((o) => arcPos(o)[1] === i).every((o) => activeSet.has(o.id))) return true;
      }
      return false;
    }
    return false;
  }
  // 활성 집합에서 각성되는 0 이해도 카드를 고정점까지 추가
  function awakenClosure(activeSet) {
    const out = new Set(activeSet); let changed = true;
    while (changed) {
      changed = false;
      for (const c of arcana) if (c.grasp === 0 && !out.has(c.id) && awakenMet(c, out)) { out.add(c.id); changed = true; }
    }
    return out;
  }
  function recommendArcana(weapon, aspect, graspCap) {
    const cap = Math.max(0, graspCap ?? builds.arcana_beginner_set.grasp);
    const state = { weapon, aspect, region: 1, boons: [], hammers: [], gods_seen: [], hp_state: 'mid' };
    const { all } = directionWeights(state);
    const dirs = all.filter((x) => Number.isFinite(x.F)).map((x) => x.d);
    const set = builds.arcana_beginner_set;
    const core = set.cards || [], path = set.upgrade_path || [], never = set.never_with || [];

    // 카드 가치. 핵심 목록은 기하급수(1000, 500, 250…)라 '죽음 1장 > 나머지 전부'가 보장된다.
    // 그 외는 초보 우선순위 + 무기 방향 힌트 + 각성 이웃 보너스.
    const value = (c) => {
      if (c.grasp === 0) return -Infinity;                       // 0 이해도는 각성으로만 켜진다
      const ci = core.indexOf(c.id), pi = path.indexOf(c.id);
      let v;
      if (ci >= 0) v = ARC_W.CORE_BASE * Math.pow(ARC_W.CORE_DECAY, ci);
      else if (pi >= 0) v = ARC_W.CORE_BASE * Math.pow(ARC_W.CORE_DECAY, core.length + pi);
      else { const pr = ARC_W.PRIORITY[c.beginner_priority]; if (pr === undefined) return -Infinity; v = pr; }
      dirs.forEach((d, i) => { if ((d.arcana || []).includes(c.id)) v += ARC_W.DIRECTION_HIT * ARC_W.DIR_WEIGHTS[Math.min(i, ARC_W.DIR_WEIGHTS.length - 1)]; });
      // 이 카드가 '둘러싼 카드 중 하나' 조건의 0 이해도 카드 이웃이면 소폭 가산 (달 등)
      if (arcana.some((z) => z.grasp === 0 && z.awaken && z.awaken.type === 'adjacent_any' && arcAdjacent(z).some((n) => n.id === c.id))) v += ARC_W.AWAKEN_LOOKAHEAD;
      return v;
    };

    // 0/1 배낭: 후보 ≤ 25장, 상한 ≤ 30 → 즉시. 값이 같으면 이해도를 덜 쓰는 쪽.
    function knapsack(cands) {
      const n = cands.length;
      const best = Array.from({ length: n + 1 }, () => new Array(cap + 1).fill(0));
      for (let i = 1; i <= n; i++) {
        const c = cands[i - 1], w = c.grasp, v = c.v;
        for (let g = 0; g <= cap; g++) {
          best[i][g] = best[i - 1][g];
          if (w <= g && best[i - 1][g - w] + v > best[i][g]) best[i][g] = best[i - 1][g - w] + v;
        }
      }
      let g = 0; for (let k = 1; k <= cap; k++) if (best[n][k] > best[n][g]) g = k;
      const out = [];
      for (let i = n; i >= 1; i--) if (best[i][g] !== best[i - 1][g]) { out.push(cands[i - 1]); g -= cands[i - 1].grasp; }
      return out.reverse();
    }
    let cands = arcana.map((c) => ({ ...c, v: value(c) })).filter((c) => Number.isFinite(c.v) && c.grasp > 0 && c.grasp <= cap);
    let chosen = knapsack(cands);
    // never_with: 둘 다 뽑혔으면 가치 낮은 쪽을 제외하고 다시
    for (const pair of never) {
      const inSet = pair.filter((id) => chosen.some((c) => c.id === id));
      if (inSet.length === pair.length) {
        const drop = inSet.map((id) => chosen.find((c) => c.id === id)).sort((a, b) => a.v - b.v)[0].id;
        cands = cands.filter((c) => c.id !== drop); chosen = knapsack(cands);
      }
    }
    // 핵심 순 → 그 외 가치 순으로 정렬해 보여준다
    chosen.sort((a, b) => b.v - a.v);
    const picked = chosen.map((c) => c.id);
    const spent = chosen.reduce((a, c) => a + c.grasp, 0);
    const active = awakenClosure(new Set(picked));
    const awakened = [...active].filter((id) => !picked.includes(id));
    const inDir = (id) => dirs.some((d) => (d.arcana || []).includes(id));
    const tag = (c) => core.includes(c.id) ? '핵심' : path.includes(c.id) ? '핵심' : (inDir(c.id) ? '무기 방향' : '보조');
    const card = (c, t) => ({ id: c.id, name_ko: c.name_ko, grasp: c.grasp, effect: c.effect, tag: t });
    const lockedFree = arcana.filter((c) => c.grasp === 0 && !active.has(c.id))
      .map((c) => ({ id: c.id, name_ko: c.name_ko, effect: c.effect, awaken_condition: c.awaken_condition }));
    const nextUp = cands.filter((c) => !picked.includes(c.id)).sort((a, b) => b.v - a.v).slice(0, 2)
      .map((c) => card(c, '이해도 +' + c.grasp + ' 필요'));
    return {
      grasp_used: spent, grasp_cap: cap, grasp_left: cap - spent,
      cards: chosen.map((c) => card(c, tag(c))),
      awakened: awakened.map((id) => card(arcanaById.get(id), '각성 — 무료')),
      free_cards: lockedFree,
      next_up: nextUp,
    };
  }

  function recommendRunStart(weapon, aspect, opts) {
    const o = opts || {};
    const graspCap = o.graspCap ?? builds.arcana_beginner_set.grasp;
    const owned = o.ownedKeepsakes || null;
    const arc = recommendArcana(weapon, aspect, graspCap);
    const state = { weapon, aspect, region: 1, boons: [], hammers: [], gods_seen: [], hp_state: 'mid' };
    const { all } = directionWeights(state);
    return {
      weapon, aspect,
      arcana: arc,
      keepsakes: (builds.keepsake_plan.region1 || []).filter((k) => !owned || owned.includes(k)).map((id) => { const k = keepsakeById.get(id); return { id, name_ko: k.name_ko, effect: k.effect, giver_ko: k.giver_ko }; }),
      hexes: (builds.hex_beginner || []).map((id) => ({ id, name_ko: nameOf(id), effect: hexById.get(id).effect, mana: hexById.get(id).mana_to_charge, giver_ko: '셀레네' })),
      directions: all.filter((x) => Number.isFinite(x.F)).map((x) => ({
        id: x.d.id, name_ko: x.d.name_ko, difficulty: x.d.difficulty, F: round(x.F), summary: x.d.summary,
        core_slots: (x.d.core_slots || []).map((s) => SLOT_KO[s]),
        first_picks: (x.d.core_slots || []).map((s) => { const p = ((x.d.slot_prefs || {})[s] || [])[0]; return p ? `${SLOT_KO[s]}: ${nameOf(p)}` : null; }).filter(Boolean),
        target_duos: (x.d.target_duos || []).slice(0, 2).map((id) => nameOf(id)),
        key_hammers: (x.d.hammers || []).slice(0, 2).map((id) => nameOf(id)),
      })),
      note: '첫 신이 뜨기 전에는 방향을 고정하지 않습니다.',
    };
  }

  function recommendKeepsake(state) {
    const ctx = directionWeights(state);
    const { dv, active } = ctx;
    const main = mainOf(active);
    if (main) {
      for (const did of main.target_duos || []) {
        const D = duoById.get(did); if (!D || dv.owned.has(did)) continue;
        const unmet = unmetGroups(D, dv.owned);
        if (unmet.length !== 1) continue;
        const godsIn = new Set((unmet[0].any || []).map((t) => (boonById.get(t) || {}).god).filter(Boolean));
        if (godsIn.size === 1) {
          const g = [...godsIn][0], k = keepsakeByGod.get(g);
          if (k) return { id: k.id, name_ko: k.name_ko, reason: `'${D.name_ko}' 마지막 조건 — ${nameOf(g)} 확정 등장` };
        }
      }
      for (const s of main.core_slots || []) {
        if (dv.slotMap[s]) continue;
        const first = ((main.slot_prefs || {})[s] || [])[0];
        const bb = first && boonById.get(first);
        if (bb && !(state.gods_seen || []).includes(bb.god)) {
          const k = keepsakeByGod.get(bb.god);
          if (k) return { id: k.id, name_ko: k.name_ko, reason: `${SLOT_KO[s]} 채울 ${bb.name_ko} 노림` };
        }
      }
    }
    if ((state.region || 1) >= 4) {
      const k = (builds.keepsake_plan.boss_region || [])[0];
      if (k) return { id: k, name_ko: nameOf(k), reason: '보스 지역 — 수호자 대상 효과' };
    }
    if (state.hp_state === 'low') {
      for (const k of ['luckier_tooth', 'ghost_onion']) if (keepsakeById.get(k)) return { id: k, name_ko: nameOf(k), reason: '체력이 낮음 — 생존 우선' };
    }
    return { id: state.keepsake || null, name_ko: state.keepsake ? nameOf(state.keepsake) : null, reason: '현재 유지' };
  }

  function directionScores(state) {
    const { dv, active } = ctx0(state);
    return active.map((x, i) => ({
      id: x.d.id, name_ko: x.d.name_ko, role: i === 0 ? '메인' : i === 1 ? '보험' : '후보',
      weight: round(x.weight), F: round(x.F), difficulty: x.d.difficulty, summary: x.d.summary,
      filled: CORE.map((s) => ({ slot: s, slot_ko: SLOT_KO[s], core: (x.d.core_slots || []).includes(s), boon: dv.slotMap[s] ? nameOf(dv.slotMap[s]) : null })),
      next_wants: (x.d.core_slots || []).filter((s) => !dv.slotMap[s]).flatMap((s) => ((x.d.slot_prefs || {})[s] || []).slice(0, 3).map((id) => ({ slot_ko: SLOT_KO[s], id, name_ko: nameOf(id) }))),
      duo_progress: (x.d.target_duos || []).map((did) => { const D = duoById.get(did); if (!D) return null; const total = (D.requires.all || []).length; return { id: did, name_ko: D.name_ko, tier: D.power_tier, satisfied: total - unmetGroups(D, dv.owned).length, total, owned: dv.owned.has(did) }; }).filter(Boolean),
    }));
  }
  const ctx0 = (state) => directionWeights(state);

  function applyChoice(state, choice) {
    const next = JSON.parse(JSON.stringify(state));
    next.boons = next.boons || []; next.hammers = next.hammers || []; next.gods_seen = next.gods_seen || [];
    if (choice.kind === 'boon') {
      const b = boonById.get(choice.id) || duoById.get(choice.id);
      if (b && b.occupies_slot) next.boons = next.boons.filter((id) => { const o = boonById.get(id); return !(o && o.occupies_slot && o.slot === b.slot); });
      if (!next.boons.includes(choice.id)) next.boons.push(choice.id);
      const god = (boonById.get(choice.id) || {}).god;
      if (god && !next.gods_seen.includes(god)) next.gods_seen.push(god);
      for (const g of (duoById.get(choice.id) || {}).gods || []) if (!next.gods_seen.includes(g)) next.gods_seen.push(g);
    } else if (choice.kind === 'hammer') {
      if (!next.hammers.includes(choice.id)) next.hammers.push(choice.id);
    } else if (choice.kind === 'god') {
      if (!next.gods_seen.includes(choice.id)) next.gods_seen.push(choice.id);
    } else if (choice.kind === 'keepsake') next.keepsake = choice.id;
    else if (choice.kind === 'hex') next.hex = choice.id;
    return next;
  }

  function validateState(state) {
    const out = [];
    const seenSlot = {};
    for (const id of state.boons || []) {
      const b = boonById.get(id);
      if (!b) { out.push(`알 수 없는 은혜 id: ${id}`); continue; }
      if (!b.occupies_slot) continue;
      if (seenSlot[b.slot]) out.push(`${SLOT_KO[b.slot]} 칸에 은혜가 2개: ${nameOf(seenSlot[b.slot])} / ${b.name_ko}`);
      else seenSlot[b.slot] = id;
    }
    for (const id of state.hammers || []) {
      const h = hammerById.get(id);
      if (!h) { out.push(`알 수 없는 망치 id: ${id}`); continue; }
      if (h.weapon !== state.weapon) out.push(`다른 무기의 망치: ${h.name_ko}`);
    }
    if (state.weapon && !weaponById.has(state.weapon)) out.push(`알 수 없는 무기: ${state.weapon}`);
    if (state.aspect && !(weaponById.get(state.weapon) || { aspects: [] }).aspects.some((a) => a.id === state.aspect)) out.push(`무기와 맞지 않는 양상: ${state.aspect}`);
    return out;
  }

  return { recommendRunStart, recommendArcana, recommendGods, recommendBoons, recommendHammers, recommendKeepsake, directionScores, applyChoice, validateState, _internal: { directionWeights, derive } };
}

if (typeof module !== 'undefined' && module.exports) module.exports = { createEngine };
if (typeof window !== 'undefined') window.createHadesEngine = createEngine;
