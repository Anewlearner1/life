import "fake-indexeddb/auto";
import { describe, expect, it } from "vitest";
import { COND, JOB, LOC, MAP } from "../data/ids";
import { GameConfig } from "../game/GameConfig";
import { IndexedDBStorage, MemoryStorage, SaveService } from "../persistence/SaveService";
import { buyItem, useItem } from "../systems/EconomySystem";
import { checkCondition, fireEvent } from "../systems/EventSystem";
import { canStartWork, completeWork } from "../systems/JobSystem";
import { createChart, judge, scoreRun } from "../systems/RhythmGame";
import { talkTo } from "../systems/RelationshipSystem";
import { advanceGameTime, realMsToGameMinutes } from "../systems/TimeSystem";
import { ARTIST, makeContent, newGame, standAt } from "./fixtures";

describe("full loop", () => {
  it.each([["memory", () => new MemoryStorage()], ["indexeddb", () => new IndexedDBStorage()]] as const)(
    "new game -> shift -> food -> partner -> rural -> save/load (%s)",
    async (_n, makeStorage) => {
      const c = makeContent(), s = newGame(c);
      expect(s.unlockedMapIds).toEqual([MAP.starter]);

      // Work the 09:00 shift.
      advanceGameTime(s, c, realMsToGameMinutes("fast", 15_000)); // 15s x 4 = 60 game-min -> 09:00
      standAt(s, c, LOC.cafe);
      const start = canStartWork(s, c, JOB.barista);
      expect(start.ok).toBe(true);
      const chart = createChart(7);
      const score = scoreRun(chart.map((cue) => judge(cue.timeMs, cue.timeMs + 50)));
      const money = s.player.money;
      const session = completeWork(s, c, JOB.barista, start.sessionId!, score)!;
      advanceGameTime(s, c, c.jobs[JOB.barista].durationMinutes);
      expect(s.player.money).toBe(money + session.wage);
      expect(completeWork(s, c, JOB.barista, start.sessionId!, score)).toBeNull();
      expect(canStartWork(s, c, JOB.barista).ok).toBe(false);

      // Buy and eat.
      const satiety = s.player.needs.satiety;
      expect(buyItem(s, c, "sandwich").ok).toBe(true);
      const used = useItem(s, c, "sandwich");
      advanceGameTime(s, c, used.minutes);
      expect(s.player.needs.satiety).toBeGreaterThan(satiety - 20);

      // Talk until partner, through the 3-event chain.
      const fired: string[] = [];
      for (let i = 0; i < 100 && s.relationships[ARTIST].stage !== "partner"; i++) {
        advanceGameTime(s, c, GameConfig.relationship.talkCooldownMinutes);
        const t = talkTo(s, c, ARTIST);
        if (t.event) {
          expect(fireEvent(s, c, t.event.id).ok).toBe(true);
          fired.push(t.event.id);
        }
      }
      expect(fired).toEqual(["ev_intro", "ev_date", "ev_confess"]);
      expect(s.relationships[ARTIST].stage).toBe("partner");

      // Rural unlocks via day processing / unlock check.
      expect(checkCondition(s, c, COND.unlockRural)).toBe(true);
      const r = advanceGameTime(s, c, 1);
      expect(s.unlockedMapIds).toContain(MAP.rural);
      expect(r.unlockedMapIds.concat(s.unlockedMapIds)).toContain(MAP.rural);

      // Save and load.
      const svc = new SaveService(makeStorage());
      await svc.save(s);
      expect(await svc.load()).toEqual(s);
    },
  );
});
