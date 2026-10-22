import { describe, expect, it } from "vitest";
import { GameConfig } from "../game/GameConfig";
import { changeAffection, getRel, talkTo } from "../systems/RelationshipSystem";
import { advanceGameTime } from "../systems/TimeSystem";
import { ARTIST, makeContent, newGame, OWNER } from "./fixtures";

const T = GameConfig.relationship.stageThresholds;

describe("RelationshipSystem", () => {
  it("getRel creates stranger/0", () => {
    const s = newGame();
    delete s.relationships[ARTIST];
    expect(getRel(s, ARTIST)).toEqual({ npcId: ARTIST, affection: 0, stage: "stranger", completedEventIds: [] });
  });

  it("stage thresholds and clamping", () => {
    const s = newGame();
    expect(changeAffection(s, ARTIST, T.acquaintance - 1).stage).toBe("stranger");
    expect(changeAffection(s, ARTIST, 1).stage).toBe("acquaintance");
    expect(changeAffection(s, ARTIST, T.close - T.acquaintance).stage).toBe("close");
    expect(changeAffection(s, ARTIST, 1000).affection).toBe(100);
    expect(getRel(s, ARTIST).stage).toBe("close"); // partner is never auto-assigned
    expect(changeAffection(s, ARTIST, -1000)).toMatchObject({ affection: 0, stage: "stranger" });
  });

  it("partner is never downgraded", () => {
    const s = newGame();
    changeAffection(s, ARTIST, 80);
    getRel(s, ARTIST).stage = "partner";
    expect(changeAffection(s, ARTIST, -80)).toMatchObject({ affection: 0, stage: "partner" });
  });

  it("talk gives affection, then cooldown blocks it", () => {
    const c = makeContent(), s = newGame(c);
    const first = talkTo(s, c, OWNER);
    expect(first.affectionGained).toBe(GameConfig.relationship.talkAffection);
    expect(first.line.text).toBe("Welcome.");
    expect(talkTo(s, c, OWNER).affectionGained).toBe(0);
    advanceGameTime(s, c, GameConfig.relationship.talkCooldownMinutes - 1);
    expect(talkTo(s, c, OWNER).affectionGained).toBe(0);
    advanceGameTime(s, c, 1);
    expect(talkTo(s, c, OWNER).affectionGained).toBe(GameConfig.relationship.talkAffection);
  });

  it("picks the highest eligible dialogue and applies its delta", () => {
    const c = makeContent(), s = newGame(c);
    expect(talkTo(s, c, ARTIST).line.id).toBe("a0");
    advanceGameTime(s, c, 120);
    changeAffection(s, ARTIST, 20);
    // ev_intro (affection >= 20) now preempts normal lines
    expect(talkTo(s, c, ARTIST).event?.id).toBe("ev_intro");
    s.eventStates.ev_intro = { eventId: "ev_intro", status: "completed" };
    const r = talkTo(s, c, ARTIST);
    expect(r.line.id).toBe("a1");
    expect(r.affectionGained).toBe(GameConfig.relationship.talkAffection + 2);
  });

  it("returns an available talk event before lines, without applying it", () => {
    const c = makeContent(), s = newGame(c);
    changeAffection(s, ARTIST, T.acquaintance);
    const r = talkTo(s, c, ARTIST);
    expect(r.event?.id).toBe("ev_intro");
    expect(r.line.text).toBe("I paint.");
    expect(r.affectionGained).toBe(0);
    expect(s.eventStates.ev_intro).toBeUndefined();
    expect(getRel(s, ARTIST).lastTalkMinute).toBeUndefined();
  });
});

describe("partner-only dialogue", () => {
  it("skips minStage lines until the stage is reached", () => {
    const content = makeContent();
    const state = newGame(content);
    const set = content.dialogues[content.npcs[ARTIST].dialogueSetId];
    set.lines.push({ id: "partner_only", text: "只對伴侶說", minAffection: 90, minStage: "partner" });
    content.events = {};
    state.relationships[ARTIST] = { npcId: ARTIST, affection: 95, stage: "close", completedEventIds: [] };
    expect(talkTo(state, content, ARTIST).line.id).not.toBe("partner_only");
    state.relationships[ARTIST].stage = "partner";
    expect(talkTo(state, content, ARTIST).line.id).toBe("partner_only");
  });
});
