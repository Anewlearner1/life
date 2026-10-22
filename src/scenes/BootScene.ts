import Phaser from "phaser";
import type { Facing } from "../game/types";
import { propsCatalog, propTextureKey } from "./props";

// ---------------------------------------------------------------------------
// Texture keys
//  - tilesets:   "tiles_ground" (6 frames), "tiles_road" (8x4 frames), "tiles_blockers" (6 frames)
//  - props:      "prop_<key>" (see props.ts)
//  - characters: textures `${spriteKey}_walk_${dir}` (64x24, 4 frames 16x24)
//                          `${spriteKey}_idle_${dir}` (32x24, 2 frames; NPCs only have "down")
//                anims    `${spriteKey}-walk-${dir}` (4f, 8fps, loop)
//                         `${spriteKey}-idle-${dir}` (2f, 2fps, loop; NPC idle reuses the Down strip)
//  - everything else (UI, icons, portraits, items, effects, minigame art): key = file name without
//    "_v01.png", e.g. "UI_001_Need_Energy", "NPC_001_CafeOwner_Portrait_Neutral", "OBJ_003_Apple".
//    FX_* files are 16x16 spritesheets.
// ---------------------------------------------------------------------------

export const PLAYER_SPRITE_KEY = "CHAR_001_Player";
export const OUTFIT2_SPRITE_KEY = "CHAR_005_Player_Outfit2";
/** Sprite key family for the player's chosen outfit (see CreateScene OUTFITS). */
export const playerSpriteKeyFor = (outfitId: string): string => (outfitId === "outfit2" ? OUTFIT2_SPRITE_KEY : PLAYER_SPRITE_KEY);
export const DIRS: Facing[] = ["down", "left", "right", "up"];

export const NPC_SPRITES: { id: string; spriteKey: string; folder: string }[] = [
  { id: "npc_001", spriteKey: "NPC_001_CafeOwner", folder: "npc_001" },
  { id: "npc_002", spriteKey: "NPC_002_Shopkeeper", folder: "npc_002" },
  { id: "npc_003", spriteKey: "NPC_003_Neighbor", folder: "npc_003" },
  { id: "npc_004", spriteKey: "NPC_004_Student", folder: "npc_004" },
  { id: "npc_005", spriteKey: "NPC_005_Farmer", folder: "npc_005" },
  { id: "npc_006", spriteKey: "NPC_006_Officeworker", folder: "npc_006" },
  { id: "npc_007", spriteKey: "NPC_007_Artist", folder: "npc_007" },
  { id: "npc_008", spriteKey: "NPC_008_Mailcarrier", folder: "npc_008" },
];

