# 데이터 스키마 (1-A, 페이블)

모든 데이터는 `data/*.json`에 UTF-8로 저장. 브라우저에서 그대로 인라인되므로 **주석 없는 순수 JSON**.
ID는 영어 snake_case(불변 키), 표시용 이름은 `name_ko`(한글판 기준) + `name_en`.

## 공통 규칙

```jsonc
{
  "id": "hestia_attack",        // 영어 snake_case. 파일 내 유일. 한 번 정하면 바꾸지 않음
  "name_ko": "불타는 공격",       // 한글판 인게임 표기. 불확실하면 ISSUES.md에 기록하고 임시값 사용
  "name_en": "Flame Strike",
  "verified": true,              // 한글명·효과를 신뢰 가능한 출처 2개 이상으로 확인했는가
  "source": ["wiki", "namu"],    // RESEARCH_GUIDE.md 출처 키
  "notes": "..."                 // 선택. 조사 중 메모
}
```

### 슬롯 enum (`slot`)

**은혜 장착 칸은 5개뿐이고, 한 칸에는 신 1명의 은혜만 들어간다.**
다른 신의 같은 칸 은혜를 받으면 **기존 은혜가 사라지고 교체**된다 (동시 장착 불가).

| 값 | 한글판 표기 | 칸 점유 | 설명 |
|---|---|---|---|
| `attack` | **일반 공격** | O | "OO 일격" 계열 |
| `special` | **기술** | O | "OO 기예" 계열 (전작의 특수 공격) |
| `cast` | **마법** | O | "OO 고리" 계열 (마법진) |
| `sprint` | **질주** | O | "OO 쇄도" 계열 (돌진-질주) |
| `magick` | **마력** | O | "OO 마력" 계열 (마력 회복/최대치) |
| `passive` | — | X | 칸을 차지하지 않음. 여러 개 동시 보유 가능 |
| `infusion` | 정기 | X | 원소 N개 보유 시 발동. `infusion_req` 동반 |
| `legendary` | 전설 | X | 신별 1개 |
| `hex` | 비술 | X | 셀레네 전용 (별도 시스템) |

**칸을 점유하는 은혜는 핵심 신 9명의 것뿐이다.** 신마다 5칸 각각에 은혜가 정확히 1개씩 있으므로
`9 × 5 = 45개`가 점유 은혜이고, 나머지는 전부 `passive` / `infusion` / `legendary`다.

> **헤르메스·아르테미스는 칸을 차지하지 않는다.**
> 헤르메스는 질주를 강화하는 은혜가 2개(거침없는 속도·잰 발걸음)이고 플레이 중 둘 다 보유
> 가능하므로 칸 점유 모델과 모순된다. 위키의 Type 열은 "점유하는 칸"이 아니라
> "강화하는 동작"을 뜻하는 것으로 판단해 `slot: passive` + `affects`로 정정했다.

### 슬롯 배타성 관련 필드

```jsonc
{
  "slot": "attack",
  "occupies_slot": true,          // 5칸 중 하나를 점유하는가. 핵심 신 9명 × 5칸만 true
  "conflicts": [                  // 같은 칸의 다른 신 은혜 전부 (점유 은혜는 8개씩)
    "poseidon_wave_strike", "hestia_flame_strike", "..."
  ],
  "conflict_reason": "슬롯 배타 - 같은 칸에는 신 1명만 장착 가능",

  "affects": ["sprint"]           // 칸은 안 차지하면서 특정 동작을 강화할 때 (헤르메스·아르테미스 등)
}
```

- `conflicts`는 **한 필드로 통일**되어 있고 두 출처가 섞여 있다:
  - **슬롯 유래**(자동): `derive_slots.py`가 같은 칸의 다른 8개를 넣는다. 손대지 말 것
  - **수동**(위키 명시 "cannot be combined"): `review_1c.py`의 `pair()`로 추가. 마법 변형 계열(번개 투창·달아오른 숯·현지 기후·위험 지대·물결 고리), Ω 마법 변형(지하수 분출↔햇살 방사·고기 분쇄), 잡초 박멸↔고속 망치, 왕의 강권↔여왕의 강권, 용력↔죽음
  - 은혜·융합·망치·아르카나 **어느 파일의 id든** 넣을 수 있다. validate가 전 파일 통합으로 존재·양방향을 검사한다
  - 망치의 `boon_conflicts`는 폐기 → `conflicts`로 통합
- `validate.js`가 (a) 신별 슬롯당 정확히 1개 (b) 비핵심 신의 칸 점유 금지 (c) conflicts 목록이 슬롯 전체와 일치 (d) 미점유 은혜에 conflicts 없음 — 4가지를 강제한다.

