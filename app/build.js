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

const stamp = new Date().toISOString().slice(0, 16).replace('T', ' ');
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

// 로컬 검증용 래퍼 (배포에는 쓰지 않음)
fs.writeFileSync(path.join(ROOT, 'app', 'preview.html'),
  `<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>html,body{margin:0;padding:0}img{max-width:100%}[hidden]{display:none!important}</style>
</head><body>\n${body}\n</body></html>`, 'utf8');

const kb = (s) => (Buffer.byteLength(s, 'utf8') / 1024).toFixed(0) + 'KB';
console.log(`app/index.html 생성: ${kb(body)}  (빌드 ${stamp})`);
console.log(`  데이터 ${kb(JSON.stringify(data))} / 엔진 ${kb(weights + engine)} / UI ${kb(css + js)}`);
console.log(`  항목 수: 은혜 ${data.boons.length} · 융합·전설 ${data.duos.length} · 망치 ${data.hammers.length} · 기념품 ${data.keepsakes.length}`);
