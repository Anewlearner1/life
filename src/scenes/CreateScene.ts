import Phaser from "phaser";
import type { GameController } from "../game/GameController";
import type { CharacterAppearance, GameState } from "../game/types";
import { formatClock } from "../systems/TimeSystem";
import { COLOR, makeText, TOUCH } from "../ui/theme";
import { CHAR_FRAME, playerSpriteKeyFor } from "./BootScene";
import { Button, makePanel } from "../ui/widgets";

export const HAIRS = [
  { id: "hair_short", name: "短髮" },
  { id: "hair_bob", name: "鮑伯頭" },
  { id: "hair_buzz", name: "平頭" },
  { id: "hair_long", name: "長髮" },
  { id: "hair_ponytail", name: "馬尾" },
  { id: "hair_spiky", name: "刺蝟頭" },
];
export const OUTFITS = [
  { id: "outfit1", name: "吊帶褲" },
  { id: "outfit2", name: "咖啡色背心" },
];

type Mode = "menu" | "create";

/** Title screen: continue / new game, then name + hair + outfit (AC-01). */
export class CreateScene extends Phaser.Scene {
  private controller!: GameController;
  private mode: Mode = "create";
  private hasSave = false;
  private saved: GameState | null = null;
  private name = "";
  private hair = 0;
  private outfit = 0;
  private objs: Phaser.GameObjects.GameObject[] = [];
  private input_?: HTMLInputElement;
  private busy = false;
  private bannerH = 0;

  constructor() {
    super("Create");
  }

  init(data: { controller: GameController }): void {
    this.controller = data.controller;
    this.objs = [];
    this.busy = false;
    this.name = "";
  }

  create(): void {
    this.cameras.main.setBackgroundColor(0x181425);
    this.scale.on("resize", this.build, this);
    this.events.once(Phaser.Scenes.Events.SHUTDOWN, () => {
      this.scale.off("resize", this.build, this);
      this.removeInput();
    });
    this.mode = "create";
    this.build();
    void this.controller.peekSave().then((s) => {
      if (!this.scene.isActive()) return;
      this.saved = s;
      this.hasSave = !!s;
      if (s) this.mode = "menu";
      this.build();
    });
  }

  private clear(): void {
    for (const o of this.objs) o.destroy();
    this.objs = [];
  }

  private removeInput(): void {
    if (this.input_) {
      this.name = this.input_.value;
      this.input_.remove();
      this.input_ = undefined;
    }
  }

  private add_<T extends Phaser.GameObjects.GameObject>(o: T): T {
    this.objs.push(o);
    return o;
  }

  private build(): void {
    // Keep the DOM input across rebuilds (a soft keyboard resizes the viewport; recreating it would drop focus).
    if (this.mode !== "create") this.removeInput();
    this.clear();
    const W = this.scale.width;
    const H = this.scale.height;
    // Concept key-art banner (1024x190, painted title text included) at the top, scaled to fit the width.
    const bs = Math.min(W / 1024, (H * 0.3) / 190);
    this.bannerH = Math.round(190 * bs);
    this.add_(this.add.image(W / 2, 0, "UI_000_TitleBanner").setOrigin(0.5, 0).setScale(bs));
    if (this.mode === "menu") this.buildMenu(W, H);
    else this.buildCreate(W, H);
  }

  // ------------------------------------------------------------------ title menu
  private buildMenu(W: number, H: number): void {
    const pw = Math.min(W - 32, 360);
    const ph = 270;
    const px = Math.round((W - pw) / 2);
    const py = Math.round(Math.max(this.bannerH + 16, (H - ph) / 2));
    this.add_(makePanel(this, "UI_010_CreatePanel", px, py, pw, ph, 2, 8));
    const s = this.saved;
    const info = s ? `${s.player.name}　${formatClock(s.gameClock.totalMinutes)}　$${s.player.money}` : "";
    this.add_(makeText(this, W / 2, py + 28, "已有存檔", { size: 20, bold: true, ox: 0.5 }));
    this.add_(makeText(this, W / 2, py + 62, info, { size: 15, color: COLOR.grey, ox: 0.5 }));
    const b1 = new Button(this, px + 24, py + 104, {
      w: pw - 48,
      h: 56,
      label: "繼續遊戲",
      name: "continue",
      size: 20,
      icon: "UI_012_Load",
      onClick: () => void this.doContinue(),
    });
    const b2 = new Button(this, px + 24, py + 172, { w: pw - 48, h: 56, label: "新遊戲", name: "new", size: 20, onClick: () => this.toCreate() });
    this.add_(b1.container);
    this.add_(b2.container);
  }

  private async doContinue(): Promise<void> {
    if (this.busy) return;
    this.busy = true;
    const ok = await this.controller.loadGame();
    if (ok) this.controller.startWorld();
    else {
      this.busy = false;
      this.hasSave = false;
      this.mode = "create";
      this.build();
    }
  }

  private toCreate(): void {
    this.mode = "create";
    this.build();
  }

