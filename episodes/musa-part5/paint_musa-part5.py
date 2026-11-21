"""Musa Part 5, illustrated: Facing Pharaoh. No people drawn; Musa (AS) and Harun (AS) are glowing lights,
Pharaoh is never shown (only his palace and an empty throne).
  python3 paint_musa-part5.py --probe 2,7,...      python3 paint_musa-part5.py --out out/paint.mp4
"""
import argparse, json, math, pathlib, subprocess, sys, time
import numpy as np
import skia

ROOT = pathlib.Path(__file__).parent
sys.path.insert(0, str(ROOT.parents[1] / "engine" / "core"))
import paint as K
from paint import P, lin, radial, text, light, motes, stars, star_orn, cam, clamp, ease, W, H, FPS, GOLD, CREAM, TF_COND, TF_SANS

TIM = json.loads((ROOT / "audio/timing.json").read_text())
SEG = TIM["segments"]; DUR = TIM["total_duration"]
L = {s["id"]: s["start"] for s in SEG}; E = {s["id"]: s["end"] for s in SEG}


def wt(i, word):
    s = next(x for x in SEG if x["id"] == i)
    ws = s["vo"].split(); tot = sum(len(w) for w in ws); acc = 0
    for w in ws:
        if w.lower().strip(".,:!?'\"").startswith(word.lower()):
            return s["start"] + (s["end"] - s["start"]) * acc / tot
        acc += len(w)
    return s["start"]


B = [0.0, L[3] - 0.15, L[5] - 0.15, L[6] - 0.15, L[8] - 0.15, L[9] - 0.15, L[10] - 0.15, L[12] - 0.15, DUR]
XF = 0.45
lab = K.label


# ------------------------------------------------------------- pieces
def staff(c, x, y, h, ang=0, rgb=(110, 74, 46), a=1.0):
    c.save(); c.translate(x, y); c.rotate(ang)
    p = skia.Path(); p.moveTo(0, 0); p.lineTo(6, -h); p.quadTo(44, -h - 44, 52, -h + 10)
    c.drawPath(p, P(rgb, a, stroke=12)); c.restore()


def serpent(c, x, y, length, t, a=1.0, prog=1.0):
    pts = []; n = 40
    for k in range(n):
        f = k / (n - 1)
        pts.append((x - length / 2 + f * length * prog, y + math.sin(f * 9 - t * 7) * 46 * (0.4 + 0.6 * f)))
    for k in range(n - 1):
        w = 30 * (1 - 0.75 * (k / n))
        cl = (186, 146, 70) if k % 4 < 2 else (150, 112, 52)
        c.drawLine(*pts[k], *pts[k + 1], P(cl, a, stroke=w, cap=skia.Paint.kRound_Cap))
    hx, hy = pts[-1]
    c.drawOval(skia.Rect.MakeLTRB(hx - 10, hy - 26, hx + 46, hy + 22), P((170, 128, 58), a))
    c.drawCircle(hx + 26, hy - 8, 5, P((255, 230, 150), a))


def column(c, x, top, bot, w, shade=1.0):
    K.column(c, x, top, bot, w, 0, shade)


def dunes(c, y0, col1, col2, px=0):
    for k, (yy, cl) in enumerate(((y0, col1), (y0 + 160, col2))):
        p = skia.Path(); p.moveTo(-100, H)
        p.lineTo(-100, yy + 40)
        p.cubicTo(250 + px * (k + 1), yy - 90, 600 + px * (k + 1), yy + 120, W + 100, yy - 20)
        p.lineTo(W + 100, H); p.close()
        c.drawPath(p, P(cl))


