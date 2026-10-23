import { describe, expect, it } from "vitest";
import { COND, JOB, MAP } from "../data/ids";
import type { Condition } from "../game/types";
import { completeWork } from "../systems/JobSystem";
import { changeAffection } from "../systems/RelationshipSystem";
import { checkCondition, checkUnlocks, availableEvents, fireEvent } from "../systems/EventSystem";
import { advanceGameTime } from "../systems/TimeSystem";
import { ARTIST, makeContent, newGame } from "./fixtures";

function cond(c: Condition) {
  const content = makeContent();
  content.conditions.t = { id: "t", all: [c] };
  return { content, state: newGame(content) };
}

describe("EventSystem conditions", () => {
  it("money", () => {
    const { content, state } = cond({ type: "money", atLeast: 300 });
    expect(checkCondition(state, content, "t")).toBe(false);
    state.player.money = 300;
    expect(checkCondition(state, content, "t")).toBe(true);
  });
  it("affection", () => {
    const { content, state } = cond({ type: "affection", npcId: ARTIST, atLeast: 10 });
    expect(checkCondition(state, content, "t")).toBe(false);
    changeAffection(state, ARTIST, 10);
    expect(checkCondition(state, content, "t")).toBe(true);
  });
  it("stage (at least)", () => {
    const { content, state } = cond({ type: "stage", npcId: ARTIST, stage: "close" });
    expect(checkCondition(state, content, "t")).toBe(false);
    changeAffection(state, ARTIST, 20);
    expect(checkCondition(state, content, "t")).toBe(false);
    changeAffection(state, ARTIST, 30);
    expect(checkCondition(state, content, "t")).toBe(true);
    state.relationships[ARTIST].stage = "partner";
    expect(checkCondition(state, content, "t")).toBe(true);
  });
  it("eventCompleted", () => {
    const { content, state } = cond({ type: "eventCompleted", eventId: "ev_day2" });
    expect(checkCondition(state, content, "t")).toBe(false);
    state.eventStates.ev_day2 = { eventId: "ev_day2", status: "completed" };
    expect(checkCondition(state, content, "t")).toBe(true);
  });
  it("shiftsWorked", () => {
    const { content, state } = cond({ type: "shiftsWorked", atLeast: 2 });
    completeWork(state, content, JOB.barista, "s1", 1);
    expect(checkCondition(state, content, "t")).toBe(false);
    completeWork(state, content, JOB.barista, "s2", 1);
    expect(checkCondition(state, content, "t")).toBe(true);
  });
  it("day (1-based)", () => {
    const { content, state } = cond({ type: "day", atLeast: 2 });
    expect(checkCondition(state, content, "t")).toBe(false);
    advanceGameTime(state, content, 24 * 60);
    expect(checkCondition(state, content, "t")).toBe(true);
  });
  it("empty `all` is true; unknown id is false", () => {
    const content = makeContent();
    content.conditions.empty = { id: "empty", all: [] };
    const state = newGame(content);
    expect(checkCondition(state, content, "empty")).toBe(true);
    expect(checkCondition(state, content, "missing")).toBe(false);
  });
});

describe("EventSystem events", () => {
  it("availableEvents filters by trigger, npc, conditions, completion", () => {
    const c = makeContent(), s = newGame(c);
    expect(availableEvents(s, c, "talk", { npcId: ARTIST })).toEqual([]);
    changeAffection(s, ARTIST, 20);
    expect(availableEvents(s, c, "talk", { npcId: ARTIST }).map((e) => e.id)).toEqual(["ev_intro"]);
    expect(availableEvents(s, c, "talk", { npcId: "npc_001" })).toEqual([]);
    expect(availableEvents(s, c, "dayStart")).toEqual([]);
    fireEvent(s, c, "ev_intro");
    expect(availableEvents(s, c, "talk", { npcId: ARTIST })).toEqual([]);
  });

  it("fireEvent applies effects once and is idempotent", () => {
    const c = makeContent(), s = newGame(c);
    changeAffection(s, ARTIST, 20);
    const first = fireEvent(s, c, "ev_intro");
    expect(first).toEqual({ ok: true, lines: ["I paint."], messages: ["Met the artist."] });
    expect(s.relationships[ARTIST].affection).toBe(25);
    expect(s.eventStates.ev_intro.status).toBe("completed");
    expect(s.relationships[ARTIST].completedEventIds).toEqual(["ev_intro"]);
    expect(fireEvent(s, c, "ev_intro")).toEqual({ ok: false, lines: [], messages: [] });
    expect(s.relationships[ARTIST].affection).toBe(25);
  });

  it("fireEvent refuses unmet conditions and unknown events", () => {
    const c = makeContent(), s = newGame(c);
    expect(fireEvent(s, c, "ev_intro").ok).toBe(false);
    expect(fireEvent(s, c, "nope").ok).toBe(false);
    expect(s.eventStates).toEqual({});
  });

  it("money effects pay exactly once", () => {
    const c = makeContent(), s = newGame(c);
    const money = s.player.money;
    advanceGameTime(s, c, 24 * 60);
    expect(s.player.money).toBe(money + 10);
  });

  it("checkUnlocks adds a map once", () => {
    const c = makeContent(), s = newGame(c);
    expect(s.unlockedMapIds).toEqual([MAP.starter]);
    expect(checkUnlocks(s, c)).toEqual([]);
    s.relationships[ARTIST].stage = "partner";
    completeWork(s, c, JOB.barista, "s1", 1);
    expect(checkCondition(s, c, COND.unlockRural)).toBe(true);
    expect(checkUnlocks(s, c)).toEqual([MAP.rural]);
    expect(checkUnlocks(s, c)).toEqual([]);
    expect(s.unlockedMapIds).toEqual([MAP.starter, MAP.rural]);
  });

  it("unlockMap effect does not duplicate", () => {
    const c = makeContent(), s = newGame(c);
    c.events.ev_u = { id: "ev_u", triggerType: "manual", conditionIds: [], effects: [{ type: "unlockMap", mapId: MAP.rural }], lines: [] };
    fireEvent(s, c, "ev_u");
    s.relationships[ARTIST].stage = "partner";
    completeWork(s, c, JOB.barista, "s1", 1);
    expect(checkUnlocks(s, c)).toEqual([]);
    expect(s.unlockedMapIds.filter((m) => m === MAP.rural)).toHaveLength(1);
  });
});

describe("noOtherPartner condition", () => {
  it("is false only when another NPC is already the partner", () => {
    const content = makeContent();
    const state = newGame(content);
    const ids = Object.keys(content.npcs);
    content.conditions.c_excl = { id: "c_excl", all: [{ type: "noOtherPartner", npcId: ids[0] }] };
    expect(checkCondition(state, content, "c_excl")).toBe(true);
    state.relationships[ids[0]] = { npcId: ids[0], affection: 90, stage: "partner", completedEventIds: [] };
    expect(checkCondition(state, content, "c_excl")).toBe(true);
    state.relationships[ids[1]] = { npcId: ids[1], affection: 90, stage: "partner", completedEventIds: [] };
    expect(checkCondition(state, content, "c_excl")).toBe(false);
  });
});
