// Fixed IDs shared by content data, maps and systems. Add new IDs here first.

export const MAP = { starter: "map_starter", rural: "map_rural" } as const;

export const LOC = {
  home: "loc_home",
  shop: "loc_shop",
  cafe: "loc_cafe", // workplace for job_barista
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
