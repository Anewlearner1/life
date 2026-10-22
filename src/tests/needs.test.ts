import { describe, expect, it } from "vitest";
import { GameConfig } from "../game/GameConfig";
import { applyHourly, applyNeedDelta, clampNeed, lowNeeds } from "../systems/NeedsSystem";
import { newGame } from "./fixtures";

describe("NeedsSystem", () => {
  it("clamps to 0-100", () => {
    expect(clampNeed(-5)).toBe(0);
    expect(clampNeed(120)).toBe(100);
    expect(clampNeed(42)).toBe(42);
    const s = newGame();
    applyNeedDelta(s, { stamina: 500, mood: -500 });
    expect(s.player.needs).toMatchObject({ stamina: 100, mood: 0 });
    applyHourly(s, 100);
    expect(Object.values(s.player.needs).every((v) => v >= 0 && v <= 100)).toBe(true);
  });

  it("warns on low needs", () => {
    const s = newGame();
    expect(lowNeeds(s)).toEqual([]);
    s.player.needs.satiety = GameConfig.needs.warnBelow - 1;
    s.player.needs.mood = GameConfig.needs.warnBelow;
    expect(lowNeeds(s)).toEqual(["satiety"]);
  });

  it("hunger drains mood faster; sleeping restores stamina", () => {
    const s = newGame();
    s.player.needs.satiety = 10;
    const mood = s.player.needs.mood;
    applyHourly(s, 1);
    expect(s.player.needs.mood).toBe(mood + GameConfig.needs.perHour.mood + GameConfig.needs.lowSatietyMoodPenaltyPerHour);
    s.player.needs.stamina = 10;
    applyHourly(s, 2, true);
    expect(s.player.needs.stamina).toBe(10 + 2 * GameConfig.needs.sleepStaminaPerHour);
  });
});
