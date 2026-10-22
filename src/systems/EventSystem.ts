import type { Condition, ContentDB, EventDefinition, EventTrigger, GameState } from "../game/types";
import { addTransaction } from "./EconomySystem";
import { applyNeedDelta } from "./NeedsSystem";
import { changeAffection, getRel, stageRank } from "./RelationshipSystem";

const MINUTES_PER_DAY = 24 * 60;

function check(state: GameState, c: Condition): boolean {
  switch (c.type) {
    case "money":
      return state.player.money >= c.atLeast;
    case "affection":
      return getRel(state, c.npcId).affection >= c.atLeast;
    case "stage": // "at least this stage"
      return stageRank(getRel(state, c.npcId).stage) >= stageRank(c.stage);
    case "eventCompleted":
      return state.eventStates[c.eventId]?.status === "completed";
    case "shiftsWorked":
      return state.workSessions.length >= c.atLeast;
    case "day": // 1-based day number, as displayed ("第N天")
      return Math.floor(state.gameClock.totalMinutes / MINUTES_PER_DAY) + 1 >= c.atLeast;
  }
}

export function checkCondition(state: GameState, content: ContentDB, conditionId: string): boolean {
  const def = content.conditions[conditionId];
  return !!def && def.all.every((c) => check(state, c));
}

const isCompleted = (state: GameState, id: string) => state.eventStates[id]?.status === "completed";
const conditionsMet = (state: GameState, content: ContentDB, e: EventDefinition) =>
  e.conditionIds.every((id) => checkCondition(state, content, id));

export function availableEvents(
  state: GameState,
  content: ContentDB,
  trigger: EventTrigger,
  ctx: { npcId?: string; locationId?: string } = {},
): EventDefinition[] {
  return Object.values(content.events).filter(
    (e) =>
      e.triggerType === trigger &&
      (ctx.npcId === undefined || e.npcId === ctx.npcId) &&
      (ctx.locationId === undefined || e.locationId === ctx.locationId) &&
      !isCompleted(state, e.id) &&
      conditionsMet(state, content, e),
  );
}

export function fireEvent(
  state: GameState,
  content: ContentDB,
  eventId: string,
): { ok: boolean; lines: string[]; messages: string[] } {
  const event = content.events[eventId];
  if (!event || isCompleted(state, eventId) || !conditionsMet(state, content, event)) {
    return { ok: false, lines: [], messages: [] };
  }
  const messages: string[] = [];
  event.effects.forEach((fx, i) => {
    switch (fx.type) {
      case "affection":
        changeAffection(state, fx.npcId, fx.delta);
        break;
      case "setStage":
        getRel(state, fx.npcId).stage = fx.stage;
        break;
      case "money":
        if (
          fx.delta !== 0 &&
          addTransaction(state, {
            id: `event:${eventId}:${i}`,
            amount: Math.abs(fx.delta),
            category: fx.delta > 0 ? "income" : "expense",
            reason: fx.reason,
          })
        ) {
          messages.push(`${fx.reason}：${fx.delta > 0 ? "+" : "-"}${Math.abs(fx.delta)}`);
        }
        break;
      case "need":
        applyNeedDelta(state, fx.delta);
        break;
      case "unlockMap":
        if (!state.unlockedMapIds.includes(fx.mapId)) state.unlockedMapIds.push(fx.mapId);
        break;
      case "message":
        messages.push(fx.text);
        break;
    }
  });
  state.eventStates[eventId] = { eventId, status: "completed", completedAtGameMinute: state.gameClock.totalMinutes };
  if (event.npcId) {
    const rel = getRel(state, event.npcId);
    if (!rel.completedEventIds.includes(eventId)) rel.completedEventIds.push(eventId);
  }
  return { ok: true, lines: event.lines, messages };
}

export function checkUnlocks(state: GameState, content: ContentDB): string[] {
  const added: string[] = [];
  for (const map of Object.values(content.maps)) {
    if (map.unlockConditionId && !state.unlockedMapIds.includes(map.id) && checkCondition(state, content, map.unlockConditionId)) {
      state.unlockedMapIds.push(map.id);
      added.push(map.id);
    }
  }
  return added;
}
