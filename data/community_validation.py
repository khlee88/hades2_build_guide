# -*- coding: utf-8 -*-
"""커뮤니티 빌드 검증 반영 (2026-09-10, 페이블).

build_directions.json은 1-C에서 페이블이 추론으로 만든 것이라 출처가 없었다.
나무위키 무기 문서 운용법(4무기 전 양상) + 디시 하데스 갤러리 뉴비 가이드 3편 +
Lee Reamsnyder 양상별 빌드 가이드(영문, 62 Fear 클리어 영상 첨부)를 대조해
방향·칸 선호·융합·망치·아르카나를 수정하고 방향마다 `sources`를 남긴다.
brokenbuilds.gg는 양상 설명이 인게임과 어긋나(모모스=회복?) 참고에서 제외.

실행: python data/community_validation.py  → 이후 node data/validate.js && node engine/test.js
"""
import io, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BD = os.path.join(ROOT, 'data', 'build_directions.json')
DL = os.path.join(ROOT, 'data', 'duo_legendary.json')

def load(p): return json.load(io.open(p, encoding='utf-8'))
def save(p, obj):
    io.open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(obj, ensure_ascii=False, indent=1) + '\n')

bd = load(BD)
if bd.get('_validated'):
    print('build_directions.json: 이미 반영됨'); sys.exit(0)

# 출처 약어. 방향별 sources에는 이 키를 쓴다.
bd['_sources'] = {
 'namu': 'https://namu.wiki/w/Hades%20II/%EB%AC%B4%EA%B8%B0 — 무기 문서 3.1~3.4 운용법·양상 평가 (2026-09 열람)',
 'dc51882': 'https://gall.dcinside.com/mgallery/board/view/?id=hades&no=51882 — 찐뉴비 은혜 빌드 가이드(+추천 양상), 2025-10',
 'dc49018': 'https://gall.dcinside.com/mgallery/board/view/?id=hades&no=49018 — 뉴비 양상별 은혜 트리: 지팡이·쌍검',
 'dc38884': 'https://gall.dcinside.com/mgallery/board/view/?id=hades&no=38884 — 초보용 클리어 빌드 추천 (지팡이 헤스티아 / 제우스 마법)',
 'lee': 'https://www.leereamsnyder.com/hades-2-build-guide — Build ideas and tips for all weapon aspects (영문, 양상별 레시피·망치·아르카나)',
}
bd['_validated'] = '2026-09-10 커뮤니티 5출처 대조. 방향별 sources 참조. 출처가 없는 항목은 페이블 추론(inferred)'
bd['_doc'] = '1-C 페이블 확정 → 2026-09-10 커뮤니티 검증 반영. 무기별 빌드 방향. 엔진은 이 파일을 그대로 로드한다. 설명은 BUILD_DIRECTIONS.md'

# ── 무기 공통 ────────────────────────────────────────────────────────────────
bd['always_take']['boons'].append('hermes_success_rate')            # lee: 모든 확률 효과 증폭
bd['always_take']['sources'] = ['lee:Very good boons']
sk = bd['survival_kit']
sk['passive'].insert(0, 'athena_renewed_faith')                     # lee: 단일 은혜 회복량 최고
sk['slot']['cast'] = ['demeter_arctic_ring', 'aphrodite_rapture_ring', 'apollo_solar_ring']  # 동결 마법이 '국밥'
sk['sources'] = ['dc51882:마법=데메테르 동결 고정', 'lee:Arctic Ring 최강 핵심 은혜 후보, Security System/Trusty Shield/Snow Queen']
bd['principles'].append('커뮤니티 정석: 마법 칸은 거의 항상 데메테르 설한 고리(광역 동결). 마력 회복 은혜는 Ω 의존 무기(횃불·모모스·카론)에서 1순위')
bd['principles'].append('신 풀은 기념품 없이 4명으로 고정된다(dc51882). 기념품으로 5번째 신을 부를 수 있으므로 3신 조합을 베이스로 짠다')

W = bd['weapons']

