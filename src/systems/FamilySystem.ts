import { GameConfig } from "../game/GameConfig";
import type { CharacterAppearance, ContentDB, FamilyMember, GameState } from "../game/types";
import { MAP, LOC } from "../data/ids";
import { childAge, lifeStage, minutesPerYear, playerAge, STAGE_LABEL } from "./CalendarSystem";
import { getRel, setStage, stageRank } from "./RelationshipSystem";
import { hash01 } from "./WeatherSystem";

const MINUTES_PER_DAY = 24 * 60;
const dayOf = (total: number) => Math.floor(total / MINUTES_PER_DAY);

const CHILD_NAMES = [
  "小明", "小華", "小美", "小安", "小晴", "小宇", "小琪", "小凱", "小雅", "小澄", "小風", "小橙",
  "小語", "小禾", "小喬", "小森",
];

export function itemCount(state: GameState, itemId: string): number {
  return state.inventory[itemId] ?? 0;
}

/** Removes up to `count` of an item (never below 0; empty stacks are deleted). Returns how many were removed. */
export function consumeItem(state: GameState, itemId: string, count = 1): number {
  const n = Math.min(count, itemCount(state, itemId));
  if (n <= 0) return 0;
  const left = itemCount(state, itemId) - n;
  if (left > 0) state.inventory[itemId] = left;
  else delete state.inventory[itemId];
  return n;
}

/** Marriage: the NPC becomes spouse and is recorded in FamilyState. */
export function marry(state: GameState, npcId: string): void {
  setStage(state, npcId, "spouse");
  state.family.spouseNpcId = npcId;
  state.family.marriedAtMinute = state.gameClock.totalMinutes;
}

/** Starts a pregnancy unless already expecting or at the child limit. Returns whether it started. */
export function conceive(state: GameState): boolean {
  const f = state.family;
  if (f.babyDueDay !== undefined || f.children.length >= GameConfig.family.maxChildren) return false;
  f.babyDueDay = dayOf(state.gameClock.totalMinutes) + GameConfig.family.pregnancyDays;
  return true;
}

export function canPropose(state: GameState, content: ContentDB, npcId: string): { ok: boolean; reason?: string } {
  const cfg = GameConfig.family;
  const def = content.npcs[npcId];
  if (!def) return { ok: false, reason: "找不到對象" };
  if (state.family.spouseNpcId) return { ok: false, reason: "已經結婚了" };
  const others = Object.values(state.relationships).some(
    (r) => r.npcId !== npcId && stageRank(r.stage) >= stageRank("partner"),
  );
  if (others) return { ok: false, reason: "已經有其他伴侶" };
  const rel = getRel(state, npcId);
  if (rel.stage !== "partner") return { ok: false, reason: "需要先成為伴侶" };
  // Legacy partners without a recorded start count as long-standing.
  const since = rel.partnerSinceMinute ?? -Infinity;
  if ((state.gameClock.totalMinutes - since) / MINUTES_PER_DAY < cfg.minPartnerDays) {
    return { ok: false, reason: `交往還不夠久（至少 ${cfg.minPartnerDays} 天）` };
  }
  if (rel.affection < cfg.proposeAffection) return { ok: false, reason: "好感度還不夠" };
  if (itemCount(state, cfg.ringItemId) < 1) return { ok: false, reason: "需要一枚戒指" };
  return { ok: true };
}

export function propose(
  state: GameState,
  content: ContentDB,
  npcId: string,
): { ok: boolean; lines: string[]; messages: string[]; reason?: string } {
  const check = canPropose(state, content, npcId);
  if (!check.ok) return { ok: false, lines: [], messages: [], reason: check.reason };
  consumeItem(state, GameConfig.family.ringItemId, 1);
  marry(state, npcId);
  const name = content.npcs[npcId].name;
  return { ok: true, lines: ["我願意。"], messages: [`你和 ${name} 結婚了！`] };
}

function pickName(state: GameState, salt: number): string {
  const used = new Set([state.player.name, ...state.family.children.map((c) => c.name)]);
  const start = Math.floor(hash01(state.worldSeed, salt + 7919) * CHILD_NAMES.length);
  for (let i = 0; i < CHILD_NAMES.length; i++) {
    const n = CHILD_NAMES[(start + i) % CHILD_NAMES.length];
    if (!used.has(n)) return n;
  }
  return `${CHILD_NAMES[start]}${state.family.children.length + 1}`;
}

function nextChildId(state: GameState): string {
  const max = Math.max(0, ...state.family.children.map((c) => Number(c.id.replace("child_", "")) || 0));
  return `child_${max + 1}`;
}

