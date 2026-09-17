# -*- coding: utf-8 -*-
"""운용 가이드 UI (페이블, 2026-09-17).
- 런 시작 '추천 빌드' 카드: 접이식 '운용법'.
- 홈: 메인 빌드 아래 접이식 '운용법' + 채운 칸 수로 지금 단계(초반/완성 후) 강조 — 게임 중에 보는 게 진짜 용도다.
"""
import io, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JS = os.path.join(ROOT, 'app', 'src', 'app.js'); CSS = os.path.join(ROOT, 'app', 'src', 'app.css')
def load(p): return io.open(p, encoding='utf-8').read()
def save(p, s): io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, old, new, n=1):
    c = s.count(old); assert c == n, ('anchor %d != %d: %r' % (c, n, old[:90])); return s.replace(old, new)

s = load(JS)
if 'function playstyleBox' in s:
    print('app.js: 이미 적용됨'); sys.exit(0)

# 공용 렌더러 — el() 정의 뒤에 둔다
s = rep(s, "  function el(html) { var d = document.createElement('div'); d.innerHTML = html; return d.firstElementChild; }\n",
"""  function el(html) { var d = document.createElement('div'); d.innerHTML = html; return d.firstElementChild; }
  // 운용 가이드. phase: 'early' | 'late' | null — 지금 단계를 강조 (홈에서 채운 칸 수로 판단)
  var PS_ROWS = [['loop', '기본 루프'], ['key', '기억할 것'], ['cast', '마법진'], ['early', '초반 · 칸 2개 이하'], ['late', '완성 후'], ['avoid', '하지 말 것']];
  function playstyleBox(dirId, weapon, phase, open) {
    var d = ((DATA.builds.weapons[weapon] || {}).directions || []).find(function (x) { return x.id === dirId; });
    var ps = d && d.playstyle; if (!ps) return null;
    var det = el('<details class="ps"' + (open ? ' open' : '') + '><summary><span>운용법</span>' +
      (phase ? '<span class="tagx">' + (phase === 'early' ? '지금은 초반' : '빌드 완성') + '</span>' : '') + '</summary></details>');
    PS_ROWS.forEach(function (r) {
      if (!ps[r[0]]) return;
      var hot = phase && (r[0] === phase);
      var dim = phase && ((r[0] === 'early' && phase === 'late') || (r[0] === 'late' && phase === 'early'));
      det.appendChild(el('<div class="psrow' + (hot ? ' hot' : '') + (dim ? ' dimmed' : '') + '"><div class="lb">' + esc(r[1]) + '</div><div class="tx">' + esc(ps[r[0]]) + '</div></div>'));
    });
    return det;
  }
""")

# 런 시작: 추천 빌드 카드에 붙인다
s = rep(s, """        (d.key_hammers.length ? '<div class="xs dim">망치: ' + esc(d.key_hammers.join(', ')) + '</div>' : '') + '</div>'));
    });""",
"""        (d.key_hammers.length ? '<div class="xs dim">망치: ' + esc(d.key_hammers.join(', ')) + '</div>' : '') + '</div>');
      var pb = playstyleBox(d.id, startSel.weapon, null, false);
      if (pb) dc.appendChild(pb);
      root.appendChild(dc);
    });""")
s = rep(s, """    r.directions.forEach(function (d) {
      root.appendChild(el('<div class="card"><div class="row"><b>' + esc(d.name_ko) + '</b><span class="xs dim">★' + d.difficulty + '</span></div>' +""",
"""    r.directions.forEach(function (d) {
      var dc = el('<div class="card"><div class="row"><b>' + esc(d.name_ko) + '</b><span class="xs dim">★' + d.difficulty + '</span></div>' +""")

# 홈: 메인 빌드 카드 안, '다음에 원하는 것' 위. 칸 2개 이하 = 초반
s = rep(s, """    if (ds.length) {
      var det = el('<details style="margin-top:8px"><summary class="sm dim">다음에 원하는 것 · 융합 진행도</summary></details>');""",
"""    if (ds.length) {
      // 운용법 — 게임 중에 보는 게 진짜 용도. 채운 칸으로 초반/완성 후를 강조한다 (사용자: 초반에 완성 후 운용을 해서 죽음 저항을 다 씀)
      var ns = filledSlots(st);
      var psb = playstyleBox(ds[0].id, st.weapon, ns <= 2 ? 'early' : 'late', false);
      if (psb) { psb.style.marginTop = '8px'; card.appendChild(psb); }
    }
    if (ds.length) {
      var det = el('<details style="margin-top:8px"><summary class="sm dim">다음에 원하는 것 · 융합 진행도</summary></details>');""")
save(JS, s); print('app.js: 운용법 접이식 (런 시작 + 홈)')

c = load(CSS)
if '.ps summary' not in c:
    c = c.rstrip('\n') + """

/* 운용 가이드 (2026-09-17) */
details.ps{border:1px solid var(--line); border-radius:10px; padding:0 10px; background:var(--panel-2); margin-top:8px}
.ps summary{display:flex; align-items:center; gap:8px; min-height:44px; font-size:.88em; font-weight:600; color:var(--text); cursor:pointer; list-style:none}
.ps summary::-webkit-details-marker{display:none}
.ps summary::before{content:'▸'; color:var(--dim); font-size:.9em}
details.ps[open] summary::before{content:'▾'}
.ps summary .tagx{margin-left:auto; color:var(--accent); border-color:var(--accent)}
.psrow{display:flex; gap:10px; padding:8px 0; border-top:1px solid var(--line); font-size:.82em; line-height:1.45}
.psrow .lb{flex:0 0 78px; color:var(--dim); font-weight:600}
.psrow .tx{flex:1; min-width:0; word-break:keep-all}
.psrow.hot{background:rgba(216,179,101,.08); margin:0 -10px; padding-left:10px; padding-right:10px}
.psrow.hot .lb{color:var(--accent)}
.psrow.dimmed{opacity:.5}
"""
    save(CSS, c); print('app.css: 운용법 스타일')