# ── 지팡이 ───────────────────────────────────────────────────────────────────
st = W['staff']
st['first_god_map'] = {
 'zeus': ['staff_special', 'staff_cast', 'staff_omega_attack'],
 'hestia': ['staff_special', 'staff_cast'],
 'poseidon': ['staff_special', 'staff_omega_attack'],
 'demeter': ['staff_cast', 'staff_special'],
 'apollo': ['staff_cast', 'staff_omega_attack', 'staff_special'],
 'aphrodite': ['staff_special', 'staff_omega_attack'],
 'hephaestus': ['staff_special', 'staff_omega_attack'],
 'hera': ['staff_omega_attack', 'staff_special'],
 'ares': ['staff_special', 'staff_cast'],
}
D = {d['id']: d for d in st['directions']}
d = D['staff_special']
d.update({
 'name_ko': '기술 월광탄', 'difficulty': 1, 'omega_dependent': False,
 'summary': '지팡이의 실전 주력은 기술(월광탄) — 빠르고 멀고 세다. 기술 칸에 잔불·암운·% 피해를 얹고 마법 칸은 설한 고리(동결)로 고정하면 커뮤니티 "국밥". 멜리노에 양상의 기술 위력 보너스가 그대로 붙고, 이중 월광탄 망치가 뜨면 화력 2배',
 'core_slots': ['special', 'cast'],
 'slot_prefs': {
  'special': ['hestia_flame_flourish', 'zeus_heaven_flourish', 'aphrodite_flutter_flourish', 'poseidon_wave_flourish', 'apollo_nova_flourish', 'hephaestus_volcanic_flourish', 'demeter_ice_flourish'],
  'cast': ['demeter_arctic_ring', 'aphrodite_rapture_ring', 'hestia_smolder_ring', 'zeus_storm_ring', 'poseidon_tidal_ring'],
  'attack': ['zeus_heaven_strike', 'hera_sworn_strike', 'hestia_flame_strike', 'demeter_ice_strike'],
  'magick': ['hestia_cardio_gain', 'apollo_lucid_gain', 'zeus_ionic_gain', 'poseidon_flood_gain'],
  'sprint': ['apollo_blinding_rush', 'demeter_frigid_rush'],
 },
 'support_boons': ['hestia_controlled_burn', 'zeus_double_strike', 'poseidon_slippery_slope', 'zeus_static_shock', 'hestia_pyro_technique', 'hestia_highly_flammable', 'artemis_killing_stroke', 'demeter_arctic_gale'],
 'target_duos': ['duo_hestia_demeter', 'duo_zeus_hestia', 'duo_hestia_poseidon', 'duo_poseidon_aphrodite', 'duo_hestia_aphrodite'],
 'hammers': ['staff_dual_moonshot', 'staff_shimmering_moonshot', 'staff_giga_moonburst', 'staff_rapid_moonshot', 'staff_aetheric_moonburst'],
 'arcana': ['the_huntress', 'the_furies', 'origination'],
 'aspects': ['staff_melinoe'],
 'sources': ['namu:멜리노에 양상 = 기술 위력+마력, Ω 기술 난사가 정석', 'dc38884:데메테르 마법+헤스티아 화염 기예+냉동 화상 = 초보 국밥, 이중 월광탄이 고점', 'dc49018:아프로 기예+포세 마법 / 포세 기예+미끄러운 경사+헤스티아 마법', 'lee:Dual Moonshot "you want this", Zeus·Aphrodite·Hephaestus special 레시피'],
})
d = D['staff_cast']
d.update({
 'name_ko': '마법진 (키르케)', 'difficulty': 2,
 'summary': '마법진에 피해를 붙이고 Ω 마법 강화 패시브(현지 기후·지하수 분출·후속 낙뢰)를 쌓는다. 키르케 양상은 동물 친구가 마법을 함께 시전해 커뮤니티 "1티어". 영롱한 마력(아폴론)이면 마법을 쓸수록 마력이 돈다',
 'slot_prefs': {
  'cast': ['demeter_arctic_ring', 'zeus_storm_ring', 'apollo_solar_ring', 'hestia_smolder_ring', 'hera_engagement_ring', 'ares_sword_ring', 'poseidon_tidal_ring'],
  'magick': ['apollo_lucid_gain', 'hera_born_gain', 'demeter_tranquil_gain', 'zeus_ionic_gain', 'poseidon_flood_gain'],
  'attack': ['zeus_heaven_strike', 'apollo_nova_strike', 'hera_sworn_strike', 'demeter_ice_strike'],
  'special': ['zeus_heaven_flourish', 'ares_vicious_flourish', 'hestia_flame_flourish'],
  'sprint': ['demeter_frigid_rush', 'apollo_blinding_rush'],
 },
 'support_boons': ['demeter_local_climate', 'poseidon_geyser_spout', 'zeus_double_strike', 'apollo_super_nova', 'apollo_prominence_flare', 'ares_meat_grinder', 'hermes_winners_circle', 'zeus_air_quality', 'demeter_arctic_gale', 'hera_fine_line', 'zeus_lightning_lance', 'artemis_lethal_snare'],
 'target_duos': ['duo_demeter_ares', 'duo_zeus_demeter', 'duo_zeus_apollo', 'duo_demeter_apollo', 'duo_poseidon_demeter'],
 'hammers': ['staff_dual_moonshot', 'staff_mirrored_thrasher', 'staff_rapid_moonshot', 'staff_wicked_thrasher', 'staff_melting_swipe', 'staff_giga_moonburst'],
 'arcana': ['the_furies', 'origination', 'the_sorceress', 'night', 'the_messenger'],
 'aspects': ['staff_circe', 'staff_momus'],
 'sources': ['namu:키르케 = 가장 직관적인 1티어, 제우스·데메테르 마법 핵심+아폴론 지원, 영롱한 마력 2배 효율', 'dc49018:데메 마법+현지 기후+지하수 분출 ★★★★ / 제우스 마법+후속 낙뢰+제우스 정기', 'dc38884:제우스 마법+청정한 대기 = 무기 무관 초보 빌드', 'lee:Circe — Zeus/Demeter/Apollo/Heph/Hestia cast, Lucid Gain·Winner\'s Circle·Geyser Spout·Local Climate·Meat Grinder'],
})
d = D['staff_omega_attack']
d.update({
 'name_ko': 'Ω 순환 난사 (모모스)', 'difficulty': 2,
 'summary': '마력 회복을 먼저 확보하고 Ω 공격·기술·마법을 돌려 쓴다. 모모스 양상(Ω 반복)의 본령. 한 핏줄(헤라)·파급 효과로 Ω마다 추가 피해, 잡초 박멸·현지 기후·지하수 분출로 Ω 위력 상향. 밤 아르카나가 Ω 교대에 치명타를 준다',
 'core_slots': ['magick', 'attack'],
 'slot_prefs': {
  'attack': ['hera_sworn_strike', 'zeus_heaven_strike', 'apollo_nova_strike', 'aphrodite_flutter_strike', 'demeter_ice_strike'],
  'magick': ['hera_born_gain', 'apollo_lucid_gain', 'poseidon_flood_gain', 'zeus_ionic_gain', 'demeter_tranquil_gain'],
  'special': ['zeus_heaven_flourish', 'hera_sworn_flourish', 'apollo_nova_flourish'],
  'cast': ['demeter_arctic_ring', 'zeus_storm_ring', 'apollo_solar_ring'],
  'sprint': ['apollo_blinding_rush', 'hera_nexus_rush'],
 },
 'support_boons': ['hera_fine_line', 'demeter_weed_killer', 'poseidon_geyser_spout', 'demeter_local_climate', 'hestia_controlled_burn', 'aphrodite_heart_breaker', 'ares_cut_above', 'athena_righteous_pike', 'zeus_arc_flash', 'artemis_shadow_pounce', 'poseidon_ocean_swell'],
 'target_duos': ['duo_poseidon_hera', 'duo_demeter_ares', 'duo_zeus_hephaestus', 'duo_zeus_apollo', 'duo_hera_hephaestus'],
 'hammers': ['staff_giga_moonburst', 'staff_mirrored_thrasher', 'staff_dual_moonshot', 'staff_rapid_thrasher', 'staff_rapid_moonshot', 'staff_wicked_thrasher'],
 'arcana': ['the_sorceress', 'night', 'eternity', 'origination'],
 'aspects': ['staff_momus', 'staff_melinoe'],
 'sources': ['namu:모모스 = 데메테르 동결 확정타, 강력 만월탄, 밤 아르카나 필수', 'dc49018:아폴론 공격+아폴론 마력+데메 마법+아폴론 전설 / 데메 마법+고기 분쇄+Ω 혼합', 'dc51882:헤라+포세이돈 파급 효과 빌드 — 마력 수급 후 Ω 난사 (멜리지팡이·모모스 ★★)', 'lee:Momus — 마력 회복 먼저, Zeus/Demeter cast, Giga Moonburst·Mirrored Thrasher·Dual Moonshot, Night arcana, Hostile Environment'],
})
st['directions'] = [D['staff_special'], D['staff_cast'], D['staff_omega_attack']]

