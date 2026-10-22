import type { ContentDB, GameState, ScheduleDefinition, ScheduleEntry } from "../game/types";

const MINUTES_PER_DAY = 24 * 60;

const covers = (e: ScheduleEntry, m: number) =>
  e.startMinute <= e.endMinute ? m >= e.startMinute && m < e.endMinute : m >= e.startMinute || m < e.endMinute;

/** Entry covering `minuteOfDay` (handles entries crossing midnight). In a gap, the most recently ended entry stays active. */
export function activeEntry(def: ScheduleDefinition, minuteOfDay: number): ScheduleEntry {
  if (def.entries.length === 0) throw new Error(`schedule ${def.id} has no entries`);
  const hit = def.entries.find((e) => covers(e, minuteOfDay));
  if (hit) return hit;
  const since = (e: ScheduleEntry) => (minuteOfDay - e.endMinute + MINUTES_PER_DAY) % MINUTES_PER_DAY;
  return def.entries.reduce((a, b) => (since(b) < since(a) ? b : a));
}

/** Slot 0,1,2,3,4 → offsets 0,+1,-1,+2,-2 so NPCs sharing a door don't overlap. */
const slotOffset = (slot: number) => (slot % 2 === 1 ? (slot + 1) / 2 : -slot / 2);

export function updateNPCs(state: GameState, content: ContentDB): void {
  const minuteOfDay = Math.floor(state.gameClock.totalMinutes) % MINUTES_PER_DAY;
  const perLocation: Record<string, number> = {};
  for (const def of Object.values(content.npcs)) {
    const schedule = content.schedules[def.scheduleId];
    if (!schedule) continue;
    const entry = activeEntry(schedule, minuteOfDay);
    const loc = content.locations[entry.locationId];
    const npc = (state.npcs[def.id] ??= {
      id: def.id,
      currentActivity: entry.activity,
      position: { mapId: loc?.mapId ?? "", x: 0, y: 0, facing: "down" },
    });
    npc.currentActivity = entry.activity;
    if (!loc) continue;
    const map = content.maps[loc.mapId];
    const slot = (perLocation[loc.id] = (perLocation[loc.id] ?? -1) + 1);
    const clamp = (v: number, max?: number) => Math.max(0, max === undefined ? v : Math.min(max - 1, v));
    const stand = loc.npcStand ?? { x: loc.door.x, y: loc.door.y + 1 };
    npc.position = {
      mapId: loc.mapId,
      x: clamp(stand.x + slotOffset(slot), map?.width),
      y: clamp(stand.y, map?.height),
      facing: "down",
    };
  }
}
