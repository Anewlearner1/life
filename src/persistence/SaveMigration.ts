import { GameConfig } from "../game/GameConfig";
import type { SaveData } from "../game/types";
import { minutesPerYear } from "../systems/CalendarSystem";
import { hashString, rollWeather } from "../systems/WeatherSystem";

type Raw = Record<string, unknown>;

/** MIGRATIONS[n] upgrades a save from schema n to n+1. Add entries when bumping GameConfig.schemaVersion. */
const MIGRATIONS: Record<number, (save: Raw) => Raw> = {
  // v1 -> v2: family, weather, worldSeed, player.birthMinute (PRD P-18).
  1: (save) => {
    const gs = save.gameState;
    if (!isObj(gs) || !isObj(gs.player) || !isObj(gs.gameClock)) return save; // assertShape rejects it later
    const player = gs.player;
    const total = isNum(gs.gameClock.totalMinutes) ? gs.gameClock.totalMinutes : 0;
    const worldSeed = isNum(gs.worldSeed) ? gs.worldSeed : hashString(String(player.name ?? ""));
    const day = Math.floor(total / (24 * 60));
    return {
      ...save,
      gameState: {
        ...gs,
        player: { ...player, birthMinute: isNum(player.birthMinute) ? player.birthMinute : total - GameConfig.calendar.playerStartAge * minutesPerYear() },
        family: isObj(gs.family) ? gs.family : { children: [], generation: 1, ancestors: [] },
        weather: isObj(gs.weather) ? gs.weather : { day, kind: rollWeather(worldSeed, day) },
        worldSeed,
      },
    };
  },
};

const isObj = (v: unknown): v is Raw => typeof v === "object" && v !== null && !Array.isArray(v);
const isNum = (v: unknown): v is number => typeof v === "number" && Number.isFinite(v);

function assertShape(gs: unknown): void {
  if (!isObj(gs)) throw new Error("存檔格式錯誤：缺少 gameState");
  const clock = gs.gameClock;
  const player = gs.player;
  const ok =
    isObj(clock) && isNum(clock.totalMinutes) && ["paused", "normal", "fast"].includes(clock.mode as string) &&
    isObj(player) && isNum(player.money) && isObj(player.position) && isObj(player.needs) &&
    ["stamina", "satiety", "mood"].every((k) => isNum((player.needs as Raw)[k])) &&
    isObj(gs.npcs) && isObj(gs.relationships) && isObj(gs.eventStates) && isObj(gs.inventory) &&
    typeof gs.currentMapId === "string" && isNum(gs.lastProcessedDay) &&
    Array.isArray(gs.unlockedMapIds) && Array.isArray(gs.transactions) && Array.isArray(gs.workSessions);
  if (!ok) throw new Error("存檔格式錯誤：gameState 欄位不完整");
}

export function migrate(data: unknown): SaveData {
  if (!isObj(data)) throw new Error("存檔格式錯誤");
  let version = data.schemaVersion;
  if (!Number.isInteger(version) || (version as number) < 1) throw new Error("存檔缺少有效的 schemaVersion");
  if ((version as number) > GameConfig.schemaVersion) throw new Error("存檔版本比遊戲新，無法讀取");

  let save: Raw = data;
  for (let v = version as number; v < GameConfig.schemaVersion; v++) {
    const step = MIGRATIONS[v];
    if (!step) throw new Error(`缺少 schema ${v} 的升級步驟`);
    save = { ...step(save), schemaVersion: v + 1 };
  }
  if (typeof save.saveId !== "string" || typeof save.savedAtRealTime !== "string") throw new Error("存檔格式錯誤：缺少 saveId");
  assertShape(save.gameState);
  (save.gameState as Raw).schemaVersion = GameConfig.schemaVersion;
  return save as unknown as SaveData;
}
