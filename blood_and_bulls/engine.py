"""Renders BLOOD & BULLS episodes: TTS voices, score, SFX, procedural visuals -> mp4."""
import glob
import hashlib
import math
import os
import random
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".cache")
OUT = os.path.join(HERE, "out")
KOKORO = os.environ.get("KOKORO_DIR", "/opt/kk")
W, H = 1080, 1920
HW, HH = 540, 960
FPS = 30
SR = 24000
INTRO = 2.4
OUTRO = 2.4
SERIES = "BLOOD & BULLS"
N_EPS = 20

VOICES = {  # speaker -> (kokoro voice, speed, name chip, chip colour)
    "N": ("bm_george", 0.93, None, None),
    "D": ("am_onyx", 0.97, "DANTE", (240, 180, 60)),
    "R": ("af_nicole", 1.0, "RHEA", (90, 200, 255)),
    "K": ("am_fenrir", 0.9, "KANE", (235, 70, 80)),
    "L": ("af_sky", 1.05, "LINA", (255, 140, 200)),
    "M": ("am_adam", 1.0, "MO", (130, 230, 160)),
}

MOODS = {  # top colour, bottom colour, accent
    "tense": ((60, 8, 14), (8, 4, 8), (255, 70, 60)),
    "cold": ((8, 28, 52), (3, 6, 14), (90, 190, 255)),
    "warm": ((72, 30, 22), (14, 6, 10), (255, 170, 80)),
    "dark": ((26, 14, 40), (3, 3, 8), (170, 110, 255)),
}


# ------------------------------------------------------------------ fonts
def _font(size, bold=True):
    names = ["Inter-ExtraBold.otf", "Inter-Black.otf", "Inter-Bold.otf"] if bold else ["Inter-Medium.otf", "Inter-Regular.otf"]
    for n in names:
        for p in glob.glob(f"/usr/share/fonts/**/{n}", recursive=True):
            return ImageFont.truetype(p, size)
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)


_FC = {}


def font(size, bold=True):
    k = (size, bold)
    if k not in _FC:
        _FC[k] = _font(size, bold)
    return _FC[k]


# ------------------------------------------------------------------ TTS
_kokoro = None


def tts(spk, text):
    os.makedirs(CACHE, exist_ok=True)
    voice, speed, _, _ = VOICES[spk]
    key = hashlib.md5(f"{voice}|{speed}|{text}".encode()).hexdigest()
    p = os.path.join(CACHE, key + ".npy")
    if os.path.exists(p):
        return np.load(p)
    global _kokoro
    if _kokoro is None:
        from kokoro_onnx import Kokoro
        _kokoro = Kokoro(os.path.join(KOKORO, "kokoro-v1.0.onnx"), os.path.join(KOKORO, "voices-v1.0.bin"))
    s, sr = _kokoro.create(text, voice=voice, speed=speed, lang="en-us")
    assert sr == SR
    s = s.astype(np.float32)
    nz = np.where(np.abs(s) > 0.01)[0]
    if len(nz):
        s = s[max(0, nz[0] - 800): nz[-1] + 2400]
    s = s / max(1e-6, np.abs(s).max()) * 0.9
    np.save(p, s)
    return s


# ------------------------------------------------------------------ SFX
def _env(n, decay):
    return np.exp(-np.arange(n) / SR * decay)


