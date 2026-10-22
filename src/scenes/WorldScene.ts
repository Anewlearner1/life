import Phaser from "phaser";
import { GameConfig } from "../game/GameConfig";
import type { Facing, MapDefinition, WorldPosition } from "../game/types";
import { findPath, type Tile } from "../systems/Pathfinding";
import { buildCollisionGrid } from "./collision";
import { idleAnimKey, playerSpriteKeyFor, walkAnimKey } from "./BootScene";
import { propDoorTile, propsCatalog, propTextureKey } from "./props";
import type { InteractTarget, WorldBridge, WorldSceneData } from "./WorldBridge";

const TS = GameConfig.movement.tileSize;
const FOOT_INSET = 2; // px the character's feet sit above the tile's bottom edge
const TARGET_TILES_ACROSS = 14; // aim for ~12-16 tiles across the narrow screen side

// ---- tile code -> frame --------------------------------------------------------------
const GROUND = { grassa: 0, grassb: 1, dirt: 2, sidewalk: 3, floorwood: 4, floortile: 5 };
const ROAD = {
  road_h: 0, road_v: 1, crossroad: 10, crosswalk_h: 11, crosswalk_v: 12,
  curb_top: 13, curb_bottom: 14, curb_left: 15, curb_right: 16,
  curb_corner_tl: 17, curb_corner_tr: 18, curb_corner_bl: 19, curb_corner_br: 20,
  path_edge_top: 21, path_edge_bottom: 22, path_edge_left: 23, path_edge_right: 24,
  path_h: 29, path_v: 30,
};
const BLOCK = { brick: 0, fence_h: 1, fence_v: 2, hedge: 3, water: 4 };
const INTERIOR = { wall_a: 0, wall_b: 1, trim: 2, door_mat: 3 };
const ROAD_CODES = new Set(["r", "R", "+", "=", "|"]);
const GRASS_CODES = new Set([".", ","]);

type Frame = [string, number];
type Seg = { from: Tile; to: Tile; t: number };

type NpcView = {
  id: string;
  spriteKey: string;
  sprite: Phaser.GameObjects.Sprite;
  tile: Tile; // last completed tile
  target: Tile; // last tile requested by state
  seg: Seg | null;
  queue: Tile[];
  facing: Facing;
};

type LocHit = { id: string; door: Tile; rect: { x0: number; y0: number; x1: number; y1: number } };

const dirOf = (a: Tile, b: Tile): Facing =>
  Math.abs(b.x - a.x) >= Math.abs(b.y - a.y) ? (b.x >= a.x ? "right" : "left") : b.y >= a.y ? "down" : "up";

export class WorldScene extends Phaser.Scene {
  private bridge!: WorldBridge;
  private map!: MapDefinition;
  private grid: boolean[][] = [];
  private groundKey?: string;
  private layerObjs: Phaser.GameObjects.GameObject[] = [];
  private locHits: LocHit[] = [];

  private player!: Phaser.GameObjects.Sprite;
  private pTile: Tile = { x: 0, y: 0 };
  private pSeg: Seg | null = null;
  private pQueue: Tile[] = [];
  private pFacing: Facing = "down";
  private pending: InteractTarget | null = null;
  private pendingFace: Facing | null = null;
  private pMoving = false;

  private npcs = new Map<string, NpcView>();
  private zoom = 2;

  constructor() {
    super("World");
  }

  init(data: WorldSceneData): void {
    this.bridge = data.bridge;
  }

  create(): void {
    this.cameras.main.setBackgroundColor(0x181425);
    this.cameras.main.roundPixels = true;
    this.input.on("pointerdown", this.onPointer, this);
    this.scale.on("resize", this.onResize, this);
    this.events.once(Phaser.Scenes.Events.SHUTDOWN, () => {
      this.input.off("pointerdown", this.onPointer, this);
      this.scale.off("resize", this.onResize, this);
      this.clearMap();
    });
    const st = this.bridge.getState();
    this.loadMap(st.currentMapId, st.player.position);
  }

