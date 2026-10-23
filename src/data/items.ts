import type { ItemDefinition } from "../game/types";
import { ITEM } from "./ids";

// Food: useEffect restores needs (satiety higher = less hungry). useMinutes = time spent eating.
// Products: no useEffect. flower and gift are intended as NPC gifts (GameConfig.relationship.giftAffection).
// ring is consumed by the proposal event (src/data/events.ts), not sold as a gift.
export const items: Record<string, ItemDefinition> = {
  item_coffee: {
    id: "item_coffee",
    name: "咖啡",
    price: 35,
    iconAsset: "objects/food/OBJ_003_Coffee_v01.png",
    useEffect: { stamina: 20, satiety: 5, mood: 5 },
    useMinutes: 15,
  },
  item_bread: {
    id: "item_bread",
    name: "吐司麵包",
    price: 20,
    iconAsset: "objects/food/OBJ_003_Bread_v01.png",
    useEffect: { satiety: 25 },
    useMinutes: 15,
  },
  item_apple: {
    id: "item_apple",
    name: "蘋果",
    price: 15,
    iconAsset: "objects/food/OBJ_003_Apple_v01.png",
    useEffect: { satiety: 15, mood: 3 },
    useMinutes: 15,
  },
  item_sandwich: {
    id: "item_sandwich",
    name: "三明治",
    price: 50,
    iconAsset: "objects/food/OBJ_003_Sandwich_v01.png",
    useEffect: { satiety: 35, stamina: 5 },
    useMinutes: 20,
  },
  item_bento: {
    id: "item_bento",
    name: "便當",
    price: 80,
    iconAsset: "objects/food/OBJ_003_Bento_v01.png",
    useEffect: { satiety: 50, mood: 5 },
    useMinutes: 30,
  },
  item_shirt: {
    id: "item_shirt",
    name: "襯衫",
    price: 65,
    iconAsset: "objects/products/OBJ_004_Shirt_v01.png",
  },
  item_flower: {
    id: "item_flower",
    name: "花束",
    price: 25,
    iconAsset: "objects/products/OBJ_004_Flower_v01.png",
  },
  item_book: {
    id: "item_book",
    name: "書",
    price: 40,
    iconAsset: "objects/products/OBJ_004_Book_v01.png",
  },
  item_gift: {
    id: "item_gift",
    name: "禮物盒",
    price: 55,
    iconAsset: "objects/products/OBJ_004_Gift_v01.png",
  },
  [ITEM.ring]: {
    id: ITEM.ring,
    name: "婚戒",
    price: 1200,
    iconAsset: "objects/products/OBJ_004_Ring_v01.png",
  },
};
