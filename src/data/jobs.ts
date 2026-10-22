import type { JobDefinition } from "../game/types";
import { JOB, LOC, MINIGAME } from "./ids";

// Minutes of day: 540 = 09:00, 720 = 12:00, 840 = 14:00, 1080 = 18:00.
export const jobs: Record<string, JobDefinition> = {
  [JOB.barista]: {
    id: JOB.barista,
    name: "咖啡店店員",
    workplaceLocationId: LOC.cafe,
    shiftRules: [
      { startMinute: 540, endMinute: 720 },
      { startMinute: 840, endMinute: 1080 },
    ],
    baseWage: 100,
    minigameId: MINIGAME.rhythmCafe,
    needDelta: { stamina: -15, satiety: -10, mood: -3 },
    durationMinutes: 180,
  },
};
