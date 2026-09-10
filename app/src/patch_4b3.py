# -*- coding: utf-8 -*-
"""4-B 추가: 신·무기 심볼(인라인 SVG).
색만으로 구분하던 것을 모양+색으로. 외부 리소스 0 원칙 유지, 신 색으로 currentColor 채색."""
import io, os, sys
SRC = os.path.dirname(os.path.abspath(__file__))
rd = lambda f: io.open(os.path.join(SRC, f), encoding='utf-8').read()
wr = lambda f, s: io.open(os.path.join(SRC, f), 'w', encoding='utf-8').write(s)
def sub(s, old, new, tag):
    if old not in s: print('패턴 못 찾음:', tag); sys.exit(1)
    return s.replace(old, new, 1)

j = rd('app.js')
if 'var SYM' in j:
    print('app.js: 이미 적용됨'); sys.exit(0)

SYM = r"""
  // ── 신·무기 심볼 (인라인 SVG, 24x24 viewBox) ─────────
  // f: 채움 경로 / s: 선 경로. 색은 currentColor라 신 색이 그대로 들어간다.
  var SYM = {
    zeus:       { f: 'M13 2 5 14h5l-2 8 9-13h-5z' },                                     // 벼락
    hestia:     { f: 'M12 22c3.6 0 6-2.6 6-6 0-4-4-6-4-10 0 0-2.6 1.8-2.6 4.4C11.4 9 10 8 10 7c-1.8 1.8-2.6 4.4-2.6 7 0 3.4 2.4 6 4.6 6z' },  // 불꽃
    poseidon:   { s: 'M12 2v20M7 9v2a5 5 0 0 0 10 0V9M7 9V6M17 9V6' },                    // 삼지창
    demeter:    { s: 'M12 2v20M3.5 7l17 10M20.5 7l-17 10M12 7l-3-2M12 7l3-2M12 17l-3 2M12 17l3 2' }, // 눈 결정
    apollo:     { s: 'M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2.1 2.1M16.9 16.9 19 19M19 5l-2.1 2.1M7.1 16.9 5 19', c: [12, 12, 4] },  // 태양
    aphrodite:  { f: 'M12 20.5S4.5 15.6 4.5 10.6A4.1 4.1 0 0 1 12 8.2a4.1 4.1 0 0 1 7.5 2.4c0 5-7.5 9.9-7.5 9.9z' },  // 하트
    hephaestus: { s: 'M3 21l8.5-8.5M11 4l9 9-2.8 2.8-9-9z' },                             // 망치
    hera:       { s: 'M12 8.5 9 4.5h6zM12 22a6 6 0 1 0 0-12 6 6 0 0 0 0 12z' },           // 반지
    ares:       { s: 'M5 19 19 5M19 19 5 5M3 17l4 4M21 17l-4 4' },                        // 교차한 검
    hermes:     { s: 'M3 8h9M2 12h7M4 16h6M13 5c4 0 7 3 7 7s-3 7-7 7z' },                 // 날개·속도선
    artemis:    { s: 'M6 3a12 12 0 0 1 0 18M6 12h13M15 8l4 4-4 4' },                      // 활과 화살
    selene:     { f: 'M16.5 2.5a9.5 9.5 0 1 0 5 13.4 7.6 7.6 0 0 1-5-13.4z' },            // 초승달
    chaos:      { s: 'M12 13.5a2 2 0 1 1-1.4-3.4 5 5 0 1 1 5 5 8 8 0 1 1-8-8' },          // 소용돌이
    staff:      { s: 'M4 20 15.5 8.5M12 4l1-2 1 2 2 1-2 1-1 2-1-2-2-1z', c: [17.5, 6, 3] },// 지팡이
    blades:     { s: 'M7.5 21 4 6l5 2.5zM16.5 21 20 6l-5 2.5z' },                          // 쌍검
    flames:     { s: 'M12 21v-7M9.5 4.5c0 2-2 3-2 5.5 0 2.4 2 4 4.5 4s4.5-1.6 4.5-4c0-3.4-3.5-4.5-3.5-8 0 0-1.8 1.2-1.8 3 0-.9-1.7-.5-1.7-.5z' },  // 횃불
    axe:        { s: 'M12 21V5M12 6.5c3.4-4 9-2.8 9 1.4 0 3.2-4.6 4.2-9 2z' },             // 도끼
  };
  function sym(id, size) {
    var d = SYM[id]; if (!d) return '';
    return '<svg class="sym" viewBox="0 0 24 24" width="' + size + '" height="' + size + '" fill="none" ' +
      'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
      (d.c ? '<circle cx="' + d.c[0] + '" cy="' + d.c[1] + '" r="' + d.c[2] + '"/>' : '') +
      (d.f ? '<path d="' + d.f + '" fill="currentColor" stroke="none"/>' : '') +
      (d.s ? '<path d="' + d.s + '"/>' : '') + '</svg>';
  }
"""
j = sub(j, "  function el(html) { var d = document.createElement('div'); d.innerHTML = html; return d.firstElementChild; }",
        "  function el(html) { var d = document.createElement('div'); d.innerHTML = html; return d.firstElementChild; }\n" + SYM.strip('\n'), 'SYM')

