import { describe, expect, it } from "vitest";
import { LOC } from "../data/ids";
import { GameConfig } from "../game/GameConfig";
import { minutesPerYear, childAge, playerAge, lifeStage } from "../systems/CalendarSystem";
import { checkCondition, fireEvent } from "../systems/EventSystem";
import { canPropose, canSucceed, conceive, propose, succeed } from "../systems/FamilySystem";
import { changeAffection } from "../systems/RelationshipSystem";
import { updateNPCs } from "../systems/NPCScheduleSystem";
import { advanceGameTime } from "../systems/TimeSystem";
import { ARTIST, HOME_IN, makeFamilyContent, makeMarriageReady, newGame, OWNER, RING } from "./fixtures";
import type { ContentDB, GameState } from "../game/types";

const DAY = 1440;
const cfg = GameConfig.family;

function married(content: ContentDB = makeFamilyContent()): [GameState, ContentDB] {
  const s = newGame(content);
  makeMarriageReady(s);
  expect(propose(s, content, ARTIST).ok).toBe(true);
  return [s, content];
}

/** A child that is exactly `age` (child-years) old right now. */
const childOfAge = (s: GameState, id: string, name: string, age: number) => ({
  id, name, appearance: { ...s.player.appearance, hairId: "h_kid" }, otherParentNpcId: ARTIST,
  birthMinute: s.gameClock.totalMinutes - (age * minutesPerYear()) / GameConfig.calendar.childAgingMultiplier,
});

describe("proposal", () => {
  it("fails without a ring", () => {
    const c = makeFamilyContent(), s = newGame(c);
    makeMarriageReady(s);
    delete s.inventory[RING];
    expect(canPropose(s, c, ARTIST)).toMatchObject({ ok: false });
    expect(propose(s, c, ARTIST).ok).toBe(false);
    expect(s.relationships[ARTIST].stage).toBe("partner");
  });

  it("fails when partners for too short a time, with low affection, or when not partners", () => {
    const c = makeFamilyContent(), s = newGame(c);
    makeMarriageReady(s);
    s.relationships[ARTIST].partnerSinceMinute = s.gameClock.totalMinutes - (cfg.minPartnerDays - 1) * DAY;
    expect(canPropose(s, c, ARTIST).ok).toBe(false);
    s.relationships[ARTIST].partnerSinceMinute = s.gameClock.totalMinutes - cfg.minPartnerDays * DAY;
    expect(canPropose(s, c, ARTIST).ok).toBe(true);
    s.relationships[ARTIST].affection = cfg.proposeAffection - 1;
    expect(canPropose(s, c, ARTIST).ok).toBe(false);
    s.relationships[ARTIST].affection = 100;
    s.relationships[ARTIST].stage = "close";
    expect(canPropose(s, c, ARTIST).ok).toBe(false);
    expect(canPropose(s, c, "npc_missing").ok).toBe(false);
  });

  it("succeeds, consumes the ring and records the marriage", () => {
    const c = makeFamilyContent(), s = newGame(c);
    makeMarriageReady(s);
    s.inventory[RING] = 2;
    const r = propose(s, c, ARTIST);
    expect(r.ok).toBe(true);
    expect(r.messages.length).toBeGreaterThan(0);
    expect(s.inventory[RING]).toBe(1);
    expect(s.relationships[ARTIST].stage).toBe("spouse");
    expect(s.family.spouseNpcId).toBe(ARTIST);
    expect(s.family.marriedAtMinute).toBe(s.gameClock.totalMinutes);
    expect(canPropose(s, c, ARTIST)).toMatchObject({ ok: false, reason: "已經結婚了" });
  });

  it("the marry/consumeItem effects do the same via events; ring removed when last", () => {
    const c = makeFamilyContent(), s = newGame(c);
    expect(fireEvent(s, c, "ev_marry").ok).toBe(false); // no ring
    s.inventory[RING] = 1;
    expect(fireEvent(s, c, "ev_marry").ok).toBe(true);
    expect(s.inventory[RING]).toBeUndefined();
    expect(s.relationships[ARTIST].stage).toBe("spouse");
    expect(s.family.spouseNpcId).toBe(ARTIST);
  });
});

