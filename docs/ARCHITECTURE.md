# 架構與模組契約（MVP）

技術：Phaser 3.90 + TypeScript + Vite + Vitest。型別在 `src/game/types.ts`，可調數值在 `src/game/GameConfig.ts`，共用 ID 在 `src/data/ids.ts`。**不要重新定義這些型別或常數。**

## 原則
- 遊戲邏輯（`src/systems`、`src/persistence`）是純 TypeScript，不 import Phaser，可單元測試。
- 所有狀態都在單一 `GameState`；系統函式直接修改傳入的 `state` 並回傳結果物件。
- 時間只能透過 `advanceGameTime()` 推進（A1.5）。離線不補算時間。
- 金錢只能透過 `EconomySystem`；交易 ID 重複即拒絕（防重複發薪）。
- 需求只能透過 `NeedsSystem` 修改，並 clamp 至 0–100。

## 模組簽章（實作者必須遵守）

### src/game/GameState.ts
- `createNewGame(content: ContentDB, name: string, appearance: CharacterAppearance): GameState`

### src/systems/TimeSystem.ts
- `clockParts(total: GameMinute): { day: number; hour: number; minute: number; minuteOfDay: number; weekday: number }`
- `formatClock(total: GameMinute): string` → `"第1天 08:00"`（day 從 1 顯示）
- `realMsToGameMinutes(mode: TimeMode, ms: number): number`（可為小數，由呼叫端累積）
- `setMode(state: GameState, mode: TimeMode): void`
- `advanceGameTime(state: GameState, content: ContentDB, minutes: number): AdvanceResult`
  - 逐小時邊界套用需求變化；每分鐘界線更新 NPC 行程位置；跨午夜依序：日期 → 需求 → NPC 行程 → `dayStart` 事件 → 解鎖檢查 → `saveRequested = true`。
  - 一次跨多個觸發點時依時間順序處理。暫停模式下 `minutes` 由呼叫端傳 0。
  - `type AdvanceResult = { dayChanged: boolean; messages: string[]; firedEventIds: string[]; unlockedMapIds: string[]; saveRequested: boolean; needWarnings: NeedKey[] }`

### src/systems/NeedsSystem.ts
- `clampNeed(v: number): number`
- `applyNeedDelta(state: GameState, delta: Partial<NeedState>): void`
- `applyHourly(state: GameState, hours: number, sleeping?: boolean): void`
- `lowNeeds(state: GameState): NeedKey[]`

### src/systems/EconomySystem.ts
- `addTransaction(state, tx: Omit<Transaction,"gameTime"> & { gameTime?: number }): boolean`（重複 ID 回傳 false，不變更金錢；支出不足回傳 false）
- `buyItem(state, content, itemId: string): { ok: boolean; reason?: string }`（交易 ID：`buy:${itemId}:${totalMinutes}:${n}`）
- `useItem(state, content, itemId): { ok: boolean; minutes: number }`

### src/systems/JobSystem.ts
- `shiftAt(job: JobDefinition, total: GameMinute): { start: GameMinute; end: GameMinute } | null`（目前時間落在哪一班）
- `nextShift(job, total): { start: GameMinute; end: GameMinute }`
- `canStartWork(state, content, jobId): { ok: boolean; reason?: string; sessionId?: string }`（需在班表時段、站在工作地點、該班未完成）
- `performanceFromScore(score: number, stamina: number): number`（0.5–1.5，體力低套用懲罰）
- `completeWork(state, content, jobId, sessionId, score): WorkSession | null`（同 sessionId 只發一次薪；套用 needDelta；推進 durationMinutes 時間由呼叫端透過 advanceGameTime 處理）

### src/systems/RhythmGame.ts（純邏輯，畫面由 UI 負責）
- `createChart(seed: number, cfg = GameConfig.rhythm): { id: number; timeMs: number; kind: "tap" }[]`
- `judge(chartTimeMs: number, tapMs: number): "perfect" | "good" | "miss"`
- `scoreRun(results: ("perfect"|"good"|"miss")[]): number`（0–1）