def palace(c, cx, base, s, shade=1.0, glow=0.0, t=0.0):
    """Distant palace with columns and a pediment."""
    cl = tuple(int(v * shade) for v in (120, 84, 56))
    c.drawRect(skia.Rect.MakeLTRB(cx - 330 * s, base - 40 * s, cx + 330 * s, base), P(cl))
    for k in range(6):
        column(c, cx - 275 * s + k * 110 * s, base - 330 * s, base - 40 * s, 52 * s, 0.8 * shade)
    c.drawRect(skia.Rect.MakeLTRB(cx - 330 * s, base - 390 * s, cx + 330 * s, base - 330 * s), P(cl))
    tri = skia.Path(); tri.moveTo(cx - 330 * s, base - 390 * s); tri.lineTo(cx, base - 520 * s); tri.lineTo(cx + 330 * s, base - 390 * s); tri.close()
    c.drawPath(tri, P(tuple(int(v * 0.85) for v in cl)))
    if glow > 0:
        radial(c, cx, base - 200 * s, 380 * s, (255, 150, 70), 0.3 * glow)


def throne(c, x, y, s, a=1.0):
    """An empty throne seen from the front (object only)."""
    g = (196, 150, 74); d = (120, 84, 40)
    c.drawRect(skia.Rect.MakeLTRB(x - 120 * s, y - 420 * s, x + 120 * s, y - 120 * s), P(d, a))
    c.drawRect(skia.Rect.MakeLTRB(x - 100 * s, y - 400 * s, x + 100 * s, y - 140 * s), P((150, 40, 40), a))
    c.drawRect(skia.Rect.MakeLTRB(x - 170 * s, y - 140 * s, x + 170 * s, y - 90 * s), P(g, a))
    for sx in (-1, 1):
        c.drawRect(skia.Rect.MakeLTRB(x + sx * 150 * s - 22 * s, y - 230 * s, x + sx * 150 * s + 22 * s, y - 90 * s), P(g, a))
        c.drawRect(skia.Rect.MakeLTRB(x + sx * 140 * s - 14 * s, y - 90 * s, x + sx * 140 * s + 14 * s, y), P(d, a))
    c.drawCircle(x, y - 450 * s, 30 * s, P(g, a))
    c.drawRect(skia.Rect.MakeLTRB(x - 220 * s, y, x + 220 * s, y + 40 * s), P((90, 60, 40), a))


def hall(c, t, u, warm=(170, 70, 40)):
    lin(c, (0, 0, W, 1350), [(0, (30, 8, 12)), (0.7, (110, 40, 30)), (1, warm)])
    lin(c, (0, 1350, W, H), [(0, (110, 66, 42)), (1, (34, 20, 18))])
    for x in (90, 990):
        column(c, x, 300, 1350, 130, 0.6)
    for x in (260, 820):
        column(c, x, 520, 1350, 90, 0.75)
    for x in (300, 780):
        radial(c, x, 900, 120, (255, 170, 80), 0.45 + 0.08 * math.sin(t * 7 + x))
        c.drawCircle(x, 900, 10, P((255, 230, 170)))


def bars(c, prog, a=1.0):
    if prog <= 0:
        return
    yb = -200 + 1500 * ease(prog)
    for k in range(9):
        x = 140 + k * 100
        c.drawLine(x, -50, x, yb, P((40, 34, 32), a, stroke=26))
        c.drawLine(x - 6, -50, x - 6, yb, P((110, 96, 86), 0.5 * a, stroke=4))
    c.drawRect(skia.Rect.MakeLTRB(100, yb - 40, 980, yb), P((50, 42, 38), a))


def plant(c, x, y, h, g, t, ph):
    if g <= 0:
        return
    hh = h * ease(g); sw = math.sin(t * 1.4 + ph) * 8
    p = skia.Path(); p.moveTo(x, y); p.quadTo(x + sw, y - hh * 0.5, x + sw * 1.5, y - hh)
    c.drawPath(p, P((70, 130, 70), 1, stroke=6))
    for k in range(3):
        f = (k + 1) / 4; lx, ly = x + sw * f * 1.5, y - hh * f; s = 26 * ease(g)
        side = 1 if k % 2 else -1
        leaf = skia.Path(); leaf.moveTo(lx, ly); leaf.quadTo(lx + side * s * 1.4, ly - s, lx + side * s * 2.0, ly - s * 0.2)
        leaf.quadTo(lx + side * s, ly + s * 0.2, lx, ly); c.drawPath(leaf, P((96, 168, 86)))