def sfx_wave(kind):
    rng = np.random.default_rng(7)
    if kind == "hit":
        n = int(SR * 0.6)
        t = np.arange(n) / SR
        f = 150 * np.exp(-t * 14) + 38
        body = np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 9)
        nz = rng.standard_normal(n) * _env(n, 38) * 0.6
        return (body + nz) * 0.9
    if kind == "bell":
        n = int(SR * 2.2)
        t = np.arange(n) / SR
        w = sum(a * np.sin(2 * np.pi * f * t) for f, a in [(880, 1), (1318, .6), (2217, .35), (3520, .2)])
        return w * _env(n, 2.2) * 0.35
    if kind == "whoosh":
        n = int(SR * 0.7)
        nz = rng.standard_normal(n)
        k = np.convolve(nz, np.ones(40) / 40, mode="same")
        env = np.sin(np.linspace(0, np.pi, n)) ** 2
        return (k * 3.5 + np.diff(nz, prepend=0) * 0.15) * env * 0.5
    if kind == "beep":
        n = int(SR * 0.9)
        t = np.arange(n) / SR
        w = np.zeros(n)
        for st in (0.0, 0.3, 0.6):
            m = (t >= st) & (t < st + 0.12)
            w[m] = np.sin(2 * np.pi * 1000 * t[m]) * 0.35
        return w
    if kind == "crash":
        n = int(SR * 1.6)
        t = np.arange(n) / SR
        f = 420 * np.exp(-t * 1.5) + 40
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 2.2)
        nz = rng.standard_normal(n) * _env(n, 4) * 0.5
        return (s * 0.7 + nz) * 0.6
    if kind == "cash":
        n = int(SR * 1.0)
        t = np.arange(n) / SR
        w = np.sin(2 * np.pi * 1760 * t) * _env(n, 7) + np.sin(2 * np.pi * 2349 * np.maximum(t - 0.09, 0)) * (t > .09) * _env(n, 6)
        return w * 0.3
    if kind == "heart":
        n = int(SR * 1.2)
        t = np.arange(n) / SR
        w = np.zeros(n)
        for st, a in [(0, 1), (0.22, 0.7), (0.8, 1), (1.02, 0.7)]:
            if st < 1.2:
                m = t >= st
                w[m] += np.sin(2 * np.pi * 55 * (t[m] - st)) * _env(m.sum(), 18) * a
        return w * 0.8
    if kind == "tick":
        n = int(SR * 0.4)
        w = np.zeros(n)
        for st in (0, 0.12, 0.24):
            i = int(st * SR)
            m = int(SR * 0.02)
            w[i:i + m] = rng.standard_normal(m) * np.linspace(1, 0, m) * 0.3
        return w
    return np.zeros(1)