# ── 쌍검 ────────────────────────────────────────────────────────────────────
bl = W['blades']
bl['first_god_map'] = {
 'zeus': ['blades_backstab_attack', 'blades_special_knives'],
 'hestia': ['blades_special_knives', 'blades_backstab_attack'],
 'poseidon': ['blades_special_knives', 'blades_backstab_attack'],
 'demeter': ['blades_special_knives', 'blades_backstab_attack'],
 'apollo': ['blades_backstab_attack', 'blades_omega_ambush'],
 'aphrodite': ['blades_omega_ambush', 'blades_backstab_attack'],
 'hephaestus': ['blades_backstab_attack'],
 'hera': ['blades_backstab_attack', 'blades_special_knives', 'blades_omega_ambush'],
 'ares': ['blades_backstab_attack', 'blades_omega_ambush'],
}
D = {d['id']: d for d in bl['directions']}
d = D['blades_backstab_attack']
d.update({
 'summary': '4연타로 타격 횟수가 압도적. 공격 칸은 아프로디테(최고 %)·아레스·헤스티아(잔불)·아폴론 무엇이든 좋고, 기술 칸에 제우스 암운을 얹어 콤보 사이에 던진다. 투척 단검 망치(돌진 공격마다 단검 7개)가 커뮤니티 최애. 춤추는 단검은 회수가 사라져 피함',
 'slot_prefs': {
  'attack': ['aphrodite_flutter_strike', 'ares_vicious_strike', 'hestia_flame_strike', 'apollo_nova_strike', 'hera_sworn_strike', 'poseidon_wave_strike', 'zeus_heaven_strike'],
  'special': ['zeus_heaven_flourish', 'hephaestus_volcanic_flourish', 'ares_vicious_flourish'],
  'cast': ['hera_engagement_ring', 'aphrodite_rapture_ring', 'demeter_arctic_ring', 'poseidon_tidal_ring'],
  'magick': ['aphrodite_glamour_gain', 'hestia_cardio_gain', 'zeus_ionic_gain'],
  'sprint': ['apollo_blinding_rush', 'hera_nexus_rush'],
 },
 'support_boons': ['zeus_static_shock', 'ares_grievous_blow', 'hestia_slow_cooker', 'aphrodite_secret_crush', 'apollo_back_burner', 'apollo_extra_dose', 'hestia_pyro_technique', 'artemis_lethal_snare'],
 'avoid_boons': ['hephaestus_volcanic_strike'],
 'avoid_reason': '화산 폭발은 쿨타임형이라 연타 공격 칸에선 낭비 — 헤파는 기술 칸에',
 'target_duos': ['duo_zeus_hephaestus', 'duo_hestia_demeter', 'duo_zeus_aphrodite', 'duo_zeus_poseidon', 'duo_poseidon_ares', 'duo_hestia_apollo'],
 'hammers': ['blades_trick_knives', 'blades_wicked_onslaught', 'blades_reaper_knives', 'blades_final_slice', 'blades_skulking_onslaught'],
 'avoid_hammers': ['blades_dancing_knives'],
 'avoid_hammer_reason': '기술이 돌아오지 않아 2회 타격·배후 보너스를 잃는다',
 'arcana': ['the_huntress', 'the_furies', 'origination', 'night'],
 'aspects': ['blades_melinoe'],
 'sources': ['namu:멜리노에 양상 — Ω 공격으로 배후 확보, 아폴론·망치로 배후 극대화', 'dc49018:아레스 공격+아프로 마법+아레스 전설 ★★★ / 아프로 공격+아프로 마력+아폴론 마법', 'lee:Trick Knives 최애, Wicked Onslaught·Reaper Knives·Final Slice, Dancing Knives 회피, Aphrodite/Apollo/Hera %, Poseidon·Hestia 고정 피해, Zeus special+Static Shock'],
})
d = D['blades_special_knives']
d.update({
 'name_ko': '기술 단검 (판)', 'difficulty': 2,
 'summary': '판 양상: 마법진 안의 적에게 단검이 유도. 타수가 많아 포세이돈(물보라)·헤스티아(잔불)·제우스(암운) 기술과 궁합, 마법은 데메테르 동결이나 아프로디테 황홀 고리로 묶기. 풀차징보다 끊어 쏘고, 투척 단검 망치면 마력 없이도 최상위',
 'slot_prefs': {
  'special': ['poseidon_wave_flourish', 'hestia_flame_flourish', 'zeus_heaven_flourish', 'aphrodite_flutter_flourish', 'demeter_ice_flourish', 'apollo_nova_flourish'],
  'cast': ['demeter_arctic_ring', 'aphrodite_rapture_ring', 'hera_engagement_ring', 'zeus_storm_ring'],
  'attack': ['demeter_ice_strike', 'zeus_heaven_strike', 'ares_vicious_strike'],
  'magick': ['hera_born_gain', 'zeus_ionic_gain', 'apollo_lucid_gain', 'demeter_tranquil_gain'],
  'sprint': ['apollo_blinding_rush', 'demeter_frigid_rush'],
 },
 'support_boons': ['poseidon_slippery_slope', 'zeus_lightning_lance', 'hestia_highly_flammable', 'hestia_controlled_burn', 'apollo_super_nova', 'apollo_back_burner', 'zeus_static_shock', 'artemis_killing_stroke', 'demeter_arctic_gale'],
 'target_duos': ['duo_poseidon_demeter', 'duo_hestia_aphrodite', 'duo_hestia_demeter', 'duo_zeus_poseidon', 'duo_poseidon_ares'],
 'hammers': ['blades_trick_knives', 'blades_sudden_flurry', 'blades_hidden_knives', 'blades_reaper_knives', 'blades_melting_sickle', 'blades_sureshot_flurry'],
 'arcana': ['the_sorceress', 'night', 'the_furies'],
 'aspects': ['blades_pan', 'blades_melinoe'],
 'sources': ['namu:판 — 제우스·헤스티아 마법 조준 은혜 필요, 타수 시너지(헤스티아·포세이돈·제우스), 기술 강화 망치', 'dc49018:포세 기예+데메 마법+번개 투창 ★★★★ / 헤스티아 기예+아프로 마법+불같은 열망 ★★★★', 'dc51882:판 = 포세이돈 빌드 ★★, 풀차징 말고 끊어 쏘기', 'lee:Trick Knives 압도적, Sudden Flurry·Hidden Knives, Poseidon special+Slippery Slope, Hestia special+Demeter Freezer Burn, Night arcana'],
})
d = D['blades_omega_ambush']
d.pop('requires_hammer', None)
d.update({
 'name_ko': '반격 Ω 공격 (아르테미스)', 'difficulty': 1,
 'summary': '아르테미스 양상: Ω 공격 충전 중 적 공격을 1회 막고 "반격" 치명타 버프. 아프로디테 공격 은혜를 최대한 강화하고 망치는 공격/Ω 공격 위주 — 빌드가 단순해 키르케와 함께 초보 최고 추천. 폭발적 암습(+400%)이 뜨면 한 방 2000+',
 'slot_prefs': {
  'attack': ['aphrodite_flutter_strike', 'ares_vicious_strike', 'hera_sworn_strike', 'apollo_nova_strike'],
  'magick': ['hera_born_gain', 'zeus_ionic_gain', 'poseidon_flood_gain', 'aphrodite_glamour_gain'],
  'special': ['ares_vicious_flourish', 'zeus_heaven_flourish', 'hera_sworn_flourish', 'apollo_nova_flourish'],
  'cast': ['demeter_arctic_ring', 'hera_engagement_ring', 'apollo_solar_ring'],
  'sprint': ['apollo_blinding_rush', 'hera_nexus_rush'],
 },
 'support_boons': ['demeter_weed_killer', 'aphrodite_heart_breaker', 'ares_grievous_blow', 'aphrodite_secret_crush', 'apollo_extra_dose', 'artemis_shadow_pounce', 'hermes_success_rate'],
 'target_duos': ['duo_apollo_aphrodite', 'duo_poseidon_aphrodite', 'duo_aphrodite_hera', 'duo_zeus_aphrodite'],
 'hammers': ['blades_sweeping_ambush', 'blades_skulking_onslaught', 'blades_trick_knives', 'blades_wicked_onslaught', 'blades_reaper_knives'],
 'arcana': ['the_sorceress', 'night', 'the_huntress', 'eternity'],
 'aspects': ['blades_artemis'],
 'sources': ['namu:아르테미스 — 아프로디테 공격 은혜 최대 강화 + 공격/Ω 공격 망치, 폭발적 암습 2000+ 치명타, 키르케와 함께 초보 최고 추천', 'dc49018:아프로 공격+아프로 마력+헤라/데메 마법 ★★☆', 'lee:Aphrodite attack + Hera/Zeus/Poseidon magick, Sweeping Ambush·Skulking Onslaught, Weed Killer·Heart Breaker, Ares attack+Grievous Blow'],
})
bl['directions'] = [D['blades_backstab_attack'], D['blades_omega_ambush'], D['blades_special_knives']]

