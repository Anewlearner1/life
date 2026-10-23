import { describe, expect, it } from "vitest";
import { GameConfig } from "../game/GameConfig";
import { createChart, judge, scoreRun } from "../systems/RhythmGame";

const { perfectWindowMs: P, goodWindowMs: G } = GameConfig.rhythm;

describe("RhythmGame", () => {
  it("judge windows are inclusive and symmetric", () => {
    expect(judge(1000, 1000)).toBe("perfect");
    expect(judge(1000, 1000 + P)).toBe("perfect");
    expect(judge(1000, 1000 - P)).toBe("perfect");
    expect(judge(1000, 1000 + P + 1)).toBe("good");
    expect(judge(1000, 1000 - G)).toBe("good");
    expect(judge(1000, 1000 + G + 1)).toBe("miss");
  });

  it("scoreRun is 0-1", () => {
    expect(scoreRun([])).toBe(0);
    expect(scoreRun(["perfect", "perfect"])).toBe(1);
    expect(scoreRun(["miss", "miss"])).toBe(0);
    expect(scoreRun(["perfect", "good", "miss", "miss"])).toBeCloseTo((1 + GameConfig.rhythm.goodScore) / 4);
  });

  it("charts are deterministic, ordered and sized by config", () => {
    const a = createChart(42), b = createChart(42);
    expect(a).toEqual(b);
    expect(a).toHaveLength(GameConfig.rhythm.cueCount);
    expect(a[0].timeMs).toBe(GameConfig.rhythm.travelMs);
    for (let i = 1; i < a.length; i++) expect(a[i].timeMs - a[i - 1].timeMs).toBeGreaterThanOrEqual(GameConfig.rhythm.cueIntervalMs);
    expect(createChart(1, { ...GameConfig.rhythm, cueCount: 3 })).toHaveLength(3);
  });
});
