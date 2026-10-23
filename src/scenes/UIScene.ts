import Phaser from "phaser";
import { GameConfig } from "../game/GameConfig";
import { STAGE_LABEL, iconKey, type DialogueSpec, type GameController, type OpenRequest } from "../game/GameController";
import { getRel } from "../systems/RelationshipSystem";
import { DialoguePanel } from "../ui/DialoguePanel";
import { Hud } from "../ui/Hud";
import { ModalMenu, type MenuSpec } from "../ui/ModalMenu";
import { showBanner, Toasts } from "../ui/Toasts";

const NEED_LABEL = { stamina: "體力", satiety: "飽足", mood: "心情" } as const;
const STAGE_ICON = {
  stranger: "EVT_002_Stage_Stranger",
  acquaintance: "EVT_002_Stage_Acquaintance",
  close: "EVT_002_Stage_CloseFriend",
  partner: "EVT_002_Stage_Partner",
  spouse: "EVT_002_Stage_Partner",
} as const;

/** HUD + toasts + dialogue + menus, drawn above WorldScene. Also drives the game clock. */
export class UIScene extends Phaser.Scene {
  private controller!: GameController;
  private hud!: Hud;
  private toasts!: Toasts;
  private menu?: ModalMenu;
  private dialogue?: DialoguePanel;
  private offs: (() => void)[] = [];

  constructor() {
    super("UI");
  }

  init(data: { controller: GameController }): void {
    this.controller = data.controller;
  }

  create(): void {
    const c = this.controller;
    this.hud = new Hud(this, c, { onBag: () => this.openMenu({ panel: "shop", tab: "bag" }) });
    this.toasts = new Toasts(this);
    this.layout();

    this.offs.push(
      c.events.on("toast", (t, k) => this.toasts.show(t, k)),
      c.events.on("banner", (t) => showBanner(this, t, this.hud.centerX, this.hud.bottom + 60, this.hud.width - 16)),
      c.events.on("saved", () => this.toasts.show("已存檔", "ok")),
      c.events.on("dialogue", (d) => this.openDialogue(d)),
      c.events.on("open", (r) => this.openMenu(r)),
    );
    this.scale.on("resize", this.layout, this);
    this.events.on(Phaser.Scenes.Events.WAKE, this.layout, this);
    this.events.once(Phaser.Scenes.Events.SHUTDOWN, () => {
      this.offs.forEach((o) => o());
      this.offs = [];
      this.scale.off("resize", this.layout, this);
      this.events.off(Phaser.Scenes.Events.WAKE, this.layout, this);
      this.toasts.clear();
      this.hud.destroy();
      this.closeMenu();
      this.dialogue?.destroy();
      this.controller.modalOpen = false;
    });
  }

  update(_t: number, delta: number): void {
    this.controller.tick(delta);
    this.hud.update();
    this.toasts.update();
  }

  private layout(): void {
    this.hud.layout();
    this.toasts.layout(this.hud.centerX, this.hud.bottom + 4, this.hud.width - 16);
    this.menu?.refresh();
    this.dialogue?.relayout();
  }

  private syncModal(): void {
    this.controller.modalOpen = !!this.menu || !!this.dialogue;
  }

  // ------------------------------------------------------------------ dialogue
  private openDialogue(spec: DialogueSpec): void {
    this.dialogue?.destroy();
    this.dialogue = new DialoguePanel(this, this.controller, spec, () => {
      this.dialogue = undefined;
      this.syncModal();
      this.controller.dialogueDone();
    });
    this.syncModal();
  }

  // ------------------------------------------------------------------ menus
  private closeMenu(): void {
    this.menu?.destroy();
    this.menu = undefined;
    this.syncModal();
  }

  private show(spec: () => MenuSpec): void {
    this.menu?.destroy();
    this.menu = new ModalMenu(this, spec);
    this.syncModal();
  }

  private refreshMenu(): void {
    this.menu?.refresh();
  }

