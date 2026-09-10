# -*- coding: utf-8 -*-
"""1-D (오퍼스): 아테나·디오니소스 추가.
둘 다 지상(올림포스 산) 이벤트 조우형. 칸을 차지하지 않고 융합·정기도 없다 → type: guest.
아테나는 고르곤 아뮬렛(죽음 저항 없을 때)으로 지하에서도 등장 가능.
출처: fandom Athena/Dionysus Boons (Hades II) + 나무위키 은혜 2.10·2.11(한글명)."""
import io, os, json, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)
LJ = lambda p: json.load(io.open(p, encoding='utf-8'))
SJ = lambda p, d: io.open(p, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1))
def sub(s, old, new, tag):
    if old not in s: print('패턴 못 찾음:', tag); sys.exit(1)
    return s.replace(old, new, 1)

SRC = ["wiki", "namu"]
B = lambda **kw: dict(verified=True, source=SRC, prereq=None, occupies_slot=False, **kw)

ATHENA = [
 B(id="athena_divine_dash", god="athena", name_ko="신성한 돌진", name_en="Divine Dash", slot="passive",
   affects=["sprint"], effect="돌진이 경로상 적에 피해 + 잠시 반사",
   rarity_scaling="돌진 피해 10/15/20/25", tags=["deflect", "armor", "beginner_safe"],
   notes="반사 0.35초 + 그동안 완전 무적. 헤르메스 잰 발걸음과 궁합"),
 B(id="athena_defensive_posture", god="athena", name_ko="수비 태세", name_en="Defensive Posture", slot="passive",
   affects=[], effect="피격 후 2초간 무적", rarity_scaling="재사용 13/11/9/7초",
   tags=["armor", "beginner_safe"]),
 B(id="athena_stalwart_stand", god="athena", name_ko="꿋꿋한 저항", name_en="Stalwart Stand", slot="passive",
   affects=["magick"], effect="지역마다 보충되는 죽음 저항 +1, 마력 집중",
   rarity_scaling="마력 집중 150/125/100/75", tags=["heal", "armor", "beginner_safe"],
   notes="죽음 저항 취급이라 용력(Strength) 아르카나와 상충"),
 B(id="athena_renewed_faith", god="athena", name_ko="되찾은 신념", name_en="Renewed Faith", slot="passive",
   affects=[], effect="소모한 죽음 저항 전부 보충 + 효과 상승",
   rarity_scaling="회복량 +10/15/20/25%", tags=["heal", "beginner_safe"]),
 B(id="athena_phalanx_shot", god="athena", name_ko="방진 탄환", name_en="Phalanx Shot", slot="passive",
   affects=["special"], effect="기술이 반사 투사체 발사 (2초 재장전)",
   rarity_scaling="투사체 피해 10/15/20/25", tags=["deflect", "armor"]),
 B(id="athena_mental_block", god="athena", name_ko="정신 방벽", name_en="Mental Block", slot="passive",
   affects=["cast"], effect="마법이 범위 피해 + 잠시 반사",
   rarity_scaling="피해 40/60/80/100", tags=["deflect", "armor", "cast", "aoe"]),
 B(id="athena_righteous_pike", god="athena", name_ko="정의의 창끝", name_en="Righteous Pike", slot="passive",
   affects=["magick"], effect="마력 90 사용마다 적 3체에 창 낙하",
   rarity_scaling="창 피해 150/200/250/300", tags=["omega", "aoe"],
   notes="Ω를 자주 쓰는 무기(횃불 Ω공격)와 시너지"),
 B(id="athena_task_force", god="athena", name_ko="전담 지원", name_en="Task Force", slot="passive",
   affects=["hex"], effect="신력 비술을 지역마다 여러 번 사용",
   rarity_scaling="추가 +1/2/3/4회", tags=["hex"],
   notes="티폰 격파 후 해금. 신력 비술 보유 시에만 등장. 비술 빌드에 필수급"),
]

