# -*- coding: utf-8 -*-
"""선택 로그 분석. 사용법: python data/runs/analyze.py [로그파일...]

지금 표본으로 통계는 못 낸다(12런). 대신 (a) 데이터 위생 점검 (b) 런별 최종 빌드 재구성
(c) 추천-선택 불일치 (d) 커버리지 구멍 실측을 한다.
"""
import io, json, os, sys, glob
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = lambda f: json.load(io.open(os.path.join(ROOT, 'data', f), encoding='utf-8'))
BOON = {b['id']: b for b in D('boons.json')}
DUO = {d['id']: d for d in D('duo_legendary.json')}
HAM = {h['id']: h for h in D('hammers.json')}
GOD = {g['id']: g for g in D('gods.json')}
BD = D('build_directions.json')
nm = lambda i: (BOON.get(i) or DUO.get(i) or HAM.get(i) or GOD.get(i) or {}).get('name_ko', i)
SLOT_KO = {'attack': '공격', 'special': '기술', 'cast': '마법', 'sprint': '질주', 'magick': '마력'}
NONPOOL = {'hermes', 'artemis', 'athena', 'dionysus', 'selene', 'chaos'}

files = sys.argv[1:] or glob.glob(os.path.join(ROOT, 'data', 'runs', '*.jsonl'))
ev = []
for f in files:
    for line in io.open(f, encoding='utf-8'):
        line = line.strip()
        if line:
            ev.append(json.loads(line))

runs = defaultdict(list)
for e in ev:
    runs[e['id']].append(e)

print('=' * 78)
print('런 %d개 · 이벤트 %d개 · 선택 %d개' % (len(runs), len(ev), sum(1 for e in ev if e['t'] == 'pick')))
print('=' * 78)

# ── 런별 최종 빌드 재구성 ────────────────────────────────────────────────────
for rid, es in runs.items():
    hdr = next((e for e in es if e['t'] == 'run'), {})
    end = next((e for e in es if e['t'] == 'end'), None)
    picks = [e for e in es if e['t'] == 'pick']
    slots, extras, hammers, duos, pool = {}, [], [], [], []
    for p in picks:
        c = p['c']
        if p['kind'] == 'god':
            if c not in pool and c not in NONPOOL:
                pool.append(c)
            continue
        if p['kind'] == 'hammer':
            hammers.append(c); continue
        if c in DUO:
            duos.append(c); continue
        b = BOON.get(c)
        if not b: continue
        if b.get('occupies_slot'):
            slots[b['slot']] = c
        else:
            extras.append(c)
    wdirs = BD['weapons'].get(hdr.get('w'), {}).get('directions', [])
    maind = picks[-1]['dir'][0][0] if picks and picks[-1].get('dir') else None
    dobj = next((d for d in wdirs if d['id'] == maind), None)
    rgv = end['rg'] if end else None
    print()
    print('■ %s  %s / %s  (이해도 %s)' % (rid, nm(hdr.get('w', '?')), hdr.get('asp', '?'), hdr.get('grasp')))
    print('  결과: %s  rg=%s  |  선택 %d회 · 최대 도달지역(로그) %d' %
          (end['res'] if end else '미입력', rgv, len(picks), max([p['rg'] for p in picks] or [0])))
    print('  방향: %s' % (dobj['name_ko'] if dobj else maind))
    for s in ['attack', 'special', 'cast', 'sprint', 'magick']:
        v = slots.get(s)
        mark = ''
        if dobj and v:
            prefs = (dobj.get('slot_prefs') or {}).get(s) or []
            mark = ('  ← %s칸 %d순위' % ('핵심 ' if s in dobj.get('core_slots', []) else '', prefs.index(v) + 1)) if v in prefs else '  ← 목록에 없음'
        core = '*' if dobj and s in dobj.get('core_slots', []) else ' '
        print('   %s%-4s %s%s' % (core, SLOT_KO[s], nm(v) if v else '— 비어 있음', mark))
    print('   신 풀(%d): %s' % (len(pool), ', '.join(nm(g) for g in pool)))
    print('   융합: %s' % (', '.join(nm(d) for d in duos) if duos else '없음'))
    print('   망치: %s' % (', '.join(nm(h) for h in hammers) if hammers else '없음'))
    if dobj:
        tgt = dobj.get('target_duos', [])
        got = [t for t in tgt if t in duos]
        print('   노린 융합 %d개 중 %d개 획득%s' % (len(tgt), len(got), (' — ' + ', '.join(nm(g) for g in got)) if got else ''))

