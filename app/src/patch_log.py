# -*- coding: utf-8 -*-
"""선택 로그(h2.log.v1) 적재 + 내보내기 + 새 런 결과 입력.

설계(사용자와 합의, 2026-09-11):
- 자동 기록. "저장 버튼을 눌러야 남는다"가 아니라 "자동으로 남고 버릴 수 있다" — 기본값이 보존.
- 이벤트 소싱(스냅샷 아님). run / pick / 상태변경 / end 4종을 JSONL로. 재생하면 어느 시점 상태든 복원되고
  나중에 가중치를 바꿔도 과거 런을 재채점할 수 있다.
- pick에는 '그때 화면에 뜬' 점수·순위·breakdown을 그대로 남긴다. 사용자는 그걸 보고 골랐기 때문에
  나중에 재계산한 값으로는 그 선택의 맥락을 복원할 수 없다.
- breakdown이 곧 조건부 로짓의 설계행렬이라 나중에 특징을 새로 만들 필요가 없다.
- 결과 라벨은 지역별 이진값 rg:[1,1,0]. 0=사망, null=중단. 루트(지하/지상)를 반드시 함께 — 없으면
  "2지역"이 두 가지 뜻이 된다.

엔진·데이터는 건드리지 않는다. app/src/app.js만 수정.
실행: python app/src/patch_log.py && node app/build.js
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
P = os.path.join(ROOT, 'app', 'src', 'app.js')
src = io.open(P, encoding='utf-8').read()
if 'h2.log.v1' in src:
    print('app.js: 이미 적용됨'); sys.exit(0)

def rep(old, new, n=1):
    global src
    c = src.count(old)
    assert c == n, ('anchor %d != %d: %r' % (c, n, old[:70]))
    src = src.replace(old, new)

# ── 1. 로그 모듈 ─────────────────────────────────────────────────────────────
rep("""  var saveRun = function () { ls('h2.run.v1', RUN); };
""",
"""  var saveRun = function () { ls('h2.run.v1', RUN); };

  // ── 선택 로그 (h2.log.v1) ────────────────────────────
  // 매 선택마다 자동 누적. 내보내기 전까지 이 폰 안에만 있다.
  // 새 런 시작 화면에서 직전 런을 통째로 버릴 수 있고, 관리 화면에서 런별/전체 삭제할 수 있다.
  var LOG = ls('h2.log.v1') || [];
  var saveLog = function () { ls('h2.log.v1', LOG); };
  function nowKst() { return new Date(Date.now() + 9 * 36e5).toISOString().slice(0, 19).replace('T', ' '); }
  function ridNew() {
    var d = new Date(Date.now() + 9 * 36e5).toISOString();
    return d.slice(2, 4) + d.slice(5, 7) + d.slice(8, 10) + '-' + d.slice(11, 13) + d.slice(14, 16) +
      '-' + Math.random().toString(36).slice(2, 6);
  }
  function logPush(ev) {
    if (!RUN || !RUN.rid) return;
    ev.id = RUN.rid; ev.n = (RUN.seq = (RUN.seq || 0) + 1);
    LOG.push(ev); saveLog(); saveRun();
  }
  function logRuns() {  // [{rid, picks, end}] 최신 순
    var m = {}, order = [];
    LOG.forEach(function (e) {
      if (!m[e.id]) { m[e.id] = { rid: e.id, picks: 0, end: null, w: null, asp: null }; order.push(e.id); }
      var r = m[e.id];
      if (e.t === 'pick') r.picks++;
      else if (e.t === 'end') r.end = e;
      else if (e.t === 'run') { r.w = e.w; r.asp = e.asp; }
    });
    return order.map(function (id) { return m[id]; }).reverse();
  }
  function logDrop(rid) { LOG = LOG.filter(function (e) { return e.id !== rid; }); saveLog(); }
  function filledSlots(st) {
    var n = 0;
    (st.boons || []).forEach(function (id) { var b = IX.boons[id]; if (b && b.occupies_slot) n++; });
    return n;
  }
  // 제시된 것 전부를 남긴다 — 고른 것만 남기면 "3택 중 선택" 모델을 못 만든다
  function logPick(kind, rows, chosenId) {
    if (!RUN || !RUN.rid) return;
    var st = RUN.state;
    logPush({
      t: 'pick', kind: kind, rg: st.region, hp: st.hp_state, ns: filledSlots(st),
      dir: E.directionScores(st).slice(0, 2).map(function (d) { return [d.id, d.weight]; }),
      off: rows.map(function (r) {
        var o = { i: r.id, s: isFinite(r.score) ? r.score : null, k: r.rank || null, b: r.breakdown || {} };
        var p = pickSel.find(function (x) { return x.id === r.id; });
        if (p && p.rarity) o.r = p.rarity;
        if (r._replacing) o.rep = 1;
        return o;
      }),
      c: chosenId,
    });
  }
