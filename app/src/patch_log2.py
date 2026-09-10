# -*- coding: utf-8 -*-
"""로그 UI 검증에서 나온 표기 결함 2건.

1) 무기 이름이 'staff'로 노출 — ent()가 IX.weapons를 안 봐서 nm('staff')이 id를 그대로 반환.
   ent() 체인 **맨 끝**에 추가한다(앞에 넣으면 기존에 해석되던 id의 결과가 바뀔 수 있음).
2) 결과 패널의 '선택 수'가 보유 은혜 수라서 런 목록(로그 pick 수)과 어긋남 → 로그 기준으로 통일.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, 'app', 'src', 'app.js')
src = io.open(P, encoding='utf-8').read()
if 'IX.weapons[id] || null' in src:
    print('app.js: 이미 적용됨'); sys.exit(0)

def rep(old, new, n=1):
    global src
    c = src.count(old)
    assert c == n, ('anchor %d != %d: %r' % (c, n, old[:70]))
    src = src.replace(old, new)

rep("|| IX.gods[id] || ASP[id] || null; };",
    "|| IX.gods[id] || ASP[id] || IX.weapons[id] || null; };")

rep("""        '<span class="xs dim">' + esc(nm(prev.state.weapon)) + ' · ' + prev.state.boons.length + '선택</span></div></div>');""",
"""        '<span class="xs dim">' + esc(nm(prev.state.weapon)) + ' · ' +
        LOG.filter(function (e) { return e.id === prev.rid && e.t === 'pick'; }).length + '선택</span></div></div>');""")

io.open(P, 'w', encoding='utf-8', newline='\n').write(src)
print('app.js: 무기명·선택 수 표기 수정')
