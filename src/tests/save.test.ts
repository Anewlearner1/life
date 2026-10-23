import "fake-indexeddb/auto";
import { beforeEach, describe, expect, it } from "vitest";
import { GameConfig } from "../game/GameConfig";
import { migrate } from "../persistence/SaveMigration";
import { DefaultStorage, IndexedDBStorage, MemoryStorage, SaveService, type SaveStorage } from "../persistence/SaveService";
import { advanceGameTime } from "../systems/TimeSystem";
import { buyItem } from "../systems/EconomySystem";
import { makeContent, newGame } from "./fixtures";

const storages: [string, () => SaveStorage][] = [
  ["in-memory", () => new MemoryStorage()],
  ["fake-indexeddb", () => new IndexedDBStorage()],
  ["default (IndexedDB first)", () => new DefaultStorage()],
];

describe.each(storages)("SaveService with %s", (_name, make) => {
  let svc: SaveService;
  beforeEach(async () => {
    svc = new SaveService(make());
    await svc.clear();
  });

  it("returns null when empty", async () => {
    expect(await svc.load()).toBeNull();
  });

  it("round-trips state", async () => {
    const c = makeContent(), s = newGame(c);
    buyItem(s, c, "sandwich");
    advanceGameTime(s, c, 1500);
    await svc.save(s);
    expect(await svc.load()).toEqual(s);
  });

  it("load does not advance time", async () => {
    const c = makeContent(), s = newGame(c);
    advanceGameTime(s, c, 100);
    await svc.save(s);
    const t = s.gameClock.totalMinutes;
    await new Promise((r) => setTimeout(r, 30));
    const loaded = (await svc.load())!;
    expect(loaded.gameClock.totalMinutes).toBe(t);
    expect(loaded.lastProcessedDay).toBe(s.lastProcessedDay);
  });

  it("clear removes the save; later save overwrites", async () => {
    const c = makeContent(), s = newGame(c);
    await svc.save(s);
    await svc.clear();
    expect(await svc.load()).toBeNull();
    await svc.save(s);
    s.player.money = 1;
    await svc.save(s);
    expect((await svc.load())!.player.money).toBe(1);
  });
});

describe("SaveMigration", () => {
  it("saves carry schemaVersion", async () => {
    const storage = new MemoryStorage();
    await new SaveService(storage).save(newGame());
    const raw = JSON.parse((await storage.get(GameConfig.save.slotId))!);
    expect(raw.schemaVersion).toBe(GameConfig.schemaVersion);
    expect(raw.gameState.schemaVersion).toBe(GameConfig.schemaVersion);
    expect(typeof raw.savedAtRealTime).toBe("string");
    expect(migrate(raw).gameState).toEqual(JSON.parse(JSON.stringify(newGame())));
  });

  it.each([null, undefined, 42, "str", [], {}, { schemaVersion: 1 }, { schemaVersion: "1", gameState: {} },
    { schemaVersion: 0, saveId: "a", savedAtRealTime: "t", gameState: {} },
    { schemaVersion: GameConfig.schemaVersion + 1, saveId: "a", savedAtRealTime: "t", gameState: {} },
    { schemaVersion: 1, saveId: "a", savedAtRealTime: "t", gameState: { player: {} } }])("rejects garbage %#", (bad) => {
    expect(() => migrate(bad)).toThrow();
  });

  it("load throws on unparsable stored data", async () => {
    const storage = new MemoryStorage();
    await storage.set(GameConfig.save.slotId, "{not json");
    await expect(new SaveService(storage).load()).rejects.toThrow();
  });
});
