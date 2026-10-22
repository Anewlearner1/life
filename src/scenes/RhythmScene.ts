import Phaser from "phaser";
import { GameConfig } from "../game/GameConfig";
import type { GameController } from "../game/GameController";
import { createChart, judge, scoreRun, type Judgement } from "../systems/RhythmGame";
import { performanceFromScore } from "../systems/JobSystem";
import { COLOR, makeText } from "../ui/theme";
import { Button, makePanel } from "../ui/widgets";

export type RhythmData = { controller: GameController; jobId: string; sessionId: string; seed: number };

const LEAD_MS = 1000; // quiet time before the first cue starts falling
const TAIL_MS = 700; // pause after the last cue before the result
const MAX_FRAME_MS = 50; // clamp so a stalled tab cannot make every cue miss at once
const EARLY_IGNORE_MS = 380; // taps earlier than this before a cue are ignored (no penalty)

type CueView = { id: number; timeMs: number; img: Phaser.GameObjects.Image; result?: Judgement };

/** Cafe rhythm mini-game: cues fall down a lane to a hit zone; tap anywhere (or Space). */
export class RhythmScene extends Phaser.Scene {
  private d!: RhythmData;
  private chart = createChart(1);
  private cues: CueView[] = [];
  private results: Judgement[] = [];
  private elapsed = -LEAD_MS;
  private lastFrameWall = 0;
  private finished = false;
  private endAt = 0;
  private confirmed = false;

  private laneTop = 0;
  private hitY = 0;
  private laneX = 0;
  private cueScale = 1;
  private judgeImg?: Phaser.GameObjects.Image;
  private statusText?: Phaser.GameObjects.Text;
  private ui: Phaser.GameObjects.GameObject[] = [];
  private resultUi: Phaser.GameObjects.GameObject[] = [];

  constructor() {
    super("Rhythm");
  }

  init(data: RhythmData): void {
    this.d = data;
    this.chart = createChart(data.seed);
    this.cues = [];
    this.results = [];
    this.elapsed = -LEAD_MS;
    this.finished = false;
    this.confirmed = false;
    this.ui = [];
    this.resultUi = [];
  }

  create(): void {
    this.cameras.main.setBackgroundColor(0x181425);
    this.build();
    this.input.on("pointerdown", this.onTap, this);
    this.input.keyboard?.on("keydown-SPACE", this.onTap, this);
    this.scale.on("resize", this.rebuild, this);
    this.events.once(Phaser.Scenes.Events.SHUTDOWN, () => {
      this.input.off("pointerdown", this.onTap, this);
      this.input.keyboard?.off("keydown-SPACE", this.onTap, this);
      this.scale.off("resize", this.rebuild, this);
    });
    this.lastFrameWall = performance.now();
  }

