import type { ConditionDefinition, EventDefinition } from "../game/types";
import { COND, LOC } from "./ids";

export const conditions: Record<string, ConditionDefinition> = {
  [COND.unlockRural]: {
    id: COND.unlockRural,
    all: [{ type: "shiftsWorked", atLeast: 2 }],
  },
  cond_artist_meet: {
    id: "cond_artist_meet",
    all: [{ type: "affection", npcId: "npc_007", atLeast: 10 }],
  },
  cond_artist_date: {
    id: "cond_artist_date",
    all: [
      { type: "affection", npcId: "npc_007", atLeast: 50 },
      { type: "eventCompleted", eventId: "ev_artist_meet" },
    ],
  },
  cond_artist_confess: {
    id: "cond_artist_confess",
    all: [
      { type: "affection", npcId: "npc_007", atLeast: 75 },
      { type: "eventCompleted", eventId: "ev_artist_date" },
    ],
  },
  cond_artist_partner_followup: {
    id: "cond_artist_partner_followup",
    all: [
      { type: "stage", npcId: "npc_007", stage: "partner" },
      { type: "eventCompleted", eventId: "ev_artist_confess" },
      { type: "day", atLeast: 1 },
    ],
  },
  cond_npc001_friend: {
    id: "cond_npc001_friend",
    all: [{ type: "affection", npcId: "npc_001", atLeast: 35 }],
  },
};

export const events: Record<string, EventDefinition> = {
  ev_artist_meet: {
    id: "ev_artist_meet",
    triggerType: "talk",
    npcId: "npc_007",
    conditionIds: ["cond_artist_meet"],
    effects: [
      { type: "affection", npcId: "npc_007", delta: 5 },
      { type: "message", text: "沈若溪好像記住你了。" },
    ],
    lines: [
      "沈若溪放下畫筆，朝你揮了揮手。",
      "「你是不是常在公園附近晃呀？」",
      "「我叫沈若溪，是個畫畫的人。」",
      "「有空的話，可以來看看我的畫喔。」",
    ],
  },
  ev_artist_date: {
    id: "ev_artist_date",
    triggerType: "talk",
    npcId: "npc_007",
    conditionIds: ["cond_artist_date"],
    effects: [
      { type: "affection", npcId: "npc_007", delta: 10 },
      { type: "need", delta: { mood: 10 } },
      { type: "message", text: "和沈若溪一起去看展，心情很好。" },
    ],
    lines: [
      "沈若溪約你去美術館看展。",
      "展場裡，她一幅一幅地向你介紹作品。",
      "「這幅畫是我第一次被看見時畫的。」",
      "走出展場時，夕陽正灑在街道上。",
    ],
    timeCostMinutes: 120,
  },
  ev_artist_confess: {
    id: "ev_artist_confess",
    triggerType: "talk",
    npcId: "npc_007",
    conditionIds: ["cond_artist_confess"],
    effects: [
      { type: "setStage", npcId: "npc_007", stage: "partner" },
      { type: "message", text: "你們成為伴侶了！" },
    ],
    lines: [
      "黃昏的河畔，你鼓起勇氣開口。",
      "沈若溪愣了一下，然後輕輕笑了。",
      "「我也一直在等你說這句話呢。」",
    ],
  },
  ev_artist_partner_followup: {
    id: "ev_artist_partner_followup",
    triggerType: "dayStart",
    npcId: "npc_007",
    conditionIds: ["cond_artist_partner_followup"],
    effects: [
      { type: "need", delta: { mood: 15 } },
      { type: "message", text: "沈若溪一早就來找你了。" },
    ],
    lines: [
      "一早，門口傳來熟悉的敲門聲。",
      "沈若溪提著熱騰騰的早餐站在門外。",
      "「我想你了，所以一早就過來囉。」",
      "你們一起吃早餐，度過了溫暖的早晨。",
    ],
  },
  ev_npc001_bonus: {
    id: "ev_npc001_bonus",
    triggerType: "talk",
    npcId: "npc_001",
    conditionIds: ["cond_npc001_friend"],
    effects: [
      { type: "money", delta: 50, reason: "店長的獎金" },
      { type: "message", text: "收到店長的獎金 +50" },
    ],
    lines: [
      "陳書豪把你叫到櫃檯前。",
      "「你一直幫忙店裡的事，我都看在眼裡。」",
      "「這是店長的獎金，拿去犒賞自己吧！」",
    ],
  },
  ev_farm_welcome: {
    id: "ev_farm_welcome",
    triggerType: "enterLocation",
    locationId: LOC.farm,
    conditionIds: [],
    effects: [{ type: "message", text: "歡迎來到農場！" }],
    lines: [
      "你第一次來到農場，空氣清新得讓人心曠神怡。",
      "遠處傳來雞鳴聲，黃德福正在田裡忙碌。",
      "「歡迎來到農場！有需要的話儘管說。」",
    ],
  },
};
