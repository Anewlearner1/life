import { describe, expect, it } from "vitest";
import { GameConfig } from "../game/GameConfig";
import { advanceGameTime, clockParts, formatClock, realMsToGameMinutes, setMode } from "../systems/TimeSystem";
import { makeContent, newGame } from "./fixtures";

const DAY = 1440;

describe("TimeSystem", () => {
  it("paused mode advances nothing", () => {
    const c = makeContent(), s = newGame(c);
    setMode(s, "paused");
    const before = JSON.stringify(s);
    const r = advanceGameTime(s, c, realMsToGameMinutes(s.gameClock.mode, 60_000));
    expect(realMsToGameMinutes("paused", 60_000)).toBe(0);
    expect(r.dayChanged).toBe(false);
    expect(JSON.stringify(s)).toBe(before);
  });

  it("fast is 4x normal", () => {
    expect(realMsToGameMinutes("normal", 1000)).toBe(GameConfig.time.normalMinutesPerSecond);
    expect(realMsToGameMinutes("fast", 1000)).toBe(4 * realMsToGameMinutes("normal", 1000));
    expect(realMsToGameMinutes("fast", 500)).toBe(2);
  });

  it("clockParts and formatClock", () => {
    expect(clockParts(0)).toEqual({ day: 0, hour: 0, minute: 0, minuteOfDay: 0, weekday: 0 });
    expect(clockParts(8 * 60 + 5)).toMatchObject({ hour: 8, minute: 5, minuteOfDay: 485 });
    expect(clockParts(8 * DAY + 61)).toMatchObject({ day: 8, weekday: 1, hour: 1, minute: 1 });
    expect(formatClock(GameConfig.time.startMinuteOfDay)).toBe("第1天 08:00");
    expect(formatClock(DAY + 9 * 60 + 5)).toBe("第2天 09:05");
  });

  it("new game starts at the configured time", () => {
    expect(newGame().gameClock.totalMinutes).toBe(GameConfig.time.startMinuteOfDay);
  });

  it("applies hourly needs once per crossed hour boundary", () => {
    const c = makeContent(), s = newGame(c);
    const start = s.player.needs.stamina;
    advanceGameTime(s, c, 90); // 08:00 -> 09:30: crosses 09:00 only
    expect(s.player.needs.stamina).toBe(start + GameConfig.needs.perHour.stamina);
    advanceGameTime(s, c, 30); // -> 10:00: crosses 10:00
    expect(s.player.needs.stamina).toBe(start + 2 * GameConfig.needs.perHour.stamina);
    advanceGameTime(s, c, 59); // 10:59: no boundary
    expect(s.player.needs.stamina).toBe(start + 2 * GameConfig.needs.perHour.stamina);
  });

  it("crossing midnight increments the day once and processes dayStart once", () => {
    const c = makeContent(), s = newGame(c);
    const msgs: string[] = [];
    const fired: string[] = [];
    let changes = 0;
    for (let i = 0; i < 16 * 60 + 30; i++) { // 08:00 -> 00:30 next day in 1-minute steps
      const r = advanceGameTime(s, c, 1);
      if (r.dayChanged) changes++;
      msgs.push(...r.messages);
      fired.push(...r.firedEventIds);
    }
    expect(changes).toBe(1);
    expect(clockParts(s.gameClock.totalMinutes).day).toBe(1);
    expect(s.lastProcessedDay).toBe(1);
    expect(msgs.filter((m) => m === "第2天開始了")).toHaveLength(1);
    expect(fired).toEqual(["ev_day2"]);
    expect(s.transactions.filter((t) => t.reason === "Allowance")).toHaveLength(1);
  });

  it("processes each day once, in order, on a multi-day jump", () => {
    const c = makeContent(), s = newGame(c);
    const r = advanceGameTime(s, c, 3 * DAY);
    expect(r.messages.filter((m) => m.endsWith("天開始了"))).toEqual(["第2天開始了", "第3天開始了", "第4天開始了"]);
    expect(r.firedEventIds).toEqual(["ev_day2", "ev_day3"]);
    expect(s.lastProcessedDay).toBe(3);
    expect(r.saveRequested).toBe(true);
    expect(r.dayChanged).toBe(true);
    // advancing again within the same day does not reprocess
    expect(advanceGameTime(s, c, 10).dayChanged).toBe(false);
  });

  it("small steps and one big jump agree", () => {
    const c = makeContent(), a = newGame(c), b = newGame(c);
    advanceGameTime(a, c, 2 * DAY + 100);
    for (let i = 0; i < 2 * DAY + 100; i += 10) advanceGameTime(b, c, 10);
    expect(b).toEqual(a);
  });

  it("reports newly low needs once", () => {
    const c = makeContent(), s = newGame(c);
    s.player.needs.satiety = GameConfig.needs.warnBelow + 1;
    const r = advanceGameTime(s, c, 60);
    expect(r.needWarnings).toContain("satiety");
    expect(advanceGameTime(s, c, 60).needWarnings).not.toContain("satiety");
  });

  it("moves NPCs per schedule as time passes", () => {
    const c = makeContent(), s = newGame(c);
    expect(s.npcs["npc_001"].currentActivity).toBe("work"); // 08:00
    advanceGameTime(s, c, 10 * 60); // 18:00
    expect(s.npcs["npc_001"].currentActivity).toBe("rest");
  });
});
