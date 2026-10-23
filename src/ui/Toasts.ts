import Phaser from "phaser";
import type { ToastKind } from "../game/GameController";
import { COLOR, makeText } from "./theme";

const ICON: Record<ToastKind, string> = {
  info: "UI_008_Notice_Info",
  ok: "UI_008_Notice_SaveOk",
  warn: "UI_008_Notice_Warning",
  unlock: "UI_008_Notice_Unlock",
  error: "UI_012_SaveError",
};

const MAX = 3;
const LIFE = 2600;

type Item = { c: Phaser.GameObjects.Container; h: number; born: number };

/** Stacked, non-interactive toasts under the HUD (taps pass through to the world). */
export class Toasts {
  private items: Item[] = [];
  private top = 120;
  private centerX = 0;
  private width = 0;

  constructor(private scene: Phaser.Scene) {}

  layout(centerX: number, top: number, width: number): void {
    this.centerX = centerX;
    this.top = top;
    this.width = width;
    this.restack();
  }

  show(text: string, kind: ToastKind = "info"): void {
    const maxW = Math.min(this.width, 420);
    const label = makeText(this.scene, 0, 0, text, { size: 15, color: COLOR.paper, bold: true, wrap: maxW - 64 });
    const w = Math.min(maxW, Math.ceil(label.width) + 64);
    const h = Math.max(44, Math.ceil(label.height) + 20);
    const bg = this.scene.add.graphics();
    bg.fillStyle(COLOR.inkHex, 0.94).fillRoundedRect(0, 0, w, h, 6);
    bg.lineStyle(2, kind === "warn" || kind === "error" ? 0xe43b44 : kind === "unlock" ? 0xfee761 : 0x4078d0, 1).strokeRoundedRect(1, 1, w - 2, h - 2, 6);
    const icon = this.scene.add.image(8 + 16, h / 2, ICON[kind]).setScale(1.5);
    label.setPosition(48, h / 2).setOrigin(0, 0.5);
    const c = this.scene.add.container(0, 0, [bg, icon, label]).setDepth(200).setSize(w, h);
    (c as Phaser.GameObjects.Container & { toastW: number }).toastW = w;
    this.items.push({ c, h, born: this.scene.time.now });
    while (this.items.length > MAX) this.drop(this.items[0]);
    this.restack();
    c.setAlpha(0);
    this.scene.tweens.add({ targets: c, alpha: 1, duration: 120 });
  }

  update(): void {
    const now = this.scene.time.now;
    for (const it of [...this.items]) {
      const age = now - it.born;
      if (age > LIFE) this.drop(it);
      else if (age > LIFE - 400) it.c.setAlpha((LIFE - age) / 400);
    }
  }

  private drop(it: Item): void {
    this.items = this.items.filter((x) => x !== it);
    it.c.destroy();
    this.restack();
  }

  private restack(): void {
    let y = this.top;
    for (const it of this.items) {
      const w = (it.c as Phaser.GameObjects.Container & { toastW: number }).toastW;
      it.c.setPosition(Math.round(this.centerX - w / 2), Math.round(y));
      y += it.h + 6;
    }
  }

  clear(): void {
    for (const it of [...this.items]) this.drop(it);
  }
}

/** Big unlock banner (UI_013_UnlockBanner) that fades out by itself. */
export function showBanner(scene: Phaser.Scene, text: string, centerX: number, y: number, maxW: number): void {
  const scale = Math.max(1, Math.min(3, Math.floor(maxW / 128)));
  const w = 128 * scale;
  const h = 32 * scale;
  const img = scene.add.image(0, 0, "UI_013_UnlockBanner").setOrigin(0, 0).setScale(scale);
  const label = makeText(scene, w / 2, h / 2, text, { size: Math.min(20, 8 * scale), bold: true, color: COLOR.ink, ox: 0.5, oy: 0.5 });
  const c = scene.add.container(Math.round(centerX - w / 2), y - 20, [img, label]).setDepth(210).setAlpha(0);
  scene.tweens.add({ targets: c, alpha: 1, y, duration: 250, ease: "Quad.easeOut" });
  scene.tweens.add({ targets: c, alpha: 0, delay: 3200, duration: 500, onComplete: () => c.destroy() });
}