**엔진(2-A)이 반드시 지켜야 할 것**
1. 이미 채워진 칸에 다른 신의 은혜를 추천할 때는 **"기존 OO을 버리게 됨"을 반드시 표시**한다. 조용히 상위 추천에 올리면 안 된다.
2. 융합/전설 은혜의 `requires`는 **현재 장착 중인** 은혜 기준이다. 칸을 교체하면 진행 중이던 융합 조건이 깨질 수 있으므로, 교체 추천 시 그 손실을 점수에 반영해야 한다.
3. 빈 칸 > 채워진 칸 순으로 가산점을 준다.

### 저주(상태이상) enum (`curse`)
**1-B 조사로 확정 (나무위키 = 한글판 인게임 표기).** 초안의 한글명은 전부 틀렸으므로 아래가 정답.

| 값 | 신 | 영어 | 한글(확정) |
|---|---|---|---|
| `blitz` | 제우스 | Blitz | **암운** |
| `scorch` | 헤스티아 | Scorch | **잔불** |
| `froth` | 포세이돈 | Froth | **침수** |
| `freeze` | 데메테르 | Freeze | **동결** |
| `gust` | 데메테르(2차) | Gust | **선풍** |
| `daze` | 아폴론 | Daze | **실명** |
| `weak` | 아프로디테 | Weak | **약화** |
| `glow` | 헤파이스토스 | Glow | **발열** |
| `hitch` | 헤라 | Hitch | **결속** |
| `wounds` | 아레스 | Wounds | **상처** |
| `charm` | 헤라·아프로디테 융합 | Charm | **현혹** |
| `marked` | 아르테미스 | Marked | **표식** |
| `morph` | 셀레네(비술) | Morph | **변형** |
| `shine` | 셀레네(천상 붕괴) | Shine | (미확인) |
| `none` | — | — | 저주 없음 |

### 한글판 용어 대조표 (중요 - UI 문구는 전부 이 표를 따를 것)

| 영어 | 한글판 정식 | 초안의 오역 |
|---|---|---|
| Special | **기술** | ~~특수 공격~~ |
| Cast | **마법** / 마법진 | |
| Magick | **마력** | |
| Duo Boon | **융합 은혜** | ~~듀오~~ |
| Legendary Boon | **전설 은혜** | |
| Infusion Boon | **정기 은혜** | ~~주입~~ |
| Hex | **비술** | ~~헥스~~ |
| Godsent | **신력** | |
| Keepsake | **기념품** | ~~유물~~ |
| Artifact | 유물 (별개 개념) | |
| Incantation | 주술 (별개 개념) | |
| Grasp | **이해도** | ~~소모~~ |
| Prime | **집중** | ~~점유~~ |
| Armor | **방어도** | |
| Guardian / Warden | **수호자 / 파수꾼** | |
| Location / Encounter | **장소 / 교전** | |
| Aspect | **양상** (`OO 양상`, '의' 없음) | ~~OO의 양상~~ |
| Pom of Power | **힘의 석류** | |
| Rarity | 일반 / 희귀 / **특별** / 영웅 | ~~서사~~ |
| Splash / Blast / Falling Blade | 물보라 / 폭발 / **비검** | ~~낙하검~~ |
| Heartthrob / Plasma | **연심** / **혈장** | ~~심장구~~ |
| Death Defiance | **죽음 저항** | |

### 시너지 태그 (`tags`) — 엔진이 점수 계산에 사용
자유 문자열이지만 아래 목록을 우선 사용. 새 태그가 필요하면 이 표에 추가하고 사용.

| 태그 | 의미 |
|---|---|
| `omega` | Ω 동작 강화/의존 |
| `omega_attack` / `omega_special` / `omega_cast` | 특정 Ω 동작 강화 |
| `curse_apply:<curse>` | 해당 저주를 부여 |
| `curse_scale:<curse>` | 해당 저주 걸린 적에게 추가 효과 (저주 소모/증폭) |
| `attack_speed` | 공격 속도/충전 속도 |
| `crit` | 치명타 |
| `armor` | 방어력/피해 감소 |
| `heal` / `max_hp` | 생존 |
| `mana_regen` / `max_mana` / `mana_cost_down` | 마력 자원 |
| `cast_duration` / `cast_size` | 마법진 유지/범위 |
| `sprint_damage` | 질주 중 피해 |
| `aoe` | 광역 |
| `dot` | 지속 피해 |
| `boss_dmg` | 보스/방어구 대상 피해 |
| `duo_key` | **자동 생성.** 칸을 차지하지 않는데 융합 전제조건에 지목된 은혜 (예: 햇살 방사→눈부신 참사, 정전기 충격→초전도체). 칸 점유 은혜는 전부 융합 전제라 태그 의미가 없어 제외 |
| `beginner_safe` | 조건·페널티·빌드 의존 없이 무난한 은혜. **37개로 엄선** (1-C). 칸 점유 은혜 중 % 피해·저주 부여 기본형, 마력 중 조건 가벼운 것, 헤르메스·아르테미스 |
| `per_hit` | 타격마다 발동/누적 → **연타 무기(쌍검·횃불·도끼 회오리)** 궁합 |
| `pct_dmg` | 공격/기술 % 피해 증가 → **단타 무기(도끼·지팡이 Ω)** 궁합 |
| `cooldown_burst` | 쿨타임형 폭발(헤파이스토스) → 단타 무기 궁합, 연타 무기 비효율 |
| ~~`duo_gateway`~~ | 폐기 (1-C). validate가 사용 시 오류 |

