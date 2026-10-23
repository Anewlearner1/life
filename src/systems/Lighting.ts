import type { Weather } from "../game/types";
export { isIndoor } from "./WeatherSystem";

type Key = { m: number; color: number; alpha: number };

const NIGHT = 0x0b1030;
const CLEAR = 0xffffff;
/** Keyframes over the day (minute of day); linear interpolation between them, wrapping at midnight. */
const KEYS: Key[] = [
  { m: 0, color: NIGHT, alpha: 0.45 },
  { m: 4 * 60, color: NIGHT, alpha: 0.45 },
  { m: 5 * 60, color: 0xff9a5a, alpha: 0.22 }, // dawn
  { m: 7 * 60, color: CLEAR, alpha: 0 },
  { m: 17 * 60, color: CLEAR, alpha: 0 },
  { m: 18 * 60, color: 0xff8a40, alpha: 0.25 }, // dusk
  { m: 20 * 60, color: NIGHT, alpha: 0.45 },
  { m: 24 * 60, color: NIGHT, alpha: 0.45 },
];

const GREY = 0x6e7681;
/** Extra grey dim per weather. */
const WEATHER_DIM: Record<Weather, number> = { sunny: 0, cloudy: 0.05, rain: 0.18, snow: 0.12 };

export function lerpColor(a: number, b: number, t: number): number {
  const ch = (shift: number) => Math.round(((a >> shift) & 255) + (((b >> shift) & 255) - ((a >> shift) & 255)) * t);
  return (ch(16) << 16) | (ch(8) << 8) | ch(0);
}

const LAMPS_ON_FROM = 18 * 60;
const LAMPS_OFF_AT = 6 * 60;

/** Pure: tint overlay for the world. Indoors weather is ignored and the tint is half as strong. */
export function lightingAt(
  minuteOfDay: number,
  weather: Weather,
  indoor: boolean,
): { color: number; alpha: number; lampsOn: boolean } {
  const m = ((minuteOfDay % 1440) + 1440) % 1440;
  let i = KEYS.findIndex((k, idx) => idx < KEYS.length - 1 && m >= k.m && m < KEYS[idx + 1].m);
  if (i < 0) i = KEYS.length - 2;
  const a = KEYS[i], b = KEYS[i + 1];
  const t = (m - a.m) / (b.m - a.m);
  let color = lerpColor(a.color, b.color, t);
  let alpha = a.alpha + (b.alpha - a.alpha) * t;
  if (!indoor) {
    const dim = WEATHER_DIM[weather];
    if (dim > 0) {
      color = lerpColor(color, GREY, dim / (alpha + dim));
      alpha += (1 - alpha) * dim;
    }
  } else {
    alpha *= 0.5;
  }
  return { color, alpha, lampsOn: m >= LAMPS_ON_FROM || m < LAMPS_OFF_AT };
}
