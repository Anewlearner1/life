import Phaser from "phaser";
import { clockParts } from "../systems/TimeSystem";
import { formatDate, playerAge, seasonOf } from "../systems/CalendarSystem";
import type { GameController } from "../game/GameController";
import type { NeedKey, TimeMode, Weather } from "../game/types";
import { GameConfig } from "../game/GameConfig";
import { COLOR, makeText, TOUCH } from "./theme";
import { Button, makePanel } from "./widgets";

const NEEDS: { key: NeedKey; icon: string; tint: number }[] = [
  { key: "stamina", icon: "UI_001_Need_Energy", tint: 0xf77622 },
  { key: "satiety", icon: "UI_001_Need_Fullness", tint: 0xfeae34 },
  { key: "mood", icon: "UI_001_Need_Mood", tint: 0x2ce8f5 },
];
const MODES: { mode: TimeMode; icon: string }[] = [
  { mode: "paused", icon: "UI_004_TimeControl_Pause" },
  { mode: "normal", icon: "UI_004_TimeControl_Normal" },
  { mode: "fast", icon: "UI_004_TimeControl_Fast" },
];

const WEATHER_ICON: Record<Weather, string> = {
  sunny: "UI_014_Weather_Sunny",
  cloudy: "UI_014_Weather_Cloudy",
  rain: "UI_014_Weather_Rain",
  snow: "UI_014_Weather_Snow",
};
const WEATHER_LABEL: Record<Weather, string> = { sunny: "晴", cloudy: "多雲", rain: "雨", snow: "雪" };
const SEASON_ICON = (s: string) => `UI_015_Season_${s[0].toUpperCase()}${s.slice(1)}`;
const pad2 = (n: number) => String(n).padStart(2, "0");
const HUD_H = 126;

type Bar = { key: NeedKey; fill: Phaser.GameObjects.Image; innerW: number; tint: number };

/** Top HUD (needs, money, time, date/season/weather/age, time controls) + bottom-right save/bag/family buttons. */
export class Hud {
  private root?: Phaser.GameObjects.Container;
  private bars: Bar[] = [];
  private money?: Phaser.GameObjects.Text;
  private clock?: Phaser.GameObjects.Text;
  private date?: Phaser.GameObjects.Text;
  private age?: Phaser.GameObjects.Text;
  private weatherLabel?: Phaser.GameObjects.Text;
  private seasonIcon?: Phaser.GameObjects.Image;
  private weatherIcon?: Phaser.GameObjects.Image;
  private modeBtns: Button[] = [];
  /** Bottom of the HUD in canvas px (toasts start below). */
  bottom = 0;
  centerX = 0;
  width = 0;

  constructor(
    private scene: Phaser.Scene,
    private controller: GameController,
    private handlers: { onBag: () => void; onFamily: () => void },
  ) {}

