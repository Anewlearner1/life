"""末日求生 Part 1 — fully synthesized soundtrack (numpy only).

Ambience, score and foley timed to the same shot list as render.py.
usage: python3 audio.py out.wav
"""
import sys
import wave

import numpy as np

SR = 48000
S = 48 / 45
DUR = 48.0
N = int(SR * DUR)
rng = np.random.default_rng(3)
L = np.zeros(N)
R = np.zeros(N)


def T(x):           # storyboard time -> seconds
    return x * S


def band(x, lo, hi):
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X = np.fft.rfft(x)
    m = np.ones_like(f)
    if lo:
        m *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi:
        m *= 1 / (1 + (f / hi) ** 4)
    return np.fft.irfft(X * m, len(x))


def env(n, a, r):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    if na:
        e[:na] = np.linspace(0, 1, na)
    if nr:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def put(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N:
        return
    sig = sig[: N - i]
    L[i:i + len(sig)] += sig * gain * (1 - pan) / 2 * 2 ** .5
    R[i:i + len(sig)] += sig * gain * (1 + pan) / 2 * 2 ** .5


def tvec(d):
    return np.arange(int(d * SR)) / SR


def reverb(x, decay=2.2, mix=.35):
    n = int(decay * SR)
    ir = rng.normal(0, 1, n) * np.exp(-np.arange(n) / SR * 6.9 / decay)
    ir = band(ir, 150, 5000)
    ir /= np.sqrt((ir ** 2).sum())
    m = len(x) + n
    y = np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(ir, m), m)
    out = np.zeros(m)
    out[:len(x)] = x * (1 - mix)
    return out + y * mix


def note(freq, d, amp=1.0, kind="piano"):
    t = tvec(d)
    if kind == "piano":
        s = sum(np.sin(2 * np.pi * freq * k * (1 + .0004 * k * k) * t) / k ** 1.6 * np.exp(-t * (1.5 + k * .8))
                for k in range(1, 7))
        s *= np.minimum(1, t / .005)
    else:  # pad: detuned saws, filtered later
        s = sum(((t * freq * dt) % 1 * 2 - 1) for dt in (.996, 1.0, 1.004)) / 3
        s *= env(len(t), min(1.2, d / 3), min(1.5, d / 3))
    return s * amp


def hz(n):  # midi -> Hz
    return 440 * 2 ** ((n - 69) / 12)


# ------------------------------------------------------------------ ambience
drone_t = tvec(DUR)
drone = (np.sin(2 * np.pi * 55 * drone_t) * .5 + np.sin(2 * np.pi * 82.4 * drone_t) * .3) \
    * (.6 + .4 * np.sin(2 * np.pi * .07 * drone_t))
rumble = band(rng.normal(0, 1, N), 30, 160) * .6
amb = (drone * .05 + rumble * .05)
amb *= np.interp(drone_t, [0, 1, T(29), T(32), T(38), T(42), DUR - 1, DUR], [0, 1, 1, 1.6, 1.6, 1.2, 1, 0])
L += amb
R += amb

# wind for the night / door sequence
wt = tvec(T(42) - T(28.6))
wind = band(rng.normal(0, 1, len(wt)), 250, 1400)
wind *= (.5 + .5 * np.sin(2 * np.pi * .23 * wt + 1)) * env(len(wt), 1.0, 1.5) * .09
put(wind, T(28.6), 1, -.3)
put(np.roll(wind, 9000), T(28.6), 1, .3)

# fire crackle during fire shots
for a, b in [(3.8, 8), (17, 21), (25, 29), (42, 45)]:
    d = T(b) - T(a)
    c = np.zeros(int(d * SR))
    for _ in range(int(d * 25)):
        i = rng.integers(0, len(c) - 600)
        c[i:i + 400] += rng.normal(0, 1, 400) * np.exp(-np.arange(400) / 60) * rng.uniform(.2, 1)
    c = band(c, 900, 7000) * env(len(c), .3, .4) * .10
    c += band(rng.normal(0, 1, len(c)), 60, 400) * .05 * env(len(c), .3, .4)
    put(c, T(a), 1, rng.uniform(-.4, .4))

# ------------------------------------------------------------------ score
# opening: lonely piano
for t0, m in [(0.15, 69), (0.9, 72), (1.7, 76), (2.5, 74)]:
    put(reverb(note(hz(m), 2.5, .16)), t0, 1, (m - 72) / 20)

# minor pad under the inventory section
chords = [(T(3.8), [45, 52, 57, 60]), (T(8), [41, 48, 53, 57]), (T(13), [48, 55, 60, 64]),
          (T(17), [43, 50, 55, 59]), (T(21), [40, 47, 52, 55])]
for k, (t0, ns) in enumerate(chords):
    d = (chords[k + 1][0] if k + 1 < len(chords) else T(25)) - t0 + 1.2
    pad = sum(note(hz(n), d, 1, "pad") for n in ns)
    put(band(pad, 80, 900) * .05, t0, 1, 0)
# sparse piano motif
motif = [(4.6, 76), (5.6, 74), (6.6, 72), (9.0, 72), (10.0, 71), (11.0, 69), (14.0, 76), (15.2, 79),
         (18.0, 74), (19.5, 71), (22.0, 76), (23.2, 72), (24.2, 71)]
for t0, m in motif:
    put(reverb(note(hz(m), 2.8, .10)), T(t0), 1, (m - 72) / 25)

# 我們一起撐 — warm major lift
for t0, ns in [(T(25), [41, 53, 57, 60, 65]), (T(27), [48, 55, 60, 64, 67])]:
    pad = sum(note(hz(n), T(2) + 1.0, 1, "pad") for n in ns)
    put(band(pad, 80, 1400) * .055, t0, 1)
