# -*- coding: utf-8 -*-
"""7단계 엔진 (페이블, 2026-10-14) — 12런 275이벤트 로그 보정.

7-A 신 풀 off-by-one: `poolSize >= CAP-1`이라 4번째 신이 매번 -4·'풀 밖 신'·등급 강등을 받았다(12런 중 4신 받은 9런 전부).
    풀은 4명이므로 4번째는 풀 안. 감점은 5번째(기념품으로 부른 신)부터. 4번째에는 역할 '마지막 새 신'만 붙인다.
7-A 대기 융합 보정: DUO_READY 8→3(+S 1), LEG_READY 8→3, 등급 '필수'→'좋음'.
    실측 — 조건이 다 찬 융합 신의 문에 들어가 바로 다음 3택에 융합이 뜬 비율 6/26 = 23%. 기대값 ≈ 0.23×(12+tier) ≈ 3.
    '필수'는 "거의 확실"로 읽히는데 4번 중 1번이다. 이유 문구에 "(실측 약 1/4)".
7-B 태그 시너지: support_boons에 없는 패시브는 전부 1점 → 칸이 다 찬 뒤 은혜 선택 16회 중 9회(56%)가 최고점 5 미만.
    보유 은혜가 부여하는 저주를 강화(curse_scale) / Ω 빌드의 Ω 발동 / 마법 핵심의 마법 강화 / 질주 핵심 / 3지역+ 보스 피해.
    NEUTRAL+CAP = 4 = 손으로 쓴 보조 4순위와 같음 — 자동 시너지가 수동 목록을 넘지 않는다.
S29·S31 개정, S38~S40 추가.
"""
import io, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RJ = os.path.join(ROOT, 'engine', 'recommend.js'); WJ = os.path.join(ROOT, 'engine', 'weights.js'); TJ = os.path.join(ROOT, 'engine', 'test.js')
def load(p): return io.open(p, encoding='utf-8').read()
def save(p, s): io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, old, new, n=1):
    c = s.count(old); assert c == n, ('anchor %d != %d: %r' % (c, n, old[:80])); return s.replace(old, new)

# ── weights ──────────────────────────────────────────────
w = load(WJ)
if 'SYNERGY' not in w:
    w = rep(w, "    NEUTRAL: 1,                 // 방향과 무관한 칸 미점유 은혜\n  },",
"""    NEUTRAL: 1,                 // 방향과 무관한 칸 미점유 은혜
    // 7-B (2026-10-14): 태그 시너지 — support_boons에 없는 패시브. 로그: 칸이 다 찬 뒤 은혜 선택 16회 중 9회(56%)가 최고점 5 미만(전부 1점)
    SYNERGY: { CURSE_SCALE: 3, CURSE_APPLY: 1.5, OMEGA: 2, CAST: 2, SPRINT: 1.5, BOSS: 1, CAP: 3 },   // NEUTRAL+CAP = 4 = SUPPORT 4순위. 자동 시너지는 손으로 쓴 보조 목록을 넘지 않는다
  },""")
    w = rep(w, "    POOL_NEW_PENALTY: -4,       // 신 풀 4명 고정은 커뮤니티에서 확인됨(dc51882, 2026-09-10). 5번째 신은 기념품으로 부른 경우만 뜬다",
               "    POOL_NEW_PENALTY: -4,       // 신 풀 4명 고정은 커뮤니티에서 확인됨(dc51882, 2026-09-10). 5번째 신은 기념품으로 부른 경우만 뜬다\n                                // 7-A: 4번째 신에 붙던 off-by-one 수정 — 12런 중 4신 받은 9런 전부에서 4번째 신이 -4·'풀 밖 신'을 받았다. 4번째는 풀 안")
    w = rep(w, """    DUO_READY: 8,               // 5-G: 조건이 다 찬 융합이 이 신의 문에서 뜰 수 있음 — 후반 문 선택의 최우선
    DUO_READY_S: 2,             //      그중 S급이면 추가
    LEG_READY: 8,               //      전설 조건 완성 — 마찬가지로 이 신 문에서만 뜸""",
"""    DUO_READY: 3,               // 5-G→7-A: 8→3. 실측 — 대기 융합 신의 문에 들어가 바로 다음 3택에 융합이 뜬 비율 6/26 = 23% (12런, 2026-10-14). 기대값 ≈ 0.23×(12+tier)
    DUO_READY_S: 1,             //      그중 S급이면 추가
    LEG_READY: 3,               //      전설 조건 완성 — 표본 0/2라 융합과 같은 값
    DUO_OFFER_RATE: 0.23,       //      이유 문구 "실측 약 1/4"의 근거. data/runs/analyze.py '대기 융합 문' 항목으로 재측정""")
    save(WJ, w); print('weights.js: SYNERGY, DUO_READY 3, POOL 주석')