describe("exclusivity and stages", () => {
  it("partner/spouse of someone else blocks noOtherPartner; affection never changes partner/spouse", () => {
    const c = makeFamilyContent(), s = newGame(c);
    c.conditions.c_excl = { id: "c_excl", all: [{ type: "noOtherPartner", npcId: ARTIST }] };
    expect(checkCondition(s, c, "c_excl")).toBe(true);
    s.relationships[OWNER].stage = "partner";
    expect(checkCondition(s, c, "c_excl")).toBe(false);
    s.relationships[OWNER].stage = "spouse";
    expect(checkCondition(s, c, "c_excl")).toBe(false);
    s.relationships[OWNER].stage = "close";
    expect(checkCondition(s, c, "c_excl")).toBe(true);
    // the NPC themself does not block
    s.relationships[ARTIST].stage = "spouse";
    expect(checkCondition(s, c, "c_excl")).toBe(true);

    changeAffection(s, ARTIST, -100);
    expect(s.relationships[ARTIST].stage).toBe("spouse");
    s.relationships[OWNER].stage = "partner";
    changeAffection(s, OWNER, 100);
    expect(s.relationships[OWNER].stage).toBe("partner");
    changeAffection(s, OWNER, -100);
    expect(s.relationships[OWNER].stage).toBe("partner");
  });

  it("cannot propose while another NPC is a partner", () => {
    const c = makeFamilyContent(), s = newGame(c);
    makeMarriageReady(s);
    s.relationships[OWNER].stage = "partner";
    expect(canPropose(s, c, ARTIST).ok).toBe(false);
  });

  it("stage condition treats spouse as above partner", () => {
    const c = makeFamilyContent(), s = newGame(c);
    c.conditions.c_partner = { id: "c_partner", all: [{ type: "stage", npcId: ARTIST, stage: "partner" }] };
    s.relationships[ARTIST].stage = "spouse";
    expect(checkCondition(s, c, "c_partner")).toBe(true);
  });
});

describe("conditions", () => {
  it("hasItem, marriedDays, childrenAtMost, notPregnant", () => {
    const c = makeFamilyContent(), s = newGame(c);
    expect(checkCondition(s, c, "c_ring")).toBe(false);
    s.inventory[RING] = 1;
    expect(checkCondition(s, c, "c_ring")).toBe(true);
    c.conditions.c_ring2 = { id: "c_ring2", all: [{ type: "hasItem", itemId: RING, count: 2 }] };
    expect(checkCondition(s, c, "c_ring2")).toBe(false);

    expect(checkCondition(s, c, "c_baby")).toBe(false); // unmarried
    makeMarriageReady(s);
    propose(s, c, ARTIST);
    expect(checkCondition(s, c, "c_baby")).toBe(false); // married 0 days
    advanceGameTime(s, c, DAY);
    expect(checkCondition(s, c, "c_baby")).toBe(true);
    s.family.children = [childOfAge(s, "child_1", "a", 1), childOfAge(s, "child_2", "b", 1), childOfAge(s, "child_3", "c", 1)];
    expect(checkCondition(s, c, "c_baby")).toBe(false);
    s.family.children.pop();
    expect(checkCondition(s, c, "c_baby")).toBe(true);
    s.family.babyDueDay = 99;
    expect(checkCondition(s, c, "c_baby")).toBe(false);
  });
});

