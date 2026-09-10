# -*- coding: utf-8 -*-
"""1-C 페이블 리뷰 반영 스크립트. 여러 번 실행해도 결과가 같다.

1. duo_gateway 제거 → duo_key 자동 생성 (칸 미점유 은혜 중 융합 조건에 지목된 것)
2. beginner_safe 재정의: 조건·페널티 없이 무난한 것만 남김
3. 무기 궁합 판단용 태그 추가: per_hit / pct_dmg / cooldown_burst
4. 상충(conflicts) 수동 관계 추가 — 마법 변형 계열, 잡초 박멸↔고속 망치, 강권 쌍, 용력↔죽음
5. hammers의 boon_conflicts를 conflicts로 통합
6. 융합 power_tier 초보 기준 재조정
"""
import json, io, os, glob

BASE = os.path.dirname(os.path.abspath(__file__))
def load(n): return json.load(io.open(os.path.join(BASE, n), encoding="utf-8"))
def save(n, d): io.open(os.path.join(BASE, n), "w", encoding="utf-8").write(json.dumps(d, ensure_ascii=False, indent=1))

frag_paths = sorted(glob.glob(os.path.join(BASE, "boons", "*.json")))
frags = {p: json.load(io.open(p, encoding="utf-8")) for p in frag_paths}
boons = [b for arr in frags.values() for b in arr]
bid = {b["id"]: b for b in boons}
duos = load("duo_legendary.json")
hammers = load("hammers.json")
arcana = load("arcana.json")

# ---------- 1. duo_gateway → duo_key ----------
referenced = set()
for d in duos:
    if d["kind"] != "duo": continue
    for g in d["requires"]["all"]:
        for t in g["any"]:
            if t in bid: referenced.add(t)
for b in boons:
    b["tags"] = [t for t in b["tags"] if t != "duo_gateway"]
    is_key = (not b.get("occupies_slot")) and b["id"] in referenced
    if is_key and "duo_key" not in b["tags"]: b["tags"].append("duo_key")
    if not is_key and "duo_key" in b["tags"]: b["tags"].remove("duo_key")

# ---------- 2. beginner_safe 재정의 ----------
BEGINNER_SAFE = {
    # 조건 없는 화력
    "zeus_heaven_strike","zeus_heaven_flourish","hestia_flame_strike","hestia_flame_flourish",
    "poseidon_wave_strike","poseidon_wave_flourish","demeter_ice_strike","demeter_ice_flourish",
    "apollo_nova_strike","apollo_nova_flourish","hera_sworn_strike","hera_sworn_flourish",
    "ares_vicious_strike","ares_vicious_flourish","hephaestus_volcanic_strike","hephaestus_volcanic_flourish",
    # 마력 — 조건이 가장 가벼운 것들
    "zeus_ionic_gain","hestia_cardio_gain","apollo_lucid_gain","aphrodite_glamour_gain","hephaestus_tough_gain",
    # 생존·편의
    "apollo_blinding_rush","demeter_frigid_rush","hestia_flash_fry","demeter_plentiful_forage",
    "demeter_steady_growth","hephaestus_security_system","aphrodite_spiritual_affirmation",
    "aphrodite_healthy_rebound","hera_bridal_glow",
    # 헤르메스·아르테미스 — 칸 안 차지하고 무조건 이득
    "hermes_nimble_limbs","hermes_racing_thoughts","hermes_nitro_boost","hermes_stutter_step",
    "hermes_hard_target","artemis_support_fire","artemis_pressure_points",
}
for b in boons:
    b["tags"] = [t for t in b["tags"] if t != "beginner_safe"]
    if b["id"] in BEGINNER_SAFE: b["tags"].append("beginner_safe")

# ---------- 3. 무기 궁합 태그 ----------
PER_HIT = {"zeus_static_shock","poseidon_wave_strike","poseidon_wave_flourish","hestia_flame_strike",
           "hestia_flame_flourish","hestia_cardio_gain","artemis_support_fire","ares_grisly_gain",
           "apollo_extra_dose","aphrodite_heart_breaker","hera_fine_line","zeus_power_surge"}
