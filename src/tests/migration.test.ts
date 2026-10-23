import { describe, expect, it } from "vitest";
import { GameConfig } from "../game/GameConfig";
import { migrate } from "../persistence/SaveMigration";
import { MemoryStorage, SaveService } from "../persistence/SaveService";
import { minutesPerYear, playerAge } from "../systems/CalendarSystem";
import { advanceGameTime } from "../systems/TimeSystem";
import { hashString, rollWeather } from "../systems/WeatherSystem";
import { makeContent } from "./fixtures";

/** A hand-written schema v1 save (before family / weather / worldSeed / birthMinute existed). */
const v1 = () => ({
  schemaVersion: 1,
  saveId: "slot1",
  savedAtRealTime: "2026-01-01T00:00:00.000Z",
  gameState: {
    schemaVersion: 1,
    gameClock: { totalMinutes: 3 * 1440 + 9 * 60, mode: "normal" },
    player: {
      id: "player", name: "老玩家",
      appearance: { bodyId: "b1", hairId: "h1", outfitId: "o1", accessoryIds: [] },
      position: { mapId: "map_starter", x: 2, y: 2, facing: "down" },
      needs: { stamina: 50, satiety: 60, mood: 70 },
      money: 321,
    },
    npcs: { npc_007: { id: "npc_007", currentActivity: "social", position: { mapId: "map_starter", x: 4, y: 2, facing: "down" } } },
    relationships: { npc_007: { npcId: "npc_007", affection: 80, stage: "partner", completedEventIds: ["ev_confess"] } },
    currentMapId: "map_starter",
    unlockedMapIds: ["map_starter"],
    eventStates: {},
    inventory: { sandwich: 2 },
    transactions: [],
    workSessions: [],
    lastProcessedDay: 3,
  },
});

describe("SaveMigration v1 -> v2", () => {
  it("fills defaults and keeps existing data", () => {
    const out = migrate(v1());
    const gs = out.gameState;
    expect(out.schemaVersion).toBe(GameConfig.schemaVersion);
    expect(gs.schemaVersion).toBe(GameConfig.schemaVersion);
    expect(gs.player.money).toBe(321);
    expect(gs.relationships.npc_007.stage).toBe("partner");
    expect(gs.family).toEqual({ children: [], generation: 1, ancestors: [] });
    expect(gs.worldSeed).toBe(hashString("老玩家"));
    expect(gs.weather).toEqual({ day: 3, kind: rollWeather(gs.worldSeed, 3) });
    expect(playerAge(gs)).toBeCloseTo(GameConfig.calendar.playerStartAge);
    expect(gs.player.birthMinute).toBe(gs.gameClock.totalMinutes - GameConfig.calendar.playerStartAge * minutesPerYear());
  });

  it("is idempotent: a migrated save migrates to itself", () => {
    const once = JSON.parse(JSON.stringify(migrate(v1())));
    expect(migrate(once)).toEqual(once);
  });

  it("loads through SaveService, keeps playing and re-saves as v2", async () => {
    const storage = new MemoryStorage();
    await storage.set(GameConfig.save.slotId, JSON.stringify(v1()));
    const svc = new SaveService(storage);
    const state = (await svc.load())!;
    expect(state.family.generation).toBe(1);
    advanceGameTime(state, makeContent(), 2 * 1440);
    expect(state.weather.day).toBe(5);
    await svc.save(state);
    const raw = JSON.parse((await storage.get(GameConfig.save.slotId))!);
    expect(raw.schemaVersion).toBe(2);
    expect(await svc.load()).toEqual(JSON.parse(JSON.stringify(state)));
  });

  it("rejects a v1 save without a usable gameState", () => {
    const bad = v1();
    (bad as { gameState: unknown }).gameState = { player: {} };
    expect(() => migrate(bad)).toThrow();
  });
});