# ------------------------------------------------------------- scenes
def s1_road(c, t, u):
    lin(c, (0, 0, W, H), [(0, (20, 16, 44)), (0.42, (120, 60, 70)), (0.68, (240, 150, 90)), (1, (100, 60, 42))])
    radial(c, 540, 1180, 600, (255, 190, 110), 0.45)
    c.save(); cam(c, 1 + 0.10 * ease(u), 0, 0, 0.35)
    palace(c, 540, 1240, 0.75, 0.55, glow=0.6, t=t)
    c.restore()
    c.save(); cam(c, 1 + 0.12 * ease(u), 0, 30 * u, 1.0)
    dunes(c, 1260, (150, 92, 58), (100, 60, 42), px=-30 * u)
    w = ease(u)
    light(c, 460, 1660 - 120 * w, 50 - 8 * w, t, 1.0)
    light(c, 620, 1680 - 120 * w, 44 - 7 * w, t + 1.3, 0.9)
    c.restore()
    motes(c, t, (255, 200, 140), a=0.35)
    a = clamp((3.6 - t) / 0.6)
    if a > 0:
        lin(c, (0, 0, W, 700), [(0, (6, 6, 14, int(235 * a))), (1, (6, 6, 14, 0))])
        star_orn(c, 540, 300, 58, t, a)
        text(c, "STORIES OF THE PROPHETS", 540, 420, 42, TF_SANS, GOLD, a, 0.24)
        text(c, "PROPHET MUSA  ·  PART 5", 540, 510, 92, TF_COND, CREAM, a, 0.06)
    g = clamp((t - wt(2, "gently")) / 0.5) * clamp((B[1] + 0.1 - t) / 0.4)
    if g > 0:
        text(c, "SPEAK GENTLY", 540, 520, 130, TF_COND, GOLD, g, 0.08)
    lab(c, "TAHA 20:42-44", t, 3.6, B[1] + 0.2)


def s2_night(c, t, u):
    lin(c, (0, 0, W, H), [(0, (6, 8, 24)), (0.6, (24, 24, 56)), (1, (50, 34, 46))])
    stars(c, t, 1.0, ymax=1300)
    c.save(); cam(c, 1 + 0.1 * ease(u), 0, -20 * u, 1.0)
    lin(c, (0, 1500, W, H), [(0, (52, 36, 40)), (1, (18, 12, 16))])
    rs = clamp((t - wt(4, "fear")) / 1.2)
    radial(c, 540, 700, 300 + 900 * rs, (255, 226, 160), 0.15 + 0.35 * rs)
    for k in range(12):
        ang = k * math.pi / 6 + t * 0.1
        if rs > 0:
            c.drawLine(540, 700, 540 + math.cos(ang) * 1400 * rs, 700 + math.sin(ang) * 1400 * rs,
                       P((255, 240, 200), 0.12 * rs, stroke=10, blend=skia.BlendMode.kScreen))
    sh = 1.0 - 0.35 * clamp((t - B[1]) / 1.0) * (1 - rs)
    light(c, 460, 1420, 48, t, sh)
    light(c, 620, 1440, 42, t + 1.3, sh * 0.9)
    c.restore()
    a = clamp((t - wt(4, "hear")) / 0.4)
    if a > 0:
        text(c, "I HEAR AND I SEE", 540, 1100, 110, TF_COND, GOLD, a, 0.08)
    lab(c, "TAHA 20:45-46", t, B[1] + 0.3, B[2] + 0.2)


