"""Build assets/asset_tracker.csv: every Asset ID from the art list v0.1, its priority and produced files."""
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pixel import ASSETS, ROOT
from PIL import Image

# (ID, 名稱, 狀態) from 美術資產需求清單 v0.1
IDS = """CHAR-001|玩家角色基礎 Sprite|必要-MVP
CHAR-002|玩家四方向行走動畫|必要-MVP
CHAR-003|玩家待機動畫|必要-MVP
CHAR-004|角色髮型素材|建議-MVP
CHAR-005|角色服裝素材|建議-MVP
CHAR-006|角色配件素材|未來擴充
CHAR-007|角色動作動畫|待確認
NPC-001|NPC 基本角色套組|必要-MVP
NPC-002|NPC 四方向行走動畫|必要-MVP
NPC-003|NPC 對話頭像|建議-MVP
NPC-004|NPC 情緒表情|建議-MVP
NPC-005|NPC 職業／服裝差異|建議-MVP
NPC-006|NPC 約會／伴侶事件插圖|未來擴充
MAP-001|地面 Tile Set|必要-MVP
MAP-002|道路與路徑轉角圖塊|必要-MVP
MAP-003|建築外觀套組|必要-MVP
MAP-004|建築門窗與入口|必要-MVP
MAP-005|自然環境圖塊|建議-MVP
MAP-006|街區裝飾物|建議-MVP
MAP-007|室內場景圖塊|建議-MVP
MAP-008|鄉村環境套組|未來擴充
MAP-009|都市環境套組|必要方向
MAP-010|地圖邊界與不可通行物件|必要-MVP
BLD-001|住宅外觀|建議-MVP
BLD-002|商店外觀|必要-MVP
BLD-003|工作場所外觀|必要-MVP
BLD-004|社交場所外觀|建議-MVP
BLD-005|建築招牌與營業標誌|建議-MVP
BLD-006|室內家具與陳設|建議-MVP
BLD-007|房屋裝修與家具擺放素材|未來擴充
OBJ-001|互動提示圖示|必要-MVP
OBJ-002|床與休息物件|待確認
OBJ-003|食物圖示或 Sprite|建議-MVP
OBJ-004|商店商品圖示|建議-MVP
OBJ-005|工作工具或設備|待確認
OBJ-006|禮物物品|未來擴充
OBJ-007|交通工具|未來擴充
UI-001|需求狀態圖示|必要-MVP
UI-002|金錢圖示|必要-MVP
UI-003|遊戲時鐘與日期 UI|必要-MVP
UI-004|時間控制按鈕|必要-MVP
UI-005|對話框與文字面板|必要-MVP
UI-006|按鈕套組|必要-MVP
UI-007|分頁／功能圖示|建議-MVP
UI-008|提示、警告與通知圖示|建議-MVP
UI-009|商店介面框體|建議-MVP
UI-010|角色創建介面素材|建議-MVP
UI-011|關係／好感度介面|建議-MVP
UI-012|存檔／載入介面|必要-MVP
UI-013|區域解鎖提示|建議-MVP
MINI-001|小遊戲背景／面板|必要-MVP
MINI-002|節奏提示符號|必要-MVP
MINI-003|判定區／時間軌道|必要-MVP
MINI-004|成功／普通／失誤提示|必要-MVP
MINI-005|分數與薪資結算面板|必要-MVP
MINI-006|工作場所裝飾與工具|建議-MVP
EVT-001|事件對話面板|必要-MVP
EVT-002|關係階段提示|建議-MVP
EVT-003|戀愛事件背景|未來擴充
EVT-004|事件插圖／CG|未來擴充
EVT-005|成就／解鎖特效|建議-MVP
FX-001|互動提示動畫|建議-MVP
FX-002|金錢獲得提示|建議-MVP
FX-003|好感度增加提示|建議-MVP
FX-004|區域解鎖特效|建議-MVP
FX-005|需求低值提示效果|建議-MVP
FX-006|環境天氣特效|未來擴充
FX-007|日夜光照效果|未來擴充
AUDIO-001|音量／音效控制圖示|建議-MVP
AUDIO-002|節奏小遊戲音符圖示|待確認"""

# IDs covered by assets filed under another ID (alias -> source ID prefix)
ALIASES = {
    "CHAR-002": "CHAR-001", "NPC-002": "NPC-001", "NPC-003": "NPC-001", "NPC-004": "NPC-001",
    "NPC-005": "NPC-001", "MAP-003": "BLD-00", "MAP-004": "BLD-00", "MAP-009": "MAP-00",
    "OBJ-002": "BLD-006", "EVT-001": "UI-005", "EVT-005": "FX-004", "AUDIO-002": "MINI-002",
}


def asset_id(name):
    m = re.match(r"([A-Z]+)_(\d{3})_", name)
    return f"{m.group(1)}-{m.group(2)}" if m else None


def main():
    files = {}
    for p in sorted(ASSETS.rglob("*.png")):
        aid = asset_id(p.name)
        if aid:
            w, h = Image.open(p).size
            files.setdefault(aid, []).append(f"{p.relative_to(ROOT)} ({w}x{h})")

    out = ASSETS / "asset_tracker.csv"
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        wr = csv.writer(f)
        wr.writerow(["Asset ID", "名稱", "需求狀態", "製作狀態", "檔案數", "檔案"])
        for line in IDS.splitlines():
            aid, name, need = line.split("|")
            own = files.get(aid, [])
            alias = ALIASES.get(aid)
            via = [x for k, v in files.items() if alias and k.startswith(alias) for x in v] if not own else []
            state = "已完成(v01)" if own else ("共用素材" if via else "未製作")
            wr.writerow([aid, name, need, state, len(own), "; ".join(own) or (f"見 {alias}" if via else "")])
    print(out)


if __name__ == "__main__":
    main()