  // ------------------------------------------------------------------ public API
  /** Rebuild all layers for `mapId` and place the player at state.player.position (or map spawn). */
  loadMap(mapId: string, pos?: WorldPosition): void {
    const content = this.bridge.getContent();
    const map = content.maps[mapId];
    if (!map) throw new Error(`WorldScene.loadMap: unknown map ${mapId}`);
    this.clearMap();
    this.map = map;
    this.grid = buildCollisionGrid(map, propsCatalog);
    this.buildGround(map);
    this.buildProps(map);
    this.buildLocHits(map);

    const sp = pos ?? this.bridge.getState().player.position;
    const useSpawn = sp.mapId !== mapId;
    const tile = useSpawn ? map.spawn : { x: sp.x, y: sp.y };
    this.pTile = { x: tile.x, y: tile.y };
    this.pFacing = useSpawn ? "down" : sp.facing;
    this.pSeg = null;
    this.pQueue = [];
    this.pending = null;
    this.pMoving = false;
    this.player = this.add.sprite(0, 0, `${this.playerKey()}_idle_down`).setOrigin(0.5, 1);
    this.layerObjs.push(this.player);
    this.placeSprite(this.player, this.pTile.x * TS + TS / 2, (this.pTile.y + 1) * TS - FOOT_INSET);
    this.playChar(this.player, this.playerKey(), "idle", this.pFacing);

    this.applyZoom();
    this.syncNpcs(0, true);
    this.updateCamera();
  }

  /** Move the player (and the map if needed) to an arbitrary position, cancelling any walk. */
  placePlayer(pos: WorldPosition): void {
    if (pos.mapId !== this.map.id) {
      this.loadMap(pos.mapId, pos);
      return;
    }
    this.pSeg = null;
    this.pQueue = [];
    this.pending = null;
    this.pTile = { x: pos.x, y: pos.y };
    this.pFacing = pos.facing;
    this.placeSprite(this.player, pos.x * TS + TS / 2, (pos.y + 1) * TS - FOOT_INSET);
    this.playChar(this.player, this.playerKey(), "idle", this.pFacing);
    this.pMoving = false;
  }

  /** Sprite family for the player's chosen outfit. */
  private playerKey(): string {
    const { outfitId, hairId } = this.bridge.getState().player.appearance;
    return playerSpriteKeyFor(outfitId, hairId);
  }

  get currentMapId(): string {
    return this.map?.id;
  }

  getPlayerTile(): Tile {
    return { ...this.pTile };
  }

  /** Tile -> canvas CSS pixel position of the tile centre (handy for overlays and tests). */
  tileToScreen(tx: number, ty: number): { x: number; y: number } {
    const wv = this.cameras.main.worldView;
    return { x: (tx * TS + TS / 2 - wv.x) * this.zoom, y: (ty * TS + TS / 2 - wv.y) * this.zoom };
  }

  /** Programmatic equivalent of tapping a tile. */
  tapTile(tx: number, ty: number): void {
    this.handleTap((tx + 0.5) * TS, (ty + 0.5) * TS);
  }

  // ------------------------------------------------------------------ map building
  private clearMap(): void {
    for (const o of this.layerObjs) o.destroy();
    this.layerObjs = [];
    for (const v of this.npcs.values()) v.sprite.destroy();
    this.npcs.clear();
    if (this.groundKey && this.textures.exists(this.groundKey)) this.textures.remove(this.groundKey);
    this.groundKey = undefined;
  }

  private codeAt(x: number, y: number): string {
    if (x < 0 || y < 0 || x >= this.map.width || y >= this.map.height) return "";
    return this.map.rows[y][x] ?? "";
  }

