# -*- coding: utf-8 -*-
"""8-B 빌드 카드(변형) 데이터 (페이블, 2026-10-26).

방향(direction)은 커뮤니티 빌드 여러 개를 칸별 순위로 합친 것이라 "어느 빌드를 타고 있는지"가 안 보였다(사용자: 매 선택이 단계별이라 학습이 느림).
각 방향 아래에 커뮤니티 빌드를 **그대로** `variants`로 둔다. 출처는 1-C/6-A/6-B에서 수집한 dc51882·dc49018·dc38884·lee·namu 요약과 실플레이 로그.

변형 필드:
  id, name_ko, trust(high=출처 2개+ 또는 실플레이 / mid=출처 1 / low=추론), strength(S/A/B)+strength_note,
  main_gods[2~3], fourth[(신, [융합])] (4번째 신 택1 — 주요 신 밖 융합은 여기), must[은혜 — 순서대로, 칸당 1개가 그 변형의 칸 1순위], support[], target_duos[], finisher{duo, note}|null,
  hammers[] (선택, 없으면 방향 것), aspects[] (선택, 특정 양상 전용), note, sources[]
은혜·융합·망치는 한글명으로 쓰고 스크립트가 id로 바꾼다 — 이름이 틀리면 즉시 실패.
함께: 여왕의 강권 B→A (첫 클리어 런 2026-10-01 근거), 공격 꾹 방향 target_duos에 추가.
"""
import io, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)
J = lambda f: json.load(io.open(P('data', f), encoding='utf-8'))
boons = J('boons.json'); duos = J('duo_legendary.json'); hammers = J('hammers.json'); gods = J('gods.json')
BD_PATH = P('data', 'build_directions.json'); BD = json.load(io.open(BD_PATH, encoding='utf-8'))
bn = {}
for b in boons: bn.setdefault(b['name_ko'], []).append(b['id'])
dn = {d['name_ko']: d for d in duos}
hn = {}
for h in hammers: hn.setdefault(h['name_ko'], []).append(h['id'])
gn = {g['name_ko']: g['id'] for g in gods}
GOD_SHORT = {'헤스': 'hestia', '데메': 'demeter', '아프로': 'aphrodite', '헤파': 'hephaestus'}

def boon(name):
    ids = bn.get(name); assert ids, '은혜 없음: %r' % name
    assert len(ids) == 1, '은혜 중복: %r %s' % (name, ids); return ids[0]
def duo(name):
    assert name in dn, '융합 없음: %r' % name; return dn[name]['id']
def ham(name, weapon):
    ids = [i for i in hn.get(name, []) if i.startswith(weapon + '_')]; assert len(ids) == 1, '망치 없음: %r %s' % (name, hn.get(name)); return ids[0]
def god(name):
    assert name in gn, '신 없음: %r' % name; return gn[name]

