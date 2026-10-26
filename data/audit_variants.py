# -*- coding: utf-8 -*-
"""빌드 카드(variants) 논리 검사 (8-I, 2026-10-26). 사용법: python data/audit_variants.py
카드만 보고 한 판을 머릿속으로 돌렸을 때 걸리는 것들을 기계적으로 찾는다. 출력이 비어야 정상.

[풀]   주요 신 + 후보 신 + (주요 신 밖) 보조 은혜의 신 > 4 → 받을 수 없는 보조
[융합] 목표/후보/끝내기 융합: 필수 은혜로 안 찬 그룹에 "주요 신(또는 그 후보 신) 은혜이면서 빈 칸에 들어가는" 선택지가 없음 → 그 융합은 이 카드로는 못 만든다
[끝내기] 강권류가 지우는 신의 은혜가 필수에 있음 → 끝내기가 빌드를 부순다
[선행] 필수 패시브의 전제조건이 필수 안에서 안 차고, 채울 은혜가 빈 칸에도 못 들어감
[상충] 필수끼리 동시 불가 / 방향 avoid_boons에 필수가 있음
[칸]   필수 칸 점유 은혜가 같은 칸에 2개
[핵심 칸] 방향의 핵심 칸을 필수가 안 덮음 / [망치] 양상에서 안 뜨는 망치 / [강함] 신뢰 high가 아닌데 S
"""
import io, json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda f: json.load(io.open(os.path.join(ROOT, 'data', f), encoding='utf-8'))
B = {b['id']: b for b in J('boons.json')}; U = {d['id']: d for d in J('duo_legendary.json')}; G = {g['id']: g['name_ko'] for g in J('gods.json')}; HM = {h['id']: h for h in J('hammers.json')}
BD = J('build_directions.json')
NONPOOL = {'hermes', 'artemis', 'athena', 'dionysus', 'selene', 'chaos'}
SLOT_KO = {'attack': '공격', 'special': '기술', 'cast': '마법', 'sprint': '질주', 'magick': '마력'}
# 강권류: 어느 신의 은혜가 사라지나 (효과 문구 "X 은혜 전부 포기")
LOSES = {}
for d in U.values():
    eff = d.get('effect') or ''
    for gid, gko in G.items():
        if eff.startswith(gko + ' 은혜 전부 포기'): LOSES[d['id']] = gid

def tok_met(tok, owned):
    if tok == 'cat:ring': return any(B[i]['tags'] and 'ring' in B[i]['tags'] for i in owned if i in B)
    if tok == 'cat:strike': return any(B[i]['slot'] == 'attack' for i in owned if i in B)
    if tok.startswith('god:'): return any(B[i]['god'] == tok[4:] for i in owned if i in B)
    return tok in owned
def tok_opts(tok):
    """토큰이 가리키는 구체 은혜 목록"""
    if tok == 'cat:ring': return [b for b in B.values() if 'ring' in (b.get('tags') or [])]
    if tok == 'cat:strike': return [b for b in B.values() if b['slot'] == 'attack']
    if tok.startswith('god:'): return [b for b in B.values() if b['god'] == tok[4:]]
    return [B[tok]] if tok in B else []
def lab(b): return '%s(%s)' % (b['name_ko'], SLOT_KO.get(b['slot'], '보조') if b.get('occupies_slot') else '보조')

issues = []
def issue(kind, v, msg): issues.append((kind, v['id'], msg))

