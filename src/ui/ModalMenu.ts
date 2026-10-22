import Phaser from "phaser";
import { COLOR, makeText, TOUCH } from "./theme";
import { Button, makePanel } from "./widgets";

export type MenuButton = { label: string; onClick: () => void; enabled?: boolean; icon?: string; name?: string };

export type RowSpec = {
  icon?: string;
  title: string;
  sub?: string;
  button?: MenuButton;
};

export type MenuSpec = {
  title: string;
  subtitle?: string;
  /** Texture key of a 48x48 portrait. */
  portrait?: string;
  /** Texture key of a 16x16 icon used when there is no portrait. */
  icon?: string;
  /** 0-100: draws 5 hearts. */
  affection?: number;
  body?: string[];
  /** Highlighted (red) note, e.g. why an action is unavailable. */
  note?: string;
  moneyLine?: string;
  tabs?: { label: string; active: boolean; onClick: () => void; name?: string }[];
  rows?: RowSpec[];
  emptyText?: string;
  buttons: MenuButton[];
};

/** Centred modal card with a dimmed, input-swallowing backdrop. Rebuilt from `getSpec()` on refresh/resize. */
export class ModalMenu {
  private root?: Phaser.GameObjects.Container;

  constructor(
    private scene: Phaser.Scene,
    private getSpec: () => MenuSpec,
    private depth = 50,
  ) {
    this.build();
  }

  refresh(): void {
    this.build();
  }

  destroy(): void {
    this.root?.destroy();
    this.root = undefined;
  }