V = lambda **k: k
# ── 변형 정의 ─────────────────────────────────────────────
SPEC = {
 'staff_special': [
  V(id='staff_special_scorch_freeze', name_ko='잔불 기예 + 동결 마법 (국밥)', trust='high', strength='S', strength_note='dc38884 "초보 국밥", 이중 월광탄이 고점',
    gods=['헤스티아', '데메테르', '제우스'], must=['화염 기예', '설한 고리', '따스한 마력'], support=['화력 보강', '완전 연소', '불쏘시개', '혹한 강풍'],
    duos=['냉동 화상', '불벼락'], finisher=None, hammers=['이중 월광탄', '탄성 월광탄'],
    note='기술에 잔불을 얹고 마법으로 얼려 냉동 화상 폭발. 4번째 신은 제우스(불벼락)', sources=['dc38884:데메테르 마법+헤스티아 화염 기예+냉동 화상 = 초보 국밥', 'namu:멜리노에 = Ω 기술 난사 정석']),
  V(id='staff_special_aphro_poseidon', name_ko='애정 기예 + 물결 마법', trust='mid', strength='A', strength_note='dc49018 추천 레시피',
    gods=['아프로디테', '포세이돈', '제우스'], must=['애정 기예', '물결 고리', '대전된 마력'], support=['미끄러운 경사', '정전기 충격'],
    duos=['섬 휴양지', '감전 급류'], finisher=None, note='% 피해 기예 + 물보라로 묶기', sources=['dc49018:아프로 기예+포세 마법']),
  V(id='staff_special_poseidon_hestia', name_ko='파도 기예 + 미끄러운 경사 + 염화 마법', trust='mid', strength='A', strength_note='dc49018 추천 레시피',
    gods=['포세이돈', '헤스티아', '제우스'], must=['파도 기예', '염화 고리', '대전된 마력'], support=['미끄러운 경사', '화력 보강'],
    duos=['뜨거운 증기', '불벼락'], finisher=None, note='물보라 침수 + 잔불. 월광탄 타수로 침수 피해를 쌓는다', sources=['dc49018:포세 기예+미끄러운 경사+헤스티아 마법']),
 ],
 'staff_cast': [
  V(id='staff_cast_demeter_geyser', name_ko='동결 마법 + 현지 기후 + 지하수 분출', trust='high', strength='S', strength_note='dc49018 ★★★★, namu 키르케 1티어',
    gods=['데메테르', '포세이돈', '아폴론'], must=['설한 고리', '영롱한 마력', '현지 기후', '지하수 분출'], support=['혹한 강풍', '초신성', '신속 대응'],
    duos=['남녘 태풍', '자연 선택'], finisher=None, note='영롱한 마력으로 마법을 쓸수록 마력이 돈다. 키르케 동물 친구가 마법을 같이 시전', sources=['dc49018:데메 마법+현지 기후+지하수 분출 ★★★★', 'namu:키르케 = 제우스·데메테르 마법 핵심+아폴론 지원', 'lee:Circe — Lucid Gain·Geyser Spout·Local Climate']),
  V(id='staff_cast_zeus_storm', name_ko='폭풍 마법 + 후속 낙뢰 + 청정한 대기', trust='high', strength='A', strength_note='dc49018·dc38884 무기 무관 초보 빌드',
    gods=['제우스', '아폴론', '데메테르'], must=['폭풍 고리', '영롱한 마력', '후속 낙뢰', '청정한 대기'], support=['한 핏줄', '혹한 강풍'],
    duos=['눈부신 참사', '우박 폭풍'], finisher=None, note='마법진이 낙뢰를 반복. 데메테르가 오면 동결로 우박 폭풍', sources=['dc49018:제우스 마법+후속 낙뢰+제우스 정기', 'dc38884:제우스 마법+청정한 대기 = 무기 무관 초보 빌드']),
 ],
 'staff_omega_attack': [
  V(id='staff_omega_hera_poseidon', name_ko='헤라+포세 파급 효과 Ω 난사', trust='high', strength='S', strength_note='dc51882 빌드 ⑥, lee',
    gods=['헤라', '포세이돈', '제우스'], must=['서약 일격', '천부적 마력', '한 핏줄', '바다 너울'], support=['잡초 박멸', '실연의 아픔', '정의의 창끝'],
    duos=['파급 효과'], finisher=None, note='마력 수급 후 Ω 난사. Ω마다 균열·파도가 2회 터진다', sources=['dc51882:헤라+포세이돈 파급 효과 빌드 — 마력 수급 후 Ω 난사', 'lee:Momus — 마력 회복 먼저']),
  V(id='staff_omega_apollo', name_ko='아폴론 Ω 순환 (광휘 + 영롱한 마력)', trust='mid', strength='A', strength_note='dc49018 레시피',
    gods=['아폴론', '데메테르', '제우스'], must=['광휘 일격', '영롱한 마력', '설한 고리'], support=['현지 기후', '확인 사살', '화력 보강'],
    duos=['눈부신 참사', '우박 폭풍'], finisher=None, note='아폴론 전설(마법 2연발)이 뜨면 완성', sources=['dc49018:아폴론 공격+아폴론 마력+데메 마법+아폴론 전설']),
 ],
 'staff_anubis_zone': [
  V(id='staff_anubis_hera_aphro', name_ko='서약 일격 + 애정 기예 + 물결 마법', trust='high', strength='S', strength_note='dc49018 ★4.5',
    gods=['헤라', '아프로디테', '포세이돈'], must=['서약 일격', '애정 기예', '물결 고리', '넘치는 마력'], support=['잡초 박멸', '확인 사살'],
    duos=['섬 휴양지', '파급 효과'], finisher=None, note='헤라면 Ω 공격을 더 쓴다 (lee)', sources=['dc49018:헤라 공격+아프로 기예+포세 마법 ★4.5', 'lee:Anubis — Hestia/Hera/Poseidon/Zeus attack + Origination']),
  V(id='staff_anubis_hestia_zeus', name_ko='화염 일격 + 천상 기예 + 정전기', trust='high', strength='A', strength_note='dc49018 ★4',
    gods=['헤스티아', '제우스', '데메테르'], must=['화염 일격', '천상 기예', '정전기 충격', '따스한 마력'], support=['화력 보강'],
    duos=['불벼락', '냉동 화상'], finisher=None, note='장판 안에 모인 적에게 잔불·암운·연쇄 번개', sources=['dc49018:헤스티아 공격+제우스 기예+정전기 ★4']),
 ],
 'blades_backstab_attack': [
  V(id='blades_backstab_ares', name_ko='상해 일격 + 황홀 마법 + 아레스 전설', trust='high', strength='S', strength_note='dc49018 ★★★',
    gods=['아레스', '아프로디테', '제우스'], must=['상해 일격', '황홀 고리', '매혹적 마력'], support=['쓰라린 부상', '정전기 충격', '죽음의 덫'],
    duos=['잔학무도', '짜릿한 접촉'], finisher=None, note='4연타로 상처를 쌓고 황홀 고리로 묶는다. 아레스 전설이 뜨면 완성', sources=['dc49018:아레스 공격+아프로 마법+아레스 전설 ★★★', 'lee:Aphrodite/Apollo/Hera %, Zeus special+Static Shock']),
  V(id='blades_backstab_aphro_apollo', name_ko='애정 일격 + 매혹적 마력 + 아폴론 마법', trust='mid', strength='A', strength_note='dc49018 레시피',
    gods=['아프로디테', '아폴론', '제우스'], must=['애정 일격', '매혹적 마력', '태양 고리'], support=['빛나는 등판', '추가 처방', '은밀한 호감'],
    duos=['명랑한 기질', '짜릿한 접촉'], finisher=None, note='약화+실명으로 배후 공격 극대화', sources=['dc49018:아프로 공격+아프로 마력+아폴론 마법']),
  V(id='blades_backstab_flat', name_ko='화염 일격 + 천상 기예 + 정전기 (고정 피해)', trust='mid', strength='A', strength_note='lee 레시피',
    gods=['헤스티아', '제우스', '포세이돈'], must=['화염 일격', '천상 기예', '정전기 충격'], support=['완전 연소', '솥단지 예열', '미끄러운 경사'],
    duos=['불벼락', '뜨거운 증기'], finisher=None, note='타격 수가 많은 쌍검에 타격마다 고정 피해', sources=['lee:Poseidon·Hestia 고정 피해, Zeus special+Static Shock']),
 ],
 'blades_omega_ambush': [
  V(id='blades_ambush_aphro', name_ko='애정 일격 극대화 + 폭발적 암습', trust='high', strength='S', strength_note='namu 초보 최고 추천(키르케와 함께)',
    gods=['아프로디테', '헤라', '데메테르'], must=['애정 일격', '천부적 마력', '설한 고리'], support=['실연의 아픔', '은밀한 호감', '잡초 박멸', '그림자 급습'],
    duos=[], finisher=None, hammers=['폭발적 암습', '은밀한 맹습'], note='융합보다 공격 은혜 희귀도와 망치. 폭발적 암습이면 한 방 2000+', sources=['namu:아르테미스 — 아프로디테 공격 최대 강화', 'dc49018:아프로 공격+아프로 마력+헤라/데메 마법 ★★☆', 'lee:Aphrodite attack + Hera/Zeus/Poseidon magick']),
  V(id='blades_ambush_ares', name_ko='상해 일격 + 쓰라린 부상', trust='mid', strength='A', strength_note='lee 변형',
    gods=['아레스', '아프로디테', '제우스'], must=['상해 일격', '쓰라린 부상', '대전된 마력'], support=['실연의 아픔', '은밀한 호감'],
    duos=['잔학무도'], finisher=None, note='치명타 반격에 상처 피해', sources=['lee:Ares attack+Grievous Blow']),
 ],
 'blades_special_knives': [
  V(id='blades_knives_poseidon', name_ko='파도 기예 + 동결 마법 + 번개 투창', trust='high', strength='S', strength_note='dc49018 ★★★★, dc51882 판 = 포세이돈',
    gods=['포세이돈', '데메테르', '제우스'], must=['파도 기예', '설한 고리', '미끄러운 경사', '대전된 마력'], support=['번개 투창', '정전기 충격'],
    duos=['감전 급류'], finisher=None, note='단검 타수로 침수를 쌓고 동결로 묶는다. 끊어 쏘기', sources=['dc49018:포세 기예+데메 마법+번개 투창 ★★★★', 'dc51882:판 = 포세이돈 빌드', 'lee:Poseidon special+Slippery Slope']),
  V(id='blades_knives_hestia', name_ko='화염 기예 + 황홀 마법 + 불같은 열망', trust='high', strength='S', strength_note='dc49018 ★★★★',
    gods=['헤스티아', '아프로디테', '데메테르'], must=['화염 기예', '황홀 고리', '차분한 마력'], support=['불쏘시개', '화력 보강'],
    duos=['불같은 열망', '냉동 화상'], finisher=None, note='단검마다 잔불, 황홀 고리로 묶고 불같은 열망', sources=['dc49018:헤스티아 기예+아프로 마법+불같은 열망 ★★★★', 'lee:Hestia special+Demeter Freezer Burn']),
 ],
 'blades_morrigan_triad': [
  V(id='blades_morrigan_hestia', name_ko='화염 일격 + 애정 기예 + 물결 마법', trust='high', strength='S', strength_note='dc49018 ★5',
    gods=['헤스티아', '아프로디테', '포세이돈'], must=['화염 일격', '애정 기예', '물결 고리', '매혹적 마력'], support=['완전 연소'],
    duos=['불같은 열망', '뜨거운 증기', '섬 휴양지'], finisher=None, note='삼연혈참은 고정 피해 — 은혜는 그 사이를 메운다', sources=['dc49018:헤스티아 공격+아프로 기예+포세 마법 ★5']),
  V(id='blades_morrigan_apollo', name_ko='광휘 일격 + 온화한 바람', trust='high', strength='S', strength_note='dc49018 ★5',
    gods=['아폴론', '헤스티아', '아프로디테'], must=['광휘 일격', '애정 기예', '매혹적 마력'], support=['빛나는 등판', '완전 연소'],
    duos=['온화한 바람', '불같은 열망'], finisher=None, note='실명 + 잔불', sources=['dc49018:아폴론 공격+온화한 바람+아프로 정기 ★5']),
  V(id='blades_morrigan_zeus', name_ko='천상 일격 + 제우스 전설 + 일가친척', trust='mid', strength='A', strength_note='dc49018 ★4',
    gods=['제우스', '헤라', '아프로디테'], must=['천상 일격', '애정 기예', '일가친척'], support=['정전기 충격'],
    duos=['짜릿한 접촉'], finisher=None, note='제우스 전설이 뜨면 완성', sources=['dc49018:제우스 공격+전설+일가친척 ★4']),
 ],
 'flames_omega_attack_spam': [
  V(id='flames_hold_hera', name_ko='헤라 집중 — 파급 효과 → 여왕의 강권', trust='high', strength='S', strength_note='lee "천부적 마력 이것뿐" + dc51882 빌드 ⑥ + 실플레이 첫 클리어(2026-10-01)',
    gods=['헤라', '제우스', '포세이돈'], must=['서약 일격', '천부적 마력', '한 핏줄', '바다 너울'], support=['정의의 창끝', '실연의 아픔', '전압 급증'],
    duos=['파급 효과'], finisher={'duo': '여왕의 강권', 'note': '제우스 기술·마법·마력 중 하나를 임시로 받아두면 여왕의 강권이 뜬다 — 제우스 은혜를 버리고 헤라 은혜 전부 +4Lv'},
    note='마력 쓰는 양 = 딜. Ω마다 균열·파도가 터지고 강권으로 서약 일격·천부적 마력·한 핏줄이 4레벨씩 오른다', sources=['lee:Mel Flames — Hera Born Gain 최고, Fine Line+Righteous Pike', 'dc51882:헤라+포세 Ω 난사', 'log:2026-10-01 지하 첫 클리어 — 서약 일격·천부적 마력·한 핏줄·바다 너울·여왕의 강권']),
  V(id='flames_hold_zeus_special', name_ko='헤라 공격 + 제우스 기술', trust='high', strength='S', strength_note='lee "최적 조합", namu',
    gods=['헤라', '제우스'], must=['서약 일격', '천상 기예', '천부적 마력'], support=['전압 급증', '전기 구이', '정전기 충격'],
    duos=[], fourth=[('아프로디테', ['짜릿한 접촉']), ('헤스티아', ['불벼락'])], finisher=None,
    note='공격 %와 기술 암운이 따로 논다. 핵심은 헤라·제우스 둘. 3번째 신은 아프로디테(짜릿한 접촉) 또는 헤스티아(불벼락) 중 먼저 뜨는 쪽 — 둘 다는 못 간다(풀 4명). 강권은 안 한다(기술을 버리게 됨)', sources=['lee:Hera attack+Zeus special 최적, Zeus special+Romantic Spark', 'namu:멜리노에 횃불']),
  V(id='flames_hold_curse_core', name_ko='잔불·암운·동결 3신 코어', trust='high', strength='S', strength_note='dc51882 3신 코어 ① (전 무기 정석)',
    gods=['헤스티아', '제우스', '데메테르'], must=['화염 일격', '천상 기예', '설한 고리', '대전된 마력'], support=['전압 급증', '솥단지 예열', '완전 연소'],
    duos=['불벼락', '우박 폭풍', '냉동 화상'], finisher=None, note='융합 3개 전부 S. 헤라가 없어 마력은 대전된 마력(방마다 샘)에 의존', sources=['dc51882:헤스+제우스+데메 (공격/기술 암운·잔불, 마법 동결)']),
  V(id='flames_hold_moros_kings', name_ko='모로스 — 서약 일격 + 천상 기예 → 왕의 강권', trust='mid', strength='A', strength_note='검색 레시피 (모로스 전용)',
    gods=['헤라', '제우스', '데메테르'], must=['서약 일격', '천상 기예', '천부적 마력'], support=['전압 급증', '전기 구이'],
    duos=['우박 폭풍'], finisher={'duo': '왕의 강권', 'note': '헤라 은혜를 버리고 제우스 은혜 +4Lv — 모로스는 기술 폭발이 주력이라 제우스 쪽을 키운다'}, aspects=['flames_moros'],
    note='여왕의 강권과 반대 방향. 모로스에서만', sources=["검색:Moros = Hera Sworn Strike + Zeus Heaven Flourish + King's Ransom"]),
 ],
 'flames_omega_special_orbit': [
  V(id='flames_orbit_hera_zeus', name_ko='천상 기예 + 서약 일격 (모로스 최적)', trust='high', strength='S', strength_note='lee "Hera attack+Zeus special 최적", dc51882 모로스 ★★★',
    gods=['헤라', '제우스', '헤스티아'], must=['천상 기예', '서약 일격', '천부적 마력'], support=['화력 보강', '후속 낙뢰', '전기 구이'],
    duos=['불벼락'], finisher=None, hammers=['급속 연발', '간결한 궤도'], note='공전 불꽃에 암운, 혼령이 닿아 폭발', sources=['lee:Moros — Hera attack+Zeus special 최적, Sudden Burst 최고', 'dc51882:모로스 ★★★']),
  V(id='flames_orbit_freeze', name_ko='화염 기예 + 동결 마법 (냉동 화상)', trust='high', strength='S', strength_note='namu 모로스 융합 조합',
    gods=['데메테르', '헤스티아', '제우스'], must=['화염 기예', '설한 고리', '대전된 마력'], support=['완전 연소', '불쏘시개'],
    duos=['냉동 화상', '불벼락', '우박 폭풍'], finisher=None, note='불꽃 궤도에 잔불, 마법으로 얼려 폭발', sources=['namu:모로스 — 데메+헤스/데메+제우스/제우스+헤스 융합 조합']),
  V(id='flames_orbit_eos', name_ko='에오스 — 서약 기예 + 아폴론 공격', trust='mid', strength='A', strength_note='lee 에오스 레시피',
    gods=['헤라', '아폴론', '제우스'], must=['서약 기예', '광휘 일격', '대전된 마력'], support=['전기 구이'],
    duos=[], finisher=None, aspects=['flames_eos'], note='서광이 기술을 복사. 아폴론 전설 + 밤 아르카나', sources=['lee:Eos — Hera special, Apollo attack+legendary', 'dc51882:에오스 = 공격 암운·기술 잔불 고정']),
 ],
 'flames_supay_auto': [
  V(id='flames_supay_flat', name_ko='고정 피해 수프 (열기 쇄도 + 잔불 + 파도)', trust='high', strength='A', strength_note='lee Winning combo, dc51882 ★3',
    gods=['헤스티아', '포세이돈', '제우스'], must=['열기 쇄도', '화염 기예', '파도 일격', '따스한 마력'], support=['정전기 충격', '미끄러운 경사', '완전 연소'],
    duos=['뜨거운 증기', '불벼락'], finisher=None, note='% 피해는 무의미. 타격마다 고정 피해 + 시초', sources=['lee:Supay — Rush boon core, flat damage soup, Origination mandatory', 'dc51882:수파이 ★3']),
  V(id='flames_supay_spark', name_ko='천둥 쇄도 + 짜릿한 접촉', trust='mid', strength='A', strength_note='lee 변형',
    gods=['제우스', '아프로디테', '헤스티아'], must=['천둥 쇄도', '천상 기예', '따스한 마력'], support=['정전기 충격', '전기 구이'],
    duos=['짜릿한 접촉'], finisher=None, note='질주만으로 암운이 터진다', sources=['lee:Zeus + Aphrodite Romantic Spark']),
 ],
 'axe_heavy_attack': [
  V(id='axe_heavy_pct', name_ko='증뎀 공격 + 동결 마법 + 시초', trust='high', strength='S', strength_note='dc51882 ④ + namu "근접엔 아폴론·아프로디테" + lee',
    gods=['아프로디테', '아폴론', '데메테르'], must=['애정 일격', '설한 고리', '매혹적 마력'], support=['추가 처방', '빛나는 등판', '약점 공략'],
    duos=['명랑한 기질'], finisher=None, hammers=['돌진 올려베기', '고속 참격'], note='마법으로 얼려 선딜을 보호. 시초 아르카나로 저주 2종', sources=['dc51882:증뎀(헤라·아프로·아폴론)+데메 마법 필수+시초', 'namu:근접 무기엔 아폴론·아프로디테 궁합 최고', 'lee:Mel Axe — Aphrodite/Apollo/Hera attack + Demeter cast']),
  V(id='axe_heavy_ares', name_ko='애정 일격 + 상해 기예 + 쓰라린 부상', trust='mid', strength='A', strength_note='lee 변형',
    gods=['아프로디테', '아레스', '데메테르'], must=['애정 일격', '상해 기예', '설한 고리'], support=['쓰라린 부상', '죽음의 덫'],
    duos=[], finisher=None, note='큰 한 방에 상처 추가 피해', sources=['lee:Ares special+Grievous Blow, Lethal Snare']),
  V(id='axe_heavy_thanatos_early', name_ko='타나토스 초반 — 광휘 일격 평타', trust='mid', strength='A', strength_note='dc51882 타나토스 ★★★ "초반엔 평타 위주"',
    gods=['아폴론', '헤라', '데메테르'], must=['광휘 일격', '설한 고리', '천부적 마력'], support=['빛나는 등판', '추가 처방'],
    duos=[], finisher=None, aspects=['axe_thanatos'], note='심령 소용돌이가 뜨면 Ω 회오리 방향으로 갈아탄다', sources=['dc51882:타나토스 ★★★ 초반엔 평타 위주']),
 ],
 'axe_omega_whirlwind': [
  V(id='axe_whirl_pct', name_ko='증뎀 공격 + 잡초 박멸 + 심령 소용돌이', trust='high', strength='S', strength_note='lee + dc51882 "심령 소용돌이 먹으면 딜 2배"',
    gods=['아프로디테', '아폴론', '데메테르'], must=['애정 일격', '잡초 박멸', '매혹적 마력', '설한 고리'], support=['빛나는 등판', '성공 신화'],
    duos=['명랑한 기질'], finisher=None, hammers=['심령 소용돌이'], note='회오리 11타에 % 피해. 밤 아르카나·순백 사슴뿔', sources=['lee:Thanatos — Aphrodite/Apollo/Hera attack + Weed Killer, Psychic Whirlwind 최고', 'dc51882:타나토스 증뎀 빌드']),
  V(id='axe_whirl_scorch', name_ko='화염 일격 + 냉동 화상', trust='high', strength='S', strength_note='lee 레시피, 타격마다 은혜가 회오리에서 폭발(namu)',
    gods=['헤스티아', '데메테르', '제우스'], must=['화염 일격', '설한 고리', '대전된 마력'], support=['완전 연소', '정전기 충격'],
    duos=['냉동 화상', '불벼락'], finisher=None, hammers=['심령 소용돌이'], note='회오리 타격마다 잔불', sources=['lee:Hestia attack+Demeter cast Freezer Burn', 'namu:타격마다 은혜가 도끼인데도 폭발']),
  V(id='axe_whirl_zeus', name_ko='천상 일격 + 정전기 + 시초', trust='mid', strength='A', strength_note='lee 변형',
    gods=['제우스', '아프로디테', '데메테르'], must=['천상 일격', '정전기 충격', '대전된 마력'], support=['전기 구이', '후속 낙뢰'],
    duos=['짜릿한 접촉', '우박 폭풍'], finisher=None, hammers=['심령 소용돌이'], note='회오리 타격마다 연쇄 번개', sources=['lee:Zeus attack+Origination']),
 ],
 'axe_omega_cleave': [
  V(id='axe_cleave_apollo', name_ko='영롱한 마력 + 물결 마법 + 지하수 분출', trust='high', strength='S', strength_note='lee + namu "아폴론 마법 궁합 최고"',
    gods=['아폴론', '포세이돈', '헤라'], must=['영롱한 마력', '물결 고리', '지하수 분출', '광휘 기예'], support=['햇살 방사', '초신성', '현지 기후'],
    duos=['물 폭탄'], finisher=None, hammers=['강력 쪼개기'], note='마법진을 Ω 기술로 즉시 폭발. 폭발마다 마력이 돌아온다', sources=['lee:Charon — Apollo Lucid Gain 시작, Poseidon cast→Geyser Spout', 'namu:카론 — 아폴론 마법 궁합 최고']),
  V(id='axe_cleave_ares_zeus', name_ko='아레스+제우스 (폭풍 마법 + 고기 분쇄)', trust='mid', strength='A', strength_note='dc51882 카론 ★★ "양상 자체가 사기"',
    gods=['아레스', '제우스', '아폴론'], must=['상해 기예', '폭풍 고리', '영롱한 마력'], support=['고기 분쇄', '번개 투창'],
    duos=[], fourth=[('데메테르', ['위험 지대'])], finisher=None, note='마법진에 낙뢰·상처', sources=['dc51882:카론 = 아레스+제우스 빌드 ★★']),
 ],
 'axe_nergal_berserk': [
  V(id='axe_nergal_apollo', name_ko='광휘 일격 + 잡초 박멸 + 천부적 마력', trust='high', strength='A', strength_note='lee Winning combo',
    gods=['아폴론', '헤라', '데메테르'], must=['광휘 일격', '천부적 마력', '잡초 박멸'], support=['확인 사살', '빛나는 등판'],
    duos=[], finisher=None, hammers=['심령 소용돌이'], note='Ω 공격 회오리가 주력. 광포화 흡혈로 거칠게', sources=['lee:Nergal — Apollo/Hera attack + Weed Killer', 'namu:3.4.5 네르갈']),
  V(id='axe_nergal_demeter_ares', name_ko='얼음 일격 + 위험 지대', trust='mid', strength='A', strength_note='lee 변형',
    gods=['데메테르', '아레스', '제우스'], must=['얼음 일격', '설한 고리', '대전된 마력'], support=['고기 분쇄', '정전기 충격'],
    duos=['위험 지대'], finisher=None, hammers=['심령 소용돌이'], note='동결 + 마법진 상처', sources=['lee:Demeter attack + Ares Hostile Environment + Psychic Whirlwind']),
 ],
 'skull_throw_retrieve': [
  V(id='skull_throw_pct', name_ko='서약 일격 + 아폴론 보조 + 동결 마법', trust='high', strength='A', strength_note='lee ①, namu "망치 잘 타면 1티어급"',
    gods=['헤라', '아폴론', '데메테르'], must=['서약 일격', '설한 고리', '천부적 마력'], support=['추가 처방', '빛나는 등판'],
    duos=[], finisher=None, hammers=['귀신 들린 탄환', '일제 발사'], note='마법진으로 묶고 연사 → 기술 회수. 사냥꾼 아르카나', sources=['lee:Mel Skull — Hera/Aphrodite/Apollo/Ares attack → Apollo Extra Dose/Back Burner, Demeter cast', 'namu:3.5 멜리노에']),
  V(id='skull_throw_heph', name_ko='화산 기예 → 헤파 전설', trust='mid', strength='A', strength_note='lee ②',
    gods=['헤파이스토스', '헤라', '데메테르'], must=['화산 기예', '서약 일격', '설한 고리'], support=['추가 처방'],
    duos=['태연한 얼굴'], finisher=None, note='헤파 전설(포환당 +21)이 목표', sources=['lee:Heph special → legendary']),
  V(id='skull_throw_apollo_dream', name_ko='아폴론 꿈 빌드 — 광휘 일격 + 귀신 들린 탄환', trust='mid', strength='A', strength_note='lee ③ "dream build"',
    gods=['아폴론', '데메테르', '헤라'], must=['광휘 일격', '영롱한 마력', '잡초 박멸'], support=['추가 처방', '빛나는 등판'],
    duos=[], finisher=None, hammers=['귀신 들린 탄환'], note='마력을 많이 쓰고 아폴론 전설', sources=['lee:Apollo attack + magick + Weed Killer + Apollo legendary + Possessed Array']),
 ],
 'skull_blast_persephone': [
  V(id='skull_perse_heph', name_ko='화산 일격 → 폭발 융합 + 서약 기예', trust='high', strength='S', strength_note='lee ① + namu "첫 클리어용 무난"',
    gods=['헤파이스토스', '헤라', '헤스티아'], must=['화산 일격', '서약 기예', '따스한 마력'], support=['거대 분화구', '용광로 폭발', '솥단지 예열'],
    duos=['연쇄 반응', '태연한 얼굴'], finisher=None, hammers=['비트는 격돌'], note='폭발로 게이지 → 무적 Ω 기술로 방 정리. 기술엔 % 피해', sources=['lee:Persephone — Heph attack → blast duos, Hera special best-in-slot', 'namu:3.5.4 페르세포네']),
  V(id='skull_perse_flat', name_ko='화염 일격 + 천상 기예 + 시초', trust='mid', strength='A', strength_note='lee ②',
    gods=['헤스티아', '포세이돈', '제우스'], must=['화염 일격', '천상 기예', '따스한 마력'], support=['정전기 충격', '솥단지 예열'],
    duos=['불벼락', '뜨거운 증기'], finisher=None, note='타격마다 저주로 게이지', sources=['lee:Hestia/Poseidon/Zeus attack + Origination + % special']),
  V(id='skull_perse_ares', name_ko='상해 일격 + 잔학무도 + 빛살 강타', trust='mid', strength='A', strength_note='lee ③',
    gods=['아레스', '제우스', '헤라'], must=['상해 일격', '서약 기예', '천부적 마력'], support=['빛살 강타', '쓰라린 부상'],
    duos=['잔학무도'], finisher=None, note='상처가 올림포스 피해로 계산돼 게이지가 찬다', sources=['lee:Ares attack + Zeus + Heinous Affront + Light Smite']),
 ],
 'skull_medea_loop': [
  V(id='skull_medea_zeus_ares', name_ko='천상 기예 + 상해 일격 → 잔학무도', trust='high', strength='S', strength_note='lee ① + namu "부동의 1위"',
    gods=['제우스', '아레스', '데메테르'], must=['상해 일격', '천상 기예', '대전된 마력'], support=['쓰라린 부상', '빛살 강타', '후속 낙뢰'],
    duos=['잔학무도', '우박 폭풍'], finisher=None, hammers=['귀신 들린 탄환'], note='장전 → 관통 폭발 → 재장전. 귀신 들린 탄환 = 왕', sources=['lee:Medea — Zeus special + % attack (Ares best)', 'namu:3.5.3 메데이아']),
  V(id='skull_medea_hera', name_ko='서약 일격 + 헤파 방어', trust='mid', strength='A', strength_note='lee ② (수호·물량 맹세)',
    gods=['헤라', '헤파이스토스', '데메테르'], must=['서약 일격', '화산 기예', '천부적 마력'], support=['방호 체계'],
    duos=[], finisher=None, note='피격 리스크를 방어로 메운다', sources=['lee:Hera attack for Wards/Hordes, Heph·Demeter defense']),
  V(id='skull_medea_blast', name_ko='화산 기예 + 폭발 융합 + 솥단지 예열', trust='mid', strength='A', strength_note='lee ③, dc51882 헤파 폭발 ★3',
    gods=['헤파이스토스', '헤스티아', '아폴론'], must=['화산 기예', '화염 일격', '따스한 마력'], support=['솥단지 예열'],
    duos=['연쇄 반응', '강제 기상'], finisher=None, note='관통 폭발 + 헤파 폭발', sources=['lee:Heph special/attack → Hestia·Apollo blast duos + Slow Cooker', 'dc51882:헤파 폭발 ★3']),
 ],
 'skull_hel_valkyrie': [
  V(id='skull_hel_poseidon', name_ko='파도 일격 + 미끄러운 경사 + 서약 기예', trust='high', strength='S', strength_note='lee ① + dc51882 "타수 goat"',
    gods=['포세이돈', '헤라', '헤스티아'], must=['파도 일격', '서약 기예', '따스한 마력'], support=['미끄러운 경사'],
    duos=[], finisher=None, note='발키리 연사 타격마다 파도. 따스한 마력 베스트', sources=['lee:Hel — Poseidon attack + Slippery Slope + Hera special', 'dc51882:헬 ★2 타수 goat']),
  V(id='skull_hel_zeus', name_ko='천상 일격 + 정전기 + 후속 낙뢰', trust='mid', strength='A', strength_note='lee ② "후반 강함"',
    gods=['제우스', '헤스티아', '데메테르'], must=['천상 일격', '정전기 충격', '따스한 마력'], support=['후속 낙뢰', '전기 구이'],
    duos=['불벼락', '냉동 화상'], finisher=None, note='연사 타격마다 연쇄 번개', sources=['lee:Zeus attack (Static Shock·Double Strike)']),
  V(id='skull_hel_hestia', name_ko='화염 일격 + 냉동 화상', trust='high', strength='A', strength_note='namu 헬 추천',
    gods=['헤스티아', '데메테르', '제우스'], must=['화염 일격', '설한 고리', '따스한 마력'], support=['화력 보강', '전기 구이'],
    duos=['냉동 화상', '불벼락'], finisher=None, note='연사로 잔불을 쌓고 얼려 폭발', sources=['namu:헤스티아 주력 + 데메테르 냉동 화상, 제우스 전기 구이, 따스한 마력 베스트']),
 ],
 'coat_punch_rocket': [
  V(id='coat_punch_flat', name_ko='서약 기예 + 파도 일격 (최고 희귀도 4신)', trust='high', strength='A', strength_note='lee ① + namu',
    gods=['헤라', '포세이돈', '헤스티아'], must=['서약 기예', '파도 일격', '따스한 마력'], support=['정전기 충격', '미끄러운 경사', '솥단지 예열'],
    duos=['뜨거운 증기'], finisher=None, hammers=['분출 상승'], note='돌진 공격 3타 = 타격마다 은혜. 4번째 신은 제우스(정전기)', sources=['lee:Mel Coat — Hera/Poseidon/Hestia/Zeus, Exhaust Riser', 'namu:3.6 멜리노에']),
  V(id='coat_punch_freeze', name_ko='화염 일격 + 서약 기예 + 냉동 화상', trust='high', strength='A', strength_note='lee ②',
    gods=['헤스티아', '데메테르', '헤라'], must=['화염 일격', '서약 기예', '설한 고리'], support=['솥단지 예열'],
    duos=['냉동 화상'], finisher=None, hammers=['분출 상승'], note='분출 상승이면 잔불 쌓기 쉬움', sources=['lee:Hestia attack + Demeter Freezer Burn (Exhaust Riser)']),
  V(id='coat_punch_zeus', name_ko='천상 일격 + 짜릿한 접촉 / 초전도체', trust='mid', strength='A', strength_note='lee ③',
    gods=['제우스', '아프로디테', '헤파이스토스'], must=['천상 일격', '화산 기예', '대전된 마력'], support=['정전기 충격'],
    duos=['짜릿한 접촉', '초전도체'], finisher=None, note='주먹 타격마다 암운', sources=['lee:Zeus attack + Aphrodite Romantic Spark / Heph Superconductor']),
  V(id='coat_punch_nyx', name_ko='닉스 — 화염 일격 + 따스한 마력 + 온화한 바람', trust='mid', strength='A', strength_note='lee 닉스 ③, namu "멜리노에·셀레네보다 좋음"',
    gods=['헤스티아', '아폴론', '헤라'], must=['화염 일격', '따스한 마력', '서약 기예'], support=['무형의 운무'],
    duos=['온화한 바람'], finisher=None, aspects=['coat_nyx'], note='헤라 천부적 마력은 Ω 추진에 안 걸린다 — 피한다', sources=['lee:Nyx — Hestia Hearth Gain + Apollo Glorious Disaster, avoid Hera gain']),
 ],
 'coat_shiva_gigapunch': [
  V(id='coat_shiva_pct', name_ko='광휘 일격 + 천부적 마력 + 잡초 박멸', trust='high', strength='A', strength_note='lee ① + namu "6중첩 1200"',
    gods=['아폴론', '헤라', '데메테르'], must=['광휘 일격', '천부적 마력', '잡초 박멸'], support=['추가 처방', '확인 사살', '한 핏줄'],
    duos=[], finisher=None, hammers=['파괴적 반격', '코끼리 로켓'], note='마력을 엄청 쓴다. 아폴론 전설(2연타 주먹)', sources=['lee:Shiva — Apollo/Demeter/Hera attack, Weed Killer, Exceptional Talent', 'namu:3.6.5 시바']),
  V(id='coat_shiva_origination', name_ko='시초 + 광휘·애정·천상 일격 그냥 주먹', trust='mid', strength='A', strength_note='lee ② 변형',
    gods=['아폴론', '아프로디테', '제우스'], must=['광휘 일격', '영롱한 마력', '태양 고리'], support=['후속 낙뢰'],
    duos=['명랑한 기질', '짜릿한 접촉'], finisher=None, note='저주 2종 + 사냥꾼', sources=['lee:Origination(+Huntress), Apollo·Aphrodite·Zeus attack']),
 ],
 'coat_selene_skyfall': [
  V(id='coat_selene_moonbeam', name_ko='달빛보라 + 서약 일격 + 마력 회복 + Ω 비용', trust='high', strength='B', strength_note='lee ① — 단 양상 자체가 외투 최하(namu, dc ★1)',
    gods=['헤라', '데메테르', '헤스티아'], must=['서약 일격', '천부적 마력', '한 핏줄'], support=['화력 보강', '잡초 박멸'],
    duos=[], finisher=None, note='달빛보라 기념품 전제. Ω 비용 증가 은혜가 비술을 더 빨리 채운다', sources=['lee:Selene — Moon Beam first, % attack + magick recovery + Ω cost', 'namu:3.6.3 셀레네']),
  V(id='coat_selene_ares', name_ko='살벌한 마력 + 아레스 전설', trust='mid', strength='B', strength_note='lee ②',
    gods=['아레스', '헤라', '제우스'], must=['살벌한 마력', '서약 일격'], support=['쓰라린 부상'],
    duos=['잔학무도'], finisher=None, note='천상 붕괴에 상처', sources=['lee:Ares magick + Ares legendary']),
  V(id='coat_selene_zeus', name_ko='시초 + 천상 기예 + 전기 구이', trust='mid', strength='B', strength_note='lee ③',
    gods=['제우스', '헤라', '아프로디테'], must=['천상 기예', '애정 일격', '천부적 마력'], support=['전기 구이', '정전기 충격'],
    duos=['짜릿한 접촉'], finisher=None, note='Ω 피해가 암운을 즉시 터뜨린다', sources=['lee:Origination + Zeus special + Arc Flash']),
 ],
}