DIONYSUS = [
 B(id="dionysus_tipsy_shot", god="dionysus", name_ko="알딸딸 탄", name_en="Tipsy Shot", slot="passive",
   affects=["cast"], effect="마법 조준 대형 폭탄, 착탄점에 마법진",
   rarity_scaling="폭발 피해 300/450/600/750", tags=["cast", "ranged_cast", "aoe"]),
 B(id="dionysus_worry_free", god="dionysus", name_ko="천하태평", name_en="Worry Free", slot="passive",
   affects=[], effect="최대 체력 대폭 증가, 단 체력 수치가 안 보임",
   rarity_scaling="최대 체력 +50~80 / +70~100 / +90~120 / +110~140", tags=["max_hp"],
   notes="증가폭이 커서 평가가 좋다. 체력이 안 보이는 것은 분수 등으로 어림 가능"),
 B(id="dionysus_drunken_stupor", god="dionysus", name_ko="인사불성", name_en="Drunken Stupor", slot="passive",
   affects=["omega_attack", "omega_special"], effect="Ω 동작이 처음 맞히는 적에 숙취 부여",
   rarity_scaling="숙취 피해 50/75/100/125 (0.5초)", tags=["curse_apply:hangover", "dot", "omega"],
   notes="적당 1회만 적용. 재부여 안 됨"),
 B(id="dionysus_bounce_back", god="dionysus", name_ko="회복 탄력성", name_en="Bounce Back", slot="passive",
   affects=[], effect="교전 종료 시 그 전투에서 잃은 체력 일부 회복",
   rarity_scaling="회복 50/60/70/80%", tags=["heal", "beginner_safe"]),
 B(id="dionysus_bottomless_drink", god="dionysus", name_ko="끝없는 축배", name_en="Bottomless Drink", slot="passive",
   affects=[], effect="교전마다 포도 주스 등장, 마시면 다음 행동 위력 +100",
   rarity_scaling="재등장 10/9/8/7초", tags=[],
   notes="다타 Ω(쌍검 Ω기술 등)에서 타격마다 +100이라 특히 강함"),
 B(id="dionysus_happy_haze", god="dionysus", name_ko="둥실둥실", name_en="Happy Haze", slot="passive",
   affects=[], effect="8초마다 축제 안개 등장, 안에서 피해 증가 + 적 기절",
   rarity_scaling="안개 내 피해 +30/40/50/60%", tags=["aoe", "beginner_safe"]),
 B(id="dionysus_personal_loan", god="dionysus", name_ko="개인 융자", name_en="Personal Loan", slot="passive",
   affects=[], effect="금화 전부 잃고 다음 수호자 격파 후 이자와 함께 회수",
   rarity_scaling="추가 금화 +300/400/500/600", tags=["meta"]),
 B(id="dionysus_reckless_abandon", god="dionysus", name_ko="흥청망청", name_en="Reckless Abandon", slot="passive",
   affects=["attack"], effect="공격이 정확히 5 / 55 / 555 무작위 피해",
   rarity_scaling="최대 피해 확률 5/7/9/11%", tags=["per_hit"],
   notes="공격 피해가 고정으로 대체된다. 타격 수 많은 무기엔 이득, 단타 무기(도끼)엔 치명적. 디오니소스 친밀도 4단계 필요"),
]
SJ(P('data', 'boons', 'athena.json'), ATHENA)
SJ(P('data', 'boons', 'dionysus.json'), DIONYSUS)
print('boons/athena.json 8종, boons/dionysus.json 8종')

# ── gods.json ──
g = LJ(P('data', 'gods.json'))
if not any(x['id'] == 'athena' for x in g):
    idx = next(i for i, x in enumerate(g) if x['id'] == 'artemis')
    g[idx:idx] = [
      {"id": "athena", "name_ko": "아테나", "name_en": "Athena", "type": "guest", "curse": "none", "curse_ko": None,
       "elements": [], "theme": "반사(적 공격 되돌리기)와 죽음 저항. 칸을 차지하지 않아 어떤 빌드에도 얹을 수 있음",
       "beginner_note": "지상 올림포스 산에서 밤당 1회 조우. 고르곤 아뮬렛을 끼면(죽음 저항이 없을 때) 지하에서도 등장. 생존이 크게 오르니 만나면 챙길 것",
       "verified": True, "source": SRC},
      {"id": "dionysus", "name_ko": "디오니소스", "name_en": "Dionysus", "type": "guest", "curse": "hangover", "curse_ko": "숙취",
       "elements": [], "theme": "숙취(지속 피해)·축제 안개·포도 주스. 이득이 큰 대신 위험도 있는 은혜가 섞여 있음",
       "beginner_note": "지상 3지역 이벤트 방에서 조우. 천하태평·회복 탄력성은 생존에 크게 도움. 흥청망청은 무기에 따라 독이 됨",
       "verified": True, "source": SRC},
    ]
    SJ(P('data', 'gods.json'), g); print('gods.json: athena, dionysus 추가')

