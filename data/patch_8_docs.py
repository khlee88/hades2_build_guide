# -*- coding: utf-8 -*-
"""8단계 문서 (페이블, 2026-10-26): HANDOFF 8단계 · DESIGN §16 · SPEC §10 · ISSUES · BUILD_DIRECTIONS 부록 · SCHEMA variants."""
import io, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)
def load(p): return io.open(p, encoding='utf-8').read()
def save(p, s): io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, old, new, n=1):
    c = s.count(old); assert c == n, ('anchor %d != %d: %r' % (c, n, old[:80])); return s.replace(old, new)

h = load(P('HANDOFF.md'))
if '## 8단계' not in h:
    h = rep(h, "## 폴더 구조 (예정)", """## 8단계 — 빌드 카드 (2026-10-26 접수)

> 배경: 사용자 "매 선택을 단계별로 완성해 가니 학습이 느리다. 횃불은 서약 일격·천부적 마력·한 핏줄·바다 너울 → 제우스 거쳐 여왕의 강권으로 고정하고, 나머지는 내 판단." 1-C에서 커뮤니티 빌드 여러 개를 방향 하나의 칸별 순위로 **합쳐서** 어느 빌드를 타는지 안 보였다 — 그래서 왕의 강권(모로스용)이 멜리노에 공격 꾹에 끼어 있었다.
> 결정: 방향은 유지(운용법·엔진 가중치의 단위), 그 아래 커뮤니티 빌드를 **합치지 않고 그대로** `variants`로. 고르면 방향 고정 + 필수 은혜 목표 배지 + 홈 체크리스트.

### 8-A. 설계 — 담당: 페이블
- [x] 스키마 `variants[]`: id · name_ko · trust(high ◎ 출처 2+ 또는 실플레이 / mid ○ 출처 1 / low △ 추론) · strength(S/A/B)+strength_note · main_gods[3] · must(칸당 1, 순서대로) · support · target_duos · finisher{duo,note} · hammers? · aspects? · note · sources. `data/SCHEMA.md`
- [x] 엔진 규칙 `DESIGN §16`: 고정 = direction_lock + effectiveDirection(must를 칸 1순위로, support·융합·끝내기를 앞으로) → 기존 채점이 그대로 "이 빌드 기준". 은혜 '목표' +5 / '목표 보조' +2 / 끝내기 융합 '끝내기' +5. 신: 목표 은혜가 남아 있고 핵심 빈 칸이면 필수, 아니면 좋음, 역할 `목표 · 은혜`, 주요 신 +2 '빌드 신'. `buildChecklist(state)`
- [x] UI `SPEC §10`: 런 시작 방향 카드 안에 빌드 카드(강함·신뢰·신·필수·융합·끝내기·근거 접기·[이 빌드로]) → CTA "'…' 빌드로 시작". 홈 체크리스트(☑/☐·신 ✓·융합 진행·끝내기·보조/망치). 관리에 빌드 칩(변경/해제). 로그 run.bld, {t:'build'}
### 8-B. 데이터 — 담당: 페이블
- [x] 22방향 **59변형** (`data/patch_8_variants.py`, 한글명 → id 변환·검산: 필수 은혜의 신 ⊆ 주요 신, 융합 신 ⊆ 주요 신+1, 칸당 1개, 양상 존재). 출처는 1-C·6-A·6-B 수집분(dc51882·dc49018·dc38884·lee·namu) + 실플레이
- [x] 여왕의 강권 B→A, 공격 꾹 방향 target_duos에 추가(첫 클리어 런 2026-10-01 근거). 왕의 강권은 모로스 전용 변형으로 분리
### 8-C. 엔진 — 담당: 페이블 (`engine/probe/patch_8_engine.py`)
- [x] variantById · effectiveDirection · derive(variant) · lock · 은혜/신/융합 목표 · recommendRunStart.variants(양상 필터) · buildChecklist · applyChoice('variant') · validateState
- [x] S41~S45 → 45/45, validate 0
### 8-D. UI — 담당: 페이블 대행 (`app/src/patch_8_ui.py`)
- [x] 빌드 카드·CTA·체크리스트·관리 칩·로그·배지 CSS. 브라우저 375px: 횃불 멜리노에 카드 5장, 헤라 집중 선택 → CTA "'헤라 집중 — 파급 효과' 빌드로 시작" → 홈 `🔒 빌드` + 필수 0/4 체크리스트 → 은혜 시트 서약 일격 1위 `목표` 배지. 가로 스크롤 0
- [ ] 푸시 1회
### 8-E. 아르카나 재검토 — 담당: 페이블 (사용자 입력 대기)
- [ ] 사용자가 커뮤니티에서 받은 세팅이 앱 추천과 다르다고 함. 앱 추천(이해도 27)은 로그의 실제 세팅 12장과 **동일**(죽음·퓨리·불굴·마법사·고집 센 아들·전령·날랜 주자·연인·시초·영겁·밤·사냥꾼) → 비교할 "커뮤니티 세팅"이 뭔지 받아야 함. 나무위키 아르카나 문서는 WebFetch 404, 검색은 영문뿐 — 인앱 브라우저로 재수집 필요

## 폴더 구조 (예정)""")
    h = h.rstrip('\n') + "\n- 2026-10-26 — 8단계 빌드 카드 (페이블): 사용자가 \"핵심 은혜를 고정해 두고 찾아가는\" 방식이 학습에 낫다고 함. 1-C가 커뮤니티 빌드를 방향 하나로 합친 탓에 왕의 강권(모로스용)이 멜리노에 공격 꾹에 끼어 있었고 여왕의 강권(사용자 첫 클리어 끝내기)은 B급·목표 밖이었음 → 정정. 방향 아래 `variants` 59개(합치지 않고 그대로, 출처·신뢰·강함), 엔진은 effectiveDirection으로 기존 채점을 재사용(must를 칸 1순위로) + 목표/끝내기 배지 + buildChecklist, UI는 빌드 카드·CTA·홈 체크리스트·관리 칩. S41~S45 → 45/45. 아르카나(8-E)는 사용자 세팅을 받아야 비교 가능 — 앱 추천과 로그의 실제 세팅이 이미 같음\n"
    save(P('HANDOFF.md'), h); print('HANDOFF.md: 8단계')