# ------------------------------------------------------------------ music
def make_music(total, style_at):
    """style_at(t) -> 'fight'|'tense'|'soft'."""
    n = int(total * SR)
    t = np.arange(n) / SR
    bpm = 98
    beat = 60 / bpm
    out = np.zeros(n, dtype=np.float32)
    rng = np.random.default_rng(3)

    chords = [(110.0, 130.8, 164.8), (87.3, 110.0, 130.8), (130.8, 164.8, 196.0), (98.0, 123.5, 146.8)]
    roots = [55.0, 43.65, 65.4, 49.0]
    bar = beat * 4
    bar_idx = (t // bar).astype(int) % 4

    # smooth style gates
    def gate(names):
        grid = np.arange(0, total + 1, 0.1)
        g = np.array([1.0 if style_at(x) in names else 0.0 for x in grid], dtype=np.float32)
        g = np.convolve(g, np.ones(8) / 8, mode="same")
        return np.interp(t, grid, g).astype(np.float32)

    g_fight, g_tense, g_soft = gate({"fight"}), gate({"tense"}), gate({"soft"})

    pad = np.zeros(n, dtype=np.float32)
    for i in range(4):
        m = bar_idx == i
        for f in chords[i]:
            for d in (-0.4, 0.4):
                pad[m] += np.sin(2 * np.pi * (f + d) * t[m]) * 0.035
    pad *= 0.6 + 0.4 * np.sin(2 * np.pi * t / (bar * 2)) ** 2
    out += pad

    bass = np.zeros(n, dtype=np.float32)
    for i in range(4):
        m = bar_idx == i
        bass[m] = np.sin(2 * np.pi * roots[i] * t[m]) * 0.22
    ph = (t % beat) / beat
    bass *= 0.55 + 0.45 * np.exp(-ph * 3)
    out += bass * (0.5 + 0.5 * (g_fight + g_tense))

    def put(arr, at, wave, gain):
        i = int(at * SR)
        if i >= n:
            return
        e = min(n, i + len(wave))
        arr[i:e] += wave[: e - i] * gain

    kt = np.arange(int(SR * 0.3)) / SR
    kick = np.sin(2 * np.pi * np.cumsum(115 * np.exp(-kt * 22) + 42) / SR) * np.exp(-kt * 11)
    snt = int(SR * 0.16)
    snare = rng.standard_normal(snt) * np.exp(-np.arange(snt) / SR * 26) * 0.5
    hht = int(SR * 0.05)
    hat = np.diff(rng.standard_normal(hht + 1)) * np.exp(-np.arange(hht) / SR * 80) * 0.5
    pl = np.arange(int(SR * 0.5)) / SR

    drums = np.zeros(n, dtype=np.float32)
    plucks = np.zeros(n, dtype=np.float32)
    nb = int(total / beat) + 1
    for b in range(nb):
        tb = b * beat
        put(drums, tb, kick, 0.55)
        if b % 2 == 1:
            put(drums, tb, snare, 0.5)
        put(drums, tb, hat, 0.35)
        put(drums, tb + beat / 2, hat, 0.25)
        chord = chords[(b // 4) % 4]
        note = chord[[0, 1, 2, 1, 2, 1, 0, 2][b % 8]] * 2
        put(plucks, tb, np.sin(2 * np.pi * note * pl) * np.exp(-pl * 6) * 0.9, 0.12)
        put(plucks, tb + beat / 2, np.sin(2 * np.pi * note * 2 * pl) * np.exp(-pl * 8), 0.05)
    out += drums * (g_fight * 1.0 + g_tense * 0.45)
    out += plucks * (g_soft * 1.0 + g_tense * 0.45 + g_fight * 0.2)
    out += pad * g_soft * 0.6
    return out


# ------------------------------------------------------------------ timeline + audio
def build_timeline(ep):
    cur = INTRO
    tl = []
    bounds = []
    for si, sc in enumerate(ep["scenes"]):
        s0 = cur if si else 0.0
        for ln in sc["lines"]:
            spk, text = ln[0], ln[1]
            sfx = ln[2] if len(ln) > 2 else None
            voice = tts(spk, text)
            dur = len(voice) / SR
            sfx_t = None
            if sfx:
                sfx_t = cur
                cur += 0.5
            tl.append(dict(spk=spk, text=text, start=cur, end=cur + dur, sfx=sfx, sfx_t=sfx_t, scene=si, voice=voice))
            cur += dur + (0.32 if spk == "N" else 0.22)
        bounds.append(s0)
    total = cur + OUTRO - 0.2
    return tl, bounds, total


def build_audio(ep, tl, total):
    n = int((total + 0.5) * SR)
    voice = np.zeros(n, dtype=np.float32)
    fx = np.zeros(n, dtype=np.float32)

    def add(arr, at, w, g=1.0):
        i = int(at * SR)
        e = min(n, i + len(w))
        arr[i:e] += (w[: e - i] * g).astype(np.float32)

    add(fx, 0.15, sfx_wave("whoosh"), 0.9)
    for ln in tl:
        add(voice, ln["start"], ln["voice"], 1.0)
        if ln["sfx"]:
            add(fx, ln["sfx_t"], sfx_wave(ln["sfx"]), 0.9)
    add(fx, total - OUTRO + 0.2, sfx_wave("bell"), 0.5)

    starts = [(b, ep["scenes"][i]["music"]) for i, b in enumerate(_bounds_of(tl, ep))]

    def style_at(x):
        s = starts[0][1]
        for b, m in starts:
            if x >= b:
                s = m
        return s

    music = make_music(total + 0.5, style_at)[:n]
    env = np.convolve(np.abs(voice), np.ones(int(SR * 0.25)) / int(SR * 0.25), mode="same")
    duck = 1.0 - 0.6 * np.clip(env / 0.12, 0, 1)
    duck = np.convolve(duck, np.ones(int(SR * 0.3)) / int(SR * 0.3), mode="same")
    mix = voice * 1.0 + fx * 0.8 + music * 0.9 * duck
    fade = np.ones(n, dtype=np.float32)
    k = int(SR * 0.8)
    fade[-k:] = np.linspace(1, 0, k)
    mix = np.tanh(mix * 1.1) * 0.95 * fade
    return mix.astype(np.float32)


def _bounds_of(tl, ep):
    out = []
    for si in range(len(ep["scenes"])):
        first = next(l for l in tl if l["scene"] == si)
        out.append(0.0 if si == 0 else first["start"] - (0.55 if first["sfx"] else 0.05))
    return out


# ------------------------------------------------------------------ visuals
_grad = {}


def grad(mood):
    if mood not in _grad:
        top, bot, _ = MOODS[mood]
        y = np.linspace(0, 1, HH)[:, None, None]
        _grad[mood] = (np.array(top) * (1 - y) + np.array(bot) * y) * np.ones((1, HW, 1))
    return _grad[mood].astype(np.float32)


_vig = None


def vignette():
    global _vig
    if _vig is None:
        yy, xx = np.mgrid[0:HH, 0:HW]
        d = np.sqrt(((xx - HW / 2) / (HW / 2)) ** 2 + ((yy - HH / 2) / (HH / 2)) ** 2)
        v = np.clip(1.15 - 0.55 * d ** 1.6, 0.25, 1)
        bottom = np.clip((yy - HH * 0.58) / (HH * 0.42), 0, 1)
        _vig = (v * (1 - 0.55 * bottom))[:, :, None].astype(np.float32)
    return _vig


_grain = None


def grain(i):
    global _grain
    if _grain is None:
        r = np.random.default_rng(1)
        _grain = [r.normal(0, 7, (HH, HW, 1)).astype(np.float32) for _ in range(6)]
    return _grain[i % 6]


class Scene:
    def __init__(self, sc, seed):
        self.sc = sc
        self.rng = random.Random(seed)
        self.mood = sc["mood"]
        self.accent = MOODS[self.mood][2]
        self.motif = sc["motif"]
        r = self.rng
        # chart series
        up = sc.get("up", None)
        drift = 0.0 if up is None else (0.5 if up else -0.5)
        p, ser = 100.0, []
        for _ in range(400):
            o = p
            p = max(5, p + r.gauss(drift, 2.6))
            hi = max(o, p) + abs(r.gauss(0, 1.3))
            lo = min(o, p) - abs(r.gauss(0, 1.3))
            ser.append((o, p, hi, lo))
        self.series = ser
        self.stars = [(r.random() * HW, r.random() * 420, r.random() * 6.28) for _ in range(60)]
        self.dust = [[r.random() * HW, r.random() * HH, r.random() * 20 + 8, r.random() * 3 + 1] for _ in range(50)]
        self.base = self._build_base()

    def _build_base(self):
        m = self.motif
        base = grad(self.mood).copy()
        if m == "ring":
            yy, xx = np.mgrid[0:HH, 0:HW]
            cone = np.clip(1 - np.abs(xx - HW / 2) / (60 + yy * 0.55), 0, 1) ** 1.5 * np.clip(1 - yy / 900, 0, 1)
            base += cone[:, :, None] * np.array([150, 130, 100]) * 0.55
            for cx in (HW * 0.22, HW * 0.78):
                c2 = np.clip(1 - np.abs(xx - cx) / (35 + yy * 0.3), 0, 1) ** 2 * np.clip(1 - yy / 700, 0, 1)
                base += c2[:, :, None] * np.array(self.accent) * 0.18
        elif m == "skyline":
            img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))
            d = ImageDraw.Draw(img)
            rr = random.Random(5)
            for layer, (colr, hmin, hmax, wmin, wmax, lit) in enumerate([((18, 20, 36), 380, 640, 40, 90, .12), ((8, 9, 18), 260, 520, 50, 110, .3)]):
                x = -20
                while x < HW + 20:
                    w = rr.randint(wmin, wmax)
                    h = rr.randint(hmin, hmax)
                    top = HH - 130 - h
                    d.rectangle([x, top, x + w, HH], fill=colr)
                    for wy in range(top + 14, HH - 150, 22):
                        for wx in range(x + 8, x + w - 8, 16):
                            if rr.random() < lit:
                                d.rectangle([wx, wy, wx + 6, wy + 9], fill=(255, 205, 120) if rr.random() < .7 else (150, 210, 255))
                    x += w + rr.randint(2, 10)
            d.rectangle([0, HH - 150, HW, HH], fill=(4, 4, 8))
            d.rectangle([0, HH - 152, HW, HH - 146], fill=(30, 30, 44))
            base = np.asarray(img).astype(np.float32)
        return base

    # ---- per-frame draw (half res) -> float32 array
    def frame(self, t, hit):
        m = self.motif
        if m == "chart":
            return self._chart(t)
        if m == "ring":
            return self._ring(t, hit)
        if m == "skyline":
            return self._skyline(t)
        return self._pulse(t)

    def _arr(self, img):
        return np.asarray(img).astype(np.float32)

    def _chart(self, t):
        img = Image.fromarray(np.clip(self.base, 0, 255).astype(np.uint8))
        d = ImageDraw.Draw(img, "RGBA")
        for gy in range(120, HH, 120):
            d.line([0, gy, HW, gy], fill=(255, 255, 255, 18), width=1)
        pitch = 22
        speed = 2.2
        pos = t * speed
        i0 = int(pos)
        frac = pos - i0
        n = HW // pitch + 3
        vis = self.series[i0 + 20: i0 + 20 + n]
        lo = min(c[3] for c in vis)
        hi = max(c[2] for c in vis)
        top, bot = 230, 700

        def Y(v):
            return bot - (v - lo) / (hi - lo + 1e-6) * (bot - top)

        pts = []
        for k, (o, c, h, l) in enumerate(vis):
            x = k * pitch - frac * pitch
            col = (60, 225, 140) if c >= o else (245, 70, 85)
            d.line([x + 7, Y(h), x + 7, Y(l)], fill=col + (255,), width=2)
            y1, y2 = sorted((Y(o), Y(c)))
            d.rectangle([x + 1, y1, x + 13, max(y2, y1 + 2)], fill=col + (255,))
            pts.append((x + 7, Y(c)))
        d.line(pts, fill=self.accent + (150,), width=3)
        lx, ly = pts[-3]
        d.ellipse([lx - 6, ly - 6, lx + 6, ly + 6], fill=(255, 255, 255, 255))
        for r in (14, 22):
            d.ellipse([lx - r, ly - r, lx + r, ly + r], outline=self.accent + (int(120 - r * 3),), width=2)
        d.line([0, ly, HW, ly], fill=(255, 255, 255, 40), width=1)
        chg = (vis[-3][1] / self.series[20 + i0 - 0][0] - 1) * 100 if False else (vis[-3][1] - vis[0][0]) / vis[0][0] * 100
        col = (60, 225, 140) if chg >= 0 else (245, 70, 85)
        d.text((24, 150), "KNCP", font=font(26), fill=(255, 255, 255, 140))
        d.text((24, 182), f"{vis[-3][1]:6.2f}  {chg:+.1f}%", font=font(30), fill=col + (230,))
        return self._arr(img)

    def _fighter(self, d, cx, gy, face, punch, bob, rim, glove):
        def L(pts, w, c):
            d.line(pts, fill=c, width=w, joint="curve")

        hip = (cx, gy - 95 + bob)
        sh = (cx + face * 6, gy - 190 + bob)
        head = (cx + face * 12, gy - 224 + bob)
        kneeF = (cx + face * 28, gy - 48)
        kneeB = (cx - face * 14, gy - 48)
        footF = (cx + face * 40, gy)
        footB = (cx - face * 32, gy)
        gl_x = cx + face * (46 + 84 * punch)
        gl_y = gy - 196 + bob - 4 * punch
        elb = (cx + face * (26 + 20 * punch), gy - 160 + bob)
        gr = (cx + face * 38, gy - 222 + bob)
        elb2 = (cx + face * 12, gy - 160 + bob)
        for w, c in ((20, rim), (14, (12, 12, 18))):
            L([footB, kneeB, hip], w, c)
            L([footF, kneeF, hip], w, c)
            L([hip, sh], w + 8, c)
            L([sh, elb2, gr], w - 2, c)
            L([sh, elb, (gl_x, gl_y)], w - 2, c)
            r = 17 if w == 14 else 20
            d.ellipse([head[0] - 20 - (w == 20), head[1] - 20 - (w == 20), head[0] + 20 + (w == 20), head[1] + 20 + (w == 20)], fill=c)
        for g in ((gl_x, gl_y), gr):
            d.ellipse([g[0] - 15, g[1] - 15, g[0] + 15, g[1] + 15], fill=glove)

    def _ring(self, t, hit):
        img = Image.fromarray(np.clip(self.base, 0, 255).astype(np.uint8))
        d = ImageDraw.Draw(img, "RGBA")
        # crowd
        rr = random.Random(11)
        for i in range(34):
            x = i * 17 + rr.randint(-4, 4)
            y = 870 + rr.randint(-14, 20) + math.sin(t * 3 + i) * 3 * (1 + hit)
            d.ellipse([x - 14, y - 14, x + 14, y + 14], fill=(5, 4, 8, 255))
            d.rectangle([x - 20, y + 10, x + 20, HH], fill=(5, 4, 8, 255))
        # canvas
        d.polygon([(30, 700), (HW - 30, 700), (HW + 40, 800), (-40, 800)], fill=(26, 22, 30, 255))
        d.line([30, 700, HW - 30, 700], fill=(255, 255, 255, 50), width=2)
        # ropes
        for k, y in enumerate((520, 585, 650)):
            sag = 6 + math.sin(t * 2 + k) * 2
            pts = [(60 - 10 * k * 0, y), (HW / 2, y + sag), (HW - 60, y)]
            d.line(pts, fill=(210, 40, 50, 230), width=7)
        for x in (50, HW - 50):
            d.rectangle([x - 8, 470, x + 8, 710], fill=(35, 35, 45, 255))
        # fighters
        cyc = (t * 1.25) % 1.0
        pa = max(0, math.sin(cyc * 2 * math.pi * 2)) ** 3
        pb = max(0, math.sin((cyc + 0.5) * 2 * math.pi * 2)) ** 3 * 0.8
        self._fighter(d, 175 + 26 * pa, 700, 1, pa, math.sin(t * 6) * 4, (240, 180, 60, 255), (240, 180, 60, 255))
        self._fighter(d, 365 - 26 * pb - 10 * hit, 700, -1, pb, math.sin(t * 6 + 1) * 4, (235, 70, 80, 255), (235, 70, 80, 255))
        # dust
        for p in self.dust:
            p[1] -= p[2] * 0.016
            p[0] += math.sin(t + p[3]) * 0.3
            if p[1] < 0:
                p[1] = HH
            d.ellipse([p[0], p[1], p[0] + p[3], p[1] + p[3]], fill=(255, 235, 200, 90))
        return self._arr(img)

    def _skyline(self, t):
        img = Image.fromarray(np.clip(self.base, 0, 255).astype(np.uint8))
        d = ImageDraw.Draw(img, "RGBA")
        for x, y, ph in self.stars:
            a = int(80 + 90 * math.sin(t * 2 + ph))
            d.ellipse([x, y, x + 2, y + 2], fill=(255, 255, 255, max(10, a)))
        mx, my = 400, 190
        for r, a in ((90, 14), (62, 24), (44, 255)):
            d.ellipse([mx - r, my - r, mx + r, my + r], fill=(255, 245, 215, a))
        if self.sc.get("couple"):
            self._couple(d, t)
        else:
            self._lone(d, t)
        return self._arr(img)

    def _person(self, d, x, base, h, col, lean=0):
        d.ellipse([x - 16 + lean, base - h - 16, x + 16 + lean, base - h + 16], fill=col)
        d.polygon([(x - 22 + lean * .6, base - h + 24), (x + 22 + lean * .6, base - h + 24), (x + 28, base), (x - 28, base)], fill=col)

    def _lone(self, d, t):
        self._person(d, 270, HH - 150, 240, (3, 3, 6, 255))

    def _couple(self, d, t):
        self._person(d, 245, HH - 150, 250, (3, 3, 6, 255), lean=10)
        self._person(d, 292, HH - 150, 240, (3, 3, 6, 255), lean=-10)
        for k in range(5):
            ph = (t * 0.35 + k * 0.2) % 1.0
            x = 270 + math.sin(ph * 9 + k) * 30 + k * 6
            y = HH - 460 - ph * 380
            a = int(255 * (1 - ph))
            s = 7 + k
            d.polygon([(x, y + s), (x - s, y - 2), (x - s / 2, y - s), (x, y - s / 3), (x + s / 2, y - s), (x + s, y - 2)], fill=(255, 90, 140, a))

    def _pulse(self, t):
        img = Image.fromarray(np.clip(self.base, 0, 255).astype(np.uint8))
        d = ImageDraw.Draw(img, "RGBA")
        cx, cy = HW // 2, 420
        beat = (t % 0.9) / 0.9
        for k in range(4):
            ph = (t * 0.55 + k * 0.25) % 1.0
            r = 40 + ph * 320
            d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=self.accent + (int(150 * (1 - ph)),), width=3)
        s = 70 + 22 * math.exp(-beat * 6)
        d.polygon([(cx, cy + s), (cx - s * 1.25, cy - s * .15), (cx - s * .62, cy - s), (cx, cy - s * .4), (cx + s * .62, cy - s), (cx + s * 1.25, cy - s * .15)], fill=self.accent + (230,))

        def ecg(u):
            u %= 0.9
            if 0.30 < u < 0.34:
                return -10 * (u - .30) / .04
            if 0.34 <= u < 0.40:
                return -10 + 120 * (u - .34) / .06
            if 0.40 <= u < 0.47:
                return 110 - 150 * (u - .40) / .07
            if 0.47 <= u < 0.52:
                return -40 + 40 * (u - .47) / .05
            if 0.65 < u < 0.78:
                return -22 * math.sin((u - .65) / .13 * math.pi)
            return 0

        y0 = 700
        pts = []
        for x in range(0, HW, 3):
            u = t - (HW - x) / 190.0
            pts.append((x, y0 - ecg(u)))
        d.line(pts, fill=(255, 255, 255, 40), width=9)
        d.line(pts, fill=self.accent + (255,), width=3)
        d.ellipse([HW - 10, pts[-1][1] - 5, HW, pts[-1][1] + 5], fill=(255, 255, 255, 255))
        return self._arr(img)


