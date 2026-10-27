# -*- coding: utf-8 -*-
"""빌드 카드 완성 배치 계산 (8-J, 2026-10-26, 오퍼스).

카드의 '필수'만으로는 목표 융합 조건이 안 차는 경우가 많다(예: 모로스 천상 기예+서약 일격 카드의 불벼락 —
헤스티아 쪽 조건은 염화 고리(마법)뿐인데 카드엔 화력 보강만 있었다). 여기서 카드마다 "필수 + 빈 칸"으로
목표 융합 조건을 **동시에** 채우는 배치를 찾는다.

규칙
- 칸 점유 은혜는 필수가 안 쓴 칸에만, 서로 겹치지 않게 (칸당 1개)
- 신은 주요 신(+해당 후보 신)만. 헤르메스·아르테미스 등 풀 밖 신은 허용
- 고른 은혜의 전제조건(prereq)이 안 차면 그것도 채워야 할 그룹으로 추가 (재귀)
- 이미 고른 은혜가 다른 그룹도 채우면 재사용 (최소 배치)

결과 (variant['plan'])
  groups: [{duo, kind: target|finisher|fourth, god?, options:[id], pick:id}]  — options = 이 카드에서 실제로 가능한 선택지
  cond_must: [id]  — 선택지가 하나뿐인 조건 (사실상 필수)
  extra: [id]      — 해에 쓰인 조건 은혜 전부
  support_after: {support_id: [id]} — 보조 은혜의 전제조건이 필수+배치로 안 차면 무엇 뒤에 뜨는지
  infeasible: [문구] — 배치를 못 찾음 (데이터 오류)
"""
NONPOOL = {'hermes', 'artemis', 'athena', 'dionysus', 'selene', 'chaos'}
SLOTS = ['attack', 'special', 'cast', 'sprint', 'magick']


