import { GameConfig } from "./GameConfig";
import type { CharacterAppearance, ContentDB, GameState } from "./types";
import { MAP } from "../data/ids";
import { checkUnlocks } from "../systems/EventSystem";
import { minutesPerYear } from "../systems/CalendarSystem";
import { updateNPCs } from "../systems/NPCScheduleSystem";
import { hashString, rollWeather } from "../systems/WeatherSystem";

const MINUTES_PER_DAY = 24 * 60;

/** `seed` is optional; without it the world seed is derived deterministically from the name. */
export function createNewGame(content: ContentDB, name: string, appearance: CharacterAppearance, seed?: number): GameState {
  const { time, needs, economy, calendar } = GameConfig;
  const startMinutes = time.startDay * MINUTES_PER_DAY + time.startMinuteOfDay;
  const worldSeed = (seed ?? hashString(name)) >>> 0;
  const startMap = content.maps[MAP.starter] ?? Object.values(content.maps)[0];
  const state: GameState = {
    schemaVersion: GameConfig.schemaVersion,
    gameClock: { totalMinutes: startMinutes, mode: "normal" },
    player: {
      id: "player",
      name,
      appearance: { ...appearance, accessoryIds: [...appearance.accessoryIds] },
      position: { mapId: startMap.id, x: startMap.spawn.x, y: startMap.spawn.y, facing: "down" },
      needs: { ...needs.initial },
      money: economy.startingMoney,
      birthMinute: startMinutes - calendar.playerStartAge * minutesPerYear(),
    },
    npcs: {},
    relationships: {},
    currentMapId: startMap.id,
    unlockedMapIds: Object.values(content.maps).filter((m) => !m.unlockConditionId).map((m) => m.id),
    eventStates: {},
    inventory: {},
    transactions: [],
    workSessions: [],
    lastProcessedDay: time.startDay,
    family: { children: [], generation: 1, ancestors: [] },
    weather: { day: time.startDay, kind: rollWeather(worldSeed, time.startDay) },
    worldSeed,
  };
  for (const id of Object.keys(content.npcs)) {
    state.relationships[id] = { npcId: id, affection: 0, stage: "stranger", completedEventIds: [] };
  }
  updateNPCs(state, content);
  checkUnlocks(state, content);
  return state;
}