# ------------------------------------------------------------------ captions
def groups(text):
    words = text.split()
    out, cur, ln = [], [], 0
    for w in words:
        if cur and (ln + len(w) > 20 or len(cur) >= 4):
            out.append(cur)
            cur, ln = [], 0
        cur.append(w)
        ln += len(w) + 1
    if cur:
        out.append(cur)
    return out


def caption_state(ln, t):
    words = ln["text"].split()
    wts = np.array([len(w) + 2.5 for w in words], dtype=float)
    dur = ln["end"] - ln["start"]
    ends = ln["start"] + np.cumsum(wts) / wts.sum() * dur
    idx = int(np.searchsorted(ends, t))
    idx = min(idx, len(words) - 1)
    g = groups(ln["text"])
    c = 0
    for gi, grp in enumerate(g):
        if idx < c + len(grp):
            return grp, idx - c
        c += len(grp)
    return g[-1], len(g[-1]) - 1


def draw_text_center(d, xy, text, f, fill, stroke=7):
    d.text(xy, text, font=f, fill=fill, anchor="mm", stroke_width=stroke, stroke_fill=(0, 0, 0))


def draw_caption(d, ln, t):
    grp, ci = caption_state(ln, t)
    size = 92
    f = font(size)
    words = [w.upper() for w in grp]
    total = d.textlength(" ".join(words), font=f)
    while total > 960 and size > 52:
        size -= 4
        f = font(size)
        total = d.textlength(" ".join(words), font=f)
    x = W / 2 - total / 2
    y = 1490
    sp = d.textlength(" ", font=f)
    for i, w in enumerate(words):
        wl = d.textlength(w, font=f)
        col = (255, 205, 70) if i == ci else (255, 255, 255)
        d.text((x, y), w, font=f, fill=col, anchor="lm", stroke_width=8, stroke_fill=(0, 0, 0))
        x += wl + sp
    _, _, name, colr = VOICES[ln["spk"]]
    if name:
        f2 = font(40)
        tw = d.textlength(name, font=f2) + 56
        d.rounded_rectangle([W / 2 - tw / 2, 1360, W / 2 + tw / 2, 1418], radius=29, fill=colr)
        d.text((W / 2, 1390), name, font=f2, fill=(10, 10, 14), anchor="mm")


