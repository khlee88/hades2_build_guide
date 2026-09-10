# -*- coding: utf-8 -*-
"""2026-09-10 커뮤니티 검증으로 build_directions.json이 바뀌어 기대값이 달라진 시나리오 갱신.
S01 지팡이 1위 방향, S03/S18 제우스 첫 은혜 순위, S07 잡초 박멸 회피 해제, S10 requires_hammer 폐지, S12 상태 조정."""
import io, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TJ = os.path.join(ROOT, 'engine', 'test.js')
SM = os.path.join(ROOT, 'engine', 'SCENARIOS.md')

t = io.open(TJ, encoding='utf-8').read()
if '커뮤니티 검증' in t:
    print('test.js: 이미 적용됨'); sys.exit(0)

def rep(old, new, count=1):
    global t
    assert t.count(old) == count, ('anchor count', t.count(old), old[:60])
    t = t.replace(old, new)

# S01
rep("check('1위 방향 == Ω 공격 화력', r.directions[0].id === 'staff_omega_attack', r.directions[0].id),",
    "check('1위 방향 == 기술 월광탄 (커뮤니티 검증: 멜리노에 지팡이는 기술 주력)', r.directions[0].id === 'staff_special', r.directions[0].id),")

# S18 (3줄 패턴이 고유 — S03보다 먼저)
rep("""    check(...a.setEq(['zeus_heaven_strike', 'zeus_ionic_gain'], [1, 2])),
    check(...a.hasBadge('zeus_ionic_gain', '마력')),
    check(...a.rankOf('zeus_storm_ring', 3)),""",
"""    check(...a.setEq(['zeus_heaven_strike', 'zeus_storm_ring'], [1, 2])),
    check('마력 배지 없음 — 기술 월광탄 방향은 Ω 비의존(magick_rule 미적용)', !rows.find((r) => r.id === 'zeus_ionic_gain').badges.includes('마력'), String(rows.find((r) => r.id === 'zeus_ionic_gain').badges)),
    check(...a.rankOf('zeus_ionic_gain', 3)),""")

# S03
rep("""    check(...a.setEq(['zeus_heaven_strike', 'zeus_ionic_gain'], [1, 2])),
    check(...a.rankOf('zeus_storm_ring', 3)),""",
"""    // 커뮤니티 검증: 기술 방향의 핵심 칸은 기술+마법 → 폭풍 고리(마법)가 대전된 마력보다 위
    check(...a.setEq(['zeus_heaven_strike', 'zeus_storm_ring'], [1, 2])),
    check(...a.rankOf('zeus_ionic_gain', 3)),""")

# S07 — 회피 해제. 회피 '표시' 검증은 S17(쌍검 화산 일격)이 이미 담당
s07_start = t.index("sc('S07',")
s07_end = t.index("sc('S08',")
t = t[:s07_start] + """sc('S07', '회피 해제 — 횃불 잡초 박멸은 한 핏줄 빌드의 보조', () => {
  // 원래 '회피 표시' 시나리오였으나 커뮤니티(lee: 한 핏줄 빌드에서 잡초 박멸은 비용 증가로 창을 더 빨리 떨어뜨림)가 반대라 회피 해제.
  // 회피 표시 자체는 S17이 검증한다.
  const st = S({ weapon: 'flames', aspect: 'flames_melinoe', region: 2, boons: ['hestia_flame_strike', 'poseidon_flood_gain', 'hera_fine_line'], gods_seen: ['hestia', 'poseidon', 'hera'] });
  const rows = E.recommendBoons(st, ['demeter_weed_killer', 'demeter_frigid_rush', 'demeter_arctic_ring']);
  const a = A(rows);
  return { rows, checks: [
    check("잡초 박멸 이유에 '비추' 없음", !/비추/.test(rows.find((r) => r.id === 'demeter_weed_killer').reason), rows.find((r) => r.id === 'demeter_weed_killer').reason),
    check(...a.rankOf('demeter_arctic_ring', 1)),
    check(...a.rankOf('demeter_frigid_rush', 2)),
    check('버리게 됨 경고 없음', rows.every((r) => !r.warnings.some((w) => w.includes('버리게'))), 'ok'),
  ] };
});

""" + t[s07_end:]

# S10 — requires_hammer 폐지(아르테미스 양상은 시작부터 방향이 열림). 망치는 방향을 '굳힌다'
rep("sc('S10', '망치가 방향을 연다 — 쌍검 폭발적 암습', () => {",
    "sc('S10', '망치가 방향을 굳힌다 — 쌍검 폭발적 암습 (requires_hammer 폐지)', () => {")
rep("    check(...a.hasBadge('blades_sweeping_ambush', '방향 전환')),\n    check('선택 후 방향 1위 == Ω 공격 암습', ds[0].id === 'blades_omega_ambush', ds[0].id),",
    "    check('선택 전에도 방향 1위 == 반격 Ω 공격 (양상 일치, 망치 불필요)', E.directionScores(st)[0].id === 'blades_omega_ambush', E.directionScores(st)[0].id),\n    check('선택 후 방향 1위 == 반격 Ω 공격', ds[0].id === 'blades_omega_ambush', ds[0].id),")

