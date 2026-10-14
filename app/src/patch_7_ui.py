# -*- coding: utf-8 -*-
"""7-C UI (페이블, 2026-10-14) — 로그 12런에서 드러난 입력 공백.
1. 지역 자동 추정: 진행 중 pick 131개 전부 rg=1 (한 번도 안 바꿈). 종료 시트와 같은 공식(은혜·망치 수/7)을 홈·엔진·로그에 쓴다.
   수동 값은 더 클 때만 이긴다. 관리 화면 세그먼트 1 = '자동'.
2. 희귀도 토글 제거: 189개 제시 전부 '일반'. rarity 값(일반/융합/전설)은 로그·엔진에 그대로 남는다.
"""
import io, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JS = os.path.join(ROOT, 'app', 'src', 'app.js'); CSS = os.path.join(ROOT, 'app', 'src', 'app.css')
def load(p): return io.open(p, encoding='utf-8').read()
def save(p, s): io.open(p, 'w', encoding='utf-8', newline='\n').write(s)
def rep(s, old, new, n=1):
    c = s.count(old); assert c == n, ('anchor %d != %d: %r' % (c, n, old[:90])); return s.replace(old, new)

s = load(JS)
if 'regionEff' in s:
    print('app.js: 이미 적용됨'); sys.exit(0)

# 1. 지역 자동 추정
s = rep(s, """  // 제시된 것 전부를 남긴다 — 고른 것만 남기면 "3택 중 선택" 모델을 못 만든다
  function logPick(kind, rows, chosenId) {
    if (!RUN || !RUN.rid) return;
    var st = RUN.state;
    logPush({
      t: 'pick', kind: kind, rg: st.region, ns: filledSlots(st),
      dir: E.directionScores(st).slice(0, 2).map(function (d) { return [d.id, d.weight]; }),""",
"""  // 7-C: 지역은 은혜·망치 수로 추정한다 (보상 6~8개당 1지역). 12런 로그에서 진행 중 지역을 바꾼 적이 0회라 엔진이 늘 1지역으로 알았다.
  // 수동 값(관리 화면)은 추정보다 클 때만 이긴다. 엔진·로그·홈 표시 전부 이 값을 쓴다
  function regionEff(st) {
    var n = (st.boons || []).length + (st.hammers || []).length;
    return Math.max(st.region || 1, Math.min(4, 1 + Math.floor(n / 7)));
  }
  function engSt(st) { return Object.assign({}, st, { region: regionEff(st) }); }
  // 제시된 것 전부를 남긴다 — 고른 것만 남기면 "3택 중 선택" 모델을 못 만든다
  function logPick(kind, rows, chosenId) {
    if (!RUN || !RUN.rid) return;
    var st = RUN.state;
    logPush({
      t: 'pick', kind: kind, rg: regionEff(st), ns: filledSlots(st),
      dir: E.directionScores(engSt(st)).slice(0, 2).map(function (d) { return [d.id, d.weight]; }),""")
s = rep(s, "    var est = Math.max(prev.state.region || 1, Math.min(4, 1 + Math.floor(n / 7)));   // 보상 6~8개당 1지역, 수동 지역이 더 크면 그것",
           "    var est = regionEff(prev.state);   // 7-C: 홈·엔진과 같은 추정")
s = rep(s, "    var ds = E.directionScores(st);", "    var ds = E.directionScores(engSt(st));")
s = rep(s, "      '<button class=\"tagx\" data-region>' + st.region + '지역</button>' +",
           "      '<button class=\"tagx\" data-region>' + regionEff(st) + '지역' + ((st.region || 1) > 1 ? '' : ' · 자동') + '</button>' +")
s = rep(s, "      var grows = E.recommendGods(RUN.state, godSel);", "      var grows = E.recommendGods(engSt(RUN.state), godSel);")
s = rep(s, "          var rows = isBoon ? E.recommendBoons(RUN.state, pickSel) : E.recommendHammers(RUN.state, pickSel.map(function (p) { return p.id; }));",
           "          var rows = isBoon ? E.recommendBoons(engSt(RUN.state), pickSel) : E.recommendHammers(engSt(RUN.state), pickSel.map(function (p) { return p.id; }));")
s = rep(s, "    body.appendChild(seg('지역', [[1, '1'], [2, '2'], [3, '3'], [4, '4']], st.region, function (v) { st.region = v; saveRun(); logPush({ t: 'rg', v: v }); render(); }));",
           "    body.appendChild(seg('지역 (은혜 수로 자동 추정 · 더 크게만 고정)', [[1, '자동'], [2, '2'], [3, '3'], [4, '4']], st.region, function (v) { st.region = v; saveRun(); logPush({ t: 'rg', v: v }); render(); }));")
s = rep(s, "    var k = E.recommendKeepsake(st);", "    var k = E.recommendKeepsake(engSt(st));")
s = rep(s, "    E.directionScores(st).forEach(function (d) {", "    E.directionScores(engSt(st)).forEach(function (d) {")

# 2. 희귀도 토글 제거
s = rep(s, "  var RAR = ['common', 'rare', 'epic', 'heroic'];\n  var RAR_KO = { common: '일반', rare: '희귀', epic: '특별', heroic: '영웅' };\n", "")
s = rep(s, """        var fixed = p.rarity === 'duo' || p.rarity === 'legendary';
        var c = el('<span class="pick">' + esc(nm(p.id)) +
          (fixed ? '' : '<button class="rar">' + RAR_KO[p.rarity] + '</button>') + '<button class="x">✕</button></span>');
        if (!fixed) c.querySelector('.rar').onclick = function () { p.rarity = RAR[(RAR.indexOf(p.rarity) + 1) % 4]; draw(); };""",
"""        // 7-C: 희귀도 토글 제거 — 12런 189개 제시 전부 '일반'(한 번도 안 씀). rarity 값(일반/융합/전설)은 그대로 로그에 남는다
        var c = el('<span class="pick">' + esc(nm(p.id)) + '<button class="x">✕</button></span>');""")
save(JS, s); print('app.js: 7-C 지역 자동 추정 + 희귀도 토글 제거')

c = load(CSS)
if '.pick .rar' in c or '.rar' in c:
    import re
    c2 = re.sub(r'\n[^\n]*\.rar[^\n]*\n', '\n', c)
    if c2 != c: save(CSS, c2); print('app.css: .rar 규칙 제거')
