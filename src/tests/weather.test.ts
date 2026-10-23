import { describe, expect, it } from "vitest";
import { GameConfig } from "../game/GameConfig";
import { createNewGame } from "../game/GameState";
import { seasonOf } from "../systems/CalendarSystem";
import { lightingAt } from "../systems/Lighting";
import { canStartWork } from "../systems/JobSystem";
import { advanceGameTime } from "../systems/TimeSystem";
import { currentWeather, isIndoor, rollWeather } from "../systems/WeatherSystem";
import { appearance, FARM_JOB, HOME_IN, makeFamilyContent, newGame, standAt } from "./fixtures";
import { LOC } from "../data/ids";
import type { Weather } from "../game/types";

describe("WeatherSystem", () => {
  it("is deterministic per (seed, day)", () => {
    for (let d = 0; d < 200; d++) expect(rollWeather(1234, d)).toBe(rollWeather(1234, d));
    const a = Array.from({ length: 100 }, (_, d) => rollWeather(1, d));
    const b = Array.from({ length: 100 }, (_, d) => rollWeather(2, d));
    expect(a).not.toEqual(b);
  });

  it("matches the configured odds over 1000 days and snows only in winter", () => {
    const seasons = ["spring", "summer", "autumn", "winter"] as const;
    for (const season of seasons) {
      const counts: Record<Weather, number> = { sunny: 0, cloudy: 0, rain: 0, snow: 0 };
      let n = 0;
      for (let d = 0; d < 1000 * 4; d++) {
        if (seasonOf(d) !== season) continue;
        counts[rollWeather(99, d)]++;
        n++;
      }
      for (const k of ["sunny", "cloudy", "rain", "snow"] as const) {
        const expected = GameConfig.weather.odds[season][k];
        expect(Math.abs(counts[k] / n - expected), `${season}/${k}`).toBeLessThan(0.05);
        if (expected === 0) expect(counts[k]).toBe(0);
      }
    }
  });

  it("rolls weather for each new day and records the day", () => {
    const c = makeFamilyContent(), s = newGame(c);
    expect(s.weather).toEqual({ day: 0, kind: rollWeather(s.worldSeed, 0) });
    advanceGameTime(s, c, 3 * 1440);
    expect(s.weather).toEqual({ day: 3, kind: rollWeather(s.worldSeed, 3) });
    expect(currentWeather(s)).toBe(s.weather.kind);
  });

  it("worldSeed is deterministic from the name unless a seed is passed", () => {
    const c = makeFamilyContent();
    expect(createNewGame(c, "A", appearance).worldSeed).toBe(createNewGame(c, "A", appearance).worldSeed);
    expect(createNewGame(c, "A", appearance).worldSeed).not.toBe(createNewGame(c, "B", appearance).worldSeed);
    expect(createNewGame(c, "A", appearance, 42).worldSeed).toBe(42);
  });

  it("bad weather drains mood only outdoors", () => {
    const c = makeFamilyContent();
    const mood = (weather: Weather, indoor: boolean) => {
      const s = newGame(c);
      s.weather = { day: 0, kind: weather };
      s.player.needs = { stamina: 80, satiety: 90, mood: 50 };
      if (indoor) s.player.position = { mapId: HOME_IN, x: 1, y: 1, facing: "down" };
      advanceGameTime(s, c, 60);
      return s.player.needs.mood;
    };
    const base = mood("sunny", false);
    expect(mood("rain", false)).toBe(base + GameConfig.weather.badWeatherMoodPerHour);
    expect(mood("snow", false)).toBe(base + GameConfig.weather.badWeatherMoodPerHour);
    expect(mood("cloudy", false)).toBe(base);
    expect(mood("rain", true)).toBe(base);
    expect(isIndoor(c, HOME_IN)).toBe(true);
    expect(isIndoor(c, "map_starter")).toBe(false);
  });

  it("farm shifts are closed on snow days, the cafe is not", () => {
    const c = makeFamilyContent(), s = newGame(c);
    s.gameClock.totalMinutes = 10 * 60;
    standAt(s, c, LOC.farm);
    expect(canStartWork(s, c, FARM_JOB).ok).toBe(true);
    s.weather = { day: 0, kind: "snow" };
    expect(canStartWork(s, c, FARM_JOB)).toEqual({ ok: false, reason: "下雪天農場休息" });
    s.weather = { day: 0, kind: "rain" };
    expect(canStartWork(s, c, FARM_JOB).ok).toBe(true);
    s.weather = { day: 0, kind: "snow" };
    standAt(s, c, LOC.cafe);
    expect(canStartWork(s, c, "job_barista").ok).toBe(true);
  });
});

