import { GameConfig } from "./GameConfig";
import type { CharacterAppearance, ContentDB, GameState } from "./types";
import { MAP } from "../data/ids";
import { checkUnlocks } from "../systems/EventSystem";
import { updateNPCs } from "../systems/NPCScheduleSystem";

const MINUTES_PER_DAY = 24 * 60;

export function createNewGame(content: ContentDB, name: string, appearance: CharacterAppearance): GameState {
  const { time, needs, economy } = GameConfig;
  const startMap = content.maps[MAP.starter] ?? Object.values(content.maps)[0];
  const state: GameState = {
    schemaVersion: GameConfig.schemaVersion,
    gameClock: { totalMinutes: time.startDay * MINUTES_PER_DAY + time.startMinuteOfDay, mode: "normal" },
    player: {
      id: "player",
      name,
      appearance: { ...appearance, accessoryIds: [...appearance.accessoryIds] },
      position: { mapId: startMap.id, x: startMap.spawn.x, y: startMap.spawn.y, facing: "down" },
      needs: { ...needs.initial },
      money: economy.startingMoney,
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
  };
  for (const id of Object.keys(content.npcs)) {
    state.relationships[id] = { npcId: id, affection: 0, stage: "stranger", completedEventIds: [] };
  }
  updateNPCs(state, content);
  checkUnlocks(state, content);
  return state;
}