""")

# ── 2. 런 식별자 ─────────────────────────────────────────────────────────────
rep("""  function newRun(weapon, aspect) {
    return { state:""",
"""  function newRun(weapon, aspect) {
    return { rid: ridNew(), seq: 0, state:""")

# ── 3. 되돌리기도 신호다 (실수 표식) ─────────────────────────────────────────
rep("""    RUN.state = JSON.parse(RUN.history.shift().snap); saveRun(); render();""",
"""    RUN.state = JSON.parse(RUN.history.shift().snap); saveRun(); logPush({ t: 'undo' }); render();""")

# ── 4. 체력 ──────────────────────────────────────────────────────────────────
rep("""    RUN.state.hp_state = o[(i + 1) % 3]; saveRun(); render();""",
"""    RUN.state.hp_state = o[(i + 1) % 3]; saveRun(); logPush({ t: 'hp', v: RUN.state.hp_state }); render();""")

# ── 5. 새 런 시작 화면: 지난 런 결과 입력 ────────────────────────────────────
rep("""  var startSel = { weapon: PREFS.last_weapon, aspect: PREFS.last_aspect };""",
"""  var startSel = { weapon: PREFS.last_weapon, aspect: PREFS.last_aspect };
  // 지난 런 결과. 여기서만 결과 라벨이 생긴다 — 안 넣으면 그 런은 클리어율 통계에서 빠진다
  // (선택 기록 자체는 남으므로 가중치 학습에는 그대로 쓰인다)
  var endSel = { route: 'under', res: 'died', upto: 1 };""")

rep("""    var cta = el('<div class="cta"><button>이 무기로 시작</button></div>');
    cta.querySelector('button').onclick = function () {
      if (RUN && RUN.state.boons.length && !confirm('진행 중인 런이 사라집니다. 새로 시작할까요?')) return;
      PREFS.last_weapon = startSel.weapon; PREFS.last_aspect = startSel.aspect; savePrefs();
      RUN = newRun(startSel.weapon, startSel.aspect); saveRun(); UI.screen = null; saveUI(); render();
    };""",
"""    // 지난 런이 있으면 결과를 먼저 받는다 (탭 두세 번)
    var prev = (RUN && RUN.rid && RUN.state.boons.length) ? RUN : null;
    var dropPrev = { on: false };
    if (prev) {
      if (!endSel._for || endSel._for !== prev.rid) { endSel._for = prev.rid; endSel.upto = prev.state.region; }
      var pc = el('<div class="card"><div class="row"><b style="flex:1">지난 런 결과</b>' +
        '<span class="xs dim">' + esc(nm(prev.state.weapon)) + ' · ' + prev.state.boons.length + '선택</span></div></div>');
      var chipRow = function (label, opts, cur, cb) {
        var r = el('<div style="margin-top:8px"><div class="xs dim">' + esc(label) + '</div></div>');
        var cs = el('<div class="chips" style="margin-top:4px"></div>');
        opts.forEach(function (o) {
          var b = el('<button class="chip" aria-pressed="' + (cur === o[0]) + '">' + esc(o[1]) + '</button>');
          b.onclick = function () { cb(o[0]); rerenderStart(root, asSheet); };
          cs.appendChild(b);
        });
        r.appendChild(cs); return r;
      };
      pc.appendChild(chipRow('루트', [['under', '지하 (크로노스)'], ['surface', '지상 (티폰)']], endSel.route,
        function (v) { endSel.route = v; }));
      pc.appendChild(chipRow('결과', [['clear', '클리어'], ['died', '사망'], ['quit', '중단']], endSel.res,
        function (v) { endSel.res = v; }));
      if (endSel.res !== 'clear')
        pc.appendChild(chipRow('어느 지역에서', [[1, '1지역'], [2, '2지역'], [3, '3지역'], [4, '4지역']], endSel.upto,
          function (v) { endSel.upto = v; }));
      var dp = el('<label class="row sm dim" style="margin-top:10px;gap:8px;cursor:pointer">' +
        '<input type="checkbox" style="width:18px;height:18px"><span>이 런은 기록하지 않기 (조작 실수 등)</span></label>');
      dp.querySelector('input').onchange = function () { dropPrev.on = this.checked; };
      pc.appendChild(dp);
      root.appendChild(pc);
    }

    var cta = el('<div class="cta"><button>이 무기로 시작</button></div>');
    cta.querySelector('button').onclick = function () {
      if (prev) {
        if (dropPrev.on) { logDrop(prev.rid); toast('지난 런 기록을 지웠습니다'); }
        else {
          // rg는 단조라 '어디까지'만으로 결정된다. 0=사망, null=중단(죽은 게 아님 — 실패로 학습하면 안 됨)
          var rgv = [];
          if (endSel.res === 'clear') rgv = [1, 1, 1, 1];
          else {
            for (var i = 1; i < endSel.upto; i++) rgv.push(1);
            rgv.push(endSel.res === 'quit' ? null : 0);
          }
          logPush({ t: 'end', ts: nowKst(), route: endSel.route, res: endSel.res, rg: rgv });
        }
        endSel._for = null;
      } else if (RUN && RUN.state.boons.length && !confirm('진행 중인 런이 사라집니다. 새로 시작할까요?')) return;
      PREFS.last_weapon = startSel.weapon; PREFS.last_aspect = startSel.aspect; savePrefs();
      RUN = newRun(startSel.weapon, startSel.aspect); saveRun();
      logPush({ t: 'run', ts: nowKst(), w: RUN.state.weapon, asp: RUN.state.aspect, grasp: PREFS.grasp_cap,
        arc: (r.arcana.cards || []).map(function (c) { return c.id; }), eng: DATA.__build || null, sv: 1 });
      UI.screen = null; saveUI(); render();
    };""")

# ── 6. 신 선택 ───────────────────────────────────────────────────────────────
rep("""        out.appendChild(recCard(r, i, function () {
          if (GUEST_INFO[r.id]) { UI.screen = 'guest:' + r.id; saveUI(); render(); return; }""",
"""        out.appendChild(recCard(r, i, function () {
          logPick('god', grows, r.id);
          if (GUEST_INFO[r.id]) { UI.screen = 'guest:' + r.id; saveUI(); render(); return; }""")

# ── 7. 은혜·망치 ─────────────────────────────────────────────────────────────
rep("""          var rows = isBoon ? E.recommendBoons(RUN.state, pickSel) : E.recommendHammers(RUN.state, pickSel.map(function (p) { return p.id; }));""",
"""          var rows = isBoon ? E.recommendBoons(RUN.state, pickSel) : E.recommendHammers(RUN.state, pickSel.map(function (p) { return p.id; }));
          lastRows = rows;""")
rep("""    function drawTray() {""",
"""    var lastRows = [];
    function drawTray() {""")
rep("""      if (!no) row.querySelector('.go').onclick = function () {
        pushHistory((isBoon ? '은혜' : '망치') + ' ' + nm(r.id));""",
"""      if (!no) row.querySelector('.go').onclick = function () {
        logPick(isBoon ? 'boon' : 'hammer', lastRows.length ? lastRows : [r], r.id);
        pushHistory((isBoon ? '은혜' : '망치') + ' ' + nm(r.id));""")

# ── 8. 관리 화면의 상태 변경 ─────────────────────────────────────────────────
rep("""st.hp_state, function (v) { st.hp_state = v; saveRun(); render(); }));""",
"""st.hp_state, function (v) { st.hp_state = v; saveRun(); logPush({ t: 'hp', v: v }); render(); }));""")
rep("""st.region, function (v) { st.region = v; saveRun(); render(); }));""",
"""st.region, function (v) { st.region = v; saveRun(); logPush({ t: 'rg', v: v }); render(); }));""")
rep("""pushHistory('기념품 ' + k.name_ko); st.keepsake = k.id; saveRun(); render(); };""",
"""pushHistory('기념품 ' + k.name_ko); st.keepsake = k.id; saveRun(); logPush({ t: 'keep', v: k.id }); render(); };""")
rep("""      b.onclick = function () { st.hex = st.hex === h.id ? null : h.id; saveRun(); render(); };""",
"""      b.onclick = function () { st.hex = st.hex === h.id ? null : h.id; saveRun(); logPush({ t: 'hex', v: st.hex }); render(); };""")
rep("""        pushHistory('제거 ' + nm(id));""",
"""        pushHistory('제거 ' + nm(id)); logPush({ t: 'rm', v: id });""")

# ── 9. 관리 화면: 기록 내보내기 ──────────────────────────────────────────────
rep("""    var nb = el('<button class="danger">새 런 시작</button>');""",
"""    body.appendChild(el('<h2>선택 기록</h2>'));
    var runs = logRuns(), nPick = LOG.filter(function (e) { return e.t === 'pick'; }).length;
    var kbs = Math.round(JSON.stringify(LOG).length / 1024);
    body.appendChild(el('<div class="wrap sm dim">' + runs.length + '런 · ' + nPick + '선택 · ' + kbs + 'KB' +
      (kbs > 3500 ? ' <b>— 용량이 찼습니다. 내보낸 뒤 지워 주세요</b>' : '') + '</div>'));

    function logText() { return LOG.map(function (e) { return JSON.stringify(e); }).join('\\n'); }
    function logName() {
      var d = new Date(Date.now() + 9 * 36e5).toISOString();
      return 'hades2_log_' + d.slice(0, 4) + d.slice(5, 7) + d.slice(8, 10) + '_' + d.slice(11, 13) + d.slice(14, 16) + '.jsonl';
    }
    var eb = el('<div class="wrap" style="display:flex;gap:8px">' +
      '<button class="tagx" style="flex:1;padding:12px" data-dl>파일로 저장</button>' +
      '<button class="tagx" style="flex:1;padding:12px" data-cp>복사</button></div>');
    eb.querySelector('[data-dl]').onclick = function () {
      if (!LOG.length) return toast('기록이 없습니다');
      // Pages는 일반 웹페이지라 다운로드가 된다 (Artifact 샌드박스에서만 막혔던 것)
      try {
        var a = document.createElement('a'), u = URL.createObjectURL(new Blob([logText()], { type: 'application/json' }));
        a.href = u; a.download = logName(); document.body.appendChild(a); a.click();
        setTimeout(function () { URL.revokeObjectURL(u); a.remove(); }, 1000);
        toast(logName() + ' 저장');
      } catch (e) { toast('저장 실패 — 복사를 써 주세요'); }
    };
    eb.querySelector('[data-cp]').onclick = function () {
      if (!LOG.length) return toast('기록이 없습니다');
      var t = logText();
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(t).then(function () { toast('복사했습니다'); }, function () { toast('복사 실패'); });
      else { var ta2 = document.createElement('textarea'); ta2.value = t; document.body.appendChild(ta2); ta2.select(); try { document.execCommand('copy'); toast('복사했습니다'); } catch (e) { toast('복사 실패'); } ta2.remove(); }
    };
    body.appendChild(eb);

    var rl = el('<div class="list"></div>');
    runs.forEach(function (R) {
      var res = R.end ? ({ clear: '클리어', died: '사망', quit: '중단' }[R.end.res] || R.end.res) +
        ' ' + (R.end.rg || []).length + '지역' : '결과 미입력';
      var it = el('<div class="item"><div class="mid"><div class="nm ell">' + esc(R.w ? nm(R.w) : R.rid) +
        '<span class="xs dim"> · ' + R.picks + '선택 · ' + esc(res) + '</span></div>' +
        '<div class="ef ell">' + esc(R.rid) + '</div></div><button class="tagx">✕</button></div>');
      it.querySelector('button').onclick = function () {
        if (!confirm('이 런의 기록을 지울까요?')) return;
        logDrop(R.rid); toast('지웠습니다'); render();
      };
      rl.appendChild(it);
    });
    if (!rl.children.length) rl.appendChild(el('<div class="empty">아직 없습니다</div>'));
    body.appendChild(rl);

    var cl = el('<div class="wrap"><button class="tagx" style="padding:10px 14px">기록 전체 지우기</button></div>');
    cl.querySelector('button').onclick = function () {
      if (!LOG.length) return toast('기록이 없습니다');
      var noEnd = runs.filter(function (R) { return !R.end; }).length;
      if (!confirm('기록 ' + runs.length + '런을 전부 지웁니다.' +
        (noEnd ? '\\n결과 미입력 ' + noEnd + '런이 있습니다.' : '') +
        '\\n내보내기를 먼저 했는지 확인하세요. 되돌릴 수 없습니다.')) return;
      LOG = []; saveLog(); toast('전부 지웠습니다'); render();
    };
    body.appendChild(cl);

    var nb = el('<button class="danger">새 런 시작</button>');""")

io.open(P, 'w', encoding='utf-8', newline='\n').write(src)
print('app.js: 선택 로그 적재 + 내보내기 + 결과 입력 추가')
