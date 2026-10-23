import type { ConditionDefinition, EventDefinition } from "../game/types";
import { COND, ITEM, LOC } from "./ids";

export const conditions: Record<string, ConditionDefinition> = {
  [COND.unlockRural]: {
    id: COND.unlockRural,
    all: [{ type: "shiftsWorked", atLeast: 2 }],
  },

  // ---- romance: 沈若溪 (npc_007) ----
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
      { type: "noOtherPartner", npcId: "npc_007" },
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

  cond_artist_propose: {
    id: "cond_artist_propose",
    all: [
      { type: "stage", npcId: "npc_007", stage: "partner" },
      { type: "noOtherPartner", npcId: "npc_007" },
      { type: "affection", npcId: "npc_007", atLeast: 90 },
      { type: "hasItem", itemId: ITEM.ring },
      { type: "eventCompleted", eventId: "ev_artist_partner_followup" },
    ],
  },
  cond_artist_newlywed: {
    id: "cond_artist_newlywed",
    all: [
      { type: "stage", npcId: "npc_007", stage: "spouse" },
      { type: "marriedDays", atLeast: 1 },
    ],
  },
  cond_artist_baby_1: {
    id: "cond_artist_baby_1",
    all: [
      { type: "stage", npcId: "npc_007", stage: "spouse" },
      { type: "marriedDays", atLeast: 3 },
      { type: "childrenAtMost", count: 0 },
      { type: "notPregnant" },
    ],
  },
  cond_artist_baby_2: {
    id: "cond_artist_baby_2",
    all: [
      { type: "stage", npcId: "npc_007", stage: "spouse" },
      { type: "marriedDays", atLeast: 3 },
      { type: "childrenAtMost", count: 1 },
      { type: "notPregnant" },
      { type: "eventCompleted", eventId: "ev_artist_baby_1" },
    ],
  },
  cond_artist_baby_3: {
    id: "cond_artist_baby_3",
    all: [
      { type: "stage", npcId: "npc_007", stage: "spouse" },
      { type: "marriedDays", atLeast: 3 },
      { type: "childrenAtMost", count: 2 },
      { type: "notPregnant" },
      { type: "eventCompleted", eventId: "ev_artist_baby_2" },
    ],
  },

  // ---- romance: 李美玲 (npc_002) ----
  cond_shop_meet: {
    id: "cond_shop_meet",
    all: [{ type: "affection", npcId: "npc_002", atLeast: 10 }],
  },
  cond_shop_date: {
    id: "cond_shop_date",
    all: [
      { type: "affection", npcId: "npc_002", atLeast: 50 },
      { type: "eventCompleted", eventId: "ev_shop_meet" },
    ],
  },
  cond_shop_confess: {
    id: "cond_shop_confess",
    all: [
      { type: "affection", npcId: "npc_002", atLeast: 75 },
      { type: "eventCompleted", eventId: "ev_shop_date" },
      { type: "noOtherPartner", npcId: "npc_002" },
    ],
  },
  cond_shop_partner_followup: {
    id: "cond_shop_partner_followup",
    all: [
      { type: "stage", npcId: "npc_002", stage: "partner" },
      { type: "eventCompleted", eventId: "ev_shop_confess" },
      { type: "day", atLeast: 1 },
    ],
  },

  cond_shop_propose: {
    id: "cond_shop_propose",
    all: [
      { type: "stage", npcId: "npc_002", stage: "partner" },
      { type: "noOtherPartner", npcId: "npc_002" },
      { type: "affection", npcId: "npc_002", atLeast: 90 },
      { type: "hasItem", itemId: ITEM.ring },
      { type: "eventCompleted", eventId: "ev_shop_partner_followup" },
    ],
  },
  cond_shop_newlywed: {
    id: "cond_shop_newlywed",
    all: [
      { type: "stage", npcId: "npc_002", stage: "spouse" },
      { type: "marriedDays", atLeast: 1 },
    ],
  },
  cond_shop_baby_1: {
    id: "cond_shop_baby_1",
    all: [
      { type: "stage", npcId: "npc_002", stage: "spouse" },
      { type: "marriedDays", atLeast: 3 },
      { type: "childrenAtMost", count: 0 },
      { type: "notPregnant" },
    ],
  },
  cond_shop_baby_2: {
    id: "cond_shop_baby_2",
    all: [
      { type: "stage", npcId: "npc_002", stage: "spouse" },
      { type: "marriedDays", atLeast: 3 },
      { type: "childrenAtMost", count: 1 },
      { type: "notPregnant" },
      { type: "eventCompleted", eventId: "ev_shop_baby_1" },
    ],
  },
  cond_shop_baby_3: {
    id: "cond_shop_baby_3",
    all: [
      { type: "stage", npcId: "npc_002", stage: "spouse" },
      { type: "marriedDays", atLeast: 3 },
      { type: "childrenAtMost", count: 2 },
      { type: "notPregnant" },
      { type: "eventCompleted", eventId: "ev_shop_baby_2" },
    ],
  },

  // ---- romance: 許偉杰 (npc_006) ----
  cond_office_meet: {
    id: "cond_office_meet",
    all: [{ type: "affection", npcId: "npc_006", atLeast: 10 }],
  },
  cond_office_date: {
    id: "cond_office_date",
    all: [
      { type: "affection", npcId: "npc_006", atLeast: 50 },
      { type: "eventCompleted", eventId: "ev_office_meet" },
    ],
  },
  cond_office_confess: {
    id: "cond_office_confess",
    all: [
      { type: "affection", npcId: "npc_006", atLeast: 75 },
      { type: "eventCompleted", eventId: "ev_office_date" },
      { type: "noOtherPartner", npcId: "npc_006" },
    ],
  },
  cond_office_partner_followup: {
    id: "cond_office_partner_followup",
    all: [
      { type: "stage", npcId: "npc_006", stage: "partner" },
      { type: "eventCompleted", eventId: "ev_office_confess" },
      { type: "day", atLeast: 1 },
    ],
  },

  cond_office_propose: {
    id: "cond_office_propose",
    all: [
      { type: "stage", npcId: "npc_006", stage: "partner" },
      { type: "noOtherPartner", npcId: "npc_006" },
      { type: "affection", npcId: "npc_006", atLeast: 90 },
      { type: "hasItem", itemId: ITEM.ring },
      { type: "eventCompleted", eventId: "ev_office_partner_followup" },
    ],
  },
  cond_office_newlywed: {
    id: "cond_office_newlywed",
    all: [
      { type: "stage", npcId: "npc_006", stage: "spouse" },
      { type: "marriedDays", atLeast: 1 },
    ],
  },
  cond_office_baby_1: {
    id: "cond_office_baby_1",
    all: [
      { type: "stage", npcId: "npc_006", stage: "spouse" },
      { type: "marriedDays", atLeast: 3 },
      { type: "childrenAtMost", count: 0 },
      { type: "notPregnant" },
    ],
  },
  cond_office_baby_2: {
    id: "cond_office_baby_2",
    all: [
      { type: "stage", npcId: "npc_006", stage: "spouse" },
      { type: "marriedDays", atLeast: 3 },
      { type: "childrenAtMost", count: 1 },
      { type: "notPregnant" },
      { type: "eventCompleted", eventId: "ev_office_baby_1" },
    ],
  },
  cond_office_baby_3: {
    id: "cond_office_baby_3",
    all: [
      { type: "stage", npcId: "npc_006", stage: "spouse" },
      { type: "marriedDays", atLeast: 3 },
      { type: "childrenAtMost", count: 2 },
      { type: "notPregnant" },
      { type: "eventCompleted", eventId: "ev_office_baby_2" },
    ],
  },

  // ---- friendship (non-romanceable NPCs) ----
  cond_npc001_friend: {
    id: "cond_npc001_friend",
    all: [{ type: "affection", npcId: "npc_001", atLeast: 35 }],
  },
  cond_npc001_deep: {
    id: "cond_npc001_deep",
    all: [
      { type: "affection", npcId: "npc_001", atLeast: 60 },
      { type: "eventCompleted", eventId: "ev_npc001_bonus" },
    ],
  },
  cond_npc003_friend: {
    id: "cond_npc003_friend",
    all: [{ type: "affection", npcId: "npc_003", atLeast: 35 }],
  },
  cond_npc003_deep: {
    id: "cond_npc003_deep",
    all: [
      { type: "affection", npcId: "npc_003", atLeast: 60 },
      { type: "eventCompleted", eventId: "ev_npc003_friend" },
    ],
  },
  cond_npc004_friend: {
    id: "cond_npc004_friend",
    all: [{ type: "affection", npcId: "npc_004", atLeast: 35 }],
  },
  cond_npc004_deep: {
    id: "cond_npc004_deep",
    all: [
      { type: "affection", npcId: "npc_004", atLeast: 60 },
      { type: "eventCompleted", eventId: "ev_npc004_friend" },
    ],
  },
  cond_npc005_friend: {
    id: "cond_npc005_friend",
    all: [{ type: "affection", npcId: "npc_005", atLeast: 35 }],
  },
  cond_npc005_deep: {
    id: "cond_npc005_deep",
    all: [
      { type: "affection", npcId: "npc_005", atLeast: 60 },
      { type: "eventCompleted", eventId: "ev_npc005_friend" },
    ],
  },
  cond_npc008_friend: {
    id: "cond_npc008_friend",
    all: [{ type: "affection", npcId: "npc_008", atLeast: 35 }],
  },
  cond_npc008_deep: {
    id: "cond_npc008_deep",
    all: [
      { type: "affection", npcId: "npc_008", atLeast: 60 },
      { type: "eventCompleted", eventId: "ev_npc008_friend" },
    ],
  },
};