  private tileFrames(x: number, y: number): Frame[] {
    const c = this.codeAt(x, y);
    const N = this.codeAt(x, y - 1);
    const S = this.codeAt(x, y + 1);
    const W = this.codeAt(x - 1, y);
    const E = this.codeAt(x + 1, y);
    const g = (k: keyof typeof GROUND): Frame => ["tiles_ground", GROUND[k]];
    const r = (k: keyof typeof ROAD): Frame => ["tiles_road", ROAD[k]];
    switch (c) {
      case ".": return [g("grassa")];
      case ",": return [g("grassb")];
      case "W": return [g("floorwood")];
      case "T": return [g("floortile")];
      case "i": return [["tiles_interior", INTERIOR.wall_a]];
      case "j": return [["tiles_interior", INTERIOR.wall_b]];
      case "v": return [["tiles_interior", INTERIOR.trim]];
      case "m": return [["tiles_interior", INTERIOR.door_mat]];
      case "r": return [r("road_h")];
      case "R": return [r("road_v")];
      case "+": return [r("crossroad")];
      case "=": return [r("crosswalk_h")];
      case "|": return [r("crosswalk_v")];
      case "s": {
        const rd = (k: string) => ROAD_CODES.has(k);
        if (rd(N) && rd(W)) return [r("curb_corner_tl")];
        if (rd(N) && rd(E)) return [r("curb_corner_tr")];
        if (rd(S) && rd(W)) return [r("curb_corner_bl")];
        if (rd(S) && rd(E)) return [r("curb_corner_br")];
        if (rd(N)) return [r("curb_top")];
        if (rd(S)) return [r("curb_bottom")];
        if (rd(W)) return [r("curb_left")];
        if (rd(E)) return [r("curb_right")];
        return [g("sidewalk")];
      }
      case "d": {
        const gr = (k: string) => GRASS_CODES.has(k);
        if (gr(W) && gr(E)) return [r("path_v")];
        if (gr(N) && gr(S)) return [r("path_h")];
        if (gr(N)) return [r("path_edge_top")];
        if (gr(S)) return [r("path_edge_bottom")];
        if (gr(W)) return [r("path_edge_left")];
        if (gr(E)) return [r("path_edge_right")];
        return [g("dirt")];
      }
      case "w": return [["tiles_blockers", BLOCK.brick]];
      case "h": return [["tiles_blockers", BLOCK.hedge]];
      case "~": return [["tiles_blockers", BLOCK.water]];
      case "f": {
        const link = (k: string) => k === "f" || k === "h";
        const horizontal = link(W) || link(E) || !(N === "f" || S === "f");
        return [g("grassa"), ["tiles_blockers", horizontal ? BLOCK.fence_h : BLOCK.fence_v]];
      }
      default: return [g("grassa")];
    }
  }

  private buildGround(map: MapDefinition): void {
    this.groundKey = `ground_${map.id}_${Date.now()}`;
    const ct = this.textures.createCanvas(this.groundKey, map.width * TS, map.height * TS)!;
    const waterTiles: Tile[] = [];
    for (let y = 0; y < map.height; y++)
      for (let x = 0; x < map.width; x++) {
        for (const [key, frame] of this.tileFrames(x, y)) ct.drawFrame(key, frame, x * TS, y * TS);
        if (this.codeAt(x, y) === "~") waterTiles.push({ x, y });
      }
    ct.refresh();
    this.layerObjs.push(this.add.image(0, 0, this.groundKey).setOrigin(0, 0).setDepth(-1000));
    for (const t of waterTiles) {
      const s = this.add.sprite(t.x * TS, t.y * TS, "tiles_blockers", BLOCK.water).setOrigin(0, 0).setDepth(-999);
      s.anims.play({ key: "water", startFrame: (t.x + t.y) % 2 });
      this.layerObjs.push(s);
    }
  }

  private buildProps(map: MapDefinition): void {
    for (const p of map.props) {
      const def = propsCatalog[p.key];
      if (!def) continue;
      const img = this.add.image(p.x * TS, (p.y + def.h) * TS - (def.lift ?? 0), propTextureKey(p.key)).setOrigin(0, 1);
      // Enterable buildings sort by their door row (not the bottom edge) so a character standing on the
      // door tile is drawn in front of the building; everything else sorts by its bottom edge.
      // Furniture whose door lies in front of it (outside the footprint) sorts normally; items lying on
      // furniture (lift) draw just above their base.
      const doorInside = !!def.door && def.door.y < def.h;
      img.setDepth(def.ground ? -500 : (p.y + def.h - (doorInside ? 1 : 0)) * TS + (doorInside ? 1 : 0) + (def.lift ? 0.5 : 0));
      this.layerObjs.push(img);
    }
  }

  private buildLocHits(map: MapDefinition): void {
    const content = this.bridge.getContent();
    this.locHits = [];
    for (const id of map.locationIds) {
      const loc = content.locations[id];
      if (!loc) continue;
      const door = { x: loc.door.x, y: loc.door.y };
      let rect = { x0: door.x, y0: door.y, x1: door.x, y1: door.y };
      for (const p of map.props) {
        const d = propDoorTile(p);
        const def = propsCatalog[p.key];
        if (d && d.x === door.x && d.y === door.y) {
          rect = { x0: p.x, y0: p.y, x1: p.x + def.w - 1, y1: p.y + def.h - 1 };
          break;
        }
      }
      this.locHits.push({ id, door, rect });
    }
  }