  // ------------------------------------------------------------------ layout
  private build(): void {
    for (const o of this.ui) o.destroy();
    this.ui = [];
    const W = this.scale.width;
    const H = this.scale.height;
    const add = <T extends Phaser.GameObjects.GameObject>(o: T): T => {
      this.ui.push(o);
      return o;
    };
    const job = this.d.controller.content.jobs[this.d.jobId];

    add(makeText(this, W / 2, 18, `${job?.name ?? "打工"}　節奏挑戰`, { size: 20, bold: true, color: COLOR.paper, ox: 0.5 }));
    this.statusText = add(makeText(this, W / 2, 48, "", { size: 15, color: COLOR.gold, ox: 0.5, bold: true }));

    const top = 84;
    const bottom = H - 96;
    const laneLen = Math.max(200, bottom - top);
    const s = Math.min(laneLen / 128, (Math.min(W, 520) * 0.4) / 24);
    this.laneTop = top;
    this.laneX = W / 2;
    this.cueScale = s * 0.8;
    const trackLen = 128 * s;
    const track = add(this.add.image(this.laneX, top + trackLen / 2, "MINI_003_Track").setScale(s).setAngle(90));
    track.setDepth(1);
    const zoneH = 24 * s;
    this.hitY = top + trackLen - zoneH / 2 - 6 * s;
    add(this.add.image(this.laneX, this.hitY, "MINI_003_HitZone").setScale(s).setDepth(2));
    this.judgeImg = add(this.add.image(this.laneX, this.hitY - zoneH, "MINI_004_Judge_Perfect").setScale(Math.max(2, s * 0.9)).setAlpha(0).setDepth(30));

    // decoration on wide screens
    if (W > 700) {
      add(this.add.image(W / 2 - 24 * s - 90, this.hitY - 40, "MINI_006_EspressoMachine").setScale(4));
      add(this.add.image(W / 2 + 24 * s + 90, this.hitY - 20, "MINI_006_Cup").setScale(5));
    }

    add(
      makeText(this, W / 2, H - 52, "點擊畫面任意處（或按空白鍵）", { size: 17, bold: true, color: COLOR.paper, ox: 0.5, oy: 0.5 }),
    );
    // keep cue sprites alive across rebuilds
    for (const c of this.cues) c.img.setScale(this.cueScale).setX(this.laneX);
    if (this.cues.length === 0) {
      for (const ch of this.chart) {
        const img = this.add.image(this.laneX, -100, "MINI_002_RhythmCue_Tap").setScale(this.cueScale).setDepth(10).setVisible(false);
        this.cues.push({ id: ch.id, timeMs: ch.timeMs, img });
      }
    }
    if (this.finished) this.showResult();
  }

  private rebuild(): void {
    this.build();
  }

  // ------------------------------------------------------------------ loop
  update(_t: number, delta: number): void {
    const dt = Math.min(delta, MAX_FRAME_MS);
    this.lastFrameWall = performance.now();
    if (this.finished) return;
    this.elapsed += dt;
    const travel = GameConfig.rhythm.travelMs;
    const total = this.cues.length;
    for (const c of this.cues) {
      if (c.result === undefined && this.elapsed > c.timeMs + GameConfig.rhythm.goodWindowMs) this.resolve(c, "miss");
      const p = 1 - (c.timeMs - this.elapsed) / travel;
      const show = p > 0 && p < 1.2 && (c.result === undefined || c.result === "miss");
      c.img.setVisible(show);
      if (show) {
        c.img.setY(this.laneTop + (this.hitY - this.laneTop) * p);
        c.img.setAlpha(c.result === "miss" ? Math.max(0, 0.6 - (p - 1) * 3) : 1);
      }
    }
    const done = this.results.length;
    this.statusText?.setText(this.elapsed < 0 ? "準備…" : `${done}/${total}　分數 ${Math.round(scoreRun(this.results) * 100)}%`);
    if (done >= total && !this.finished && this.elapsed > (this.cues[total - 1]?.timeMs ?? 0) + TAIL_MS) {
      this.endAt = this.elapsed;
      this.finished = true;
      this.showResult();
    }
  }

  private currentTapMs(): number {
    return this.elapsed + Math.min(MAX_FRAME_MS, performance.now() - this.lastFrameWall);
  }

  /** Public so tests can drive the game deterministically. */
  tap(): void {
    if (this.finished) return;
    const t = this.currentTapMs();
    const target = this.cues.find((c) => c.result === undefined);
    if (!target) return;
    const diff = target.timeMs - t;
    if (diff > EARLY_IGNORE_MS) return; // too early: not aimed at this cue
    this.resolve(target, judge(target.timeMs, t));
  }

  private onTap(): void {
    if (this.elapsed < -LEAD_MS + 150) return;
    this.tap();
  }