else:
    print('weights.js: 이미 적용됨')

# ── recommend ────────────────────────────────────────────
r = load(RJ)
if 'synergyOf' not in r:
    # 7-A 풀 off-by-one (은혜 단계는 가중치 0이지만 같이 고친다)
    r = rep(r, "      else if (dv.poolSize >= W.GOD_POOL_CAP - 1 && W.FLAT.POOL_NEW_PENALTY) {",
               "      else if (dv.poolSize >= W.GOD_POOL_CAP && W.FLAT.POOL_NEW_PENALTY) {")
    r = rep(r, """    if (!W.NON_POOL_GODS.includes(godId)) {
      if ((state.gods_seen || []).includes(godId)) { score += W.GOD.POOL_SEEN; bd.pool = W.GOD.POOL_SEEN; }
      else if (dv.poolSize >= W.GOD_POOL_CAP - 1) { score += W.GOD.POOL_NEW_PENALTY; badges.push('새 신'); bd.pool = W.GOD.POOL_NEW_PENALTY; }
    }""",
"""    // 7-A: 풀 상한 4 = 4번째 신까지 풀 안. 감점은 5번째(기념품으로 부른 신)부터. 종전 `>= CAP-1`은 4번째 신을 매번 '풀 밖'으로 깎았다
    let lastNew = false;
    if (!W.NON_POOL_GODS.includes(godId)) {
      if ((state.gods_seen || []).includes(godId)) { score += W.GOD.POOL_SEEN; bd.pool = W.GOD.POOL_SEEN; }
      else if (dv.poolSize >= W.GOD_POOL_CAP) { score += W.GOD.POOL_NEW_PENALTY; badges.push('새 신'); bd.pool = W.GOD.POOL_NEW_PENALTY; }
      else if (dv.poolSize === W.GOD_POOL_CAP - 1) lastNew = true;   // 이 신을 받으면 풀이 닫힌다 — 감점 없이 알리기만
    }""")
    r = rep(r, "    if (poolOver) roles.push('풀 밖 신');",
               "    if (poolOver) roles.push('풀 밖 신');\n    if (lastNew) roles.push('마지막 새 신');")
    # 7-A 등급: 대기 융합·전설은 '좋음'
    r = rep(r, """    if (readyDuos.length || legReady || partnerDuo || (bestFill && bestFill.empty && bestFill.core && bestFill.rank === 1)) tier = 3;
    else if (bestFill && bestFill.empty && ((bestFill.core && bestFill.rank <= 3) || bestFill.rank === 1)) tier = 2;""",
"""    const coreFirst = !!(bestFill && bestFill.empty && bestFill.core && bestFill.rank === 1);
    if (partnerDuo || coreFirst) tier = 3;
    // 7-A: 대기 융합·전설은 '좋음' — 실측 23%(6/26)라 '필수'("거의 확실")로 읽히면 안 된다. 그래도 후반 문 사이에서는 이 값이 순위를 가른다
    else if (readyDuos.length || legReady) tier = 2;
    else if (bestFill && bestFill.empty && ((bestFill.core && bestFill.rank <= 3) || bestFill.rank === 1)) tier = 2;""")
    r = rep(r, """    else if (readyDuos.length) reason = `'${readyDuos[0].name_ko}'${readyDuos.length > 1 ? ` 외 ${readyDuos.length - 1}개` : ''} 조건 완성 — 이 문에서 뜰 수 있음`;
    else if (legReady) reason = `전설 '${legB.name_ko}' 조건 완성 — 이 문에서 뜰 수 있음`;
    else if (partnerDuo) reason = `'${partnerDuo.name_ko}' 마지막 조건을 채울 수 있음`;""",
"""    else if (partnerDuo) reason = `'${partnerDuo.name_ko}' 마지막 조건을 채울 수 있음`;
    else if (readyDuos.length && !coreFirst) reason = `'${readyDuos[0].name_ko}'${readyDuos.length > 1 ? ` 외 ${readyDuos.length - 1}개` : ''} 조건 완성 — 이 문에서 뜰 수 있음 (실측 약 1/${oneIn})`;
    else if (legReady && !coreFirst) reason = `전설 '${legB.name_ko}' 조건 완성 — 이 문에서 뜰 수 있음 (약 1/${oneIn})`;""")
    r = rep(r, """    const GRADES = ['pass', 'ok', 'good', 'must'];
    const GRADE_KO = { must: '필수', good: '좋음', ok: '보통', pass: '패스' };
    const grade = GRADES[tier];
""",
"""    const GRADES = ['pass', 'ok', 'good', 'must'];
    const GRADE_KO = { must: '필수', good: '좋음', ok: '보통', pass: '패스' };
    const grade = GRADES[tier];
    const oneIn = Math.max(2, Math.round(1 / (W.GOD.DUO_OFFER_RATE || 0.25)));
""")
    r = rep(r, """    } else if (firstInfo) reason = `첫 신으로 무난 (${firstInfo.count}개 방향 열림: ${firstInfo.names.join(', ')})`;
    else reason = '무난함';

    return { id: godId, score: round(score), reason, warnings, badges, breakdown: bd, grade, grade_ko: GRADE_KO[grade], roles, _replacing: false };""",
"""    } else if (firstInfo) reason = `첫 신으로 무난 (${firstInfo.count}개 방향 열림: ${firstInfo.names.join(', ')})`;
    else reason = '무난함';
    if (lastNew && grade !== 'must') reason += ' · 4번째 신 — 받으면 이후 새 신은 안 뜸';

    return { id: godId, score: round(score), reason, warnings, badges, breakdown: bd, grade, grade_ko: GRADE_KO[grade], roles, _replacing: false };""")

    # 7-B 태그 시너지
    r = rep(r, """  // ── §3 은혜 후보 점수 ─────────────────────────────────
  function scoreBoonEntry(state, cand, ctx) {""",
"""  // ── 7-B (2026-10-14): 태그 시너지 — support_boons에 없는 패시브를 보유 은혜·방향 성격으로 자동 채점 ──
  // 로그 12런: 칸이 다 찬 뒤 은혜 선택 16회 중 9회(56%)가 최고점 5 미만(패시브 3개가 전부 1점). 손으로 쓴 보조 목록 밖은 전부 '무난함'이었다.
  // 값은 NEUTRAL+CAP(=4)까지 — 수동 보조 4순위와 같다. 수동 목록이 있으면 그쪽이 우선(이 함수는 kind 'neutral'일 때만 호출).
  const CURSE_KO = { blitz: '암운', scorch: '잔불', froth: '침수', freeze: '동결', gust: '선풍', daze: '실명', weak: '약화', glow: '발열', hitch: '결속', wounds: '상처', charm: '현혹', marked: '표식', hangover: '숙취' };
  function synergyOf(b, d, dv, state) {
    const S = W.BOON.SYNERGY; if (!S) return { v: 0, why: [] };
    const tags = b.tags || []; let v = 0; const why = [];
    const applied = new Set(), scaled = new Set();
    for (const id of dv.owned) for (const t of (boonById.get(id) || {}).tags || []) {
      if (t.startsWith('curse_apply:')) applied.add(t.slice(12));
      else if (t.startsWith('curse_scale:')) scaled.add(t.slice(12));
    }
    for (const t of tags) {
      const c = t.slice(12);
      if (t.startsWith('curse_scale:') && applied.has(c)) { v += S.CURSE_SCALE; why.push(`${CURSE_KO[c] || c} 강화`); }
      else if (t.startsWith('curse_apply:') && scaled.has(c)) { v += S.CURSE_APPLY; why.push(`${CURSE_KO[c] || c} 부여`); }
    }
    const core = d.core_slots || [];
    if (d.omega_dependent && tags.some((t) => t === 'omega' || (t.startsWith('omega_') && core.includes(t.slice(6))))) { v += S.OMEGA; why.push('Ω 발동'); }
    if (core.includes('cast') && tags.some((t) => ['cast', 'omega_cast', 'cast_size', 'ranged_cast'].includes(t))) { v += S.CAST; why.push('마법 강화'); }
    if (core.includes('sprint') && tags.includes('sprint_damage')) { v += S.SPRINT; why.push('질주 강화'); }
    if ((state.region || 1) >= 3 && tags.includes('boss_dmg')) { v += S.BOSS; why.push('보스 피해'); }
    return { v: Math.min(v, S.CAP), why };
  }

  // ── §3 은혜 후보 점수 ─────────────────────────────────
  function scoreBoonEntry(state, cand, ctx) {""")
    r = rep(r, "    let dirDetail = null;\n    // 2-C §13-5(개정)",
               "    let dirDetail = null, synSum = 0;\n    // 2-C §13-5(개정)")
    r = rep(r, """        else { fit = W.BOON.NEUTRAL; consider({ d, weight, rank: -1, kind: 'neutral', fit }); }
      }
      dirScore += weight * fit;
    }
    bd.direction = round(dirScore);""",
"""        else {
          const syn = synergyOf(b, d, dv, state);   // 7-B
          if (syn.v > 0) { fit = W.BOON.NEUTRAL + syn.v; synSum += weight * syn.v; consider({ d, weight, rank: -1, kind: 'synergy', fit, why: syn.why }); }
          else { fit = W.BOON.NEUTRAL; consider({ d, weight, rank: -1, kind: 'neutral', fit }); }
        }
      }
      dirScore += weight * fit;
    }
    bd.direction = round(dirScore);
    if (synSum) bd.synergy = round(synSum);   // 로그용 — direction에 이미 포함된 값의 내역""")
    r = rep(r, """    else if (dirDetail && dirDetail.kind === 'support')
      reason = `'${dirDetail.d.name_ko}' 보조 ${dirDetail.rank + 1}순위${dirTag(dirDetail.d)}`;""",
"""    else if (dirDetail && dirDetail.kind === 'support')
      reason = `'${dirDetail.d.name_ko}' 보조 ${dirDetail.rank + 1}순위${dirTag(dirDetail.d)}`;
    else if (dirDetail && dirDetail.kind === 'synergy')
      reason = `'${dirDetail.d.name_ko}' 시너지: ${dirDetail.why.join(' · ')}${dirTag(dirDetail.d)}`;""")
    save(RJ, r); print('recommend.js: 7-A 풀·대기 융합, 7-B 시너지')