def make(B, U):
    def tok_opts(t):
        if t == 'cat:ring': return [b['id'] for b in B.values() if 'ring' in (b.get('tags') or [])]
        if t == 'cat:strike': return [b['id'] for b in B.values() if b['slot'] == 'attack']
        if t.startswith('god:'): return [b['id'] for b in B.values() if b['god'] == t[4:]]
        return [t] if t in B else []

    def tok_met(t, owned):
        return any(x in owned for x in tok_opts(t))

    def grp_met(g, owned):
        return any(tok_met(t, owned) for t in g['any'])

    def solve(must, gods_ok, reqs):
        """reqs: [(label_dict, group)]. 반환 (picks{idx: id}, owned_set) 또는 None"""
        must = set(must)
        used0 = {B[i]['slot'] for i in must if B[i].get('occupies_slot')}

        def ok_boon(i, used):
            b = B[i]
            if b['god'] not in gods_ok and b['god'] not in NONPOOL: return False
            if b.get('occupies_slot') and b['slot'] in used: return False
            return True

        def rec(queue, owned, used, picks):
            # 이미 충족된 그룹은 건너뛴다
            queue = [q for q in queue if not grp_met(q[1], owned)]
            if not queue: return picks, owned
            # 선택지 적은 그룹부터
            def opts_of(q): return [i for t in q[1]['any'] for i in tok_opts(t) if ok_boon(i, used)]
            queue.sort(key=lambda q: len(opts_of(q)))
            lab, g = queue[0]
            for i in opts_of((lab, g)):
                b = B[i]
                nowned = owned | {i}
                nused = used | ({b['slot']} if b.get('occupies_slot') else set())
                extra = [({'prereq_of': i}, pg) for pg in ((b.get('prereq') or {}).get('all') or []) if not grp_met(pg, nowned)]
                r = rec(queue[1:] + extra, nowned, nused, {**picks, id(g): i})
                if r: return r
            return None

        return rec(list(reqs), set(must), set(used0), {})

    def plan_for(v):
        must = list(v['must']); main = set(v['main_gods'])
        used = {B[i]['slot'] for i in must if B[i].get('occupies_slot')}
        out = {'groups': [], 'cond_must': [], 'extra': [], 'support_after': {}, 'infeasible': []}

        def add_groups(duo_id, kind, gods_ok, base_owned, god=None):
            D = U[duo_id]
            reqs = [({'duo': duo_id, 'kind': kind, 'god': god}, g) for g in D['requires']['all'] if not grp_met(g, base_owned)]
            return reqs

        # 1) 목표 융합 + 끝내기: 주요 신만, 동시에
        reqs = []
        for t in v.get('target_duos', []): reqs += add_groups(t, 'target', main, set(must))
        fin = (v.get('finisher') or {}).get('duo')
        if fin: reqs += add_groups(fin, 'finisher', main, set(must))
        # 보조 은혜의 선행조건까지 함께 풀어 본다 — 되면 그 배치를 쓴다 (예: 감전 급류를 공격 칸 대신 보조로 채워 파도 일격 자리를 남김)
        sreqs = [({'support_of': sid}, g) for sid in v.get('support', []) for g in ((B[sid].get('prereq') or {}).get('all') or []) if not grp_met(g, set(must))]
        r = solve(must, main, reqs + sreqs) if sreqs else None
        if r is None: r = solve(must, main, reqs)
        if r is None:
            out['infeasible'].append('목표 융합 %s 를 필수와 함께 동시에 채울 배치가 없음' % ([U[t]['name_ko'] for t in v.get('target_duos', [])] + ([U[fin]['name_ko']] if fin else [])))
            base = set(must)
        else:
            picks, base = r
        def record(reqs, picks, gods_ok, owned_before_used):
            for lab, g in reqs:
                if grp_met(g, set(must)): continue
                opts = [i for t in g['any'] for i in tok_opts(t)
                        if (B[i]['god'] in gods_ok or B[i]['god'] in NONPOOL) and (not B[i].get('occupies_slot') or B[i]['slot'] not in owned_before_used)]
                opts = list(dict.fromkeys(opts))
                opts = [o for o in opts if solve(list(must) + [o], gods_ok, reqs) is not None]   # 다른 조건과 동시에 성립하는 것만
                pick = picks.get(id(g)) if picks else None
                if pick is None:   # 다른 그룹의 선택이 이 그룹도 채움
                    pick = next((x for x in base_all if tok_met_any(g, x)), None)
                out['groups'].append({**{k: v2 for k, v2 in lab.items() if v2 is not None}, 'options': opts, 'pick': pick})
                if len(opts) == 1 and lab.get('kind') in ('target', 'finisher'): out['cond_must'].append(opts[0])
        def tok_met_any(g, x): return grp_met(g, {x})
        # 융합 조건으로 고른 것만 (보조 선행용으로 고른 것은 제외 — 그건 support_after로 안내)
        duo_picks = {r[0][id(g)] for _, g in reqs if r and id(g) in r[0]}
        base_all = duo_picks
        record(reqs, r[0] if r else None, main, used)
        # 2) 후보 신(fourth): 각자, 목표 배치 위에서
        for f in v.get('fourth', []):
            for t in f['duos']:
                freqs = add_groups(t, 'fourth', main | {f['god']}, base, f['god'])
                used_now = used | {B[i]['slot'] for i in base_all if B[i].get('occupies_slot')}
                fr = solve(list(base), main | {f['god']}, freqs)
                if fr is None:
                    out['infeasible'].append('후보 %s → %s 배치가 없음' % (f['god'], U[t]['name_ko']))
                    continue
                for lab, g in freqs:
                    opts = [i for tk in g['any'] for i in tok_opts(tk)
                            if (B[i]['god'] in main | {f['god']} or B[i]['god'] in NONPOOL) and (not B[i].get('occupies_slot') or B[i]['slot'] not in used_now)]
                    opts = [o for o in dict.fromkeys(opts) if solve(list(base) + [o], main | {f['god']}, freqs) is not None]
                    out['groups'].append({**{k: v2 for k, v2 in lab.items() if v2 is not None}, 'options': opts, 'pick': fr[0].get(id(g)) or next((x for x in (fr[1] - set(base)) if grp_met(g, {x})), None)})
        out['extra'] = [i for i in base_all]
        out['cond_must'] = list(dict.fromkeys(out['cond_must']))
        # 3) 보조 은혜 선행조건
        have = set(must) | base_all
        allowed = main | {f['god'] for f in v.get('fourth', [])}
        used_all = {B[i]['slot'] for i in have if B[i].get('occupies_slot')}
        for s in v.get('support', []):
            pre = B[s].get('prereq')
            if not pre: continue
            for g in pre['all']:
                if grp_met(g, have): continue
                opts = [i for t in g['any'] for i in tok_opts(t) if (B[i]['god'] in allowed or B[i]['god'] in NONPOOL) and (not B[i].get('occupies_slot') or B[i]['slot'] not in used_all)]
                out['support_after'][s] = list(dict.fromkeys(opts))[:4]
                if not opts: out['infeasible'].append('보조 %s 의 전제조건을 채울 신·칸이 없음 (필수+조건 배치가 칸을 다 씀)' % B[s]['name_ko'])
        # 5) 전설 경로 (선택) — 주요·후보 신의 전설 중, 필수+융합 배치를 건드리지 않고 남은 칸·보조로 조건을 채울 수 있는 것
        out['legendary'] = []
        fixed = set(must) | base_all
        used_fixed = {B[i]['slot'] for i in fixed if B[i].get('occupies_slot')}
        dmg_gods = {B[i]['god'] for i in must if B[i].get('occupies_slot') and B[i]['slot'] in ('attack', 'special')}
        for g in list(dict.fromkeys(list(main) + [f['god'] for f in v.get('fourth', [])])):
            leg = next((b for b in B.values() if b['god'] == g and b['slot'] == 'legendary'), None)
            if not leg or not leg.get('prereq'): continue
            gods_ok = set(main) | {g}
            lreqs = [({'leg': leg['id']}, grp) for grp in leg['prereq']['all'] if not grp_met(grp, fixed)]
            lr = solve(list(fixed), gods_ok, lreqs)
            if lr is None: continue
            groups = []
            for grp in leg['prereq']['all']:
                have = [i for t in grp['any'] for i in tok_opts(t) if i in fixed]
                if have: groups.append({'met': True, 'have': have[:1]}); continue
                opts = [i for t in grp['any'] for i in tok_opts(t)
                        if (B[i]['god'] in gods_ok or B[i]['god'] in NONPOOL) and (not B[i].get('occupies_slot') or B[i]['slot'] not in used_fixed)]
                opts = [o for o in dict.fromkeys(opts) if solve(list(fixed) + [o], gods_ok, lreqs) is not None]
                groups.append({'met': False, 'options': opts})
            tier = (U.get('leg_' + g) or {}).get('power_tier') or '?'
            out['legendary'].append({'id': leg['id'], 'god': g, 'need': len(lr[1] - fixed), 'tier': tier, 'main_dmg': g in dmg_gods, 'groups': groups})
        out['legendary'].sort(key=lambda x: (x['need'], {'S': 0, 'A': 1, 'B': 2}.get(x['tier'], 3), not x['main_dmg']))
        out['legendary'] = out['legendary'][:3]
        # 4) 필수 대안 — 그 필수가 끝내 안 뜰 때. 같은 칸의 다른 은혜(주요·후보 신, 방향 칸 순위 먼저)로 바꿔도 목표·끝내기 배치가 성립하는 것만
        out['fallbacks'] = {}
        prefs_all = (v.get('_dir_slot_prefs') or {})
        avoid = set(v.get('_dir_avoid') or [])
        for m in must:
            bm = B[m]
            if not bm.get('occupies_slot'): continue
            pool = list(dict.fromkeys((prefs_all.get(bm['slot']) or []) + [b['id'] for b in B.values() if b['slot'] == bm['slot'] and b.get('occupies_slot')]))
            alts = []
            for a in pool:
                if a == m or a in avoid or B[a]['god'] not in allowed: continue
                must2 = [x for x in must if x != m] + [a]
                reqs2 = []
                for t in v.get('target_duos', []): reqs2 += add_groups(t, 'target', main, set(must2))
                if fin: reqs2 += add_groups(fin, 'finisher', main, set(must2))
                if solve(must2, main, reqs2) is None: continue
                alts.append(a)
                if len(alts) == 2: break
            out['fallbacks'][m] = alts
        return out

    return plan_for
