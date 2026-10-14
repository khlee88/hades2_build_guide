# -*- coding: utf-8 -*-
"""6-A 조사 반영 (오퍼스, 2026-10-14) — 은백색 해골·검은빛 외투.

출처 (2026-10-14 인앱 브라우저 열람):
- 나무위키 Hades II/무기 3.5·3.6 — 위력표, 운용 서술, 강화 목록(망치) 한글명·수치·[양상×]/[양상 전용] 표기, 양상 평가
- Hades Wiki(Fandom) Argent_Skull·Black_Coat — 망치 영문명 전량, 무브셋 수치
- Lee Reamsnyder 가이드 — 양상별 Winning combo / Hammers of note / Build recipes (해골 4·외투 4)
수치 불일치는 RESEARCH_6A.md에 기록. 방향(build_directions)은 6-B 페이블 담당이라 여기서 쓰지 않는다.
"""
import io, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WP = os.path.join(ROOT, 'data', 'weapons.json'); HP = os.path.join(ROOT, 'data', 'hammers.json')
VJ = os.path.join(ROOT, 'data', 'validate.js')
def load(p): return json.load(io.open(p, encoding='utf-8'))
def save(p, o): io.open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(o, ensure_ascii=False, indent=1) + '\n')
SRC = ['wiki', 'namu', 'lee']

ws = load(WP)
W = {w['id']: w for w in ws}
if W['skull'].get('aspects'):
    print('weapons.json: 이미 적용됨')
