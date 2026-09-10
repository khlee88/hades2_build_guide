# 테스트 시나리오 (2-A, 페이블)

> `engine/test.js`가 이 문서의 시나리오를 그대로 실행한다. **검사 대상은 순위·배지·경고의 존재**이며 절대 점수는 검사하지 않는다.
> 각 시나리오는 `given`(상태) / `offered`(선택지) / `expect`(기대) 로 적는다. id는 전부 `data/*.json` 기준.
> 결과는 `engine/TEST_RESULTS.md`에 시나리오별 실제 순위·점수·이유를 표로 남긴다 (2-C 튜닝 근거).

공통 기본값: `region: 1`, `hp_state: "mid"`, `hammers: []`, `arcana: []`, `keepsake: null`, `hex: null`, `direction_lock: null`, rarity 미지정 = common.

---

## S01. 런 시작 — 지팡이 / 멜리노에 양상
- given: `weapon: staff, aspect: staff_melinoe`, graspCap 10
- call: `recommendRunStart`
- expect:
  - 아르카나 = `[death, the_furies, persistence, the_sorceress, the_wayward_son]` (이해도 합 10)
  - **이해도 0 카드(달·켄타우로스·왕비·운명·신성·심판)는 자동 선택에 넣지 않고** `free_cards`로 각성 조건과 함께 따로 안내
    > 2-B에서 발견: 0 이해도 카드는 각성 조건을 충족해야 활성화된다. 조건을 일반화해 판정할 수 없으므로
    > 자동 편성에 넣으면 "공짜니까 켜라"는 잘못된 추천이 된다 (달 카드는 주변 카드가 켜져야 활성화되는데 초보 세트엔 없음).
  - 열린 방향 3개 전부 표시, 1위는 `staff_omega_attack` (난이도 1 + 양상 보너스)
  - 어떤 신도 "확정"으로 표시되지 않음 (첫 신 대기 문구)

## S02. 첫 신 선택 — 지팡이
- given: `weapon: staff, aspect: staff_melinoe, boons: [], gods_seen: []`
- offered gods: `[zeus, demeter, aphrodite]`
- expect:
  - 1위 `zeus` 또는 `demeter` (둘 다 2개 방향을 열고 난이도 1 방향 포함)
  - `aphrodite`는 3위
  - 각 신의 이유에 열리는 방향 이름이 포함됨

## S03. 첫 은혜 — 지팡이, 제우스
- given: `weapon: staff, boons: [], gods_seen: [zeus]`
- offered: `[zeus_heaven_strike, zeus_storm_ring, zeus_ionic_gain]`
- expect:
  - 1위 `zeus_heaven_strike` (메인 `staff_omega_attack` 공격 칸 4순위 → 하지만 빈 핵심 칸) **또는** `zeus_ionic_gain` (마력 규칙 +2, 마력 칸 2순위) — 둘 중 하나가 1위, 다른 하나가 2위
  - `zeus_storm_ring` 3위
  - 경고 없음 (전부 빈 칸)

## S04. 교체 경고 — 지팡이 3지역
- given: `weapon: staff, region: 3, boons: [hera_sworn_strike, poseidon_flood_gain], gods_seen: [hera, poseidon]`
- offered: `[apollo_nova_strike, apollo_super_nova, apollo_blinding_rush]`
- expect:
  - `apollo_nova_strike` **3위**, warnings에 `"서약 일격을 버리게 됨"` 포함 (서약 일격은 메인 공격 칸 1순위, 광휘 일격은 2순위 → 교체 fit < 0)
  - `apollo_blinding_rush` 1위 (빈 질주 칸 + survival_kit.slot.sprint 1순위 + 3지역인데 방어/회복 0개 → 생존 배지)
  - `apollo_super_nova` 2위, 이유가 "무난함" 계열 (메인 방향엔 보조가 아님)

## S05. 융합 완성 신호 — 쌍검 헤스티아 → 제우스
- given: `weapon: blades, aspect: blades_melinoe, boons: [hestia_flame_strike, hestia_cardio_gain], gods_seen: [hestia]`
- offered: `[zeus_heaven_strike, zeus_static_shock, zeus_heaven_flourish]`
- expect:
  - `zeus_heaven_strike` **3위**, warnings에 `"화염 일격을 버리게 됨"`; 이 교체는 `duo_zeus_hestia` 진행을 깨지 않지만(천상 일격도 조건 충족) 화염 일격이 메인 공격 칸 1순위라 fit 음수
  - `zeus_heaven_flourish` 배지에 `융합 임박` (불벼락: 제우스 [천상 일격|천상 기예] + 헤스티아 [화염 일격] → 완성)
  - `zeus_static_shock`는 support 1순위(per_hit) — 1·2위는 `zeus_heaven_flourish`와 `zeus_static_shock` 중 어느 순서든 허용
  - 셋 다 이유에 "쌍검" 방향명 `공격 백스탭` 또는 융합명 포함

