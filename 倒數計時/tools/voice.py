"""倒數計時 韓文配音（edge-tts）。讀 timeline.json 的 subs[].ko / speaker，輸出 vo/<id>.mp3。

  python3 tools/voice.py            # 只生成缺少的
  python3 tools/voice.py --force    # 全部重生

聲線（edge-tts 能用的韓文聲線只有 SunHi／InJoon／Hyunsu）：
  her    主角＋旁白：ko-KR-SunHiNeural，音調稍高、語速稍慢（安靜少女）
  friend 好友：ko-KR-SunHiNeural，音調更高、語速更快（開朗）
  him    男生：ko-KR-InJoonNeural，語速稍慢、輕聲
"""
import asyncio, json, os, sys
import edge_tts

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOICES = {
    "her":    dict(voice="ko-KR-SunHiNeural", pitch="+12Hz", rate="-6%", volume="+0%"),
    "friend": dict(voice="ko-KR-SunHiNeural", pitch="+30Hz", rate="+12%", volume="+0%"),
    "him":    dict(voice="ko-KR-InJoonNeural", pitch="+0Hz", rate="-8%", volume="+0%"),
}
proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")


async def main():
    cfg = json.load(open(os.path.join(ROOT, "timeline.json"), encoding="utf-8"))
    lines = [s for s in cfg["subs"] if s.get("ko_tts") or s.get("ko")]
    if cfg.get("card", {}).get("ko_tts"):
        lines.append(dict(id="card", ko_tts=cfg["card"]["ko_tts"], speaker="her", **cfg["card"].get("vo", {})))
    for s in lines:
        out = os.path.join(ROOT, "vo", f"{s['id']}.mp3")
        if os.path.exists(out) and "--force" not in sys.argv:
            continue
        v = dict(VOICES[s["speaker"]]); v.update({k: s[k] for k in ("pitch", "rate") if k in s})
        text = s.get("ko_tts") or s["ko"].replace("\n", " ")
        await edge_tts.Communicate(text, proxy=proxy, **v).save(out)
        print("✓", s["id"], v["voice"], text)

asyncio.run(main())