# ── 횃불 ────────────────────────────────────────────────────────────────────
fl = W['flames']
fl['first_god_map'] = {
 'zeus': ['flames_omega_special_orbit', 'flames_omega_attack_spam'],
 'hestia': ['flames_omega_special_orbit', 'flames_omega_attack_spam'],
 'poseidon': ['flames_omega_special_orbit', 'flames_omega_attack_spam'],
 'demeter': ['flames_omega_special_orbit', 'flames_omega_attack_spam'],
 'apollo': ['flames_omega_attack_spam', 'flames_omega_special_orbit'],
 'aphrodite': ['flames_omega_attack_spam', 'flames_omega_special_orbit'],
 'hephaestus': ['flames_omega_attack_spam'],
 'hera': ['flames_omega_attack_spam', 'flames_omega_special_orbit'],
 'ares': ['flames_omega_attack_spam'],
}
D = {d['id']: d for d in fl['directions']}
d = D['flames_omega_attack_spam']
d.update({
 'name_ko': '공격 꾹 + 마력 순환', 'difficulty': 1,
 'summary': '횃불 기본 운용은 "Ω 기술 띄워두고 공격 꾹". 마력 회복 은혜가 최우선(천부적 마력), 공격 칸엔 % 피해(서약 일격) — 커뮤니티 정석은 헤라 공격 + 제우스 기술. 한 핏줄·파급 효과로 Ω마다 추가 피해가 터지고, 급속 연발 망치로 Ω 공격이 빨라진다',
 'slot_prefs': {
  'attack': ['hera_sworn_strike', 'hestia_flame_strike', 'aphrodite_flutter_strike', 'demeter_ice_strike', 'zeus_heaven_strike', 'apollo_nova_strike', 'ares_vicious_strike'],
  'magick': ['hera_born_gain', 'zeus_ionic_gain', 'apollo_lucid_gain', 'poseidon_flood_gain', 'hestia_cardio_gain', 'ares_grisly_gain'],
  'special': ['zeus_heaven_flourish', 'hestia_flame_flourish', 'poseidon_wave_flourish'],
  'cast': ['demeter_arctic_ring', 'aphrodite_rapture_ring'],
  'sprint': ['apollo_blinding_rush', 'demeter_frigid_rush'],
 },
 'support_boons': ['hera_fine_line', 'zeus_power_surge', 'zeus_static_shock', 'aphrodite_heart_breaker', 'poseidon_slippery_slope', 'hestia_slow_cooker', 'athena_righteous_pike', 'poseidon_ocean_swell', 'zeus_arc_flash'],
 'avoid_boons': [], 'avoid_reason': '',
 'target_duos': ['duo_poseidon_hera', 'duo_zeus_aphrodite', 'duo_zeus_hestia', 'duo_zeus_demeter', 'duo_hestia_demeter', 'duo_zeus_hera_kings_ransom'],
 'hammers': ['flames_sudden_burst', 'flames_enduring_coil', 'flames_clean_coil', 'flames_furious_blaze', 'flames_mega_blaze', 'flames_dividing_blaze', 'flames_leaden_blaze'],
 'arcana': ['the_sorceress', 'origination', 'the_furies', 'the_unseen'],
 'aspects': ['flames_melinoe', 'flames_moros'],
 'sources': ['namu:멜리노에 횃불 — 은혜·망치에 맞춰 유연하게, 마력 은혜 빠르게', 'dc51882:멜리횃불·모로스 ★★★ (헤스+제우스+데메 / 헤라+포세 Ω 난사 / 헤파 폭발) — Ω 기술 써놓고 평타 꾹', 'lee:Mel Flames — magick recovery 먼저(Hera Born Gain 최고), Hera attack+Zeus special, Fine Line+Righteous Pike, Poseidon special+Slippery Slope, Zeus special+Romantic Spark; Sudden Burst·Enduring Coil·Clean Coil', '검색:Moros = Hera Sworn Strike + Zeus Heaven Flourish + King\'s Ransom'],
})
d = D['flames_omega_special_orbit']
d.update({
 'difficulty': 1,
 'summary': 'Ω 기술(마력 25)로 불꽃 2개를 공전시키고 그 궤도로 공격을 쏜다. 모로스 양상은 잔류 혼령이 기술에 닿아 폭발 — 필드가 폭발로 뒤덮이는 전천후 양상. 기술 칸에 암운·잔불, 마력 회복은 즉시. 에오스 양상은 서광이 기술을 복사하므로 기술 위주 + 밤 아르카나',
 'slot_prefs': {
  'special': ['zeus_heaven_flourish', 'hestia_flame_flourish', 'poseidon_wave_flourish', 'aphrodite_flutter_flourish', 'demeter_ice_flourish', 'hera_sworn_flourish'],
  'magick': ['hera_born_gain', 'zeus_ionic_gain', 'poseidon_flood_gain', 'apollo_lucid_gain', 'demeter_tranquil_gain'],
  'attack': ['hera_sworn_strike', 'hestia_flame_strike', 'demeter_ice_strike', 'apollo_nova_strike', 'zeus_heaven_strike'],
  'cast': ['demeter_arctic_ring', 'aphrodite_rapture_ring'],
  'sprint': ['apollo_blinding_rush', 'demeter_frigid_rush'],
 },
 'support_boons': ['hestia_controlled_burn', 'zeus_double_strike', 'hestia_pyro_technique', 'hestia_highly_flammable', 'zeus_static_shock', 'poseidon_slippery_slope', 'demeter_weed_killer', 'zeus_arc_flash'],
 'target_duos': ['duo_zeus_hestia', 'duo_hestia_demeter', 'duo_zeus_demeter', 'duo_demeter_hephaestus', 'duo_hestia_aphrodite', 'duo_zeus_aphrodite'],
 'hammers': ['flames_sudden_burst', 'flames_clean_coil', 'flames_hidden_helix', 'flames_enduring_coil', 'flames_furious_blaze', 'flames_mega_blaze', 'flames_rising_helix'],
 'arcana': ['the_sorceress', 'night', 'origination', 'eternity'],
 'aspects': ['flames_moros', 'flames_eos', 'flames_melinoe'],
 'sources': ['namu:모로스 — Ω 기술 궤도로 공격 폭발, 망치는 Ω 기술 강화, 데메+헤스/데메+제우스/제우스+헤스/데메+헤파/아프로+헤스 융합 조합; 에오스 — 기술 위주, 아폴론 전설, 밤 아르카나', 'dc51882:에오스 = 공격 암운·기술 잔불 고정, 모로스 ★★★', 'lee:Moros — Sudden Burst 최고, Furious/Mega/Leaden Blaze, Clean Coil·Hidden Helix; Hera attack+Zeus special 최적; Eos — Hera special, Apollo attack+legendary'],
})
fl['directions'] = [D['flames_omega_attack_spam'], D['flames_omega_special_orbit']]