# ── 적용 ─────────────────────────────────────────────────
warn = []
total = 0
for w, wd in BD['weapons'].items():
    for d in wd['directions']:
        spec = SPEC.get(d['id'])
        assert spec, '변형 없음: ' + d['id']
        out = []
        for v in spec:
            gods_ids = [god(g) for g in v['gods']]
            must = [boon(n) for n in v['must']]; sup = [boon(n) for n in v['support']]
            tds = [duo(n) for n in v['duos']]
            # 8-G: 4번째 신 의존 융합 — 주요 신 밖의 신이 필요한 융합은 fourth에 명시 (택1)
            fourth = [{'god': god(g), 'duos': [duo(n) for n in ds]} for g, ds in v.get('fourth', [])]
            for t in tds:
                dg = dn[[k for k, x in dn.items() if x['id'] == t][0]]['gods']
                assert all(g in gods_ids for g in dg), '%s/%s: 융합 %s의 신 %s가 main_gods 밖 — fourth로 옮길 것' % (d['id'], v['id'], t, dg)
            fin = None
            if v.get('finisher'):
                fin = {'duo': duo(v['finisher']['duo']), 'note': v['finisher']['note']}
            # 검산: must 은혜의 신이 main_gods 안에 있는가 (헤르메스·아르테미스·아테나 제외)
            bmap = {b['id']: b for b in boons}
            for i in must + sup:
                g = bmap[i]['god']
                if g not in gods_ids and g not in ('hermes', 'artemis', 'athena', 'dionysus'):
                    warn.append('%s/%s: %s(%s)의 신 %s가 main_gods %s에 없음' % (d['id'], v['id'], bmap[i]['name_ko'], 'must' if i in must else 'sup', g, v['gods']))
            # 검산: 융합 신 ⊆ main_gods ∪ {4번째}
            for t in tds + ([fin['duo']] if fin else []):
                dg = dn[[k for k, x in dn.items() if x['id'] == t][0]]['gods']
                extra = [g for g in dg if g not in gods_ids]
                if len(extra) > 1: warn.append('%s/%s: 융합 %s 신 %s 중 %s가 main_gods 밖' % (d['id'], v['id'], t, dg, extra))
            # 검산: must는 칸당 1개
            slots = [bmap[i]['slot'] for i in must if bmap[i].get('occupies_slot')]
            assert len(slots) == len(set(slots)), '%s/%s must에 같은 칸 2개' % (d['id'], v['id'])
            # 검산: 양상 존재
            for a in v.get('aspects', []):
                assert a in (d.get('aspects') or []), '%s/%s 양상 %s가 방향 aspects %s에 없음' % (d['id'], v['id'], a, d.get('aspects'))
            o = {'id': v['id'], 'name_ko': v['name_ko'], 'trust': v['trust'], 'strength': v['strength'], 'strength_note': v['strength_note'],
                 'main_gods': gods_ids, 'must': must, 'support': sup, 'target_duos': tds, 'finisher': fin,
                 'note': v['note'], 'sources': v['sources']}
            if fourth: o['fourth'] = fourth
            if v.get('hammers'): o['hammers'] = [ham(n, w) for n in v['hammers']]
            if v.get('aspects'): o['aspects'] = v['aspects']
            out.append(o); total += 1
        d['variants'] = out

