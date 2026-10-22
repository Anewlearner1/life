import { describe, expect, it } from "vitest";
import { GameConfig } from "../game/GameConfig";
import type { JobDefinition } from "../game/types";
import { JOB, LOC } from "../data/ids";
import { canStartWork, completeWork, nextShift, performanceFromScore, shiftAt } from "../systems/JobSystem";
import { advanceGameTime } from "../systems/TimeSystem";
import { makeContent, newGame, standAt } from "./fixtures";

const DAY = 1440;
const H = 60;
const job = makeContent().jobs[JOB.barista];

describe("JobSystem shifts", () => {
  it("detects the shift window (end exclusive)", () => {
    expect(shiftAt(job, 8 * H)).toBeNull();
    expect(shiftAt(job, 9 * H)).toEqual({ start: 9 * H, end: 13 * H });
    expect(shiftAt(job, 13 * H - 1)).not.toBeNull();
    expect(shiftAt(job, 13 * H)).toBeNull();
  });

  it("honors weekday rules", () => {
    expect(shiftAt(job, 20 * H)).toBeNull(); // weekday 0
    expect(shiftAt(job, 6 * DAY + 20 * H)).toEqual({ start: 6 * DAY + 20 * H, end: 6 * DAY + 22 * H });
    expect(shiftAt(job, 13 * DAY + 21 * H)).not.toBeNull(); // next Saturday
    expect(shiftAt(job, 5 * DAY + 21 * H)).toBeNull();
  });

  it("handles shifts crossing midnight", () => {
    const night: JobDefinition = { ...job, shiftRules: [{ weekday: 2, startMinute: 22 * H, endMinute: 2 * H }] };
    expect(shiftAt(night, 2 * DAY + 23 * H)).toEqual({ start: 2 * DAY + 22 * H, end: 3 * DAY + 2 * H });
    expect(shiftAt(night, 3 * DAY + H)).not.toBeNull(); // spilled into weekday 3
    expect(shiftAt(night, 3 * DAY + 2 * H)).toBeNull();
  });

  it("nextShift is the earliest start after now", () => {
    expect(nextShift(job, 8 * H)).toEqual({ start: 9 * H, end: 13 * H });
    expect(nextShift(job, 9 * H).start).toBe(DAY + 9 * H); // currently in one: next is tomorrow
    expect(nextShift(job, 14 * H + 6 * DAY).start).toBe(6 * DAY + 20 * H);
    expect(() => nextShift({ ...job, shiftRules: [] }, 0)).toThrow();
  });
});

describe("JobSystem work", () => {
  it("canStartWork rejects outside shift, wrong location, already completed", () => {
    const c = makeContent(), s = newGame(c);
    standAt(s, c, LOC.cafe);
    expect(canStartWork(s, c, JOB.barista)).toMatchObject({ ok: false, reason: "不在班表時段" });
    advanceGameTime(s, c, 60); // 09:00
    standAt(s, c, LOC.home);
    expect(canStartWork(s, c, JOB.barista)).toMatchObject({ ok: false, reason: "不在工作地點" });
    standAt(s, c, LOC.cafe);
    const ok = canStartWork(s, c, JOB.barista);
    expect(ok.ok).toBe(true);
    expect(ok.sessionId).toBe(`${JOB.barista}@0:${9 * H}`);
    completeWork(s, c, JOB.barista, ok.sessionId!, 1);
    expect(canStartWork(s, c, JOB.barista)).toMatchObject({ ok: false, reason: "這一班已完成" });
    expect(canStartWork(s, c, "nope").ok).toBe(false);
  });

  it("completeWork pays exactly once per sessionId", () => {
    const c = makeContent(), s = newGame(c);
    const money = s.player.money;
    const id = "job_barista@0:540";
    const first = completeWork(s, c, JOB.barista, id, 1);
    expect(first).not.toBeNull();
    expect(completeWork(s, c, JOB.barista, id, 1)).toBeNull();
    expect(s.player.money).toBe(money + first!.wage);
    expect(s.workSessions).toHaveLength(1);
    expect(s.transactions).toHaveLength(1);
    expect(s.player.needs.satiety).toBe(GameConfig.needs.initial.satiety + job.needDelta.satiety!);
    expect(completeWork(s, c, JOB.barista, "job_barista@1:540", 0.5)).not.toBeNull();
  });

  it("wage = base x performance x attendance; performance clamped 0.5-1.5", () => {
    const c = makeContent(), s = newGame(c);
    const { performanceMin: lo, performanceMax: hi, attendanceMultiplier } = GameConfig.job;
    expect(performanceFromScore(0, 100)).toBe(lo);
    expect(performanceFromScore(1, 100)).toBe(hi);
    expect(performanceFromScore(5, 100)).toBe(hi);
    expect(performanceFromScore(-5, 100)).toBe(lo);
    expect(performanceFromScore(0.5, 100)).toBeCloseTo(1);
    const w = completeWork(s, c, JOB.barista, "a", 0.75)!;
    expect(w.performanceMultiplier).toBeCloseTo(1.25);
    expect(w.wage).toBe(Math.round(job.baseWage * 1.25 * attendanceMultiplier));
    expect(completeWork(s, c, JOB.barista, "b", 0)!.wage).toBe(job.baseWage * lo);
  });

  it("low stamina applies a penalty", () => {
    const high = performanceFromScore(0.75, 100);
    const low = performanceFromScore(0.75, GameConfig.needs.warnBelow - 1);
    expect(low).toBeCloseTo(high * GameConfig.job.lowStaminaPenalty);
    expect(performanceFromScore(0, 0)).toBe(GameConfig.job.performanceMin); // never below min
  });
});
