"""倒數計時 韓文版混音：配樂（music.py）＋ 韓文配音（vo/*.mp3），人聲進來時自動壓低配樂。

  python3 tools/mix.py out.wav [timing.json]
timing.json 會寫出每句配音的實際起訖秒數，給 assemble.py 排雙語字幕用。
"""
import json, os, subprocess, sys, tempfile, wave
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 48000
cfg = json.load(open(os.path.join(ROOT, "timeline.json"), encoding="utf-8"))
out = sys.argv[1]
timing_out = sys.argv[2] if len(sys.argv) > 2 else None

DUCK_DB = -10.0          # 人聲期間配樂壓低多少
ATTACK, RELEASE, LOOKAHEAD = 0.12, 0.45, 0.15
VO_GAIN_DB = {"her": 0.0, "friend": -0.5, "him": 0.5}
NARRATION = {"n1", "n2", "n3", "card"}   # 內心旁白：加一點空間感


def load(path, ch=2):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", str(ch), "-ar", str(SR), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float64).reshape(-1, ch) / 32768


def onepole_hp(x, fc=90.0):
    a = np.exp(-2 * np.pi * fc / SR); y = np.zeros_like(x); prev_x = prev_y = 0.0
    # vectorised enough for short clips
    for i, v in enumerate(x):
        prev_y = a * (prev_y + v - prev_x); prev_x = v; y[i] = prev_y
    return y


def room(x, wet=0.16):
    y = x.copy()
    for d, g in ((0.023, 0.5), (0.037, 0.4), (0.053, 0.32), (0.079, 0.25), (0.113, 0.18), (0.167, 0.12)):
        k = int(d * SR); y[k:] += x[:-k] * g * wet * 3
    return y


tmp = tempfile.mkdtemp(prefix="mix_")
mpath = os.path.join(tmp, "music.wav")
subprocess.run([sys.executable, os.path.join(ROOT, "tools", "music.py"), mpath], check=True, stdout=subprocess.DEVNULL)
music = load(mpath)
N = len(music)
vo = np.zeros(N)
timing = {}

items = [dict(s) for s in cfg["subs"]]
items.append(dict(id="card", speaker="her", vo_at=cfg["card"]["vo_at"]))
for s in items:
    a = load(os.path.join(ROOT, "vo", f"{s['id']}.mp3"), 1)[:, 0]
    idx = np.where(np.abs(a) > 0.01)[0]
    a = a[max(0, idx[0] - int(0.02 * SR)): idx[-1] + int(0.12 * SR)]
    a = onepole_hp(a)
    rms = np.sqrt(np.mean(a[np.abs(a) > 0.02] ** 2))
    a = a / rms * 10 ** ((-17 + VO_GAIN_DB[s["speaker"]]) / 20)          # 每句響度對齊
    a = np.tanh(a * 1.6) / 1.6                                            # 輕壓縮，收掉爆音
    if s["id"] in NARRATION:
        a = room(a)
    fade = int(0.01 * SR); a[:fade] *= np.linspace(0, 1, fade); a[-fade * 4:] *= np.linspace(1, 0, fade * 4)
    i0 = int(s["vo_at"] * SR); a = a[: N - i0]
    vo[i0:i0 + len(a)] += a
    timing[s["id"]] = [round(s["vo_at"], 3), round(s["vo_at"] + len(a) / SR, 3)]
    print(f"{s['id']:5s} {s['speaker']:6s} {timing[s['id']][0]:6.2f}–{timing[s['id']][1]:6.2f}s")

# 側鏈 ducking：用人聲包絡控制配樂增益（含 lookahead，人聲開口前就開始壓）
env = np.abs(vo)
win = int(0.03 * SR); env = np.convolve(env, np.ones(win) / win, mode="same")
active = (env > 0.004).astype(float)
la = int(LOOKAHEAD * SR); active = np.maximum(active, np.concatenate([active[la:], np.zeros(la)]))
target = 1 - active * (1 - 10 ** (DUCK_DB / 20))
g = np.empty(N); cur = 1.0
ka, kr = 1 - np.exp(-1 / (ATTACK * SR)), 1 - np.exp(-1 / (RELEASE * SR))
step = 48  # 每 1ms 更新一次增益，再內插
pts = np.arange(0, N, step); gv = np.empty(len(pts))
for j, i in enumerate(pts):
    t = target[i]; k = ka if t < cur else kr
    cur += (t - cur) * (1 - (1 - k) ** step); gv[j] = cur
g = np.interp(np.arange(N), pts, gv)

mix = music * g[:, None] + vo[:, None]
db = lambda x: 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-12)
sp = np.abs(vo) > 0; spm = np.convolve(sp.astype(float), np.ones(4800), "same") > 0
mu = music.mean(1)
print(f"配樂（無人聲段）{db(mu[~spm]):.1f} dB｜配樂（人聲段，壓低後）{db((mu * g)[spm]):.1f} dB｜"
      f"人聲 {db(vo[spm]):.1f} dB｜人聲高出配樂 {db(vo[spm]) - db((mu * g)[spm]):.1f} dB｜最深壓低 {20*np.log10(g.min()):.1f} dB")
peak = np.abs(mix).max()
mix = np.tanh(mix / peak * 1.15) * 0.80   # 柔性限幅，AAC 編碼後真峰值約 -1 dBTP
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
if timing_out:
    json.dump(timing, open(timing_out, "w"), indent=1)
print("wrote", out)