def s3_gate(c, t, u):
    lin(c, (0, 0, W, H), [(0, (60, 14, 18)), (0.45, (170, 70, 40)), (0.65, (240, 140, 70)), (1, (40, 22, 20))])
    radial(c, 540, 1150, 460, (255, 170, 90), 0.5)
    c.save(); cam(c, 1.0 + 0.18 * ease(u), 0, 60 * u, 1.0)
    lin(c, (-200, 1250, W + 200, H + 300), [(0, (120, 70, 44)), (1, (40, 22, 20))])
    palace(c, 540, 1260, 1.35, 0.9, glow=0.5, t=t)
    c.restore()
    light(c, 470, 1640, 50, t, 1.0)
    light(c, 610, 1660, 44, t + 1.3, 0.9)
    a = clamp((t - wt(5, "Let")) / 0.4)
    if a > 0:
        text(c, "LET THEM GO", 540, 470, 140, TF_COND, CREAM, a, 0.08)
    lab(c, "TAHA 20:47  ·  26:16-17", t, B[2] + 0.3, B[3] + 0.2)


def s4_throne(c, t, u):
    hall(c, t, u)
    c.save(); cam(c, 1 + 0.12 * ease(u), 0, 40 * u, 1.0)
    throne(c, 540, 1350, 1.0)
    c.restore()
    # memory of the basket on the river (Part 1), fading in during line 6
    m = clamp((t - wt(6, "raise")) / 0.6) * clamp((L[7] - 0.1 - t) / 0.5)
    if m > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), P((8, 10, 24), 0.75 * m))
        lin(c, (0, 1100, W, H), [(0, (20, 40, 60, int(255 * m))), (1, (10, 16, 30, int(255 * m)))])
        K.water(c, 1100, t, a=m)
        K.basket(c, 540, 1300 + 10 * math.sin(t * 2), 170, t)
        radial(c, 540, 1280, 300, (255, 220, 160), 0.3 * m)
        text(c, "RAISED IN THE PALACE", 540, 900, 80, TF_COND, CREAM, m, 0.08)
    q = clamp((t - L[7]) / 0.4)
    if q > 0:
        light(c, 540, 1700, 46, t, q)
        text(c, "WHO IS YOUR LORD?", 540, 520, 120, TF_COND, GOLD, q, 0.06)
    lab(c, "ASH-SHU'ARA 26:18" if t < L[7] else "TAHA 20:49", t, B[3] + 0.3, B[4] + 0.2)


def s5_creation(c, t, u):
    lin(c, (0, 0, W, H), [(0, (40, 70, 120)), (0.48, (120, 150, 170)), (0.68, (220, 200, 160)), (1, (50, 40, 28))])
    c.save(); cam(c, 1 + 0.1 * ease(u), 0, 0, 0.5)
    for k in range(5):
        cx = (180 + k * 240 + t * 12) % (W + 300) - 150
        for dx, dy, r in ((0, 0, 80), (70, 10, 64), (-70, 14, 60)):
            c.drawCircle(cx + dx, 100 + 30 * (k % 2) + dy, r, P((236, 240, 246), 0.8))
    c.restore()
    rain = clamp((t - wt(8, "form")) / 0.6)
    if rain > 0:
        rng = np.random.default_rng(5)
        for k in range(90):
            x = rng.uniform(0, W); y0 = rng.uniform(0, 1400)
            y = (y0 + t * 900) % 1400 + 400
            c.drawLine(x, y, x - 6, y + 34, P((220, 230, 255), 0.45 * rain, stroke=2.5))
    c.save(); cam(c, 1 + 0.12 * ease(u), 0, 20 * u, 1.0)
    lin(c, (-200, 1300, W + 200, H + 300), [(0, (110, 90, 56)), (1, (50, 40, 28))])
    g0 = wt(8, "guided")
    for k in range(9):
        plant(c, 80 + k * 115, 1330 + (k % 3) * 60, 220 + 60 * (k % 4), clamp((t - g0 + 0.8 - k * 0.12) / 1.2), t, k)
    light(c, 540, 1660, 46, t, 1.0)
    c.restore()
    a = clamp((t - wt(8, "Lord")) / 0.4)
    if a > 0:
        text(c, "HE GAVE EVERYTHING", 540, 430, 100, TF_COND, CREAM, a, 0.06)
        text(c, "ITS FORM", 540, 550, 120, TF_COND, GOLD, a, 0.08)
    lab(c, "TAHA 20:50", t, B[4] + 0.3, B[5] + 0.2)