# ── 도끼 ────────────────────────────────────────────────────────────────────
ax = W['axe']
ax['first_god_map'] = {
 'zeus': ['axe_omega_whirlwind', 'axe_heavy_attack'],
 'hestia': ['axe_omega_whirlwind', 'axe_heavy_attack'],
 'poseidon': ['axe_omega_cleave', 'axe_heavy_attack'],
 'demeter': ['axe_heavy_attack', 'axe_omega_whirlwind'],
 'apollo': ['axe_heavy_attack', 'axe_omega_cleave', 'axe_omega_whirlwind'],
 'aphrodite': ['axe_heavy_attack', 'axe_omega_whirlwind'],
 'hephaestus': ['axe_heavy_attack'],
 'hera': ['axe_heavy_attack', 'axe_omega_cleave'],
 'ares': ['axe_heavy_attack', 'axe_omega_cleave'],
}
D = {d['id']: d for d in ax['directions']}
d = D['axe_heavy_attack']
d.update({
 'summary': '느리고 굵은 3연타. 공격 칸은 아프로디테(최고 %)·아폴론(범위+실명)·헤라(결속), 마법은 데메테르 동결로 선딜을 보호 — 커뮤니티 "근접 무기엔 아폴론·아프로디테 궁합 최고". 3타째 큰 참격은 익숙해지기 전엔 돌진 공격→1·2타→기술로 끊는다. 돌진 올려베기 망치가 뜨면 돌진 공격만 반복해도 됨',
 'core_slots': ['attack', 'cast'],
 'slot_prefs': {
  'attack': ['aphrodite_flutter_strike', 'apollo_nova_strike', 'hera_sworn_strike', 'demeter_ice_strike', 'hephaestus_volcanic_strike'],
  'cast': ['demeter_arctic_ring', 'aphrodite_rapture_ring', 'hera_engagement_ring', 'apollo_solar_ring'],
  'special': ['zeus_heaven_flourish', 'hestia_flame_flourish', 'hephaestus_volcanic_flourish', 'ares_vicious_flourish'],
  'magick': ['hephaestus_tough_gain', 'aphrodite_glamour_gain', 'zeus_ionic_gain', 'hestia_cardio_gain'],
  'sprint': ['demeter_frigid_rush', 'apollo_blinding_rush', 'hephaestus_smithy_rush'],
 },
 'support_boons': ['ares_grievous_blow', 'apollo_extra_dose', 'apollo_back_burner', 'artemis_lethal_snare', 'hermes_success_rate', 'artemis_pressure_points', 'hephaestus_security_system', 'hephaestus_trusty_shield', 'hephaestus_heavy_metal', 'hera_dying_wish'],
 'avoid_reason': '타격 수가 적어 정전기 충격 효율이 낮고, 물보라 넉백은 3타째를 빗나가게 한다(추론). 흥청망청은 공격 피해를 5/55/555로 고정해 단타 무기엔 치명적',
 'target_duos': ['duo_apollo_aphrodite', 'duo_hera_hephaestus', 'duo_demeter_aphrodite', 'duo_apollo_hephaestus', 'duo_hestia_demeter', 'duo_aphrodite_hera'],
 'hammers': ['axe_dashing_heave', 'axe_rapid_slash', 'axe_seething_marauder', 'axe_colossus_slash'],
 'avoid_hammers': ['axe_hell_splitter'],
 'avoid_hammer_reason': '공격이 가장 느린 3타로 고정 — 처형인의 도끼와 조합하면 강하지만 초보엔 위험',
 'arcana': ['the_huntress', 'the_furies', 'persistence', 'the_lovers', 'origination'],
 'aspects': ['axe_melinoe', 'axe_thanatos'],
 'sources': ['namu:근접 무기 특성상 아폴론·아프로디테 궁합 매우 좋음(실명·약화), 지옥 가르기+처형인의 도끼, 휩쓰는 맹공, 심령 소용돌이 고빈도', 'dc51882:증뎀(헤라·아프로·아폴론)+데메 마법 필수+시초 아르카나; 타나토스 ★★★ 초반엔 평타 위주', 'lee:Mel Axe — Aphrodite/Apollo/Hera attack + Demeter cast, Dashing Heave "king", Rapid Hack, Seething Marauder, Hell Splitter 회피, Huntress arcana, Ares special+Grievous Blow, Lethal Snare'],
})
d = D['axe_omega_whirlwind']
d.update({
 'name_ko': 'Ω 공격 회오리 (타나토스)',
 'summary': '타나토스 양상 표준: 공속 +40%로 평타를 치며 필멸 스택을 쌓고 Ω 공격 회오리(최대 11타)로 터뜨린다. "타격마다" 은혜(잔불·정전기)가 도끼인데도 폭발. 심령 소용돌이 망치가 핵심(회오리 중 이동·돌진 가능). 밤 아르카나·순백 사슴뿔로 치명타',
 'slot_prefs': {
  'attack': ['hestia_flame_strike', 'aphrodite_flutter_strike', 'apollo_nova_strike', 'hera_sworn_strike', 'zeus_heaven_strike', 'demeter_ice_strike'],
  'magick': ['aphrodite_glamour_gain', 'zeus_ionic_gain', 'hestia_cardio_gain', 'demeter_tranquil_gain', 'hephaestus_tough_gain'],
  'cast': ['demeter_arctic_ring', 'hestia_smolder_ring', 'zeus_storm_ring'],
  'special': ['zeus_heaven_flourish', 'hephaestus_volcanic_flourish', 'apollo_nova_flourish'],
  'sprint': ['apollo_blinding_rush', 'demeter_frigid_rush'],
 },
 'support_boons': ['demeter_weed_killer', 'zeus_static_shock', 'hestia_pyro_technique', 'hermes_success_rate', 'zeus_arc_flash', 'zeus_double_strike', 'artemis_shadow_pounce', 'apollo_back_burner'],
 'target_duos': ['duo_hestia_demeter', 'duo_apollo_aphrodite', 'duo_zeus_hestia', 'duo_zeus_hephaestus', 'duo_hera_ares'],
 'hammers': ['axe_psychic_whirlwind', 'axe_seething_marauder', 'axe_furious_whirlwind', 'axe_rapid_slash', 'axe_colossus_slash'],
 'arcana': ['the_huntress', 'night', 'the_sorceress', 'eternity'],
 'aspects': ['axe_thanatos', 'axe_melinoe'],
 'sources': ['namu:타나토스 — 공속 40%, 필멸 최대 20% Ω 치명타, 공속 빌드는 아레스 전설/아레스·헤라 융합, Ω 빌드는 아폴론 전설, 순백 사슴뿔', 'dc51882:타나토스 ★★★ 증뎀 빌드, 심령 소용돌이 먹으면 딜 체감 2배', 'lee:Thanatos — Aphrodite/Apollo/Hera attack + Demeter Weed Killer, Hestia attack+Demeter cast Freezer Burn, Zeus attack+Origination; Psychic Whirlwind 최고, Seething Marauder, Rapid Hack, Furious Whirlwind; Huntress+Night'],
})
d = D['axe_omega_cleave']
d.update({
 'name_ko': 'Ω 기술 가르기 (카론)', 'difficulty': 2,
 'summary': '카론 양상: 일반 마법으로 묶고 Ω 기술(가르기)로 마법진을 즉시 폭발 — Ω 마법 강화 은혜(지하수 분출·햇살 방사·고기 분쇄·현지 기후)를 전부 받는다. 영롱한 마력(아폴론)이 사실상 필수: 폭발마다 마력이 돌아온다. 강력 쪼개기로 2연발. 공격 버튼은 거의 안 쓴다',
 'slot_prefs': {
  'special': ['apollo_nova_flourish', 'hera_sworn_flourish', 'ares_vicious_flourish', 'aphrodite_flutter_flourish', 'hephaestus_volcanic_flourish'],
  'cast': ['poseidon_tidal_ring', 'apollo_solar_ring', 'demeter_arctic_ring', 'zeus_storm_ring', 'ares_sword_ring', 'hera_engagement_ring'],
  'magick': ['apollo_lucid_gain', 'hera_born_gain', 'zeus_ionic_gain', 'poseidon_flood_gain'],
  'attack': ['apollo_nova_strike', 'hera_sworn_strike'],
  'sprint': ['apollo_blinding_rush', 'demeter_frigid_rush'],
 },
 'support_boons': ['poseidon_geyser_spout', 'apollo_prominence_flare', 'apollo_super_nova', 'ares_meat_grinder', 'demeter_local_climate', 'demeter_arctic_gale', 'hermes_nimble_limbs', 'zeus_lightning_lance', 'hestia_glowing_coal', 'artemis_easy_shot'],
 'target_duos': ['duo_demeter_ares', 'duo_zeus_apollo', 'duo_poseidon_apollo', 'duo_hephaestus_ares', 'duo_poseidon_aphrodite'],
 'hammers': ['axe_giga_cleaver', 'axe_sudden_cleaver', 'axe_melting_shredder', 'axe_siege_shredder'],
 'arcana': ['the_sorceress', 'the_furies', 'origination', 'eternity'],
 'aspects': ['axe_charon'],
 'sources': ['namu:카론 — 마법·Ω 기술 특화, 아폴론 마법 궁합 최고, 제우스·헤스티아·하데스 마법 설치, 강력 쪼개기·아폴론 전설, 영롱한 마력 무한', 'dc51882:카론 = 아레스+제우스 빌드 ★★ (양상 자체가 사기)', 'lee:Charon — Apollo Lucid Gain 시작, Hera/Ares/Apollo special, Poseidon cast→Geyser Spout, Local Climate·Hostile Environment·Prominence Flare·Meat Grinder; Giga Cleaver·Sudden Cleaver·Melting Shredder; Sorceress+Furies+Origination(+Eternity), Night 무효'],
})
ax['directions'] = [D['axe_heavy_attack'], D['axe_omega_whirlwind'], D['axe_omega_cleave']]

