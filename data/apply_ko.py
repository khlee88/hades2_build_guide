# -*- coding: utf-8 -*-
"""나무위키(한글판 인게임 표기) 기준으로 name_ko / 저주명 / 용어를 일괄 교정."""
import json, io, os, re

BASE = os.path.dirname(os.path.abspath(__file__))

BOON_KO = {
 # 제우스
 "Heaven Strike":"천상 일격","Heaven Flourish":"천상 기예","Storm Ring":"폭풍 고리","Thunder Rush":"천둥 쇄도",
 "Ionic Gain":"대전된 마력","Power Surge":"전압 급증","Divine Vengeance":"신성한 복수","Lightning Lance":"번개 투창",
 "Static Shock":"정전기 충격","Double Strike":"후속 낙뢰","Arc Flash":"전기 구이","Electric Overload":"전력 과부하",
 "Air Quality":"청정한 대기","Shocking Loss":"청천벽력",
 # 헤라
 "Sworn Strike":"서약 일격","Sworn Flourish":"서약 기예","Engagement Ring":"혼약 고리","Nexus Rush":"연분 쇄도",
 "Born Gain":"천부적 마력","Extended Family":"일가친척","Dying Wish":"마지막 소원","Bridal Glow":"신혼의 정열",
 "Hereditary Bane":"액운의 대물림","Rousing Reception":"성대한 환영","Uncommon Grace":"범상찮은 기품",
 "Fine Line":"한 핏줄","Proper Upbringing":"올바른 양육","All Together":"모둠 원소",
 # 포세이돈
 "Wave Strike":"파도 일격","Wave Flourish":"파도 기예","Tidal Ring":"물결 고리","Breaker Rush":"격랑 쇄도",
 "Flood Gain":"넘치는 마력","Hydraulic Might":"세찬 물줄기","Buried Treasure":"바다의 보배","High Surf":"거친 풍랑",
 "Sea Star":"물밑 보답","Slippery Slope":"미끄러운 경사","Geyser Spout":"지하수 분출","Ocean Swell":"바다 너울",
 "Water Fitness":"흐르는 활력","King Tide":"지진 해일",
 # 데메테르
 "Ice Strike":"얼음 일격","Ice Flourish":"얼음 기예","Arctic Ring":"설한 고리","Frigid Rush":"한풍 쇄도",
 "Tranquil Gain":"차분한 마력","Arctic Gale":"혹한 강풍","Plentiful Forage":"풍족한 채집","Steady Growth":"꾸준한 성장",
 "Snow Queen":"방한 외투","Weed Killer":"잡초 박멸","Local Climate":"현지 기후","Cold Storage":"냉장 보관",
 "Frosty Veneer":"쌀쌀맞은 외관","Winter Harvest":"겨울 추수",
 # 아폴론
 "Nova Strike":"광휘 일격","Nova Flourish":"광휘 기예","Solar Ring":"태양 고리","Blinding Rush":"섬광 쇄도",
 "Lucid Gain":"영롱한 마력","Light Smite":"빛살 강타","Perfect Image":"완벽한 매무새","Dazzling Display":"현란한 솜씨",
 "Back Burner":"빛나는 등판","Prominence Flare":"햇살 방사","Super Nova":"초신성","Extra Dose":"추가 처방",
 "Self Healing":"자가 치유","Exceptional Talent":"비상한 재능",
 # 아프로디테
 "Flutter Strike":"애정 일격","Flutter Flourish":"애정 기예","Rapture Ring":"황홀 고리","Passion Rush":"열정 쇄도",
 "Glamour Gain":"매혹적 마력","Shameless Attitude":"두꺼운 상판","Spiritual Affirmation":"정신력 확증",
 "Healthy Rebound":"기운찬 재기","Broken Resolve":"무너진 결심","Sweet Surrender":"달콤한 항복",
 "Heart Breaker":"실연의 아픔","Secret Crush":"은밀한 호감","Wispy Wiles":"무형의 운무","Nervous Wreck":"신경 쇠약",
 # 헤파이스토스
 "Volcanic Strike":"화산 일격","Volcanic Flourish":"화산 기예","Anvil Ring":"모루 고리","Smithy Rush":"단철 쇄도",
 "Tough Gain":"강고한 마력","Grand Caldera":"거대 분화구","Molten Touch":"융해의 손길","Heavy Metal":"중금속",
 "Trusty Shield":"무쇠 가죽","Security System":"방호 체계","Uncanny Fortitude":"초자연적 맷집",
 "Furnace Blast":"용광로 폭발","Martial Art":"굳센 무예","Premium Service":"맞춤 개조",
 # 헤스티아
 "Flame Strike":"화염 일격","Flame Flourish":"화염 기예","Smolder Ring":"염화 고리","Heat Rush":"열기 쇄도",
 "Cardio Gain":"따스한 마력","Highly Flammable":"불쏘시개","Glowing Coal":"달아오른 숯","Controlled Burn":"화력 보강",
 "Flash Fry":"천연가스","Hot Pot":"끓는 냄비","Pyro Technique":"완전 연소","Snuffed Candle":"꺼진 촛불",
 "Slow Cooker":"솥단지 예열","Fire Away":"불길 장벽",
 # 아레스
 "Vicious Strike":"상해 일격","Vicious Flourish":"상해 기예","Sword Ring":"검날 고리","Stabbing Rush":"참격 쇄도",
 "Grisly Gain":"살벌한 마력","Meat Grinder":"고기 분쇄","Profuse Bleeding":"과다 출혈","Grievous Blow":"쓰라린 부상",
 "Visceral Impact":"유혈 사태","Mutual Destruction":"상호 공멸","Blood Spree":"피투성이","Cut Above":"확인 사살",
 "Rallying Cry":"집결 함성","Sanguinary Savor":"달콤한 피",
 # 헤르메스
 "Nimble Limbs":"기민한 동작","Racing Thoughts":"기민한 정신","Winner's Circle":"신속 대응","Nitro Boost":"거침없는 속도",
 "Stutter Step":"잰 발걸음","Hasty Retreat":"황급한 후퇴","Hard Target":"까다로운 표적","Quick Buck":"일확천금",
 "Mean Streak":"연쇄 처단","Travel Deal":"여행 특가","Success Rate":"성공 신화","Tall Order":"무리한 요건",
 "Paid Dues":"생명 수당",
 # 아르테미스
 "Support Fire":"지원 사격","Pressure Points":"약점 공략","Shadow Pounce":"그림자 급습","Vital Sign":"성한 사냥감",
 "Lethal Snare":"죽음의 덫","Easy Shot":"손쉬운 표적","Death Warrant":"사형 선고","Killing Stroke":"일격 필살",
 "Whispered Prayer":"나지막한 기도",
 # 융합(듀오)
 "King's Ransom":"왕의 강권","Queen's Ransom":"여왕의 강권","Killer Current":"감전 급류","Hail Storm":"우박 폭풍",
 "Glorious Disaster":"눈부신 참사","Romantic Spark":"짜릿한 접촉","Thermal Dynamics":"불벼락",
 "Master Conductor":"초전도체","Heinous Affront":"잔학무도","Scalding Vapor":"뜨거운 증기","Freezer Burn":"냉동 화상",
 "Warm Breeze":"온화한 바람","Burning Desire":"불같은 열망","Chain Reaction":"연쇄 반응","Incandescent Aura":"존재감 작열",
 "Fourth Degree":"사도 화상","Ripple Effect":"파급 효과","Natural Selection":"자연 선택","Beach Ball":"물 폭탄",
 "Island Getaway":"섬 휴양지","Seismic Servo":"수력 구동","Arterial Spray":"피바다","Cherished Heirloom":"귀중한 가보",
 "Tropical Cyclone":"남녘 태풍","Hearty Appetite":"원기 왕성","Cryo Pounder":"동결 분쇄","Hostile Environment":"위험 지대",
 "Sun Worshiper":"태양 숭배","Sunny Disposition":"명랑한 기질","Rude Awakening":"강제 기상","Cutting Edge":"날 선 기세",
 "Ecstatic Obsession":"광적인 집착","Love Handles":"설렘 폭발","Carnal Pleasure":"핏빛 사랑","Brave Face":"태연한 얼굴",
 "Universal Donor":"혈기 충만","Coffin Nail":"관짝에 못",
}

