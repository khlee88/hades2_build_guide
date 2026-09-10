# -*- coding: utf-8 -*-
"""U6 셀레네·카오스 막다른 길 / U7 빌드 시각 KST / U8 뒤로가기 이력 / U9 심볼 교정
+ 아테나·디오니소스 UI 등록"""
import io, os, sys
SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(SRC))
rd = lambda p: io.open(p, encoding='utf-8').read()
wr = lambda p, s: io.open(p, 'w', encoding='utf-8').write(s)
def sub(s, old, new, tag):
    if old not in s: print('패턴 못 찾음:', tag); sys.exit(1)
    return s.replace(old, new, 1)

# ══ U7: 빌드 시각을 KST로 ══
p = os.path.join(ROOT, 'app', 'build.js'); s = rd(p)
if 'KST' not in s:
    s = sub(s, "const stamp = new Date().toISOString().slice(0, 16).replace('T', ' ');",
"""// 사용자가 최신 버전인지 시각으로 확인하므로 UTC가 아니라 한국 시간으로 찍는다 (U7)
const stamp = new Date(Date.now() + 9 * 3600 * 1000).toISOString().slice(0, 16).replace('T', ' ') + ' KST';""", 'U7')
    wr(p, s); print('build.js: 빌드 시각 KST')

j = rd(os.path.join(SRC, 'app.js'))

# ══ 아테나·디오니소스 UI 등록 ══
if "'athena'" not in j:
    j = sub(j, "artemis: '#5fbf8a', selene: '#a9c4ff', chaos: '#c76bd9' };",
               "artemis: '#5fbf8a', athena: '#d9d2b0', dionysus: '#9b59b6', selene: '#a9c4ff', chaos: '#c76bd9' };", 'GC')
    j = sub(j, "'hermes', 'artemis', 'selene', 'chaos'];",
               "'hermes', 'artemis', 'athena', 'dionysus', 'selene', 'chaos'];", 'GOD_ORDER')

# ══ U9: 심볼 교정 (게임 내 상징에 맞춤) + 신규 2신 ══
if 'athena:' not in j:
    # 헤라: 반지 → 오메가(Ω)
    j = sub(j, "    hera:       { s: 'M12 8.5 9 4.5h6zM12 22a6 6 0 1 0 0-12 6 6 0 0 0 0 12z' },           // 반지",
               "    hera:       { s: 'M6 20.5h4.2v-1.8a6.8 6.8 0 1 1 3.6 0v1.8H18' },                     // 오메가", 'hera sym')
    # 헤파이스토스: 망치 → 대장장이 집게
    j = sub(j, "    hephaestus: { s: 'M3 21l8.5-8.5M11 4l9 9-2.8 2.8-9-9z' },                             // 망치",
               "    hephaestus: { s: 'M7.5 21 11.2 12.6M16.5 21 12.8 12.6M11 11 7.5 3M13 11l3.5-8', c: [12, 11.8, 1.5] },  // 대장장이 집게", 'heph sym')
    # 데메테르: 눈 결정 → 밀 이삭 (얼어붙은 줄기 + 낟알)
    j = sub(j, "    demeter:    { s: 'M12 2v20M3.5 7l17 10M20.5 7l-17 10M12 7l-3-2M12 7l3-2M12 17l-3 2M12 17l3 2' }, // 눈 결정",
               "    demeter:    { s: 'M12 22V4', f: 'M12 10.2c-2.7 0-3.8-1.9-3.8-3.8 1.9 0 3.8 1 3.8 3.8zM12 10.2c2.7 0 3.8-1.9 3.8-3.8-1.9 0-3.8 1-3.8 3.8zM12 15.4c-2.7 0-3.8-1.9-3.8-3.8 1.9 0 3.8 1 3.8 3.8zM12 15.4c2.7 0 3.8-1.9 3.8-3.8-1.9 0-3.8 1-3.8 3.8z' },  // 밀 이삭", 'demeter sym')
    # 아레스: 교차검 → 세로 검 + 양옆 불꽃
    j = sub(j, "    ares:       { s: 'M5 19 19 5M19 19 5 5M3 17l4 4M21 17l-4 4' },                        // 교차한 검",
               "    ares:       { s: 'M12 21V5.5M12 5.5 10 8.5M12 5.5 14 8.5M8.6 11h6.8', f: 'M8.4 11.4c-2.1 1.2-2.6 3.4-1 5 .3-1.7 1.1-2.4 2.7-2.9zM15.6 11.4c2.1 1.2 2.6 3.4 1 5-.3-1.7-1.1-2.4-2.7-2.9z' },  // 양옆 불꽃 검", 'ares sym')
    # 헤르메스: 속도선 → 날개
    j = sub(j, "    hermes:     { s: 'M3 8h9M2 12h7M4 16h6M13 5c4 0 7 3 7 7s-3 7-7 7z' },                 // 날개·속도선",
               "    hermes:     { f: 'M21.5 4.6c-6.3.4-11.2 3-14.3 7.8-.9 1.3-1.6 2.8-2.2 4.4 5.5.5 9.9-1.2 13.2-4.9 2.3-2.6 3.3-4.9 3.3-7.3z', s: 'M6.6 15.4c2.4-.9 4.4-2.1 6.1-3.6M8.8 12.2c2.2-.6 4.1-1.6 5.6-2.9' },  // 날개", 'hermes sym')
    # 신규 2신
    j = sub(j, "    staff:      {", """    athena:     { s: 'M12 2.5 4.5 5.5v6c0 4.6 3.1 8.6 7.5 10 4.4-1.4 7.5-5.4 7.5-10v-6z', f: 'M12 8.5 9.6 13h4.8z' },  // 방패
    dionysus:   { s: 'M12 8.5V4.5c1.6-.6 3-.6 4-.2', f: 'M9 9.5a1.7 1.7 0 1 0 0 3.4 1.7 1.7 0 0 0 0-3.4zm6 0a1.7 1.7 0 1 0 0 3.4 1.7 1.7 0 0 0 0-3.4zm-3 3.4a1.7 1.7 0 1 0 0 3.4 1.7 1.7 0 0 0 0-3.4zm-2.2 3.6a1.7 1.7 0 1 0 0 3.4 1.7 1.7 0 0 0 0-3.4zm4.4 0a1.7 1.7 0 1 0 0 3.4 1.7 1.7 0 0 0 0-3.4z' },  // 포도송이
    staff:      {""", 'new syms')

