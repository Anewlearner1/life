import { GameConfig } from "../game/GameConfig";
import type { GameState, SaveData } from "../game/types";
import { migrate } from "./SaveMigration";

export interface SaveStorage {
  get(key: string): Promise<string | null>;
  set(key: string, value: string): Promise<void>;
  delete(key: string): Promise<void>;
}

export class MemoryStorage implements SaveStorage {
  private data = new Map<string, string>();
  async get(key: string) {
    return this.data.get(key) ?? null;
  }
  async set(key: string, value: string) {
    this.data.set(key, value);
  }
  async delete(key: string) {
    this.data.delete(key);
  }
}

export class LocalStorageStorage implements SaveStorage {
  private key = (k: string) => `${GameConfig.save.dbName}:${k}`;
  async get(key: string) {
    return localStorage.getItem(this.key(key));
  }
  async set(key: string, value: string) {
    localStorage.setItem(this.key(key), value);
  }
  async delete(key: string) {
    localStorage.removeItem(this.key(key));
  }
}

const STORE = "saves";

export class IndexedDBStorage implements SaveStorage {
  private db?: Promise<IDBDatabase>;

  private open(): Promise<IDBDatabase> {
    this.db ??= new Promise<IDBDatabase>((resolve, reject) => {
      const req = indexedDB.open(GameConfig.save.dbName, 1);
      req.onupgradeneeded = () => req.result.createObjectStore(STORE);
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    }).catch((e) => {
      this.db = undefined;
      throw e;
    });
    return this.db;
  }

  private async run<T>(mode: IDBTransactionMode, fn: (store: IDBObjectStore) => IDBRequest<T>): Promise<T> {
    const db = await this.open();
    return new Promise<T>((resolve, reject) => {
      const req = fn(db.transaction(STORE, mode).objectStore(STORE));
      req.onsuccess = () => resolve(req.result);
      req.onerror = () => reject(req.error);
    });
  }

  async get(key: string) {
    return ((await this.run("readonly", (s) => s.get(key))) as string | undefined) ?? null;
  }
  async set(key: string, value: string) {
    await this.run("readwrite", (s) => s.put(value, key));
  }
  async delete(key: string) {
    await this.run("readwrite", (s) => s.delete(key));
  }
}

/** IndexedDB first; any failure falls back to localStorage. */
export class DefaultStorage implements SaveStorage {
  private idb = new IndexedDBStorage();
  private ls = new LocalStorageStorage();

  private async run<T>(op: (s: SaveStorage) => Promise<T>): Promise<T> {
    try {
      return await op(this.idb);
    } catch {
      return op(this.ls);
    }
  }
  get(key: string) {
    return this.run((s) => s.get(key));
  }
  set(key: string, value: string) {
    return this.run((s) => s.set(key, value));
  }
  delete(key: string) {
    return this.run((s) => s.delete(key));
  }
}

export class SaveService {
  constructor(private storage: SaveStorage = new DefaultStorage()) {}

  async save(state: GameState): Promise<void> {
    const data: SaveData = {
      schemaVersion: GameConfig.schemaVersion,
      saveId: GameConfig.save.slotId,
      savedAtRealTime: new Date().toISOString(),
      gameState: state,
    };
    await this.storage.set(GameConfig.save.slotId, JSON.stringify(data));
  }

  /** Returns null when there is no save; throws if the save is corrupt or from a newer version. Never touches the game clock. */
  async load(): Promise<GameState | null> {
    const raw = await this.storage.get(GameConfig.save.slotId);
    if (raw === null) return null;
    let parsed: unknown;
    try {
      parsed = JSON.parse(raw);
    } catch {
      throw new Error("存檔損毀，無法解析");
    }
    return migrate(parsed).gameState;
  }

  async clear(): Promise<void> {
    await this.storage.delete(GameConfig.save.slotId);
  }
}
