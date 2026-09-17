# -*- coding: utf-8 -*-
"""운용 가이드 (페이블, 2026-09-17). 방향마다 `playstyle` 6줄.

배경: 6번째 런(지팡이, 크로노스 도달)에서 사용자가 "빌드는 잘 탔는데 운용을 모르겠다 — 멀리서 기술만 쏘면 딜이 안 나오고,
질주로 들어가 마법진 펼치고 때리면 맞아서 초반에 죽음 저항을 다 썼다". 앱은 '무엇을 고를지'만 알려주고 '어떻게 칠지'가 없었다.
weapons.json에 moveset/style이 있었지만 UI에 안 떴고, 지팡이 style은 "Ω 공격 중심"으로 커뮤니티 검증(기술 주력)과 어긋나 있었다.

출처: Lee Reamsnyder 양상별 "Winning combo"(62 Fear 클리어 영상 첨부) + 나무위키 무기 문서 운용법. 새 조사 없음 — 2026-09-10 수집분.
구조: loop(기본 루프) / key(기억할 것) / cast(마법진 — "쓴다·안 쓴다·루프 어디서"를 명시) / early(초반, 칸 2개 이하) / late(완성 후) / avoid.
초반/후반을 나눈 이유: 같은 빌드도 완성 전엔 안전, 후엔 화력. 사용자가 죽은 지점이 정확히 "완성 전에 완성 후 운용을 한 것".
"""
import io, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BD = os.path.join(ROOT, 'data', 'build_directions.json'); WP = os.path.join(ROOT, 'data', 'weapons.json')
bd = json.load(io.open(BD, encoding='utf-8'))
if bd.get('_playstyle'):
    print('이미 적용됨'); sys.exit(0)

