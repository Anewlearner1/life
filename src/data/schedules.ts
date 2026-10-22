import type { ScheduleDefinition } from "../game/types";
import { LOC } from "./ids";

// Each schedule covers 0–1440 with no gaps. Sleep entries wrap midnight (start 1320 -> end 360).
// Times are minutes of day: 360 = 06:00, 540 = 09:00, 1320 = 22:00.
export const schedules: Record<string, ScheduleDefinition> = {
  // npc_001 陳書豪: works at the cafe
  sch_npc_001: {
    id: "sch_npc_001",
    entries: [
      { startMinute: 1320, endMinute: 360, activity: "sleep", locationId: LOC.home },
      { startMinute: 360, endMinute: 420, activity: "rest", locationId: LOC.home },
      { startMinute: 420, endMinute: 1140, activity: "work", locationId: LOC.cafe },
      { startMinute: 1140, endMinute: 1260, activity: "social", locationId: LOC.park },
      { startMinute: 1260, endMinute: 1320, activity: "rest", locationId: LOC.home },
    ],
  },
  // npc_002 李美玲: works at the shop
  sch_npc_002: {
    id: "sch_npc_002",
    entries: [
      { startMinute: 1320, endMinute: 360, activity: "sleep", locationId: LOC.home },
      { startMinute: 360, endMinute: 480, activity: "rest", locationId: LOC.home },
      { startMinute: 480, endMinute: 1140, activity: "work", locationId: LOC.shop },
      { startMinute: 1140, endMinute: 1230, activity: "social", locationId: LOC.cafe },
      { startMinute: 1230, endMinute: 1320, activity: "rest", locationId: LOC.home },
    ],
  },
  // npc_003 周建國: rotates park / shop / cafe / home
  sch_npc_003: {
    id: "sch_npc_003",
    entries: [
      { startMinute: 1320, endMinute: 420, activity: "sleep", locationId: LOC.home },
      { startMinute: 420, endMinute: 540, activity: "rest", locationId: LOC.home },
      { startMinute: 540, endMinute: 600, activity: "shopping", locationId: LOC.shop },
      { startMinute: 600, endMinute: 720, activity: "social", locationId: LOC.park },
      { startMinute: 720, endMinute: 840, activity: "social", locationId: LOC.cafe },
      { startMinute: 840, endMinute: 960, activity: "rest", locationId: LOC.park },
      { startMinute: 960, endMinute: 1080, activity: "shopping", locationId: LOC.shop },
      { startMinute: 1080, endMinute: 1200, activity: "social", locationId: LOC.park },
      { startMinute: 1200, endMinute: 1320, activity: "rest", locationId: LOC.home },
    ],
  },
  // npc_004 林小晴: studies (work) at the cafe, socializes at the park
  sch_npc_004: {
    id: "sch_npc_004",
    entries: [
      { startMinute: 1380, endMinute: 540, activity: "sleep", locationId: LOC.home },
      { startMinute: 540, endMinute: 720, activity: "work", locationId: LOC.cafe },
      { startMinute: 720, endMinute: 780, activity: "rest", locationId: LOC.park },
      { startMinute: 780, endMinute: 960, activity: "work", locationId: LOC.cafe },
      { startMinute: 960, endMinute: 1020, activity: "shopping", locationId: LOC.shop },
      { startMinute: 1020, endMinute: 1140, activity: "social", locationId: LOC.park },
      { startMinute: 1140, endMinute: 1380, activity: "rest", locationId: LOC.home },
    ],
  },
  // npc_005 黃德福: works at the farm
  sch_npc_005: {
    id: "sch_npc_005",
    entries: [
      { startMinute: 1260, endMinute: 300, activity: "sleep", locationId: LOC.home },
      { startMinute: 300, endMinute: 1080, activity: "work", locationId: LOC.farm },
      { startMinute: 1080, endMinute: 1140, activity: "shopping", locationId: LOC.shop },
      { startMinute: 1140, endMinute: 1260, activity: "social", locationId: LOC.park },
    ],
  },
  // npc_006 許偉杰: office work simulated at the cafe
  sch_npc_006: {
    id: "sch_npc_006",
    entries: [
      { startMinute: 1350, endMinute: 420, activity: "sleep", locationId: LOC.home },
      { startMinute: 420, endMinute: 480, activity: "rest", locationId: LOC.home },
      { startMinute: 480, endMinute: 1020, activity: "work", locationId: LOC.cafe },
      { startMinute: 1020, endMinute: 1080, activity: "shopping", locationId: LOC.shop },
      { startMinute: 1080, endMinute: 1200, activity: "social", locationId: LOC.park },
      { startMinute: 1200, endMinute: 1350, activity: "rest", locationId: LOC.home },
    ],
  },
  // npc_007 沈若溪: paints outdoors at the park, cafe for breaks
  sch_npc_007: {
    id: "sch_npc_007",
    entries: [
      { startMinute: 1380, endMinute: 540, activity: "sleep", locationId: LOC.home },
      { startMinute: 540, endMinute: 660, activity: "work", locationId: LOC.park },
      { startMinute: 660, endMinute: 720, activity: "shopping", locationId: LOC.shop },
      { startMinute: 720, endMinute: 840, activity: "rest", locationId: LOC.cafe },
      { startMinute: 840, endMinute: 1020, activity: "work", locationId: LOC.park },
      { startMinute: 1020, endMinute: 1140, activity: "social", locationId: LOC.cafe },
      { startMinute: 1140, endMinute: 1380, activity: "rest", locationId: LOC.home },
    ],
  },
  // npc_008 郭志強: mail route (work), breaks and evenings around town
  sch_npc_008: {
    id: "sch_npc_008",
    entries: [
      { startMinute: 1290, endMinute: 360, activity: "sleep", locationId: LOC.home },
      { startMinute: 360, endMinute: 420, activity: "rest", locationId: LOC.home },
      { startMinute: 420, endMinute: 720, activity: "work", locationId: LOC.park },
      { startMinute: 720, endMinute: 780, activity: "rest", locationId: LOC.cafe },
      { startMinute: 780, endMinute: 1020, activity: "work", locationId: LOC.shop },
      { startMinute: 1020, endMinute: 1110, activity: "social", locationId: LOC.park },
      { startMinute: 1110, endMinute: 1200, activity: "social", locationId: LOC.cafe },
      { startMinute: 1200, endMinute: 1290, activity: "rest", locationId: LOC.home },
    ],
  },
};