# S12 — 5번째 신이 S급 융합 마지막 조건이면 이기는 게 맞다(커뮤니티 헤스+제우스+데메 코어). 융합 보상이 없는 상태로 바꿔 풀 집중만 본다
rep("'apollo_blinding_rush', 'poseidon_flood_gain'], gods_seen: ['zeus', 'hestia', 'apollo', 'poseidon'] });",
    "'apollo_blinding_rush', 'poseidon_wave_flourish'], gods_seen: ['zeus', 'hestia', 'apollo', 'poseidon'] }); // 기술 칸을 채워 데메테르가 융합(냉동 화상)을 완성할 저주 칸이 없게 함")

io.open(TJ, 'w', encoding='utf-8', newline='\n').write(t)
print('test.js: 갱신')

# ── SCENARIOS.md ──
m = io.open(SM, encoding='utf-8').read()
def repl_section(heading_prefix, new_body):
    global m
    i = m.index('\n## ' + heading_prefix)
    j = m.index('\n## ', i + 5)
    m = m[:i] + '\n' + new_body.rstrip('\n') + '\n' + m[j:]

repl_section('S07.', """## S07. 회피 해제 — 횃불 잡초 박멸은 한 핏줄 빌드의 보조 (2026-09-10 개정)
- given: `weapon: flames, aspect: flames_melinoe, region: 2, boons: [hestia_flame_strike, poseidon_flood_gain, hera_fine_line], gods_seen: [hestia, poseidon, hera]`
- offered: `[demeter_weed_killer, demeter_frigid_rush, demeter_arctic_ring]`
- expect:
  - `demeter_weed_killer` 이유에 **`비추` 없음** — 원래 "Ω 공격 마력 5→15" 이유로 회피했으나, 커뮤니티(lee)는 한 핏줄 빌드에서 잡초 박멸을 비용 증가기로 권장(균열이 더 빨리 터짐). 회피 해제
  - `demeter_arctic_ring` 1위 (커뮤니티 '국밥' 동결 마법), `demeter_frigid_rush` 2위
  - 셋 중 어느 것도 warnings에 "버리게 됨" 없음
- 회피 '표시' 검증은 S17(쌍검 화산 일격)이 담당
""")
repl_section('S10.', """## S10. 망치가 방향을 굳힌다 — 쌍검 폭발적 암습 (2026-09-10 개정: requires_hammer 폐지)
- given: `weapon: blades, aspect: blades_artemis, boons: [hera_sworn_strike, poseidon_flood_gain], gods_seen: [hera, poseidon]`
- offered hammers: `[blades_sweeping_ambush, blades_dancing_knives, blades_melting_sickle]`
- expect:
  - `blades_sweeping_ambush` 1위
  - 선택 **전에도** `directionScores` 1위가 `blades_omega_ambush` — 나무위키·lee 모두 아르테미스 양상은 아프로디테 공격 + 공격/Ω 공격 망치면 되는 초보 추천 양상이라 망치를 요구 조건으로 걸지 않음 (양상 일치 +2)
  - `applyChoice(hammer: blades_sweeping_ambush)` 후에도 1위 유지 (망치 보유 +2)
""")
repl_section('S12.', """## S12. 신 풀 집중 (2026-09-10 개정)
- given: `weapon: staff, region: 3, boons: [zeus_heaven_strike, hestia_smolder_ring, apollo_blinding_rush, poseidon_wave_flourish], gods_seen: [zeus, hestia, apollo, poseidon]` (풀 4 = CAP, 커뮤니티 확인)
- offered gods: `[demeter, zeus]`
- expect: `zeus` 1위, `demeter` 이유 또는 배지에 `새 신` 표시
- 개정 이유: 원래 상태(기술 칸 비어 있음)에서는 데메테르가 S급 융합 '냉동 화상'의 마지막 조건을 채울 수 있어 5번째 신이어도 이기는 게 맞다(커뮤니티 코어 헤스+제우스+데메). 융합 보상이 없는 상태로 바꿔 풀 집중 항만 검사
""")
# S01/S03/S18 기대값 문구 갱신
m = m.replace('1위 방향 `staff_omega_attack`', '1위 방향 `staff_special` (2026-09-10 개정: 커뮤니티가 멜리노에 지팡이 = 기술 주력)') \
     .replace('`zeus_heaven_strike`·`zeus_ionic_gain`이 1·2위', '`zeus_heaven_strike`·`zeus_storm_ring`이 1·2위 (2026-09-10 개정: 기술 방향 핵심 칸 = 기술+마법)') \
     .replace('`zeus_ionic_gain` 1위 이유가 `마력`', '`zeus_ionic_gain` 3위, `마력` 배지 없음 (기술 방향은 Ω 비의존)')
m = m.rstrip('\n') + """

---

## 2026-09-10 커뮤니티 검증 개정 요약
`data/build_directions.json`을 나무위키·디시 뉴비 가이드 3편·Lee Reamsnyder 가이드와 대조해 방향을 고쳤다(`data/BUILD_DIRECTIONS.md` 참조). 영향받은 시나리오: S01(지팡이 1위 방향), S03/S18(제우스 첫 은혜 순위), S07(회피 해제), S10(requires_hammer 폐지), S12(상태 조정). 엔진 로직은 불변.
"""
io.open(SM, 'w', encoding='utf-8', newline='\n').write(m)
print('SCENARIOS.md: 갱신')
