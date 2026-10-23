import Phaser from "phaser";
import { COLOR, TOUCH, makeText } from "./theme";

/** 9-slice panel from the 24x24 UI frames (8px border). `scale` makes the pixel art chunkier. */
export function makePanel(
  scene: Phaser.Scene,
  key: string,
  x: number,
  y: number,
  w: number,
  h: number,
  scale = 2,
  slice = 8,
): Phaser.GameObjects.NineSlice {
  return scene.add.nineslice(x, y, key, undefined, w / scale, h / scale, slice, slice, slice, slice).setOrigin(0, 0).setScale(scale);
}

export type ButtonOpts = {
  w: number;
  h?: number;
  label?: string;
  /** Debug/test name (defaults to the label). */
  name?: string;
  /** Texture key drawn left of (or instead of) the label. */
  icon?: string;
  iconScale?: number;
  size?: number;
  enabled?: boolean;
  selected?: boolean;
  onClick: () => void;
};

const registry = new Set<Button>();

/** Debug/test helper: every live button with its centre in canvas CSS pixels. */
export function listButtons(): { label: string; x: number; y: number; w: number; h: number; enabled: boolean }[] {
  const out: { label: string; x: number; y: number; w: number; h: number; enabled: boolean }[] = [];
  for (const b of registry) {
    if (!b.container.active || !b.isVisible()) continue;
    const m = b.container.getWorldTransformMatrix();
    out.push({ label: b.name, x: m.tx + b.w / 2, y: m.ty + b.h / 2, w: b.w, h: b.h, enabled: b.enabled });
  }
  return out;
}

/** Pixel-art button: Button_Normal / Selected / Pressed / Disabled frames, >= 44px tall by default. */
export class Button {
  readonly container: Phaser.GameObjects.Container;
  readonly w: number;
  readonly h: number;
  label: string;
  readonly name: string;
  enabled: boolean;
  private selected: boolean;
  private pressed = false;
  private skins: Record<"normal" | "pressed" | "selected" | "disabled", Phaser.GameObjects.NineSlice>;
  private text?: Phaser.GameObjects.Text;

  constructor(scene: Phaser.Scene, x: number, y: number, private o: ButtonOpts) {
    this.w = o.w;
    this.h = o.h ?? 48;
    this.label = o.label ?? "";
    this.name = o.name ?? this.label;
    this.enabled = o.enabled ?? true;
    this.selected = o.selected ?? false;
    const mk = (key: string) => makePanel(scene, key, 0, 0, this.w, this.h, 2, 4);
    this.skins = {
      normal: mk("UI_006_Button_Normal"),
      pressed: mk("UI_006_Button_Pressed"),
      selected: mk("UI_006_Button_Selected"),
      disabled: mk("UI_006_Button_Disabled"),
    };
    const parts: Phaser.GameObjects.GameObject[] = Object.values(this.skins);
    const size = o.size ?? 17;
    let icon: Phaser.GameObjects.Image | undefined;
    const is = o.iconScale ?? 2;
    if (o.icon) {
      icon = scene.add.image(0, this.h / 2, o.icon).setScale(is).setOrigin(0.5, 0.5);
      parts.push(icon);
    }
    if (this.label) {
      this.text = makeText(scene, 0, this.h / 2, this.label, { size, bold: true, ox: 0.5, oy: 0.5 });
      parts.push(this.text);
    }
    // icon + label are laid out as a centred group
    const iconW = icon ? 16 * is : 0;
    const gap = icon && this.text ? 6 : 0;
    const total = iconW + gap + (this.text?.width ?? 0);
    const start = (this.w - total) / 2;
    if (icon) icon.setX(start + iconW / 2);
    if (this.text) this.text.setX(start + iconW + gap + this.text.width / 2);
    const hit = scene.add.rectangle(0, 0, this.w, Math.max(this.h, TOUCH), 0xffffff, 0).setOrigin(0, 0);
    hit.setInteractive({ useHandCursor: true });
    parts.push(hit);
    hit.on("pointerdown", () => {
      this.pressed = true;
      this.refresh();
    });
    const release = () => {
      this.pressed = false;
      this.refresh();
    };
    hit.on("pointerout", release);
    hit.on("pointerup", () => {
      const fire = this.pressed && this.enabled;
      release();
      if (fire) this.o.onClick();
    });
    this.container = scene.add.container(x, y, parts);
    this.refresh();
    registry.add(this);
    this.container.once(Phaser.GameObjects.Events.DESTROY, () => registry.delete(this));
  }

  isVisible(): boolean {
    let c: Phaser.GameObjects.Container | null = this.container;
    while (c) {
      if (!c.visible) return false;
      c = c.parentContainer;
    }
    return true;
  }

  setEnabled(v: boolean): this {
    this.enabled = v;
    this.refresh();
    return this;
  }

  setSelected(v: boolean): this {
    if (this.selected === v) return this;
    this.selected = v;
    this.refresh();
    return this;
  }

  setLabel(s: string): this {
    this.label = s;
    this.text?.setText(s);
    return this;
  }

  private refresh(): void {
    const state = !this.enabled ? "disabled" : this.pressed ? "pressed" : this.selected ? "selected" : "normal";
    for (const [k, s] of Object.entries(this.skins)) s.setVisible(k === state);
    this.text?.setColor(state === "disabled" ? COLOR.grey : state === "pressed" ? COLOR.paper : COLOR.ink);
  }
}