PS = {
 'staff_special': {
  'loop': '돌진 공격 → 마법(발밑) → 일반 공격 1~2타 → 기술로 빠지기. 기술이 돌아오는 동안 반복',
  'key': '기술은 멀리서 쏘는 주포가 아니라 ① 붙기 전에 적 공격을 끊고 ② 콤보를 끊고 빠지는 수단이다. 딜은 붙어서 난다. 제자리에서 안 때리고 돌진으로 들어가 기술로 나온다',
  'cast': '쓴다 — 루프 안에서. 돌진으로 붙은 직후 마법 버튼을 누르면 콤보가 끊기지 않고 발밑에 깔린다. 설한 고리면 주변이 묶이고 그 안에서 평타를 친다. 마법진을 펼치러 따로 들어가지 않는다',
  'early': '칸 2개 이하·마력 회복 없음 → 방 클리어 속도를 포기한다. 돌진 공격 → 기술로 거리를 유지하고 Ω는 아낀다. 여기서 죽음 저항을 쓰면 후반이 없다',
  'late': '이중 월광탄·마력 회복이 들어오면 붙어서 Ω 기술(마력 10)을 난사 — 싸고 빠르고 몰린 적에 최고효율. 일렬로 서면 Ω 공격(마력 20, 관통)',
  'avoid': '제자리 풀콤보. 3타째(60)는 느려서 대부분의 적 반응보다 늦다 — 마법진에 묶인 적에게만',
  'sources': ['lee:Mel Staff Winning combo — dash-strike → attack → special, cast any time in combo, special interrupts', 'namu:멜리노에 양상 운용법'] },
 'staff_cast': {
  'loop': '마법(또는 Ω 마법) → 기술 견제 → 돌진 공격 → 평타/Ω 공격. 마법진이 사라지기 전에 다음 마법',
  'key': '"항상 마법진이 깔려 있어야 한다"가 이 빌드의 전부다. 마법이 주포, 나머지는 마법진이 터지는 동안 채우는 딜. 동물 친구가 마법을 함께 시전하므로 적 근처에 있어야 한다',
  'cast': '반드시, 계속. Ω 마법 충전 중에도 돌진으로 빠질 수 있다. 영롱한 마력이면 마법진이 사라질 때 마력이 돌아와 무한 순환. 신속 대응(헤르메스)이 Ω 마법을 빨리 만든다',
  'early': 'Ω 마법을 채울 마력 회복이 없으면 일반 마법 + 기술 견제로 버틴다. 근접은 마법진 안에 묶인 적에게만',
  'late': 'Ω 마법으로 묶고 Ω 공격으로 마무리. 지하수 분출·현지 기후·햇살 방사가 붙으면 마법진 자체가 딜이라 때릴 필요가 줄어든다',
  'avoid': '마법진 없이 근접 싸움. 키르케는 마법진 밖에서 약하다',
  'sources': ['lee:Circe Staff — Always Be Casting, dash while channeling Ω cast, Lucid Gain double', 'namu:키르케 양상'] },
 'staff_omega_attack': {
  'loop': 'Ω 마법으로 묶기 → 뒤로 돌진 → Ω 기술 → 돌진 공격 → Ω 공격. Ω를 이어 돌리면 모모스 반복 발동이 겹친다',
  'key': '타워 디펜스처럼 친다 — 적이 모이는 자리에 Ω 마법을 깔고 그 위에 Ω 기술·Ω 공격을 쌓는다. 적이 자리를 벗어나면 기존 것에 집착하지 말고 새로 깐다',
  'cast': 'Ω 마법이 시작점. 묶인 적 위에 나머지 Ω를 쌓는다. 급하면 일반 마법으로 묶어두는 것도 좋다',
  'early': '마력 회복(천부적·영롱한·넘치는 마력)이 없으면 시동이 안 걸린다. 확보 전엔 일반 공격·기술로 버티고 Ω는 아낀다',
  'late': '마력이 돌면 Ω만 돌린다. 밤 아르카나로 Ω 교대 치명타, 한 핏줄·잡초 박멸이면 Ω마다 추가 피해',
  'avoid': '마력 없이 Ω 남발. 무기 강화 전(랭크 1~2) 모모스는 반복 발동이 느려 답답하다 — 초반엔 무리하지 않는다',
  'sources': ['lee:Momus Staff — tower defense, King of Omegas chain, Night arcana', 'namu:모모스 양상'] },
 'blades_backstab_attack': {
  'loop': '기술(던지기) → 돌진 공격 → 일반 공격 1~2타 → 기술이 돌아오면 반복. 4타째까지 가지 않는다',
  'key': '배후 보너스는 뒤로 돌아가서 얻는 게 아니라 돌진 공격으로 뒤를 잡으며 얻는다. 돌진 공격 자체가 의외로 세서 초반 잡몹은 이것만으로 죽는다',
  'cast': '보조. 콤보 사이에 깐다. 혼약 고리(결속)·황홀 고리(끌어모음)·설한 고리(동결)가 쌍검의 짧은 사거리와 광역 부족을 메운다',
  'early': '짧은 사거리 = 맞기 쉽다. 기술로 먼저 견제하고 한 마리씩 돌진 공격. 둘러싸이면 Ω 공격(마력 10)으로 적 뒤로 순간이동해 빠져나온다',
  'late': '투척 단검이 뜨면 돌진 공격만 반복(단검 7개). 위력적 맹습이면 평타 풀콤보도 세진다',
  'avoid': '춤추는 단검(기술이 안 돌아옴). 티폰·스킬라엔 배후 타격이 안 먹힌다 — 보스에선 배후를 노리지 않는다',
  'sources': ['lee:Mel Blades — special → dash-strike → attack, Trick Knives, avoid Dancing Knives', 'namu:멜리노에 양상 — 스킬라·티폰 배후 불가'] },
 'blades_omega_ambush': {
  'loop': '적 공격 직전 Ω 공격 충전(막기) → 반격 버프 → Ω 공격 연타(적 뒤로 순간이동, 버프 중 최대 5회) → 버프가 끝나면 기술 → 돌진 공격',
  'key': '막기는 마력이 없어도 되고 거의 모든 공격을 막는다 — 투사체·폭발·크로노스 즉사기까지. 막은 직후 잠깐 무적. 즉 보스 패턴 = 딜 타이밍이다',
  'cast': '보조. 반격 버프는 시간 제한이 없으니 버프를 켜둔 채 마법진으로 정리하고 들어가도 된다',
  'early': '잡몹은 막기를 세팅할 가치가 없다 — 기술 + 돌진 공격으로 그냥 죽인다. 막기는 덩치 큰 적·보스에만',
  'late': '폭발적 암습이 뜨면 마력 확보가 전부. 아프로디테 공격 은혜를 최대 강화해 Ω 공격 한 방(2000+ 치명타)을 키운다',
  'avoid': '충전 중 무방비 — 충전하면서 돌진 키를 짧게 눌러 회피한다(충전은 초기화되지만 랭크가 오르면 빠르다). 춤추는 단검',
  'sources': ['lee:Artemis Blades — parry everything incl. Chronos instakill, 5 Ω attacks during Riposte', 'namu:아르테미스 양상 — 크로노스 2페이즈 즉사 패턴 무시'] },
 'blades_special_knives': {
  'loop': '마법진 깔기 → 뒤로 돌진 → Ω 기술 충전 → 발사(마법진 안 적에게 유도). 잡몹전은 풀충전 말고 짧게 끊어 쏜다',
  'key': '단검은 마법진 안의 적에게 유도된다. 마법진 밖을 향해 쏘면 휘어 들어가며 주변까지 훑는다. Ω 기술 발사 중엔 제자리 고정이라 풀충전은 보스전용',
  'cast': '필수 — 유도의 기준점이다. 번개 투창(제우스)·달아오른 숯(헤스티아)이 있으면 마법진을 원거리에 깔 수 있어 훨씬 안전해진다',
  'early': 'Ω 기술 충전이 길다. 마력 회복 전엔 일반 기술 던지기 → 돌진 공격(멜리노에 쌍검처럼)으로 운용',
  'late': '투척 단검이면 돌진 공격 연타만으로 단검이 흩날린다. 급속 난사·감춰둔 단검이면 Ω 기술이 주포',
  'avoid': '잡몹 사이에서 풀충전 — 서 있는 동안 맞는다(나무위키: 가만히 풀차징하면 쳐맞는다)',
  'sources': ['lee:Pan Blades — sprint in, cast, dash out, charge Ω special; curve knives', 'namu:판 양상'] },
 'flames_omega_attack_spam': {
  'loop': 'Ω 기술(불꽃 2개 공전) → 다가가 공격 버튼 꾹(3발마다 Ω 공격 자동) → 불꽃이 꺼지면 물러나 Ω 기술 재장전',
  'key': '공격 버튼을 누른 채로 돌진·마법이 된다. 위험하면 손을 떼지 말고 돌진으로 비킨다. 적과 약간 거리를 두고 공전 불꽃이 스치게 한다',
  'cast': '쓴다 — 공격을 누른 채 마법 버튼. 발밑에 깔고 계속 쏜다. 설한 고리·황홀 고리로 적을 모아두면 공전 불꽃과 화염구가 전부 맞는다',
  'early': '횃불은 마력이 없으면 딜이 최악이다. 마력 회복 은혜가 1지역 1순위. 그 전엔 일반 기술(근거리 2타)로 버틴다',
  'late': '천부적 마력·한 핏줄이면 공격을 누르기만 해도 균열이 터진다. 급속 연발이면 Ω 공격이 더 자주 나간다',
  'avoid': '근접 고정 싸움 — Ω 기술은 적을 경직시키지 못한다. 적이 다가오게 두면 맞고 있는 것이다',
  'sources': ['lee:Mel Flames — charge Ω special, hold Attack, dash/cast while holding; Ω special no hitstun', 'namu:멜리노에 횃불 — 마력 없으면 최악의 딜'] },
 'flames_omega_special_orbit': {
  'loop': '적이 나올 때 Ω 기술 → 뛰어들어 근접에서 공격 꾹 → 혼령이 공전 불꽃에 닿아 폭발 → 불꽃이 꺼지면 질주로 빠져 재장전',
  'key': '모로스는 "미친 듯이 붙어서" 강하다 — 공격으로 뿌린 혼령이 회전 불꽃에 닿아야 터진다. 붙지 않으면 그냥 약한 횃불이다',
  'cast': '쓴다 — 공격을 누른 채 마법 버튼. 적을 묶어두면 혼령·불꽃이 전부 맞는다. 에오스는 서광이 기술을 복사하니 마법으로 묶고 기술 연타',
  'early': '마력이 곧 딜. 마력 회복 전엔 Ω 기술 1개만 띄우고 아껴 쓰며 일반 기술(근거리 2타)로 정리',
  'late': '급속 연발·간결한 궤도·감춰둔 위성이면 불꽃 유지시간·개수가 늘어 필드 전체가 폭발한다. 에오스는 밤 아르카나 + 아폴론 전설',
  'avoid': '마력 0에서 공격 꾹 — 혼령만 쌓이고 안 터진다. 그때는 혼령 쪽으로 돌진 후 일반 기술로 터뜨린다',
  'sources': ['lee:Moros Flames — ludicrously powerful at close range; out of magick: dash to ghosts, tap special. Eos — Daybreaker then tap special', 'namu:모로스·에오스 양상'] },
 'axe_heavy_attack': {
  'loop': '마법진(묶기) → 돌진 공격 → 일반 공격 1·2타 → 기술(취소용) → 다시 돌진. 3타째 큰 참격은 안전할 때만',
  'key': '기술을 아무 때나 누르면 공격 모션이 즉시 끊긴다 — 3타 선딜 중에도. 위험하면 기술로 취소한다. 타격 사이마다 돌진이 가능하다',
  'cast': '필수 — 선딜을 보호한다. 설한 고리로 묶어두고 그 안에서 휘두른다. 도끼는 마법진 없이는 맞으면서 휘두르는 무기다',
  'early': '돌진 공격 → 1·2타 → 기술 → 돌진 반복. 3타는 잊는다. 돌진 올려베기가 뜨면 돌진 공격만 반복해도 된다',
  'late': '아프로디테·아폴론 % 피해와 실명·약화가 붙으면 3타(180)가 방을 지운다. 동결 걸린 적에겐 풀콤보',
  'avoid': '선딜 중 노출. 사냥꾼 아르카나(Ω 안 쓸 때)와 방어도·회복 은혜가 도끼의 생명이다',
  'sources': ['lee:Mel Axe — cast to keep things off, dash-strike → attack → attack → special, special cancels anytime, Dashing Heave', 'namu:멜리노에 양상 — 1타-2타-돌진-막타 콤보'] },
 'axe_omega_whirlwind': {
  'loop': '돌진 공격·평타로 필멸 스택 쌓기 → 스택이 차면 마법진으로 묶고 → Ω 공격 충전 → 회오리(최대 11타) → 돌진으로 취소·이탈',
  'key': '스택은 한 번만 맞아도 전부 날아간다. 이 빌드의 운용 = 안 맞는 운용. 회오리 중에도 느리게 이동하고 돌진으로 언제든 끊을 수 있다',
  'cast': '필수 — 충전 시간을 사준다. 설한 고리(동결)로 묶고 그 위에서 회오리',
  'early': '심령 소용돌이 전엔 회오리 중 무방비. 잡몹전은 멜리노에 도끼처럼 돌진 공격·1·2타·기술로, 회오리는 묶인 적에게만',
  'late': '심령 소용돌이가 뜨면 회오리 중 돌진·질주·마법·공격이 전부 된다 — 도망치며 갈아버릴 수 있다. 밤 아르카나·순백 사슴뿔로 치명타',
  'avoid': '충전 중 돌진으로 시작한 회오리는 무적이 없다. 원거리 적을 회오리로 쫓아가지 않는다',
  'sources': ['lee:Thanatos Axe — build Mortality then Ω, Psychic Whirlwind best, dash-started spin has no invulnerability', 'namu:타나토스 양상 — 필멸 스택'] },
 'axe_omega_cleave': {
  'loop': '일반 마법(묶기) → 즉시 Ω 기술 충전 → 위험하면 돌진으로 방향 전환 → 마법진에 걸치게 발사 → 마법진이 Ω 마법처럼 즉시 폭발',
  'key': 'Ω 마법을 쓰지 않는다 — 일반 마법을 깔고 Ω 기술로 터뜨린다. 폭발 범위는 보이는 마법진보다 크고, Ω 기술이 마법진을 스치기만 해도 터진다',
  'cast': '이 빌드의 전부. 적이 등장하는 자리에 미리 깔고 터뜨리면 나오면서 죽는다. 번개 투창·달아오른 숯이면 원거리 설치',
  'early': '영롱한 마력(아폴론)이 없으면 시동이 안 걸린다 — 폭발마다 마력이 돌아와야 무한 순환. 그 전엔 돌진 공격 → 기술로 정리',
  'late': '강력 쪼개기면 마법 → 2연발 → 다음 마법도 즉시 폭발. 지하수 분출·햇살 방사·고기 분쇄가 폭발에 얹힌다',
  'avoid': '공격 버튼. 카론에서 일반 공격은 존재하지 않는 셈이다',
  'sources': ['lee:Charon Axe — bind in cast (not Ω cast), Ω special clips cast → castplosion; attack button doesn\'t exist', 'namu:카론 양상'] },
}
n = 0
for w, wd in bd['weapons'].items():
    for d in wd['directions']:
        if d['id'] in PS: d['playstyle'] = PS[d['id']]; n += 1
