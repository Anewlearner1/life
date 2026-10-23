import Phaser from "phaser";
import type { DialogueSpec } from "../game/GameController";
import type { GameController } from "../game/GameController";
import { COLOR, makeText } from "./theme";
import { makePanel } from "./widgets";

/** Bottom dialogue sheet: portrait + nine-slice box; tap anywhere to advance. */
export class DialoguePanel {
  private root?: Phaser.GameObjects.Container;
  private idx = 0;
  private openedAt = 0;
  private arrow?: Phaser.GameObjects.Text;

  constructor(
    private scene: Phaser.Scene,
    private controller: GameController,
    private spec: DialogueSpec,
    private onClose: () => void,
  ) {
    this.openedAt = scene.time.now;
    this.build();
  }

  relayout(): void {
    this.build();
  }

  destroy(): void {
    if (this.arrow) this.scene.tweens.killTweensOf(this.arrow);
    this.root?.destroy();
    this.root = undefined;
  }

  private advance(): void {
    if (this.scene.time.now - this.openedAt < 150) return;
    if (this.idx < this.spec.lines.length - 1) {
      this.idx++;
      this.build();
      return;
    }
    this.destroy();
    this.onClose();
  }

  private build(): void {
    if (this.arrow) this.scene.tweens.killTweensOf(this.arrow);
    this.root?.destroy();
    const sc = this.scene;
    const W = sc.scale.width;
    const H = sc.scale.height;
    const npc = this.spec.speakerId ? this.controller.content.npcs[this.spec.speakerId] : undefined;
    const name = npc?.name ?? this.spec.name ?? "";
    const portraitKey = npc ? `${npc.spriteKey}_Portrait_${this.spec.mood ?? "Neutral"}` : undefined;
    const pw = Math.min(W - 16, 560);
    const hasPortrait = !!portraitKey && sc.textures.exists(portraitKey);
    const PAD = 24;
    const textX = PAD + (hasPortrait ? 96 + 12 : 0);
    const textW = pw - textX - PAD;

    const root = sc.add.container(0, 0).setDepth(60);
    this.root = root;
    // transparent full-screen catcher: tap anywhere advances
    const catcher = sc.add.rectangle(0, 0, W, H, 0x000000, 0.18).setOrigin(0, 0).setInteractive();
    catcher.on("pointerup", () => this.advance());
    root.add(catcher);

    const kids: Phaser.GameObjects.GameObject[] = [];
    const nameT = makeText(sc, textX, PAD, name, { size: 18, bold: true, color: COLOR.blue });
    const body = makeText(sc, textX, PAD + nameT.height + 4, this.spec.lines[this.idx] ?? "", { size: 17, wrap: textW });
    const contentH = Math.max(hasPortrait ? 96 : 0, nameT.height + 4 + body.height);
    const ph = Math.ceil(PAD * 2 + contentH + 8);
    const px = Math.round((W - pw) / 2);
    const py = Math.round(H - ph - 12);
    kids.push(makePanel(sc, "UI_005_DialogBox", 0, 0, pw, ph, 2, 8));
    if (hasPortrait) kids.push(sc.add.image(PAD, PAD, portraitKey!).setOrigin(0, 0).setScale(2));
    kids.push(nameT, body);
    const more = this.idx < this.spec.lines.length - 1;
    this.arrow = makeText(sc, pw - PAD - 2, ph - PAD - 2, more ? `▼ ${this.idx + 1}/${this.spec.lines.length}` : "▼", {
      size: 14,
      bold: true,
      color: COLOR.blue,
      ox: 1,
      oy: 1,
    });
    kids.push(this.arrow);
    sc.tweens.add({ targets: this.arrow, alpha: 0.3, yoyo: true, repeat: -1, duration: 500 });
    const card = sc.add.container(px, py, kids);
    root.add(card);
  }
}