# 효과 설명문에 쓰인 임시 용어 -> 한글판 정식 용어
TERMS = [
 ("전격(Blitz)","암운"),("전격","암운"),
 ("화상(Scorch)","잔불"),("화상","잔불"),
 ("거품","침수"),
 ("빙결","동결"),
 ("현혹","실명"),          # Daze=실명. (Charm=현혹은 별도 처리)
 ("돌풍","선풍"),
 ("발광(Glow)","발열"),("발광","발열"),
 ("결속(Hitch)","결속"),
 ("상처(Wounds)","상처"),
 ("특수 공격","기술"),("특수가","기술이"),("특수 피해","기술 피해"),("Ω 특수","Ω 기술"),("특수를","기술을"),
 ("심장구","연심"),
 ("낙하검","비검"),
 ("유물","기념품"),
 ("헥스","비술"),
]
CURSE_KO = {
 "blitz":"암운","scorch":"잔불","froth":"침수","freeze":"동결","gust":"선풍","daze":"실명","weak":"약화",
 "glow":"발열","hitch":"결속","wounds":"상처","marked":"표식","morph":"변형","charm":"현혹","shine":"광휘","none":None,
}

def fix_text(s):
    if not isinstance(s, str):
        return s
    for a, b in TERMS:
        s = s.replace(a, b)
    return s

def walk(obj, in_boonish=False):
    if isinstance(obj, list):
        return [walk(o, in_boonish) for o in obj]
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k == "name_ko" and obj.get("name_en") in BOON_KO:
                out[k] = BOON_KO[obj["name_en"]]
            elif k in ("effect", "rarity_scaling", "notes", "theme", "beginner_note", "style", "region_note"):
                out[k] = fix_text(v)
            elif k == "moveset" and isinstance(v, dict):
                out[k] = {mk: fix_text(mv) for mk, mv in v.items()}
            else:
                out[k] = walk(v, in_boonish)
        return out
    return obj

changed = []
for fn in ["gods.json", "duo_legendary.json", "weapons.json", "arcana.json", "keepsakes.json", "hexes.json"] + \
          ["boons/" + g + ".json" for g in "zeus hestia poseidon demeter apollo aphrodite hephaestus hera ares hermes artemis".split()]:
    p = os.path.join(BASE, fn)
    data = json.load(io.open(p, encoding="utf-8"))
    data = walk(data)
    # gods.json 저주 한글명 교정
    if fn == "gods.json":
        for g in data:
            if g.get("curse") in CURSE_KO:
                g["curse_ko"] = CURSE_KO[g["curse"]]
            if g.get("curse2") in CURSE_KO:
                g["curse2_ko"] = CURSE_KO[g["curse2"]]
    io.open(p, "w", encoding="utf-8").write(json.dumps(data, ensure_ascii=False, indent=1))
    changed.append(fn)

print("교정 완료:", len(changed), "개 파일")