assert n == 11, n
bd['_playstyle'] = '2026-09-17 방향별 운용 가이드 6줄(loop/key/cast/early/late/avoid). 출처 lee Winning combo + 나무위키 운용법'
io.open(BD, 'w', encoding='utf-8', newline='\n').write(json.dumps(bd, ensure_ascii=False, indent=1) + '\n')
print('build_directions.json: playstyle %d개' % n)

# weapons.json — 낡은 style·오타·옛 이름
ws = json.load(io.open(WP, encoding='utf-8'))
for w in ws:
    for k, v in list(w.get('moveset', {}).items()):
        w['moveset'][k] = v.replace('기술는', '기술은')
    if w['id'] == 'staff':
        w['style'] = '기술(월광탄) 주력 — 돌진 공격→마법(발밑)→평타→기술 루프. Ω 기술은 마력 회복 확보 후 난사. (2026-09-17 커뮤니티 검증에 맞춰 "Ω 공격 중심"에서 수정)'
        w['beginner_note'] = '시작 무기이자 가장 무난. 기술 칸(잔불·암운)과 마법 칸(설한 고리)을 먼저 채우고, 마력 회복 1개는 반드시'
    if w['id'] == 'flames':
        w['beginner_note'] = '마력이 없으면 딜이 최악 — 마력 회복 은혜 1지역 1순위. 헤라 한 핏줄·아프로디테 실연의 아픔·제우스 전압 급증이 Ω마다 터진다'
io.open(WP, 'w', encoding='utf-8', newline='\n').write(json.dumps(ws, ensure_ascii=False, indent=1) + '\n')
print('weapons.json: 지팡이 style·오타·옛 은혜명 수정')
