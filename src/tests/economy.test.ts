import { describe, expect, it } from "vitest";
import { addTransaction, buyItem, useItem } from "../systems/EconomySystem";
import { makeContent, newGame } from "./fixtures";

describe("EconomySystem", () => {
  it("rejects duplicate transaction ids", () => {
    const s = newGame();
    const money = s.player.money;
    expect(addTransaction(s, { id: "t1", amount: 50, category: "income", reason: "x" })).toBe(true);
    expect(addTransaction(s, { id: "t1", amount: 50, category: "income", reason: "x" })).toBe(false);
    expect(s.player.money).toBe(money + 50);
    expect(s.transactions).toHaveLength(1);
    expect(s.transactions[0].gameTime).toBe(s.gameClock.totalMinutes);
  });

  it("rejects insufficient money and non-positive amounts", () => {
    const s = newGame();
    const money = s.player.money;
    expect(addTransaction(s, { id: "e1", amount: money + 1, category: "expense", reason: "x" })).toBe(false);
    expect(addTransaction(s, { id: "e2", amount: 0, category: "income", reason: "x" })).toBe(false);
    expect(addTransaction(s, { id: "e3", amount: money, category: "expense", reason: "x" })).toBe(true);
    expect(s.player.money).toBe(0);
  });

  it("buys and uses items", () => {
    const c = makeContent(), s = newGame(c);
    const money = s.player.money;
    s.player.needs.satiety = 40;
    expect(buyItem(s, c, "sandwich")).toEqual({ ok: true });
    expect(buyItem(s, c, "sandwich").ok).toBe(true); // same minute, distinct id
    expect(s.player.money).toBe(money - 60);
    expect(s.inventory.sandwich).toBe(2);
    expect(new Set(s.transactions.map((t) => t.id)).size).toBe(2);
    expect(useItem(s, c, "sandwich")).toEqual({ ok: true, minutes: 15 });
    expect(s.player.needs.satiety).toBe(70);
    expect(s.inventory.sandwich).toBe(1);
    expect(useItem(s, c, "juice").ok).toBe(false);
  });

  it("refuses unaffordable or unknown purchases", () => {
    const c = makeContent(), s = newGame(c);
    s.player.money = 5;
    expect(buyItem(s, c, "sandwich")).toEqual({ ok: false, reason: "金錢不足" });
    expect(buyItem(s, c, "nope").ok).toBe(false);
    expect(s.inventory).toEqual({});
    expect(s.player.money).toBe(5);
  });
});
