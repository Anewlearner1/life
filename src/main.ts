import Phaser from "phaser";
import { GameController } from "./game/GameController";
import { BootScene } from "./scenes/BootScene";
import { CreateScene } from "./scenes/CreateScene";
import { RhythmScene } from "./scenes/RhythmScene";
import { UIScene } from "./scenes/UIScene";
import { WorldScene } from "./scenes/WorldScene";

const controller = new GameController();

// Scene order = render order: Create < World < UI < Rhythm.
const game = new Phaser.Game({
  type: Phaser.AUTO,
  parent: "game",
  backgroundColor: "#181425",
  pixelArt: true,
  roundPixels: true,
  scale: { mode: Phaser.Scale.RESIZE, width: "100%", height: "100%" },
  scene: [BootScene, CreateScene, WorldScene, UIScene, RhythmScene],
});
controller.attachGame(game);

game.events.once("assets-ready", () => {
  game.scene.start("Create", { controller });
  game.scene.stop("Boot");
});

// Testing hook (Playwright): window.__pixelLife.controller
Object.assign(window, { __pixelLife: { controller } });
