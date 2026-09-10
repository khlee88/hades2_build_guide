const {createEngine}=require('../recommend');const W=require('../weights');
const fs=require('fs'),p=require('path');const L=n=>JSON.parse(fs.readFileSync(p.join(__dirname,'..','..','data',n),'utf8'));
const data={boons:L('boons.json'),duos:L('duo_legendary.json'),hammers:L('hammers.json'),weapons:L('weapons.json'),arcana:L('arcana.json'),keepsakes:L('keepsakes.json'),hexes:L('hexes.json'),builds:L('build_directions.json'),gods:L('gods.json')};
const E=createEngine(data,W);
const N=id=>{for(const k of ['boons','duos','hammers']){const f=data[k].find(x=>x.id===id);if(f)return f.name_ko;}return id;};
const S=o=>Object.assign({region:1,hp_state:'mid',boons:[],hammers:[],gods_seen:[],keepsake:null,hex:null,direction_lock:null},o);
const show=(t,rows)=>{console.log('\n### '+t);for(const r of rows)console.log(`  ${r.rank} ${N(r.id).padEnd(10)} ${String(r.score).padStart(6)}  ${r.reason}${r.warnings.length?'  ⚠'+r.warnings.join(' / '):''}  ${JSON.stringify(r.breakdown)}`);};
// P1 지팡이 중반, 헤라 패시브 3개
show('P1 지팡이 2지역 헤라 패시브',E.recommendBoons(S({weapon:'staff',aspect:'staff_melinoe',region:2,boons:['hera_sworn_strike','poseidon_flood_gain','apollo_blinding_rush'],gods_seen:['hera','poseidon','apollo']}),['hera_fine_line','hera_extended_family','hera_dying_wish']));
// P2 망치: 십자 대격변 vs 고속 강타 동시 제시
show('P2 지팡이 망치 상충 예고',E.recommendHammers(S({weapon:'staff',aspect:'staff_melinoe',boons:['hera_sworn_strike'],gods_seen:['hera']}),['staff_cross_cataclysm','staff_rapid_thrasher','staff_dual_moonshot']));
// P3 신 선택에 헤르메스
show('P3 신 선택 헤르메스 vs 제우스 vs 셀레네',E.recommendGods(S({weapon:'blades',aspect:'blades_melinoe',region:2,boons:['hestia_flame_strike','hestia_cardio_gain'],gods_seen:['hestia']}),['hermes','zeus','selene']));
// P4 전설 조건 미충족/충족
show('P4 전설 미충족',E.recommendBoons(S({weapon:'staff',boons:['zeus_heaven_strike'],gods_seen:['zeus']}),['zeus_shocking_loss','zeus_double_strike']));
show('P4b 전설 충족',E.recommendBoons(S({weapon:'staff',boons:['zeus_heaven_strike','zeus_static_shock','zeus_arc_flash'],gods_seen:['zeus']}),[{id:'zeus_shocking_loss',rarity:'legendary'},'zeus_double_strike']));
// P5 도끼 4지역 슬롯 다 찬 상태에서 2순위 교체 제안
show('P5 도끼 4지역 교체 제안',E.recommendBoons(S({weapon:'axe',aspect:'axe_melinoe',region:4,boons:['hera_sworn_strike','hephaestus_volcanic_flourish','hephaestus_tough_gain','apollo_blinding_rush','hera_engagement_ring','hephaestus_security_system'],gods_seen:['hera','hephaestus','apollo']}),['apollo_nova_strike','apollo_back_burner','apollo_light_smite']));
// P6 첫 신 헤파이스토스로 쌍검 (first_god_map 1개)
show('P6 쌍검 첫 신 헤파 은혜',E.recommendBoons(S({weapon:'blades',aspect:'blades_melinoe',gods_seen:['hephaestus']}),['hephaestus_volcanic_strike','hephaestus_tough_gain','hephaestus_security_system']));
console.log('\n### 방향(P6)',E.directionScores(S({weapon:'blades',aspect:'blades_melinoe',gods_seen:['hephaestus']})).map(d=>`${d.name_ko}:${d.weight}`).join(' '));
