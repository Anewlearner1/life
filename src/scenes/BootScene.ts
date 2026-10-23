import Phaser from "phaser";
import type { Facing } from "../game/types";
import { propsCatalog, propTextureKey } from "./props";

// ---------------------------------------------------------------------------
// Texture keys
//  - tilesets:   "tiles_ground" (6 frames), "tiles_road" (8x4 frames), "tiles_blockers" (6 frames),
//                "tiles_interior" (wall_a, wall_b, trim, door_mat), "tiles_farm" (soil, cabbage_row, wheat_row)
//  - props:      "prop_<key>" (see props.ts)
//  - characters: textures `${spriteKey}_walk_${dir}` (96x32, 4 frames 24x32)
//                          `${spriteKey}_idle_${dir}` (48x32, 2 frames; NPCs only have "down")
//                player keys are per hair x outfit: `CHAR_004_Player_<Hair>_<Outfit>` (see playerSpriteKeyFor)
//                anims    `${spriteKey}-walk-${dir}` (4f, 8fps, loop)
//                         `${spriteKey}-idle-${dir}` (2f, 2fps, loop; NPC idle reuses the Down strip)
//  - everything else (UI, icons, portraits, items, effects, minigame art): key = file name without
//    "_v01.png", e.g. "UI_001_Need_Energy", "NPC_001_CafeOwner_Portrait_Neutral", "OBJ_003_Apple".
//    FX_* files are 16x16 spritesheets.
// ---------------------------------------------------------------------------

export const CHAR_FRAME = { frameWidth: 24, frameHeight: 32 };

/** hairId (CreateScene HAIRS) -> art style name used in assets/characters/player/hair_variants. */
export const HAIR_STYLES: Record<string, string> = {
  hair_spiky: "Spiky",
  hair_short: "Short",
  hair_long: "Long",
  hair_bob: "Bob",
  hair_ponytail: "Ponytail",
  hair_buzz: "Buzz",
};
const OUTFIT_STYLES: Record<string, string> = { outfit1: "Default", outfit2: "Outfit2" };

/** Sprite key family for the player's chosen hair + outfit; unknown ids fall back to the default look. */
export const playerSpriteKeyFor = (outfitId: string, hairId = "hair_spiky"): string =>
  `CHAR_004_Player_${HAIR_STYLES[hairId] ?? "Spiky"}_${OUTFIT_STYLES[outfitId] ?? "Default"}`;
const PLAYER_VARIANTS = Object.keys(HAIR_STYLES).flatMap((h) => Object.keys(OUTFIT_STYLES).map((o) => playerSpriteKeyFor(o, h)));
export const DIRS: Facing[] = ["down", "left", "right", "up"];

/** Children (CHAR_006 A/B/C; all four idle directions ship) and the elder player look (CHAR_007). */
export const CHILD_SPRITES = ["CHAR_006_Child_A", "CHAR_006_Child_B", "CHAR_006_Child_C"];
const ELDER_STYLES: Record<string, string> = { outfit1: "Default", outfit2: "Outfit2" };
export const elderSpriteKeyFor = (outfitId: string): string => `CHAR_007_Player_Elder_${ELDER_STYLES[outfitId] ?? "Default"}`;
const ELDER_VARIANTS = Object.keys(OUTFIT_STYLES).map((o) => elderSpriteKeyFor(o));

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
  "characters/player/hair/CHAR_004_Hair_Preview_v01.png",
  "characters/player/portraits/CHAR_001_Player_Portrait_v01.png",
  "effects/interaction/FX_001_InteractPulse_v01.png",
  "effects/interaction/FX_005_LowNeed_v01.png",
  "effects/rewards/FX_002_CoinPop_v01.png",
  "effects/rewards/FX_003_HeartUp_v01.png",
  "effects/unlocks/FX_004_Sparkle_v01.png",
  "effects/weather/FX_006_RainDrop_v01.png",
  "effects/weather/FX_006_SnowFlake_v01.png",
  "effects/weather/FX_007_LampGlow_v01.png",
  "effects/weather/FX_008_Hearts_Wedding_v01.png",
  "minigames/rhythm/MINI_001_Panel_v01.png",
  "minigames/rhythm/MINI_002_RhythmCue_Crop_Cabbage_v01.png",
  "minigames/rhythm/MINI_002_RhythmCue_Crop_Carrot_v01.png",
  "minigames/rhythm/MINI_002_RhythmCue_Crop_Pumpkin_v01.png",
  "minigames/rhythm/MINI_002_RhythmCue_Hold_v01.png",
  "minigames/rhythm/MINI_002_RhythmCue_Tap_v01.png",
  "minigames/rhythm/MINI_003_HitZone_v01.png",
  "minigames/rhythm/MINI_003_Track_Farm_v01.png",
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
  "objects/products/OBJ_004_Ring_v01.png",
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
  "ui/hud/UI_007_Tab_Family_v01.png",
  "ui/hud/UI_014_Weather_Cloudy_v01.png",
  "ui/hud/UI_014_Weather_Rain_v01.png",
  "ui/hud/UI_014_Weather_Snow_v01.png",
  "ui/hud/UI_014_Weather_Sunny_v01.png",
  "ui/hud/UI_015_Season_Autumn_v01.png",
  "ui/hud/UI_015_Season_Spring_v01.png",
  "ui/hud/UI_015_Season_Summer_v01.png",
  "ui/hud/UI_015_Season_Winter_v01.png",
  "ui/hud/UI_016_Ring_v01.png",
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
  "ui/title/UI_000_TitleBanner_v01.png",
];

