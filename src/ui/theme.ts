import Phaser from "phaser";

export const FONT = '"Noto Sans TC","PingFang TC","Microsoft JhengHei","WenQuanYi Zen Hei",system-ui,sans-serif';

export const COLOR = {
  ink: "#181425",
  paper: "#f4f0e8",
  blue: "#284080",
  gold: "#fee761",
  red: "#e43b44",
  green: "#3e8948",
  grey: "#6b6b80",
  inkHex: 0x181425,
  paperHex: 0xf4f0e8,
  blueHex: 0x284080,
};

/** Smallest comfortable touch target in CSS px. */
export const TOUCH = 44;

let mctx: CanvasRenderingContext2D | null = null;

export function measure(str: string, size: number, bold = false): number {
  mctx ??= document.createElement("canvas").getContext("2d");
  if (!mctx) return str.length * size;
  mctx.font = `${bold ? "bold " : ""}${size}px ${FONT}`;
  return mctx.measureText(str).width;
}

const NO_LINE_START = "，。！？、：；」』）”’…,.!?:;)";

/** Greedy wrap that also works for CJK text (Phaser only wraps at spaces). Returns the text with \n inserted. */
export function wrap(str: string, maxW: number, size: number, bold = false): string {
  const out: string[] = [];
  for (const para of str.split("\n")) {
    let line = "";
    for (const ch of para) {
      if (line && measure(line + ch, size, bold) > maxW && !NO_LINE_START.includes(ch)) {
        out.push(line);
        line = ch === " " ? "" : ch;
      } else {
        line += ch;
      }
    }
    out.push(line);
  }
  return out.join("\n");
}

export type TextOpts = {
  size?: number;
  color?: string;
  bold?: boolean;
  /** Wrap width in px (CJK aware). */
  wrap?: number;
  align?: "left" | "center" | "right";
  /** Origin x/y (0..1). */
  ox?: number;
  oy?: number;
  stroke?: string;
};

export function makeText(scene: Phaser.Scene, x: number, y: number, str: string, o: TextOpts = {}): Phaser.GameObjects.Text {
  const size = o.size ?? 16;
  const body = o.wrap ? wrap(str, o.wrap, size, o.bold) : str;
  const t = scene.add.text(x, y, body, {
    fontFamily: FONT,
    fontSize: `${size}px`,
    fontStyle: o.bold ? "bold" : "normal",
    color: o.color ?? COLOR.ink,
    align: o.align ?? "left",
    lineSpacing: Math.round(size * 0.3),
    stroke: o.stroke,
    strokeThickness: o.stroke ? 3 : 0,
  });
  t.setOrigin(o.ox ?? 0, o.oy ?? 0);
  return t;
}
