import { describe, expect, it } from "vitest";
import { LOC, MAP } from "../data/ids";
import type { ScheduleDefinition } from "../game/types";
import { activeEntry, updateNPCs } from "../systems/NPCScheduleSystem";
import { advanceGameTime } from "../systems/TimeSystem";
import { makeContent, newGame } from "./fixtures";

const def = makeContent().schedules.sch_owner; // rest 17:00-08:00 (spans midnight), work 08:00-17:00

describe("NPCScheduleSystem", () => {
  it("activeEntry picks the covering entry, including across midnight", () => {
    expect(activeEntry(def, 8 * 60).activity).toBe("work");
    expect(activeEntry(def, 17 * 60 - 1).activity).toBe("work");
    expect(activeEntry(def, 17 * 60).activity).toBe("rest");
    expect(activeEntry(def, 23 * 60 + 59).activity).toBe("rest");
    expect(activeEntry(def, 0).activity).toBe("rest");
    expect(activeEntry(def, 8 * 60 - 1).activity).toBe("rest");
  });

  it("falls back to the most recently ended entry in a gap", () => {
    const gap: ScheduleDefinition = { id: "g", entries: [
      { startMinute: 100, endMinute: 200, activity: "a", locationId: "x" },
      { startMinute: 300, endMinute: 400, activity: "b", locationId: "x" },
    ] };
    expect(activeEntry(gap, 250).activity).toBe("a");
    expect(activeEntry(gap, 450).activity).toBe("b");
    expect(activeEntry(gap, 50).activity).toBe("b");
    expect(() => activeEntry({ id: "e", entries: [] }, 0)).toThrow();
  });

  it("updateNPCs places NPCs one tile below the door, staggered when sharing a door", () => {
    const c = makeContent(), s = newGame(c);
    const cafe = c.locations[LOC.cafe];
    // 08:00: both NPCs at the cafe
    expect(s.npcs.npc_001.position).toMatchObject({ mapId: MAP.starter, x: cafe.door.x, y: cafe.door.y + 1 });
    expect(s.npcs.npc_007.position.x).toBe(cafe.door.x + 1);
    expect(s.npcs.npc_001.position.y).toBe(s.npcs.npc_007.position.y);
    advanceGameTime(s, c, 10 * 60); // 18:00: owner home, artist still at cafe
    const home = c.locations[LOC.home];
    expect(s.npcs.npc_001.currentActivity).toBe("rest");
    expect(s.npcs.npc_001.position).toMatchObject({ x: home.door.x, y: home.door.y + 1 });
    expect(s.npcs.npc_007.position.x).toBe(cafe.door.x); // alone now -> slot 0
  });

  it("creates missing NPC entries and keeps positions inside the map", () => {
    const c = makeContent(), s = newGame(c);
    c.locations[LOC.cafe].door = { x: 5, y: 3 }; // bottom-right corner of 6x4 map
    s.npcs = {};
    updateNPCs(s, c);
    for (const n of Object.values(s.npcs)) {
      expect(n.position.x).toBeLessThanOrEqual(5);
      expect(n.position.y).toBeLessThanOrEqual(3);
    }
    expect(Object.keys(s.npcs)).toHaveLength(2);
  });
});
