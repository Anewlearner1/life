import type { JobDefinition } from "../game/types";
import { JOB, LOC, MINIGAME } from "./ids";

// Minutes of day: 420 = 07:00, 540 = 09:00, 600 = 10:00, 720 = 12:00, 840 = 14:00, 900 = 15:00, 1080 = 18:00.
export const jobs: Record<string, JobDefinition> = {
  [JOB.barista]: {
    id: JOB.barista,
    name: "咖啡店店員",
    workplaceLocationId: LOC.cafeCounter,
    shiftRules: [
      { startMinute: 540, endMinute: 720 },
      { startMinute: 840, endMinute: 1080 },
    ],
    baseWage: 100,
    minigameId: MINIGAME.rhythmCafe,
    needDelta: { stamina: -15, satiety: -10, mood: -3 },
    durationMinutes: 180,
  },
  // Outdoor work: tiring and hungry, but the fresh air lifts the mood.
  [JOB.farmhand]: {
    id: JOB.farmhand,
    name: "農場幫手",
    workplaceLocationId: LOC.field,
    shiftRules: [
      { startMinute: 420, endMinute: 600 },
      { startMinute: 900, endMinute: 1080 },
    ],
    baseWage: 120,
    minigameId: MINIGAME.rhythmFarm,
    needDelta: { stamina: -20, satiety: -12, mood: 2 },
    durationMinutes: 180,
  },
};
