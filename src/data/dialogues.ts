import type { DialogueSet } from "../game/types";

// Each NPC: 6 lines, escalating minAffection (0, 10, 20, 35, 50, 75).
// affectionDelta is left unset: RelationshipSystem grants affection.
export const dialogues: Record<string, DialogueSet> = {
  dlg_npc_001: {
    id: "dlg_npc_001",
    lines: [
      { id: "dlg_npc_001_01", text: "歡迎光臨！今天想喝點什麼呢？", minAffection: 0 },
      { id: "dlg_npc_001_02", text: "又見面了！我們店的拿鐵很受歡迎喔。", minAffection: 10 },
      { id: "dlg_npc_001_03", text: "你工作時很認真，我都看在眼裡呢。", minAffection: 20 },
      { id: "dlg_npc_001_04", text: "要不要試試我新研發的手沖咖啡？", minAffection: 35 },
      { id: "dlg_npc_001_05", text: "有你在店裡，感覺氣氛都變好了。", minAffection: 50 },
      { id: "dlg_npc_001_06", text: "謝謝你一直來支持這家小店。", minAffection: 75 },
    ],
  },
  dlg_npc_002: {
    id: "dlg_npc_002",
    lines: [
      { id: "dlg_npc_002_01", text: "要買什麼？今天有特價喔！", minAffection: 0 },
      { id: "dlg_npc_002_02", text: "常來光顧，我幫你記住熟客價。", minAffection: 10 },
      { id: "dlg_npc_002_03", text: "最近進了一批好蘋果，要不要看看？", minAffection: 20 },
      { id: "dlg_npc_002_04", text: "你看起來很累，要多吃點東西啊。", minAffection: 35 },
      { id: "dlg_npc_002_05", text: "下次來我請你喝飲料，別跟我客氣。", minAffection: 50 },
      { id: "dlg_npc_002_06", text: "有你這個朋友，我每天都很開心。", minAffection: 75 },
    ],
  },
  dlg_npc_003: {
    id: "dlg_npc_003",
    lines: [
      { id: "dlg_npc_003_01", text: "早啊！今天天氣真不錯。", minAffection: 0 },
      { id: "dlg_npc_003_02", text: "有空來我家喝茶吧，我泡的茶很香。", minAffection: 10 },
      { id: "dlg_npc_003_03", text: "要不要一起去公園走走？我每天都跑步。", minAffection: 20 },
      { id: "dlg_npc_003_04", text: "有事儘管說，鄰居就是要互相照應。", minAffection: 35 },
      { id: "dlg_npc_003_05", text: "你做事很有一套，我很佩服。", minAffection: 50 },
      { id: "dlg_npc_003_06", text: "能當你的鄰居，真是我的福氣。", minAffection: 75 },
    ],
  },
  dlg_npc_004: {
    id: "dlg_npc_004",
    lines: [
      { id: "dlg_npc_004_01", text: "啊，你也來這裡讀書嗎？", minAffection: 0 },
      { id: "dlg_npc_004_02", text: "我最近在趕期末報告，好累喔。", minAffection: 10 },
      { id: "dlg_npc_004_03", text: "你覺得我該選哪個研究主題呢？", minAffection: 20 },
      { id: "dlg_npc_004_04", text: "跟你聊天，心情就放鬆多了。", minAffection: 35 },
      { id: "dlg_npc_004_05", text: "我夢想有一天能開一間自己的書店。", minAffection: 50 },
      { id: "dlg_npc_004_06", text: "謝謝你陪我熬過這段日子。", minAffection: 75 },
    ],
  },
  dlg_npc_005: {
    id: "dlg_npc_005",
    lines: [
      { id: "dlg_npc_005_01", text: "來鄉下啦？這裡空氣很好吧。", minAffection: 0 },
      { id: "dlg_npc_005_02", text: "今年的番茄收成不錯，嚐嚐看吧。", minAffection: 10 },
      { id: "dlg_npc_005_03", text: "種田最怕的就是老天爺不作美。", minAffection: 20 },
      { id: "dlg_npc_005_04", text: "你做事很踏實，像我年輕的時候。", minAffection: 35 },
      { id: "dlg_npc_005_05", text: "等秋收了，帶你去看滿田的稻穗。", minAffection: 50 },
      { id: "dlg_npc_005_06", text: "在這裡，你就像是我們家的人。", minAffection: 75 },
    ],
  },
  dlg_npc_006: {
    id: "dlg_npc_006",
    lines: [
      { id: "dlg_npc_006_01", text: "唉，又是加班的一天。", minAffection: 0 },
      { id: "dlg_npc_006_02", text: "你也常來這裡放鬆啊？我懂那種感覺。", minAffection: 10 },
      { id: "dlg_npc_006_03", text: "上班真的很累，但有咖啡就撐得住。", minAffection: 20 },
      { id: "dlg_npc_006_04", text: "有時很羨慕你，不用被時間綁住。", minAffection: 35 },
      { id: "dlg_npc_006_05", text: "下班後一起吃個飯吧，我請客。", minAffection: 50 },
      { id: "dlg_npc_006_06", text: "有你當朋友，上班也沒那麼無聊了。", minAffection: 75 },
    ],
  },
  dlg_npc_007: {
    id: "dlg_npc_007",
    lines: [
      { id: "dlg_npc_007_01", text: "嗯？你在看我的畫嗎？", minAffection: 0 },
      { id: "dlg_npc_007_02", text: "今天光線很好，我正在畫這片天空。", minAffection: 10 },
      { id: "dlg_npc_007_03", text: "你覺得這幅畫怎麼樣？說實話就好。", minAffection: 20 },
      { id: "dlg_npc_007_04", text: "跟你聊天的時候，靈感好像特別多。", minAffection: 35 },
      { id: "dlg_npc_007_05", text: "我很少跟別人分享作品，但你不一樣。", minAffection: 50 },
      { id: "dlg_npc_007_06", text: "能遇見你，是我這段時間最美好的事。", minAffection: 75 },
    ],
  },
  dlg_npc_008: {
    id: "dlg_npc_008",
    lines: [
      { id: "dlg_npc_008_01", text: "嗨，這是你的信，請簽收一下。", minAffection: 0 },
      { id: "dlg_npc_008_02", text: "每天跑來跑去，這一區我全都熟。", minAffection: 10 },
      { id: "dlg_npc_008_03", text: "你最近有寄信給誰嗎？我幫你送。", minAffection: 20 },
      { id: "dlg_npc_008_04", text: "聽說你最近很忙？別太累了啊。", minAffection: 35 },
      { id: "dlg_npc_008_05", text: "每次見到你，都是我一天最期待的時刻。", minAffection: 50 },
      { id: "dlg_npc_008_06", text: "以後你的每封信，我都親手送到。", minAffection: 75 },
    ],
  },
};