else:
    W['skull'].update({
     'moveset': {
      'attack': '포환 투척 40 — 첫 적에게 범위 피해. 포환 4발로 시작, 던진 포환은 기술(돌진)로 회수하거나 가까이 가서 줍는다(자동 귀환은 매우 느림). Ω 공격은 마력 10으로 지정 지점에 포환을 던져 150',
      'special': '전방 돌진 45 + 경로의 포환 회수. **무적 없음**. Ω 기술은 마력 20으로 더 멀리 돌진하며 좌우로 투사체 100×4 — **돌진 중 무적**',
      'cast': '기본 마법진',
     },
     'core_slots': ['attack', 'special'],
     'style': '원거리 범위 투척. 공격으로 포환을 던지고 기술(돌진)로 회수하는 루프가 전부 — 멀리서 던지기만 하면 탄이 떨어져 화력이 안 나온다. Ω 공격은 싸고(마력 10) 광역, Ω 기술은 무적 이동기',
     'beginner_note': '기술 돌진은 무적이 없다(Ω 기술만 무적). 탄환 회수·일제 발사·귀신 들린 탄환 망치가 판을 바꾼다. 페르세포네 양상이 첫 클리어용으로 무난',
     'aspects': [
      {'id': 'skull_melinoe', 'name_ko': '멜리노에 양상', 'name_en': 'Aspect of Melinoë', 'unlocked_by_default': True,
       'effect': '회수하지 않은 포환 하나당 공격 위력 증가 (+3~+12, 6랭크 +21)', 'favors': ['attack', 'attack_power'],
       'favored_gods': ['aphrodite', 'apollo', 'hera', 'hephaestus'], 'beginner_rank': 2},
      {'id': 'skull_medea', 'name_ko': '메데이아 양상', 'name_en': 'Aspect of Medea', 'unlocked_by_default': False,
       'effect': '일반 공격이 곁에 머물다 기술 적중 또는 3초 후 크게 폭발. 일반 공격·기술 피해 +30~90% (6랭크 +135%)', 'favors': ['attack', 'special', 'pct_dmg'],
       'favored_gods': ['zeus', 'ares', 'hephaestus', 'hera'], 'beginner_rank': 2},
      {'id': 'skull_persephone', 'name_ko': '페르세포네 양상', 'name_en': 'Aspect of Persephone', 'unlocked_by_default': False,
       'effect': 'Ω 기술이 발아 — 올림포스 신의 피해 효과로 게이지가 차면 다음 Ω 기술 최대 +2초, 방향 조절 가능, 사용 중 무적. 받는 은혜 레벨 무작위 상승(최대 +2~+6, 6랭크 +9)', 'favors': ['omega_special', 'boon_level'],
       'favored_gods': ['hephaestus', 'aphrodite', 'demeter', 'hestia'], 'beginner_rank': 1},
      {'id': 'skull_hel', 'name_ko': '헬 양상', 'name_en': 'Aspect of Hel', 'unlocked_by_default': False, 'hidden': True,
       'effect': '서리 앉은 장발 — 공격이 포환 없이 3연사, 기술이 적 추적. Ω 기술 후 3초간 발키리(공격 끊김 없는 연사, Ω 불가). 발키리 공속 +5~+35%', 'favors': ['attack_speed', 'per_hit', 'omega_special'],
       'favored_gods': ['hestia', 'zeus', 'poseidon', 'hera'], 'beginner_rank': 3},
     ],
     'verified': True, 'source': SRC,
    })
    W['skull'].pop('notes', None)
    W['coat'].update({
     'name_en': 'Black Coat (Xinth)',
     'moveset': {
      'attack': '주먹 2연타 40-40, 넉백. 돌진 공격 15×3. Ω 공격은 마력 1~30을 충전하는 동안 **정면 방어막(투사체 삭제, 대부분의 공격 방어)** → 놓으면 30~300 폭발. 장판·확장 고리류는 못 막는다',
      'special': '유도 미사일 2발 30×2 — 공격과 동시에 쓸 수 있다. Ω 기술은 마력 5~15로 록온해 미사일 1~6발(발당 40), 충전 중 돌진 불가. 날아가는 중에 다시 록온하면 앞 미사일이 사라진다',
      'cast': '기본 마법진',
     },
     'core_slots': ['attack', 'special'],
     'style': '근접 주먹 + 유도 미사일 혼합. 기술 → 공격 → 공격 반복 — 공격이 기술 후딜을 취소한다. Ω 공격 충전 = 정면 방어(크로노스 낫·돌진도 막는다)',
     'beginner_note': '마력 소모가 커서 마력 회복 은혜 필수. 돌진 공격이 3타라 포세이돈·헤스티아·정전기 충격과 궁합. 양상 평가가 크게 갈린다(닉스·시바 > 멜리노에 > 셀레네)',
     'aspects': [
      {'id': 'coat_melinoe', 'name_ko': '멜리노에 양상', 'name_en': 'Aspect of Melinoë', 'unlocked_by_default': True,
       'effect': '공격·질주·이동 속도 증가 (+5~+20%, 6랭크 +35%)', 'favors': ['attack_speed', 'per_hit'],
       'favored_gods': ['zeus', 'poseidon', 'hestia', 'hera'], 'beginner_rank': 2},
      {'id': 'coat_selene', 'name_ko': '셀레네 양상', 'name_en': 'Aspect of Selene', 'unlocked_by_default': False,
       'effect': '전용 비술 천상 붕괴 즉시 습득 — 달빛을 떨어뜨려 피해 + 8초 달빛 저주(Ω 행동 추가 피해). 비술 발동 마력 100→40', 'favors': ['hex', 'omega'],
       'favored_gods': ['ares', 'hera', 'zeus'], 'beginner_rank': 4},
      {'id': 'coat_nyx', 'name_ko': '닉스 양상', 'name_en': 'Aspect of Nyx', 'unlocked_by_default': False,
       'effect': 'Ω 추진 — 질주를 길게 눌러 마력 30, 충돌 시 범위 피해 250(150) 후 5초 잔영: 공격·기술이 2갈래로 나뉘어 추가 피해(15~75%, 6랭크 105%)', 'favors': ['sprint', 'per_hit'],
       'favored_gods': ['hestia', 'poseidon', 'zeus', 'ares'], 'beginner_rank': 3},
      {'id': 'coat_shiva', 'name_ko': '시바 양상', 'name_en': 'Aspect of Shiva', 'unlocked_by_default': False, 'hidden': True,
       'effect': '정화의 은총 — Ω 공격이 돌격, 기술이 튕기는 수류탄. Ω 기술 폭발(3회)을 몸으로 흡수하면 파괴력 중첩(최대 2~6, 6랭크 8) → Ω 공격 시 중첩당 +50% 후 소모', 'favors': ['omega_attack', 'omega_special'],
       'favored_gods': ['apollo', 'demeter', 'hera', 'ares'], 'beginner_rank': 4},
     ],
     'verified': True, 'source': SRC,
    })
    W['coat'].pop('notes', None)
    save(WP, ws); print('weapons.json: 해골·외투 무브셋·양상 8개')

hs = load(HP)
if any(h['weapon'] == 'skull' for h in hs):
    print('hammers.json: 이미 적용됨')
