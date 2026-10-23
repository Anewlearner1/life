import { GameConfig } from "../game/GameConfig";
import type { FamilyMember, GameMinute, GameState, LifeStage, Season } from "../game/types";

// Local constant (not imported from TimeSystem) so TimeSystem can depend on this module without a cycle.
const MINUTES_PER_DAY = 24 * 60;

export const SEASON_LABEL: Record<Season, string> = { spring: "春", summer: "夏", autumn: "秋", winter: "冬" };
export const STAGE_LABEL: Record<LifeStage, string> = { baby: "嬰兒", child: "孩童", teen: "青少年", adult: "成年人", elder: "長者" };

const seasons = GameConfig.calendar.seasons;
const daysPerSeason = () => GameConfig.calendar.daysPerSeason;
/** Days in one game year (4 seasons). */
export const daysPerYear = (): number => daysPerSeason() * seasons.length;
export const minutesPerYear = (): number => daysPerYear() * MINUTES_PER_DAY;

const dayInYear = (day: number) => ((Math.floor(day) % daysPerYear()) + daysPerYear()) % daysPerYear();

/** day is the 0-based day index. */
export function seasonOf(day: number): Season {
  return seasons[Math.floor(dayInYear(day) / daysPerSeason())];
}

/** 1-based year number. */
export function yearOf(day: number): number {
  return Math.floor(Math.floor(day) / daysPerYear()) + 1;
}

/** 1-based day within the season. */
export function dayOfSeason(day: number): number {
  return (dayInYear(day) % daysPerSeason()) + 1;
}

/** "第1年 春 第3天" */
export function formatDate(total: GameMinute): string {
  const day = Math.floor(total / MINUTES_PER_DAY);
  return `第${yearOf(day)}年 ${SEASON_LABEL[seasonOf(day)]} 第${dayOfSeason(day)}天`;
}

/** Age in (fractional) years; `multiplier` speeds up aging (children). */
export function ageYears(birthMinute: GameMinute, now: GameMinute, multiplier = 1): number {
  return ((now - birthMinute) * multiplier) / minutesPerYear();
}

export function lifeStage(age: number): LifeStage {
  const s = GameConfig.calendar.stages;
  return age < s.child ? "baby" : age < s.teen ? "child" : age < s.adult ? "teen" : age < s.elder ? "adult" : "elder";
}

export function playerAge(state: GameState): number {
  return ageYears(state.player.birthMinute, state.gameClock.totalMinutes);
}

export function childAge(child: FamilyMember, now: GameMinute): number {
  return ageYears(child.birthMinute, now, GameConfig.calendar.childAgingMultiplier);
}