function newborn(state: GameState, birthMinute: number, dueDay: number): FamilyMember {
  const p = state.player.appearance;
  // Inherit the player's hair/outfit/body; the other parent's look is not modelled.
  const appearance: CharacterAppearance = { ...p, accessoryIds: [] };
  return {
    id: nextChildId(state),
    name: pickName(state, dueDay),
    birthMinute,
    appearance,
    otherParentNpcId: state.family.spouseNpcId,
  };
}

/** Day-start hook: due births (once) and life-stage changes. Uses the current day's 00:00 as "now". */
export function processFamilyDay(state: GameState, _content: ContentDB): string[] {
  const messages: string[] = [];
  const f = state.family;
  const day = dayOf(state.gameClock.totalMinutes);
  const now = day * MINUTES_PER_DAY;
  const prev = now - MINUTES_PER_DAY;

  for (const child of f.children) {
    if (child.birthMinute > prev) continue;
    const before = lifeStage(childAge(child, prev));
    const after = lifeStage(childAge(child, now));
    if (before !== after) messages.push(`${child.name} 長大成為${STAGE_LABEL[after]}了`);
  }

  if (f.babyDueDay !== undefined && day >= f.babyDueDay) {
    const child = newborn(state, f.babyDueDay * MINUTES_PER_DAY, f.babyDueDay);
    f.children.push(child);
    f.babyDueDay = undefined;
    messages.push("寶寶出生了！", `為孩子取名叫 ${child.name}`);
  }
  return messages;
}

export function canSucceed(state: GameState): { ok: boolean; heirId?: string; reason?: string } {
  const now = state.gameClock.totalMinutes;
  const eligible = state.family.children
    .filter((c) => childAge(c, now) >= GameConfig.family.successionAge)
    .sort((a, b) => a.birthMinute - b.birthMinute);
  if (eligible.length === 0) return { ok: false, reason: "還沒有年滿 " + GameConfig.family.successionAge + " 歲的孩子" };
  return { ok: true, heirId: eligible[0].id };
}

/** The heir becomes the player; returns messages (empty when preconditions fail). */
export function succeed(state: GameState, content: ContentDB, heirId: string): string[] {
  const f = state.family;
  const now = state.gameClock.totalMinutes;
  const heir = f.children.find((c) => c.id === heirId);
  if (!heir || childAge(heir, now) < GameConfig.family.successionAge) return [];

  const oldName = state.player.name;
  const spouseId = f.spouseNpcId;
  f.ancestors.push({
    generation: f.generation,
    name: oldName,
    spouseName: spouseId ? content.npcs[spouseId]?.name : undefined,
    retiredDay: dayOf(now),
    ageAtRetirement: playerAge(state),
  });

  // The heir keeps their (accelerated) age: birthMinute is rebased so playerAge() continues from it.
  const age = childAge(heir, now);
  state.player.name = heir.name;
  state.player.appearance = { ...heir.appearance, accessoryIds: [...heir.appearance.accessoryIds] };
  state.player.birthMinute = now - age * minutesPerYear();
  state.player.money = Math.floor(state.player.money * GameConfig.family.inheritanceRate);
  state.player.currentJobId = undefined;

  f.generation += 1;
  f.children = f.children.filter((c) => c.id !== heirId);
  f.spouseNpcId = undefined;
  f.marriedAtMinute = undefined;
  f.babyDueDay = undefined;

  const resetNpcs = new Set<string>();
  for (const rel of Object.values(state.relationships)) {
    if (rel.npcId === spouseId) {
      rel.stage = "close";
      delete rel.partnerSinceMinute;
    } else {
      rel.affection = 0;
      rel.stage = "stranger";
      rel.completedEventIds = [];
      delete rel.lastTalkMinute;
      delete rel.partnerSinceMinute;
      resetNpcs.add(rel.npcId);
    }
  }
  // A new generation can live through each NPC's story again.
  for (const ev of Object.values(content.events)) {
    if (ev.npcId && resetNpcs.has(ev.npcId)) delete state.eventStates[ev.id];
  }

  const bed = content.locations[LOC.homeBed] ?? content.locations[LOC.home];
  const map = bed ? content.maps[bed.mapId] : content.maps[MAP.starter] ?? Object.values(content.maps)[0];
  const spot = bed ? bed.door : map.spawn;
  state.player.position = { mapId: map.id, x: spot.x, y: spot.y, facing: "down" };
  state.currentMapId = map.id;

  return [`${oldName} 把家交給了 ${heir.name}`, `第 ${f.generation} 代開始了`];
}