### 조건 표현 (`requires`) — 듀오/전설/각성 공용
```jsonc
"requires": {
  "all": [                                  // 모든 항목 충족 (AND)
    { "any": ["zeus_attack", "zeus_special", "zeus_cast"] },   // 이 중 하나 (OR)
    { "any": ["poseidon_attack", "poseidon_sprint"] }
  ]
}
```
- `any` 목록은 **boon id**. 신 전체를 가리켜야 할 땐 `"god:zeus"` 형태 허용.
- 게임 내 "Any Ring Boon" / "Any Strike Boon" 처럼 **신을 가리지 않는 카테고리 조건**은 아래 토큰 사용 (validate.js가 해석):
  - `cat:ring` — `tags`에 `ring`이 있는 은혜 아무거나 (마법 슬롯 "OO 고리")
  - `cat:strike` — `slot`이 `attack`인 은혜 아무거나 ("OO 일격")
- 전설 은혜는 보통 `all` 안에 `any` 2~3개.

---

## 파일별 스키마

### `weapons.json`
```jsonc
[
  {
    "id": "staff",
    "name_ko": "마녀의 지팡이",      // 확인 필요
    "name_en": "Witch's Staff (Descura)",
    "unlock_order": 1,               // 초반 4개 = 1~4
    "moveset": {
      "attack":  "짧은 콤보 근접, Ω공격은 충전 후 강타",
      "special": "원거리 투사체, Ω특수는 ...",
      "cast":    "기본 마법진"
    },
    "core_slots": ["attack", "cast"], // 이 무기가 체감상 가장 잘 쓰는 슬롯 (BUILD_DIRECTIONS와 일치)
    "aspects": [
      {
        "id": "staff_melinoe",
        "name_ko": "멜리노에의 양상",
        "name_en": "Aspect of Melinoë",
        "unlocked_by_default": true,
        "effect": "...",
        "favors": ["omega_attack", "attack_speed"],   // 시너지 태그
        "favored_gods": ["hestia", "zeus"],           // 커뮤니티 정석에서 자주 조합되는 신
        "beginner_rank": 1                            // 1=초보 추천, 숫자 클수록 후순위
      }
    ]
  }
]
```
- 초반 4무기: `staff`, `blades`, `flames`, `axe`. 나중 무기(`skull`, `coat`)는 id만 예약, 내용 비워도 됨.
- 숨겨진 양상(hidden aspect)은 `hidden: true`로 표시하고 `beginner_rank` 크게.

### `gods.json`
```jsonc
[
  {
    "id": "hestia",
    "name_ko": "헤스티아",
    "name_en": "Hestia",
    "type": "core",            // core(핵심 슬롯 제공, 선택지 등장) | guest(아테나·디오니소스 — 지상 이벤트 조우, 칸 미점유, 융합·정기 없음, 신 풀 미포함) | encounter(아르테미스 등 조우형) | hermes | selene | chaos | npc(아라크네·이카로스·나르키소스·에코·메데이아·키르케 등 비선택 소스)
    "curse": "scorch",
    "theme": "지속 화상 피해. 보스전에 강함, 잡몹 처리 느림",
    "beginner_note": "화상은 시간이 걸리므로 공격속도 빠른 무기와 궁합"
  }
]
```

