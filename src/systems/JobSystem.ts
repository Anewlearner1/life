import { GameConfig } from "../game/GameConfig";
import type { ContentDB, GameMinute, GameState, JobDefinition, WorkSession } from "../game/types";
import { addTransaction } from "./EconomySystem";
import { applyNeedDelta } from "./NeedsSystem";
import { clockParts, MINUTES_PER_DAY } from "./TimeSystem";

type Shift = { start: GameMinute; end: GameMinute };

/** Absolute shifts of `job` that start on `day`; a rule whose end <= start runs past midnight. */
function shiftsStartingOn(job: JobDefinition, day: number): Shift[] {
  const weekday = ((day % 7) + 7) % 7;
  return job.shiftRules
    .filter((r) => r.weekday === undefined || r.weekday === weekday)
    .map((r) => {
      const start = day * MINUTES_PER_DAY + r.startMinute;
      const length = (r.endMinute - r.startMinute + MINUTES_PER_DAY) % MINUTES_PER_DAY || MINUTES_PER_DAY;
      return { start, end: start + length };
    });
}

export function shiftAt(job: JobDefinition, total: GameMinute): Shift | null {
  const day = clockParts(total).day;
  const candidates = [day - 1, day].flatMap((d) => shiftsStartingOn(job, d));
  return candidates.find((s) => total >= s.start && total < s.end) ?? null;
}

/** First shift starting strictly after `total`. */
export function nextShift(job: JobDefinition, total: GameMinute): Shift {
  const day = clockParts(total).day;
  for (let d = day; d <= day + 7; d++) {
    const next = shiftsStartingOn(job, d)
      .filter((s) => s.start > total)
      .sort((a, b) => a.start - b.start)[0];
    if (next) return next;
  }
  throw new Error(`job ${job.id} has no upcoming shift`);
}

const sessionIdFor = (jobId: string, shift: Shift) => `${jobId}@${clockParts(shift.start).day}:${shift.start}`;

export function canStartWork(
  state: GameState,
  content: ContentDB,
  jobId: string,
): { ok: boolean; reason?: string; sessionId?: string } {
  const job = content.jobs[jobId];
  if (!job) return { ok: false, reason: "找不到工作" };
  const shift = shiftAt(job, state.gameClock.totalMinutes);
  if (!shift) return { ok: false, reason: "不在班表時段" };
  if (
    GameConfig.weather.farmClosedOnSnow && state.weather.kind === "snow" &&
    (job.minigameId === "mg_rhythm_farm" || job.id.includes("farm"))
  ) {
    return { ok: false, reason: "下雪天農場休息" };
  }
  const loc = content.locations[job.workplaceLocationId];
  const p = state.player.position;
  // Standing on or next to the door counts as being at the workplace.
  if (!loc || p.mapId !== loc.mapId || Math.abs(p.x - loc.door.x) + Math.abs(p.y - loc.door.y) > 1) {
    return { ok: false, reason: "不在工作地點" };
  }
  const sessionId = sessionIdFor(jobId, shift);
  if (state.workSessions.some((s) => s.id === sessionId)) return { ok: false, reason: "這一班已完成" };
  return { ok: true, sessionId };
}

export function performanceFromScore(score: number, stamina: number): number {
  const { performanceMin: lo, performanceMax: hi, lowStaminaPenalty } = GameConfig.job;
  const s = Math.min(1, Math.max(0, score));
  let perf = lo + (hi - lo) * s;
  if (stamina < GameConfig.needs.warnBelow) perf *= lowStaminaPenalty;
  return Math.min(hi, Math.max(lo, perf));
}

/** Pays once per sessionId. Time cost (job.durationMinutes) is advanced by the caller. */
export function completeWork(
  state: GameState,
  content: ContentDB,
  jobId: string,
  sessionId: string,
  score: number,
): WorkSession | null {
  const job = content.jobs[jobId];
  if (!job || state.workSessions.some((s) => s.id === sessionId)) return null;
  const performance = performanceFromScore(score, state.player.needs.stamina);
  const wage = Math.round(job.baseWage * performance * GameConfig.job.attendanceMultiplier);
  if (wage > 0 && !addTransaction(state, { id: `wage:${sessionId}`, amount: wage, category: "income", reason: job.name })) {
    return null;
  }
  applyNeedDelta(state, job.needDelta);
  const session: WorkSession = {
    id: sessionId,
    jobId,
    score: Math.min(1, Math.max(0, score)),
    performanceMultiplier: performance,
    wage,
    completedAtMinute: state.gameClock.totalMinutes,
  };
  state.workSessions.push(session);
  return session;
}