# 신 그리드: 색 점 → 심볼
j = sub(j, """        '<span class="ord"></span><span class="dot" style="background:' + GC[id] + '"></span>' +
        '<span class="n">' + esc(nm(id)) + '</span>' +""",
"""        '<span class="ord"></span><span class="gi" style="color:' + GC[id] + '">' + sym(id, 24) + '</span>' +
        '<span class="n">' + esc(nm(id)) + '</span>' +""", 'god grid sym')

# 은혜 선택의 신 탭에도
j = sub(j, """        var b = el('<button class="chip" aria-pressed="' + (godTab === id) + '" style="border-color:' + GC[id] + '">' + esc(nm(id)) + '</button>');""",
"""        var b = el('<button class="chip" aria-pressed="' + (godTab === id) + '" style="border-color:' + GC[id] + '">' +
          '<span class="gi" style="color:' + GC[id] + '">' + sym(id, 17) + '</span>' + esc(nm(id)) + '</button>');""", 'god tab sym')

# 무기 카드
j = sub(j, """      var b = el('<button class="wcard" ' + (ready ? '' : 'disabled') + ' aria-pressed="' + (startSel.weapon === w.id) + '">' +
        '<div class="n">' + esc(w.name_ko) + '</div><div class="a">' + esc(ready ? (w.alias_ko || '') : '준비 중') + '</div></button>');""",
"""      var b = el('<button class="wcard" ' + (ready ? '' : 'disabled') + ' aria-pressed="' + (startSel.weapon === w.id) + '">' +
        '<div class="n"><span class="gi wi">' + sym(w.id, 20) + '</span>' + esc(w.name_ko) + '</div>' +
        '<div class="a">' + esc(ready ? (w.alias_ko || '') : '준비 중') + '</div></button>');""", 'weapon sym')

# 홈 상단 무기명에도
j = sub(j, """    var top = el('<div class="top"><div class="t">' + esc(wp.name_ko) + '</div>' +""",
        """    var top = el('<div class="top"><div class="t"><span class="gi wi">' + sym(wp.id, 19) + '</span>' + esc(wp.name_ko) + '</div>' +""", 'home sym')
wr('app.js', j); print('app.js: 심볼 17종 추가')

c = rd('app.css')
if '.sym{' not in c:
    c = sub(c, ".god .dot{width:12px; height:12px; border-radius:50%}",
            ".god .gi{display:flex; align-items:center; justify-content:center; height:26px}", 'god dot')
    c += """
/* 신·무기 심볼 */
.sym{display:block; overflow:visible}
.gi{display:inline-flex; align-items:center; justify-content:center; flex:0 0 auto}
.chip .gi{margin-right:6px; vertical-align:-3px}
.chip{display:inline-flex; align-items:center}
.wcard .n{display:flex; align-items:center; gap:7px}
.wi{color:var(--accent)}
.wcard:disabled .wi{color:var(--dim)}
.top .t{display:flex; align-items:center; gap:8px}
"""
    wr('app.css', c); print('app.css: 심볼 스타일 추가')
