import type Phaser from "phaser";
import { content as defaultContent } from "../data";
import { GameConfig } from "./GameConfig";
import { createNewGame } from "./GameState";
import type {
  CharacterAppearance,
  Condition,
  ContentDB,
  GameMinute,
  GameState,
  LocationDefinition,
  RelationshipStage,
  TimeMode,
  WorkSession,
  WorldPosition,
} from "./types";
import { SaveService } from "../persistence/SaveService";
import { buildCollisionGrid } from "../scenes/collision";
import type { InteractTarget, WorldBridge } from "../scenes/WorldBridge";
import type { WorldScene } from "../scenes/WorldScene";
import { buyItem, useItem } from "../systems/EconomySystem";
import { availableEvents, fireEvent } from "../systems/EventSystem";
import { canStartWork, completeWork, nextShift, shiftAt } from "../systems/JobSystem";
import { applyHourly, applyNeedDelta } from "../systems/NeedsSystem";
import { changeAffection, getRel, talkTo } from "../systems/RelationshipSystem";
import {
  advanceGameTime,
  clockParts,
  formatClock,
  MINUTES_PER_DAY,
  realMsToGameMinutes,
  setMode,
  type AdvanceResult,
} from "../systems/TimeSystem";
import { listButtons } from "../ui/widgets";

export type ToastKind = "info" | "ok" | "warn" | "unlock" | "error";

export type DialogueSpec = {
  /** NPC id (portrait + name come from content); omit for narration. */
  speakerId?: string;
  /** Used when there is no speaker. */
  name?: string;
  lines: string[];
  mood?: "Neutral" | "Happy" | "Sad";
  onDone?: () => void;
};

export type OpenRequest =
  | { panel: "npc"; npcId: string }
  | { panel: "gift"; npcId: string }
  | { panel: "shop"; tab?: "shop" | "bag" }
  | { panel: "home"; locationId: string }
  | { panel: "rest"; locationId: string }
  | { panel: "work"; locationId: string }
  | { panel: "locked"; locationId: string; hint: string };

type EventMap = {
  toast: [string, ToastKind];
  banner: [string];
  dialogue: [DialogueSpec];
  open: [OpenRequest];
  saved: [];
  mode: [TimeMode];
};

class Emitter<E extends Record<string, unknown[]>> {
  private map = new Map<keyof E, Set<(...a: any[]) => void>>();
  on<K extends keyof E>(k: K, fn: (...a: E[K]) => void): () => void {
    const set = this.map.get(k) ?? new Set();
    set.add(fn);
    this.map.set(k, set);
    return () => set.delete(fn);
  }
  emit<K extends keyof E>(k: K, ...a: E[K]): void {
    for (const fn of [...(this.map.get(k) ?? [])]) fn(...a);
  }
}

/** Items that can be given to NPCs. */
export const GIFT_ITEM_IDS = ["item_flower", "item_gift"];

/** Resting restores a little on top of the hour that passes. */
const REST_MINUTES = 60;
const REST_BONUS = { stamina: 12, mood: 4 };

export const STAGE_LABEL: Record<RelationshipStage, string> = {
  stranger: "陌生",
  acquaintance: "熟識",
  close: "親密",
  partner: "伴侶",
  spouse: "配偶",
};

const NEED_LABEL = { stamina: "體力", satiety: "飽足", mood: "心情" } as const;
const pad = (n: number) => String(n).padStart(2, "0");
export const hhmm = (total: GameMinute) => {
  const p = clockParts(total);
  return `${pad(p.hour)}:${pad(p.minute)}`;
};

export class GameController implements WorldBridge {
  state: GameState | null = null;
  readonly content: ContentDB;
  readonly events = new Emitter<EventMap>();
  game?: Phaser.Game;
  /** Set by the UI while any modal (menu / dialogue) is open. */
  modalOpen = false;
  rhythmActive = false;

  private acc = 0;
  private saves: SaveService;
  private saveChain: Promise<unknown> = Promise.resolve();
  private queue: DialogueSpec[] = [];
  private current: DialogueSpec | null = null;
  private deferred: (() => void)[] = [];
  private peeked: GameState | null = null;

  constructor(content: ContentDB = defaultContent, saves: SaveService = new SaveService()) {
    this.content = content;
    this.saves = saves;
    if (typeof document !== "undefined") {
      document.addEventListener("visibilitychange", () => {
        if (document.hidden) void this.save(false);
      });
      window.addEventListener("pagehide", () => void this.save(false));
    }
  }

