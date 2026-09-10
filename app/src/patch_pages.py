# -*- coding: utf-8 -*-
"""GitHub Pages 대응: build.js가 docs/index.html(단독 실행 가능한 완전한 문서)을 만들게 한다.
app/index.html은 Artifact 규약상 <html>/<body>가 없어 브라우저에서 단독으로 열리지 않는다.
CRLF·인코딩 문제를 피하려고 ASCII 앵커 + 줄 단위로 편집한다."""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BJ = os.path.join(ROOT, 'app', 'build.js')
src = io.open(BJ, encoding='utf-8').read()
if 'docs' in src and 'nojekyll' in src:
    print('build.js: 이미 적용됨'); sys.exit(0)

lines = src.splitlines()
start = next((i for i, l in enumerate(lines) if "'preview.html'" in l), None)
if start is None:
    print('preview.html 줄을 못 찾음'); sys.exit(1)
# 위쪽 주석 줄까지 포함
while start > 0 and lines[start - 1].lstrip().startswith('//'):
    start -= 1
end = next((i for i, l in enumerate(lines) if l.startswith('const kb =')), None)
if end is None:
    print('const kb 줄을 못 찾음'); sys.exit(1)

NEW = [
 "// docs/index.html - 단독으로 열리는 완전한 문서.",
 "// GitHub Pages(main 브랜치 /docs)로 서비스되고 로컬 미리보기도 이 파일을 쓴다.",
 "// app/index.html은 Artifact 규약상 <html>/<body>가 없어 브라우저에서 단독으로 열리지 않는다.",
 "const full = `<!doctype html><html lang=\"ko\"><head><meta charset=\"utf-8\">",
 "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">",
 "<meta name=\"theme-color\" content=\"#0f1116\">",
 "<meta name=\"description\" content=\"하데스 2 초보용 빌드 추천 - 무기·신·은혜·망치를 고르면 지금 빌드에 맞는 우선순위를 알려줍니다\">",
 "<meta name=\"mobile-web-app-capable\" content=\"yes\">",
 "<meta name=\"apple-mobile-web-app-capable\" content=\"yes\">",
 "<meta name=\"apple-mobile-web-app-status-bar-style\" content=\"black-translucent\">",
 "<link rel=\"icon\" href=\"data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><text y='27' font-size='27'>%F0%9F%8C%99</text></svg>\">",
 "<style>html,body{margin:0;padding:0;background:#0f1116}img{max-width:100%}[hidden]{display:none!important}</style>",
 "</head><body>",
 "${body}",
 "</body></html>`;",
 "const docsDir = path.join(ROOT, 'docs');",
 "if (!fs.existsSync(docsDir)) fs.mkdirSync(docsDir);",
 "fs.writeFileSync(path.join(docsDir, 'index.html'), full, 'utf8');",
 "fs.writeFileSync(path.join(docsDir, '.nojekyll'), '', 'utf8');  // Jekyll 처리 건너뛰기",
 "",
]
lines[start:end] = NEW
out = '\n'.join(lines) + '\n'
out = out.replace("console.log(`app/index.html 생성: ${kb(body)}  (빌드 ${stamp})`);",
                  "console.log(`app/index.html (Artifact용) ${kb(body)} · docs/index.html (단독·Pages용) ${kb(full)}  빌드 ${stamp}`);")
io.open(BJ, 'w', encoding='utf-8', newline='\n').write(out)
print('build.js: docs/index.html 생성으로 변경')

# .gitignore에서 preview 규칙 제거
GI = os.path.join(ROOT, '.gitignore')
g = [l for l in io.open(GI, encoding='utf-8').read().splitlines()
     if 'preview.html' not in l and '미리보기' not in l]
while g and not g[0].strip(): g.pop(0)
io.open(GI, 'w', encoding='utf-8', newline='\n').write('\n'.join(g) + '\n')
print('.gitignore: preview 규칙 제거')