else:
    print('recommend.js: 이미 적용됨')

# ── test ─────────────────────────────────────────────────
t = load(TJ)
if "sc('S38'" not in t:
    t = rep(t, "sc('S29', '조건이 다 찬 융합은 그 신의 문에서 뜬다 — 제우스·포세이돈이 필수', () => {",
               "sc('S29', '조건이 다 찬 융합은 그 신의 문에서 뜬다 — 제우스·포세이돈이 좋음 (7-A: 실측 23%라 필수 아님)', () => {")
    t = rep(t, """    check("제우스 = 필수 (불벼락 S·감전 급류 A 대기)", by('zeus').grade === 'must', by('zeus').grade_ko + ' ' + by('zeus').roles.join(',')),""",
               """    check("제우스 = 좋음 (불벼락 S·감전 급류 A 대기 — 7-A: 뜰 확률 약 1/4라 필수는 아님)", by('zeus').grade === 'good', by('zeus').grade_ko + ' ' + by('zeus').roles.join(',')),""")
    t = rep(t, """    check("제우스 이유에 '이 문에서 뜰 수 있음'", /이 문에서 뜰 수 있음/.test(by('zeus').reason), by('zeus').reason),
    check("포세이돈 = 필수 (뜨거운 증기 S 대기) — 원래 '패스'였음", by('poseidon').grade === 'must', by('poseidon').grade_ko + ' ' + by('poseidon').roles.join(',')),
    check("헤스티아 = 필수 (불벼락·뜨거운 증기 대기)", by('hestia').grade === 'must', by('hestia').grade_ko),
    check('필수 3신이 헤르메스(좋음)보다 위', rows.findIndex((r) => r.id === 'hermes') > 2, rows.map((r) => r.id + ':' + r.grade_ko).join(' ')),""",
"""    check("제우스 이유에 '이 문에서 뜰 수 있음 (실측 약 1/4)'", /이 문에서 뜰 수 있음 \\(실측 약 1\\/4\\)/.test(by('zeus').reason), by('zeus').reason),
    check("포세이돈 = 좋음 (뜨거운 증기 S 대기) — 원래 '패스'였음", by('poseidon').grade === 'good', by('poseidon').grade_ko + ' ' + by('poseidon').roles.join(',')),
    check("헤스티아 = 좋음 (불벼락·뜨거운 증기 대기)", by('hestia').grade === 'good', by('hestia').grade_ko),
    check('대기 융합 3신이 데메테르·아르테미스(대기 없음)보다 위', ['demeter', 'artemis'].every((g) => rows.findIndex((r) => r.id === g) > rows.findIndex((r) => r.id === 'hestia')), rows.map((r) => r.id + ':' + r.grade_ko).join(' ')),""")
    t = rep(t, "sc('S31', '전설 진행도 — 2/3이면 사정권(좋음), 3/3이면 대기(필수)', () => {",
               "sc('S31', '전설 진행도 — 2/3이면 사정권(좋음), 3/3이면 대기(좋음, 7-A)', () => {")
    t = rep(t, "    check('3/3: 등급 필수', r2.grade === 'must', r2.grade_ko),",
               "    check('3/3: 등급 좋음 (7-A: 전설도 그 문에서 뜰 확률일 뿐)', r2.grade === 'good', r2.grade_ko),\n    check('3/3 점수 > 2/3 점수', r2.score > r1.score, r2.score + ' vs ' + r1.score),")
    NEW = """

// ── 7단계 로그 보정 (2026-10-14) ────────────────────────
sc('S38', '4번째 신은 풀 안 — 감점·강등 없이 역할 "마지막 새 신". 5번째만 풀 밖 (런 261013 n=11 재현)', () => {
  const three = S({ weapon: 'flames', aspect: 'flames_melinoe', region: 2, boons: ['zeus_ionic_gain', 'aphrodite_rapture_ring', 'hephaestus_volcanic_flourish'], hammers: ['flames_sudden_burst'], gods_seen: ['zeus', 'aphrodite', 'hephaestus'] });
  const r4 = E.recommendGods(three, ['hephaestus', 'poseidon']);
  const p4 = r4.find((r) => r.id === 'poseidon');
  const four = S({ ...three, boons: [...three.boons, 'poseidon_breaker_rush'], gods_seen: [...three.gods_seen, 'poseidon'] });
  const r5 = E.recommendGods(four, ['demeter'])[0];
  return { rows: r4, rows2: [r5], checks: [
    check('4번째 신(포세이돈)에 풀 감점 없음', p4.breakdown.pool === undefined && !p4.badges.includes('새 신'), JSON.stringify(p4.breakdown) + ' ' + p4.badges.join(',')),
    check("4번째 신 역할에 '마지막 새 신'", p4.roles.includes('마지막 새 신'), p4.roles.join(',')),
    check("4번째 신 등급 '패스' 아님 (빈 공격 칸을 파도 일격으로 채움)", p4.grade !== 'pass', p4.grade_ko + ' ' + p4.roles.join(',')),
    check("이유에 '4번째 신' 안내", /4번째 신/.test(p4.reason), p4.reason),
    check("5번째 신(데메테르)은 -4 · '풀 밖 신'", r5.breakdown.pool === W.GOD.POOL_NEW_PENALTY && r5.roles.includes('풀 밖 신'), JSON.stringify(r5.breakdown) + ' ' + r5.roles.join(',')),
  ] };
});

sc('S39', '태그 시너지 — 실명(섬광 쇄도) 보유 시 뒷불(실명 강화)이 1점짜리 둘을 이긴다 (런 261001-2133 n=16 재현)', () => {
  const st = S({ weapon: 'flames', aspect: 'flames_melinoe', region: 2, boons: ['hera_sworn_strike', 'zeus_ionic_gain', 'hera_bridal_glow', 'apollo_blinding_rush', 'hermes_hard_target', 'zeus_heaven_flourish'], hammers: ['flames_clean_coil'], gods_seen: ['hera', 'zeus', 'apollo', 'hermes'] });
  const rows = E.recommendBoons(st, ['apollo_back_burner', 'apollo_extra_dose', 'apollo_light_smite']);
  const a = A(rows);
  return { rows, checks: [
    check(...a.rankOf('apollo_back_burner', 1)),
    check(...a.reasonHas('apollo_back_burner', '시너지: 실명 강화')),
    check('뒷불 점수가 2위보다 2점 이상 높음 (원래 셋 다 1점)', rows[0].score - rows[1].score >= 2, rows.map((r) => r.id + '=' + r.score).join(' ')),
    check('breakdown.synergy 기록', rows[0].breakdown.synergy > 0, JSON.stringify(rows[0].breakdown)),
  ] };
});

sc('S40', '태그 시너지는 수동 보조 목록을 넘지 않는다 — 결속 강화(유전된 저주)는 보조 목록의 가느다란 선 아래, 1점짜리 위 (n=45 재현)', () => {
  const st = S({ weapon: 'flames', aspect: 'flames_melinoe', region: 4, boons: ['hera_sworn_strike', 'zeus_ionic_gain', 'hera_bridal_glow', 'apollo_blinding_rush', 'hermes_hard_target', 'zeus_heaven_flourish', 'zeus_storm_ring', 'zeus_power_surge', 'zeus_double_strike', 'demeter_arctic_gale', 'duo_demeter_apollo', 'demeter_steady_growth', 'duo_hera_zeus_queens_ransom', 'hermes_racing_thoughts', 'apollo_super_nova'], hammers: ['flames_clean_coil', 'flames_sudden_burst'], gods_seen: ['hera', 'zeus', 'apollo', 'hermes', 'demeter'] });
  const rows = E.recommendBoons(st, ['hera_fine_line', 'hera_hereditary_bane', 'hera_proper_upbringing']);
  const a = A(rows);
  return { rows, checks: [
    check(...a.rankOf('hera_fine_line', 1)),
    check(...a.rankOf('hera_hereditary_bane', 2)),
    check(...a.reasonHas('hera_hereditary_bane', '결속 강화')),
    check(...a.rankOf('hera_proper_upbringing', 3)),
  ] };
});
"""
    t = rep(t, "\n// ── 실행 ────────────────────────────────────────────────", NEW + "\n// ── 실행 ────────────────────────────────────────────────")
    save(TJ, t); print('test.js: S29·S31 개정, S38~S40')
else:
    print('test.js: 이미 적용됨')