### src/systems/RelationshipSystem.ts
- `getRel(state, npcId): Relationship`（不存在則建立 stranger/0）
- `changeAffection(state, npcId, delta): Relationship`（clamp 0–100，依門檻自動更新 stage，但 `partner` 只能由事件設定，且不會被降級）
- `talkTo(state, content, npcId): { line: DialogueLine; affectionGained: number; event?: EventDefinition }`
  - 先找該 NPC 可觸發（條件達成、未完成）的 `talk` 事件；有則回傳 event（尚未套用，由 `EventSystem.fireEvent` 套用）。
  - 否則挑選符合 `minAffection` 的最高門檻台詞；冷卻時間內好感度不增加。

### src/systems/NPCScheduleSystem.ts
- `activeEntry(def: ScheduleDefinition, minuteOfDay: number): ScheduleEntry`（跨午夜區段需正確處理）
- `updateNPCs(state, content): void`（依行程設定 `currentActivity` 與 `position`；位置＝地點 door 下方一格，依 NPC 序號左右錯開避免重疊）

### src/systems/EventSystem.ts
- `checkCondition(state, content, conditionId): boolean`
- `availableEvents(state, content, trigger: EventTrigger, ctx?: { npcId?: string; locationId?: string }): EventDefinition[]`
- `fireEvent(state, content, eventId): { ok: boolean; lines: string[]; messages: string[] }`（完成後標記 completed，不可重複）
- `checkUnlocks(state, content): string[]`（地圖 `unlockConditionId` 達成即加入 `unlockedMapIds`，回傳新解鎖的 mapId）

### src/persistence/SaveService.ts / SaveMigration.ts
- `class SaveService { constructor(storage?: SaveStorage); save(state): Promise<void>; load(): Promise<GameState | null>; clear(): Promise<void> }`
- `SaveStorage` 介面：`get(key) / set(key, value) / delete(key)`；預設 IndexedDB，失敗時退回 localStorage。
- `migrate(data: unknown): SaveData`（依 schemaVersion 升級；未知格式丟出錯誤）。

### src/scenes（Phaser，依賴上面的系統）
- `WorldScene` 只負責繪製與輸入：讀取 `GameController` 的狀態，點擊地面 → 尋路移動；點擊 NPC／場所 → `controller.interact(target)`。
- `src/systems/Pathfinding.ts`：`findPath(grid: boolean[][] /*true=blocked*/, from, to): {x,y}[] | null`（4 方向 A*，純函式）。
- `src/scenes/props.ts`：prop 目錄（key → 圖片、footprint、碰撞、門位置）。

### 地圖圖塊代碼（`MapDefinition.rows`）
| 代碼 | 圖塊 | 可通行 |
|---|---|---|
| `.` | grassa | ✓ |
| `,` | grassb | ✓ |
| `d` | dirt | ✓ |
| `s` | sidewalk | ✓ |
| `r` | road_h | ✓ |
| `R` | road_v | ✓ |
| `+` | crossroad | ✓ |
| `=` | crosswalk_h | ✓ |
| `\|` | crosswalk_v | ✓ |
| `W` | floorwood | ✓ |
| `T` | floortile | ✓ |
| `m` | door mat（室內出口） | ✓ |
| `t` | tilled soil（農田土壤，田間小徑） | ✓ |
| `c` / `y` | 高麗菜田列 / 麥田列（作物） | ✗ |
| `i` / `j` | 室內牆 A（米白壁紙）/ B（木板） | ✗ |
| `v` | 室內邊牆（深木框） | ✗ |
| `w` | brick wall | ✗ |
| `f` | fence | ✗ |
| `h` | hedge | ✗ |
| `~` | water | ✗ |

## 原型預設決策（文件 E，皆可在 GameConfig 調整，待使用者確認）
1. 時間：正常 1 遊戲分／秒，加速 4 倍。
2. 需求：第二項為「飽足程度」（越高越不餓）。
3. 錯過班表：失去該班收入，不可補班。
4. 戀愛：先以一位主要 NPC（npc_007 Artist）完成完整伴侶流程。