def s6_threat(c, t, u):
    hall(c, t, u, warm=(120, 30, 24))
    c.save(); cam(c, 1.15 - 0.1 * ease(u), 0, 0, 1.0)
    throne(c, 540, 1300, 0.85, 0.9)
    c.restore()
    c.drawRect(skia.Rect.MakeWH(W, H), P((40, 0, 0), 0.25))
    light(c, 540, 1650, 48, t, 1.0)
    bars(c, clamp((t - wt(9, "imprison")) / 0.7))
    a = clamp((t - wt(9, "imprison")) / 0.4)
    if a > 0:
        text(c, "PRISON", 540, 560, 180, TF_COND, (240, 120, 90), a, 0.1)
    lab(c, "ASH-SHU'ARA 26:29", t, B[5] + 0.3, B[6] + 0.2)


def s7_signs(c, t, u):
    hall(c, t, u)
    c.drawRect(skia.Rect.MakeWH(W, H), P((10, 6, 10), 0.35))
    c.save(); cam(c, 1 + 0.1 * ease(u), 0, -30 * u, 1.0)
    t_throw = wt(10, "threw"); t_ser = wt(10, "serpent"); t_hand = L[11]
    hand = clamp((t - wt(11, "shone")) / 0.6)
    light(c, 360, 1250, 50, t, 1.0 + 0.8 * hand)
    if t < t_throw + 0.15:
        staff(c, 450, 1420, 400, 8)
    elif t < t_ser - 0.2:
        f = ease(clamp((t - t_throw - 0.15) / 0.5))
        staff(c, 450 + 60 * f, 1420 + 260 * f, 400 - 120 * f, 8 + 75 * f)
    else:
        m = ease(clamp((t - (t_ser - 0.2)) / 0.5))
        radial(c, 640, 1650, 260, (255, 220, 140), 0.5 * (1 - m) + 0.1)
        serpent(c, 640, 1650, 520, t, m * (1 - 0.6 * hand), 0.6 + 0.4 * m)
    if hand > 0:
        radial(c, 360, 1250, 900 * hand, (255, 255, 255), 0.55 * hand)
        for k in range(14):
            ang = k * math.pi / 7 + t * 0.2
            r0, r1 = 110, 110 + 520 * hand
            c.drawLine(360 + math.cos(ang) * r0, 1250 + math.sin(ang) * r0, 360 + math.cos(ang) * r1, 1250 + math.sin(ang) * r1,
                       P((255, 255, 245), 0.35 * hand, stroke=6, blend=skia.BlendMode.kScreen))
    c.restore()
    a = clamp((t - t_ser) / 0.4) * clamp((t_hand - t) / 0.3)
    if a > 0:
        text(c, "A CLEAR SERPENT", 540, 520, 120, TF_COND, GOLD, a, 0.08)
    b = clamp((t - wt(11, "white")) / 0.4)
    if b > 0:
        text(c, "SHINING WHITE", 540, 520, 120, TF_COND, CREAM, b, 0.08)
    lab(c, "ASH-SHU'ARA 26:32-33", t, B[6] + 0.3, B[7] + 0.2)