def draw_chrome(d, ep_no, t, total, accent):
    d.text((W / 2, 236), SERIES, font=font(34), fill=(255, 255, 255, 235), anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))
    gap = 38
    x0 = W / 2 - gap * (N_EPS - 1) / 2
    for i in range(N_EPS):
        x = x0 + i * gap
        if i + 1 == ep_no:
            d.ellipse([x - 9, 290, x + 9, 308], fill=(255, 205, 70))
        else:
            d.ellipse([x - 5, 294, x + 5, 304], fill=(255, 255, 255) if i + 1 < ep_no else (110, 110, 120))
    f = font(30)
    d.text((W / 2, 350), f"EPISODE {ep_no} OF {N_EPS}", font=f, fill=(255, 205, 70), anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0))


def draw_title(d, ep_no, title, alpha):
    a = int(255 * alpha)
    for txt, y, sz, col in (("BLOOD", 760, 190, (255, 255, 255)), ("&", 930, 120, (255, 205, 70)), ("BULLS", 1090, 190, (235, 70, 80))):
        d.text((W / 2, y), txt, font=font(sz), fill=col, anchor="mm", stroke_width=8, stroke_fill=(0, 0, 0))
    d.text((W / 2, 1290), f"EPISODE {ep_no}", font=font(48), fill=(255, 205, 70), anchor="mm", stroke_width=4, stroke_fill=(0, 0, 0))
    d.text((W / 2, 1370), f"“{title}”", font=font(62), fill=(255, 255, 255), anchor="mm", stroke_width=5, stroke_fill=(0, 0, 0))


