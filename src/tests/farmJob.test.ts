import { describe, expect, it } from "vitest";
import { content } from "../data";
import { JOB, LOC, MAP, MINIGAME } from "../data/ids";
import { GameConfig } from "../game/GameConfig";
import { checkCondition } from "../systems/EventSystem";
import { canStartWork, completeWork, nextShift, performanceFromScore, shiftAt } from "../systems/JobSystem";
import { findPath } from "../systems/Pathfinding";
import { createChart } from "../systems/RhythmGame";
import { advanceGameTime } from "../systems/TimeSystem";
import { buildCollisionGrid } from "../scenes/collision";
import { newGame, standAt } from "./fixtures";

const H = 60;
const DAY = 1440;
const job = content.jobs[JOB.farmhand];
const barista = content.jobs[JOB.barista];

describe("farmhand job data", () => {
  it("is defined at loc_field with the agreed pay and costs", () => {
    expect(job).toMatchObject({ workplaceLocationId: LOC.field, baseWage: 120, minigameId: MINIGAME.rhythmFarm, durationMinutes: 180 });
    expect(job.needDelta).toEqual({ stamina: -20, satiety: -12, mood: 2 });
    expect(content.locations[LOC.field]).toMatchObject({ type: "workplace", mapId: MAP.rural });
    expect(content.maps[MAP.rural].locationIds).toContain(LOC.field);
  });

  it("has a minigame config for every job; farm differs from cafe, cafe keeps the original chart", () => {
    for (const j of Object.values(content.jobs)) expect(GameConfig.minigames[j.minigameId], j.id).toBeDefined();
    const cafe = GameConfig.minigames[MINIGAME.rhythmCafe];
    const farm = GameConfig.minigames[MINIGAME.rhythmFarm];
    expect(cafe.rhythm).toBe(GameConfig.rhythm);
    expect(cafe.seedOffset).toBe(0);
    expect(createChart(5, cafe.rhythm)).toEqual(createChart(5));
    expect(farm.title).toBe("農場幫手　收成挑戰");
    expect(farm.cueTextures).toHaveLength(3);
    expect(createChart(5 + farm.seedOffset, farm.rhythm)).not.toEqual(createChart(5));
    expect(farm.rhythm.cueIntervalMs).not.toBe(cafe.rhythm.cueIntervalMs);
  });
});

describe("farmhand shifts", () => {
  it("runs 07:00-10:00 and 15:00-18:00 every day (end exclusive)", () => {
    expect(shiftAt(job, 6 * H + 59)).toBeNull();
    expect(shiftAt(job, 7 * H)).toEqual({ start: 7 * H, end: 10 * H });
    expect(shiftAt(job, 10 * H - 1)).not.toBeNull();
    expect(shiftAt(job, 10 * H)).toBeNull();
    expect(shiftAt(job, 12 * H)).toBeNull();
    expect(shiftAt(job, 15 * H)).toEqual({ start: 15 * H, end: 18 * H });
    expect(shiftAt(job, 18 * H)).toBeNull();
    expect(shiftAt(job, 3 * DAY + 16 * H)).toEqual({ start: 3 * DAY + 15 * H, end: 3 * DAY + 18 * H });
  });

  it("overlaps the cafe shifts in time (one place at a time) and nextShift skips the gap", () => {
    expect(shiftAt(barista, 9 * H + 30)).not.toBeNull();
    expect(shiftAt(job, 9 * H + 30)).not.toBeNull();
    expect(nextShift(job, 10 * H).start).toBe(15 * H);
    expect(nextShift(job, 18 * H).start).toBe(DAY + 7 * H);
  });
});