describe("Lighting", () => {
  const sunny = (m: number) => lightingAt(m, "sunny", false);

  it("night is darker than noon; noon is clear", () => {
    expect(sunny(12 * 60).alpha).toBe(0);
    expect(sunny(2 * 60).alpha).toBeGreaterThan(0.4);
    expect(sunny(22 * 60).alpha).toBeGreaterThan(sunny(12 * 60).alpha);
  });

  it("alpha is monotone through dawn (04-12) and dusk (12-20)", () => {
    let prev = Infinity;
    for (let m = 4 * 60; m <= 12 * 60; m += 5) {
      const a = sunny(m).alpha;
      expect(a).toBeLessThanOrEqual(prev + 1e-9);
      prev = a;
    }
    prev = -Infinity;
    for (let m = 12 * 60; m <= 20 * 60; m += 5) {
      const a = sunny(m).alpha;
      expect(a).toBeGreaterThanOrEqual(prev - 1e-9);
      prev = a;
    }
  });

  it("is continuous across midnight, colours are 0xRRGGBB and lamps follow 18:00-06:00", () => {
    expect(Math.abs(sunny(1439).alpha - sunny(0).alpha)).toBeLessThan(0.01);
    expect(Math.abs(sunny(1440 + 30).alpha - sunny(30).alpha)).toBe(0);
    for (let m = 0; m < 1440; m += 17) {
      const { color, alpha } = sunny(m);
      expect(Number.isInteger(color) && color >= 0 && color <= 0xffffff).toBe(true);
      expect(alpha).toBeGreaterThanOrEqual(0);
      expect(alpha).toBeLessThanOrEqual(1);
    }
    expect(sunny(17 * 60 + 59).lampsOn).toBe(false);
    expect(sunny(18 * 60).lampsOn).toBe(true);
    expect(sunny(3 * 60).lampsOn).toBe(true);
    expect(sunny(6 * 60).lampsOn).toBe(false);
    expect(sunny(12 * 60).lampsOn).toBe(false);
  });

  it("dawn and dusk are orange-ish, rain and snow dim the day", () => {
    const dusk = sunny(18 * 60).color;
    expect((dusk >> 16) & 255).toBeGreaterThan(dusk & 255);
    const dawn = sunny(5 * 60).color;
    expect((dawn >> 16) & 255).toBeGreaterThan(dawn & 255);
    expect(lightingAt(12 * 60, "rain", false).alpha).toBeGreaterThan(0);
    expect(lightingAt(12 * 60, "snow", false).alpha).toBeGreaterThan(0);
    expect(lightingAt(12 * 60, "rain", false).alpha).toBeGreaterThan(lightingAt(12 * 60, "cloudy", false).alpha);
  });

  it("indoor is lighter and ignores weather", () => {
    for (const m of [0, 5 * 60, 12 * 60, 18 * 60, 22 * 60]) {
      expect(lightingAt(m, "sunny", true).alpha).toBeLessThanOrEqual(lightingAt(m, "sunny", false).alpha);
    }
    expect(lightingAt(23 * 60, "sunny", true).alpha).toBeLessThan(lightingAt(23 * 60, "sunny", false).alpha);
    expect(lightingAt(12 * 60, "rain", true)).toEqual(lightingAt(12 * 60, "sunny", true));
  });
});
