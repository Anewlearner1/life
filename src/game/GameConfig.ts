// Tunable prototype values. Every number here is a [建議] / [待確認] default from 開發規格包 v0.2,
// kept in one place so it can change without touching system code.

const rhythm = {
  cueCount: 16,
  cueIntervalMs: 700,
  travelMs: 1600, // time a cue takes to reach the hit zone
  perfectWindowMs: 90,
  goodWindowMs: 180,
  perfectScore: 1,
  goodScore: 0.6,
} as const;

/** Per-minigame rhythm setup (chart tempo, seed salt and look); keyed by JobDefinition.minigameId. */
export type MinigameConfig = {
  /** Scene title; defaults to `${job.name}　節奏挑戰`. */
  title?: string;
  rhythm: { [K in keyof typeof rhythm]: number };
  /** Added to the controller's seed so each minigame plays a different chart. */
  seedOffset: number;
  background: number;
  trackTexture: string;
  /** Cue sprites, used in order (cue i uses entry i % length). */
  cueTextures: string[];
  /** Multiply-tints for the hit zone (omit for the original colours). */
  hitZoneTint?: number;
  /** Wide-screen decoration: texture, side of the lane (-1 left / 1 right), offset above the hit zone, scale. */
  decor: { key: string; side: -1 | 1; dy: number; scale: number }[];
};

export const GameConfig = {
  schemaVersion: 2,

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

  rhythm,

  minigames: {
    mg_rhythm_cafe: {
      rhythm,
      seedOffset: 0,
      background: 0x181425,
      trackTexture: "MINI_003_Track",
      cueTextures: ["MINI_002_RhythmCue_Tap"],
      decor: [
        { key: "MINI_006_EspressoMachine", side: -1, dy: 40, scale: 4 },
        { key: "MINI_006_Cup", side: 1, dy: 20, scale: 5 },
      ],
    },
    mg_rhythm_farm: {
      title: "農場幫手　收成挑戰",
      rhythm: { ...rhythm, cueCount: 18, cueIntervalMs: 620, travelMs: 1500 },
      seedOffset: 104729,
      background: 0x1d2a1b,
      trackTexture: "MINI_003_Track_Farm",
      cueTextures: ["MINI_002_RhythmCue_Crop_Carrot", "MINI_002_RhythmCue_Crop_Cabbage", "MINI_002_RhythmCue_Crop_Pumpkin"],
      hitZoneTint: 0xc8e890,
      decor: [
        { key: "prop_scarecrow", side: -1, dy: 60, scale: 4 },
        { key: "prop_pumpkin", side: 1, dy: 20, scale: 5 },
      ],
    },
  } as Record<string, MinigameConfig>,

  /** Calendar & aging (PRD P-18 future systems; all [建議], tune freely). */
  calendar: {
    daysPerSeason: 7, // 4 seasons → 28-day year
    seasons: ["spring", "summer", "autumn", "winter"] as const,
    playerStartAge: 22,
    /** Children age this many times faster than adults so a generation fits in play time. */
    childAgingMultiplier: 6,
    /** Age thresholds (years) for LifeStage. */
    stages: { child: 3, teen: 12, adult: 18, elder: 60 },
    /** Elders have a lower stamina cap. */
    elderStaminaCap: 70,
  },

  weather: {
    /** Daily weather odds per season (must sum to 1). */
    odds: {
      spring: { sunny: 0.5, cloudy: 0.3, rain: 0.2, snow: 0 },
      summer: { sunny: 0.6, cloudy: 0.2, rain: 0.2, snow: 0 },
      autumn: { sunny: 0.4, cloudy: 0.35, rain: 0.25, snow: 0 },
      winter: { sunny: 0.3, cloudy: 0.3, rain: 0.1, snow: 0.3 },
    },
    /** Mood change per game hour spent outdoors in rain/snow. */
    badWeatherMoodPerHour: -1,
    /** Farm shifts are closed on snow days. */
    farmClosedOnSnow: true,
  },

  family: {
    ringItemId: "item_ring",
    /** Partner for at least this many days and affection ≥ proposeAffection before proposing. */
    minPartnerDays: 3,
    proposeAffection: 90,
    pregnancyDays: 7,
    maxChildren: 3,
    /** Heir must be at least this old (years) to take over the household. */
    successionAge: 18,
    /** Money the heir keeps (fraction). */
    inheritanceRate: 1,
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
