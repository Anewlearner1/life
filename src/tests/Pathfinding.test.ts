import { describe, expect, it } from "vitest";
import { findPath } from "../systems/Pathfinding";
import { buildCollisionGrid } from "../scenes/collision";
import { propsCatalog } from "../scenes/props";
import { JOB, LOC, MAP } from "../data/ids";
import { jobs } from "../data/jobs";
import { locations, maps } from "../data/maps";
import { schedules } from "../data/schedules";

const parse = (rows: string[]): boolean[][] => rows.map((r) => [...r].map((c) => c === "#"));

describe("findPath", () => {
  it("returns a straight path including both endpoints", () => {
    const grid = parse(["....", "....", "...."]);
    const p = findPath(grid, { x: 0, y: 1 }, { x: 3, y: 1 })!;
    expect(p).toHaveLength(4);
    expect(p[0]).toEqual({ x: 0, y: 1 });
    expect(p[3]).toEqual({ x: 3, y: 1 });
  });

  it("routes around obstacles with 4-direction steps", () => {
    const grid = parse([".....", ".###.", ".....", "....."]);
    const p = findPath(grid, { x: 2, y: 0 }, { x: 2, y: 2 })!;
    expect(p).not.toBeNull();
    for (const t of p) expect(grid[t.y][t.x]).toBe(false);
    for (let i = 1; i < p.length; i++) {
      expect(Math.abs(p[i].x - p[i - 1].x) + Math.abs(p[i].y - p[i - 1].y)).toBe(1);
    }
    expect(p.length).toBe(7); // shortest detour around the 3-wide wall
  });

  it("returns null when unreachable", () => {
    const grid = parse([".#.", ".#.", ".#."]);
    expect(findPath(grid, { x: 0, y: 0 }, { x: 2, y: 2 })).toBeNull();
  });

  it("returns null when the goal is blocked or out of bounds", () => {
    const grid = parse(["..#"]);
    expect(findPath(grid, { x: 0, y: 0 }, { x: 2, y: 0 })).toBeNull();
    expect(findPath(grid, { x: 0, y: 0 }, { x: 5, y: 0 })).toBeNull();
  });

  it("start == goal gives a single-tile path", () => {
    const grid = parse(["..."]);
    expect(findPath(grid, { x: 1, y: 0 }, { x: 1, y: 0 })).toEqual([{ x: 1, y: 0 }]);
  });
});