def draw_outro(d, ep_no, nxt_title):
    if ep_no < N_EPS:
        d.text((W / 2, 880), "TO BE CONTINUED", font=font(92), fill=(255, 255, 255), anchor="mm", stroke_width=8, stroke_fill=(0, 0, 0))
        d.text((W / 2, 1010), f"EPISODE {ep_no + 1}: “{nxt_title}”", font=font(46), fill=(255, 205, 70), anchor="mm", stroke_width=5, stroke_fill=(0, 0, 0))
        d.text((W / 2, 1110), "FOLLOW FOR PART " + str(ep_no + 1), font=font(52), fill=(255, 255, 255), anchor="mm", stroke_width=5, stroke_fill=(0, 0, 0))
    else:
        d.text((W / 2, 880), "THE END", font=font(120), fill=(255, 255, 255), anchor="mm", stroke_width=8, stroke_fill=(0, 0, 0))
        d.text((W / 2, 1030), "SEASON ONE", font=font(54), fill=(255, 205, 70), anchor="mm", stroke_width=5, stroke_fill=(0, 0, 0))
        d.text((W / 2, 1130), "FOLLOW FOR SEASON TWO", font=font(48), fill=(255, 255, 255), anchor="mm", stroke_width=5, stroke_fill=(0, 0, 0))