def s8_end(c, t, u):
    lin(c, (0, 0, W, 1250), [(0, (40, 10, 16)), (1, (150, 60, 40))])
    lin(c, (0, 1250, W, H), [(0, (90, 54, 36)), (1, (30, 18, 16))])
    c.save(); cam(c, 1 + 0.12 * ease(u), 0, 0, 0.6)
    palace(c, 540, 1250, 1.0, 0.6, glow=0.3, t=t)
    c.restore()
    w = ease(u)
    light(c, 470, 1700 - 200 * w, 46 - 8 * w, t, 1.0)
    light(c, 610, 1720 - 200 * w, 40 - 6 * w, t + 1.3, 0.9)
    motes(c, t, (255, 190, 120), a=0.3)
    tf = wt(13, "Follow")
    a = clamp((t - wt(12, "denied")) / 0.4) * clamp((tf - 0.7 - t) / 0.4)
    if a > 0:
        text(c, "HE DENIED", 540, 450, 150, TF_COND, (240, 120, 90), a, 0.1)
        text(c, "AND REFUSED", 540, 555, 90, TF_COND, CREAM, a, 0.1)
    d = ease(clamp((t - tf + 0.6) / 0.8))
    if d > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), P((10, 6, 10), 0.72 * d))
        star_orn(c, 540, 900, 70, t, d)
        text(c, "PART 6", 540, 1170 + 30 * (1 - d), 230, TF_COND, GOLD, d, 0.05)
        f = skia.Font(TF_COND, 96)
        bw = sum(f.measureText(ch) + 0.06 * 96 for ch in "FOLLOW") + 50
        c.drawRect(skia.Rect.MakeXYWH(540 - bw / 2, 1232, bw * ease(clamp((t - tf) / 0.35)), 100), P(GOLD, d))
        text(c, "FOLLOW", 540, 1315, 96, TF_COND, (30, 22, 14), d * clamp((t - tf - 0.1) / 0.3), 0.06)
        text(c, "THE MAGICIANS  ·  COMING NEXT", 540, 1420, 34, TF_SANS, CREAM, d * clamp((t - tf - 0.4) / 0.4), 0.2)
    else:
        lab(c, "TAHA 20:56", t, B[7] + 0.3, tf - 0.5)


SCENES = [s1_road, s2_night, s3_gate, s4_throne, s5_creation, s6_threat, s7_signs, s8_end]


def scene_img(i, t):
    surf = skia.Surface(W, H)
    with surf as c:
        c.clear(skia.Color(0, 0, 0))
        SCENES[i](c, t, clamp((t - B[i]) / (B[i + 1] - B[i])))
    return surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)[..., :3].astype(np.float32)


def frame(t):
    n = len(SCENES)
    i = max(k for k in range(n) if B[k] <= t) if t < DUR else n - 1
    img = scene_img(i, t)
    if i < n - 1 and t > B[i + 1] - XF:
        a = ease((t - (B[i + 1] - XF)) / XF)
        img = img * (1 - a) + scene_img(i + 1, t) * a
    k = min(clamp(t / 0.3 + 0.4), clamp((DUR - t) / 0.6))
    img = img * K.VIG * k + K.GRAIN[int(t * FPS) % 6]
    return np.clip(img, 0, 255).astype(np.uint8)


def render_range(f0, f1, out):
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for n in range(f0, f1):
        enc.stdin.write(frame(n / FPS).tobytes())
    enc.stdin.close(); enc.wait()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--probe", default=""); ap.add_argument("--out", default=""); ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    from PIL import Image
    if a.probe:
        d = ROOT / "out/probe"; d.mkdir(parents=True, exist_ok=True)
        for ts in a.probe.split(","):
            Image.fromarray(frame(float(ts))).save(d / f"p{float(ts):06.2f}.png")
        print("probes done", [round(b, 2) for b in B])
    if a.out:
        from multiprocessing import Process
        N = int(math.ceil(DUR * FPS)); k = a.workers
        cuts = [N * i // k for i in range(k + 1)]
        parts = [str(ROOT / f"out/part{i}.mp4") for i in range(k)]
        ps = [Process(target=render_range, args=(cuts[i], cuts[i + 1], parts[i])) for i in range(k)]
        t0 = time.time(); [p.start() for p in ps]; [p.join() for p in ps]
        lst = ROOT / "out/parts.txt"; lst.write_text("".join(f"file '{p}'\n" for p in parts))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(ROOT / a.out)], check=True)
        print(f"wrote {a.out} ({N} frames, {time.time() - t0:.0f}s)")
