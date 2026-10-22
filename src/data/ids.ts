// Fixed IDs shared by content data, maps and systems. Add new IDs here first.

export const MAP = {
  starter: "map_starter",
  rural: "map_rural",
  homeIn: "map_home_in", // interiors: always open (no unlock condition)
  shopIn: "map_shop_in",
  cafeIn: "map_cafe_in",
} as const;

export const LOC = {
  home: "loc_home", // entrances (gates) on map_starter; NPC schedules use them as "outside the building"
  shop: "loc_shop",
  cafe: "loc_cafe",
  homeBed: "loc_home_bed", // sleep / rest
  homeExit: "loc_home_exit",
  shopCounter: "loc_shop_counter", // shop panel; shopkeeper stands behind it
  shopExit: "loc_shop_exit",
  cafeCounter: "loc_cafe_counter", // workplace for job_barista; cafe owner stands behind it
  cafeSeat: "loc_cafe_seat", // social spot where visiting NPCs sit
  cafeExit: "loc_cafe_exit",
  park: "loc_park", // social place (gazebo)
  gateEast: "loc_gate_east", // starter -> rural (locked until cond_unlock_rural)
  farm: "loc_farm", // rural social place
  gateWest: "loc_gate_west", // rural -> starter
} as const;

export const NPC_IDS = [
  "npc_001", // CafeOwner
  "npc_002", // Shopkeeper
  "npc_003", // Neighbor
  "npc_004", // Student
  "npc_005", // Farmer
  "npc_006", // Officeworker
  "npc_007", // Artist — main romance route (文件E-4 原型預設)
  "npc_008", // Mailcarrier
] as const;

export const JOB = { barista: "job_barista" } as const;
export const MINIGAME = { rhythmCafe: "mg_rhythm_cafe" } as const;
export const COND = { unlockRural: "cond_unlock_rural" } as const;