describe("buildCollisionGrid + maps", () => {
  it("blocks building footprints but keeps door and entry tiles walkable", () => {
    const grid = buildCollisionGrid(maps.map_starter, propsCatalog);
    // house at (4,8): body blocked, door (5,10) walkable, entry (5,11) walkable
    expect(grid[8][4]).toBe(true);
    expect(grid[10][4]).toBe(true);
    expect(grid[10][5]).toBe(false);
    expect(grid[11][5]).toBe(false);
  });

  it("tall props only block their base row", () => {
    const grid = buildCollisionGrid(
      { ...maps.map_starter, props: [{ key: "tree", x: 20, y: 3 }] },
      propsCatalog,
    );
    expect(grid[3][20]).toBe(false);
    expect(grid[4][20]).toBe(true);
    expect(grid[4][21]).toBe(true);
  });

  it("blocks water, fences and hedges from tile codes", () => {
    const grid = buildCollisionGrid(maps.map_starter, propsCatalog);
    expect(grid[3][3]).toBe(true); // pond
    expect(grid[0][5]).toBe(true); // north hedge
    expect(grid[12][2]).toBe(true); // yard fence
  });

  for (const map of Object.values(maps)) {
    describe(map.id, () => {
      const grid = buildCollisionGrid(map, propsCatalog);

      it("has consistent dimensions and known props", () => {
        expect(map.rows).toHaveLength(map.height);
        for (const r of map.rows) expect(r).toHaveLength(map.width);
        for (const p of map.props) expect(propsCatalog[p.key]).toBeDefined();
      });

      it("keeps blocking props on walkable ground and never overlapping", () => {
        const owner = new Map<string, string>();
        for (const p of map.props) {
          const def = propsCatalog[p.key];
          for (let ry = 0; ry < def.h; ry++)
            for (let rx = 0; rx < def.w; rx++) {
              if (def.collision[ry][rx] !== "#") continue;
              const x = p.x + rx;
              const y = p.y + ry;
              expect("., dsWT".includes(map.rows[y][x]), `${p.key}@${x},${y} on '${map.rows[y][x]}'`).toBe(true);
              const k = `${x},${y}`;
              expect(owner.has(k), `${p.key}@${k} overlaps ${owner.get(k)}`).toBe(false);
              owner.set(k, p.key);
            }
        }
      });

      it("spawns on a walkable tile", () => {
        expect(grid[map.spawn.y][map.spawn.x]).toBe(false);
      });

      it("has every location door walkable and reachable from spawn", () => {
        for (const id of map.locationIds) {
          const loc = locations[id];
          expect(loc, id).toBeDefined();
          expect(loc.mapId).toBe(map.id);
          expect(grid[loc.door.y][loc.door.x], `${id} door blocked`).toBe(false);
          expect(findPath(grid, map.spawn, loc.door), `${id} unreachable`).not.toBeNull();
        }
      });

      it("has every prop door tile (furniture fronts included) on walkable ground", () => {
        for (const p of map.props) {
          const d = propsCatalog[p.key].door;
          if (!d) continue;
          expect(grid[p.y + d.y]?.[p.x + d.x], `${p.key}@${p.x},${p.y} door`).toBe(false);
        }
      });

      it("matches location doors to prop doors", () => {
        for (const id of map.locationIds) {
          const loc = locations[id];
          if (loc.type === "gate") continue;
          const match = map.props.some((p) => {
            const d = propsCatalog[p.key].door;
            return d && p.x + d.x === loc.door.x && p.y + d.y === loc.door.y;
          });
          expect(match, `${id} has no prop door at ${loc.door.x},${loc.door.y}`).toBe(true);
        }
      });
    });
  }

  it("interiors are always open, link to the street and every gate pairs with a gate back", () => {
    for (const id of [MAP.homeIn, MAP.shopIn, MAP.cafeIn]) {
      expect(maps[id].unlockConditionId, id).toBeUndefined();
      const exits = maps[id].locationIds.map((l) => locations[l]).filter((l) => l.type === "gate");
      expect(exits, id).toHaveLength(1);
      expect(exits[0].targetMapId).toBe(MAP.starter);
      // exit door is the mat tile in the bottom wall; the spawn sits right above it
      expect(exits[0].door).toEqual({ x: maps[id].spawn.x, y: maps[id].height - 1 });
      expect(maps[id].rows[exits[0].door.y][exits[0].door.x]).toBe("m");
    }
    for (const gate of Object.values(locations).filter((l) => l.type === "gate")) {
      const back = Object.values(locations).find((l) => l.type === "gate" && l.mapId === gate.targetMapId && l.targetMapId === gate.mapId);
      expect(back, `${gate.id} has no gate back`).toBeDefined();
    }
    expect(locations[LOC.home]).toMatchObject({ type: "gate", targetMapId: MAP.homeIn });
    expect(locations[LOC.shop]).toMatchObject({ type: "gate", targetMapId: MAP.shopIn });
    expect(locations[LOC.cafe]).toMatchObject({ type: "gate", targetMapId: MAP.cafeIn });
  });

  it("indoor spots have the right types and the barista works at the cafe counter", () => {
    expect(locations[LOC.homeBed].type).toBe("home");
    expect(locations[LOC.shopCounter].type).toBe("shop");
    expect(locations[LOC.cafeCounter]).toMatchObject({ type: "workplace", mapId: MAP.cafeIn });
    expect(jobs[JOB.barista].workplaceLocationId).toBe(LOC.cafeCounter);
  });

  it("every schedule location exists and scheduled NPCs stand on free tiles of that map", () => {
    const grids: Record<string, boolean[][]> = {};
    for (const sch of Object.values(schedules))
      for (const e of sch.entries) {
        const loc = locations[e.locationId];
        expect(loc, `${sch.id} -> ${e.locationId}`).toBeDefined();
        const grid = (grids[loc.mapId] ??= buildCollisionGrid(maps[loc.mapId], propsCatalog));
        const stand = loc.npcStand ?? { x: loc.door.x, y: loc.door.y + 1 };
        expect(grid[stand.y]?.[stand.x], `${e.locationId} stand ${stand.x},${stand.y}`).toBe(false);
      }
    expect(schedules.sch_npc_001.entries.some((e) => e.locationId === LOC.cafeCounter && e.activity === "work")).toBe(true);
    expect(schedules.sch_npc_002.entries.some((e) => e.locationId === LOC.shopCounter && e.activity === "work")).toBe(true);
  });

  it("rural map is locked behind cond_unlock_rural and gates link both ways", () => {
    expect(maps.map_rural.unlockConditionId).toBe("cond_unlock_rural");
    expect(locations.loc_gate_east.targetMapId).toBe("map_rural");
    expect(locations.loc_gate_west.targetMapId).toBe("map_starter");
    expect(locations.loc_gate_east.type).toBe("gate");
  });
});
