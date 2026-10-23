import { GameConfig } from "../game/GameConfig";
import type { ContentDB, GameMinute, GameState, NeedKey, TimeMode } from "../game/types";
import { availableEvents, checkUnlocks, fireEvent } from "./EventSystem";
import { processFamilyDay } from "./FamilySystem";
import { applyHourly, applyNeedDelta, lowNeeds } from "./NeedsSystem";
import { updateNPCs } from "./NPCScheduleSystem";
import { isIndoor, rollWeather } from "./WeatherSystem";

export const MINUTES_PER_HOUR = 60;
export const MINUTES_PER_DAY = 24 * MINUTES_PER_HOUR;

export type AdvanceResult = {
  dayChanged: boolean;
  messages: string[];
  firedEventIds: string[];
  unlockedMapIds: string[];
  saveRequested: boolean;
  /** Needs that newly dropped below the warning threshold during this advance. */
  needWarnings: NeedKey[];
};

const NEED_LABEL: Record<NeedKey, string> = { stamina: "體力", satiety: "飽足", mood: "心情" };
const pad = (n: number) => String(n).padStart(2, "0");

/** day is 0-based; weekday = day % 7 (day 0 = weekday 0). */
export function clockParts(total: GameMinute) {
  const day = Math.floor(total / MINUTES_PER_DAY);
  const minuteOfDay = Math.floor(total) - day * MINUTES_PER_DAY;
  return {
    day,
    hour: Math.floor(minuteOfDay / MINUTES_PER_HOUR),
    minute: minuteOfDay % MINUTES_PER_HOUR,
    minuteOfDay,
    weekday: day % 7,
  };
}

export function formatClock(total: GameMinute): string {
  const p = clockParts(total);
  return `第${p.day + 1}天 ${pad(p.hour)}:${pad(p.minute)}`;
}

export function realMsToGameMinutes(mode: TimeMode, ms: number): number {
  if (mode === "paused") return 0;
  const perSecond = mode === "fast" ? GameConfig.time.fastMinutesPerSecond : GameConfig.time.normalMinutesPerSecond;
  return (ms / 1000) * perSecond;
}

export function setMode(state: GameState, mode: TimeMode): void {
  state.gameClock.mode = mode;
}

function processDayStart(state: GameState, content: ContentDB, res: AdvanceResult): void {
  const day = clockParts(state.gameClock.totalMinutes).day;
  if (state.lastProcessedDay >= day) return;
  state.lastProcessedDay = day;
  res.dayChanged = true;
  res.saveRequested = true;
  res.messages.push(`第${day + 1}天開始了`);
  state.weather = { day, kind: rollWeather(state.worldSeed, day) };
  res.messages.push(...processFamilyDay(state, content));
  updateNPCs(state, content);
  for (const e of availableEvents(state, content, "dayStart")) {
    const fired = fireEvent(state, content, e.id);
    if (!fired.ok) continue;
    res.firedEventIds.push(e.id);
    res.messages.push(...fired.messages);
  }
  res.unlockedMapIds.push(...checkUnlocks(state, content));
}

/** The only way game time moves. Boundaries (hours, midnight) are processed in chronological order. */
export function advanceGameTime(state: GameState, content: ContentDB, minutes: number): AdvanceResult {
  const res: AdvanceResult = {
    dayChanged: false, messages: [], firedEventIds: [], unlockedMapIds: [], saveRequested: false, needWarnings: [],
  };
  if (!(minutes > 0)) return res;

  const clock = state.gameClock;
  const startMinute = Math.floor(clock.totalMinutes);
  const lowBefore = lowNeeds(state);

  for (let left = minutes; left > 0; ) {
    const boundary = (Math.floor(clock.totalMinutes / MINUTES_PER_HOUR) + 1) * MINUTES_PER_HOUR;
    const gap = boundary - clock.totalMinutes;
    if (left < gap) {
      clock.totalMinutes += left;
      break;
    }
    clock.totalMinutes = boundary; // exact, so midnight detection never drifts
    left -= gap;
    applyHourly(state, 1);
    // The hour that just ended still belongs to the previous day's weather.
    if ((state.weather.kind === "rain" || state.weather.kind === "snow") && !isIndoor(content, state.player.position.mapId)) {
      applyNeedDelta(state, { mood: GameConfig.weather.badWeatherMoodPerHour });
    }
    if (clock.totalMinutes % MINUTES_PER_DAY === 0) processDayStart(state, content, res);
  }

  if (Math.floor(clock.totalMinutes) !== startMinute) updateNPCs(state, content);
  res.unlockedMapIds.push(...checkUnlocks(state, content));
  const every = GameConfig.save.autosaveEveryGameMinutes;
  if (Math.floor(clock.totalMinutes / every) !== Math.floor(startMinute / every)) res.saveRequested = true;

  res.needWarnings = lowNeeds(state).filter((k) => !lowBefore.includes(k));
  for (const k of res.needWarnings) res.messages.push(`${NEED_LABEL[k]}過低`);
  return res;
}
