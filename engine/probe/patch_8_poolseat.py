# -*- coding: utf-8 -*-
"""8-M (오퍼스, 2026-10-27): 빌드 카드 — 신 풀 자리 예약.

사용자: "어제 데메테르가 3번째로 떠서 위험했다. 4번째로 헤스티아를 갔다."
시뮬레이션: 헤라·제우스 뒤 데메테르 '좋음'(경고 없음), 데메테르 뒤 아폴론도 '좋음' — 아폴론을 받으면 풀이 닫혀 헤스티아가 안 나오고 불벼락 불가.
규칙 (카드 고정 시):
  need = 아직 안 나온 주요 신 수 + (후보 신이 있고 하나도 안 나왔으면 1)
  free = 풀 상한 − 지금 풀 크기
  카드 밖 새 신 G: 받으면 free−1.
    free−1 < need  → '빌드 막힘' 등급 패스, 이유 "받으면 풀이 차서 ○○이(가) 더 안 나옴 — ○○ 불가"
    free−1 == need → 역할 '남은 자리는 ○○용', 이유 꼬리 "남은 자리는 ○○ — 다음 새 신은 받지 않는다"
은혜: 카드 배치(plan)가 비워 둔 칸을 카드 밖 은혜가 먼저 차지하면 경고 "마법 칸은 염화 고리 자리 — 나중에 교체"
"""
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RJ = os.path.join(ROOT, 'engine', 'recommend.js'); TJ = os.path.join(ROOT, 'engine', 'test.js')
def load(p): return io.open(p, encoding='utf-8').read()
def save(p, s): io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, old, new, n=1):
    c = s.count(old); assert c == n, ('anchor %d != %d: %r' % (c, n, old[:80])); return s.replace(old, new)

r = load(RJ)
if 'seatInfo' not in r:
    r = rep(r, "  const dirOfVariant = (vid) =>",
"""  // 8-M: 신 풀 자리 — 카드 신이 들어올 자리가 남았나
  function seatInfo(v, state, dv) {
    const seen = new Set(state.gods_seen || []);
    const mainLeft = (v.main_gods || []).filter((g) => !seen.has(g) && !W.NON_POOL_GODS.includes(g));
    const fg = (v.fourth || []).map((f) => f.god);
    const fourthLeft = fg.length && !fg.some((g) => seen.has(g)) ? 1 : 0;
    return { need: mainLeft.length + fourthLeft, free: W.GOD_POOL_CAP - dv.poolSize, waiting: [...mainLeft, ...(fourthLeft ? [fg.map((g) => nameOf(g)).join('/')] : [])].map((g) => (godById.get(g) ? nameOf(g) : g)),
      cardGods: new Set([...(v.main_gods || []), ...fg]) };
  }
  const dirOfVariant = (vid) =>""")
    # 신: 자리 판정
    r = rep(r, "    if (lastNew) roles.push('마지막 새 신');",
"""    if (lastNew) roles.push('마지막 새 신');
    // 8-M: 카드 밖 새 신이 빌드 신 자리를 빼앗는가
    let seatBlock = null, seatLast = null;
    if (dv.variant && !W.NON_POOL_GODS.includes(godId) && !(state.gods_seen || []).includes(godId)) {
      const si = seatInfo(dv.variant, state, dv);
      if (!si.cardGods.has(godId) && si.need > 0) {
        if (si.free - 1 < si.need) { seatBlock = si; roles.unshift('빌드 막힘'); }
        else if (si.free - 1 === si.need) { seatLast = si; roles.push(`남은 자리는 ${si.waiting.join('·')}용`); }
      }
    }""")
    r = rep(r, "    if (poolOver && !partnerDuo && !readyDuos.length && !legReady) tier = Math.max(0, tier - 1);",
               "    if (poolOver && !partnerDuo && !readyDuos.length && !legReady) tier = Math.max(0, tier - 1);\n    if (seatBlock) tier = 0;   // 8-M")
    r = rep(r, "    if (lastNew && grade !== 'must') reason += ' · 4번째 신 — 받으면 이후 새 신은 안 뜸';",
"""    if (seatBlock) { const dd = [...cardDuoSet(dv.variant)].map((x) => nameOf(x)).slice(0, 2).join('·'); reason = `받으면 풀이 차서 ${josa(seatBlock.waiting.join('·'), '이', '가')} 더 안 나옴${dd ? ` — ${dd} 불가` : ''}. 석류·재화 문으로`; }
    else if (seatLast) reason += ` · 남은 자리는 ${seatLast.waiting.join('·')} — 다음 새 신은 받지 않는다`;
    else if (lastNew && grade !== 'must') reason += ' · 4번째 신 — 받으면 이후 새 신은 안 뜸';""")
    # 은혜: 배치가 비워 둔 칸
    r = rep(r, "    if (breaksMust) warnings.push(`빌드 필수 ${eul(nameOf(replacing))} 버림`);",
"""    if (breaksMust) warnings.push(`빌드 필수 ${eul(nameOf(replacing))} 버림`);
    // 8-M: 카드 배치가 조건 은혜용으로 비워 둔 칸을 다른 은혜가 먼저 차지 — 막지는 않고 알린다 (나중에 교체 가능)
    if (dv.variant && b.occupies_slot && !replacing && !cardKeep(dv.variant).includes(b.id)) {
      const P = dv.variant.plan || {};
      const res = [...(P.cond_must || []), ...(P.extra || [])].map((x) => boonById.get(x)).find((x) => x && x.occupies_slot && x.slot === b.slot && !dv.owned.has(x.id));
      if (res && !(P.groups || []).some((g) => (g.options || []).includes(b.id))) warnings.push(`${SLOT_KO[b.slot]} 칸은 ${res.name_ko} 자리 — 나중에 교체`);
    }""")
    save(RJ, r); print('recommend.js: 8-M')

