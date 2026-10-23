import { GameConfig } from "../game/GameConfig";
import type { GameState, NeedKey, NeedState } from "../game/types";
import { lifeStage, playerAge } from "./CalendarSystem";

const NEED_KEYS: NeedKey[] = ["stamina", "satiety", "mood"];

export function clampNeed(v: number): number {
  return Math.min(100, Math.max(0, v));
}

/** Elders cannot exceed calendar.elderStaminaCap. */
export function staminaCap(state: GameState): number {
  return lifeStage(playerAge(state)) === "elder" ? GameConfig.calendar.elderStaminaCap : 100;
}

export function applyNeedDelta(state: GameState, delta: Partial<NeedState>): void {
  for (const k of NEED_KEYS) {
    const d = delta[k];
    if (d !== undefined) state.player.needs[k] = clampNeed(state.player.needs[k] + d);
  }
  state.player.needs.stamina = Math.min(state.player.needs.stamina, staminaCap(state));
}

/** Applies `hours` game hours (fractions allowed). Sleeping restores stamina and spares mood. */
export function applyHourly(state: GameState, hours: number, sleeping = false): void {
  const { perHour, sleepStaminaPerHour, lowSatietyMoodPenaltyPerHour, warnBelow } = GameConfig.needs;
  for (let left = hours; left > 0; left -= 1) {
    const f = Math.min(1, left);
    const n = state.player.needs;
    if (sleeping) {
      applyNeedDelta(state, { stamina: sleepStaminaPerHour * f, satiety: perHour.satiety * f });
    } else {
      const hungry = n.satiety < warnBelow;
      applyNeedDelta(state, {
        stamina: perHour.stamina * f,
        satiety: perHour.satiety * f,
        mood: (perHour.mood + (hungry ? lowSatietyMoodPenaltyPerHour : 0)) * f,
      });
    }
  }
}

export function lowNeeds(state: GameState): NeedKey[] {
  return NEED_KEYS.filter((k) => state.player.needs[k] < GameConfig.needs.warnBelow);
}