## S06. 같은 무기, 방향에 따라 추천 반전 — 도끼 정전기 충격
- given-A: `weapon: axe, aspect: axe_melinoe, boons: [apollo_nova_strike], gods_seen: [apollo]`
- given-B: `weapon: axe, aspect: axe_melinoe, boons: [hestia_flame_strike], hammers: [axe_psychic_whirlwind], gods_seen: [hestia]`
- offered (둘 다): `[zeus_static_shock, zeus_power_surge, zeus_divine_vengeance]`
  > **2-B 수정.** 최초 작성판은 `[zeus_static_shock, zeus_heaven_flourish, zeus_ionic_gain]`이었으나
  > 천상 기예(융합 '불벼락' 완성)와 대전된 마력(빈 마력 칸 1순위)이 설계상 정당하게 상위를 차지해
  > 정전기 충격이 A·B 양쪽에서 3위가 되었다 — 방향 반전이 순위에 드러나지 않는 선택지 구성이었다.
  > 변수를 분리하기 위해 **칸 미점유 은혜만** 제시하도록 교체했다. 엔진 로직은 바꾸지 않았다.
- expect:
  - A: `zeus_static_shock` **3위**, 이유 `"비추: 타격 수가 적어..."`, 배지 없음 (메인 `axe_heavy_attack`의 avoid)
  - B: `zeus_static_shock` **1위**, 이유에 `보조` (메인 `axe_omega_whirlwind`의 support 2순위 + 망치 보너스로 방향 확정)
  - B의 `directionScores` 1위가 `axe_omega_whirlwind`, A의 1위가 `axe_heavy_attack`

## S07. 회피 은혜 표시 — 횃불 잡초 박멸
- given: `weapon: flames, aspect: flames_melinoe, region: 2, boons: [hestia_flame_strike, poseidon_flood_gain, hera_fine_line], gods_seen: [hestia, poseidon, hera]`
- offered: `[demeter_weed_killer, demeter_frigid_rush, demeter_arctic_ring]`
- expect:
  - `demeter_weed_killer` **3위**, 이유 `"비추: 잡초 박멸은 Ω 공격 마력을 +10..."` — **숨기지 않고 표시**
  - `demeter_frigid_rush` 1위 (빈 질주 + survival_kit + beginner_safe)
  - `demeter_arctic_ring` 2위
  - 셋 중 어느 것도 warnings에 "버리게 됨" 없음

## S08. 수동 상충 — 지팡이 망치 + 잡초 박멸
- given: `weapon: staff, boons: [hera_sworn_strike, zeus_ionic_gain], hammers: [staff_rapid_thrasher], gods_seen: [hera, zeus]`
- offered hammers: `[staff_cross_cataclysm, staff_vampiric_cataclysm, staff_aetheric_moonburst]`
- expect: `staff_aetheric_moonburst` 1위; 나머지 둘은 점수 −∞, 이유 `"상충: 고속 강타와 동시 불가"`
- offered boons: `[demeter_weed_killer, demeter_ice_strike]`
- expect: `demeter_weed_killer` −∞ `"상충: 고속 강타와 동시 불가"`; `demeter_ice_strike` 1위이지만 warnings `"서약 일격을 버리게 됨"`

## S09. 융합 은혜가 뜨면 무조건 1위
- given: `weapon: blades, boons: [zeus_heaven_strike, hestia_flame_flourish], gods_seen: [zeus, hestia]`
- offered: `[{id: duo_zeus_hestia, rarity: duo}, zeus_double_strike, zeus_arc_flash]`
- expect: `duo_zeus_hestia` 1위, 배지 `융합`, 이유에 `"티어 S"`

## S10. 망치가 방향을 연다 — 쌍검 폭발적 암습
- given: `weapon: blades, aspect: blades_artemis, boons: [hera_sworn_strike, poseidon_flood_gain], gods_seen: [hera, poseidon]`
- offered hammers: `[blades_sweeping_ambush, blades_dancing_knives, blades_melting_sickle]`
- expect:
  - `blades_sweeping_ambush` 1위, 배지 `방향 전환: Ω 공격 암습`
  - `applyChoice(hammer: blades_sweeping_ambush)` 후 `directionScores` 1위가 `blades_omega_ambush` (양상 아르테미스 +2, requires_hammer +4)

## S11. 헤르메스는 경고 없이 상위
- given: `weapon: blades, boons: [hestia_flame_strike, hera_nexus_rush], gods_seen: [hestia, hera]`
- offered: `[hermes_nimble_limbs, zeus_heaven_flourish, hermes_stutter_step]`
- expect:
  - 헤르메스 둘 다 배지 `항상`, warnings **비어 있음** (질주 칸에 연분 쇄도가 있어도 교체 경고가 없어야 함 — 칸 미점유)
  - `zeus_heaven_flourish`(빈 기술 칸, 메인 1순위 아님)와 `hermes_nimble_limbs`가 1·2위 중 어느 순서든 허용

## S12. 신 풀 집중
- given: `weapon: staff, region: 3, boons: [zeus_heaven_strike, hestia_smolder_ring, apollo_blinding_rush, poseidon_flood_gain], gods_seen: [zeus, hestia, apollo, poseidon]` (풀 4 = CAP)
- offered gods: `[demeter, zeus]`
- expect: `zeus` 1위, `demeter` 이유 또는 배지에 `새 신` 표시