### `boons.json`
```jsonc
[
  {
    "id": "hestia_attack",
    "god": "hestia",
    "name_ko": "...",
    "name_en": "Flame Strike",
    "slot": "attack",
    "effect": "공격 시 화상 부여 (한 줄 요약, 수치는 Common 기준)",
    "rarity_scaling": "화상 피해 60/70/80/100",   // 있으면 기록, 없으면 생략
    "tags": ["curse_apply:scorch", "dot", "beginner_safe"],
    "prereq": null,                             // 일반 은혜는 대부분 null. 상위 은혜는 requires 형식
    "weapon_affinity": { "staff": 2, "blades": 1, "flames": 1, "axe": 3 },  // 선택. 무기별 궁합 0~3, 없으면 생략(엔진이 태그로 추정)
    "verified": true,
    "source": ["wiki"]
  }
]
```
- **핵심 신 9명(아프로디테·아폴론·아레스·데메테르·헤파이스토스·헤라·헤스티아·포세이돈·제우스)의 은혜는 전부** 넣는다.
- 헤르메스·아르테미스·카오스·NPC 은혜는 `slot`을 정확히 표기하고 `tags`는 최소한만.
- `effect`는 폰 화면에 한 줄로 뜨는 텍스트다. **30자 내외**로 요약.

### `duo_legendary.json`
```jsonc
[
  {
    "id": "duo_zeus_poseidon",
    "kind": "duo",                    // duo | legendary
    "gods": ["zeus", "poseidon"],     // legendary는 1개
    "name_ko": "...",
    "name_en": "...",
    "effect": "...",
    "requires": { "all": [ { "any": [...] }, { "any": [...] } ] },
    "power_tier": "S",                // S/A/B — 커뮤니티 평가. 초보 기준 체감 강도
    "tags": [...],
    "verified": true,
    "source": [...]
  }
]
```
- **`requires`가 이 프로젝트의 가장 중요한 데이터.** 은혜 id가 boons.json과 정확히 일치해야 한다 (검증 스크립트로 확인).

### `hammers.json` (다이달로스 망치 = 무기 강화)

교전 보상으로 등장하는 **3개 중 1개 선택**. 은혜와 동일한 선택 구조이므로 엔진 추천 대상.
등장 빈도: 1~2지역 각 1개, 3지역부터 각 2개.

```jsonc
[
  {
    "id": "staff_cross_cataclysm",
    "weapon": "staff",                     // weapons.json의 id
    "name_ko": "십자 대격변",
    "name_en": "Cross Cataclysm",
    "effect": "Ω 공격 피해 +50%, 측면도 타격",
    "rank2": "Ω 공격 +75%",                // 이카로스 '사후 지원' 획득 시 2단계. 없으면 생략
    "affects": ["omega_attack"],           // attack|special|cast|dash|sprint|magick|omega_attack|omega_special|omega_cast
    "tags": ["omega_attack", "aoe"],
    "aspect_only": null,                   // 특정 양상 전용이면 그 양상 id
    "aspect_excluded": ["staff_anubis"],   // 이 양상에서는 등장하지 않음
    "conflicts": ["staff_rapid_thrasher"], // 같은 무기의 다른 망치와 동시 채용 불가 (반드시 양방향 기재)
    "boon_conflicts": ["demeter_weed_killer"], // 은혜와 상충
    "beginner_priority": 1,                // 1=우선, 2=무난, 3=후순위, 0=비추천
    "verified": true,
    "source": ["wiki", "namu"]
  }
]
```

- `conflicts`는 **양방향으로 기재**해야 한다 (validate.js가 단방향을 오류로 잡음).
- `affects`는 엔진이 "이 망치가 지금 빌드의 주력 동작을 강화하는가"를 판단하는 축이다.
  무기의 `core_slots` 및 보유 은혜가 붙은 슬롯과 대조해 점수를 준다.
- 숨겨진 양상 전용 망치(`aspect_only`)는 해당 양상을 쓰지 않으면 후보에서 제외한다.

### `build_directions.json` (1-C 확정, 엔진의 정본)

무기별 빌드 방향. 사람용 설명은 `BUILD_DIRECTIONS.md`. **두 파일이 어긋나면 JSON이 맞다.**

```jsonc
{
  "principles": ["..."],                     // 엔진 규칙 문장
  "always_take": { "boons": [...] },         // 칸 미점유·무조건 이득 → 항상 상위
  "survival_kit": { "passive": [...], "slot": { "sprint": [...], "cast": [...], "magick": [...] }, "duos": [...] },
  "magick_rule": {...},                      // omega_dependent 방향의 마력 강제 규칙
  "weapons": {
    "staff": {
      "first_god_map": { "zeus": ["staff_omega_attack", "staff_special"], ... },  // 첫 신 → 열리는 방향 순위
      "directions": [{
        "id": "staff_omega_attack", "name_ko": "Ω 공격 화력", "difficulty": 1,   // ★1~3
        "omega_dependent": true,             // true면 마력 칸 비어 있을 때 마력 은혜 1순위
        "core_slots": ["attack", "magick"],
        "slot_prefs": { "attack": [boon ids 순위], "magick": [...], ... },      // 칸별 신 후보. 반드시 해당 slot의 은혜만
        "support_boons": [...],              // 칸 미점유 보조 은혜 순위 (점유 은혜 넣으면 validate 오류)
        "avoid_boons": [...], "avoid_reason": "...",
        "target_duos": [duo ids], "hammers": [hammer ids 순위], "requires_hammer": "id"(선택),
        "arcana": [...], "aspects": [aspect ids]
      }]
    }
  },
  "arcana_beginner_set": { "grasp": 10, "cards": [...], "upgrade_path": [...], "never_with": [["strength","death"]] },
  "keepsake_plan": {...}, "hex_beginner": [...]
}
```

