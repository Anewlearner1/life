// Prop catalog: key -> image, footprint (tiles), collision rows, door offsets.
// Phaser-free on purpose: imported by the collision builder, tests and the scene.
// Anchor: the image's bottom-left corner sits at the bottom-left of the footprint
// (same convention as assets/buildings/collision.json). MapProp x,y = footprint top-left tile.

export type PropDef = {
  key: string;
  /** Path under assets/ (no leading slash). */
  texturePath: string;
  /** Footprint in tiles. Image size in px = footprint * 16. */
  w: number;
  h: number;
  /** One string per footprint row: '#' blocked, '.' free, 'D' door (walkable). */
  collision: string[];
  /** Door tile offset (col,row) from the footprint top-left, if the prop is enterable. */
  door?: { x: number; y: number };
  /** Tile in front of the door where the player normally arrives. */
  entry?: { x: number; y: number };
  /** Decoration lying on the ground (always drawn below characters). */
  ground?: boolean;
};

const b = (
  key: string,
  texturePath: string,
  w: number,
  h: number,
  collision: string[],
  extra: Partial<PropDef> = {},
): PropDef => ({ key, texturePath, w, h, collision, ...extra });

export const propsCatalog: Record<string, PropDef> = {
  // Buildings (collision straight from assets/buildings/collision.json)
  house: b("house", "buildings/houses/BLD_001_House_v01.png", 3, 3, ["###", "###", "#D#"], {
    door: { x: 1, y: 2 },
    entry: { x: 1, y: 3 },
  }),
  shop: b("shop", "buildings/shops/BLD_002_Shop_v01.png", 4, 3, ["####", "####", "##D#"], {
    door: { x: 2, y: 2 },
    entry: { x: 2, y: 3 },
  }),
  cafe: b("cafe", "buildings/workplaces/BLD_003_Cafe_v01.png", 4, 3, ["####", "####", "##D#"], {
    door: { x: 2, y: 2 },
    entry: { x: 2, y: 3 },
  }),
  gazebo: b("gazebo", "buildings/social/BLD_004_Park_Gazebo_v01.png", 3, 3, ["###", "###", "#D#"], {
    door: { x: 1, y: 2 },
    entry: { x: 1, y: 3 },
  }),

  // Tall props only block their base row.
  tree: b("tree", "maps/urban/MAP_005_Nature_Tree_v01.png", 2, 2, ["..", "##"]),
  lamp: b("lamp", "maps/urban/MAP_006_Deco_Streetlamp_v01.png", 1, 2, [".", "#"]),
  trafficsign: b("trafficsign", "maps/urban/MAP_006_Deco_TrafficSign_v01.png", 1, 2, [".", "#"]),

  // Small props
  bush: b("bush", "maps/urban/MAP_005_Nature_Bush_v01.png", 1, 1, ["#"]),
  rock: b("rock", "maps/urban/MAP_005_Nature_Rock_v01.png", 1, 1, ["#"]),
  flower: b("flower", "maps/urban/MAP_005_Nature_FlowerPatch_v01.png", 1, 1, ["."], { ground: true }),
  bench: b("bench", "maps/urban/MAP_006_Deco_Bench_v01.png", 2, 1, ["##"]),
  trash: b("trash", "maps/urban/MAP_006_Deco_TrashCan_v01.png", 1, 1, ["#"]),
  mailbox: b("mailbox", "maps/urban/MAP_006_Deco_Mailbox_v01.png", 1, 1, ["#"]),
  signboard: b("signboard", "maps/urban/MAP_006_Deco_Signboard_v01.png", 1, 1, ["#"]),
};

export const propTextureKey = (key: string): string => `prop_${key}`;

/** Absolute tile of a prop's door, or null if the prop is not enterable / unknown. */
export function propDoorTile(
  prop: { key: string; x: number; y: number },
  catalog: Record<string, PropDef> = propsCatalog,
): { x: number; y: number } | null {
  const def = catalog[prop.key];
  if (!def || !def.door) return null;
  return { x: prop.x + def.door.x, y: prop.y + def.door.y };
}