  // ------------------------------------------------------------------ camera
  private onResize = (): void => {
    this.applyZoom();
    this.updateCamera();
  };

  private applyZoom(): void {
    const { width, height } = this.scale;
    this.zoom = Math.max(1, Math.round(Math.min(width, height) / (TARGET_TILES_ACROSS * TS)));
    this.cameras.main.setZoom(this.zoom);
  }

  private updateCamera(): void {
    if (!this.player || !this.map) return;
    const cam = this.cameras.main;
    const viewW = cam.width / this.zoom;
    const viewH = cam.height / this.zoom;
    const mapW = this.map.width * TS;
    const mapH = this.map.height * TS;
    const px = this.player.x;
    const py = this.player.y - 8;
    const cx = mapW <= viewW ? mapW / 2 : Phaser.Math.Clamp(px, viewW / 2, mapW - viewW / 2);
    const cy = mapH <= viewH ? mapH / 2 : Phaser.Math.Clamp(py, viewH / 2, mapH - viewH / 2);
    const snap = (v: number) => Math.round(v * this.zoom) / this.zoom;
    cam.setScroll(snap(cx - cam.width / 2), snap(cy - cam.height / 2));
  }

  // ------------------------------------------------------------------ helpers
  private placeSprite(s: Phaser.GameObjects.Sprite, x: number, y: number): void {
    s.setPosition(x, y);
    s.setDepth(y + 0.1);
  }

  private playChar(s: Phaser.GameObjects.Sprite, sk: string, kind: "walk" | "idle", dir: Facing): void {
    const key = kind === "walk" ? walkAnimKey(sk, dir) : idleAnimKey(sk, dir);
    if (this.anims.exists(key)) s.play(key, true);
  }

  private walkable(t: Tile): boolean {
    return t.x >= 0 && t.y >= 0 && t.x < this.map.width && t.y < this.map.height && !this.grid[t.y][t.x];
  }

  /** Where a new route should start: the end of the segment in progress, else the current tile. */
  private routeStart(): Tile {
    return this.pSeg ? this.pSeg.to : this.pTile;
  }

  private showMarker(tx: number, ty: number, ok: boolean): void {
    const g = this.add.graphics().setDepth(100000);
    g.lineStyle(1, ok ? 0xffffff : 0xe43b44, 1);
    g.strokeRect(tx * TS + 1.5, ty * TS + 1.5, TS - 3, TS - 3);
    g.fillStyle(ok ? 0xfee761 : 0xe43b44, 0.35);
    g.fillRect(tx * TS + 2, ty * TS + 2, TS - 4, TS - 4);
    g.setPosition(0, 0);
    this.tweens.add({
      targets: g,
      alpha: 0,
      duration: 450,
      ease: "Quad.easeIn",
      onComplete: () => g.destroy(),
    });
  }

  // ------------------------------------------------------------------ input
  private onPointer(pointer: Phaser.Input.Pointer): void {
    if (this.bridge.isInputBlocked()) return;
    for (const sc of this.scene.manager.getScenes(true)) {
      if (sc === this) continue;
      try {
        if (sc.input.hitTestPointer(pointer).length > 0) return; // UI scene handled it
      } catch {
        /* scene without input plugin */
      }
    }
    // pointer.worldX/Y are only refreshed when interactive objects exist, so convert explicitly.
    const wp = this.cameras.main.getWorldPoint(pointer.x, pointer.y);
    this.handleTap(wp.x, wp.y);
  }

  private handleTap(wx: number, wy: number): void {
    if (!this.map) return;
    const tx = Math.floor(wx / TS);
    const ty = Math.floor(wy / TS);
    if (tx < 0 || ty < 0 || tx >= this.map.width || ty >= this.map.height) return;

    // 1. NPC under the finger (sprite is 16x24, feet at the bottom)
    let bestNpc: NpcView | null = null;
    let bestD = Infinity;
    for (const v of this.npcs.values()) {
      const s = v.sprite;
      if (wx >= s.x - 10 && wx <= s.x + 10 && wy >= s.y - 26 && wy <= s.y + 4) {
        const d = Math.abs(wx - s.x) + Math.abs(wy - (s.y - 10));
        if (d < bestD) {
          bestD = d;
          bestNpc = v;
        }
      }
    }
    if (bestNpc) {
      this.walkToNpc(bestNpc);
      return;
    }

    // 2. Location: its door tile or the building footprint
    const hit = this.locHits.find((h) => tx >= h.rect.x0 && tx <= h.rect.x1 && ty >= h.rect.y0 && ty <= h.rect.y1);
    if (hit) {
      this.showMarker(hit.door.x, hit.door.y, true);
      this.walkTo(hit.door, { kind: "location", id: hit.id }, "up");
      return;
    }

    // 3. Plain ground: nearest reachable tile when the tap lands on an obstacle
    const dest = this.nearestReachable({ x: tx, y: ty });
    if (!dest) {
      this.showMarker(tx, ty, false);
      return;
    }
    this.showMarker(dest.x, dest.y, true);
    this.walkTo(dest, null, null);
  }

