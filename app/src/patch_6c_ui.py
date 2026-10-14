# -*- coding: utf-8 -*-
"""6-C UI (페이블 대행, 2026-10-14) — ui/SPEC.md §8.
무기 6개 해금·심볼 2개, 숨김 양상 선택 가능, 추천 빌드 양상 배지·접기·양상 효과 한 줄, logPick 등급."""
import io, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JS = os.path.join(ROOT, 'app', 'src', 'app.js'); CSS = os.path.join(ROOT, 'app', 'src', 'app.css')
def load(p): return io.open(p, encoding='utf-8').read()
def save(p, s): io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, old, new, n=1):
    c = s.count(old); assert c == n, ('anchor %d != %d: %r' % (c, n, old[:90])); return s.replace(old, new)

s = load(JS)
if 'aspBadge' in s:
    print('app.js: 이미 적용됨'); sys.exit(0)

# 심볼: 해골(두개골 채움 + 눈 구멍), 외투(주먹 채움 + 로켓 선)
s = rep(s, "    axe:        { s: 'M6.5 21 16 6', f: 'M11.5 5.2c4.6-2.4 9.5.4 9.5 4.6 0 2.6-1.8 4.6-4.4 5.2-.3-4-2.2-7.4-5.1-9.8z' },  // 도끼",
"""    axe:        { s: 'M6.5 21 16 6', f: 'M11.5 5.2c4.6-2.4 9.5.4 9.5 4.6 0 2.6-1.8 4.6-4.4 5.2-.3-4-2.2-7.4-5.1-9.8z' },  // 도끼
    skull:      { f: 'M12 3a7 7 0 0 0-7 7c0 2.6 1.4 4.6 3 5.8V19h8v-3.2c1.6-1.2 3-3.2 3-5.8a7 7 0 0 0-7-7zM9.5 9.5a1.6 1.6 0 1 1 0 3.2 1.6 1.6 0 0 1 0-3.2zm5 0a1.6 1.6 0 1 1 0 3.2 1.6 1.6 0 0 1 0-3.2z', s: 'M9 19v2.5M12 19v2.5M15 19v2.5' },  // 해골
    coat:       { f: 'M5 12.5c0-1.2.8-2 2-2h1.2V8.2c0-1 .8-1.7 1.8-1.7s1.7.7 1.7 1.7v2.3h1.2V7.6c0-1 .8-1.7 1.8-1.7s1.7.7 1.7 1.7v2.9h.8c1.2 0 2 .8 2 2V15c0 3-2.4 5.5-5.5 5.5h-3C7.4 20.5 5 18 5 15v-2.5z', s: 'M19 4l2 2M20.5 2.5 22 1M17 6.5l1.5-1.5' },  // 외투 (주먹 + 로켓 불꽃)""")

# 무기 잠금 해제
s = rep(s, "      var ready = w.unlock_order <= 4;", "      var ready = (w.aspects || []).length > 0;   // 6-C: 데이터가 갖춰진 무기는 전부 연다 (해골·외투 해금)")

# 숨김 양상 선택 가능
s = rep(s, """      var locked = !!a.hidden;
      var b = el('<button class="chip" aria-pressed="' + (startSel.aspect === a.id) + '">' + esc(a.name_ko) + (locked ? ' 🔒' : '') + '</button>');
      b.onclick = locked ? function () { toast('숨겨진 양상 — 해금 후 사용'); } : function () { startSel.aspect = a.id; rerenderStart(root, asSheet); };""",
"""      // 6-C: 숨김 양상도 고를 수 있다 (사용자가 해금함). 표식만 남긴다
      var b = el('<button class="chip" aria-pressed="' + (startSel.aspect === a.id) + '">' + esc(a.name_ko) + (a.hidden ? ' <span class="xs dim">★숨김</span>' : '') + '</button>');
      b.onclick = function () { startSel.aspect = a.id; rerenderStart(root, asSheet); };""")