  private build(): void {
    this.root?.destroy();
    const spec = this.getSpec();
    const W = this.scene.scale.width;
    const H = this.scene.scale.height;
    const sc = this.scene;
    const pw = Math.min(W - 24, 440);
    const PAD = 24; // 16px border + 8px breathing room
    const iw = pw - PAD * 2;
    const root = sc.add.container(0, 0).setDepth(this.depth);
    this.root = root;

    const backdrop = sc.add.rectangle(0, 0, W, H, 0x000000, 0.55).setOrigin(0, 0).setInteractive();
    root.add(backdrop);

    const card = sc.add.container(0, 0);
    const kids: Phaser.GameObjects.GameObject[] = [];
    let y = PAD;

    // header
    if (spec.portrait || spec.icon || spec.affection !== undefined) {
      const hasPortrait = !!spec.portrait;
      const left = hasPortrait ? 96 + 12 : spec.icon ? 40 : 0;
      if (spec.portrait) kids.push(sc.add.image(PAD, y, spec.portrait).setOrigin(0, 0).setScale(2));
      else if (spec.icon) kids.push(sc.add.image(PAD + 16, y + 16, spec.icon).setScale(2));
      const title = makeText(sc, PAD + left, y, spec.title, { size: 22, bold: true, wrap: iw - left });
      kids.push(title);
      let ty = y + title.height + 2;
      if (spec.subtitle) {
        const s = makeText(sc, PAD + left, ty, spec.subtitle, { size: 14, color: COLOR.grey, wrap: iw - left });
        kids.push(s);
        ty += s.height + 4;
      }
      if (spec.affection !== undefined) {
        const full = Math.floor(spec.affection / 20);
        const half = spec.affection % 20 >= 10 ? 1 : 0;
        for (let i = 0; i < 5; i++) {
          const key = i < full ? "UI_011_Heart_Full" : i === full && half ? "UI_011_Heart_Half" : "UI_011_Heart_Empty";
          kids.push(sc.add.image(PAD + left + 14 + i * 30, ty + 14, key).setScale(1.75));
        }
        kids.push(makeText(sc, PAD + left + 5 * 30 + 4, ty + 14, `${Math.round(spec.affection)}`, { size: 14, bold: true, oy: 0.5 }));
        ty += 30;
      }
      y += Math.max(hasPortrait ? 96 : spec.icon ? 36 : 0, ty - y) + 12;
    } else {
      const title = makeText(sc, PAD, y, spec.title, { size: 22, bold: true, wrap: iw });
      kids.push(title);
      y += title.height + 6;
      if (spec.subtitle) {
        const s = makeText(sc, PAD, y, spec.subtitle, { size: 14, color: COLOR.grey, wrap: iw });
        kids.push(s);
        y += s.height + 6;
      }
    }

    if (spec.body) {
      for (const line of spec.body) {
        const t = makeText(sc, PAD, y, line, { size: 16, wrap: iw });
        kids.push(t);
        y += t.height + 8;
      }
    }
    if (spec.note) {
      const t = makeText(sc, PAD, y, spec.note, { size: 15, bold: true, color: COLOR.red, wrap: iw });
      kids.push(t);
      y += t.height + 8;
    }
    if (spec.moneyLine) {
      kids.push(sc.add.image(PAD + 12, y + 14, "UI_002_Money").setScale(1.5));
      kids.push(makeText(sc, PAD + 30, y + 14, spec.moneyLine, { size: 18, bold: true, oy: 0.5 }));
      y += 32;
    }

    if (spec.tabs?.length) {
      const n = spec.tabs.length;
      const tw = (iw - (n - 1) * 6) / n;
      spec.tabs.forEach((t, i) => {
        const b = new Button(sc, PAD + i * (tw + 6), y, { w: tw, h: TOUCH, label: t.label, selected: t.active, name: t.name ?? t.label, onClick: t.onClick });
        kids.push(b.container);
      });
      y += TOUCH + 10;
    }

    if (spec.rows) {
      if (!spec.rows.length && spec.emptyText) {
        const t = makeText(sc, PAD, y, spec.emptyText, { size: 16, color: COLOR.grey, wrap: iw });
        kids.push(t);
        y += t.height + 12;
      }
      // shrink rows if the card would not fit the screen
      const fixed = y + 12 + spec.buttons.length * 56 + PAD;
      const rowH = Math.max(TOUCH + 4, Math.min(58, Math.floor((H - 24 - fixed) / Math.max(1, spec.rows.length))));
      for (const r of spec.rows) {
        const bw = r.button ? 104 : 0;
        const textX = PAD + (r.icon ? 40 : 0);
        const textW = iw - (r.icon ? 40 : 0) - bw - 8;
        if (r.icon) kids.push(sc.add.image(PAD + 16, y + rowH / 2 - 2, r.icon).setScale(2));
        const hasSub = !!r.sub;
        const t = makeText(sc, textX, y + (hasSub ? 5 : rowH / 2 - 2), r.title, { size: 16, bold: true, oy: hasSub ? 0 : 0.5, wrap: textW });
        kids.push(t);
        if (hasSub) kids.push(makeText(sc, textX, y + 5 + 20, r.sub!, { size: 12, color: COLOR.grey, wrap: textW }));
        if (r.button) {
          const b = new Button(sc, PAD + iw - bw, y + (rowH - TOUCH) / 2 - 2, {
            w: bw,
            h: TOUCH,
            label: r.button.label,
            size: 15,
            enabled: r.button.enabled,
            name: r.button.name ?? r.button.label,
            onClick: r.button.onClick,
          });
          kids.push(b.container);
        }
        y += rowH;
      }
      y += 8;
    }

    for (const bt of spec.buttons) {
      const b = new Button(sc, PAD, y, {
        w: iw,
        h: 48,
        label: bt.label,
        icon: bt.icon,
        enabled: bt.enabled,
        name: bt.name ?? bt.label,
        onClick: bt.onClick,
      });
      kids.push(b.container);
      y += 56;
    }
    y += PAD - 8;

    const ph = Math.ceil(y);
    const px = Math.round((W - pw) / 2);
    const py = Math.max(8, Math.round((H - ph) / 2));
    const panel = makePanel(sc, "UI_005_DialogBox", 0, 0, pw, ph, 2, 8);
    card.add([panel, ...kids]);
    card.setPosition(px, py);
    root.add(card);
  }
}