/** FX_* files are 16x16 spritesheets unless listed here: frame size, or null for a plain image. */
const FX_FRAME: Record<string, { w: number; h: number } | null> = {
  FX_006_RainDrop: null,
  FX_006_SnowFlake: { w: 4, h: 4 },
  FX_007_LampGlow: null,
};

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
    this.load.spritesheet("tiles_farm", "maps/tilesets/MAP_011_Farm_Tileset_v01.png", { frameWidth: 16, frameHeight: 16 });
    this.load.spritesheet("tiles_interior", "maps/interiors/MAP_007_Interior_Tileset_v01.png", { frameWidth: 16, frameHeight: 16 });

    // Props
    for (const p of Object.values(propsCatalog)) this.load.image(propTextureKey(p.key), p.texturePath);

    // Player: every hair x outfit variant, 4-direction walk + idle strips
    for (const sk of PLAYER_VARIANTS) {
      for (const d of DIRS) {
        const base = `characters/player/hair_variants/${sk}_${cap(d)}`;
        this.load.spritesheet(`${sk}_walk_${d}`, `${base}_Walk_v01.png`, CHAR_FRAME);
        this.load.spritesheet(`${sk}_idle_${d}`, `${base}_Idle_v01.png`, CHAR_FRAME);
      }
    }

    // Elder player look + the three child looks (portraits for the family panel)
    for (const sk of ELDER_VARIANTS) {
      for (const d of DIRS) {
        const base = `characters/player/elder/${sk}_${cap(d)}`;
        this.load.spritesheet(`${sk}_walk_${d}`, `${base}_Walk_v01.png`, CHAR_FRAME);
        this.load.spritesheet(`${sk}_idle_${d}`, `${base}_Idle_v01.png`, CHAR_FRAME);
      }
    }
    for (const sk of CHILD_SPRITES) {
      for (const d of DIRS) {
        const base = `characters/children/${sk}_${cap(d)}`;
        this.load.spritesheet(`${sk}_walk_${d}`, `${base}_Walk_v01.png`, CHAR_FRAME);
        this.load.spritesheet(`${sk}_idle_${d}`, `${base}_Idle_v01.png`, CHAR_FRAME);
      }
      this.load.image(`${sk}_Portrait`, `characters/children/${sk}_Portrait_v01.png`);
    }

    // NPCs: 4-direction walk, Down idle only; portraits for dialogue UI
    for (const n of NPC_SPRITES) {
      const dir = `characters/npcs/${n.folder}/${n.spriteKey}`;
      for (const d of DIRS) {
        this.load.spritesheet(`${n.spriteKey}_walk_${d}`, `${dir}_${cap(d)}_Walk_v01.png`, CHAR_FRAME);
      }
      this.load.spritesheet(`${n.spriteKey}_idle_down`, `${dir}_Down_Idle_v01.png`, CHAR_FRAME);
      for (const mood of ["Neutral", "Happy", "Sad"]) {
        this.load.image(`${n.spriteKey}_Portrait_${mood}`, `${dir}_Portrait_${mood}_v01.png`);
      }
    }

    // Everything else
    for (const path of MISC_ASSETS) {
      const key = path.slice(path.lastIndexOf("/") + 1).replace(/_v01\.png$/, "");
      if (key.startsWith("FX_") && FX_FRAME[key] !== null) {
        const f = FX_FRAME[key] ?? { w: 16, h: 16 };
        this.load.spritesheet(key, path, { frameWidth: f.w, frameHeight: f.h });
      } else this.load.image(key, path);
    }
  }

  create(): void {
    // The title banner is painted key art, not pixel art: smooth it when scaled (everything else stays nearest).
    this.textures.get("UI_000_TitleBanner")?.setFilter(Phaser.Textures.FilterMode.LINEAR);
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
    const chars = [...PLAYER_VARIANTS, ...ELDER_VARIANTS, ...CHILD_SPRITES, ...NPC_SPRITES.map((n) => n.spriteKey)];
    for (const sk of chars) {
      for (const d of DIRS) {
        mk(walkAnimKey(sk, d), `${sk}_walk_${d}`, 8);
        // NPCs only ship a Down idle strip; reuse it for every facing.
        const idleTex = this.textures.exists(`${sk}_idle_${d}`) ? `${sk}_idle_${d}` : `${sk}_idle_down`;
        mk(idleAnimKey(sk, d), idleTex, 2);
      }
    }
    mk("fx-hearts-wedding", "FX_008_Hearts_Wedding", 6);
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