/** Misc images (UI, HUD, icons, portraits, items, effects, minigame art) keyed by file basename. */
const MISC_ASSETS: string[] = [
  "characters/player/hair/CHAR_004_BaseHead_Down_v01.png",
  "characters/player/hair/CHAR_004_Hair_Bob_Down_v01.png",
  "characters/player/hair/CHAR_004_Hair_Buzz_Down_v01.png",
  "characters/player/hair/CHAR_004_Hair_Long_Down_v01.png",
  "characters/player/hair/CHAR_004_Hair_Ponytail_Down_v01.png",
  "characters/player/hair/CHAR_004_Hair_Preview_v01.png",
  "characters/player/hair/CHAR_004_Hair_Short_Down_v01.png",
  "characters/player/hair/CHAR_004_Hair_Spiky_Down_v01.png",
  "characters/player/outfits/CHAR_005_Player_Outfit2_Down_Walk_v01.png",
  "characters/player/outfits/CHAR_005_Player_Outfit2_Left_Walk_v01.png",
  "characters/player/outfits/CHAR_005_Player_Outfit2_Right_Walk_v01.png",
  "characters/player/outfits/CHAR_005_Player_Outfit2_Up_Walk_v01.png",
  "characters/player/portraits/CHAR_001_Player_Portrait_v01.png",
  "effects/interaction/FX_001_InteractPulse_v01.png",
  "effects/interaction/FX_005_LowNeed_v01.png",
  "effects/rewards/FX_002_CoinPop_v01.png",
  "effects/rewards/FX_003_HeartUp_v01.png",
  "effects/unlocks/FX_004_Sparkle_v01.png",
  "minigames/rhythm/MINI_001_Panel_v01.png",
  "minigames/rhythm/MINI_002_RhythmCue_Hold_v01.png",
  "minigames/rhythm/MINI_002_RhythmCue_Tap_v01.png",
  "minigames/rhythm/MINI_003_HitZone_v01.png",
  "minigames/rhythm/MINI_003_Track_v01.png",
  "minigames/rhythm/MINI_004_Judge_Good_v01.png",
  "minigames/rhythm/MINI_004_Judge_Miss_v01.png",
  "minigames/rhythm/MINI_004_Judge_Perfect_v01.png",
  "minigames/rhythm/MINI_005_ResultPanel_v01.png",
  "objects/food/OBJ_003_Apple_v01.png",
  "objects/food/OBJ_003_Bento_v01.png",
  "objects/food/OBJ_003_Bread_v01.png",
  "objects/food/OBJ_003_Coffee_v01.png",
  "objects/food/OBJ_003_Sandwich_v01.png",
  "objects/furniture/BLD_006_Bed_v01.png",
  "objects/furniture/BLD_006_Chair_v01.png",
  "objects/furniture/BLD_006_Counter_v01.png",
  "objects/furniture/BLD_006_Lamp_v01.png",
  "objects/furniture/BLD_006_Shelf_v01.png",
  "objects/furniture/BLD_006_Table_v01.png",
  "objects/products/OBJ_004_Book_v01.png",
  "objects/products/OBJ_004_Flower_v01.png",
  "objects/products/OBJ_004_Gift_v01.png",
  "objects/products/OBJ_004_Shirt_v01.png",
  "objects/work_tools/MINI_006_Apron_v01.png",
  "objects/work_tools/MINI_006_Cup_v01.png",
  "objects/work_tools/MINI_006_EspressoMachine_v01.png",
  "objects/work_tools/MINI_006_Grinder_v01.png",
  "objects/work_tools/MINI_006_MenuBoard_v01.png",
  "objects/work_tools/MINI_006_Milk_v01.png",
  "objects/work_tools/MINI_006_Tray_v01.png",
  "ui/buttons/UI_004_TimeControl_Fast_v01.png",
  "ui/buttons/UI_004_TimeControl_Normal_v01.png",
  "ui/buttons/UI_004_TimeControl_Pause_v01.png",
  "ui/buttons/UI_006_Button_Disabled_v01.png",
  "ui/buttons/UI_006_Button_Normal_v01.png",
  "ui/buttons/UI_006_Button_Pressed_v01.png",
  "ui/buttons/UI_006_Button_Selected_v01.png",
  "ui/hud/UI_001_NeedBar_Fill_v01.png",
  "ui/hud/UI_001_NeedBar_Frame_v01.png",
  "ui/hud/UI_001_Need_Energy_v01.png",
  "ui/hud/UI_001_Need_Fullness_v01.png",
  "ui/hud/UI_001_Need_Mood_v01.png",
  "ui/hud/UI_002_Money_v01.png",
  "ui/hud/UI_003_Calendar_v01.png",
  "ui/hud/UI_003_ClockFrame_v01.png",
  "ui/hud/UI_003_Clock_v01.png",
  "ui/icons/AUDIO_001_Volume_Off_v01.png",
  "ui/icons/AUDIO_001_Volume_On_v01.png",
  "ui/icons/EVT_002_StageBar_v01.png",
  "ui/icons/EVT_002_Stage_Acquaintance_v01.png",
  "ui/icons/EVT_002_Stage_CloseFriend_v01.png",
  "ui/icons/EVT_002_Stage_Crush_v01.png",
  "ui/icons/EVT_002_Stage_Friend_v01.png",
  "ui/icons/EVT_002_Stage_Partner_v01.png",
  "ui/icons/EVT_002_Stage_Stranger_v01.png",
  "ui/icons/OBJ_001_Interact_v01.png",
  "ui/icons/OBJ_001_Talk_v01.png",
  "ui/icons/UI_007_Tab_Bag_v01.png",
  "ui/icons/UI_007_Tab_Character_v01.png",
  "ui/icons/UI_007_Tab_Map_v01.png",
  "ui/icons/UI_007_Tab_Relationship_v01.png",
  "ui/icons/UI_007_Tab_Settings_v01.png",
  "ui/icons/UI_007_Tab_Work_v01.png",
  "ui/icons/UI_008_Notice_Info_v01.png",
  "ui/icons/UI_008_Notice_SaveOk_v01.png",
  "ui/icons/UI_008_Notice_Unlock_v01.png",
  "ui/icons/UI_008_Notice_Warning_v01.png",
  "ui/icons/UI_011_Heart_Empty_v01.png",
  "ui/icons/UI_011_Heart_Full_v01.png",
  "ui/icons/UI_011_Heart_Half_v01.png",
  "ui/icons/UI_012_Load_v01.png",
  "ui/icons/UI_012_SaveError_v01.png",
  "ui/icons/UI_012_Save_v01.png",
  "ui/menus/UI_010_Arrow_Left_v01.png",
  "ui/menus/UI_010_Arrow_Right_v01.png",
  "ui/menus/UI_010_ColorSwatch_Frame_v01.png",
  "ui/menus/UI_010_CreatePanel_v01.png",
  "ui/menus/UI_010_NameField_v01.png",
  "ui/menus/UI_010_Preview_v01.png",
  "ui/menus/UI_013_Lock_Locked_v01.png",
  "ui/menus/UI_013_Lock_Unlocked_v01.png",
  "ui/menus/UI_013_MapPin_New_v01.png",
  "ui/menus/UI_013_UnlockBanner_v01.png",
  "ui/panels/UI_005_DialogBox_Preview_v01.png",
  "ui/panels/UI_005_DialogBox_v01.png",
  "ui/panels/UI_009_ShopPanel_v01.png",
];

