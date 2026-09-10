# -*- coding: utf-8 -*-
"""4-A 수정 2: 아르카나 선택을 탐욕(÷√grasp) → 핵심 기하 가중치 + 0/1 배낭 DP로 교체.
탐욕판은 죽음(4)을 싼 카드 3장에 밀어냈다 (S01/S23 실패). DESIGN §14-2 개정."""
import io, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = lambda *a: os.path.join(ROOT, *a)
rd = lambda p: io.open(p, encoding='utf-8').read()
wr = lambda p, s: io.open(p, 'w', encoding='utf-8').write(s)

p = P('engine', 'recommend.js'); s = rd(p)
start = s.index("  function recommendArcana(weapon, aspect, graspCap) {")
end = s.index("  function recommendRunStart(weapon, aspect, opts) {")
new = r"""  function recommendArcana(weapon, aspect, graspCap) {
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

"""
s = s[:start] + new + s[end:]
s = s.replace("  const ARC_W = W.ARCANA || { PRIORITY: { 1: 6, 2: 3, 3: 1 }, DIRECTION_HIT: 2, DIR_WEIGHTS: [1, 0.6, 0.4], AWAKEN_LOOKAHEAD: 1.5 };",
              "  const ARC_W = W.ARCANA || { CORE_BASE: 1000, CORE_DECAY: 0.5, PRIORITY: { 1: 6, 2: 3, 3: 1 }, DIRECTION_HIT: 2, DIR_WEIGHTS: [1, 0.6, 0.4], AWAKEN_LOOKAHEAD: 1.5 };")
wr(p, s); print('recommend.js: DP 교체')

p = P('engine', 'weights.js'); s = rd(p)
if 'CORE_BASE' not in s:
    s = s.replace("  ARCANA: {\n    PRIORITY: { 1: 6, 2: 3, 3: 1 },",
                  "  ARCANA: {\n    CORE_BASE: 1000,                  // 핵심 목록(arcana_beginner_set.cards→upgrade_path) 1위 가치. 기하급수라 '죽음 > 나머지 전부'\n    CORE_DECAY: 0.5,                  // 핵심 순위마다 ×0.5\n    PRIORITY: { 1: 6, 2: 3, 3: 1 },")
    wr(p, s); print('weights.js: CORE_BASE/DECAY 추가')

# DESIGN §14-2 개정
p = P('engine', 'DESIGN.md'); s = rd(p)
old_start = s.index('### 14-2. 알고리즘')
old_end = s.index('### 14-3.')
s = s[:old_start] + """### 14-2. 알고리즘 `recommendArcana(weapon, aspect, graspCap)` — 0/1 배낭 DP

> 초판은 탐욕 + "비용 효율(÷√이해도)"였고, 테스트에서 **죽음(4)이 싼 카드 3장에 밀려 빠졌다**(S01/S23). 초보에게 죽음 저항 1장은 1짜리 카드 셋보다 중요하다. 아래로 교체.

카드 가치:
```
value(c) = 핵심 목록(arcana_beginner_set.cards → upgrade_path) i번째 → CORE_BASE × CORE_DECAY^i   (1000, 500, 250, 125, 62, 31, 16, 8, 4, 2)
         | 그 외                       → PRIORITY[beginner_priority] (1→6, 2→3, 3→1; 0은 제외)
         + Σ_d DIRECTION_HIT × DIR_WEIGHTS[d 순위]      // 무기 방향 d의 arcana 힌트에 있으면
         + AWAKEN_LOOKAHEAD                              // '둘러싼 카드 중 하나' 조건(달)의 이웃이면
```
기하급수 덕에 **핵심 카드 하나가 비핵심 전부보다 크다** → 이해도가 얼마든 핵심이 먼저 채워지고, 남은 이해도에서 무기 방향 카드가 갈린다.
- 값이 결정되면 **0/1 배낭 DP**(후보 ≤ 25, 상한 ≤ 30)로 Σvalue 최대 조합을 구한다. 같은 값이면 이해도를 덜 쓰는 쪽.
- `never_with`(용력↔죽음) 둘 다 뽑히면 가치 낮은 쪽을 빼고 다시 푼다.
- 0 이해도 카드는 후보에 넣지 않고, 결과 집합의 **각성 고정점**으로 공짜로 붙인다.
- 출력: `cards`(태그 핵심/무기 방향/보조) · `awakened` · `free_cards`(잠긴 0 이해도 + 조건) · `next_up`(이해도 더 있으면 들어갈 2장) · `grasp_left`.

검증 결과(§S23/S24): 이해도 10 → 죽음·퓨리 자매·불굴·마법사·고집 센 아들(기존 세트와 동일). 이해도 20 → 무기별로 영겁/사냥꾼/밤 등이 갈리고 달·신성이 각성으로 붙는다.

""" + s[old_end:]
wr(p, s); print('DESIGN §14-2 개정')
