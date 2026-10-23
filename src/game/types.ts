// Shared data types (開發規格包 v0.2 文件 B). Every module imports from here; do not redefine.

export type TimeMode = "paused" | "normal" | "fast";
export type Facing = "up" | "down" | "left" | "right";

/** Absolute game minutes since day 0 00:00. dayIndex/hour/minute are derived (see TimeSystem). */
export type GameMinute = number;

export type GameClock = {
  totalMinutes: GameMinute;
  mode: TimeMode;
};

export type NeedKey = "stamina" | "satiety" | "mood";
export type NeedState = Record<NeedKey, number>; // each 0–100; satiety: higher = less hungry

export type CharacterAppearance = {
  bodyId: string;
  hairId: string;
  outfitId: string;
  accessoryIds: string[];
};

export type WorldPosition = {
  mapId: string;
  x: number; // tile coordinates
  y: number;
  facing: Facing;
};

export type Player = {
  id: string;
  name: string;
  appearance: CharacterAppearance;
  position: WorldPosition;
  needs: NeedState;
  money: number;
  currentJobId?: string;
  /** Game minute of birth; age is derived (CalendarSystem.ageYears). */
  birthMinute: GameMinute;
};

// ---------- content definitions (static data in src/data) ----------

export type ScheduleEntry = {
  startMinute: number; // minute of day 0–1439
  endMinute: number;
  activity: string; // e.g. "work", "rest", "social", "sleep"
  locationId: string; // NPC stands near this location's door (resolved by NPCScheduleSystem)
};

export type ScheduleDefinition = { id: string; entries: ScheduleEntry[] };

export type DialogueLine = {
  id: string;
  text: string;
  /** Minimum affection to be eligible; defaults to 0. */
  minAffection?: number;
  /** Only eligible at or above this relationship stage (e.g. partner-only lines). */
  minStage?: RelationshipStage;
  affectionDelta?: number;
};

export type DialogueSet = { id: string; lines: DialogueLine[] };

export type NPCDefinition = {
  id: string; // "npc_001" … matches assets/characters/npcs/npc_00N
  name: string;
  spriteKey: string; // e.g. "NPC_001_CafeOwner"
  personalityTags: string[];
  occupation: string;
  scheduleId: string;
  dialogueSetId: string;
  romanceable: boolean;
};

export type NPC = {
  id: string;
  position: WorldPosition;
  currentActivity: string;
};

export type RelationshipStage = "stranger" | "acquaintance" | "close" | "partner" | "spouse";

export type Relationship = {
  npcId: string;
  affection: number; // 0–100
  stage: RelationshipStage;
  completedEventIds: string[];
  /** Game minute of the last affection-giving talk, for cooldown. */
  lastTalkMinute?: GameMinute;
  /** Game minute the stage became "partner" (set by RelationshipSystem.setStage); used for minPartnerDays. */
  partnerSinceMinute?: GameMinute;
};

export type ShiftRule = {
  weekday?: number; // 0–6; undefined = every day
  startMinute: number; // minute of day
  endMinute: number;
};

export type JobDefinition = {
  id: string;
  name: string;
  workplaceLocationId: string;
  shiftRules: ShiftRule[];
  baseWage: number;
  minigameId: string;
  /** Need changes applied once per completed shift. */
  needDelta: Partial<NeedState>;
  durationMinutes: number;
};

export type WorkSession = {
  id: string; // `${jobId}@${day}:${shiftStart}` — unique per shift, used for idempotent pay
  jobId: string;
  score: number; // 0–1 accuracy
  performanceMultiplier: number; // 0.5–1.5
  wage: number;
  completedAtMinute: GameMinute;
};

export type ItemDefinition = {
  id: string;
  name: string;
  price: number;
  iconAsset: string; // path under assets/
  /** Applied when used (e.g. food). */
  useEffect?: Partial<NeedState>;
  useMinutes?: number;
};

export type Inventory = Record<string, number>; // itemId -> count

export type Transaction = {
  id: string; // unique; duplicates are rejected
  amount: number; // always positive
  category: "income" | "expense";
  reason: string;
  gameTime: GameMinute;
};

export type MapDefinition = {
  id: string;
  name: string;
  width: number; // tiles
  height: number;
  /** Row strings of tile codes; see src/data/maps legend. */
  rows: string[];
  locationIds: string[];
  unlockConditionId?: string;
  spawn: { x: number; y: number };
  /** Interiors: no weather, softer day/night tint. */
  indoor?: boolean;
  /** Buildings, trees, decorations. x,y = top-left tile of the prop footprint. */
  props: MapProp[];
};

/** Prop keys are defined by the prop catalog in src/scenes/props.ts. */
export type MapProp = { key: string; x: number; y: number };

export type LocationType = "home" | "shop" | "workplace" | "social" | "gate";