describe("pregnancy and birth", () => {
  it("conceive sets the due day; birth happens once after pregnancyDays, even across one big jump", () => {
    const [s, c] = married();
    advanceGameTime(s, c, DAY);
    expect(fireEvent(s, c, "ev_baby").ok).toBe(true);
    const due = Math.floor(s.gameClock.totalMinutes / DAY) + cfg.pregnancyDays;
    expect(s.family.babyDueDay).toBe(due);
    expect(conceive(s)).toBe(false); // already expecting
    expect(s.family.babyDueDay).toBe(due);

    const msgs: string[] = [];
    // one jump that skips well past the due day
    const r = advanceGameTime(s, c, (cfg.pregnancyDays + 4) * DAY);
    msgs.push(...r.messages);
    expect(msgs.filter((m) => m === "寶寶出生了！")).toHaveLength(1);
    expect(s.family.children).toHaveLength(1);
    expect(s.family.babyDueDay).toBeUndefined();
    const baby = s.family.children[0];
    expect(baby.id).toBe("child_1");
    expect(baby.name.length).toBeGreaterThan(0);
    expect(baby.birthMinute).toBe(due * DAY);
    expect(baby.otherParentNpcId).toBe(ARTIST);
    expect(baby.appearance.hairId).toBe(s.player.appearance.hairId);
    expect(advanceGameTime(s, c, 5 * DAY).messages.filter((m) => m === "寶寶出生了！")).toHaveLength(0);
    expect(s.family.children).toHaveLength(1);
  });

  it("does not give birth one day early", () => {
    const [s, c] = married();
    conceive(s);
    const due = s.family.babyDueDay!;
    advanceGameTime(s, c, due * DAY - s.gameClock.totalMinutes - 1);
    expect(s.family.children).toHaveLength(0);
    advanceGameTime(s, c, 1);
    expect(s.family.children).toHaveLength(1);
  });

  it("birth names are deterministic per world seed and unique among siblings", () => {
    const run = () => {
      const [s, c] = married();
      for (let i = 0; i < 3; i++) {
        conceive(s);
        advanceGameTime(s, c, (cfg.pregnancyDays + 1) * DAY);
      }
      return s.family.children.map((k) => k.name);
    };
    const names = run();
    expect(names).toEqual(run());
    expect(new Set(names).size).toBe(3);
  });

  it("maxChildren stops further conception", () => {
    const [s, c] = married();
    for (let i = 0; i < cfg.maxChildren; i++) {
      expect(conceive(s)).toBe(true);
      advanceGameTime(s, c, (cfg.pregnancyDays + 1) * DAY);
    }
    expect(s.family.children).toHaveLength(cfg.maxChildren);
    expect(conceive(s)).toBe(false);
    expect(s.family.babyDueDay).toBeUndefined();
    advanceGameTime(s, c, DAY);
    expect(s.family.children).toHaveLength(cfg.maxChildren);
  });

  it("reports life-stage changes", () => {
    const [s, c] = married();
    s.family.children = [childOfAge(s, "child_1", "小明", 2.9)];
    // age crosses 3 within (0.1 * 28 / 6) days ≈ 0.47 days: the next midnight
    const msgs = advanceGameTime(s, c, DAY).messages;
    expect(msgs).toContain("小明 長大成為孩童了");
    expect(lifeStage(childAge(s.family.children[0], s.gameClock.totalMinutes))).toBe("child");
    expect(advanceGameTime(s, c, DAY).messages.some((m) => m.includes("長大成為"))).toBe(false); // no repeat next day
  });
});