describe("farmhand work", () => {
  it("canStartWork only inside a shift and only at loc_field", () => {
    const s = newGame(content);
    s.gameClock.totalMinutes = 6 * H; // 06:00
    standAt(s, content, LOC.field);
    expect(canStartWork(s, content, JOB.farmhand)).toMatchObject({ ok: false, reason: "不在班表時段" });
    advanceGameTime(s, content, H); // 07:00
    standAt(s, content, LOC.cafeCounter);
    expect(canStartWork(s, content, JOB.farmhand)).toMatchObject({ ok: false, reason: "不在工作地點" });
    standAt(s, content, LOC.farm); // the farmhouse is not the field
    expect(canStartWork(s, content, JOB.farmhand)).toMatchObject({ ok: false, reason: "不在工作地點" });
    standAt(s, content, LOC.field);
    const ok = canStartWork(s, content, JOB.farmhand);
    expect(ok).toMatchObject({ ok: true, sessionId: `${JOB.farmhand}@0:${7 * H}` });
    // and the barista job is not workable from the field
    s.gameClock.totalMinutes = 9 * H;
    expect(canStartWork(s, content, JOB.barista)).toMatchObject({ ok: false, reason: "不在工作地點" });
  });

  it("pays the wage once per shift, applies the need delta, then reports the shift done", () => {
    const s = newGame(content);
    s.gameClock.totalMinutes = 7 * H;
    standAt(s, content, LOC.field);
    const chk = canStartWork(s, content, JOB.farmhand);
    const money = s.player.money;
    const before = { ...s.player.needs };
    const first = completeWork(s, content, JOB.farmhand, chk.sessionId!, 1)!;
    expect(first.wage).toBe(Math.round(120 * performanceFromScore(1, before.stamina)));
    expect(s.player.money).toBe(money + first.wage);
    expect(s.player.needs.stamina).toBe(before.stamina - 20);
    expect(s.player.needs.satiety).toBe(before.satiety - 12);
    expect(s.player.needs.mood).toBe(before.mood + 2);
    expect(completeWork(s, content, JOB.farmhand, chk.sessionId!, 1)).toBeNull();
    expect(s.player.money).toBe(money + first.wage);
    expect(s.transactions.filter((t) => t.id === `wage:${chk.sessionId}`)).toHaveLength(1);
    expect(canStartWork(s, content, JOB.farmhand)).toMatchObject({ ok: false, reason: "這一班已完成" });
    // the afternoon shift is a new session
    s.gameClock.totalMinutes = 15 * H;
    expect(canStartWork(s, content, JOB.farmhand)).toMatchObject({ ok: true, sessionId: `${JOB.farmhand}@0:${15 * H}` });
  });

  it("farm shifts count towards shiftsWorked (rural unlock) together with cafe shifts", () => {
    const s = newGame(content);
    expect(checkCondition(s, content, "cond_unlock_rural")).toBe(false);
    completeWork(s, content, JOB.farmhand, `${JOB.farmhand}@0:${7 * H}`, 0.5);
    expect(checkCondition(s, content, "cond_unlock_rural")).toBe(false);
    completeWork(s, content, JOB.barista, `${JOB.barista}@0:${9 * H}`, 0.5);
    expect(checkCondition(s, content, "cond_unlock_rural")).toBe(true);
  });
});

describe("rural field map", () => {
  const map = content.maps[MAP.rural];
  const grid = buildCollisionGrid(map);
  const field = content.locations[LOC.field];

  it("crop rows block, tilled soil paths and the work tile are walkable and reachable from the west gate", () => {
    const code = (x: number, y: number) => map.rows[y][x];
    expect(code(18, 11)).toBe("c");
    expect(code(19, 13)).toBe("y");
    expect(grid[11][18]).toBe(true);
    expect(grid[13][19]).toBe(true);
    expect(code(18, 12)).toBe("t");
    expect(grid[12][18]).toBe(false);
    expect(grid[field.door.y][field.door.x]).toBe(false);
    expect(findPath(grid, map.spawn, field.door)).not.toBeNull();
    expect(findPath(grid, map.spawn, content.locations[LOC.farm].door)).not.toBeNull();
  });

  it("the work tile is the scarecrow's door and the farmer stands on a free field tile by day", () => {
    const scarecrow = map.props.find((p) => p.key === "scarecrow")!;
    expect({ x: scarecrow.x, y: scarecrow.y + 2 }).toEqual(field.door);
    expect(field.npcStand && grid[field.npcStand.y][field.npcStand.x]).toBe(false);
    const day = content.schedules[content.npcs.npc_005.scheduleId].entries.find((e) => e.activity === "work")!;
    expect(day.locationId).toBe(LOC.field);
    expect(day.startMinute).toBeLessThanOrEqual(7 * H);
    expect(day.endMinute).toBeGreaterThanOrEqual(18 * H);
  });
});