const cap = (s: string) => s[0].toUpperCase() + s.slice(1);

export const walkAnimKey = (spriteKey: string, dir: Facing) => `${spriteKey}-walk-${dir}`;
export const idleAnimKey = (spriteKey: string, dir: Facing) => `${spriteKey}-idle-${dir}`;

export class BootScene extends Phaser.Scene {
  private nextScene?: string;
  private nextData?: object;

  constructor() {
    super("Boot");
  }

  /** Optional: `scene.start("Boot", { next: "World", nextData: { bridge } })`. */
  init(data?: { next?: string; nextData?: object }): void {
    this.nextScene = data?.next;
    this.nextData = data?.nextData;
  }

  preload(): void {
    const base = `${import.meta.env.BASE_URL}assets/`;
    this.load.setPath(base);

    const { width, height } = this.scale;
    const bg = this.add.rectangle(width / 2, height / 2, 160, 8, 0x3a4466).setOrigin(0.5);
    const bar = this.add.rectangle(width / 2 - 80, height / 2, 1, 8, 0xfee761).setOrigin(0, 0.5);
    this.load.on("progress", (p: number) => (bar.width = Math.max(1, 160 * p)));
    this.load.once("complete", () => {
      bg.destroy();
      bar.destroy();
    });
    this.load.on("loaderror", (f: Phaser.Loader.File) => console.warn("[Boot] failed to load", f.src));

    // Tilesets (16x16 frames)
    this.load.spritesheet("tiles_ground", "maps/tilesets/MAP_001_Ground_Tileset_v01.png", { frameWidth: 16, frameHeight: 16 });
    this.load.spritesheet("tiles_road", "maps/tilesets/MAP_002_Road_Tileset_v01.png", { frameWidth: 16, frameHeight: 16 });
    this.load.spritesheet("tiles_blockers", "maps/tilesets/MAP_010_Blockers_v01.png", { frameWidth: 16, frameHeight: 16 });

    // Props
    for (const p of Object.values(propsCatalog)) this.load.image(propTextureKey(p.key), p.texturePath);

    // Player: 4-direction walk + idle strips
    for (const d of DIRS) {
      const D = cap(d);
      this.load.spritesheet(`${PLAYER_SPRITE_KEY}_walk_${d}`, `characters/player/walk/CHAR_001_Player_${D}_Walk_v01.png`, { frameWidth: 16, frameHeight: 24 });
      this.load.spritesheet(`${PLAYER_SPRITE_KEY}_idle_${d}`, `characters/player/idle/CHAR_003_Player_${D}_Idle_v01.png`, { frameWidth: 16, frameHeight: 24 });
    }

    // Outfit2 variant: same walk strips; the idle texture reuses the walk file (anim uses frame 0 only)
    for (const d of DIRS) {
      const file = `characters/player/outfits/CHAR_005_Player_Outfit2_${cap(d)}_Walk_v01.png`;
      this.load.spritesheet(`${OUTFIT2_SPRITE_KEY}_walk_${d}`, file, { frameWidth: 16, frameHeight: 24 });
      this.load.spritesheet(`${OUTFIT2_SPRITE_KEY}_idle_${d}`, file, { frameWidth: 16, frameHeight: 24 });
    }

    // NPCs: 4-direction walk, Down idle only; portraits for dialogue UI
    for (const n of NPC_SPRITES) {
      const dir = `characters/npcs/${n.folder}/${n.spriteKey}`;
      for (const d of DIRS) {
        this.load.spritesheet(`${n.spriteKey}_walk_${d}`, `${dir}_${cap(d)}_Walk_v01.png`, { frameWidth: 16, frameHeight: 24 });
      }
      this.load.spritesheet(`${n.spriteKey}_idle_down`, `${dir}_Down_Idle_v01.png`, { frameWidth: 16, frameHeight: 24 });
      for (const mood of ["Neutral", "Happy", "Sad"]) {
        this.load.image(`${n.spriteKey}_Portrait_${mood}`, `${dir}_Portrait_${mood}_v01.png`);
      }
    }

    // Everything else
    for (const path of MISC_ASSETS) {
      const key = path.slice(path.lastIndexOf("/") + 1).replace(/_v01\.png$/, "");
      if (key.startsWith("FX_")) this.load.spritesheet(key, path, { frameWidth: 16, frameHeight: 16 });
      else this.load.image(key, path);
    }
  }

