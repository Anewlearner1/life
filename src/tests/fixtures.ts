import { COND, JOB, LOC, MAP } from "../data/ids";
import { createNewGame } from "../game/GameState";
import type { CharacterAppearance, ContentDB, GameState } from "../game/types";

export const ARTIST = "npc_007";
export const OWNER = "npc_001";

export const appearance: CharacterAppearance = { bodyId: "b1", hairId: "h1", outfitId: "o1", accessoryIds: [] };

export function makeContent(): ContentDB {
  const aff = (atLeast: number) => ({ type: "affection", npcId: ARTIST, atLeast }) as const;
  return {
    npcs: {
      [OWNER]: { id: OWNER, name: "Owner", spriteKey: "NPC_001", personalityTags: [], occupation: "cafe", scheduleId: "sch_owner", dialogueSetId: "dlg_owner", romanceable: false },
      [ARTIST]: { id: ARTIST, name: "Artist", spriteKey: "NPC_007", personalityTags: [], occupation: "artist", scheduleId: "sch_artist", dialogueSetId: "dlg_artist", romanceable: true },
    },
    schedules: {
      // Owner: rest overnight (spans midnight) at home, work at cafe by day.
      sch_owner: { id: "sch_owner", entries: [
        { startMinute: 1020, endMinute: 480, activity: "rest", locationId: LOC.home },
        { startMinute: 480, endMinute: 1020, activity: "work", locationId: LOC.cafe },
      ] },
      sch_artist: { id: "sch_artist", entries: [
        { startMinute: 0, endMinute: 480, activity: "sleep", locationId: LOC.home },
        { startMinute: 480, endMinute: 1440, activity: "social", locationId: LOC.cafe },
      ] },
    },
    dialogues: {
      dlg_owner: { id: "dlg_owner", lines: [{ id: "o1", text: "Welcome." }] },
      dlg_artist: { id: "dlg_artist", lines: [
        { id: "a0", text: "Hello." },
        { id: "a1", text: "Nice to see you.", minAffection: 20, affectionDelta: 2 },
        { id: "a2", text: "I missed you.", minAffection: 50, affectionDelta: 2 },
      ] },
    },
    jobs: {
      [JOB.barista]: {
        id: JOB.barista, name: "Barista", workplaceLocationId: LOC.cafe,
        shiftRules: [
          { startMinute: 9 * 60, endMinute: 13 * 60 }, // every day
          { weekday: 6, startMinute: 20 * 60, endMinute: 22 * 60 }, // Saturday evening only
        ],
        baseWage: 100, minigameId: "mg_rhythm_cafe", needDelta: { stamina: -15, satiety: -10, mood: 5 }, durationMinutes: 240,
      },
    },
    items: {
      sandwich: { id: "sandwich", name: "Sandwich", price: 30, iconAsset: "x.png", useEffect: { satiety: 30 }, useMinutes: 15 },
      juice: { id: "juice", name: "Juice", price: 10, iconAsset: "y.png", useEffect: { stamina: 10 }, useMinutes: 5 },
    },
    maps: {
      [MAP.starter]: { id: MAP.starter, name: "Town", width: 6, height: 4, rows: ["......", ".ww...", "......", "ssssss"], locationIds: [LOC.home, LOC.cafe], spawn: { x: 2, y: 2 }, props: [] },
      [MAP.rural]: { id: MAP.rural, name: "Rural", width: 5, height: 3, rows: [".....", ",,,,,", "....."], locationIds: [LOC.farm], unlockConditionId: COND.unlockRural, spawn: { x: 0, y: 1 }, props: [] },
    },
    locations: {
      [LOC.home]: { id: LOC.home, mapId: MAP.starter, name: "Home", type: "home", door: { x: 1, y: 0 }, interactionIds: [] },
      [LOC.cafe]: { id: LOC.cafe, mapId: MAP.starter, name: "Cafe", type: "workplace", door: { x: 4, y: 1 }, interactionIds: [] },
      [LOC.farm]: { id: LOC.farm, mapId: MAP.rural, name: "Farm", type: "social", door: { x: 2, y: 1 }, interactionIds: [] },
    },
    conditions: {
      [COND.unlockRural]: { id: COND.unlockRural, all: [{ type: "stage", npcId: ARTIST, stage: "partner" }, { type: "shiftsWorked", atLeast: 1 }] },
      c_aff20: { id: "c_aff20", all: [aff(20)] },
      c_date: { id: "c_date", all: [aff(50), { type: "eventCompleted", eventId: "ev_intro" }] },
      c_confess: { id: "c_confess", all: [aff(75), { type: "eventCompleted", eventId: "ev_date" }] },
      c_day2: { id: "c_day2", all: [{ type: "day", atLeast: 2 }] },
      c_day3: { id: "c_day3", all: [{ type: "day", atLeast: 3 }] },
      c_rich: { id: "c_rich", all: [{ type: "money", atLeast: 1000 }] },
    },
    events: {
      ev_intro: { id: "ev_intro", triggerType: "talk", npcId: ARTIST, conditionIds: ["c_aff20"], effects: [{ type: "affection", npcId: ARTIST, delta: 5 }, { type: "message", text: "Met the artist." }], lines: ["I paint."] },
      ev_date: { id: "ev_date", triggerType: "talk", npcId: ARTIST, conditionIds: ["c_date"], effects: [{ type: "affection", npcId: ARTIST, delta: 5 }], lines: ["Walk with me?"] },
      ev_confess: { id: "ev_confess", triggerType: "talk", npcId: ARTIST, conditionIds: ["c_confess"], effects: [{ type: "setStage", npcId: ARTIST, stage: "partner" }, { type: "message", text: "Partners!" }], lines: ["Be mine?"] },
      ev_day2: { id: "ev_day2", triggerType: "dayStart", conditionIds: ["c_day2"], effects: [{ type: "money", delta: 10, reason: "Allowance" }], lines: [] },
      ev_day3: { id: "ev_day3", triggerType: "dayStart", conditionIds: ["c_day3"], effects: [{ type: "message", text: "Day three" }], lines: [] },
    },
  };
}

