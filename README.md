# 하데스 2 빌드 길잡이

게임 중 폰으로 열어 보는 초보용 빌드 추천 도구. 무기·신·은혜·망치를 고르면 지금 빌드에 맞는 우선순위와 이유를 알려준다.

## 앱 실행

### GitHub Pages (폰에서 쓰기 제일 편함)

저장소 **Settings → Pages → Source: Deploy from a branch → Branch: `main` / 폴더 `/docs` → Save**

몇 분 뒤 아래 주소로 열린다. 폰 브라우저로 열고 **홈 화면에 추가**하면 앱처럼 쓸 수 있다.

```
https://khlee88.github.io/hades2_build_guide/
```

### 그 밖의 방법

- **로컬** — `python -m http.server 8777` 후 `http://localhost:8777/docs/`
  같은 WiFi의 폰에서는 `http://<PC의 IP>:8777/docs/`
- **Claude Artifact** — `app/index.html`을 그대로 배포 (Artifact 규약상 `<html>`·`<body>`가 없는 조각이다)
- 어느 쪽이든 **외부 요청이 0**이라 한 번 열면 오프라인에서도 돌아간다. 진행 상황은 브라우저에 저장된다.

## 빌드

```
node app/build.js
```

`data/*.json` + `engine/*.js` + `app/src/*` 를 묶어 두 파일을 만든다.

| 산출물 | 용도 |
|---|---|
| `docs/index.html` | **단독 실행용 완전한 문서.** GitHub Pages·로컬·파일 열기 전부 이것 |
| `app/index.html` | Claude Artifact 전용 (`<html>`/`<body>` 없는 조각) |

데이터나 엔진을 고치면 다시 실행해 커밋한다. 검증은 `node data/validate.js`, `node engine/test.js`.

## 선택 기록

관리 화면 → **선택 기록**에서 지금까지의 선택을 `hades2_log_YYYYMMDD_HHMM.jsonl`로 내려받을 수 있다.
새 런을 시작할 때 지난 런의 결과(루트·클리어/사망/중단·지역)를 입력하면 결과 라벨이 붙는다.
스키마와 설계 근거는 [`data/RUN_LOG.md`](data/RUN_LOG.md). 저장소에는 `data/runs/history.jsonl` 한 경로에 덮어쓴다.

## 출처

게임 데이터는 아래에서 수집해 한글판 표기로 대조·정리한 것이다. 원본은 모두 **CC BY-NC-SA**이며 이 저장소의 `data/`도 같은 조건을 따른다.

- [Hades Wiki (Fandom)](https://hades.fandom.com/) — 은혜·융합·전설 효과와 전제조건, 무기·양상, 아르카나, 기념품 (CC BY-NC-SA)
- [나무위키 Hades II](https://namu.wiki/w/Hades%20II) — 한글판 인게임 명칭 전량 대조 (CC BY-NC-SA 2.0 KR)
- 빌드 방향 검증(2026-09-10): [나무위키 Hades II/무기](https://namu.wiki/w/Hades%20II/%EB%AC%B4%EA%B8%B0) 운용법, 디시 하데스 갤러리 뉴비 가이드 [51882](https://gall.dcinside.com/mgallery/board/view/?id=hades&no=51882)·[49018](https://gall.dcinside.com/mgallery/board/view/?id=hades&no=49018)·[38884](https://gall.dcinside.com/mgallery/board/view/?id=hades&no=38884), [Lee Reamsnyder — Hades 2 build guide](https://www.leereamsnyder.com/hades-2-build-guide). 방향별 근거는 `data/build_directions.json`의 `sources`, 요약은 `data/BUILD_DIRECTIONS.md`

Hades II는 Supergiant Games의 저작물이며 이 저장소는 팬 제작 도구로 공식과 무관하다.
빌드 방향·우선순위 판단은 커뮤니티 통념을 참고한 제작자의 해석이므로 정답이 아니다.