  private openMenu(req: OpenRequest): void {
    const c = this.controller;
    const close = () => this.closeMenu();
    switch (req.panel) {
      case "npc":
        this.show(() => this.npcMenu(req.npcId));
        break;
      case "gift":
        this.show(() => ({
          title: "送禮",
          subtitle: `送給${c.npcName(req.npcId)}（好感度 +${GameConfig.relationship.giftAffection}）`,
          rows: c.giftables().map((g) => ({
            icon: g.icon,
            title: `${g.name} ×${g.count}`,
            button: {
              label: "送出",
              onClick: () => {
                close();
                c.giveGift(req.npcId, g.id);
              },
            },
          })),
          emptyText: "沒有可以送的禮物。到商店買花束或禮物盒吧！",
          buttons: [{ label: "返回", onClick: () => this.show(() => this.npcMenu(req.npcId)) }],
        }));
        break;
      case "shop":
        this.showShop(req.tab ?? "shop");
        break;
      case "home":
        this.show(() => ({
          title: c.content.locations[req.locationId]?.name ?? "家",
          icon: "UI_007_Tab_Character",
          body: ["要休息一下嗎？"],
          buttons: [
            {
              label: `睡覺（睡到隔天 ${c.wakeTimeLabel()}）`,
              name: "sleep",
              onClick: () => {
                close();
                c.sleep();
              },
            },
            {
              label: "休息（1 小時）",
              name: "rest",
              onClick: () => {
                close();
                c.rest();
              },
            },
            { label: "離開", name: "close", onClick: close },
          ],
        }));
        break;
      case "rest":
        this.show(() => ({
          title: c.content.locations[req.locationId]?.name ?? "休息",
          icon: "UI_007_Tab_Character",
          body: ["在這裡坐一下，放鬆心情。"],
          buttons: [
            {
              label: "休息（1 小時）",
              name: "rest",
              onClick: () => {
                close();
                c.rest();
              },
            },
            { label: "離開", name: "close", onClick: close },
          ],
        }));
        break;
      case "work":
        this.show(() => {
          const info = c.workInfo(req.locationId);
          if (!info) return { title: "沒有工作", buttons: [{ label: "離開", onClick: close }] };
          const body = [
            `${info.job.name}　基本薪資 $${info.job.baseWage}／班`,
            info.current ? `目前班表：${info.current}` : "目前不在班表時段",
            `下一班：${info.next}`,
          ];
          return {
            title: c.content.locations[req.locationId]?.name ?? "工作",
            icon: "UI_007_Tab_Work",
            body,
            note: info.check.ok ? undefined : `無法開始工作：${info.check.reason ?? ""}`,
            buttons: [
              {
                label: "開始工作",
                name: "work",
                enabled: info.check.ok,
                onClick: () => {
                  close();
                  c.startWork(req.locationId);
                },
              },
              { label: "離開", name: "close", onClick: close },
            ],
          };
        });
        break;
      case "locked":
        this.show(() => ({
          title: c.content.locations[req.locationId]?.name ?? "出口",
          icon: "UI_013_Lock_Locked",
          body: ["這裡還沒有開放。"],
          note: req.hint,
          buttons: [{ label: "確定", name: "ok", onClick: close }],
        }));
        break;
    }
  }

  private npcMenu(npcId: string): MenuSpec {
    const c = this.controller;
    const def = c.content.npcs[npcId];
    const rel = getRel(c.getState(), npcId);
    const portrait = `${def?.spriteKey}_Portrait_Neutral`;
    const gifts = c.giftables();
    return {
      title: def?.name ?? npcId,
      subtitle: `${def?.occupation ?? ""} · ${STAGE_LABEL[rel.stage]}`,
      portrait: this.textures.exists(portrait) ? portrait : undefined,
      icon: STAGE_ICON[rel.stage],
      affection: rel.affection,
      buttons: [
        {
          label: "聊天",
          name: "talk",
          icon: "OBJ_001_Talk",
          onClick: () => {
            this.closeMenu();
            c.talk(npcId);
          },
        },
        {
          label: gifts.length ? "送禮" : "送禮（沒有禮物）",
          name: "gift",
          enabled: gifts.length > 0,
          onClick: () => this.openMenu({ panel: "gift", npcId }),
        },
        { label: "關閉", name: "close", onClick: () => this.closeMenu() },
      ],
    };
  }

  private showShop(tab: "shop" | "bag"): void {
    const c = this.controller;
    this.show(() => {
      const st = c.getState();
      const tabs = [
        { label: "商店", name: "tab_shop", active: tab === "shop", onClick: () => this.showShop("shop") },
        { label: "背包", name: "tab_bag", active: tab === "bag", onClick: () => this.showShop("bag") },
      ];
      const effectText = (id: string) => {
        const it = c.content.items[id];
        if (!it.useEffect) return GIFT_HINT(id);
        return Object.entries(it.useEffect)
          .map(([k, v]) => `${NEED_LABEL[k as keyof typeof NEED_LABEL]}${(v as number) >= 0 ? "+" : ""}${v}`)
          .join(" ");
      };
      const rows =
        tab === "shop"
          ? Object.values(c.content.items).map((it) => ({
              icon: iconKey(it.iconAsset),
              title: it.name,
              sub: effectText(it.id),
              button: {
                label: `$${it.price}`,
                name: `buy:${it.id}`,
                enabled: st.player.money >= it.price,
                onClick: () => {
                  c.buy(it.id);
                  this.refreshMenu();
                },
              },
            }))
          : Object.entries(st.inventory)
              .filter(([id, n]) => n > 0 && c.content.items[id])
              .map(([id, n]) => {
                const it = c.content.items[id];
                return {
                  icon: iconKey(it.iconAsset),
                  title: `${it.name} ×${n}`,
                  sub: effectText(id),
                  button: it.useEffect
                    ? {
                        label: "使用",
                        name: `use:${id}`,
                        onClick: () => {
                          c.eat(id);
                          this.refreshMenu();
                        },
                      }
                    : undefined,
                };
              });
      return {
        title: tab === "shop" ? "商店" : "背包",
        tabs,
        moneyLine: `$${st.player.money}`,
        rows,
        emptyText: "背包是空的。",
        buttons: [{ label: "關閉", name: "close", onClick: () => this.closeMenu() }],
      };
    });
  }
}

const GIFT_HINT = (id: string) => (id === "item_flower" || id === "item_gift" ? "可以送給 NPC" : "");
