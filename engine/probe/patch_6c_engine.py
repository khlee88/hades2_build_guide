# -*- coding: utf-8 -*-
"""6-C 엔진 (페이블 대행, 2026-10-14): avoid_hammers 연결 (ISSUES P3). 모리안(춤추는 단검)·메데이아(일제 발사)·도끼 단발(지옥 가르기)·쌍검 백스탭이 기대고 있다."""
import io, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RJ = os.path.join(ROOT, 'engine', 'recommend.js'); WJ = os.path.join(ROOT, 'engine', 'weights.js'); TJ = os.path.join(ROOT, 'engine', 'test.js')
def load(p): return io.open(p, encoding='utf-8').read()
def save(p, s): io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, old, new, n=1):
    c = s.count(old); assert c == n, ('anchor %d != %d: %r' % (c, n, old[:80])); return s.replace(old, new)

w = load(WJ)
if 'AVOID: -8,                  // 6-C' not in w:
    w = rep(w, "    BLOCKS_FUTURE: -1,          // 메인 방향 순위에 있는 미보유 망치를 막음",
               "    BLOCKS_FUTURE: -1,          // 메인 방향 순위에 있는 미보유 망치를 막음\n    AVOID: -8,                  // 6-C: 방향의 avoid_hammers (은혜 AVOID와 같은 크기)")
    save(WJ, w); print('weights.js: HAMMER.AVOID')

r = load(RJ)
if 'avoid_hammers' not in r:
    r = rep(r, """      let fitSum = 0, detail = null;
      for (const { d, weight } of active) {
        const i = (d.hammers || []).indexOf(h.id);
        const fit = i >= 0 ? rankVal(W.HAMMER.FIT, i) : W.HAMMER.NOT_LISTED;
        fitSum += weight * fit;
        if (i >= 0 && (!detail || weight > detail.weight)) detail = { d, weight, rank: i };
      }""",
"""      let fitSum = 0, detail = null, avoidBy = null;
      for (const { d, weight } of active) {
        // 6-C: 방향의 avoid_hammers — 은혜의 avoid_boons와 같은 취급 (ISSUES P3)
        if ((d.avoid_hammers || []).includes(h.id)) { fitSum += weight * W.HAMMER.AVOID; if (!avoidBy || weight > avoidBy.weight) avoidBy = { d, weight }; continue; }
        const i = (d.hammers || []).indexOf(h.id);
        const fit = i >= 0 ? rankVal(W.HAMMER.FIT, i) : W.HAMMER.NOT_LISTED;
        fitSum += weight * fit;
        if (i >= 0 && (!detail || weight > detail.weight)) detail = { d, weight, rank: i };
      }""")
    r = rep(r, """      let reason;
      if (unlock) reason = `'${unlock.name_ko}' 방향을 열어줌`;
      else if (detail) reason = `'${detail.d.name_ko}' 망치 ${detail.rank + 1}순위`;""",
"""      let reason;
      if (avoidBy && (!detail || avoidBy.weight >= detail.weight)) reason = `비추: ${String(avoidBy.d.avoid_hammer_reason || '').slice(0, 30)}`;
      else if (unlock) reason = `'${unlock.name_ko}' 방향을 열어줌`;
      else if (detail) reason = `'${detail.d.name_ko}' 망치 ${detail.rank + 1}순위`;""")
    save(RJ, r); print('recommend.js: avoid_hammers')

t = load(TJ)
if "sc('S37'" not in t:
    NEW = """

sc('S37', 'avoid_hammers — 모리안 쌍검에서 춤추는 단검은 비추 (ISSUES P3 연결)', () => {
  const st = S({ weapon: 'blades', aspect: 'blades_morrigan', boons: ['hestia_flame_strike'], gods_seen: ['hestia'] });
  const rows = E.recommendHammers(st, ['blades_dancing_knives', 'blades_wicked_onslaught', 'blades_melting_sickle']);
  const a = A(rows);
  return { rows, checks: [
    check(...a.rankOf('blades_dancing_knives', 3)),
    check(...a.reasonHas('blades_dancing_knives', '비추')),
    check(...a.rankOf('blades_wicked_onslaught', 1)),
  ] };
});
"""
    t = rep(t, "\n// ── 실행 ────────────────────────────────────────────────", NEW + "\n// ── 실행 ────────────────────────────────────────────────")
    save(TJ, t); print('test.js: S37')
