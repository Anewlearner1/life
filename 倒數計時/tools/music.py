"""倒數計時 配樂合成（純 numpy，32 秒，48kHz 立體聲）。

結構對應 timeline.json：
  0–14s   A 小調鋼琴動機 + 時鐘滴答（數字出現時加一道 shimmer）
  14–19s  看到「2」：滴答停止，只剩低頻心跳
  19–23.5s 弦樂 pad 漸強（擁抱）
  23.5–29.3s 撞到陌生人：落書悶響（24.05s），對視、數字滾動時（27.8s）轉 C 大調
  29.3–32s 片尾字卡：長和弦收尾 + 最後一聲滴答
用法： python3 tools/music.py out.wav
"""
import sys, wave
import numpy as np

SR = 48000
DUR = 32.0
N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def add(sig, t0, pan=0.0, gain=1.0):
    i0 = int(t0 * SR)
    if i0 >= N:
        return
    sig = sig[: N - i0] * gain
    L[i0:i0 + len(sig)] += sig * np.sqrt((1 - pan) / 2)
    R[i0:i0 + len(sig)] += sig * np.sqrt((1 + pan) / 2)


def env_adsr(n, a=0.005, d=0.3, s=0.3, r=0.6):
    t = np.arange(n) / SR
    e = np.where(t < a, t / a, s + (1 - s) * np.exp(-(t - a) / d))
    tail = int(r * SR)
    if tail < n:
        e[-tail:] *= np.linspace(1, 0, tail)
    return e


def piano(m, dur=2.5, vel=0.5):
    n = int(dur * SR); t = np.arange(n) / SR; f = midi(m)
    s = sum(np.sin(2 * np.pi * f * k * t * (1 + 0.0004 * k)) * (0.6 ** (k - 1)) * np.exp(-t * (1.2 + 0.9 * k))
            for k in range(1, 7))
    return s * env_adsr(n, 0.003, 0.5, 0.0, 0.3) * vel