PCT_DMG = {"apollo_nova_strike","apollo_nova_flourish","hera_sworn_strike","hera_sworn_flourish",
           "demeter_ice_strike","demeter_ice_flourish","ares_vicious_strike","ares_vicious_flourish",
           "aphrodite_flutter_strike","aphrodite_flutter_flourish"}
COOLDOWN_BURST = {"hephaestus_volcanic_strike","hephaestus_volcanic_flourish","hephaestus_smithy_rush"}
for b in boons:
    for tag, S in (("per_hit", PER_HIT), ("pct_dmg", PCT_DMG), ("cooldown_burst", COOLDOWN_BURST)):
        if b["id"] in S and tag not in b["tags"]: b["tags"].append(tag)

# ---------- 4. 상충 관계 (수동) ----------
def add_conflict(obj, other_id, reason):
    obj.setdefault("conflicts", [])
    if other_id not in obj["conflicts"]:
        obj["conflicts"].append(other_id)
    obj.setdefault("conflict_reason", reason)

everything = {**bid, **{d["id"]: d for d in duos}, **{h["id"]: h for h in hammers}, **{a["id"]: a for a in arcana}}
def pair(a, b, reason):
    add_conflict(everything[a], b, reason); add_conflict(everything[b], a, reason)

CAST_MOD = ["zeus_lightning_lance", "hestia_glowing_coal", "demeter_local_climate"]
R = "마법 변형 계열 - 동시 채용 불가 (위키 명시)"
for i in range(len(CAST_MOD)):
    for j in range(i + 1, len(CAST_MOD)):
        pair(CAST_MOD[i], CAST_MOD[j], R)
for c in CAST_MOD + ["poseidon_tidal_ring"]:
    pair("duo_demeter_ares", c, R)                      # 위험 지대
pair("demeter_local_climate", "poseidon_tidal_ring", R)
pair("poseidon_geyser_spout", "apollo_prominence_flare", "Ω 마법 변형 - 동시 채용 불가 (위키 명시)")
pair("poseidon_geyser_spout", "ares_meat_grinder", "Ω 마법 변형 - 동시 채용 불가 (위키 명시)")

# 잡초 박멸 ↔ 고속 망치 (hammers.boon_conflicts를 conflicts로 통합)
for h in hammers:
    for bc in h.pop("boon_conflicts", []):
        pair(h["id"], bc, "공격 속도 망치와 잡초 박멸은 동시 채용 불가 (위키 명시)")
pair("duo_zeus_hera_kings_ransom", "duo_hera_zeus_queens_ransom", "서로의 은혜를 전부 파괴하는 관계")
pair("strength", "death", "용력은 죽음 저항이 있으면 효과 없음 - 함께 켜면 낭비")

# ---------- 5. 융합 power_tier 초보 기준 재조정 ----------
TIER = {
 "duo_zeus_hera_kings_ransom":"B","duo_hera_zeus_queens_ransom":"B",   # 빌드를 통째로 뒤집음 - 초보 부적합
 "duo_zeus_ares":"B","duo_hestia_ares":"B","duo_poseidon_hera":"B","duo_apollo_hera":"B",
 "duo_aphrodite_ares":"B","duo_hera_ares":"B","duo_demeter_hera":"B",
 "duo_poseidon_aphrodite":"S","duo_hera_hephaestus":"S","duo_demeter_apollo":"S",
}
for d in duos:
    if d["id"] in TIER: d["power_tier"] = TIER[d["id"]]

# ---------- 저장 ----------
for p, arr in frags.items():
    io.open(p, "w", encoding="utf-8").write(json.dumps(arr, ensure_ascii=False, indent=1))
save("duo_legendary.json", duos); save("hammers.json", hammers); save("arcana.json", arcana)

print("duo_key:", sorted(b["id"] for b in boons if "duo_key" in b["tags"]))
print("beginner_safe:", sum(1 for b in boons if "beginner_safe" in b["tags"]), "개")
print("per_hit/pct_dmg/cooldown_burst:", *(sum(1 for b in boons if t in b["tags"]) for t in ("per_hit","pct_dmg","cooldown_burst")))
print("수동 상충 추가 완료")