t = load(TJ)
if "sc('S54'" not in t:
    NEW = """

sc('S54', '신 풀 자리 — 모로스 카드: 헤라·제우스 뒤 데메테르는 "남은 자리는 헤스티아용", 그 뒤 아폴론은 빌드 막힘(패스)', () => {
  const st3 = E.applyChoice(S({ weapon: 'flames', aspect: 'flames_moros', region: 2, boons: ['zeus_heaven_flourish', 'hera_sworn_strike'], gods_seen: ['hera', 'zeus'] }), { kind: 'variant', id: 'flames_orbit_hera_zeus' });
  const d3 = E.recommendGods(st3, ['demeter'])[0];
  const st4 = E.applyChoice(S({ weapon: 'flames', aspect: 'flames_moros', region: 2, boons: ['zeus_heaven_flourish', 'hera_sworn_strike', 'demeter_arctic_ring'], gods_seen: ['hera', 'zeus', 'demeter'] }), { kind: 'variant', id: 'flames_orbit_hera_zeus' });
  const r4 = E.recommendGods(st4, ['apollo', 'hestia']);
  const ap = r4.find((r) => r.id === 'apollo'), he = r4.find((r) => r.id === 'hestia');
  const boons3 = E.recommendBoons(E.applyChoice(st3, { kind: 'god', id: 'demeter' }), ['demeter_arctic_ring', 'demeter_frigid_rush']);
  return { rows: r4, checks: [
    check("데메테르(3번째): 역할 '남은 자리는 헤스티아용'", d3.roles.some((x) => /남은 자리는 헤스티아용/.test(x)), d3.grade_ko + ' ' + d3.roles.join(',')),
    check("아폴론(4번째): 패스 + '빌드 막힘'", ap.grade === 'pass' && ap.roles.includes('빌드 막힘'), ap.grade_ko + ' ' + ap.roles.join(',')),
    check("아폴론 이유에 '헤스티아이(가) 더 안 나옴'", /헤스티아이\\(가\\) 더 안 나옴/.test(ap.reason), ap.reason),
    check('헤스티아가 1위', r4[0].id === 'hestia', r4.map((r) => r.id + ':' + r.grade_ko).join(' ')),
    check("데메테르 설한 고리에 '마법 칸은 염화 고리 자리' 경고", boons3.find((r) => r.id === 'demeter_arctic_ring').warnings.some((w) => /마법 칸은 염화 고리 자리/.test(w)), JSON.stringify(boons3.find((r) => r.id === 'demeter_arctic_ring').warnings)),
  ] };
});
"""
    t = rep(t, "\n// ── 실행 ────────────────────────────────────────────────", NEW + "\n// ── 실행 ────────────────────────────────────────────────")
    save(TJ, t); print('test.js: S54')