validate.js가 검사하는 것: 모든 id 존재 · `slot_prefs.X`에는 X 칸 은혜만 · `support_boons`에 칸 점유 은혜 금지 · 회피와 선호 동시 존재 금지 · 망치/양상은 같은 무기 것만 · `first_god_map` 방향 id 존재 · 아르카나 초기 세트 이해도 합 ≤ grasp.

### `arcana.json`
```jsonc
[
  {
    "id": "the_sorceress",
    "name_ko": "마법사",              // 확인 필요
    "name_en": "The Sorceress",
    "grasp": 3,
    "effect": "Ω동작 사용 중 피해 감소 ...",
    "awaken_condition": "...",       // 각성 조건 (있으면)
    "tags": ["omega", "cast"],
    "beginner_priority": 1,          // 1=초보 필수, 2=추천, 3=선택, 0=비추천/후반용
    "grid_position": [1, 3]          // 선택. 카드 위치(행,열) — 각성 조건에 쓰이면 기록
  }
]
```

### `keepsakes.json`
```jsonc
[
  {
    "id": "silver_wheel",
    "name_ko": "은빛 바퀴",           // 확인 필요
    "name_en": "Silver Wheel",
    "giver_ko": "헤카테",
    "giver_en": "Hecate",
    "effect": "...",
    "kind": "utility",               // god_favor(특정 신 등장 유도) | utility | defense | offense | meta(자원)
    "god": null,                     // god_favor면 신 id
    "beginner_priority": 1,
    "region_note": "1지역에 장착, 2지역부터 신 유물로 교체" // 선택
  }
]
```

### `hexes.json`
```jsonc
[
  {
    "id": "hex_moon_water",
    "name_ko": "...",
    "name_en": "Moon Water",
    "effect": "...",
    "mana_to_charge": 200,           // 충전에 필요한 마력 소모량
    "tags": ["heal"],
    "beginner_priority": 1
  }
]
```

### `ISSUES.md` (자유 형식)
- `[한글명 불확실] boons.json/hestia_attack — 위키 "불꽃 공격" vs 나무 "화염 강타"`
- `[조건 불일치] duo_legendary.json/duo_xxx — 출처 A는 ..., 출처 B는 ...`
- `[누락] ...`

---

## 검증 규칙 (오퍼스가 1-B 끝에 `data/validate.js`로 구현·실행)
1. 모든 `id` 파일 내 유일
2. `boons[].god` ∈ `gods[].id`
3. `requires` 안의 모든 id ∈ `boons[].id` 또는 `god:<gods.id>`
4. `slot` ∈ 슬롯 enum, `curse` ∈ 저주 enum
5. 핵심 신 9명 각각 `attack/special/cast/sprint/magick` 슬롯 은혜가 최소 1개씩 존재 (없는 신이 있으면 ISSUES에 사유 기록)
6. `verified: false` 항목 수를 출력
7. `hammers[].weapon` ∈ `weapons[].id`, `affects` ∈ affects enum
8. `aspect_only` / `aspect_excluded`는 실제 양상 id, `conflicts`는 **양방향 + 같은 무기**, `boon_conflicts`는 실제 은혜 id
9. 초반 4무기 각각 망치가 10개 이상 존재
10. **슬롯 배타성** — (a) 핵심 신 9명은 슬롯당 정확히 1개 (b) 비핵심 신은 칸 점유 불가 (c) 점유 은혜의 `conflicts`가 같은 슬롯 나머지를 전부 포함
11. **상충 통합 검사** — 은혜·융합·망치·아르카나의 `conflicts` id가 존재하고 **양방향 대칭**. `boon_conflicts`·`duo_gateway` 사용 시 오류
12. 전설 은혜의 `boons.json` prereq == `duo_legendary.json` requires
13. `build_directions.json` 참조 무결성 (위 스펙 참조)