## S13. 기념품 — 융합 마지막 조건
- given: `weapon: staff, region: 1(클리어 직후), boons: [hera_sworn_strike, hera_fine_line, zeus_ionic_gain], gods_seen: [hera, zeus]`
- call: `recommendKeepsake`
- expect: `vivid_sea`(포세이돈) — `duo_poseidon_hera`(파급 효과)의 미충족 그룹이 포세이돈 [파도 일격|파도 기예|물결 고리|바다 너울] 하나뿐. 이유에 `'파급 효과'` 포함

## S14. 생존 우선 — 체력 낮음
- given: `weapon: axe, region: 2, hp_state: low, boons: [apollo_nova_strike, hephaestus_volcanic_flourish], gods_seen: [apollo, hephaestus]`
- offered: `[hephaestus_security_system, hephaestus_grand_caldera, hephaestus_anvil_ring]`
- expect: `hephaestus_security_system` 1위, 배지 `생존`; `hephaestus_grand_caldera` 2위 (메인 support 2순위)

## S15. 상태 검증
- given: `boons: [zeus_heaven_strike, hestia_flame_strike]` (같은 공격 칸 2개)
- call: `validateState`
- expect: 경고 1건 이상, 문구에 `"일반 공격"` 칸 중복 언급. `applyChoice`로 두 번째를 넣었다면 첫 번째가 자동 제거되어 경고 0건

## S16. 결정성
- 모든 시나리오를 2회 실행해 출력 JSON이 문자열 단위로 동일해야 한다.

---

## TEST_RESULTS.md 형식

```
## S04. 교체 경고 — 지팡이 3지역   ✅ PASS | ❌ FAIL
| 순위 | id | 점수 | 이유 | 경고 | 배지 |
|---|---|---|---|---|---|
| 1 | apollo_blinding_rush | 13.2 | 체력 관리용 — ... | | 생존 |
...
기대 대비: (FAIL이면 어떤 기대가 깨졌는지 한 줄)
방향 가중치: staff_omega_attack 0.71 / staff_cast 0.29
```
마지막에 PASS/FAIL 집계와, FAIL 시나리오의 `breakdown`을 붙인다. 2-C에서 페이블이 이 파일만 보고 가중치를 고친다.

---

## 2-C 추가 시나리오 (프로브 승격, 페이블)

## S17. 회피는 칸 점유 은혜에도 — 쌍검 첫 신 헤파이스토스
- given: `weapon: blades, aspect: blades_melinoe, gods_seen: [hephaestus]`
- offered: `[hephaestus_volcanic_strike, hephaestus_tough_gain, hephaestus_security_system]`
- expect: `hephaestus_volcanic_strike` **3위**, 이유에 `비추`; `hephaestus_tough_gain` 1위 (빈 마력 칸 + beginner_safe)

## S18. 허수 융합 진전 제거 — 지팡이 첫 은혜
- given: S03과 동일
- expect: `zeus_storm_ring`의 `breakdown.duo_progress`가 **없거나 0** (제우스만 등장한 상태에서 도달 불가 융합은 세지 않음); `zeus_ionic_gain` 1위 이유가 `마력`

## S19. 교체 손실은 도달 가능한 융합만 — S04 재검
- given: S04와 동일
- expect: `apollo_nova_strike` 경고에 `'파급 효과'`(포세이돈·헤라 모두 등장, 목표) 포함, **`'여왕의 강권'`·`'귀중한 가보'` 등 상대 신 미등장 융합은 없음**; 경고 총 3줄 이하

## S20. 전설 후보 이유
- given: `weapon: staff, boons: [zeus_heaven_strike, zeus_static_shock, zeus_arc_flash], gods_seen: [zeus]`
- offered: `[{id: zeus_shocking_loss, rarity: legendary}, zeus_double_strike]`
- expect: `zeus_shocking_loss` 1위, 배지 `전설`, 이유에 `전설`
- given-2: `boons: [zeus_heaven_strike]`만 → `zeus_shocking_loss` 선택 불가, 이유 `조건 미충족`

## S21. 후반 1↔2순위 교체는 권하지 않음 — 도끼 4지역
- given: `weapon: axe, aspect: axe_melinoe, region: 4, boons: [hera_sworn_strike, hephaestus_volcanic_flourish, hephaestus_tough_gain, apollo_blinding_rush, hera_engagement_ring, hephaestus_security_system], gods_seen: [hera, hephaestus, apollo]`
- offered: `[apollo_nova_strike, apollo_back_burner, apollo_light_smite]`
- expect: `apollo_nova_strike` **3위**, warnings `서약 일격을 버리게 됨`, 이유에 `비슷한 급` 또는 `나을 게 없음` (1순위라는 칭찬 문구 금지)

## S22. 조사·완성 대표 융합 — 쌍검 헤르메스 상황
- given: S11과 동일
- expect: `zeus_heaven_flourish` 이유에 `'불벼락'` (강권이 아님); 모든 경고·이유에 `와 동시` / `이 여기서` 같은 오조사 없음