else:
    def H(w, slug, ko, en, eff, r2, aff, tags, only=None, excl=None, bp=2):
        return {'id': f'{w}_{slug}', 'weapon': w, 'name_ko': ko, 'name_en': en, 'effect': eff, 'rank2': r2, 'affects': aff, 'tags': tags,
                'aspect_only': only, 'aspect_excluded': excl or [], 'conflicts': [], 'beginner_priority': bp, 'verified': True, 'source': ['wiki', 'namu']}
    NH, NC = ['skull_hel'], ['coat_shiva']
    new = [
     H('skull', 'bolstered_array', '탄환 보충', 'Bolstered Array', '포환 +2발', '포환 +3발', ['attack'], ['attack_power'], excl=NH),
     H('skull', 'fetching_array', '탄환 회수', 'Fetching Array', '포환이 자동으로 100% 빠르게 돌아옴', '200% 빠르게', ['attack'], ['attack_speed'], excl=NH, bp=1),
     H('skull', 'melting_tackle', '녹이는 돌입', 'Melting Tackle', '기술이 방어도에 +600 피해', None, ['special'], ['armor_break']),
     H('skull', 'wide_grin', '일제 발사', 'Wide Grin', '공격 시 모든 포환을 한꺼번에 흩뿌림 (Ω 공격에도 적용 — 한 번 비용으로 전탄)', None, ['attack', 'omega_attack'], ['aoe', 'omega_attack'], excl=NH),
     H('skull', 'rapid_driver', '고속 돌격', 'Rapid Driver', '기술 35% 빨라짐', '45%', ['special', 'omega_special'], ['attack_speed']),
     H('skull', 'colossus_driver', '굳건한 돌격', 'Colossus Driver', '기술 위력 +30%, 사용 중 받는 피해 -30%', '위력 +40%', ['special'], ['special_power', 'armor'], bp=1),
     H('skull', 'mega_driver', '가공할 돌격', 'Mega Driver', '기술 피해 +50%, 돌격이 빨라짐', '+75%', ['special'], ['special_power'], excl=NH),
     H('skull', 'twisting_crash', '비트는 격돌', 'Twisting Crash', 'Ω 기술 투사체가 바깥으로 날아간 뒤 안쪽으로 돌아옴', None, ['omega_special'], ['omega_special', 'aoe'], bp=1),
     H('skull', 'boosted_ignition', '향상된 발화', 'Boosted Ignition', '돌진·기술 뒤 공격이 빨라지고 위력 +15', '+20', ['attack'], ['attack_power', 'attack_speed'], excl=NH),
     H('skull', 'volatile_array', '불안정 탄환', 'Volatile Array', '포환이 떨어지는 곳에 공격 피해의 50%', '75%', ['attack'], ['aoe'], excl=NH),
     H('skull', 'possessed_array', '귀신 들린 탄환', 'Possessed Array', '포환을 회수하면 Ω 공격이 터지고 마력 25를 잃음', '마력 20', ['attack', 'omega_attack'], ['omega_attack'], excl=NH),
     H('skull', 'looming_ignition', '유예된 발화', 'Looming Ignition', '공격이 발사 후 0.7초에 걸쳐 피해·폭발 범위 +50%', '+75%', ['attack'], ['aoe', 'attack_power'], excl=NH),
     H('skull', 'venerated_relic', '숭배받는 유물', 'Venerated Relic', '발키리 상태 +3초 (그동안 Ω 기술 재사용 불가)', '+4초', ['attack'], ['attack_speed'], only='skull_hel', bp=1),
     H('skull', 'leering_glance', '흘기는 눈길', 'Leering Glance', '공격이 +1번 튕기며 둘째 적에게 피해 +15%', '+25%', ['attack'], ['aoe']),
     H('skull', 'runic_driver', '룬 가속', 'Runic Driver', '기술 탄속 증가, 맞힌 적 하나당 피해 +15%', '+25%', ['special'], ['special_power'], only='skull_hel', bp=3),
     H('skull', 'garmr_gaze', '가름의 응시', 'Garmr Gaze', '공격이 25% 멀리 날아가고 피해 +25%', '+35%', ['attack'], ['range', 'attack_power'], only='skull_hel'),
     H('skull', 'helheim_charge', '헬헤임 강습', 'Helheim Charge', 'Ω 공격이 연속 +2번 발동', None, ['omega_attack'], ['omega_attack'], only='skull_hel'),
     H('coat', 'melting_cross', '녹이는 십자', 'Melting Cross', '공격이 방어도에 +250 피해 (돌진 공격 제외)', None, ['attack'], ['armor_break'], bp=3),
     H('coat', 'rapid_frame', '고속 완갑', 'Rapid Frame', '공격 35% 빨라짐', '45%', ['attack'], ['attack_speed']),
     H('coat', 'reaper_frame', '초토화 완갑', 'Reaper Frame', '공격 범위 확대, 위력 +10', '+15', ['attack'], ['attack_power', 'aoe']),
     H('coat', 'siege_frame', '공성 완갑', 'Siege Frame', '공격이 더 멀리 닿고 피해 +30% (Ω 공격 사거리도)', '나무위키 표기 +75% — 확인 필요', ['attack', 'omega_attack'], ['range'], bp=1),
     H('coat', 'world_collider', '천체 충돌', 'World Collider', '완전 충전한 Ω 공격 위력 +100', '+140', ['omega_attack'], ['omega_attack'], bp=3),
     H('coat', 'exhaust_riser', '분출 상승', 'Exhaust Riser', '돌진 공격 +3타 (총 6타)', None, ['dash'], ['on_hit'], excl=NC, bp=1),
     H('coat', 'shimmering_rockets', '탄성 로켓', 'Shimmering Rockets', '기술이 적에게 2번 더 튕김', '3번', ['special'], ['aoe'], excl=NC, bp=1),
     H('coat', 'furious_rockets', '거센 로켓', 'Furious Rockets', '기술 발사·비행 80% 빨라짐', None, ['special'], ['attack_speed'], excl=NC),
     H('coat', 'launcher_frame', '발사 완갑', 'Launcher Frame', '공격 적중 시 25% 확률로 기술 자동 발사 (돌진 공격 포함)', '35%', ['attack', 'special'], ['on_hit'], excl=NC),
     H('coat', 'counter_barrage', '반격 세례', 'Counter Barrage', 'Ω 공격으로 방어하면 기술 5발 자동 발사 (3초 재장전)', None, ['omega_attack', 'special'], ['omega_attack'], excl=NC, bp=3),
     H('coat', 'sudden_salvo', '급속 포화', 'Sudden Salvo', 'Ω 기술 록온이 빨라지고 마력 -20%', '-30%', ['omega_special'], ['mana_cost_down'], excl=NC),
     H('coat', 'ripper_rockets', '작렬 로켓', 'Ripper Rockets', '같은 적에게 연속 적중하는 기술 5발까지 위력 +5씩', '+8씩', ['special'], ['special_power', 'boss_dmg'], excl=NC),
     H('coat', 'elephant_rockets', '코끼리 로켓', 'Elephant Rockets', '기술이 직선으로 날아가고 위력 +30', '+45', ['special'], ['special_power'], only='coat_shiva', bp=1),
     H('coat', 'counter_supreme', '파괴적 반격', 'Counter Supreme', 'Ω 공격으로 방어하면 파괴력 최대 +3', '+4', ['omega_attack'], ['omega_attack'], only='coat_shiva', bp=1),
     H('coat', 'awakened_rockets', '각성한 로켓', 'Awakened Rockets', 'Ω 기술 폭발을 흡수하면 기술 폭발도 일어나지만 마력 10을 잃음', '마력 6', ['omega_special'], ['aoe'], only='coat_shiva', bp=3),
     H('coat', 'mooncrest_riser', '달맞이 상승', 'Mooncrest Riser', '돌진 공격 피해 +40%, 범위 확대', '+60%', ['dash'], ['aoe'], only='coat_shiva', bp=3),
     H('coat', 'chakra_collider', '차크라 충돌', 'Chakra Collider', 'Ω 공격을 정조준할 수 있고, 성공 시 피해 +150%', '+225%', ['omega_attack'], ['omega_attack'], only='coat_shiva'),
    ]
    # 흘기는 눈길은 헬 전용 (fandom 표기상 aspect_only 누락 방지)
    for h in new:
        if h['id'] == 'skull_leering_glance': h['aspect_only'] = 'skull_hel'
    hs.extend(new); save(HP, hs); print('hammers.json: +%d (해골 17 · 외투 17) → %d' % (len(new), len(hs)))

v = io.open(VJ, encoding='utf-8').read()
old = "for (const w of weapons.filter((x) => x.unlock_order <= 4)) {"
if old in v:
    io.open(VJ, 'w', encoding='utf-8', newline='\n').write(v.replace(old, "for (const w of weapons.filter((x) => x.unlock_order <= 6)) {  // 6-A: 해골·외투 포함"))
    print('validate.js: 망치 수 검사를 무기 6개로')
