// data/boons/*.json 조각을 data/boons.json 하나로 병합
const fs = require('fs');
const path = require('path');

const dir = path.join(__dirname, 'boons');
const order = ['zeus', 'hestia', 'poseidon', 'demeter', 'apollo', 'aphrodite', 'hephaestus', 'hera', 'ares', 'hermes', 'artemis'];
const out = [];

for (const god of order) {
  const f = path.join(dir, god + '.json');
  if (!fs.existsSync(f)) { console.warn('누락:', god); continue; }
  const arr = JSON.parse(fs.readFileSync(f, 'utf8'));
  out.push(...arr);
  console.log(`${god}: ${arr.length}개`);
}

fs.writeFileSync(path.join(__dirname, 'boons.json'), JSON.stringify(out, null, 1), 'utf8');
console.log('총', out.length, '개 -> data/boons.json');