  attachGame(game: Phaser.Game): void {
    this.game = game;
  }

  get world(): WorldScene | undefined {
    return this.game?.scene.getScene("World") as WorldScene | undefined;
  }

  /** Test helper: live UI buttons with their centre in canvas pixels. */
  debugButtons() {
    return listButtons();
  }

  // ------------------------------------------------------------------ WorldBridge
  getState(): GameState {
    if (!this.state) throw new Error("GameController: no game in progress");
    return this.state;
  }
  getContent(): ContentDB {
    return this.content;
  }
  isInputBlocked(): boolean {
    return !this.state || this.modalOpen || this.rhythmActive || this.queue.length > 0 || this.current !== null;
  }
  onPlayerStep(pos: WorldPosition): void {
    if (!this.state) return;
    this.state.player.position = pos;
    this.state.currentMapId = pos.mapId;
  }
  onInteract(target: InteractTarget): void {
    if (!this.state) return;
    void this.save(false);
    if (target.kind === "npc") {
      this.events.emit("open", { panel: "npc", npcId: target.id });
      return;
    }
    this.enterLocation(target.id);
  }

  // ------------------------------------------------------------------ new / load / save
  /** Loads the save (if any) without applying it; used by the title screen. */
  async peekSave(): Promise<GameState | null> {
    try {
      this.peeked = await this.saves.load();
    } catch (e) {
      console.warn("[save] unreadable save ignored", e);
      this.peeked = null;
    }
    return this.peeked;
  }

  /** Continue from the save. Game time is never advanced for the time spent offline (AC-05). */
  async loadGame(): Promise<boolean> {
    const s = this.peeked ?? (await this.peekSave());
    if (!s) return false;
    this.state = s;
    this.acc = 0;
    return true;
  }

  newGame(name: string, appearance: CharacterAppearance): void {
    this.state = createNewGame(this.content, name, appearance);
    this.acc = 0;
    void this.save(false);
  }

  /** Leave the create scene and show the world + UI overlay. */
  startWorld(): void {
    const g = this.game;
    if (!g) throw new Error("GameController: attachGame() first");
    g.scene.stop("Create");
    g.scene.start("World", { bridge: this });
    g.scene.start("UI", { controller: this });
  }

  save(manual = false): Promise<boolean> {
    if (!this.state) return Promise.resolve(false);
    const run = async () => {
      try {
        await this.saves.save(this.state as GameState);
        if (manual) this.events.emit("saved");
        return true;
      } catch (e) {
        console.warn("[save] failed", e);
        this.toast("存檔失敗", "error");
        return false;
      }
    };
    const p = this.saveChain.then(run);
    this.saveChain = p.catch(() => undefined);
    return p;
  }

  // ------------------------------------------------------------------ clock
  setTimeMode(mode: TimeMode): void {
    if (!this.state) return;
    setMode(this.state, mode);
    this.events.emit("mode", mode);
  }

  private clockPaused(): boolean {
    return !this.state || this.modalOpen || this.rhythmActive || (typeof document !== "undefined" && document.hidden);
  }

  /** Called every frame by the UI scene. Fractional minutes accumulate; whole minutes go through advanceGameTime. */
  tick(deltaMs: number): void {
    if (!this.state || this.clockPaused()) return;
    this.acc += realMsToGameMinutes(this.state.gameClock.mode, Math.min(deltaMs, 500));
    const whole = Math.floor(this.acc);
    if (whole > 0) {
      this.acc -= whole;
      this.advance(whole);
    }
  }

  /** The only place the controller moves game time. */
  advance(minutes: number, opts: { skipNeedWarnings?: boolean } = {}): AdvanceResult {
    const res = advanceGameTime(this.getState(), this.content, minutes);
    this.route(res, opts);
    return res;
  }

  private route(res: AdvanceResult, opts: { skipNeedWarnings?: boolean } = {}): void {
    for (const m of res.messages) {
      const warn = m.endsWith("過低");
      if (warn && opts.skipNeedWarnings) continue;
      this.toast(m, warn ? "warn" : "info");
    }
    for (const id of res.unlockedMapIds) this.events.emit("banner", `新區域開放：${this.content.maps[id]?.name ?? id}`);
    for (const id of res.firedEventIds) {
      const ev = this.content.events[id];
      if (ev && ev.lines.length) {
        this.showDialogue({ speakerId: ev.npcId, name: "旁白", lines: ev.lines, mood: "Happy" });
      }
    }
    if (res.saveRequested) void this.save(false);
  }

