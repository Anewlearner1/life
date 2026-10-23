import { GameConfig } from "../game/GameConfig";
import type { ContentDB, GameState, Weather } from "../game/types";
import { seasonOf } from "./CalendarSystem";

const KINDS: Weather[] = ["sunny", "cloudy", "rain", "snow"];

/** FNV-1a string hash → uint32 (deterministic seeds from names). */
export function hashString(s: string): number {
  let h = 0x811c9dc5;
  for (let i = 0; i < s.length; i++) h = Math.imul(h ^ s.charCodeAt(i), 0x01000193);
  return h >>> 0;
}

/** Deterministic uniform [0,1) from (seed, n). */
export function hash01(seed: number, n: number): number {
  let h = (seed ^ Math.imul(Math.floor(n) + 1, 0x9e3779b1)) >>> 0;
  h = Math.imul(h ^ (h >>> 16), 0x85ebca6b);
  h = Math.imul(h ^ (h >>> 13), 0xc2b2ae35);
  h ^= h >>> 16;
  h = Math.imul(h ^ (h >>> 15), 0x2c1b3c6d);
  h ^= h >>> 12;
  return (h >>> 0) / 4294967296;
}

/** Same seed + same day always gives the same weather; odds come from GameConfig.weather.odds by season. */
export function rollWeather(seed: number, day: number): Weather {
  const odds = GameConfig.weather.odds[seasonOf(day)];
  const u = hash01(seed, day);
  let acc = 0;
  let last: Weather = "sunny";
  for (const k of KINDS) {
    if (odds[k] <= 0) continue;
    last = k;
    acc += odds[k];
    if (u < acc) return k;
  }
  return last;
}

export function currentWeather(state: GameState): Weather {
  return state.weather.kind;
}

export function isIndoor(content: ContentDB, mapId: string): boolean {
  return content.maps[mapId]?.indoor === true;
}
