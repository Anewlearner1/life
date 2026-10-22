// Pure 4-direction A* on a tile grid. No Phaser imports.

export type Tile = { x: number; y: number };

/**
 * grid[y][x] === true means blocked. Returns the tile sequence from `from` to `to`
 * INCLUDING both endpoints (start === goal -> [from]), or null when unreachable,
 * out of bounds, or the goal tile is blocked. The start tile is allowed to be blocked.
 */
export function findPath(grid: boolean[][], from: Tile, to: Tile): Tile[] | null {
  const h = grid.length;
  const w = h > 0 ? grid[0].length : 0;
  const inside = (x: number, y: number) => x >= 0 && y >= 0 && x < w && y < h;
  if (!inside(from.x, from.y) || !inside(to.x, to.y)) return null;
  if (grid[to.y][to.x]) return null;
  if (from.x === to.x && from.y === to.y) return [{ x: from.x, y: from.y }];

  const idx = (x: number, y: number) => y * w + x;
  const g = new Float64Array(w * h).fill(Infinity);
  const parent = new Int32Array(w * h).fill(-1);
  const closed = new Uint8Array(w * h);
  const heur = (x: number, y: number) => Math.abs(x - to.x) + Math.abs(y - to.y);

  // Binary min-heap of [f, h, index]
  const heap: [number, number, number][] = [];
  const less = (a: [number, number, number], b: [number, number, number]) =>
    a[0] < b[0] || (a[0] === b[0] && a[1] < b[1]);
  const push = (n: [number, number, number]) => {
    heap.push(n);
    let i = heap.length - 1;
    while (i > 0) {
      const p = (i - 1) >> 1;
      if (!less(heap[i], heap[p])) break;
      [heap[i], heap[p]] = [heap[p], heap[i]];
      i = p;
    }
  };
  const pop = (): [number, number, number] => {
    const top = heap[0];
    const last = heap.pop()!;
    if (heap.length > 0) {
      heap[0] = last;
      let i = 0;
      for (;;) {
        const l = 2 * i + 1;
        const r = l + 1;
        let m = i;
        if (l < heap.length && less(heap[l], heap[m])) m = l;
        if (r < heap.length && less(heap[r], heap[m])) m = r;
        if (m === i) break;
        [heap[i], heap[m]] = [heap[m], heap[i]];
        i = m;
      }
    }
    return top;
  };

  const s = idx(from.x, from.y);
  const goal = idx(to.x, to.y);
  g[s] = 0;
  push([heur(from.x, from.y), heur(from.x, from.y), s]);
  const dirs = [
    [0, -1],
    [1, 0],
    [0, 1],
    [-1, 0],
  ];
  while (heap.length > 0) {
    const [, , cur] = pop();
    if (closed[cur]) continue;
    closed[cur] = 1;
    if (cur === goal) break;
    const cx = cur % w;
    const cy = (cur - cx) / w;
    for (const [dx, dy] of dirs) {
      const nx = cx + dx;
      const ny = cy + dy;
      if (!inside(nx, ny) || grid[ny][nx]) continue;
      const ni = idx(nx, ny);
      if (closed[ni]) continue;
      const ng = g[cur] + 1;
      if (ng < g[ni]) {
        g[ni] = ng;
        parent[ni] = cur;
        const hh = heur(nx, ny);
        push([ng + hh, hh, ni]);
      }
    }
  }
  if (parent[goal] === -1) return null;
  const out: Tile[] = [];
  for (let c = goal; c !== -1; c = parent[c]) {
    const x = c % w;
    out.push({ x, y: (c - x) / w });
    if (c === s) break;
  }
  return out.reverse();
}
