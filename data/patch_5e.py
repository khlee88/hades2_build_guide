# -*- coding: utf-8 -*-
"""5-E 데이터 구멍 (페이블, 2026-09-16). 실플레이 로그가 잡아낸 누락.

- 염화 고리(헤스티아 마법): 횃불 2방향·도끼 단발·쌍검 백스탭 마법 목록에 없었는데 실플레이에서 2회 선택됨.
  lee "Smolder Ring & Storm Ring: an awful lot of damage while you do other things".
- 매혹적 마력(아프로디테): 횃불 마력 목록에 없었음. lee Very good boons.
- 폭풍 고리(제우스 마법): 같은 근거로 횃불 마법 목록에 추가.
경위: 커뮤니티 검증 때 slot_prefs를 신 단위로 다시 쓰면서 헤스티아·아프로디테의 비주력 칸이 빠졌다.
"""
import io, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, 'data', 'build_directions.json')
bd = json.load(io.open(P, encoding='utf-8'))
if bd.get('_patch_5e'):
    print('이미 적용됨'); sys.exit(0)

def add(w, did, slot, boon, pos=None):
    d = next(x for x in bd['weapons'][w]['directions'] if x['id'] == did)
    lst = d['slot_prefs'].setdefault(slot, [])
    if boon in lst: return
    if pos is None: lst.append(boon)
    else: lst.insert(pos, boon)
    d.setdefault('sources', []).append('log:2026-09-16 실플레이 5런 — %s 누락 보정' % boon)

for did in ('flames_omega_attack_spam', 'flames_omega_special_orbit'):
    add('flames', did, 'cast', 'hestia_smolder_ring')
    add('flames', did, 'cast', 'zeus_storm_ring')
    add('flames', did, 'magick', 'aphrodite_glamour_gain')
add('axe', 'axe_heavy_attack', 'cast', 'hestia_smolder_ring')
add('blades', 'blades_backstab_attack', 'cast', 'hestia_smolder_ring')
bd['_patch_5e'] = '2026-09-16 실플레이 로그 기반 누락 보정 (염화 고리·매혹적 마력·폭풍 고리)'
io.open(P, 'w', encoding='utf-8', newline='\n').write(json.dumps(bd, ensure_ascii=False, indent=1) + '\n')
print('build_directions.json: 5-E 반영')
