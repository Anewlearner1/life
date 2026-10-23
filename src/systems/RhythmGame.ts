import { GameConfig } from "../game/GameConfig";

export type Judgement = "perfect" | "good" | "miss";

function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Deterministic per seed: each cue follows its predecessor after one or two beats. */
export type RhythmConfig = { [K in keyof typeof GameConfig.rhythm]: number };

export function createChart(seed: number, cfg: RhythmConfig = GameConfig.rhythm) {
  const rnd = mulberry32(seed);
  const chart: { id: number; timeMs: number; kind: "tap" }[] = [];
  let t = cfg.travelMs;
  for (let id = 0; id < cfg.cueCount; id++) {
    chart.push({ id, timeMs: t, kind: "tap" });
    t += cfg.cueIntervalMs * (rnd() < 0.5 ? 1 : 2);
  }
  return chart;
}

export function judge(chartTimeMs: number, tapMs: number): Judgement {
  const d = Math.abs(tapMs - chartTimeMs);
  if (d <= GameConfig.rhythm.perfectWindowMs) return "perfect";
  if (d <= GameConfig.rhythm.goodWindowMs) return "good";
  return "miss";
}

export function scoreRun(results: Judgement[]): number {
  if (results.length === 0) return 0;
  const { perfectScore, goodScore } = GameConfig.rhythm;
  const sum = results.reduce((s, r) => s + (r === "perfect" ? perfectScore : r === "good" ? goodScore : 0), 0);
  return sum / results.length / perfectScore;
}