  toast(text: string, kind: ToastKind = "info"): void {
    this.events.emit("toast", text, kind);
  }

  // ------------------------------------------------------------------ dialogue queue
  showDialogue(spec: DialogueSpec): void {
    this.queue.push(spec);
    if (!this.current) this.pump();
  }

  private pump(): void {
    const next = this.queue.shift();
    if (!next) {
      this.current = null;
      const cbs = this.deferred.splice(0);
      for (const cb of cbs) cb();
      return;
    }
    this.current = next;
    this.events.emit("dialogue", next);
  }

  /** UI calls this when the player finished reading the current dialogue. */
  dialogueDone(): void {
    const done = this.current?.onDone;
    if (done) this.deferred.push(done);
    this.pump();
  }

  // ------------------------------------------------------------------ events helper
  private playEvent(eventId: string, onDone?: () => void): boolean {
    const st = this.getState();
    const ev = this.content.events[eventId];
    const r = fireEvent(st, this.content, eventId);
    if (!r.ok || !ev) {
      onDone?.();
      return false;
    }
    for (const m of r.messages) this.toast(m, "ok");
    if (r.lines.length) {
      this.showDialogue({ speakerId: ev.npcId, name: "旁白", lines: r.lines, mood: "Happy", onDone });
    } else onDone?.();
    if (ev.timeCostMinutes) this.advance(ev.timeCostMinutes);
    return true;
  }

  // ------------------------------------------------------------------ NPCs
  npcName(id: string): string {
    return this.content.npcs[id]?.name ?? id;
  }

  talk(npcId: string): void {
    const st = this.getState();
    const back = () => this.events.emit("open", { panel: "npc", npcId });
    const r = talkTo(st, this.content, npcId);
    if (r.event) {
      this.playEvent(r.event.id, back);
      return;
    }
    if (r.affectionGained > 0) this.toast(`${this.npcName(npcId)} 好感度 +${r.affectionGained}`, "ok");
    else this.toast("剛聊過天，好感度暫時沒有增加", "info");
    this.showDialogue({
      speakerId: npcId,
      lines: [r.line.text],
      mood: r.affectionGained > 0 ? "Happy" : "Neutral",
      onDone: back,
    });
  }

  giftables(): { id: string; name: string; count: number; icon: string }[] {
    const st = this.getState();
    return GIFT_ITEM_IDS.filter((id) => (st.inventory[id] ?? 0) > 0 && this.content.items[id]).map((id) => ({
      id,
      name: this.content.items[id].name,
      count: st.inventory[id],
      icon: iconKey(this.content.items[id].iconAsset),
    }));
  }

  giveGift(npcId: string, itemId: string): boolean {
    const st = this.getState();
    const item = this.content.items[itemId];
    if (!item || !GIFT_ITEM_IDS.includes(itemId) || (st.inventory[itemId] ?? 0) <= 0) return false;
    st.inventory[itemId] -= 1;
    const before = getRel(st, npcId).affection;
    const rel = changeAffection(st, npcId, GameConfig.relationship.giftAffection);
    this.toast(`送出${item.name}，好感度 +${rel.affection - before}`, "ok");
    this.showDialogue({
      speakerId: npcId,
      lines: [`哇，是${item.name}！謝謝你，我很開心。`],
      mood: "Happy",
      onDone: () => this.events.emit("open", { panel: "npc", npcId }),
    });
    return true;
  }

  // ------------------------------------------------------------------ locations
  private enterLocation(locationId: string): void {
    const loc = this.content.locations[locationId];
    if (!loc) return;
    const st = this.getState();
    if (loc.type === "gate") {
      const target = loc.targetMapId ?? "";
      if (!this.mapOpen(target)) {
        this.events.emit("open", { panel: "locked", locationId, hint: this.unlockHint(target) });
        return;
      }
    }
    const proceed = () => this.openLocation(loc);
    const evs = availableEvents(st, this.content, "enterLocation", { locationId });
    if (!evs.length) return proceed();
    evs.forEach((e, i) => this.playEvent(e.id, i === evs.length - 1 ? proceed : undefined));
  }