# ══ U8: 시트를 닫을 때 뒤로가기 이력을 되돌린다 ══
if 'closeSheet(fromPop)' not in j:
    j = sub(j, """  function openSheet(name) { UI.screen = name; saveUI(); history.pushState({ sheet: name }, ''); render(); }
  function closeSheet() { if (UI.screen) { UI.screen = null; saveUI(); render(); } }
  window.addEventListener('popstate', function () { if (UI.screen) { UI.screen = null; saveUI(); render(); } });""",
"""  function openSheet(name) { UI.screen = name; saveUI(); history.pushState({ sheet: name }, ''); render(); }
  // X로 닫을 때도 pushState로 쌓인 이력을 되감는다. 안 그러면 열고 닫을수록 뒤로가기가 밀린다 (U8)
  function closeSheet(fromPop) {
    if (!UI.screen) return;
    if (!fromPop && history.state && history.state.sheet) { history.back(); return; } // popstate가 렌더를 맡는다
    UI.screen = null; saveUI(); render();
  }
  window.addEventListener('popstate', function () { closeSheet(true); });""", 'U8')

# ══ U6: 셀레네·카오스는 은혜 목록이 없으므로 다른 화면으로 ══
if 'GUEST_INFO' not in j:
    j = sub(j, "  var pickSel = [], godTab = null,",
"""  // 은혜 목록이 없는 신 — 문을 골라도 빈 목록이 뜨던 문제 (U6)
  var GUEST_INFO = {
    selene: { to: 'manage', title: '셀레네는 비술을 줍니다',
      body: '은혜가 아니라 <b>비술</b>을 하나 받습니다. 관리 화면에서 받은 비술을 눌러 두면 추천에 반영됩니다.',
      tip: '초보 추천 순서: 달빛줄기(마력 30) → 늑대 포효(50) → 월색 담수(70)' },
    chaos: { to: null, title: '카오스는 저주를 먼저 받습니다',
      body: '일정 시간 <b>저주</b>를 견디면 축복을 줍니다. 지금 화면에서는 개별 축복을 추천하지 않습니다.',
      tip: '초보는 체력·마력이 잠시 줄어드는 저주만 받는 게 안전합니다. 피해를 더 받거나 이동이 느려지는 저주는 방 클리어가 위험해집니다.' },
  };
  function guestSheet(id) {
    var g = GUEST_INFO[id], body = document.createElement('div');
    body.appendChild(el('<div class="card"><div class="row"><span class="gi" style="color:' + GC[id] + '">' + sym(id, 26) + '</span><b>' + esc(g.title) + '</b></div>' +
      '<div class="sm" style="margin-top:8px">' + g.body + '</div>' +
      '<div class="sm dim" style="margin-top:8px">' + esc(g.tip) + '</div></div>'));
    if (g.to === 'manage') {
      var b = el('<div class="cta"><button>관리에서 비술 고르기</button></div>');
      b.querySelector('button').onclick = function () { UI.screen = 'manage'; saveUI(); render(); };
      body.appendChild(b);
    }
    return wrapSheet(nm(id), body);
  }

  var pickSel = [], godTab = null,""", 'U6 info')
    # 신 선택 → 문 결정 시 분기
    j = sub(j, """          RUN.pending_god = r.id; pickSel = []; godTab = r.id;
          UI.screen = 'boons'; saveUI(); saveRun(); render();""",
"""          if (GUEST_INFO[r.id]) { UI.screen = 'guest:' + r.id; saveUI(); render(); return; }
          RUN.pending_god = r.id; pickSel = []; godTab = r.id;
          UI.screen = 'boons'; saveUI(); saveRun(); render();""", 'U6 branch')
    # 라우팅
    j = sub(j, "    else if (UI.screen === 'manage') app.appendChild(viewManage());",
               "    else if (UI.screen === 'manage') app.appendChild(viewManage());\n    else if (String(UI.screen).indexOf('guest:') === 0) app.appendChild(guestSheet(UI.screen.slice(6)));", 'U6 route')
    # 은혜 선택의 신 탭에서 셀레네/카오스를 눌러도 동일 안내
    j = sub(j, "        b.onclick = function () { godTab = id; UI.god_tab = id; saveUI(); searchQ = ''; draw(); };",
               "        b.onclick = function () {\n          if (GUEST_INFO[id]) { UI.screen = 'guest:' + id; saveUI(); render(); return; }\n          godTab = id; UI.god_tab = id; saveUI(); searchQ = ''; draw();\n        };", 'U6 tab')

wr(os.path.join(SRC, 'app.js'), j); print('app.js: U6/U8/U9 + 신규 2신')
