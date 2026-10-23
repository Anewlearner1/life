import { GameConfig } from "../game/GameConfig";
import type { ContentDB, DialogueLine, EventDefinition, GameState, Relationship, RelationshipStage } from "../game/types";
import { availableEvents } from "./EventSystem";

const STAGE_ORDER: RelationshipStage[] = ["stranger", "acquaintance", "close", "partner", "spouse"];
export const stageRank = (s: RelationshipStage): number => STAGE_ORDER.indexOf(s);

export function getRel(state: GameState, npcId: string): Relationship {
  return (state.relationships[npcId] ??= { npcId, affection: 0, stage: "stranger", completedEventIds: [] });
}

function stageFor(affection: number): RelationshipStage {
  const t = GameConfig.relationship.stageThresholds;
  return affection >= t.close ? "close" : affection >= t.acquaintance ? "acquaintance" : "stranger";
}

/** Sets a stage explicitly (events, marriage) and tracks when the partnership began. */
export function setStage(state: GameState, npcId: string, stage: RelationshipStage): Relationship {
  const rel = getRel(state, npcId);
  rel.stage = stage;
  if (stage === "partner") rel.partnerSinceMinute ??= state.gameClock.totalMinutes;
  else if (stageRank(stage) < stageRank("partner")) delete rel.partnerSinceMinute;
  return rel;
}

/** `partner`/`spouse` are only ever set explicitly (events, marriage) and are never downgraded here. */
export function changeAffection(state: GameState, npcId: string, delta: number): Relationship {
  const rel = getRel(state, npcId);
  rel.affection = Math.min(100, Math.max(0, rel.affection + delta));
  if (rel.stage !== "partner" && rel.stage !== "spouse") rel.stage = stageFor(rel.affection);
  return rel;
}

export function talkTo(
  state: GameState,
  content: ContentDB,
  npcId: string,
): { line: DialogueLine; affectionGained: number; event?: EventDefinition } {
  const event = availableEvents(state, content, "talk", { npcId })[0];
  if (event) return { line: { id: event.id, text: event.lines[0] ?? "" }, affectionGained: 0, event };

  const rel = getRel(state, npcId);
  const lines = content.dialogues[content.npcs[npcId]?.dialogueSetId ?? ""]?.lines ?? [];
  const eligible = lines.filter(
    (l) => (l.minAffection ?? 0) <= rel.affection && (!l.minStage || stageRank(rel.stage) >= stageRank(l.minStage)),
  );
  const top = Math.max(...eligible.map((l) => l.minAffection ?? 0));
  const best = eligible.filter((l) => (l.minAffection ?? 0) === top);
  const now = state.gameClock.totalMinutes;
  const line = best.length ? best[Math.floor(now) % best.length] : { id: "none", text: "…" };

  const ready = rel.lastTalkMinute === undefined || now - rel.lastTalkMinute >= GameConfig.relationship.talkCooldownMinutes;
  if (!ready) return { line, affectionGained: 0 };
  const before = rel.affection;
  changeAffection(state, npcId, GameConfig.relationship.talkAffection + (line.affectionDelta ?? 0));
  rel.lastTalkMinute = now;
  return { line, affectionGained: rel.affection - before };
}
