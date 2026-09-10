// engine/weights.js — DESIGN.md의 모든 숫자를 이름 붙인 상수로 분리.
// 2-C 튜닝은 이 파일만 고치고 test.js를 다시 돌린다.

const WEIGHTS = {
  // ── §2 방향 적합도 F_d ────────────────────────────────
  F: {
    BASE: 1,                              // 모든 방향의 기본값 (초반엔 전부 열림)
    CORE_SLOT_FILLED: [3, 2.5, 2, 1.5],   // 핵심 칸이 slot_prefs 은혜로 채워짐 (순위별, 4위 이하 마지막 값)
    OTHER_SLOT_FILLED: [1.5, 1.2, 1, 0.8],// 비핵심 칸
    SUPPORT_OWNED: 1.5,
    HAMMER_OWNED: 2,
    REQUIRES_HAMMER_OWNED: 4,
    AVOID_OWNED: -2,
    ASPECT_MATCH: 2,
    FIRST_GOD: [3, 1.5, 0.5],             // first_god_map 순위별, 3위 이하 마지막 값
    DIFFICULTY_PENALTY: -0.5,             // × (difficulty - 1)
  },

  // ── §2 수렴 단계 ─────────────────────────────────────
  CONVERGE: {
    STAGE_B_MIN_SLOTS: 2,   // 점유 은혜 2개부터 상위 N개만
    STAGE_B_KEEP: 3,
    STAGE_C_MIN_SLOTS: 4,   // 4개부터 메인·보험 2개
    STAGE_C_KEEP: 2,
    LOCK_MAIN: 0.7,         // direction_lock 시 고정 방향 가중치
    LOCK_BACKUP: 0.3,
  },

  // ── §3-2 방향 의존 항 ────────────────────────────────
  BOON: {
    SLOT_PREF: [10, 8, 6, 5],   // 칸 선호 순위별 (4위 이하 마지막 값)
    CORE_SLOT_OTHER: 2,         // 핵심 칸이지만 선호 목록에 없는 신
    NON_CORE_SLOT: 3,           // 비핵심 칸 채움
    REPLACE_COST: 2,            // 교체 시 고정 비용
    DUO_LOSS_TARGET: -4,        // 교체로 목표 융합의 유일 조건이 깨짐
    DUO_LOSS_OTHER: -2,
    SUPPORT: [7, 6, 5, 4],      // 칸 미점유 보조 순위별
    AVOID: -8,
    NEUTRAL: 1,                 // 방향과 무관한 칸 미점유 은혜
  },

  // ── §3-3 방향 무관 항 ────────────────────────────────
  FLAT: {
    ALWAYS_TAKE: 7.5,           // 2-C: 9→7.5. 핵심 칸 1·2순위(10/8+1)보다 아래, 3순위(6)·비핵심 칸(3)보다 위
    SURVIVAL_PASSIVE: [4, 3.5, 3, 2.5],
    SURVIVAL_SLOT: 2,
    MAGICK_RULE_REGION1: 2,
    MAGICK_RULE_REGION2: 5,
    DUO_PROGRESS_TARGET: 1.5,   // 2-C: 2→1.5. 탐색 단계엔 3방향 목표 융합 ~10개가 전부 대상이라 부풀려짐
    DUO_PROGRESS_OTHER: 1,
    DUO_PROGRESS_CAP: 4,        // 2-C: 6→4. 진전은 힌트, 빈 핵심 칸 채우기(5~10)를 넘어서면 안 됨
    DUO_COMPLETE_TARGET: 5,
    DUO_COMPLETE_OTHER: 2,
    DUO_CANDIDATE: 12,
    DUO_TIER: { S: 4, A: 2, B: 0, '?': 0 },
    LEGENDARY_CANDIDATE: 11,
    RARITY: { common: 0, rare: 1, epic: 2, heroic: 3 },
    POOL_SEEN: 0,               // 2-C: 은혜 단계 신 풀 항 OFF — 이미 그 신의 문을 고른 뒤. 신 선택(GOD.*)에서만 적용
    POOL_NEW_PENALTY: 0,
    BEGINNER_SAFE: 1,
  },

  // ── §4 신 후보 ───────────────────────────────────────
  GOD: {
    TOP_N: 3,                   // 상위 N개 은혜 점수의 평균
    DUO_PARTNER: 4,
    DUO_PARTNER_CAP: 8,
    POOL_SEEN: 2,
    POOL_NEW_PENALTY: -4,
    FIRST_EASY_DIRECTION: 2,    // 첫 신이고 1위 방향 난이도 1
    FIRST_MULTI_DIRECTION: 1,   // 첫 신이고 열리는 방향 2개 이상
    KEEPSAKE_MATCH: 1,
    SELENE_NO_HEX: 8,
    SELENE_HAS_HEX: 3,
    CHAOS: 2,
  },

  // ── §5 신 풀 ─────────────────────────────────────────
  GOD_POOL_CAP: 4,              // 미확인. ISSUES.md [P2] 참조. 5번째 신이 정상 등장하면 5로 올릴 것

  // ── §6 망치 ──────────────────────────────────────────
  HAMMER: {
    FIT: [10, 8, 6, 5, 4],      // 방향 hammers 순위별 (5위 이하 마지막 값)
    NOT_LISTED: 1,
    DIRECTION_UNLOCK: 6,
    AFFECTS_MATCH: 2,
    BEGINNER_PRIORITY: { 1: 3, 2: 1, 3: 0, 0: -3 },
    BLOCKS_FUTURE: -1,          // 메인 방향 순위에 있는 미보유 망치를 막음
  },

  // ── 기타 ─────────────────────────────────────────────
  SURVIVAL_TAGS: ['armor', 'heal', 'max_hp'],
  NON_POOL_GODS: ['hermes', 'artemis', 'selene', 'chaos'],
  CORE_SLOTS: ['attack', 'special', 'cast', 'sprint', 'magick'],
  SLOT_KO: { attack: '일반 공격', special: '기술', cast: '마법', sprint: '질주', magick: '마력' },
  SCORE_PRECISION: 1,
};

if (typeof module !== 'undefined' && module.exports) module.exports = WEIGHTS;
if (typeof window !== 'undefined') window.HADES_WEIGHTS = WEIGHTS;