# ── 집계 ─────────────────────────────────────────────────────────────────────
picks = [e for e in ev if e['t'] == 'pick']
print()
print('=' * 78)
agree = sum(1 for p in picks if next((o for o in p['off'] if o['i'] == p['c']), {}).get('k') == 1)
print('앱 1위 채택률 : %d/%d = %.0f%%' % (agree, len(picks), 100.0 * agree / len(picks)))
for kind in ['god', 'boon', 'hammer']:
    sub = [p for p in picks if p['kind'] == kind]
    if not sub: continue
    a = sum(1 for p in sub if next((o for o in p['off'] if o['i'] == p['c']), {}).get('k') == 1)
    ranks = Counter(next((o for o in p['off'] if o['i'] == p['c']), {}).get('k') for p in sub)
    print('  %-7s %2d/%2d = %3.0f%%   고른 순위 분포 %s' % (kind, a, len(sub), 100.0 * a / len(sub),
          dict(sorted((k, v) for k, v in ranks.items() if k))))

# 커버리지 구멍: breakdown이 direction 1점뿐 = "무난함"
offers = [o for p in picks for o in p['off']]
bland = [o for o in offers if list(o['b'].keys()) == ['direction'] and o['b']['direction'] == 1]
print('"무난함"(방향 1점뿐) : %d/%d = %.0f%% 의 선택지에 앱이 할 말이 없었음'
      % (len(bland), len(offers), 100.0 * len(bland) / len(offers)))
print('  최다: %s' % ', '.join('%s×%d' % (nm(i), c) for i, c in Counter(o['i'] for o in bland).most_common(6)))

rar = Counter(o.get('r') for o in offers)
print('희귀도 입력      : %s' % dict(rar))

# ── 7단계 (2026-10-14): 가중치 보정의 근거 — 표본이 늘면 여기로 재측정 ───────────
print()
# (1) 대기 융합 문: breakdown에 duo_ready가 있는 신 문을 고른 뒤, 바로 다음 은혜 3택에 융합이 떴는가 → GOD.DUO_READY / DUO_OFFER_RATE
tot = hit = 0
for rid, es in runs.items():
    pk = [e for e in es if e['t'] == 'pick']
    for i, p in enumerate(pk):
        if p['kind'] != 'god': continue
        ch = next((o for o in p['off'] if o['i'] == p['c']), {})
        if not ch.get('b', {}).get('duo_ready'): continue
        nxt = pk[i + 1] if i + 1 < len(pk) else None
        if not nxt or nxt['kind'] != 'boon': continue
        tot += 1
        hit += any(o['i'] in DUO and DUO[o['i']].get('kind') == 'duo' for o in nxt['off'])
print('대기 융합 문 → 다음 3택에 융합 제시 : %d/%d = %.0f%%   (weights GOD.DUO_OFFER_RATE 근거, 2026-10-14 실측 23%%)' % (hit, tot, 100.0 * hit / max(tot, 1)))
# (2) 칸이 다 찬 뒤(ns=5) 은혜 선택의 변별력 — 최고점 5 미만이면 앱이 사실상 할 말이 없던 것 → BOON.SYNERGY
late = [p for p in picks if p['kind'] == 'boon' and p.get('ns') == 5]
weak = [p for p in late if max((o['s'] or -99) for o in p['off']) < 5 and not any(o.get('r') in ('duo', 'legendary') for o in p['off'])]
print('칸 5개 찬 뒤 은혜 선택 중 최고점 5 미만 : %d/%d = %.0f%%   (7-B 이전 로그값 — 5-G 이후 5런만 보면 56%%)' % (len(weak), len(late), 100.0 * len(weak) / max(len(late), 1)))
# (3) 4번째 신 감점 회귀 확인 — 7-A 이후 로그에서는 5번째 신(기념품)에만 붙어야 한다
pen = sum(1 for p in picks if p['kind'] == 'god' for o in p['off'] if o.get('b', {}).get('pool') == -4)
print('신 선택지에 풀 감점(-4)이 붙은 횟수     : %d   (7-A 이전에는 4번째 신마다 붙었음)' % pen)

# 데이터 위생
print()
print('데이터 위생')
for rid, es in runs.items():
    picks_r = [e for e in es if e['t'] == 'pick']
    end = next((e for e in es if e['t'] == 'end'), None)
    maxrg = max([p['rg'] for p in picks_r] or [0])
    rgn = len(end['rg']) if end and end['rg'] else 0
    flag = ''
    if end and rgn < maxrg: flag = '  ⚠ 결과(%d지역)가 로그 최대 지역(%d)보다 작음' % (rgn, maxrg)
    if len(picks_r) >= 10 and rgn <= 1: flag = '  ⚠ 선택 %d회인데 결과가 1지역 사망 — 지역 미갱신 의심' % len(picks_r)
    print('  %s  선택%2d  지역이벤트%d  결과지역%d%s' %
          (rid, len(picks_r), sum(1 for e in es if e['t'] == 'rg'), rgn, flag))