# 여왕의 강권: B→A + 공격 꾹 방향 목표에 추가
q = dn['여왕의 강권']
if q['power_tier'] != 'A':
    q['power_tier'] = 'A'; q['tier_note'] = 'B→A (2026-10-26, 8-B): 횃불 공격 꾹 헤라 집중 빌드의 끝내기 — 실플레이 첫 클리어(2026-10-01) + lee Queen\'s Ransom. 헤라 핵심 은혜 3개가 한 번에 +4Lv'
    io.open(P('data', 'duo_legendary.json'), 'w', encoding='utf-8', newline='\n').write(json.dumps(duos, ensure_ascii=False, indent=1) + '\n')
    print('duo_legendary.json: 여왕의 강권 A')
fa = next(d for d in BD['weapons']['flames']['directions'] if d['id'] == 'flames_omega_attack_spam')
if 'duo_hera_zeus_queens_ransom' not in fa['target_duos']:
    fa['target_duos'].insert(1, 'duo_hera_zeus_queens_ransom')
BD['_8b'] = '2026-10-26 빌드 카드(variants) — 커뮤니티 빌드를 합치지 않고 그대로. data/patch_8_variants.py'
io.open(BD_PATH, 'w', encoding='utf-8', newline='\n').write(json.dumps(BD, ensure_ascii=False, indent=1) + '\n')
print('build_directions.json: 변형 %d개 / 방향 %d개' % (total, sum(len(wd['directions']) for wd in BD['weapons'].values())))
for x in warn: print('  검토:', x)