  // ------------------------------------------------------------------ create form
  private buildCreate(W: number, H: number): void {
    const compact = H < 700;
    const pw = Math.min(W - 24, 420);
    const iw = pw - 48;
    const previewScale = compact ? 3 : 5;
    const previewH = CHAR_FRAME.frameHeight * previewScale;
    const top = this.bannerH + 28;
    const ph = 24 + 22 + 6 + 48 + 14 + previewH + 14 + 52 + 8 + 52 + 16 + 56 + (this.hasSave ? 60 : 0) + 24;
    const px = Math.round((W - pw) / 2);
    const py = Math.round(Math.max(top - 20, Math.min((H - ph) / 2 + 40, H - ph - 8)));
    this.add_(makePanel(this, "UI_010_CreatePanel", px, py, pw, ph, 2, 8));

    let y = py + 24;
    this.add_(makeText(this, px + 24, y, "你的名字", { size: 16, bold: true }));
    y += 22 + 6;
    this.mountInput(px + 24, y, iw, 48);
    y += 48 + 14;

    // preview
    const cx = W / 2;
    const feetY = y + previewH;
    const outfit = OUTFITS[this.outfit];
    const hair = HAIRS[this.hair];
    this.add_(this.add.rectangle(cx, y + previewH / 2, previewScale * CHAR_FRAME.frameWidth + 24, previewH + 8, 0xd8d2c4, 1).setOrigin(0.5));
    const previewKey = `${playerSpriteKeyFor(outfit.id, hair.id)}_idle_down`;
    this.add_(this.add.image(cx, feetY, previewKey, 0).setOrigin(0.5, 1).setScale(previewScale));
    y += previewH + 14;

    y = this.selector(px + 24, y, iw, "髮型", hair.name, `${this.hair + 1}/${HAIRS.length}`, (d) => this.cycle("hair", d), "hair");
    y += 8;
    y = this.selector(px + 24, y, iw, "服裝", outfit.name, `${this.outfit + 1}/${OUTFITS.length}`, (d) => this.cycle("outfit", d), "outfit");
    y += 16;

    const start = new Button(this, px + 24, y, {
      w: iw,
      h: 56,
      label: "開始",
      name: "start",
      size: 20,
      enabled: this.name.trim().length > 0,
      onClick: () => this.start(),
    });
    this.add_(start.container);
    this.startBtn = start;
    y += 60;
    if (this.hasSave) {
      const back = new Button(this, px + 24, y, { w: iw, h: 52, label: "返回（繼續舊存檔）", name: "back", size: 16, onClick: () => ((this.mode = "menu"), this.build()) });
      this.add_(back.container);
    }
  }

  private startBtn?: Button;

  private selector(x: number, y: number, w: number, _label: string, value: string, idx: string, onStep: (d: number) => void, tag: string): number {
    const bw = TOUCH + 4;
    const l = new Button(this, x, y, { w: bw, h: 52, icon: "UI_010_Arrow_Left", name: `${tag}_prev`, onClick: () => onStep(-1) });
    const r = new Button(this, x + w - bw, y, { w: bw, h: 52, icon: "UI_010_Arrow_Right", name: `${tag}_next`, onClick: () => onStep(1) });
    this.add_(l.container);
    this.add_(r.container);
    this.add_(makeText(this, x + w / 2, y + 16, `${_label}：${value}`, { size: 17, bold: true, ox: 0.5, oy: 0.5 }));
    this.add_(makeText(this, x + w / 2, y + 38, idx, { size: 12, color: COLOR.grey, ox: 0.5, oy: 0.5 }));
    return y + 52;
  }

  private cycle(what: "hair" | "outfit", d: number): void {
    if (what === "hair") this.hair = (this.hair + d + HAIRS.length) % HAIRS.length;
    else this.outfit = (this.outfit + d + OUTFITS.length) % OUTFITS.length;
    this.build();
  }

  private mountInput(x: number, y: number, w: number, h: number): void {
    if (this.input_) {
      Object.assign(this.input_.style, { left: `${x}px`, top: `${y}px`, width: `${w}px`, height: `${h}px` });
      return;
    }
    const el = document.createElement("input");
    el.type = "text";
    el.maxLength = 8;
    el.placeholder = "輸入名字（最多 8 字）";
    el.value = this.name;
    el.setAttribute("aria-label", "角色名字");
    el.autocomplete = "off";
    Object.assign(el.style, {
      position: "fixed",
      left: `${x}px`,
      top: `${y}px`,
      width: `${w}px`,
      height: `${h}px`,
      boxSizing: "border-box",
      padding: "0 12px",
      font: `bold 18px "Noto Sans TC","PingFang TC","Microsoft JhengHei","WenQuanYi Zen Hei",system-ui,sans-serif`,
      color: COLOR.ink,
      background: COLOR.paper,
      border: `3px solid ${COLOR.blue}`,
      borderRadius: "4px",
      outline: "none",
      zIndex: "10",
    } as Partial<CSSStyleDeclaration>);
    el.addEventListener("input", () => {
      this.name = el.value;
      this.startBtn?.setEnabled(el.value.trim().length > 0);
    });
    el.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && el.value.trim()) this.start();
    });
    document.body.appendChild(el);
    this.input_ = el;
  }

  private start(): void {
    if (this.busy) return;
    const name = (this.input_?.value ?? this.name).trim();
    if (!name) return;
    this.busy = true;
    const appearance: CharacterAppearance = {
      bodyId: "body_default",
      hairId: HAIRS[this.hair].id,
      outfitId: OUTFITS[this.outfit].id,
      accessoryIds: [],
    };
    this.removeInput();
    this.controller.newGame(name, appearance);
    this.controller.startWorld();
  }
}