  private openLocation(loc: LocationDefinition): void {
    switch (loc.type) {
      case "home":
        this.events.emit("open", { panel: "home", locationId: loc.id });
        break;
      case "shop":
        this.events.emit("open", { panel: "shop", tab: "shop" });
        break;
      case "workplace":
        this.events.emit("open", { panel: "work", locationId: loc.id });
        break;
      case "social":
        this.events.emit("open", { panel: "rest", locationId: loc.id });
        break;
      case "gate":
        this.travel(loc.id);
        break;
    }
  }

  /** Maps without an unlock condition (interiors, town) are always open; others once unlocked. */
  private mapOpen(mapId: string): boolean {
    const m = this.content.maps[mapId];
    return !!m && (!m.unlockConditionId || this.getState().unlockedMapIds.includes(mapId));
  }

  unlockHint(mapId: string): string {
    const cid = this.content.maps[mapId]?.unlockConditionId;
    const cond = cid ? this.content.conditions[cid] : undefined;
    if (!cond) return "尚未開放";
    return cond.all.map((c) => this.describeCondition(c)).join("、") + "後開放";
  }

  private describeCondition(c: Condition): string {
    switch (c.type) {
      case "shiftsWorked":
        return `完成${c.atLeast}次打工`;
      case "money":
        return `擁有${c.atLeast}元`;
      case "day":
        return `到第${c.atLeast}天`;
      case "affection":
        return `與${this.npcName(c.npcId)}的好感度達${c.atLeast}`;
      case "stage":
        return `與${this.npcName(c.npcId)}成為${STAGE_LABEL[c.stage]}`;
      case "eventCompleted":
        return "完成特定事件";
      case "noOtherPartner":
        return "目前沒有其他伴侶";
      case "hasItem":
        return `持有${this.content.items[c.itemId]?.name ?? c.itemId}`;
      case "marriedDays":
        return `結婚滿${c.atLeast}天`;
      case "childrenAtMost":
        return `孩子不超過${c.count}位`;
      case "notPregnant":
        return "目前沒有待產";
    }
  }

  /** Walkable tile next to a gate door, on the map-interior side. */
  private arrivalTile(map: { id: string; width: number; height: number }, door: { x: number; y: number }) {
    const m = this.content.maps[map.id];
    const grid = buildCollisionGrid(m);
    const dx = door.x === 0 ? 1 : door.x === m.width - 1 ? -1 : 0;
    // Doors inside the map (building entrances): arrive on the tile below the door.
    const dy = door.y === 0 ? 1 : door.y === m.height - 1 ? -1 : dx === 0 ? 1 : 0;
    const cands = [
      { x: door.x + dx, y: door.y + dy },
      { x: door.x + 1, y: door.y },
      { x: door.x - 1, y: door.y },
      { x: door.x, y: door.y + 1 },
      { x: door.x, y: door.y - 1 },
    ];
    const ok = cands.find((c) => c.x >= 0 && c.y >= 0 && c.x < m.width && c.y < m.height && !grid[c.y][c.x]);
    return ok ?? m.spawn;
  }

  travel(gateId: string): void {
    const st = this.getState();
    const gate = this.content.locations[gateId];
    const targetId = gate?.targetMapId;
    const target = targetId ? this.content.maps[targetId] : undefined;
    if (!gate || !target || !this.mapOpen(target.id)) return;
    const back = Object.values(this.content.locations).find(
      (l) => l.mapId === target.id && l.type === "gate" && l.targetMapId === gate.mapId,
    );
    const tile = back ? this.arrivalTile(target, back.door) : target.spawn;
    const facing = !back
      ? "down"
      : back.door.x === 0
        ? "right"
        : back.door.x === target.width - 1
          ? "left"
          : back.door.y === target.height - 1
            ? "up"
            : "down";
    const pos: WorldPosition = { mapId: target.id, x: tile.x, y: tile.y, facing };
    st.currentMapId = target.id;
    st.player.position = pos;
    this.world?.loadMap(target.id, pos);
    this.toast(`前往：${target.name}`, "info");
    void this.save(false);
  }