d = load(P('engine', 'DESIGN.md'))
if '## 16.' not in d:
    d = d.rstrip('\n') + """

---

## 16. 빌드 카드 (8단계, 2026-10-26, 페이블)

### 16-1. 왜
방향(§2)은 커뮤니티 빌드 여러 개를 칸별 순위로 합친 것. 매 선택을 점수로 보면 맞긴 하지만 "지금 어느 빌드를 타고 있나"가 안 보여 사용자 학습이 느리다. 게임 구조(신 풀 4명)상 빌드는 "주요 신 3 + 핵심 은혜 6~8 + 융합 1~2"로 정의되므로, 그 단위를 **그대로** 보여주고 고르게 한다.

### 16-2. 데이터
`build_directions.json` 방향마다 `variants[]` (SCHEMA.md). must는 칸당 1개 — 그 변형에서 그 칸의 1순위. support·target_duos·finisher(끝내기 융합: 서로를 파괴하는 강권류)·hammers(없으면 방향 것)·aspects(양상 전용)·trust·strength·sources.

### 16-3. 엔진
- `state.variant` = 변형 id. `derive()`가 그 방향을 `effectiveDirection(d, v)`로 바꿔 끼운다: slot_prefs 맨 앞에 must, support 맨 앞에 변형 support(+칸 미점유 must), target_duos 맨 앞에 변형 융합+끝내기, hammers 교체. **기존 채점 전부가 그대로 "이 빌드 기준"이 된다.**
- `directionWeights`: lock = direction_lock || 변형의 방향 (0.7/0.3).
- 은혜: must → 배지 `목표` **+5**(같은 칸 2순위 8+5 > 목표 아닌 1순위 10), support → `목표 보조` **+2**, 끝내기 융합 후보 → `끝내기` +5. 이유 `빌드 '헤라 집중' 필수`.
- 신: 그 신의 must 은혜가 미보유이고 선택 가능 → 역할 `목표 · 은혜`; 그 칸이 비었으면 '필수', 아니면 '좋음'. main_gods → +2 '빌드 신'.
- `buildChecklist(state)`: must(보유·지금 그 칸에 뭐가 있나)·support·융합 진행·끝내기·망치·신 등장 여부.
- `applyChoice({kind:'variant', id|null})`가 direction_lock도 같이 건다/푼다. 다른 무기 변형은 무시 + validateState 경고.

### 16-4. 하지 않은 것
- 변형별 운용법 — 방향 운용법을 그대로 쓴다. 변형의 note·finisher.note가 차이를 적는다.
- 변형 점수화 — 강함(S/A/B)은 커뮤니티 평가의 전사이지 엔진 입력이 아니다. 정렬은 데이터 순서(강한 것·실플레이 검증 먼저).
"""
    save(P('engine', 'DESIGN.md'), d); print('DESIGN.md: §16')

s = load(P('ui', 'SPEC.md'))
if '## 10.' not in s:
    s = s.rstrip('\n') + """

## 10. 8단계 (2026-10-26) — 빌드 카드

- **런 시작**: 각 방향 카드 안에 `커뮤니티 빌드 N개` + 빌드 카드(`.vcard`): `[S] 이름 ◎` / 주요 신 3(색) / 필수(칸) / 융합(티어) → 끝내기 / `근거 · 메모` 접기(강함 근거·메모·끝내기 설명·보조·망치·출처) / `[이 빌드로]` 토글(선택 시 테두리 강조 + "✓ 이 빌드로 시작"). 양상 전용 변형은 그 양상에서만. 무기·양상을 바꾸면 선택 해제.
- **CTA**: 선택 시 `'헤라 집중 — 파급 효과' 빌드로 시작`, 없으면 `이 무기로 시작 (빌드 자유)`. 시작 시 `applyChoice({kind:'variant'})` → direction_lock 동시 설정. 로그 run 헤더 `bld`.
- **홈**: 메타 `🔒 빌드`. 칸 행 아래 체크리스트(`.chk`): `[S] 이름 · 필수 n/N` / 필수 행 ☑☐(칸, 미보유인데 칸이 찼으면 `지금 ○○`) / 신 3(등장 ✓) / 융합·끝내기 진행 바(`대기`=조건 완성) / 접기: 보조·망치·메모.
- **은혜·망치 시트**: 배지 `목표`(필수) · `목표 보조` · `끝내기`(융합). 엔진이 주고 badgeHtml이 그린다.
- **관리**: `빌드 카드` 칩(무기·양상의 전 변형, 강함 표시). 탭 = 변경, 같은 것 다시 탭 = 해제. 로그 `{t:'build', v}`.
"""
    save(P('ui', 'SPEC.md'), s); print('SPEC.md: §10')

