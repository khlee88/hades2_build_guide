# -*- coding: utf-8 -*-
"""핵심 슬롯 5칸의 배타성을 데이터에 명시한다.

규칙 (사용자 확인):
  일반 공격 / 기술 / 마법 / 질주 / 마력 5칸에는 **신 1명의 은혜만** 장착된다.
  다른 신의 같은 슬롯 은혜를 받으면 기존 것이 교체되어 사라진다.

따라서:
  - `occupies_slot: true` 인 은혜끼리 같은 슬롯이면 서로 `conflicts` 관계다.
  - 헤르메스는 질주 슬롯 은혜가 2개(거침없는 속도/잰 발걸음)라 이 모델과 모순된다.
    → 헤르메스 은혜는 칸을 차지하지 않고 '해당 동작을 강화'만 하는 것으로 정정.
    → slot을 passive로 바꾸고 무엇을 강화하는지는 affects에 남긴다. (아르테미스도 동일)

이 스크립트는 data/boons/*.json 조각을 직접 수정하므로 여러 번 돌려도 결과가 같다.
"""
import json, io, os, glob

BASE = os.path.dirname(os.path.abspath(__file__))
CORE_SLOTS = ["attack", "special", "cast", "sprint", "magick"]
CORE_GODS = ["zeus", "hestia", "poseidon", "demeter", "apollo",
             "aphrodite", "hephaestus", "hera", "ares"]

# 1) 조각 로드
frags = {}
for p in glob.glob(os.path.join(BASE, "boons", "*.json")):
    frags[p] = json.load(io.open(p, encoding="utf-8"))

# 2) 칸을 차지하지 않는 신(헤르메스·아르테미스)의 slot을 passive로 내리고 affects로 옮김
NON_SLOT_GODS = {"hermes", "artemis"}
for p, arr in frags.items():
    for b in arr:
        if b["god"] in NON_SLOT_GODS and b["slot"] in CORE_SLOTS:
            b.setdefault("affects", [])
            if b["slot"] not in b["affects"]:
                b["affects"].append(b["slot"])
            b["slot"] = "passive"

# 3) occupies_slot 플래그 부여
for p, arr in frags.items():
    for b in arr:
        b["occupies_slot"] = (b["god"] in CORE_GODS and b["slot"] in CORE_SLOTS)

# 4) 슬롯별 점유 은혜 목록 → conflicts 생성
by_slot = {s: [] for s in CORE_SLOTS}
for arr in frags.values():
    for b in arr:
        if b["occupies_slot"]:
            by_slot[b["slot"]].append(b["id"])
for s in CORE_SLOTS:
    by_slot[s].sort()

all_occupying = {i for s in CORE_SLOTS for i in by_slot[s]}
for p, arr in frags.items():
    for b in arr:
        if b["occupies_slot"]:
            # 수동으로 넣은 상충(마법 변형 계열 등)은 보존, 슬롯 유래 상충은 재생성
            manual = [c for c in b.get("conflicts", []) if c not in all_occupying]
            derived = [i for i in by_slot[b["slot"]] if i != b["id"]]
            b["conflicts"] = sorted(set(manual + derived))
            b.setdefault("conflict_reason", "슬롯 배타 - 같은 칸에는 신 1명만 장착 가능")
        else:
            # 칸 미점유 은혜의 conflicts는 전부 수동(마법 변형 계열 등)이므로 그대로 둔다
            if "conflicts" in b and not b["conflicts"]:
                b.pop("conflicts"); b.pop("conflict_reason", None)

# 5) 키 순서를 보기 좋게 정렬해 저장
ORDER = ["id", "god", "name_ko", "name_en", "slot", "occupies_slot", "affects",
         "effect", "rarity_scaling", "infusion_req", "tags", "prereq",
         "conflicts", "conflict_reason", "weapon_affinity", "verified", "source", "notes"]
def reorder(b):
    out = {k: b[k] for k in ORDER if k in b}
    for k in b:
        if k not in out:
            out[k] = b[k]
    return out

for p, arr in frags.items():
    io.open(p, "w", encoding="utf-8").write(
        json.dumps([reorder(b) for b in arr], ensure_ascii=False, indent=1))

print("슬롯 배타 관계 생성 완료")
for s in CORE_SLOTS:
    print("  %-8s %d개 -> 각 은혜가 나머지 %d개와 상충" % (s, len(by_slot[s]), len(by_slot[s]) - 1))
moved = sum(1 for arr in frags.values() for b in arr
            if b["god"] in NON_SLOT_GODS and b.get("affects"))
print("  칸 미점유로 정정된 헤르메스·아르테미스 은혜: %d개" % moved)