# ------------------------------------------------------------------ render
def render_episode(ep_no, episodes, limit=None):
    os.makedirs(OUT, exist_ok=True)
    ep = episodes[ep_no - 1]
    tl, bounds, total = build_timeline(ep)
    audio = build_audio(ep, tl, total)
    wav = os.path.join(CACHE, f"ep{ep_no:02d}.wav")
    import soundfile as sf
    sf.write(wav, audio, SR)
    scenes = [Scene(sc, ep_no * 100 + i) for i, sc in enumerate(ep["scenes"])]
    events = [(l["sfx_t"], l["sfx"]) for l in tl if l["sfx"] in ("hit", "bell", "crash")]
    nxt = episodes[ep_no]["title"] if ep_no < len(episodes) else ""
    out = os.path.join(OUT, f"BloodAndBulls_Ep{ep_no:02d}_{ep['title'].replace(' ', '')}.mp4")
    nframes = int(total * FPS)
    if limit:
        nframes = min(nframes, limit)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", wav, "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p", "-threads", "2",
           "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-t", f"{nframes / FPS:.3f}", "-movflags", "+faststart", out]
    pr = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    vg = vignette()
    for fi in range(nframes):
        t = fi / FPS
        si = 0
        for i, b in enumerate(bounds):
            if t >= b:
                si = i
        st = t - bounds[si]
        hit = 0.0
        shake = 0.0
        for et, kind in events:
            if et is not None and t >= et:
                dt = t - et
                hit = max(hit, math.exp(-dt * 7))
                shake = max(shake, math.exp(-dt * 8))
        sc = scenes[si]
        arr = sc.frame(st + si * 0.0, hit)
        arr = arr * vg
        arr += grain(fi)
        # fade in per scene
        fadein = min(1.0, st / 0.28) if si else min(1.0, t / 0.5)
        arr *= (0.25 + 0.75 * fadein)
        if hit > 0.01:
            arr += hit * 70
        img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
        scale = 1.04 + 0.07 * min(1, st / 12)
        cw, ch = HW / scale, HH / scale
        ox = (HW - cw) / 2 + math.sin(t * 40) * 8 * shake
        oy = (HH - ch) / 2 + math.cos(t * 47) * 8 * shake
        ox = min(max(ox, 0.0), HW - cw)
        oy = min(max(oy, 0.0), HH - ch)
        img = img.resize((W, H), Image.BILINEAR, box=(ox, oy, ox + cw, oy + ch))
        # overlays
        if t < INTRO or t > total - OUTRO:
            dark = Image.new("RGB", (W, H), (0, 0, 0))
            if t < INTRO:
                a = 0.62 if t < INTRO - 0.4 else 0.62 * (INTRO - t) / 0.4
            else:
                a = min(0.7, (t - (total - OUTRO)) / 0.3 * 0.7)
            img = Image.blend(img, dark, a)
        d = ImageDraw.Draw(img, "RGBA")
        if t < INTRO:
            draw_title(d, ep_no, ep["title"], 1)
        else:
            draw_chrome(d, ep_no, t, total, sc.accent)
            if t > total - OUTRO:
                draw_outro(d, ep_no, nxt)
            else:
                cur = None
                for l in tl:
                    if l["start"] - 0.05 <= t < l["end"] + 0.25:
                        cur = l
                if cur:
                    draw_caption(d, cur, min(t, cur["end"] - 0.01))
        try:
            pr.stdin.write(img.tobytes())
        except BrokenPipeError:
            break
    pr.stdin.close()
    pr.wait()
    return out, total