describe("succession", () => {
  function withHeir(): [GameState, ContentDB] {
    const [s, c] = married();
    s.family.children = [childOfAge(s, "child_1", "小明", cfg.successionAge), childOfAge(s, "child_2", "小美", 5)];
    s.player.money = 1000;
    s.inventory.sandwich = 3;
    s.relationships[OWNER].affection = 60;
    s.relationships[OWNER].stage = "close";
    return [s, c];
  }

  it("requires an heir old enough", () => {
    const [s] = married();
    expect(canSucceed(s)).toMatchObject({ ok: false });
    s.family.children = [childOfAge(s, "child_1", "小明", cfg.successionAge - 0.5)];
    expect(canSucceed(s).ok).toBe(false);
    s.family.children = [childOfAge(s, "child_1", "小明", cfg.successionAge)];
    expect(canSucceed(s)).toEqual({ ok: true, heirId: "child_1" });
  });

  it("picks the oldest eligible child; invalid heirs are refused untouched", () => {
    const [s, c] = withHeir();
    s.family.children.push(childOfAge(s, "child_3", "小凱", cfg.successionAge + 3));
    expect(canSucceed(s).heirId).toBe("child_3");
    const before = JSON.stringify(s);
    expect(succeed(s, c, "child_2")).toEqual([]); // too young
    expect(succeed(s, c, "nobody")).toEqual([]);
    expect(JSON.stringify(s)).toBe(before);
  });

  it("makes the heir the player and resets the household", () => {
    const [s, c] = withHeir();
    const oldName = s.player.name;
    const heirAge = childAge(s.family.children[0], s.gameClock.totalMinutes);
    const oldAge = playerAge(s);
    const msgs = succeed(s, c, "child_1");
    expect(msgs.length).toBeGreaterThan(0);
    expect(s.player.id).toBe("player");
    expect(s.player.name).toBe("小明");
    expect(s.player.appearance.hairId).toBe("h_kid");
    expect(playerAge(s)).toBeCloseTo(heirAge);
    expect(s.family.generation).toBe(2);
    expect(s.family.ancestors).toEqual([
      { generation: 1, name: oldName, spouseName: "Artist", retiredDay: 0, ageAtRetirement: oldAge },
    ]);
    expect(s.family.children.map((k) => k.id)).toEqual(["child_2"]);
    expect(s.family.spouseNpcId).toBeUndefined();
    expect(s.family.marriedAtMinute).toBeUndefined();
    expect(s.relationships[ARTIST].stage).toBe("close");
    expect(s.relationships[OWNER]).toMatchObject({ stage: "stranger", affection: 0 });
    expect(s.player.money).toBe(Math.floor(1000 * cfg.inheritanceRate));
    expect(s.inventory.sandwich).toBe(3);
    expect(s.player.position).toMatchObject({ mapId: HOME_IN, x: 1, y: 3 });
    expect(s.currentMapId).toBe(HOME_IN);
    expect(canSucceed(s).ok).toBe(false); // child_2 still too young
  });

  it("money follows inheritanceRate; position falls back to loc_home / spawn without a bed", () => {
    const c = makeFamilyContent({ withBed: false }), s = newGame(c);
    makeMarriageReady(s);
    propose(s, c, ARTIST);
    s.family.children = [childOfAge(s, "child_1", "小明", 20)];
    s.player.money = 1001;
    const saved = GameConfig.family.inheritanceRate;
    (GameConfig.family as { inheritanceRate: number }).inheritanceRate = 0.5;
    try {
      succeed(s, c, "child_1");
    } finally {
      (GameConfig.family as { inheritanceRate: number }).inheritanceRate = saved;
    }
    expect(s.player.money).toBe(500);
    const home = c.locations[LOC.home];
    expect(s.player.position).toMatchObject({ mapId: home.mapId, x: home.door.x, y: home.door.y });
  });

  it("a new generation can marry again (event states of reset NPCs are cleared, ring needed)", () => {
    const [s, c] = withHeir();
    succeed(s, c, "child_1");
    s.relationships[OWNER].stage = "partner";
    expect(canPropose(s, c, ARTIST).ok).toBe(false); // artist is "close", not partner
    s.relationships[OWNER].stage = "stranger";
    expect(s.family.spouseNpcId).toBeUndefined();
  });
});

describe("spouse schedule", () => {
  const posOf = (s: GameState, id: string) => s.npcs[id].position;

  it("spouse sleeps at the bed from 18:00 to 08:00, otherwise follows the schedule", () => {
    const [s, c] = married();
    const bed = c.locations[LOC.homeBed];
    const at = (minuteOfDay: number) => {
      s.gameClock.totalMinutes = 3 * DAY + minuteOfDay;
      updateNPCs(s, c);
    };
    for (const m of [18 * 60, 21 * 60, 23 * 60 + 59, 0, 3 * 60, 8 * 60 - 1]) {
      at(m);
      expect(posOf(s, ARTIST).mapId, `minute ${m}`).toBe(HOME_IN);
      expect(Math.abs(posOf(s, ARTIST).x - bed.door.x) + Math.abs(posOf(s, ARTIST).y - bed.door.y)).toBeLessThanOrEqual(2);
    }
    expect(s.npcs[ARTIST].currentActivity).toBe("sleep");
    at(12 * 60);
    expect(posOf(s, ARTIST).mapId).toBe(c.locations[LOC.cafe].mapId); // artist's schedule: cafe
    expect(s.npcs[ARTIST].currentActivity).toBe("social");
    // other NPCs unaffected at night
    at(20 * 60);
    expect(posOf(s, OWNER).mapId).not.toBe(HOME_IN);
  });

  it("falls back to loc_home when there is no bed location; non-spouses never move in", () => {
    const c = makeFamilyContent({ withBed: false }), s = newGame(c);
    s.gameClock.totalMinutes = 3 * DAY + 20 * 60;
    updateNPCs(s, c);
    const outsideDoor = c.locations[LOC.home];
    expect(s.npcs[ARTIST].currentActivity).toBe("social"); // unmarried: own schedule (cafe)
    makeMarriageReady(s);
    propose(s, c, ARTIST);
    updateNPCs(s, c);
    expect(posOf(s, ARTIST)).toMatchObject({ mapId: outsideDoor.mapId, y: outsideDoor.door.y + 1 });
    expect(s.npcs[ARTIST].currentActivity).toBe("rest");
  });
});