def pad(ms, dur, vel=0.12, bright=0.3, a=1.5):
    n = int(dur * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for m in ms:
        for det in (-0.12, 0.0, 0.11):
            f = midi(m + det)
            s += np.sin(2 * np.pi * f * t) + bright * np.sin(2 * np.pi * 2 * f * t) + bright * 0.4 * np.sin(2 * np.pi * 3 * f * t)
    e = np.minimum(t / a, 1) * np.minimum((dur - t) / 1.2, 1)
    trem = 1 + 0.08 * np.sin(2 * np.pi * 4.6 * t)
    return s / (3 * len(ms)) * np.clip(e, 0, 1) * trem * vel


def tick(vel=0.25, high=True):
    n = int(0.05 * SR); t = np.arange(n) / SR
    f = 3200 if high else 2400
    return (np.sin(2 * np.pi * f * t) * 0.6 + rng.normal(0, 0.4, n)) * np.exp(-t * 160) * vel


def heartbeat(vel=0.6):
    n = int(0.5 * SR); t = np.arange(n) / SR
    thump = lambda d: np.where(t >= d, np.sin(2 * np.pi * 52 * (t - d)) * np.exp(-(t - d) * 18), 0)
    return (thump(0.0) + 0.7 * thump(0.22)) * vel


def shimmer(dur=1.6, vel=0.12):
    n = int(dur * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for m in (88, 91, 95, 100):
        s += np.sin(2 * np.pi * midi(m) * t + rng.uniform(0, 6)) * (0.5 + 0.5 * np.sin(2 * np.pi * rng.uniform(5, 9) * t))
    return s / 4 * np.minimum(t / 0.25, 1) * np.exp(-t * 1.8) * vel


def whoosh(dur=0.9, vel=0.18):
    n = int(dur * SR); t = np.arange(n) / SR
    noise = rng.normal(0, 1, n)
    k = np.ones(40) / 40
    lo = np.convolve(noise, k, mode="same")
    return (noise - lo) * np.sin(np.pi * t / dur) ** 2 * vel


def thud(vel=0.7):
    n = int(0.6 * SR); t = np.arange(n) / SR
    body = np.sin(2 * np.pi * (70 + 60 * np.exp(-t * 30)) * t) * np.exp(-t * 11)
    slap = rng.normal(0, 1, n) * np.exp(-t * 70) * 0.5
    return (body + slap) * vel


# --- 0–14s：A 小調鋼琴動機（72 BPM, 每拍 0.833s）+ 滴答 ---
beat = 60 / 72
motif = [(69, 0), (72, 1), (76, 2), (74, 3.5), (72, 4), (71, 5), (69, 6)]   # A C E D C B A
chords = [(0.0, [45, 57]), (beat * 4, [41, 53]), (beat * 8, [43, 55]), (beat * 12, [40, 52])]  # Am F G Em
for rep, base in enumerate((0.2, 0.2 + beat * 8)):
    for m, b in motif:
        add(piano(m + (12 if rep else 0) * 0, 2.4, 0.32), base + b * beat, pan=0.15)
for t0, ch in chords:
    for m in ch:
        add(piano(m, 3.4, 0.28), 0.2 + t0, pan=-0.2)
add(pad([57, 60, 64], 14.0, 0.07, 0.2, 3.0), 0.0)
t = 0.0
while t < 14.0:
    add(tick(0.16 if int(t * 2) % 2 else 0.22, high=int(t * 2) % 2 == 0), t, pan=0.3)
    t += 0.5
add(whoosh(1.0, 0.16), 3.7)
add(shimmer(2.0, 0.14), 4.5, pan=-0.3)
add(shimmer(1.2, 0.08), 11.1, pan=0.4)

# --- 14–19s：「2」——滴答停、心跳 ---
add(shimmer(1.6, 0.10), 15.5)
add(piano(45, 4.5, 0.45), 15.6)            # 低音 A 單音重擊
add(piano(57, 4.5, 0.25), 15.6)
for hb in np.arange(16.2, 19.2, 0.95):
    add(heartbeat(0.55), hb)
add(pad([45, 52], 5.0, 0.05, 0.1, 2.0), 14.2)

# --- 19–24s：擁抱，弦樂漸強 Am → F ---
add(pad([57, 60, 64, 69], 3.0, 0.16, 0.35, 2.2), 19.0)
add(pad([53, 57, 60, 65], 2.4, 0.19, 0.35, 0.8), 21.6)
for m, b in [(76, 0), (74, 1), (72, 2), (71, 3), (72, 4.5)]:
    add(piano(m, 2.6, 0.30), 19.6 + b * beat, pan=0.1)
add(piano(41, 3.0, 0.3), 21.6, pan=-0.2)

# --- 24–29s：撞到他，轉 C 大調 ---
add(thud(0.75), 24.05, pan=-0.1)
add(thud(0.45), 24.25, pan=0.2)
add(shimmer(2.2, 0.16), 27.8, pan=0.2)        # 數字往上跳
for i, m in enumerate([60, 64, 67, 72, 76, 79]):
    add(piano(m, 2.4, 0.22), 27.85 + i * 0.12, pan=-0.3 + i * 0.12)
add(pad([48, 60, 64, 67], 1.9, 0.14, 0.45, 1.0), 27.6)

# --- 29–32s：片尾 C add9，最後一聲滴答 ---
add(pad([48, 55, 64, 67, 74], 2.7, 0.16, 0.5, 0.4), 29.3)
for m in (48, 60, 67, 74):
    add(piano(m, 2.7, 0.28), 29.35)
add(tick(0.28), 31.2, pan=0.0)

# --- 簡易殘響（多組延遲） + 母帶 ---
def verb(x):
    y = x.copy()
    for d, g in ((0.031, 0.35), (0.047, 0.3), (0.071, 0.25), (0.113, 0.2), (0.173, 0.15), (0.263, 0.1)):
        k = int(d * SR); y[k:] += x[:-k] * g
    return y

L, R = verb(L), verb(np.roll(R, 37))
fade = np.ones(N); fade[-int(0.6 * SR):] = np.linspace(1, 0, int(0.6 * SR))
st = np.stack([L, R], 1) * fade[:, None]
st = np.tanh(st / np.abs(st).max() * 1.4) * 0.89
out = sys.argv[1] if len(sys.argv) > 1 else "music.wav"
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes())
print("wrote", out, f"{DUR}s")
