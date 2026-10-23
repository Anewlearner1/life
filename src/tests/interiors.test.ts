import { describe, expect, it } from "vitest";
import { content } from "../data";
import { MAP } from "../data/ids";
import { createNewGame } from "../game/GameState";
import { updateNPCs } from "../systems/NPCScheduleSystem";

const look = { bodyId: "b", hairId: "hair_spiky", outfitId: "outfit1", accessoryIds: [] };

describe("interior NPC placement", () => {
  it("staff stand behind their indoor counters; visitors sit in the cafe", () => {
    const st = createNewGame(content, "t", look);
    st.gameClock.totalMinutes = 10 * 1440 + 10 * 60; // 10:00
    updateNPCs(st, content);
    expect(st.npcs.npc_001.position).toMatchObject({ mapId: MAP.cafeIn, x: 4, y: 2 });
    expect(st.npcs.npc_002.position).toMatchObject({ mapId: MAP.shopIn, x: 8, y: 2 });
    st.gameClock.totalMinutes = 10 * 1440 + 12 * 60 + 30; // 12:30: neighbor + artist visit the cafe
    updateNPCs(st, content);
    expect(st.npcs.npc_003.position.mapId).toBe(MAP.cafeIn);
    expect(st.npcs.npc_007.position.mapId).toBe(MAP.cafeIn);
  });
});