  private nearestReachable(t: Tile): Tile | null {
    if (this.walkable(t)) return t;
    const start = this.routeStart();
    let best: Tile | null = null;
    let bestLen = Infinity;
    for (let r = 1; r <= 3; r++) {
      for (let dy = -r; dy <= r; dy++)
        for (let dx = -r; dx <= r; dx++) {
          if (Math.abs(dx) + Math.abs(dy) !== r) continue;
          const c = { x: t.x + dx, y: t.y + dy };
          if (!this.walkable(c)) continue;
          const p = findPath(this.grid, start, c);
          if (p && p.length < bestLen) {
            best = c;
            bestLen = p.length;
          }
        }
      if (best) return best;
    }
    return null;
  }

  private walkTo(dest: Tile, interact: InteractTarget | null, faceAtEnd: Facing | null): void {
    const path = findPath(this.grid, this.routeStart(), dest);
    if (!path) {
      this.showMarker(dest.x, dest.y, false);
      return;
    }
    this.pQueue = path.slice(1);
    this.pending = interact;
    this.pendingFace = faceAtEnd;
    if (!this.pSeg && this.pQueue.length === 0) this.finishWalk();
  }

  private walkToNpc(v: NpcView): void {
    const npcTile = v.seg ? v.seg.to : v.tile;
    const start = this.routeStart();
    const target: InteractTarget = { kind: "npc", id: v.id };
    // Already adjacent (or sharing the tile)? Interact right away.
    let best: { tile: Tile; len: number } | null = null;
    const cands: Tile[] = [start, { x: npcTile.x, y: npcTile.y + 1 }, { x: npcTile.x - 1, y: npcTile.y }, { x: npcTile.x + 1, y: npcTile.y }, { x: npcTile.x, y: npcTile.y - 1 }];
    for (const c of cands) {
      const adjacent = Math.abs(c.x - npcTile.x) + Math.abs(c.y - npcTile.y) <= 1;
      if (!adjacent || !this.walkable(c)) continue;
      const p = findPath(this.grid, start, c);
      if (p && (!best || p.length < best.len)) best = { tile: c, len: p.length };
    }
    if (!best) {
      this.showMarker(npcTile.x, npcTile.y, false);
      return;
    }
    this.showMarker(npcTile.x, npcTile.y, true);
    const face = best.tile.x === npcTile.x && best.tile.y === npcTile.y ? null : dirOf(best.tile, npcTile);
    this.walkTo(best.tile, target, face);
  }

  // ------------------------------------------------------------------ per-frame
  update(_time: number, delta: number): void {
    if (!this.map) return;
    this.updatePlayer(delta);
    this.syncNpcs(delta, false);
    this.updateCamera();
  }

  private finishWalk(): void {
    if (this.pMoving) {
      this.pMoving = false;
    }
    const p = this.pending;
    if (this.pendingFace) this.pFacing = this.pendingFace;
    else if (p?.kind === "location") this.pFacing = "up";
    this.playChar(this.player, this.playerKey(), "idle", this.pFacing);
    this.pending = null;
    this.pendingFace = null;
    if (p) this.bridge.onInteract(p);
  }

  private updatePlayer(delta: number): void {
    if (this.bridge.isInputBlocked()) {
      this.pQueue = [];
      this.pending = null;
    }
    let budget = (delta / 1000) * GameConfig.movement.tilesPerSecond;
    while (budget > 0) {
      if (!this.pSeg) {
        const next = this.pQueue.shift();
        if (!next) break;
        this.pSeg = { from: { ...this.pTile }, to: next, t: 0 };
        this.pFacing = dirOf(this.pTile, next);
        this.pMoving = true;
        this.playChar(this.player, this.playerKey(), "walk", this.pFacing);
      }
      const seg = this.pSeg;
      const adv = Math.min(budget, 1 - seg.t);
      seg.t += adv;
      budget -= adv;
      if (seg.t >= 1 - 1e-9) {
        this.pTile = seg.to;
        this.pSeg = null;
        this.bridge.onPlayerStep({ mapId: this.map.id, x: seg.to.x, y: seg.to.y, facing: this.pFacing });
        if (this.pQueue.length === 0) {
          this.syncPlayerSprite();
          this.finishWalk();
          break;
        }
      }
    }
    this.syncPlayerSprite();
  }