for w, wd in BD['weapons'].items():
    for d in wd['directions']:
        for v in d.get('variants', []):
            must = v['must']; mset = set(must)
            main = v['main_gods']; fourth = v.get('fourth', [])
            fgods = [f['god'] for f in fourth]
            used = {B[i]['slot'] for i in must if B[i].get('occupies_slot')}
            free = set(SLOT_KO) - used
            allowed_gods = set(main) | set(fgods)
            # [칸]
            slots = [B[i]['slot'] for i in must if B[i].get('occupies_slot')]
            if len(slots) != len(set(slots)): issue('칸', v, '필수에 같은 칸 2개: %s' % slots)
            # [풀]
            sup_gods = {B[i]['god'] for i in v['support'] if B[i]['god'] not in NONPOOL and B[i]['god'] not in allowed_gods}
            budget = len(main) + len(set(fgods)) + len(sup_gods)
            if budget > 4:
                issue('풀', v, '주요 %d + 후보 %d + 보조의 다른 신 %s = %d > 4 — 보조 %s 는 받을 신 자리가 없음' % (len(main), len(set(fgods)), [G[g] for g in sup_gods], budget,
                      [B[i]['name_ko'] for i in v['support'] if B[i]['god'] in sup_gods]))
            # [융합] 목표·끝내기·후보
            duos = [(t, set(main)) for t in v['target_duos']]
            if v.get('finisher'): duos.append((v['finisher']['duo'], set(main)))
            for f in fourth:
                for t in f['duos']: duos.append((t, set(main) | {f['god']}))
            for t, gods_ok in duos:
                D = U[t]
                for grp in D['requires']['all']:
                    if any(tok_met(x, mset) for x in grp['any']): continue
                    opts = [b for x in grp['any'] for b in tok_opts(x)]
                    ok = [b for b in opts if (b['god'] in gods_ok or b['god'] in NONPOOL) and (not b.get('occupies_slot') or b['slot'] in free)]
                    if not ok:
                        issue('융합', v, "'%s' 조건 [%s] — 주요 신 은혜로 빈 칸(%s)에 넣을 수 있는 게 없음" % (D['name_ko'], '/'.join(lab(b) for b in opts[:5]), '·'.join(SLOT_KO[s] for s in free) or '없음'))
            # [끝내기]
            if v.get('finisher'):
                lose = LOSES.get(v['finisher']['duo'])
                if lose:
                    lost = [B[i]['name_ko'] for i in must if B[i]['god'] == lose]
                    if lost: issue('끝내기', v, "'%s'이 %s 은혜를 지움 — 필수 %s 가 사라진다" % (U[v['finisher']['duo']]['name_ko'], G[lose], lost))
                    # 강권 조건의 "지워질 신" 쪽 은혜가 빈 칸에 들어가나
            # [선행]
            for i in must:
                b = B[i]; pre = b.get('prereq')
                if not pre: continue
                for grp in pre['all']:
                    if any(tok_met(x, mset) for x in grp['any']): continue
                    opts = [bb for x in grp['any'] for bb in tok_opts(x)]
                    ok = [bb for bb in opts if (bb['god'] in allowed_gods or bb['god'] in NONPOOL) and (not bb.get('occupies_slot') or bb['slot'] in free)]
                    if not ok: issue('선행', v, "필수 '%s'의 전제 [%s] — 필수로도, 빈 칸(%s)으로도 못 채움" % (b['name_ko'], '/'.join(lab(x) for x in opts[:5]), '·'.join(SLOT_KO[s] for s in free) or '없음'))
                    else: issue('선행·순서', v, "필수 '%s'은 %s 뒤에만 뜬다 (필수에 없음 → 카드에 순서 표시 필요)" % (b['name_ko'], '/'.join(lab(x) for x in ok[:3])))
            # [상충]
            for i in must:
                for c in B[i].get('conflicts', []):
                    if c in mset and B[c].get('occupies_slot') and B[i].get('occupies_slot') and B[c]['slot'] == B[i]['slot']: continue
                    if c in mset: issue('상충', v, "필수 '%s' ↔ '%s' 동시 불가" % (B[i]['name_ko'], B[c]['name_ko']))
            for i in must + v['support']:
                if i in (d.get('avoid_boons') or []): issue('상충', v, "방향 회피 은혜 '%s'가 필수/보조에 있음" % B[i]['name_ko'])
            # [핵심 칸] 방향의 핵심 칸을 필수가 덮는가
            miss = [SLOT_KO[x] for x in (d.get('core_slots') or []) if x not in used]
            if miss: issue('핵심 칸', v, '방향 핵심 칸 %s 이 필수에 없음' % miss)
            # [망치] 카드 양상에서 뜨는 망치인가
            asps = v.get('aspects') or d.get('aspects') or []
            for h in v.get('hammers', []):
                hh = HM[h]
                if hh.get('aspect_only') and hh['aspect_only'] not in asps: issue('망치', v, '%s 는 %s 전용' % (hh['name_ko'], hh['aspect_only']))
                if any(x in (hh.get('aspect_excluded') or []) for x in asps): issue('망치', v, '%s 는 이 양상에서 안 뜸' % hh['name_ko'])
            # [강함] S는 신뢰 high에서만
            if v['strength'] == 'S' and v['trust'] != 'high': issue('강함', v, 'S인데 신뢰 %s' % v['trust'])
            if len(main) < 2: issue('신', v, '주요 신 %d명' % len(main))

by = {}
for k, vid, m in issues: by.setdefault(k, []).append((vid, m))
total = sum(len(x) for x in by.values())
print('변형 %d개 검사 → 문제 %d건' % (sum(len(d.get('variants', [])) for wd in BD['weapons'].values() for d in wd['directions']), total))
for k in ['칸', '핵심 칸', '풀', '융합', '끝내기', '선행', '선행·순서', '상충', '망치', '강함', '신']:
    for vid, m in by.get(k, []): print('[%s] %-30s %s' % (k, vid, m))
sys.exit(1 if total else 0)