## 第二階段：未來系統（PRD P-18：結婚家庭、老化傳承、天氣季節、日夜）

型別已加在 `types.ts`（`Season`、`Weather`、`LifeStage`、`FamilyState`、`FamilyMember`、`AncestorRecord`、新 Condition／Effect、`RelationshipStage` 新增 `spouse`），數值在 `GameConfig.calendar / weather / family`。存檔 `schemaVersion` 升到 2，`SaveMigration` 需把 v1 存檔補上預設值（`family`、`weather`、`worldSeed`、`player.birthMinute`）。

### 曆法與年齡 `src/systems/CalendarSystem.ts`
- `seasonOf(day: number): Season`（day 為 0 起算的日索引，每季 `daysPerSeason` 天）
- `yearOf(day): number`（1 起）、`dayOfSeason(day): number`（1 起）
- `formatDate(total: GameMinute): string` → `"第1年 春 第3天"`
- `ageYears(birthMinute, now, multiplier = 1): number`（以 28 天為一年，可為小數）
- `lifeStage(age): LifeStage`（依 `calendar.stages`）
- `playerAge(state): number`、`childAge(child, now): number`（套用 `childAgingMultiplier`）

### 天氣與光照 `src/systems/WeatherSystem.ts`、`src/systems/Lighting.ts`
- `rollWeather(seed: number, day: number): Weather`（決定性；同 seed 同天必同結果）
- `currentWeather(state): Weather`
- `isIndoor(content, mapId): boolean`（`MapDefinition.indoor`）
- `lightingAt(minuteOfDay: number, weather: Weather, indoor: boolean): { color: number; alpha: number; lampsOn: boolean }`（純函式；清晨、白天、黃昏、夜晚漸變；雨雪較暗；室內較淡）
- 跨日時擲當天天氣；在戶外遇雨雪每小時心情 `badWeatherMoodPerHour`；雪天農場不開班（`JobSystem.canStartWork` 回傳原因）。

### 家庭與傳承 `src/systems/FamilySystem.ts`
- `canPropose(state, content, npcId): { ok: boolean; reason?: string }`（伴侶滿 `minPartnerDays` 天、好感 ≥ `proposeAffection`、背包有戒指）
- `propose(state, content, npcId): { ok: boolean; lines: string[]; messages: string[] }`（消耗戒指 → stage `spouse`、記錄 `spouseNpcId`/`marriedAtMinute`）
- `processFamilyDay(state, content): string[]`（跨日呼叫：到期出生、孩子成長階段變化的訊息）
- `canSucceed(state): { ok: boolean; heirId?: string; reason?: string }`、`succeed(state, content, heirId): string[]`（孩子成為新玩家：姓名、外觀、出生時間沿用；金錢依 `inheritanceRate`；舊玩家寫入 `ancestors`；`generation + 1`；配偶關係與一般 NPC 好感重設為新世代的起點）
- 配偶會搬進家裡：`NPCScheduleSystem` 在晚上與夜間把配偶放在 `loc_home_bed` 附近。
- 只有 `stage` 為 `partner`/`spouse` 的 NPC 算伴侶（`noOtherPartner` 同時檢查兩者）。

### 畫面（`src/scenes`、`src/ui`）
- 世界場景依 `lightingAt` 疊色調，夜晚路燈發光；戶外雨、雪粒子；季節以地面色調呈現。
- HUD 顯示日期（年、季、日）、天氣圖示、玩家年齡。
- 新「家庭」面板：配偶、孩子（姓名、年齡、階段）、世代與祖先、「傳承」按鈕（`canSucceed` 為真時）。
- 孩子在住家室內以兒童圖像行走；嬰兒顯示為嬰兒床。
- 商店販售戒指（`item_ring`）；向伴侶求婚在 NPC 選單出現「求婚」。