for t0, m in [(25.2, 72), (25.8, 77), (26.4, 76), (27.0, 72), (27.7, 79), (28.4, 76)]:
    put(reverb(note(hz(m), 3.0, .14), 2.6, .4), T(t0), 1, (m - 72) / 25)

# night: music drops out, high eerie tone creeps in
et = tvec(T(32) - T(29.3))
eerie = (np.sin(2 * np.pi * 1318.5 * et) + np.sin(2 * np.pi * 1396.9 * et)) * np.linspace(0, 1, len(et)) ** 2 * .012
put(eerie, T(29.3))

# 門外沒有人 — dissonant sting
st = tvec(4.0)
sting = sum(note(hz(n), 4.0, 1, "pad") for n in [57, 58, 63, 64])
sting = band(sting, 200, 2500) * np.exp(-st * .7) * .06
put(reverb(sting, 3, .5), T(36))

# 如果是你 — heartbeat (matches render.py pulse: every .9s, double beat)
def thump(f=55, d=.35):
    t = tvec(d)
    return np.sin(2 * np.pi * (f + 40 * np.exp(-t * 30)) * t) * np.exp(-t * 14)


for k in range(int((T(42) - T(38)) / .9)):
    t0 = T(38) + k * .9
    put(thump(), t0, .55)
    put(thump(50), t0 + .2, .35)

# outro: resolve on Am(add9) and a low hit
pad = sum(note(hz(n), DUR - T(42), 1, "pad") for n in [45, 52, 57, 59, 64])
put(band(pad, 80, 1100) * .06, T(42))
for t0, m in [(T(42) + .3, 69), (T(42) + 1.1, 71), (T(42) + 1.9, 72), (T(42) + 2.9, 76)]:
    put(reverb(note(hz(m), 2.5, .12)), t0)

# ------------------------------------------------------------------ foley
# lantern ignition
lt = tvec(.6)
put(band(rng.normal(0, 1, len(lt)), 200, 2500) * np.exp(-lt * 7) * np.minimum(1, lt / .04) * .12, .1)

# title slam
bt = tvec(2.5)
boom = np.sin(2 * np.pi * np.cumsum(35 + 70 * np.exp(-bt * 6)) / SR) * np.exp(-bt * 2.2)
boom += band(rng.normal(0, 1, len(bt)), 40, 1800) * np.exp(-bt * 10) * .6
put(reverb(boom * .5, 2.5, .3), T(3))

# radio static that dies with a click
rt = tvec(2.2)
static = band(rng.normal(0, 1, len(rt)), 900, 5000) * (.6 + .4 * np.sin(2 * np.pi * 7 * rt) * np.sin(2 * np.pi * .9 * rt))
static *= env(len(rt), .15, .02) * .05
put(static, T(3.8) + .2, 1, -.5)
put(band(np.r_[np.ones(60), -np.ones(60), np.zeros(600)], 300, 6000) * .25, T(3.8) + 2.4, 1, -.5)

# chalk scratches with the tally marks
for t0 in [8.8, 9.4, 10.0, 10.5, 11.0, 11.5, 12.0]:
    ct = tvec(.22)
    sc = band(rng.normal(0, 1, len(ct)), 2500, 7000) * (np.sin(np.pi * ct / .22) ** 2) \
        * (1 + .6 * np.sin(2 * np.pi * 38 * ct)) * .07
    put(sc, T(t0), 1, .3)

# water drips
for t0 in [13.6, 14.9, 16.1]:
    dt_ = tvec(.12)
    drip = np.sin(2 * np.pi * np.cumsum(600 + 1100 * np.exp(-dt_ * 40)) / SR) * np.exp(-dt_ * 35) * .18
    put(reverb(drip, 1.6, .45), T(t0), 1, -.2)

# hammering the fence
for t0 in [17.7, 18.9, 20.1, 34.05]:
    ht = tvec(.5)
    hit = np.sin(2 * np.pi * 110 * ht) * np.exp(-ht * 18) + band(rng.normal(0, 1, len(ht)), 800, 3500) * np.exp(-ht * 60) * .7
    put(reverb(hit * .35, 1.2, .25), T(t0), 1, .15)

# three knocks — the scariest sound in the film
for k, t0 in enumerate([32.25, 32.85, 33.45]):
    kt = tvec(.6)
    knock = np.sin(2 * np.pi * (75 + 30 * np.exp(-kt * 40)) * kt) * np.exp(-kt * 11)
    knock += band(rng.normal(0, 1, len(kt)), 300, 1500) * np.exp(-kt * 45) * .8
    put(reverb(knock * (.75 + .1 * k), 2.6, .4), T(t0))

# door creak
ct = tvec(1.5)
f = 230 + 70 * np.sin(2 * np.pi * .9 * ct) + 25 * band(rng.normal(0, 1, len(ct)), 0, 12) * 10
saw = (np.cumsum(f) / SR) % 1 * 2 - 1
creak = band(saw * (rng.random(len(ct)) < .35 + .3 * np.sin(2 * np.pi * 3 * ct) ** 2), 400, 3200)
put(reverb(creak * env(len(ct), .1, .4) * .12, 1.8, .35), T(34) + .15, 1, .4)

# ------------------------------------------------------------------ master
mix = np.stack([L, R], 1)
mix *= np.minimum(1, np.arange(N) / (SR * .3))[:, None]
fade = int(SR * 1.2)
mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
mix = np.tanh(mix * 1.6) / np.tanh(1.6)
mix *= .89 / np.abs(mix).max()
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())
print("wrote", sys.argv[1], f"{DUR}s")