export type LocationDefinition = {
  id: string;
  mapId: string;
  name: string;
  type: LocationType;
  /** Tile the player must stand on / tap to interact. */
  door: { x: number; y: number };
  interactionIds: string[];
  /** For gates: map they lead to. */
  targetMapId?: string;
  /** Tile where scheduled NPCs stand (default: one tile below the door), e.g. behind a counter. */
  npcStand?: { x: number; y: number };
};

export type Condition =
  | { type: "money"; atLeast: number }
  | { type: "affection"; npcId: string; atLeast: number }
  | { type: "stage"; npcId: string; stage: RelationshipStage }
  | { type: "eventCompleted"; eventId: string }
  | { type: "shiftsWorked"; atLeast: number }
  | { type: "day"; atLeast: number }
  /** True while the player has no partner other than npcId (keeps romance exclusive). */
  | { type: "noOtherPartner"; npcId: string }
  | { type: "hasItem"; itemId: string; count?: number }
  /** Days since marriage ≥ atLeast (false when unmarried). */
  | { type: "marriedDays"; atLeast: number }
  | { type: "childrenAtMost"; count: number }
  | { type: "notPregnant" };

export type ConditionDefinition = { id: string; all: Condition[] };

export type Effect =
  | { type: "affection"; npcId: string; delta: number }
  | { type: "setStage"; npcId: string; stage: RelationshipStage }
  | { type: "money"; delta: number; reason: string }
  | { type: "need"; delta: Partial<NeedState> }
  | { type: "unlockMap"; mapId: string }
  | { type: "message"; text: string }
  | { type: "consumeItem"; itemId: string; count?: number }
  /** Marriage: sets stage "spouse" and FamilyState.spouseNpcId (FamilySystem). */
  | { type: "marry"; npcId: string }
  /** Starts a pregnancy; the baby is born GameConfig.family.pregnancyDays later (FamilySystem). */
  | { type: "conceive" };

export type EventTrigger = "talk" | "dayStart" | "manual" | "enterLocation";

export type EventDefinition = {
  id: string;
  triggerType: EventTrigger;
  npcId?: string;
  locationId?: string;
  conditionIds: string[];
  effects: Effect[];
  /** Dialogue shown when the event fires. */
  lines: string[];
  timeCostMinutes?: number;
};

export type EventStatus = "locked" | "available" | "completed";
export type EventState = {
  eventId: string;
  status: EventStatus;
  completedAtGameMinute?: GameMinute;
};

export type Season = "spring" | "summer" | "autumn" | "winter";
export type Weather = "sunny" | "cloudy" | "rain" | "snow";
export type LifeStage = "baby" | "child" | "teen" | "adult" | "elder";

export type FamilyMember = {
  id: string; // "child_1", ...
  name: string;
  birthMinute: GameMinute;
  appearance: CharacterAppearance;
  /** The other parent (spouse NPC id). */
  otherParentNpcId?: string;
};

export type AncestorRecord = {
  generation: number;
  name: string;
  spouseName?: string;
  /** Day index (0-based) when they passed the household on. */
  retiredDay: number;
  ageAtRetirement: number;
};

export type FamilyState = {
  spouseNpcId?: string;
  marriedAtMinute?: GameMinute;
  children: FamilyMember[];
  /** 0-based day index on which the baby is born; undefined = not expecting. */
  babyDueDay?: number;
  /** 1 for the first character; +1 on each succession. */
  generation: number;
  ancestors: AncestorRecord[];
};

export type GameState = {
  schemaVersion: number;
  gameClock: GameClock;
  player: Player;
  npcs: Record<string, NPC>;
  relationships: Record<string, Relationship>;
  currentMapId: string;
  unlockedMapIds: string[];
  eventStates: Record<string, EventState>;
  inventory: Inventory;
  transactions: Transaction[];
  workSessions: WorkSession[];
  /** Last day index whose day-start processing ran (prevents double processing). */
  lastProcessedDay: number;
  family: FamilyState;
  /** Weather of the current day, rolled at day start (WeatherSystem). */
  weather: { day: number; kind: Weather };
  /** Seed for deterministic per-save randomness (weather, names). */
  worldSeed: number;
};

export type SaveData = {
  schemaVersion: number;
  saveId: string;
  savedAtRealTime: string; // ISO; never used for game progress
  gameState: GameState;
};

/** All static content, passed to systems that need lookups. */
export type ContentDB = {
  npcs: Record<string, NPCDefinition>;
  schedules: Record<string, ScheduleDefinition>;
  dialogues: Record<string, DialogueSet>;
  jobs: Record<string, JobDefinition>;
  items: Record<string, ItemDefinition>;
  maps: Record<string, MapDefinition>;
  locations: Record<string, LocationDefinition>;
  conditions: Record<string, ConditionDefinition>;
  events: Record<string, EventDefinition>;
};