  private syncPlayerSprite(): void {
    const seg = this.pSeg;
    const fx = seg ? seg.from.x + (seg.to.x - seg.from.x) * seg.t : this.pTile.x;
    const fy = seg ? seg.from.y + (seg.to.y - seg.from.y) * seg.t : this.pTile.y;
    this.placeSprite(this.player, fx * TS + TS / 2, (fy + 1) * TS - FOOT_INSET);
  }

  // ------------------------------------------------------------------ NPCs
  private syncNpcs(delta: number, snap: boolean): void {
    const st = this.bridge.getState();
    const content = this.bridge.getContent();
    for (const [id, npc] of Object.entries(st.npcs)) {
      let v = this.npcs.get(id);
      if (npc.position.mapId !== this.map.id) {
        if (v) {
          v.sprite.destroy();
          this.npcs.delete(id);
        }
        continue;
      }
      if (!v) {
        const sk = content.npcs[id]?.spriteKey;
        if (!sk || !this.textures.exists(`${sk}_idle_down`)) continue;
        const sprite = this.add.sprite(0, 0, `${sk}_idle_down`).setOrigin(0.5, 1);
        v = {
          id,
          spriteKey: sk,
          sprite,
          tile: { x: npc.position.x, y: npc.position.y },
          target: { x: npc.position.x, y: npc.position.y },
          seg: null,
          queue: [],
          facing: npc.position.facing,
        };
        this.npcs.set(id, v);
        this.placeSprite(sprite, v.tile.x * TS + TS / 2, (v.tile.y + 1) * TS - FOOT_INSET);
        this.playChar(sprite, sk, "idle", v.facing);
      }
      if (v.target.x !== npc.position.x || v.target.y !== npc.position.y) {
        v.target = { x: npc.position.x, y: npc.position.y };
        const from = v.seg ? v.seg.to : v.tile;
        const path = snap ? null : findPath(this.grid, from, v.target);
        if (path && path.length <= 80) {
          v.queue = path.slice(1);
        } else {
          // unreachable (or huge) jump: teleport
          v.queue = [];
          v.seg = null;
          v.tile = { ...v.target };
          this.placeSprite(v.sprite, v.tile.x * TS + TS / 2, (v.tile.y + 1) * TS - FOOT_INSET);
          this.playChar(v.sprite, v.spriteKey, "idle", npc.position.facing);
        }
      }
      this.stepNpc(v, delta, npc.position.facing);
    }
  }

  private stepNpc(v: NpcView, delta: number, restFacing: Facing): void {
    const speed = GameConfig.movement.tilesPerSecond * (v.queue.length > 12 ? 2 : 1);
    let budget = (delta / 1000) * speed;
    let moved = false;
    while (budget > 0) {
      if (!v.seg) {
        const next = v.queue.shift();
        if (!next) break;
        v.seg = { from: { ...v.tile }, to: next, t: 0 };
        v.facing = dirOf(v.tile, next);
        this.playChar(v.sprite, v.spriteKey, "walk", v.facing);
      }
      const seg = v.seg;
      const adv = Math.min(budget, 1 - seg.t);
      seg.t += adv;
      budget -= adv;
      moved = true;
      if (seg.t >= 1 - 1e-9) {
        v.tile = seg.to;
        v.seg = null;
        if (v.queue.length === 0) {
          v.facing = restFacing;
          this.playChar(v.sprite, v.spriteKey, "idle", v.facing);
        }
      }
    }
    if (moved || v.seg) {
      const seg = v.seg;
      const fx = seg ? seg.from.x + (seg.to.x - seg.from.x) * seg.t : v.tile.x;
      const fy = seg ? seg.from.y + (seg.to.y - seg.from.y) * seg.t : v.tile.y;
      this.placeSprite(v.sprite, fx * TS + TS / 2, (fy + 1) * TS - FOOT_INSET);
    }
  }
}

