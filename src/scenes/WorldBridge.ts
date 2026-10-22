import type { ContentDB, GameState, WorldPosition } from "../game/types";

export type InteractTarget = { kind: "npc"; id: string } | { kind: "location"; id: string };

/**
 * Integration surface between the Phaser WorldScene and the game controller.
 * WorldScene never mutates GameState: it reads positions through getState() and reports
 * movement/interaction through the callbacks; the controller owns all state changes.
 */
export interface WorldBridge {
  getState(): GameState;
  getContent(): ContentDB;
  /** Player reached the interaction tile of an NPC (adjacent) or location (its door tile). */
  onInteract(target: InteractTarget): void;
  /** Called after each completed tile step. The controller should store it in state.player.position. */
  onPlayerStep(pos: WorldPosition): void;
  /** True while a UI modal is open; taps are ignored and any queued walk is cancelled. */
  isInputBlocked(): boolean;
}

export type WorldSceneData = { bridge: WorldBridge };