export function newGame(content = makeContent()): GameState {
  return createNewGame(content, "Tester", appearance);
}

/** Moves the player to a location's door. */
export function standAt(state: GameState, content: ContentDB, locationId: string): void {
  const loc = content.locations[locationId];
  state.player.position = { mapId: loc.mapId, x: loc.door.x, y: loc.door.y, facing: "down" };
  state.currentMapId = loc.mapId;
}

// ---------- second-phase (family / weather) fixtures; test-local, independent of src/data content ----------

export const RING = "item_ring";
export const FARM_JOB = "job_farmhand";
export const HOME_IN = "map_home_in";

/** makeContent() plus a ring, an indoor home interior with a bed, a farm job and family conditions/events. */
export function makeFamilyContent(opts: { withBed?: boolean } = {}): ContentDB {
  const c = makeContent();
  const withBed = opts.withBed ?? true;
  c.items[RING] = { id: RING, name: "Ring", price: 500, iconAsset: "r.png" };
  if (withBed) {
    c.maps[HOME_IN] = { id: HOME_IN, name: "Home inside", width: 10, height: 8, rows: Array(8).fill("W".repeat(10)), locationIds: [LOC.homeBed], spawn: { x: 4, y: 6 }, indoor: true, props: [] };
    c.locations[LOC.homeBed] = { id: LOC.homeBed, mapId: HOME_IN, name: "Bed", type: "home", door: { x: 1, y: 3 }, interactionIds: [] };
  }
  c.jobs[FARM_JOB] = {
    id: FARM_JOB, name: "Farmhand", workplaceLocationId: LOC.farm,
    shiftRules: [{ startMinute: 9 * 60, endMinute: 13 * 60 }],
    baseWage: 120, minigameId: "mg_rhythm_farm", needDelta: { stamina: -20 }, durationMinutes: 180,
  };
  c.conditions.c_ring = { id: "c_ring", all: [{ type: "hasItem", itemId: RING }] };
  c.conditions.c_baby = { id: "c_baby", all: [{ type: "marriedDays", atLeast: 1 }, { type: "childrenAtMost", count: 2 }, { type: "notPregnant" }] };
  c.events.ev_baby = { id: "ev_baby", triggerType: "manual", npcId: ARTIST, conditionIds: ["c_baby"], effects: [{ type: "conceive" }], lines: [] };
  c.events.ev_marry = {
    id: "ev_marry", triggerType: "manual", npcId: ARTIST, conditionIds: ["c_ring"],
    effects: [{ type: "consumeItem", itemId: RING }, { type: "marry", npcId: ARTIST }], lines: ["I do"],
  };
  return c;
}

/** Makes the artist a long-standing partner with max affection and gives the player a ring. */
export function makeMarriageReady(state: GameState): void {
  const rel = state.relationships[ARTIST];
  rel.stage = "partner";
  rel.affection = 100;
  rel.partnerSinceMinute = state.gameClock.totalMinutes - 10 * 1440;
  state.inventory[RING] = 1;
}