  // ------------------------------------------------------------------ home
  sleep(): void {
    const st = this.getState();
    const now = st.gameClock.totalMinutes;
    const day = clockParts(now).day;
    let target = day * MINUTES_PER_DAY + GameConfig.time.wakeMinuteOfDay;
    if (target <= now) target += MINUTES_PER_DAY;
    const minutes = Math.ceil(target - now);
    const before = { ...st.player.needs };
    const res = advanceGameTime(st, this.content, minutes);
    // advanceGameTime applied awake drain; replace it with the sleeping rates.
    Object.assign(st.player.needs, before);
    applyHourly(st, minutes / 60, true);
    this.route(res, { skipNeedWarnings: true });
    this.toast(`睡到${formatClock(st.gameClock.totalMinutes)}，體力 ${Math.round(before.stamina)}→${Math.round(st.player.needs.stamina)}`, "ok");
    void this.save(false);
  }

  rest(): void {
    const st = this.getState();
    this.advance(REST_MINUTES);
    applyNeedDelta(st, REST_BONUS);
    this.toast("休息了一個小時，體力和心情恢復了一些", "ok");
  }

  wakeTimeLabel(): string {
    const w = GameConfig.time.wakeMinuteOfDay;
    return `${pad(Math.floor(w / 60))}:${pad(w % 60)}`;
  }

  // ------------------------------------------------------------------ shop
  buy(itemId: string): boolean {
    const st = this.getState();
    const item = this.content.items[itemId];
    const r = buyItem(st, this.content, itemId);
    if (r.ok) this.toast(`購買${item.name}  -$${item.price}`, "ok");
    else this.toast(r.reason ?? "無法購買", "warn");
    return r.ok;
  }

  eat(itemId: string): boolean {
    const st = this.getState();
    const item = this.content.items[itemId];
    if (!item?.useEffect) return false;
    const r = useItem(st, this.content, itemId);
    if (!r.ok) return false;
    const fx = Object.entries(item.useEffect)
      .map(([k, v]) => `${NEED_LABEL[k as keyof typeof NEED_LABEL]}${(v as number) >= 0 ? "+" : ""}${v}`)
      .join(" ");
    this.toast(`使用${item.name}：${fx}`, "ok");
    if (r.minutes > 0) this.advance(r.minutes);
    return true;
  }

  // ------------------------------------------------------------------ work
  jobAt(locationId: string) {
    return Object.values(this.content.jobs).find((j) => j.workplaceLocationId === locationId);
  }

  workInfo(locationId: string) {
    const st = this.getState();
    const job = this.jobAt(locationId);
    if (!job) return null;
    const now = st.gameClock.totalMinutes;
    const cur = shiftAt(job, now);
    const next = nextShift(job, now);
    return {
      job,
      current: cur ? `${hhmm(cur.start)}–${hhmm(cur.end)}` : null,
      next: `${formatClock(next.start)}–${hhmm(next.end)}`,
      check: canStartWork(st, this.content, job.id),
    };
  }

  /** Opens the rhythm mini-game (AC-07); the clock stays paused until the result is confirmed. */
  startWork(locationId: string): void {
    const st = this.getState();
    const job = this.jobAt(locationId);
    if (!job || !this.game) return;
    const chk = canStartWork(st, this.content, job.id);
    if (!chk.ok || !chk.sessionId) {
      this.toast(chk.reason ?? "現在不能工作", "warn");
      return;
    }
    this.rhythmActive = true;
    this.game.scene.sleep("UI");
    this.game.scene.start("Rhythm", {
      controller: this,
      jobId: job.id,
      sessionId: chk.sessionId,
      seed: Math.floor(st.gameClock.totalMinutes) + st.workSessions.length * 7919,
    });
  }

  /** Called once by the result panel. Pays (idempotent per session) and advances the shift duration. */
  finishWork(jobId: string, sessionId: string, score: number): WorkSession | null {
    const st = this.getState();
    const job = this.content.jobs[jobId];
    const session = completeWork(st, this.content, jobId, sessionId, score);
    this.rhythmActive = false;
    if (this.game) {
      this.game.scene.stop("Rhythm");
      this.game.scene.wake("UI");
    }
    if (session && job) {
      this.toast(`工資 +$${session.wage}`, "ok");
      this.advance(job.durationMinutes);
    } else {
      this.toast("這一班已經結算過了", "warn");
    }
    void this.save(false);
    return session;
  }
}

export const iconKey = (asset: string): string => asset.slice(asset.lastIndexOf("/") + 1).replace(/_v01\.png$/, "");
