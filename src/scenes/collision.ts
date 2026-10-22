import type { MapDefinition } from "../game/types";
import { propsCatalog, type PropDef } from "./props";

/** Tile codes that cannot be walked on (see docs/ARCHITECTURE.md legend). */
export const BLOCKING_TILES = new Set(["w", "f", "h", "~", "i", "j", "v"]);

/**
 * Build the blocked-grid for a map: grid[y][x] === true means blocked.
 * Combines blocking tile codes with prop collision rows ('#' blocked; '.' and 'D' walkable).
 * Props that overhang the map edge are clipped.
 */
export function buildCollisionGrid(
  map: MapDefinition,
  catalog: Record<string, PropDef> = propsCatalog,
): boolean[][] {
  const grid: boolean[][] = [];
  for (let y = 0; y < map.height; y++) {
    const row: boolean[] = [];
    const line = map.rows[y] ?? "";
    for (let x = 0; x < map.width; x++) row.push(BLOCKING_TILES.has(line[x] ?? "."));
    grid.push(row);
  }
  for (const p of map.props) {
    const def = catalog[p.key];
    if (!def) continue;
    for (let ry = 0; ry < def.h; ry++) {
      const crow = def.collision[ry] ?? "";
      for (let rx = 0; rx < def.w; rx++) {
        if (crow[rx] !== "#") continue;
        const gx = p.x + rx;
        const gy = p.y + ry;
        if (gy >= 0 && gy < map.height && gx >= 0 && gx < map.width) grid[gy][gx] = true;
      }
    }
  }
  return grid;
}
