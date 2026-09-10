# -*- coding: utf-8 -*-
"""4-B 추가: 1·2위 점수가 가까우면 '비슷함 · 취향' 표시.
근거 — 시나리오 20개의 1·2위 점수차를 뽑으니 0~2.5 / 8 이상 두 덩어리로 갈렸다.
융합 완성(+5)·항상 챙김(+7.5)·회피(-8) 같은 항목이 통째로 붙거나 안 붙어서,
2 미만이면 순위 차이만 남은 것이라 엔진이 사실상 구분하지 못한다."""
import io, os, sys
SRC = os.path.dirname(os.path.abspath(__file__))
rd = lambda f: io.open(os.path.join(SRC, f), encoding='utf-8').read()
wr = lambda f, s: io.open(os.path.join(SRC, f), 'w', encoding='utf-8').write(s)
def sub(s, old, new, tag):
    if old not in s: print('패턴 못 찾음:', tag); sys.exit(1)
    return s.replace(old, new, 1)

j = rd('app.js')
if 'CLOSE_GAP' in j:
    print('app.js: 이미 적용됨'); sys.exit(0)

# 1) 임계값 + 판정 헬퍼
j = sub(j, "  var RAR = ['common', 'rare', 'epic', 'heroic'];",
"""  // 1·2위 점수차가 이 값 미만이면 엔진이 사실상 구분 못 한 것으로 보고 '취향' 표시.
  // 근거: 시나리오 20개 점수차 분포가 0~2.5와 8 이상으로 갈리고 그 사이가 비어 있다.
  var CLOSE_GAP = 2;
  function closeSet(rows) {
    var s = {};
    var fin = rows.filter(function (r) { return isFinite(r.score); });
    if (fin.length < 2) return s;
    var top = fin[0].score;
    var near = fin.filter(function (r) { return top - r.score < CLOSE_GAP; });
    if (near.length >= 2) near.forEach(function (r) { s[r.id] = true; });
    return s;
  }
  var CLOSE_CHIP = '<span class="close">비슷함 · 취향</span>';

  var RAR = ['common', 'rare', 'epic', 'heroic'];""", 'CLOSE_GAP')

# 2) 컴팩트 행(은혜·망치)에 표시
j = sub(j, "          rows.forEach(function (r, i) { box.appendChild(compactRec(r, i, isBoon)); });",
        "          var cs = closeSet(rows);\n          rows.forEach(function (r, i) { box.appendChild(compactRec(r, i, isBoon, cs[r.id])); });", 'tray close')
j = sub(j, "    function compactRec(r, i, isBoon) {", "    function compactRec(r, i, isBoon, isClose) {", 'compact sig')
j = sub(j, """        (mainBadge ? '<span class="bdg">' + esc(mainBadge) + '</span>' : '') + '</div>' +""",
        """        (mainBadge ? '<span class="bdg">' + esc(mainBadge) + '</span>' : '') +
        (isClose ? CLOSE_CHIP : '') + '</div>' +""", 'compact chip')

# 3) 신 추천 카드에도
j = sub(j, """      E.recommendGods(RUN.state, godSel).forEach(function (r, i) {
        out.appendChild(recCard(r, i, function () {""",
"""      var grows = E.recommendGods(RUN.state, godSel);
      var gcs = closeSet(grows);
      grows.forEach(function (r, i) {
        out.appendChild(recCard(r, i, function () {""", 'gods rows')
j = sub(j, """          UI.screen = 'boons'; saveUI(); saveRun(); render();
        }, '이 문으로'));
      });""",
"""          UI.screen = 'boons'; saveUI(); saveRun(); render();
        }, '이 문으로', gcs[r.id]));
      });""", 'gods close arg')
j = sub(j, "  function recCard(r, i, onDecide, label) {", "  function recCard(r, i, onDecide, label, isClose) {", 'recCard sig')
j = sub(j, """      '<div class="nm">' + slotChip(ent(r.id)) + '<span class="ell">' + esc(nm(r.id)) + '</span></div>' +""",
        """      '<div class="nm">' + slotChip(ent(r.id)) + '<span class="ell">' + esc(nm(r.id)) + '</span>' +
      (isClose ? CLOSE_CHIP : '') + '</div>' +""", 'recCard chip')
wr('app.js', j); print('app.js: 비슷함·취향 표시 추가')

c = rd('app.css')
if '.close{' not in c:
    c += """
/* 1·2위 점수차가 작을 때 (취향 구간) */
.close{flex:0 0 auto; font-size:.66em; font-weight:600; padding:2px 7px; border-radius:999px;
  border:1px solid var(--info); color:var(--info); background:rgba(86,204,242,.1); white-space:nowrap}
"""
    wr('app.css', c); print('app.css: .close 추가')