  private resolve(c: CueView, r: Judgement): void {
    c.result = r;
    this.results.push(r);
    const key = r === "perfect" ? "MINI_004_Judge_Perfect" : r === "good" ? "MINI_004_Judge_Good" : "MINI_004_Judge_Miss";
    if (this.judgeImg) {
      this.judgeImg.setTexture(key).setAlpha(1).setY(this.hitY - 24 * this.cueScale * 1.4);
      this.tweens.killTweensOf(this.judgeImg);
      this.tweens.add({ targets: this.judgeImg, alpha: 0, y: this.judgeImg.y - 24, duration: 500, delay: 150 });
    }
    if (r !== "miss") {
      c.img.setVisible(false);
      const fx = this.add.image(this.laneX, this.hitY, "MINI_002_RhythmCue_Tap").setScale(this.cueScale).setDepth(20);
      this.tweens.add({ targets: fx, scale: this.cueScale * 1.7, alpha: 0, duration: 220, onComplete: () => fx.destroy() });
    }
  }

  // ------------------------------------------------------------------ result
  private showResult(): void {
    for (const o of this.resultUi) o.destroy();
    this.resultUi = [];
    const W = this.scale.width;
    const H = this.scale.height;
    const st = this.d.controller.getState();
    const job = this.d.controller.content.jobs[this.d.jobId];
    const score = scoreRun(this.results);
    const total = this.cues.length;
    const count = (j: Judgement) => this.results.filter((r) => r === j).length;
    const perf = performanceFromScore(score, st.player.needs.stamina);
    const wage = Math.round(job.baseWage * perf * GameConfig.job.attendanceMultiplier);
    const grade = score >= 0.9 ? "S" : score >= 0.7 ? "A" : score >= 0.5 ? "B" : "C";

    const pw = Math.min(W - 32, 360);
    const ph = 350;
    const px = Math.round((W - pw) / 2);
    const py = Math.round((H - ph) / 2);
    const add = <T extends Phaser.GameObjects.GameObject>(o: T): T => {
      this.resultUi.push(o);
      return o;
    };
    add(this.add.rectangle(0, 0, W, H, 0x000000, 0.6).setOrigin(0, 0).setDepth(100).setInteractive());
    add(makePanel(this, "MINI_005_ResultPanel", px, py, pw, ph, 2, 8).setDepth(101));
    const cx = W / 2;
    const T = (y: number, s: string, o: Parameters<typeof makeText>[4]) => add(makeText(this, cx, py + y, s, { ox: 0.5, ...o }).setDepth(102));
    T(26, "工作完成！", { size: 24, bold: true });
    T(66, `評價 ${grade}`, { size: 36, bold: true, color: COLOR.blue });
    T(116, `分數 ${Math.round(score * 100)}%`, { size: 20, bold: true });
    T(150, `PERFECT ${count("perfect")}　GOOD ${count("good")}　MISS ${count("miss")}　／${total}`, { size: 14, color: COLOR.grey });
    add(this.add.image(cx - 70, py + 205, "UI_002_Money").setScale(2).setDepth(102));
    T(190, `工資 +$${wage}`, { size: 26, bold: true, color: COLOR.ink, ox: 0.3 });
    T(236, `耗時 ${Math.round(job.durationMinutes / 60)} 小時`, { size: 14, color: COLOR.grey });
    const btn = new Button(this, px + 24, py + ph - 24 - 52, {
      w: pw - 48,
      h: 52,
      label: "確定",
      name: "confirm",
      size: 20,
      onClick: () => this.confirm(score),
    });
    btn.container.setDepth(102);
    this.resultUi.push(btn.container);
  }

  /** Pays and advances time exactly once. */
  private confirm(score: number): void {
    if (this.confirmed) return;
    this.confirmed = true;
    this.d.controller.finishWork(this.d.jobId, this.d.sessionId, score);
  }

  /** Test/debug state. */
  debug() {
    return {
      elapsed: this.elapsed,
      finished: this.finished,
      cueTimes: this.cues.map((c) => c.timeMs),
      resolved: this.results.length,
      results: [...this.results],
      endAt: this.endAt,
    };
  }
}