  layout(): void {
    this.root?.destroy();
    this.bars = [];
    this.modeBtns = [];
    const W = this.scene.scale.width;
    const H = this.scene.scale.height;
    const hudW = Math.min(W, 440);
    const pad = 8;
    const root = this.scene.add.container(0, 0).setDepth(10);
    this.root = root;

    // translucent strip behind the HUD for readability over the map
    const strip = this.scene.add.graphics();
    strip.fillStyle(COLOR.inkHex, 0.72).fillRect(0, 0, hudW, HUD_H);
    root.add(strip);

    // Row 1: need bars
    const gap = 6;
    const cw = (hudW - pad * 2 - gap * 2) / 3;
    NEEDS.forEach((n, i) => {
      const x = pad + i * (cw + gap);
      const icon = this.scene.add.image(x + 16, pad + 16, n.icon).setScale(2);
      const barX = x + 34;
      const barW = Math.floor(cw - 34);
      const frame = makePanel(this.scene, "UI_001_NeedBar_Frame", barX, pad + 8, barW, 16, 2, 1);
      const innerW = barW - 4;
      const back = this.scene.add.rectangle(barX + 2, pad + 10, innerW, 12, 0x3a4466, 1).setOrigin(0, 0);
      const fill = this.scene.add.image(barX + 2, pad + 10, "UI_001_NeedBar_Fill").setOrigin(0, 0).setTint(n.tint);
      root.add([icon, back, frame, fill]);
      this.bars.push({ key: n.key, fill, innerW, tint: n.tint });
    });

    // Row 2: money + clock | time controls
    const y2 = pad + 32 + 8;
    const coin = this.scene.add.image(pad + 14, y2 + 22, "UI_002_Money").setScale(2);
    this.money = makeText(this.scene, pad + 32, y2 + 22, "", { size: 18, bold: true, color: COLOR.gold, oy: 0.5 });
    this.clock = makeText(this.scene, pad + 32 + 62, y2 + 22, "", { size: 16, bold: true, color: COLOR.paper, oy: 0.5 });
    root.add([coin, this.money, this.clock]);

    // Row 3: season icon + year/season/day | weather icon + label | player age
    const y3 = y2 + 44 + 8 + 12;
    this.seasonIcon = this.scene.add.image(pad + 12, y3, "UI_015_Season_Spring").setScale(1.5);
    this.date = makeText(this.scene, pad + 30, y3, "", { size: 14, bold: true, color: COLOR.paper, oy: 0.5 });
    this.weatherIcon = this.scene.add.image(0, y3, "UI_014_Weather_Sunny").setScale(1.5);
    this.weatherLabel = makeText(this.scene, 0, y3, "", { size: 14, bold: true, color: COLOR.paper, oy: 0.5 });
    this.age = makeText(this.scene, hudW - pad, y3, "", { size: 14, bold: true, color: COLOR.gold, ox: 1, oy: 0.5 });
    root.add([this.seasonIcon, this.date, this.weatherIcon, this.weatherLabel, this.age]);
    const bw = TOUCH;
    const bx0 = hudW - pad - bw * 3 - 4 * 2;
    MODES.forEach((m, i) => {
      const b = new Button(this.scene, bx0 + i * (bw + 4), y2, {
        w: bw,
        h: bw,
        icon: m.icon,
        name: m.mode,
        onClick: () => this.controller.setTimeMode(m.mode),
      });
      this.modeBtns.push(b);
      root.add(b.container);
    });

    // bottom-right: bag + save
    const by = H - pad - 48;
    const save = new Button(this.scene, W - pad - 48, by, {
      w: 48,
      h: 48,
      icon: "UI_012_Save",
      name: "save",
      onClick: () => void this.controller.save(true),
    });
    const bag = new Button(this.scene, W - pad - 48 * 2 - 6, by, {
      w: 48,
      h: 48,
      icon: "UI_007_Tab_Bag",
      name: "bag",
      onClick: this.handlers.onBag,
    });
    const family = new Button(this.scene, W - pad - 48 * 3 - 12, by, {
      w: 48,
      h: 48,
      icon: "UI_007_Tab_Family",
      name: "family",
      onClick: this.handlers.onFamily,
    });
    root.add([save.container, bag.container, family.container]);
    this.bottom = HUD_H;
    this.centerX = hudW / 2;
    this.width = hudW;
    this.update();
  }

  update(): void {
    const st = this.controller.state;
    if (!st || !this.root) return;
    const blink = Math.floor(this.scene.time.now / 400) % 2 === 0;
    for (const b of this.bars) {
      const v = Math.max(0, Math.min(100, st.player.needs[b.key]));
      const low = v < GameConfig.needs.warnBelow;
      b.fill.setDisplaySize(Math.max(0, Math.round((b.innerW * v) / 100)), 12);
      b.fill.setVisible(v > 0);
      b.fill.setTint(low ? (blink ? 0xe43b44 : 0x9e2835) : b.tint);
    }
    this.money?.setText(String(st.player.money));
    const cp = clockParts(st.gameClock.totalMinutes);
    this.clock?.setText(`${pad2(cp.hour)}:${pad2(cp.minute)}`);
    const season = seasonOf(cp.day);
    this.seasonIcon?.setTexture(SEASON_ICON(season));
    this.date?.setText(formatDate(st.gameClock.totalMinutes));
    if (this.date && this.weatherIcon && this.weatherLabel) {
      const wx = this.date.x + this.date.width + 14;
      this.weatherIcon.setTexture(WEATHER_ICON[st.weather.kind]).setPosition(wx + 12, this.date.y);
      this.weatherLabel.setText(WEATHER_LABEL[st.weather.kind]).setPosition(wx + 28, this.date.y);
    }
    this.age?.setText(`${Math.floor(playerAge(st))}歲`);
    this.modeBtns.forEach((btn, i) => btn.setSelected(st.gameClock.mode === MODES[i].mode));
  }

  destroy(): void {
    this.root?.destroy();
  }
}
