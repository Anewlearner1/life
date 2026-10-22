import type { ContentDB } from "../game/types";
import { conditions, events } from "./events";
import { items } from "./items";
import { jobs } from "./jobs";
import { dialogues } from "./dialogues";
import { locations, maps } from "./maps";
import { npcs } from "./npcs";
import { schedules } from "./schedules";

/** All static content assembled for the systems (GameController owns the single instance). */
export const content: ContentDB = { npcs, schedules, dialogues, jobs, items, maps, locations, conditions, events };