export const events: Record<string, EventDefinition> = {
  // ---- 沈若溪 (npc_007) ----
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

  ev_artist_propose: {
    id: "ev_artist_propose",
    triggerType: "talk",
    npcId: "npc_007",
    conditionIds: ["cond_artist_propose"],
    effects: [
      { type: "consumeItem", itemId: ITEM.ring, count: 1 },
      { type: "marry", npcId: "npc_007" },
      { type: "need", delta: { mood: 20 } },
      { type: "message", text: "你們結婚了！" },
    ],
    lines: [
      "黃昏的畫室裡，晚霞映滿了整面牆。",
      "你單膝跪下，把婚戒輕輕放在她的掌心。",
      "「我想把之後的每一幅畫，都和你一起完成。」",
      "沈若溪含著淚點頭，笑得像陽光一樣燦爛。",
      "「好，我願意。」",
    ],
    timeCostMinutes: 240,
  },
  ev_artist_newlywed: {
    id: "ev_artist_newlywed",
    triggerType: "dayStart",
    npcId: "npc_007",
    conditionIds: ["cond_artist_newlywed"],
    effects: [
      { type: "need", delta: { mood: 10 } },
      { type: "message", text: "新婚的第一天，家裡暖洋洋的。" },
    ],
    lines: [
      "新婚的第一個早晨，陽光透過窗簾灑進來。",
      "沈若溪還在睡夢中，手卻緊緊抓著你的衣角。",
      "「原來每天醒來都能看到你，是這種感覺呀。」",
      "你輕輕吻了吻她的額頭，今天也是溫暖的一天。",
    ],
  },
  ev_artist_baby_1: {
    id: "ev_artist_baby_1",
    triggerType: "talk",
    npcId: "npc_007",
    conditionIds: ["cond_artist_baby_1"],
    effects: [
      { type: "conceive" },
      { type: "message", text: "家裡即將迎接新成員！" },
    ],
    lines: [
      "沈若溪拿著驗孕棒，眼睛亮晶晶的。",
      "「我們要有寶寶了，你聽見了嗎？」",
      "你把她擁進懷裡，心裡滿是說不出的喜悅。",
      "「以後，這個家會更熱鬧了呢。」",
    ],
  },
  ev_artist_baby_2: {
    id: "ev_artist_baby_2",
    triggerType: "talk",
    npcId: "npc_007",
    conditionIds: ["cond_artist_baby_2"],
    effects: [
      { type: "conceive" },
      { type: "message", text: "家裡即將迎接新成員！" },
    ],
    lines: [
      "沈若溪在窗邊畫了一幅小小的搖籃。",
      "「這次的小傢伙，要和大寶寶好好相處喔。」",
      "「我想把我們的家，一筆一筆畫得更溫暖。」",
    ],
  },
  ev_artist_baby_3: {
    id: "ev_artist_baby_3",
    triggerType: "talk",
    npcId: "npc_007",
    conditionIds: ["cond_artist_baby_3"],
    effects: [
      { type: "conceive" },
      { type: "message", text: "家裡即將迎接新成員！" },
    ],
    lines: [
      "沈若溪把畫室的一角改成小小的遊戲區。",
      "「最後這個孩子，我要畫進我們最滿意的一幅畫。」",
      "「三個寶貝，就是我一生最好的作品。」",
    ],
  },

  // ---- 李美玲 (npc_002) ----
  ev_shop_meet: {
    id: "ev_shop_meet",
    triggerType: "talk",
    npcId: "npc_002",
    conditionIds: ["cond_shop_meet"],
    effects: [
      { type: "affection", npcId: "npc_002", delta: 5 },
      { type: "message", text: "李美玲好像記住你這位熟客了。" },
    ],
    lines: [
      "李美玲從櫃檯後探出頭來，笑得很熱情。",
      "「哎呀，你是常來買東西的那位吧？」",
      "「我是這家店的老闆，大家都叫我美玲姐。」",
      "「以後買東西來找我，我幫你留意特價！」",
    ],
  },
  ev_shop_date: {
    id: "ev_shop_date",
    triggerType: "talk",
    npcId: "npc_002",
    conditionIds: ["cond_shop_date"],
    effects: [
      { type: "affection", npcId: "npc_002", delta: 10 },
      { type: "need", delta: { mood: 10 } },
      { type: "message", text: "和李美玲逛夜市，心情輕快極了。" },
    ],
    lines: [
      "李美玲說今晚要去夜市挑菜，順便邀你同行。",
      "她一路殺價，攤販都拿她沒辦法，你看得直笑。",
      "「別小看我，我可是精打細算的高手呢。」",
      "吃著熱騰騰的烤魷魚，她偷偷瞄了你一眼。",
    ],
    timeCostMinutes: 90,
  },
  ev_shop_confess: {
    id: "ev_shop_confess",
    triggerType: "talk",
    npcId: "npc_002",
    conditionIds: ["cond_shop_confess"],
    effects: [
      { type: "setStage", npcId: "npc_002", stage: "partner" },
      { type: "message", text: "你們成為伴侶了！" },
    ],
    lines: [
      "打烊後的店裡，只剩下燈光和你們兩人。",
      "你深吸一口氣，把心裡的話說了出來。",
      "李美玲先是愣住，接著紅著臉笑了。",
      "「傻瓜，我還以為你永遠不會開口呢。」",
    ],
  },
  ev_shop_partner_followup: {
    id: "ev_shop_partner_followup",
    triggerType: "dayStart",
    npcId: "npc_002",
    conditionIds: ["cond_shop_partner_followup"],
    effects: [
      { type: "need", delta: { mood: 15 } },
      { type: "message", text: "李美玲一早就幫你留了早餐。" },
    ],
    lines: [
      "一早，雜貨店的捲門已經拉起一半。",
      "李美玲探出頭來，手裡捧著剛出爐的蛋餅。",
      "「我特地幫你留的，趁熱吃，別跟我客氣。」",
      "你們在店門口分享早餐，聊著今天的八卦。",
    ],
  },

  ev_shop_propose: {
    id: "ev_shop_propose",
    triggerType: "talk",
    npcId: "npc_002",
    conditionIds: ["cond_shop_propose"],
    effects: [
      { type: "consumeItem", itemId: ITEM.ring, count: 1 },
      { type: "marry", npcId: "npc_002" },
      { type: "need", delta: { mood: 20 } },
      { type: "message", text: "你們結婚了！" },
    ],
    lines: [
      "雜貨店打烊後，店裡只剩下收銀機的聲音。",
      "你把戒指遞到她面前，聲音有點發抖。",
      "「這輩子的帳，我想跟你一起算下去。」",
      "李美玲愣了兩秒，眼眶一下子紅了。",
      "「傻瓜，這麼大的事，你還讓我先算一下！」",
      "「好啦，我答應你，這筆帳我認了。」",
    ],
    timeCostMinutes: 240,
  },
  ev_shop_newlywed: {
    id: "ev_shop_newlywed",
    triggerType: "dayStart",
    npcId: "npc_002",
    conditionIds: ["cond_shop_newlywed"],
    effects: [
      { type: "need", delta: { mood: 10 } },
      { type: "message", text: "新婚的第一天，家裡暖洋洋的。" },
    ],
    lines: [
      "新婚的早晨，雜貨店的捲門還沒拉起來。",
      "李美玲在廚房煎蛋，香味飄滿了整間屋子。",
      "「以後早餐我包了，你負責把碗洗乾淨。」",
      "你笑著答應，覺得這個家比什麼都踏實。",
    ],
  },
  ev_shop_baby_1: {
    id: "ev_shop_baby_1",
    triggerType: "talk",
    npcId: "npc_002",
    conditionIds: ["cond_shop_baby_1"],
    effects: [
      { type: "conceive" },
      { type: "message", text: "家裡即將迎接新成員！" },
    ],
    lines: [
      "李美玲拿著驗孕棒，愣在浴室門口。",
      "「我們……要有寶寶了？」她的聲音有點發顫。",
      "你把她緊緊抱住，心裡滿是說不出的喜悅。",
      "「那就從今天起，我們好好存錢吧！」",
    ],
  },
  ev_shop_baby_2: {
    id: "ev_shop_baby_2",
    triggerType: "talk",
    npcId: "npc_002",
    conditionIds: ["cond_shop_baby_2"],
    effects: [
      { type: "conceive" },
      { type: "message", text: "家裡即將迎接新成員！" },
    ],
    lines: [
      "李美玲把小嬰兒床搬到窗邊，仔細地量了又量。",
      "「這次的小寶貝，要好好跟大寶寶相處喔。」",
      "「家裡又要熱鬧一點了，我的算盤可要加倍忙了。」",
    ],
  },
  ev_shop_baby_3: {
    id: "ev_shop_baby_3",
    triggerType: "talk",
    npcId: "npc_002",
    conditionIds: ["cond_shop_baby_3"],
    effects: [
      { type: "conceive" },
      { type: "message", text: "家裡即將迎接新成員！" },
    ],
    lines: [
      "李美玲把舊衣服一件件洗乾淨，整齊收進衣櫃。",
      "「這些衣服還很新，留給最後一位小寶貝吧。」",
      "「我們的家，再添一個小小的笑聲。」",
    ],
  },

  // ---- 許偉杰 (npc_006) ----
  ev_office_meet: {
    id: "ev_office_meet",
    triggerType: "talk",
    npcId: "npc_006",
    conditionIds: ["cond_office_meet"],
    effects: [
      { type: "affection", npcId: "npc_006", delta: 5 },
      { type: "message", text: "許偉杰好像把你當成同類了。" },
    ],
    lines: [
      "許偉杰揉著眼睛，手裡的咖啡已經見底。",
      "「唉，你也是來續命的嗎？我懂，我懂。」",
      "「我叫許偉杰，附近公司的職員，很會加班。」",
      "「下次遇到，我們互相抱怨一下老闆吧。」",
    ],
  },
  ev_office_date: {
    id: "ev_office_date",
    triggerType: "talk",
    npcId: "npc_006",
    conditionIds: ["cond_office_date"],
    effects: [
      { type: "affection", npcId: "npc_006", delta: 10 },
      { type: "need", delta: { mood: 10 } },
      { type: "message", text: "和許偉杰吃宵夜，他終於笑得很開心。" },
    ],
    lines: [
      "許偉杰難得準時下班，約你去吃宵夜。",
      "「平常都是泡麵解決，今天吃頓像樣的。」",
      "他一邊講公司的糗事，一邊笑到拍桌子。",
      "「跟你聊天，連加班的疲憊都少一半。」",
    ],
    timeCostMinutes: 120,
  },
  ev_office_confess: {
    id: "ev_office_confess",
    triggerType: "talk",
    npcId: "npc_006",
    conditionIds: ["cond_office_confess"],
    effects: [
      { type: "setStage", npcId: "npc_006", stage: "partner" },
      { type: "message", text: "你們成為伴侶了！" },
    ],
    lines: [
      "回家的路上，路燈把兩人的影子拉得很長。",
      "你停下腳步，認真地說出心裡的話。",
      "許偉杰愣了幾秒，然後笑著說：「我是不是幻聽？」",
      "「好，那以後下班就一起走吧。」",
    ],
  },
  ev_office_partner_followup: {
    id: "ev_office_partner_followup",
    triggerType: "dayStart",
    npcId: "npc_006",
    conditionIds: ["cond_office_partner_followup"],
    effects: [
      { type: "need", delta: { mood: 15 } },
      { type: "message", text: "許偉杰一早就傳來早安訊息。" },
    ],
    lines: [
      "一早，手機響起提示音。",
      "許偉杰傳來一張便利商店早餐的照片。",
      "「今天也要加油，中午我請你吃飯！」",
      "你回了個笑臉，今天的上班好像輕鬆一點。",
    ],
  },

  ev_office_propose: {
    id: "ev_office_propose",
    triggerType: "talk",
    npcId: "npc_006",
    conditionIds: ["cond_office_propose"],
    effects: [
      { type: "consumeItem", itemId: ITEM.ring, count: 1 },
      { type: "marry", npcId: "npc_006" },
      { type: "need", delta: { mood: 20 } },
      { type: "message", text: "你們結婚了！" },
    ],
    lines: [
      "下班後的公園，晚風吹得人很舒服。",
      "許偉杰難得沒有滑手機，只是盯著你看。",
      "「我加班加了這麼多年，最想拚的是跟你的以後。」",
      "你把戒指遞過去，他一時忘了呼吸。",
      "「好！我願意！這次不用加班，我保證！」",
    ],
    timeCostMinutes: 240,
  },
  ev_office_newlywed: {
    id: "ev_office_newlywed",
    triggerType: "dayStart",
    npcId: "npc_006",
    conditionIds: ["cond_office_newlywed"],
    effects: [
      { type: "need", delta: { mood: 10 } },
      { type: "message", text: "新婚的第一天，家裡暖洋洋的。" },
    ],
    lines: [
      "新婚的早晨，鬧鐘居然是許偉杰自己設的。",
      "他難得沒有賴床，還煎好了兩個荷包蛋。",
      "「以後我每天準時下班，回家吃你煮的飯。」",
      "你笑著說好，覺得今天的陽光特別溫暖。",
    ],
  },
  ev_office_baby_1: {
    id: "ev_office_baby_1",
    triggerType: "talk",
    npcId: "npc_006",
    conditionIds: ["cond_office_baby_1"],
    effects: [
      { type: "conceive" },
      { type: "message", text: "家裡即將迎接新成員！" },
    ],
    lines: [
      "許偉杰看著驗孕棒，手裡的咖啡灑了一地。",
      "「我……我要當爸爸了？我沒聽錯吧？」",
      "你笑著點頭，他一把將你抱起來轉了一圈。",
      "「從今天起，我的加班時數全部歸零！」",
    ],
  },
  ev_office_baby_2: {
    id: "ev_office_baby_2",
    triggerType: "talk",
    npcId: "npc_006",
    conditionIds: ["cond_office_baby_2"],
    effects: [
      { type: "conceive" },
      { type: "message", text: "家裡即將迎接新成員！" },
    ],
    lines: [
      "許偉杰在客廳組裝嬰兒床，說明書看得滿頭大汗。",
      "「這次我一定要一次就組好，不能再拆了。」",
      "「家裡多一個小傢伙，生活會更有活力吧。」",
    ],
  },
  ev_office_baby_3: {
    id: "ev_office_baby_3",
    triggerType: "talk",
    npcId: "npc_006",
    conditionIds: ["cond_office_baby_3"],
    effects: [
      { type: "conceive" },
      { type: "message", text: "家裡即將迎接新成員！" },
    ],
    lines: [
      "許偉杰把全家的行事曆排得滿滿的，每格都寫著寶貝。",
      "「三個寶貝，我的人生計畫表又要改了。」",
      "「不過，有你們在，再累我也甘願。」",
    ],
  },

  // ---- friendship: 陳書豪 (npc_001) ----
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
  ev_npc001_deep: {
    id: "ev_npc001_deep",
    triggerType: "talk",
    npcId: "npc_001",
    conditionIds: ["cond_npc001_deep"],
    effects: [{ type: "need", delta: { mood: 10 } }],
    lines: [
      "打烊後，陳書豪泡了兩杯手沖咖啡。",
      "「這是我最滿意的豆子，你嚐嚐看。」",
      "「能有你這樣認真的夥伴，我真的很安心。」",
    ],
  },

  // ---- friendship: 周建國 (npc_003) ----
  ev_npc003_friend: {
    id: "ev_npc003_friend",
    triggerType: "talk",
    npcId: "npc_003",
    conditionIds: ["cond_npc003_friend"],
    effects: [
      { type: "money", delta: 30, reason: "鄰居的心意" },
      { type: "message", text: "周建國硬塞給你一些零用錢。" },
    ],
    lines: [
      "周建國在院子裡擦汗，看到你就招了招手。",
      "「來來來，這個你拿去，別跟我客氣！」",
      "他硬是把一張紙鈔塞進你的口袋。",
      "「鄰居互相照顧，本來就是應該的。」",
    ],
  },
  ev_npc003_deep: {
    id: "ev_npc003_deep",
    triggerType: "talk",
    npcId: "npc_003",
    conditionIds: ["cond_npc003_deep"],
    effects: [{ type: "need", delta: { mood: 10 } }],
    lines: [
      "周建國帶著一身汗水，正在門口等你。",
      "「下次一起去跑步吧，我來當你的教練！」",
      "「你說話直來直往，跟我很合得來。」",
    ],
  },

  // ---- friendship: 林小晴 (npc_004) ----
  ev_npc004_friend: {
    id: "ev_npc004_friend",
    triggerType: "talk",
    npcId: "npc_004",
    conditionIds: ["cond_npc004_friend"],
    effects: [
      { type: "need", delta: { stamina: 15 } },
      { type: "message", text: "林小晴分你一顆提神軟糖。" },
    ],
    lines: [
      "林小晴趴在桌上，眼睛半睜半閉。",
      "「啊，我又熬夜了……你會不會笑我？」",
      "她從包包裡翻出一顆軟糖，塞進你手裡。",
      "「吃了這個，精神就會好一點喔！」",
    ],
  },
  ev_npc004_deep: {
    id: "ev_npc004_deep",
    triggerType: "talk",
    npcId: "npc_004",
    conditionIds: ["cond_npc004_deep"],
    effects: [{ type: "need", delta: { mood: 10 } }],
    lines: [
      "林小晴難得早睡，還約你去喝杯飲料。",
      "「我一直想跟人說我的書店夢想呢。」",
      "「你聽了都沒笑我，我好開心。」",
    ],
  },

  // ---- friendship: 黃德福 (npc_005) ----
  ev_npc005_friend: {
    id: "ev_npc005_friend",
    triggerType: "talk",
    npcId: "npc_005",
    conditionIds: ["cond_npc005_friend"],
    effects: [
      { type: "need", delta: { satiety: 15 } },
      { type: "message", text: "黃德福塞給你一袋剛採的番茄。" },
    ],
    lines: [
      "黃德福蹲在田埂邊，正在整理番茄藤。",
      "「來，這些是今天剛採的，很甜喔。」",
      "他把一大袋番茄塞進你懷裡，怎麼都不肯收錢。",
      "「做人嘛，就是要互相照應。」",
    ],
  },
  ev_npc005_deep: {
    id: "ev_npc005_deep",
    triggerType: "talk",
    npcId: "npc_005",
    conditionIds: ["cond_npc005_deep"],
    effects: [{ type: "need", delta: { mood: 10 } }],
    lines: [
      "黃德福帶你走到田邊，指著成熟的稻穗。",
      "「你看，風一吹，整片田都在點頭呢。」",
      "「認真做事的人，土地都會記得。」",
    ],
  },

  // ---- friendship: 郭志強 (npc_008) ----
  ev_npc008_friend: {
    id: "ev_npc008_friend",
    triggerType: "talk",
    npcId: "npc_008",
    conditionIds: ["cond_npc008_friend"],
    effects: [
      { type: "need", delta: { stamina: 10 } },
      { type: "message", text: "郭志強幫你省下了一趟跑腿。" },
    ],
    lines: [
      "郭志強騎著腳踏車經過，車籃裡還堆著信。",
      "「嘿，你要寄信嗎？順路，我幫你帶。」",
      "他俐落地把信收進郵袋，還順手幫你指路。",
      "「這一區跑了好幾年，哪裡有捷徑我最清楚。」",
    ],
  },
  ev_npc008_deep: {
    id: "ev_npc008_deep",
    triggerType: "talk",
    npcId: "npc_008",
    conditionIds: ["cond_npc008_deep"],
    effects: [{ type: "need", delta: { mood: 10 } }],
    lines: [
      "郭志強難得準時收工，在路口等你。",
      "「你每次都跟我打招呼，我很感動呢。」",
      "「以後有信要寄，記得第一個找我。」",
    ],
  },

  // ---- other ----
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