# ── 알딸딸 탄 상충: 마법 변형 계열 (위키 "Cannot be combined with") ──
def add_pair(objs, a, b, reason):
    for x, y in ((a, b), (b, a)):
        o = next((z for z in objs if z['id'] == x), None)
        if o is None: continue
        o.setdefault('conflicts', [])
        if y not in o['conflicts']: o['conflicts'].append(y)
        o.setdefault('conflict_reason', reason)
R = "마법 변형 계열 - 동시 채용 불가 (위키 명시)"
CAST_MOD = ['zeus_lightning_lance', 'hestia_glowing_coal', 'demeter_local_climate', 'poseidon_tidal_ring']
import glob
frags = {p: LJ(p) for p in glob.glob(P('data', 'boons', '*.json'))}
allb = [b for arr in frags.values() for b in arr]
for other in CAST_MOD:
    add_pair(allb, 'dionysus_tipsy_shot', other, R)
duos = LJ(P('data', 'duo_legendary.json'))
add_pair(allb + duos, 'dionysus_tipsy_shot', 'duo_demeter_ares', R)
for p, arr in frags.items(): SJ(p, arr)
SJ(P('data', 'duo_legendary.json'), duos)
print('알딸딸 탄 ↔ 마법 변형 5종 상충 (양방향)')

# ── build_directions: 도끼 단발 방향에서 흥청망청 회피 ──
bd = LJ(P('data', 'build_directions.json'))
d = next(x for x in bd['weapons']['axe']['directions'] if x['id'] == 'axe_heavy_attack')
if 'dionysus_reckless_abandon' not in d['avoid_boons']:
    d['avoid_boons'].append('dionysus_reckless_abandon')
    d['avoid_reason'] += ' 흥청망청은 공격 피해를 5/55/555로 고정해 단타 무기엔 치명적'
    SJ(P('data', 'build_directions.json'), bd); print('도끼 단발 방향: 흥청망청 회피 추가')

# ── 파이프라인·검증 ──
p = P('data', 'derive_slots.py'); s = io.open(p, encoding='utf-8').read()
if '"athena"' not in s:
    s = sub(s, 'NON_SLOT_GODS = {"hermes", "artemis"}', 'NON_SLOT_GODS = {"hermes", "artemis", "athena", "dionysus"}', 'NON_SLOT')
    io.open(p, 'w', encoding='utf-8').write(s); print('derive_slots.py: NON_SLOT_GODS')

p = P('data', 'merge.js'); s = io.open(p, encoding='utf-8').read()
if "'athena'" not in s:
    s = sub(s, "'hermes', 'artemis']", "'hermes', 'artemis', 'athena', 'dionysus']", 'merge order')
    io.open(p, 'w', encoding='utf-8').write(s); print('merge.js: 순서 추가')

p = P('data', 'validate.js'); s = io.open(p, encoding='utf-8').read()
if "'hangover'" not in s:
    s = sub(s, "'marked', 'morph', 'charm', 'shine', 'none'", "'marked', 'morph', 'charm', 'shine', 'hangover', 'none'", 'CURSES')
    s = sub(s, " && k.god !== 'athena'", "", 'athena 땜질 제거')
    io.open(p, 'w', encoding='utf-8').write(s); print('validate.js: hangover 추가, athena 예외 제거')

p = P('engine', 'weights.js'); s = io.open(p, encoding='utf-8').read()
if "'athena'" not in s:
    s = sub(s, "NON_POOL_GODS: ['hermes', 'artemis', 'selene', 'chaos'],",
                "NON_POOL_GODS: ['hermes', 'artemis', 'selene', 'chaos', 'athena', 'dionysus'],", 'NON_POOL')
    io.open(p, 'w', encoding='utf-8').write(s); print('weights.js: NON_POOL_GODS')

p = P('data', 'SCHEMA.md'); s = io.open(p, encoding='utf-8').read()
if 'guest(' not in s:
    s = sub(s, '"type": "core",            // core(핵심 슬롯 제공, 선택지 등장) | encounter(아르테미스 등 조우형) | hermes | selene | chaos | npc',
                '"type": "core",            // core(핵심 슬롯 제공, 선택지 등장) | guest(아테나·디오니소스 — 지상 이벤트 조우, 칸 미점유, 융합·정기 없음, 신 풀 미포함) | encounter(아르테미스 등 조우형) | hermes | selene | chaos | npc', 'SCHEMA type')
    io.open(p, 'w', encoding='utf-8').write(s); print('SCHEMA.md: guest 타입')
