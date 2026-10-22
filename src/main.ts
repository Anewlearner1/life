// TEMPORARY dev harness: boots Phaser with a stub bridge + inline fake state so the world can be
// viewed on its own. The integration agent replaces this file.
import Phaser from "phaser";
import { locations, maps } from "./data/maps";
import { BootScene, NPC_SPRITES } from "./scenes/BootScene";
import { WorldScene } from "./scenes/WorldScene";
import type { WorldBridge } from "./scenes/WorldBridge";
import type { ContentDB, GameState, NPCDefinition, NPC, WorldPosition } from "./game/types";

const npcDefs: Record<string, NPCDefinition> = {};
for (const n of NPC_SPRITES) {
  npcDefs[n.id] = {
    id: n.id,
    name: n.spriteKey,
    spriteKey: n.spriteKey,
    personalityTags: [],
    occupation: "",
    scheduleId: "",
    dialogueSetId: "",
    romanceable: false,
  };
}

const content: ContentDB = {
  npcs: npcDefs,
  schedules: {},
  dialogues: {},
  jobs: {},
  items: {},
  maps,
  locations,
  conditions: {},
  events: {},
};

const mkNpc = (id: string, x: number, y: number): NPC => ({
  id,
  currentActivity: "idle",
  position: { mapId: "map_starter", x, y, facing: "down" },
});

const state: GameState = {
  schemaVersion: 1,
  gameClock: { totalMinutes: 480, mode: "normal" },
  player: {
    id: "player",
    name: "Dev",
    appearance: { bodyId: "", hairId: "", outfitId: "", accessoryIds: [] },
    position: { mapId: "map_starter", x: maps.map_starter.spawn.x, y: maps.map_starter.spawn.y, facing: "down" },
    needs: { stamina: 80, satiety: 80, mood: 70 },
    money: 200,
  },
  npcs: {
    npc_001: mkNpc("npc_001", 23, 13),
    npc_002: mkNpc("npc_002", 19, 13),
    npc_003: mkNpc("npc_003", 6, 11),
    npc_007: mkNpc("npc_007", 10, 12),
    npc_005: { id: "npc_005", currentActivity: "idle", position: { mapId: "map_rural", x: 15, y: 7, facing: "down" } },
  },
  relationships: {},
  currentMapId: "map_starter",
  unlockedMapIds: ["map_starter"],
  eventStates: {},
  inventory: {},
  transactions: [],
  workSessions: [],
  lastProcessedDay: 0,
};

const hud = document.createElement("div");
hud.style.cssText =
  "position:fixed;left:6px;top:6px;padding:4px 6px;background:#000a;color:#fff;font:12px monospace;pointer-events:none;z-index:9";
document.body.appendChild(hud);
const log = (s: string) => {
  hud.textContent = s;
  console.log("[bridge]", s);
};

const bridge: WorldBridge = {
  getState: () => state,
  getContent: () => content,
  onPlayerStep: (pos: WorldPosition) => {
    state.player.position = pos;
  },
  isInputBlocked: () => false,
  onInteract: (t) => {
    log(`interact ${t.kind}:${t.id}`);
    if (t.kind !== "location") return;
    const loc = locations[t.id];
    if (loc.type !== "gate" || !loc.targetMapId) return;
    // Dev-only gate handling: hop to the target map, arriving next to the matching gate.
    const target = maps[loc.targetMapId];
    const back = Object.values(locations).find((l) => l.mapId === target.id && l.type === "gate" && l.targetMapId === loc.mapId);
    const arrive = back ? { x: back.door.x + (back.door.x === 0 ? 1 : -1), y: back.door.y } : target.spawn;
    state.currentMapId = target.id;
    state.player.position = { mapId: target.id, x: arrive.x, y: arrive.y, facing: "down" };
    (game.scene.getScene("World") as WorldScene).loadMap(target.id);
  },
};

const game = new Phaser.Game({
  type: Phaser.AUTO,
  parent: "game",
  backgroundColor: "#181425",
  pixelArt: true,
  roundPixels: true,
  scale: { mode: Phaser.Scale.RESIZE, width: "100%", height: "100%" },
  scene: [BootScene, WorldScene],
});

game.events.once("assets-ready", () => {
  game.scene.start("World", { bridge });
});

// Wander npc_003 now and then so NPC tweening is visible.
const spots = [{ x: 6, y: 11 }, { x: 9, y: 13 }, { x: 12, y: 13 }, { x: 4, y: 11 }];
let si = 0;
setInterval(() => {
  si = (si + 1) % spots.length;
  const p = state.npcs.npc_003.position;
  state.npcs.npc_003.position = { ...p, x: spots[si].x, y: spots[si].y };
}, 6000);

Object.assign(window, { __game: game, __state: state, __bridge: bridge });