# 양상 효과 한 줄 (beginner_note 아래)
s = rep(s, "    root.appendChild(el('<div class=\"wrap sm dim\">' + esc(wp.beginner_note || '') + '</div>'));",
"""    root.appendChild(el('<div class="wrap sm dim">' + esc(wp.beginner_note || '') + '</div>'));
    var curAsp = (wp.aspects || []).find(function (a) { return a.id === startSel.aspect; });
    if (curAsp && curAsp.effect) root.appendChild(el('<div class="wrap sm" style="margin-top:4px"><span class="tagx">' + esc(curAsp.name_ko) + '</span> ' + esc(curAsp.effect) + '</div>'));""")

# 추천 빌드: 배지 + 접기
s = rep(s, """    root.appendChild(el('<h2>추천 빌드</h2>'));
    root.appendChild(el('<div class="wrap sm dim">' + esc(r.note) + '</div>'));
    r.directions.forEach(function (d) {
      var dc = el('<div class="card"><div class="row"><b>' + esc(d.name_ko) + '</b><span class="xs dim">★' + d.difficulty + '</span></div>' +""",
"""    root.appendChild(el('<h2>추천 빌드</h2>'));
    root.appendChild(el('<div class="wrap sm dim">' + esc(r.note) + '</div>'));
    // 6-C: 선택한 양상 기준 배지. 전용(aspects가 그 양상 하나) / 추천(포함) / 없음. 배지 없는 방향은 접는다 (전부 없으면 안 접음)
    var aspBadge = function (d) {
      var asp = ((DATA.builds.weapons[startSel.weapon] || {}).directions || []).find(function (x) { return x.id === d.id; });
      var list = (asp && asp.aspects) || [];
      if (list.length === 1 && list[0] === startSel.aspect) return 'only';
      return list.indexOf(startSel.aspect) >= 0 ? 'rec' : null;
    };
    var anyBadge = r.directions.some(aspBadge);
    var foldBox = null;
    r.directions.forEach(function (d) {
      var badge = aspBadge(d);
      var bh = badge === 'only' ? '<span class="tagx asp only">이 양상 전용</span>' : badge === 'rec' ? '<span class="tagx asp">이 양상 추천</span>' : '';
      var dc = el('<div class="card"><div class="row"><b>' + esc(d.name_ko) + '</b>' + bh + '<span class="xs dim">★' + d.difficulty + '</span></div>' +""")
s = rep(s, """      var pb = playstyleBox(d.id, startSel.weapon, null, false);
      if (pb) dc.appendChild(pb);
      root.appendChild(dc);
    });""",
"""      var pb = playstyleBox(d.id, startSel.weapon, null, false);
      if (pb) dc.appendChild(pb);
      if (anyBadge && !badge) {
        if (!foldBox) { foldBox = el('<details class="card tight fold"><summary class="sm dim">다른 방향</summary></details>'); root.appendChild(foldBox); }
        dc.classList.add('tight'); dc.style.margin = '8px 0 0'; foldBox.appendChild(dc); foldBox.querySelector('summary').textContent = '다른 방향 ' + foldBox.querySelectorAll('.card').length + '개';
      } else root.appendChild(dc);
    });""")

# logPick 등급 (ISSUES P3)
s = rep(s, "        var o = { i: r.id, s: isFinite(r.score) ? r.score : null, k: r.rank || null, b: r.breakdown || {} };",
           "        var o = { i: r.id, s: isFinite(r.score) ? r.score : null, k: r.rank || null, b: r.breakdown || {} };\n        if (r.grade) o.g = r.grade;   // 6-C: 등급 정확도 검증용 (ISSUES P3)")
save(JS, s); print('app.js: 6-C UI')

c = load(CSS)
if '.tagx.asp' not in c:
    c = c.rstrip('\n') + """

/* 6-C 양상 배지·접기 */
.tagx.asp{color:var(--info); border-color:var(--info); margin-left:6px}
.tagx.asp.only{color:var(--accent); border-color:var(--accent)}
details.fold>summary{min-height:44px; display:flex; align-items:center; cursor:pointer}
"""
    save(CSS, c); print('app.css: 배지')