# ── 아르카나·기념품 ───────────────────────────────────────────────────────────
abs_ = bd['arcana_beginner_set']
abs_['upgrade_path'] = ['the_messenger', 'the_swift_runner', 'the_lovers', 'origination', 'the_champions', 'the_moon']
abs_['sources'] = ['lee:필수 = 죽음 or 용력 / 리롤·자금 카드 / 불굴. 퓨리 자매+시초가 가장 유연한 화력. Ω 쓰면 마법사, 안 쓰면 사냥꾼. Ω 교대면 밤·영겁. 초보는 죽음', 'dc51882:증뎀 빌드는 시초(저주 2종) 켜는 게 핵심']
bd['keepsake_plan']['region1_note'] = '커뮤니티 정석은 1지역부터 원하는 신의 기념품으로 신 풀(4명)을 통제하는 것. 특정 융합을 노리면 아래 목록보다 그 신 기념품 우선 (dc51882, lee)'
bd['hex_beginner_sources'] = ['lee:Twilight Curse(황혼 저주) 무강화도 유용 +50% 피해, Wolf Howl 무적 회피, Phase Shift, Dark Side']

save(BD, bd)
print('build_directions.json: 커뮤니티 검증 반영')

# ── 융합·전설 power_tier 재조정 (커뮤니티 언급 빈도·평가 기준) ─────────────────
dl = load(DL)
TIER = {
 'duo_poseidon_hera': ('S', 'dc51882 빌드 6(파급 효과 Ω 난사) 전용 / lee Ripple Effect'),
 'duo_zeus_ares': ('S', 'dc51882 빌드 2 핵심 / lee Heinous Affront potent'),
 'duo_zeus_hephaestus': ('S', 'lee Master Conductor 반복 추천(쌍검·지팡이·횃불)'),
 'duo_zeus_aphrodite': ('S', 'lee Romantic Spark 반복 추천(지팡이·횃불·도끼)'),
 'duo_hestia_apollo': ('S', 'dc49018 "요즘 유행하는 온화한 바람 빌드" ★★★★★'),
 'duo_zeus_hera_kings_ransom': ('A', '검색: 모로스 헤라+제우스 빌드 핵심 / lee Queen\'s Ransom'),
 'duo_hera_ares': ('A', 'namu 타나토스 공속 빌드'),
 'leg_poseidon': ('S', 'lee: 판 쌍검·횃불에서 "legendary로 보스 shred" 반복'),
}
n = 0
for x in dl:
 if x['id'] in TIER:
  t, why = TIER[x['id']]
  if x.get('power_tier') != t:
   x['tier_note'] = '%s→%s (2026-09-10 커뮤니티): %s' % (x.get('power_tier'), t, why)
   x['power_tier'] = t; n += 1
save(DL, dl)
print('duo_legendary.json: power_tier %d건 조정' % n)
