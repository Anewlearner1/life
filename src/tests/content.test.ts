import { describe, expect, it } from "vitest";
import { content } from "../data/index";
import type { Condition, Effect, EventDefinition } from "../game/types";
import { ITEM } from "../data/ids";

const { npcs, events, conditions, dialogues, items } = content;
const MAX_LINE = 40;
const lenOf = (s: string) => [...s].length;

function npcIdOfCondition(c: Condition): string | undefined {
  return c.type === "affection" || c.type === "stage" || c.type === "noOtherPartner" ? c.npcId : undefined;
}

function npcIdOfEffect(fx: Effect): string | undefined {
  return fx.type === "affection" || fx.type === "setStage" || fx.type === "marry" ? fx.npcId : undefined;
}

const condsOf = (e: EventDefinition): Condition[] => e.conditionIds.flatMap((id) => conditions[id]?.all ?? []);

/** childrenAtMost cap of a baby event, or undefined when it has no such condition. */
function childCapOf(e: EventDefinition): number | undefined {
  const c = condsOf(e).find((x): x is Extract<Condition, { type: "childrenAtMost" }> => x.type === "childrenAtMost");
  return c?.count;
}

describe("content integrity", () => {
  it("every event conditionId exists, and event npcId exists when set", () => {
    for (const e of Object.values(events)) {
      for (const id of e.conditionIds) expect(conditions[id], `${e.id} -> ${id}`).toBeDefined();
      if (e.npcId !== undefined) expect(npcs[e.npcId], `${e.id} npcId`).toBeDefined();
    }
  });

  it("every condition refers to an existing NPC and event", () => {
    for (const cond of Object.values(conditions)) {
      for (const c of cond.all) {
        const npcId = npcIdOfCondition(c);
        if (npcId !== undefined) expect(npcs[npcId], `${cond.id} npcId`).toBeDefined();
        if (c.type === "eventCompleted") expect(events[c.eventId], `${cond.id} eventId`).toBeDefined();
      }
    }
  });

  it("every effect npcId exists", () => {
    for (const e of Object.values(events)) {
      for (const fx of e.effects) {
        const npcId = npcIdOfEffect(fx);
        if (npcId !== undefined) expect(npcs[npcId], `${e.id} effect npcId`).toBeDefined();
      }
    }
  });

  it("every NPC has an existing dialogue set", () => {
    for (const n of Object.values(npcs)) expect(dialogues[n.dialogueSetId], n.id).toBeDefined();
  });

  it("dialogue line ids are unique across all sets", () => {
    const ids = Object.values(dialogues).flatMap((s) => s.lines.map((l) => l.id));
    expect(new Set(ids).size).toBe(ids.length);
  });
});

describe("romance", () => {
  const romanceable = Object.values(npcs).filter((n) => n.romanceable);

  it("romanceable NPCs are exactly npc_002, npc_006, npc_007", () => {
    expect(romanceable.map((n) => n.id).sort()).toEqual(["npc_002", "npc_006", "npc_007"]);
  });

  for (const npc of romanceable) {
    it(`${npc.id} has exactly one confess event that is guarded by noOtherPartner`, () => {
      const confess = Object.values(events).filter(
        (e) => e.npcId === npc.id && e.effects.some((fx) => fx.type === "setStage" && fx.stage === "partner"),
      );
      expect(confess, `${npc.id} confess events`).toHaveLength(1);
      const [ev] = confess;
      const guarded = ev.conditionIds.some((cid) =>
        (conditions[cid]?.all ?? []).some((c) => c.type === "noOtherPartner" && c.npcId === npc.id),
      );
      expect(guarded, `${ev.id} noOtherPartner`).toBe(true);
    });

    it(`${npc.id} has exactly one marry event gated by the ring and noOtherPartner`, () => {
      const marry = Object.values(events).filter(
        (e) => e.npcId === npc.id && e.effects.some((fx) => fx.type === "marry"),
      );
      expect(marry, `${npc.id} marry events`).toHaveLength(1);
      const [ev] = marry;
      const cs = condsOf(ev);
      expect(cs.some((c) => c.type === "hasItem" && c.itemId === ITEM.ring), `${ev.id} hasItem ring`).toBe(true);
      expect(cs.some((c) => c.type === "noOtherPartner" && c.npcId === npc.id), `${ev.id} noOtherPartner`).toBe(true);
    });

    it(`${npc.id} baby events form a chain (childrenAtMost 0 → 1 → 2)`, () => {
      const babies = Object.values(events).filter(
        (e) => e.npcId === npc.id && e.effects.some((fx) => fx.type === "conceive"),
      );
      expect(babies, `${npc.id} baby events`).toHaveLength(3);
      expect(babies.map(childCapOf).sort(), `${npc.id} caps`).toEqual([0, 1, 2]);
      for (const ev of babies) {
        const cs = condsOf(ev);
        expect(cs.some((c) => c.type === "notPregnant"), `${ev.id} notPregnant`).toBe(true);
        expect(cs.some((c) => c.type === "stage" && c.npcId === npc.id && c.stage === "spouse"), `${ev.id} spouse`).toBe(true);
        const cap = childCapOf(ev) ?? -1;
        const prev = babies.find((p) => childCapOf(p) === cap - 1);
        if (prev) {
          expect(cs.some((c) => c.type === "eventCompleted" && c.eventId === prev.id), `${ev.id} follows ${prev.id}`).toBe(true);
        } else {
          expect(cap, `${ev.id} is the first variant`).toBe(0);
        }
      }
    });
  }
});

describe("items", () => {
  it("item_ring is a 1200 product with the ring icon and no use effect", () => {
    const ring = items[ITEM.ring];
    expect(ring, ITEM.ring).toBeDefined();
    expect(ring.price).toBe(1200);
    expect(ring.iconAsset).toMatch(/^objects\/products\/OBJ_004_Ring_v01\.png$/);
    expect(ring.useEffect).toBeUndefined();
  });
});

describe("dialogue", () => {
  it("minAffection is sorted ascending within each set", () => {
    for (const set of Object.values(dialogues)) {
      const mins = set.lines.map((l) => l.minAffection ?? 0);
      expect(mins, set.id).toEqual([...mins].sort((a, b) => a - b));
    }
  });
});

describe("player-facing text length", () => {
  it(`all dialogue lines are <= ${MAX_LINE} chars`, () => {
    for (const set of Object.values(dialogues)) {
      for (const l of set.lines) expect(lenOf(l.text), l.id).toBeLessThanOrEqual(MAX_LINE);
    }
  });

  it(`all event lines and messages are <= ${MAX_LINE} chars`, () => {
    for (const e of Object.values(events)) {
      for (const line of e.lines) expect(lenOf(line), `${e.id} line`).toBeLessThanOrEqual(MAX_LINE);
      for (const fx of e.effects) {
        if (fx.type === "message") expect(lenOf(fx.text), `${e.id} message`).toBeLessThanOrEqual(MAX_LINE);
        if (fx.type === "money") expect(lenOf(fx.reason), `${e.id} reason`).toBeLessThanOrEqual(MAX_LINE);
      }
    }
  });
});
