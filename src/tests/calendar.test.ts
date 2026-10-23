import { describe, expect, it } from "vitest";
import { GameConfig } from "../game/GameConfig";
import { ageYears, childAge, dayOfSeason, formatDate, lifeStage, minutesPerYear, playerAge, seasonOf, yearOf } from "../systems/CalendarSystem";
import { staminaCap, applyNeedDelta } from "../systems/NeedsSystem";
import { newGame } from "./fixtures";

const DAY = 1440;
const YEAR_MIN = minutesPerYear();

describe("CalendarSystem", () => {
  it("season boundaries (7 days per season)", () => {
    expect([0, 6].map(seasonOf)).toEqual(["spring", "spring"]);
    expect([7, 13].map(seasonOf)).toEqual(["summer", "summer"]);
    expect([14, 20].map(seasonOf)).toEqual(["autumn", "autumn"]);
    expect([21, 27].map(seasonOf)).toEqual(["winter", "winter"]);
  });

  it("year rolls over after 28 days", () => {
    expect(seasonOf(28)).toBe("spring");
    expect(seasonOf(28 + 21)).toBe("winter");
    expect(yearOf(0)).toBe(1);
    expect(yearOf(27)).toBe(1);
    expect(yearOf(28)).toBe(2);
    expect(yearOf(56)).toBe(3);
    expect(dayOfSeason(0)).toBe(1);
    expect(dayOfSeason(6)).toBe(7);
    expect(dayOfSeason(7)).toBe(1);
    expect(dayOfSeason(28)).toBe(1);
  });

  it("formatDate", () => {
    expect(formatDate(2 * DAY + 100)).toBe("第1年 春 第3天");
    expect(formatDate(7 * DAY)).toBe("第1年 夏 第1天");
    expect(formatDate(28 * DAY + 21 * DAY + 6 * DAY)).toBe("第2年 冬 第7天");
  });

  it("ageYears, multiplier and lifeStage thresholds", () => {
    expect(YEAR_MIN).toBe(28 * DAY);
    expect(ageYears(0, YEAR_MIN)).toBeCloseTo(1);
    expect(ageYears(0, YEAR_MIN / 2)).toBeCloseTo(0.5);
    expect(ageYears(0, YEAR_MIN, 6)).toBeCloseTo(6);
    const s = GameConfig.calendar.stages;
    expect(lifeStage(0)).toBe("baby");
    expect(lifeStage(s.child - 0.01)).toBe("baby");
    expect(lifeStage(s.child)).toBe("child");
    expect(lifeStage(s.teen)).toBe("teen");
    expect(lifeStage(s.adult)).toBe("adult");
    expect(lifeStage(s.elder - 0.01)).toBe("adult");
    expect(lifeStage(s.elder)).toBe("elder");
  });

  it("playerAge starts at playerStartAge and grows with the clock", () => {
    const s = newGame();
    expect(playerAge(s)).toBeCloseTo(GameConfig.calendar.playerStartAge);
    s.gameClock.totalMinutes += YEAR_MIN;
    expect(playerAge(s)).toBeCloseTo(GameConfig.calendar.playerStartAge + 1);
  });

  it("children age childAgingMultiplier times faster", () => {
    const now = 100 * DAY;
    const child = { id: "child_1", name: "x", birthMinute: now - YEAR_MIN, appearance: newGame().player.appearance };
    expect(childAge(child, now)).toBeCloseTo(GameConfig.calendar.childAgingMultiplier);
    expect(childAge(child, now)).toBeCloseTo(6 * ageYears(child.birthMinute, now));
  });

  it("elders have a stamina cap", () => {
    const s = newGame();
    expect(staminaCap(s)).toBe(100);
    applyNeedDelta(s, { stamina: 100 });
    expect(s.player.needs.stamina).toBe(100);
    s.player.birthMinute = s.gameClock.totalMinutes - 61 * YEAR_MIN;
    expect(staminaCap(s)).toBe(GameConfig.calendar.elderStaminaCap);
    applyNeedDelta(s, { stamina: 100 });
    expect(s.player.needs.stamina).toBe(GameConfig.calendar.elderStaminaCap);
    applyNeedDelta(s, { mood: -1 });
    expect(s.player.needs.stamina).toBe(GameConfig.calendar.elderStaminaCap);
  });
});
