// Tunable prototype values. Every number here is a [建議] / [待確認] default from 開發規格包 v0.2,
// kept in one place so it can change without touching system code.

export const GameConfig = {
  schemaVersion: 1,

  time: {
    normalMinutesPerSecond: 1, // A1.2 [建議]
    fastMinutesPerSecond: 4, // A1.2 [建議]
    startDay: 0,
    startMinuteOfDay: 8 * 60, // 08:00 [待確認]
    wakeMinuteOfDay: 6 * 60, // sleep advances to 06:00 next day [待確認]
    // Day rollover happens at midnight (PRD 4.2-8).
  },

  needs: {
    initial: { stamina: 80, satiety: 80, mood: 70 }, // A2.2 [建議]
    warnBelow: 30,
    /** Change per game hour while awake [待確認]. */
    perHour: { stamina: -2, satiety: -4, mood: -1 },
    lowSatietyMoodPenaltyPerHour: -2, // applies when satiety < warnBelow [建議]
    sleepStaminaPerHour: 12,
  },

  economy: {
    startingMoney: 200, // [待確認]
  },

  job: {
    performanceMin: 0.5, // A3.2 [建議]
    performanceMax: 1.5,
    attendanceMultiplier: 1.0,
    /** Low stamina reduces performance multiplier by this factor [建議]. */
    lowStaminaPenalty: 0.8,
    /** Missed shift = no pay, no make-up [文件E-3 原型預設，待確認]. */
    allowMakeUpShift: false,
  },

  rhythm: {
    cueCount: 16,
    cueIntervalMs: 700,
    travelMs: 1600, // time a cue takes to reach the hit zone
    perfectWindowMs: 90,
    goodWindowMs: 180,
    perfectScore: 1,
    goodScore: 0.6,
  },

  relationship: {
    /** A5.1 thresholds [建議]. */
    stageThresholds: { acquaintance: 20, close: 50, partnerEligible: 75 },
    talkAffection: 3,
    talkCooldownMinutes: 120,
    giftAffection: 8,
  },

  movement: {
    tileSize: 16,
    tilesPerSecond: 4,
    /** Game minutes consumed per tile walked come from the clock running; no extra cost. */
  },

  save: {
    autosaveEveryGameMinutes: 60,
    dbName: "pixel-life",
    slotId: "slot1",
  },
} as const;