i = load(P('data', 'ISSUES.md'))
if '여왕의 강권 B→A' not in i:
    i = i.rstrip('\n') + """

## [P2→반영 2026-10-26] 여왕의 강권 B→A, 왕의 강권은 모로스 전용 (8-B)

1-C는 "검색: Moros = Hera Sworn Strike + Zeus Heaven Flourish + King's Ransom"을 멜리노에 횃불 공격 꾹의 목표 융합으로 합쳤다. 멜리노에 헤라 공격·마력 빌드의 끝내기는 반대 방향인 **여왕의 강권**(제우스 은혜를 버리고 헤라 +4Lv) — 사용자 첫 클리어(2026-10-01) 빌드가 정확히 이것. 왕의 강권은 `flames_hold_moros_kings` 변형(모로스 전용)으로 분리. 둘은 서로를 파괴하므로 한 변형에 하나만.

## [P2] 아르카나 커뮤니티 세팅 — 사용자 입력 대기 (2026-10-26, 8-E)

앱 추천(이해도 27)과 로그에 기록된 실제 세팅 12장이 같다. 사용자가 "커뮤니티에서 받은 세팅"이 다르다고 하므로 그 세팅을 받아 카드 단위로 비교해야 한다. 나무위키 `하데스 2/아르카나`는 WebFetch 404(문서명 다름), 웹 검색은 영문 가이드만 — 인앱 브라우저로 재수집.
"""
    save(P('data', 'ISSUES.md'), i); print('ISSUES.md: 8단계 2건')

b = load(P('data', 'BUILD_DIRECTIONS.md'))
if '## 8단계 부록' not in b:
    b = b.rstrip('\n') + """

## 8단계 부록 — 빌드 카드 (2026-10-26)

방향은 "합친" 단위고, 그 아래 `variants`가 커뮤니티 빌드 **원형**이다. 22방향 59변형. 생성·검산은 `data/patch_8_variants.py` (한글명으로 쓰고 id로 변환; 필수 은혜의 신 ⊆ 주요 신, 융합 신 ⊆ 주요 신+1, 칸당 1개). 신뢰 ◎ = 출처 2개 이상 또는 실플레이 / ○ = 출처 1 / △ = 추론. 강함 S = 커뮤니티 1티어·★4 이상·"정석/최적" / A = 추천 레시피 / B = 양상 자체 평가 낮음.

예: 횃불 공격 꾹 — ① 헤라 집중(파급 효과 → **여왕의 강권**, ◎S, 실플레이 첫 클리어) ② 헤라 공격 + 제우스 기술(◎S, lee 최적) ③ 잔불·암운·동결 3신 코어(◎S, dc51882 ①) ④ 모로스 왕의 강권(○A, 모로스 전용).
"""
    save(P('data', 'BUILD_DIRECTIONS.md'), b); print('BUILD_DIRECTIONS.md: 부록')

sc = load(P('data', 'SCHEMA.md'))
if 'variants' not in sc:
    sc = sc.rstrip('\n') + """

### `build_directions.json` 방향의 `variants[]` (8단계, 2026-10-26)

| 필드 | 뜻 |
|---|---|
| `id`, `name_ko` | 변형 id · 이름(" — " 앞이 짧은 이름, 이유 문구에 쓰임) |
| `trust` | `high`(◎ 출처 2+ 또는 실플레이) / `mid`(○ 출처 1) / `low`(△ 추론) |
| `strength`, `strength_note` | S/A/B + 근거 한 줄 (엔진 입력 아님, 표시용) |
| `main_gods` | 신 id 3개, 순서 = 중요도 |
| `must` | 은혜 id. 칸 점유 은혜는 칸당 1개 = 그 변형의 칸 1순위. 칸 미점유(한 핏줄 등)도 가능 |
| `support` | 보조 은혜 id (4번째 신 것도 허용) |
| `target_duos` | 융합 id |
| `finisher` | `{duo, note}` 또는 null — 끝내기 융합(강권류: 받으면 한쪽 신 은혜가 사라짐) |
| `hammers` | 선택. 없으면 방향 것 |
| `aspects` | 선택. 있으면 그 양상에서만 표시 |
| `note`, `sources` | 메모 · 출처 태그 |
"""
    save(P('data', 'SCHEMA.md'), sc); print('SCHEMA.md: variants')
