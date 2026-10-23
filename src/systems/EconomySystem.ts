import type { ContentDB, GameState, Transaction } from "../game/types";
import { applyNeedDelta } from "./NeedsSystem";

export function addTransaction(
  state: GameState,
  tx: Omit<Transaction, "gameTime"> & { gameTime?: number },
): boolean {
  if (!(tx.amount > 0) || state.transactions.some((t) => t.id === tx.id)) return false;
  const signed = tx.category === "income" ? tx.amount : -tx.amount;
  if (state.player.money + signed < 0) return false;
  state.player.money += signed;
  state.transactions.push({ ...tx, gameTime: tx.gameTime ?? state.gameClock.totalMinutes });
  return true;
}

export function buyItem(state: GameState, content: ContentDB, itemId: string): { ok: boolean; reason?: string } {
  const item = content.items[itemId];
  if (!item) return { ok: false, reason: "找不到物品" };
  const prefix = `buy:${itemId}:${state.gameClock.totalMinutes}:`;
  const n = state.transactions.filter((t) => t.id.startsWith(prefix)).length;
  const ok = addTransaction(state, {
    id: `${prefix}${n}`,
    amount: item.price,
    category: "expense",
    reason: `購買${item.name}`,
  });
  if (!ok) return { ok: false, reason: "金錢不足" };
  state.inventory[itemId] = (state.inventory[itemId] ?? 0) + 1;
  return { ok: true };
}

export function useItem(state: GameState, content: ContentDB, itemId: string): { ok: boolean; minutes: number } {
  const item = content.items[itemId];
  if (!item || (state.inventory[itemId] ?? 0) <= 0) return { ok: false, minutes: 0 };
  state.inventory[itemId] -= 1;
  if (item.useEffect) applyNeedDelta(state, item.useEffect);
  return { ok: true, minutes: item.useMinutes ?? 0 };
}