  create(): void {
    this.createAnimations();
    this.game.events.emit("assets-ready");
    if (this.nextScene) this.scene.start(this.nextScene, this.nextData);
  }

  private createAnimations(): void {
    const mk = (key: string, tex: string, frameRate: number) => {
      if (this.anims.exists(key) || !this.textures.exists(tex)) return;
      const n = this.textures.get(tex).frameTotal - 1; // minus __BASE
      this.anims.create({
        key,
        frames: this.anims.generateFrameNumbers(tex, { start: 0, end: n - 1 }),
        frameRate,
        repeat: -1,
      });
    };
    const chars = [PLAYER_SPRITE_KEY, ...NPC_SPRITES.map((n) => n.spriteKey)];
    for (const sk of chars) {
      for (const d of DIRS) {
        mk(walkAnimKey(sk, d), `${sk}_walk_${d}`, 8);
        // NPCs only ship a Down idle strip; reuse it for every facing.
        const idleTex = this.textures.exists(`${sk}_idle_${d}`) ? `${sk}_idle_${d}` : `${sk}_idle_down`;
        mk(idleAnimKey(sk, d), idleTex, 2);
      }
    }
    for (const d of DIRS) {
      mk(walkAnimKey(OUTFIT2_SPRITE_KEY, d), `${OUTFIT2_SPRITE_KEY}_walk_${d}`, 8);
      const key = idleAnimKey(OUTFIT2_SPRITE_KEY, d);
      if (!this.anims.exists(key) && this.textures.exists(`${OUTFIT2_SPRITE_KEY}_idle_${d}`)) {
        this.anims.create({ key, frames: this.anims.generateFrameNumbers(`${OUTFIT2_SPRITE_KEY}_idle_${d}`, { frames: [0] }), frameRate: 1, repeat: -1 });
      }
    }
    if (!this.anims.exists("water")) {
      this.anims.create({
        key: "water",
        frames: this.anims.generateFrameNumbers("tiles_blockers", { frames: [4, 5] }),
        frameRate: 2,
        repeat: -1,
      });
    }
  }
}
