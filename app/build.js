// app/build.js — data + engine + src → app/index.html 단일 파일 생성
// 실행: node app/build.js   (데이터나 엔진이 바뀌면 다시 실행)
// 엔진(engine/*.js)은 **복사만** 한다. 여기서 수정하지 않는다.
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const rd = (...p) => fs.readFileSync(path.join(ROOT, ...p), 'utf8');

const DATA_FILES = {
  boons: 'boons.json', duos: 'duo_legendary.json', hammers: 'hammers.json',
  weapons: 'weapons.json', arcana: 'arcana.json', keepsakes: 'keepsakes.json',
  hexes: 'hexes.json', builds: 'build_directions.json', gods: 'gods.json',
};
const data = {};
for (const [k, f] of Object.entries(DATA_FILES)) data[k] = JSON.parse(rd('data', f));

// 사용자가 최신 버전인지 시각으로 확인하므로 UTC가 아니라 한국 시간으로 찍는다 (U7)
const stamp = new Date(Date.now() + 9 * 3600 * 1000).toISOString().slice(0, 16).replace('T', ' ') + ' KST';
data.__build = stamp;

const weights = rd('engine', 'weights.js');
const engine = rd('engine', 'recommend.js');
const css = rd('app', 'src', 'app.css');
const js = rd('app', 'src', 'app.js');

// Artifact 규약: <!doctype>/<html>/<head>/<body> 없이 본문만. 외부 리소스 0.
const body = `<title>하데스2 빌드 길잡이</title>
<style>
${css}
</style>
<div id="app"></div>
<div id="toast" hidden></div>
<script type="application/json" id="h2-data">${JSON.stringify(data).replace(/<\//g, '<\\/')}</script>
<script>
${weights}
</script>
<script>
${engine}
</script>
<script>
${js}
</script>
`;

fs.writeFileSync(path.join(ROOT, 'app', 'index.html'), body, 'utf8');

// docs/index.html - 단독으로 열리는 완전한 문서.
// GitHub Pages(main 브랜치 /docs)로 서비스되고 로컬 미리보기도 이 파일을 쓴다.
// app/index.html은 Artifact 규약상 <html>/<body>가 없어 브라우저에서 단독으로 열리지 않는다.
const full = `<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#0f1116">
<meta name="description" content="하데스 2 초보용 빌드 추천 - 무기·신·은혜·망치를 고르면 지금 빌드에 맞는 우선순위를 알려줍니다">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><text y='27' font-size='27'>%F0%9F%8C%99</text></svg>">
<style>html,body{margin:0;padding:0;background:#0f1116}img{max-width:100%}[hidden]{display:none!important}</style>
</head><body>
${body}
</body></html>`;
const docsDir = path.join(ROOT, 'docs');
if (!fs.existsSync(docsDir)) fs.mkdirSync(docsDir);
fs.writeFileSync(path.join(docsDir, 'index.html'), full, 'utf8');
fs.writeFileSync(path.join(docsDir, '.nojekyll'), '', 'utf8');  // Jekyll 처리 건너뛰기

const kb = (s) => (Buffer.byteLength(s, 'utf8') / 1024).toFixed(0) + 'KB';
console.log(`app/index.html (Artifact용) ${kb(body)} · docs/index.html (단독·Pages용) ${kb(full)}  빌드 ${stamp}`);
console.log(`  데이터 ${kb(JSON.stringify(data))} / 엔진 ${kb(weights + engine)} / UI ${kb(css + js)}`);
console.log(`  항목 수: 은혜 ${data.boons.length} · 융합·전설 ${data.duos.length} · 망치 ${data.hammers.length} · 기념품 ${data.keepsakes.length}`);
