"""Musa Part 7, illustrated: The Signs. No people drawn; Musa (AS) is a glowing light. Pharaoh's people are shown only
through their palace, grain and an empty throne; the Children of Israel only by their lamps.
  python3 paint_musa-part7.py --probe 2,7,...      python3 paint_musa-part7.py --out out/paint.mp4
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


B = [0.0, L[2] - 0.15, L[4] - 0.15, L[6] - 0.15, L[7] - 0.15, L[9] - 0.15, L[11] - 0.15, L[12] - 0.15, DUR]
XF = 0.45
lab = K.label


# ------------------------------------------------------------- the signs (objects only)
_R = np.random.default_rng(11)
LOC = [(_R.uniform(-200, W + 200), _R.uniform(200, 1500), _R.uniform(0.6, 1.2), _R.uniform(0, 6.3)) for _ in range(70)]
LICE = [(_R.uniform(0, W), _R.uniform(1250, H), _R.uniform(0, 6.3)) for _ in range(260)]
FROGS = [(120 + k * 165 + (k % 2) * 50, 1500 + (k % 3) * 120, 0.8 + 0.25 * (k % 3), k * 1.1) for k in range(6)]


def flood(c, t, level, a=1.0, rgb=(60, 110, 150)):
    """Rising flood water with moving wave lines; level = y of the surface."""
    if a <= 0:
        return
    p = skia.Path(); p.moveTo(-50, H + 50)
    for k in range(0, 24):
        x = -50 + k * 55
        p.lineTo(x, level + math.sin(k * 0.8 + t * 2.4) * 14)
    p.lineTo(W + 50, H + 50); p.close()
    c.drawPath(p, P(rgb, 0.92 * a))
    K.water(c, level, t, a * 0.9, (200, 230, 255), 50, 50, 5)


def blood_river(c, t, top, a=1.0):
    lin(c, (0, top, W, H), [(0, (120, 16, 20, int(255 * a))), (1, (50, 6, 10, int(255 * a)))])
    K.water(c, top, t, a, (255, 110, 100), 26, 60, 8)


def locust(c, x, y, s, t, ph, a=1.0):
    c.save(); c.translate(x, y); c.scale(s, s); c.rotate(-12 + math.sin(t * 3 + ph) * 6)
    c.drawOval(skia.Rect.MakeLTRB(-26, -7, 26, 7), P((96, 84, 40), a))
    fl = 0.5 + 0.5 * math.sin(t * 40 + ph)
    c.drawOval(skia.Rect.MakeLTRB(-18, -20 - 6 * fl, 14, -2), P((200, 190, 140), 0.45 * a))
    c.drawLine(-24, 4, -36, 16, P((80, 66, 30), a, stroke=3)); c.drawLine(20, 4, 30, 16, P((80, 66, 30), a, stroke=3))
    c.restore()


def locusts(c, t, a=1.0, speed=1.0):
    if a <= 0:
        return
    for x, y, s, ph in LOC:
        xx = (x + t * 260 * speed * s) % (W + 400) - 200
        locust(c, xx, y + math.sin(t * 2 + ph) * 30, s, t, ph, a)


def lice(c, t, a=1.0):
    if a <= 0:
        return
    for x, y, ph in LICE:
        c.drawCircle(x + math.sin(t * 6 + ph) * 4, y + math.cos(t * 5 + ph) * 3, 3.2, P((40, 30, 26), 0.8 * a))


def frog(c, x, y, s, t, ph, a=1.0):
    hop = max(0.0, math.sin(t * 2.6 + ph)) ** 3 * 60
    c.save(); c.translate(x, y - hop); c.scale(s, s)
    c.drawOval(skia.Rect.MakeLTRB(-60, -34, 60, 30), P((70, 120, 60), a))
    c.drawOval(skia.Rect.MakeLTRB(-46, -6, 46, 30), P((140, 170, 90), a))
    for sx in (-1, 1):
        c.drawCircle(sx * 30, -36, 15, P((70, 120, 60), a))
        c.drawCircle(sx * 30, -38, 7, P((20, 20, 16), a))
        c.drawOval(skia.Rect.MakeLTRB(sx * 40 - 30, 14, sx * 40 + 30, 36), P((56, 100, 50), a))
    c.restore()


def frogs(c, t, a=1.0):
    if a <= 0:
        return
    for x, y, s, ph in FROGS:
        frog(c, x, y, s, t, ph, a)


def ground(c, y0=1250, cols=((150, 110, 70), (80, 54, 36))):
    lin(c, (0, y0, W, H), [(0, cols[0]), (1, cols[1])])


def cracks(c, a=1.0):
    r = np.random.default_rng(4)
    for k in range(26):
        x = r.uniform(0, W); y = r.uniform(1320, H); p = skia.Path(); p.moveTo(x, y)
        for j in range(4):
            x += r.uniform(-90, 90); y += r.uniform(-20, 40); p.lineTo(x, y)
        c.drawPath(p, P((60, 36, 22), 0.8 * a, stroke=4))


def dead_tree(c, x, y, h, a=1.0):
    p = skia.Path(); p.moveTo(x, y); p.lineTo(x + 8, y - h)
    p.moveTo(x + 4, y - h * 0.55); p.lineTo(x + h * 0.35, y - h * 0.85)
    p.moveTo(x + 6, y - h * 0.72); p.lineTo(x - h * 0.3, y - h * 0.98)
    c.drawPath(p, P((70, 46, 30), a, stroke=14, cap=skia.Paint.kRound_Cap))


def tablet(c, x, y, split, a=1.0):
    """A clay tablet of a promise that cracks and splits in two."""
    off = 120 * ease(split); rot = 9 * ease(split)
    for side in (-1, 1):
        c.save(); c.translate(x + side * off, y + 40 * ease(split)); c.rotate(side * rot)
        p = skia.Path()
        if side < 0:
            p.moveTo(-170, -230); p.lineTo(10, -230); p.lineTo(-20, -80); p.lineTo(20, 60); p.lineTo(-10, 230); p.lineTo(-170, 230)
        else:
            p.moveTo(10, -230); p.lineTo(170, -230); p.lineTo(170, 230); p.lineTo(-10, 230); p.lineTo(20, 60); p.lineTo(-20, -80)
        p.close()
        c.drawPath(p, P((176, 132, 88), a)); c.drawPath(p, P((110, 76, 46), a, stroke=5))
        for k in range(6):
            yy = -170 + k * 62
            c.drawLine(side * 150 if side < 0 else 30, yy, -30 if side < 0 else 150, yy, P((120, 84, 52), 0.7 * a, stroke=5))
        c.restore()


# ------------------------------------------------------------- scenes
def s1_hook(c, t, u):
    # five quick signs, one per word of line 1
    words = ["Flood", "locusts", "lice", "frogs", "blood"]
    ts = [wt(1, w) for w in words] + [wt(1, "One")]
    k = max([0] + [i for i, x in enumerate(ts[:5]) if t >= x - 0.1])
    lin(c, (0, 0, W, 1250), [(0, (30, 26, 50)), (0.7, (120, 70, 70)), (1, (210, 140, 90))])
    c.save(); cam(c, 1.04 + 0.1 * ease(u), 0, 30 * u, 0.5)
    palace(c, 540, 1250, 0.8, 0.6, glow=0.15, t=t)
    c.restore()
    ground(c)
    c.save(); cam(c, 1.05 + 0.1 * ease(u), 0, 30 * u, 1.0)
    if k == 0:
        flood(c, t, 1300 - 120 * clamp(t / 1.5))
    elif k == 1:
        locusts(c, t, 1.0, 1.4)
    elif k == 2:
        lice(c, t, 1.0)
    elif k == 3:
        frogs(c, t, 1.0)
    else:
        blood_river(c, t, 1330, 1.0)
    c.restore()
    if t > ts[5] - 0.1:
        c.drawRect(skia.Rect.MakeWH(W, H), P((30, 0, 0), 0.25))
    a = clamp((3.2 - t) / 0.6)
    if a > 0:
        lin(c, (0, 0, W, 640), [(0, (6, 6, 14, int(225 * a))), (1, (6, 6, 14, 0))])
        star_orn(c, 540, 290, 50, t, a)
        text(c, "STORIES OF THE PROPHETS", 540, 400, 40, TF_SANS, GOLD, a, 0.24)
        text(c, "PROPHET MUSA  ·  PART 7", 540, 490, 86, TF_COND, CREAM, a, 0.06)
    b = clamp((t - 3.3) / 0.4)
    if b > 0:
        text(c, ["THE FLOOD", "LOCUSTS", "LICE", "FROGS", "BLOOD"][k], 540, 560, 130, TF_COND, GOLD, b, 0.08)
    lab(c, "AL-A'RAF 7:133", t, 3.3, B[1] + 0.2)


def s2_famine(c, t, u):
    lin(c, (0, 0, W, 1250), [(0, (150, 110, 70)), (0.6, (230, 170, 100)), (1, (250, 210, 150))])
    radial(c, 540, 700, 420, (255, 230, 170), 0.8)
    c.drawCircle(540, 700, 110, P((255, 246, 220)))
    ground(c, 1250, ((180, 130, 80), (110, 70, 40)))
    c.save(); cam(c, 1 + 0.12 * ease(u), 0, 40 * u, 1.0)
    cracks(c, clamp((t - B[1]) / 1.2))
    for k, x in enumerate((140, 400, 700, 960)):
        dead_tree(c, x, 1400 + (k % 2) * 60, 300 + (k % 3) * 60)
    # a few fallen, shrivelled fruits
    for k in range(9):
        x = 120 + k * 105; y = 1640 + (k % 3) * 40
        c.drawOval(skia.Rect.MakeLTRB(x - 16, y - 10, x + 16, y + 10), P((110, 70, 40)))
    c.restore()
    motes(c, t, (255, 230, 180), a=0.3)
    a = clamp((t - wt(2, "famine")) / 0.4) * clamp((L[3] - 0.1 - t) / 0.4)
    if a > 0:
        text(c, "YEARS OF", 540, 470, 100, TF_COND, CREAM, a, 0.06)
        text(c, "FAMINE", 540, 600, 150, TF_COND, (120, 40, 20), a, 0.08)
    b = clamp((t - wt(3, "reminded")) / 0.4)
    if b > 0:
        text(c, "SO THEY MIGHT", 540, 470, 100, TF_COND, CREAM, b, 0.06)
        text(c, "BE REMINDED", 540, 600, 130, TF_COND, (110, 50, 20), b, 0.08)
    lab(c, "AL-A'RAF 7:130", t, B[1] + 0.3, B[2] + 0.2)


def s3_ours(c, t, u):
    t5 = L[5]
    dark = clamp((t - t5 + 0.2) / 0.8)
    lin(c, (0, 0, W, 1250), [(0, (60, 90, 140)), (0.6, (220, 190, 140)), (1, (250, 220, 160))])
    c.drawRect(skia.Rect.MakeLTRB(0, 0, W, 1250), P((30, 14, 20), 0.6 * dark))
    c.save(); cam(c, 1.02 + 0.1 * ease(u), 0, 0, 0.5)
    palace(c, 540, 1250, 0.9, 0.8 - 0.3 * dark, glow=0.3 * (1 - dark), t=t)
    c.restore()
    ground(c)
    c.save(); cam(c, 1.05 + 0.1 * ease(u), 0, 30 * u, 1.0)
    # golden heaps of grain in good times
    g = 1 - dark
    for k, x in enumerate((260, 540, 820)):
        p = skia.Path(); p.moveTo(x - 150, 1560); p.quadTo(x, 1300 - 40 * (k % 2), x + 150, 1560); p.close()
        c.drawPath(p, P((220, 176, 80), 0.25 + 0.75 * g))
        radial(c, x, 1450, 200, (255, 210, 110), 0.4 * g)
    if dark > 0:
        light(c, 540, 1700, 44, t, dark)
        for k in range(6):
            x = 300 + k * 96 + (60 if k >= 3 else 0) - 30
            radial(c, x, 1760, 30, (255, 200, 120), 0.55 * dark)
            c.drawCircle(x, 1760, 5, P((255, 236, 190), dark))
    c.restore()
    a = clamp((t - wt(4, "ours")) / 0.4) * clamp((t5 - 0.1 - t) / 0.4)
    if a > 0:
        text(c, "“THIS IS OURS”", 540, 540, 130, TF_COND, (110, 60, 20), a, 0.06)
    b = clamp((t - wt(5, "blamed")) / 0.4)
    if b > 0:
        text(c, "THEY BLAMED", 540, 470, 120, TF_COND, CREAM, b, 0.06)
        text(c, "MUSA", 540, 600, 150, TF_COND, GOLD, b, 0.08)
    lab(c, "AL-A'RAF 7:131", t, B[2] + 0.3, B[3] + 0.2)


def s4_refuse(c, t, u):
    hall(c, t, u, warm=(130, 34, 26))
    c.save(); cam(c, 1.12 - 0.08 * ease(u), 0, 0, 1.0)
    throne(c, 540, 1320, 0.85, 0.95)
    c.restore()
    c.drawRect(skia.Rect.MakeWH(W, H), P((40, 0, 0), 0.25))
    light(c, 540, 1640, 44, t, 0.9)
    a = clamp((t - wt(6, "Whatever")) / 0.4)
    if a > 0:
        lin(c, (0, 300, W, 720), [(0, (10, 0, 0, 0)), (0.5, (10, 0, 0, int(170 * a))), (1, (10, 0, 0, 0))])
        text(c, "WE WILL", 540, 470, 110, TF_COND, CREAM, a * clamp((t - wt(6, "never")) / 0.3), 0.08)
        text(c, "NEVER BELIEVE", 540, 600, 130, TF_COND, (255, 140, 100), a * clamp((t - wt(6, "never")) / 0.3), 0.08)
        text(c, "WHATEVER SIGN", 540, 540, 120, TF_COND, CREAM, a * clamp((wt(6, "never") - t) / 0.3), 0.06)
    lab(c, "AL-A'RAF 7:132", t, B[3] + 0.3, B[4] + 0.2)


def s5_signs(c, t, u):
    words = ["flood", "locusts", "lice", "frogs", "blood"]
    ts = [wt(7, w) for w in words]
    k = max([0] + [i for i, x in enumerate(ts) if t >= x - 0.15])
    t8 = L[8]
    lin(c, (0, 0, W, 1250), [(0, (20, 24, 50)), (0.6, (90, 70, 90)), (1, (180, 110, 80))])
    c.save(); cam(c, 1 + 0.1 * ease(u), 0, 0, 0.5)
    palace(c, 540, 1250, 0.8, 0.55, glow=0.1, t=t)
    c.restore()
    ground(c, 1250, ((130, 96, 64), (60, 40, 28)))
    c.save(); cam(c, 1.05 + 0.12 * ease(u), 0, 40 * u, 1.0)
    fl = ease(clamp((t - ts[0] + 0.2) / 1.0))
    flood(c, t, 1500 - 220 * fl, 1.0 if k == 0 else clamp(1 - (t - ts[1] + 0.15) / 0.4))
    locusts(c, t, 1.0 if k == 1 else (0.0 if k < 1 else 0.25), 1.2)
    lice(c, t, 1.0 if k == 2 else (0.0 if k < 2 else 0.3))
    frogs(c, t, 1.0 if k == 3 else (0.0 if k < 3 else 0.5))
    if k >= 4:
        blood_river(c, t, 1380, clamp((t - ts[4] + 0.15) / 0.4))
    c.restore()
    if t >= t8 - 0.2:
        c.drawRect(skia.Rect.MakeWH(W, H), P((30, 0, 0), 0.3 * clamp((t - t8 + 0.2) / 0.5)))
    a = clamp((t - B[4] - 0.3) / 0.3) * clamp((t8 - 0.15 - t) / 0.3)
    if a > 0:
        text(c, ["THE FLOOD", "LOCUSTS", "LICE", "FROGS", "BLOOD"][k], 540, 520, 150, TF_COND, GOLD, a, 0.08)
        text(c, "SIGN %d OF 5" % (k + 1), 540, 640, 44, TF_SANS, CREAM, a, 0.24)
    b = clamp((t - wt(8, "arrogant")) / 0.4)
    if b > 0:
        text(c, "BUT THEY WERE", 540, 470, 100, TF_COND, CREAM, b, 0.06)
        text(c, "ARROGANT", 540, 600, 150, TF_COND, (255, 140, 100), b, 0.08)
    lab(c, "AL-A'RAF 7:133", t, B[4] + 0.3, B[5] + 0.2)


def s6_beg(c, t, u):
    lin(c, (0, 0, W, H), [(0, (8, 10, 30)), (0.6, (30, 28, 60)), (1, (60, 40, 50))])
    stars(c, t, 0.9, ymax=1100)
    c.save(); cam(c, 1 + 0.1 * ease(u), 0, 20 * u, 0.5)
    palace(c, 760, 1300, 0.75, 0.45, glow=0.25, t=t)
    c.restore()
    ground(c, 1300, ((70, 50, 44), (24, 16, 16)))
    c.save(); cam(c, 1.04 + 0.12 * ease(u), 0, 30 * u, 1.0)
    rs = clamp((t - wt(9, "pray")) / 1.0)
    radial(c, 300, 700, 300 + 400 * rs, (255, 226, 160), 0.1 + 0.25 * rs)
    light(c, 300, 1450, 50, t, 0.9 + 0.3 * rs)
    # the waiting Children of Israel, shown only by their lamps
    w = clamp((t - wt(10, "Children")) / 0.6)
    for r in range(2):
        for k in range(6):
            x = 140 + k * 90 + r * 45; y = 1650 + r * 70
            radial(c, x, y, 28, (255, 200, 120), 0.3 + 0.4 * w)
            c.drawCircle(x, y, 5, P((255, 236, 190), 0.5 + 0.5 * w))
    c.restore()
    a = clamp((t - wt(9, "begged")) / 0.4) * clamp((L[10] - 0.1 - t) / 0.4)
    if a > 0:
        text(c, "PRAY TO", 540, 470, 110, TF_COND, CREAM, a, 0.06)
        text(c, "YOUR LORD", 540, 600, 140, TF_COND, GOLD, a, 0.08)
    b = clamp((t - wt(10, "believe")) / 0.4)
    if b > 0:
        text(c, "“WE WILL", 540, 470, 110, TF_COND, CREAM, b, 0.06)
        text(c, "BELIEVE”", 540, 600, 140, TF_COND, GOLD, b, 0.08)
    lab(c, "AL-A'RAF 7:134", t, B[5] + 0.3, B[6] + 0.2)


def s7_broken(c, t, u):
    clr = clamp((t - B[6]) / 1.5)
    lin(c, (0, 0, W, 1250), [(0, (40 + int(40 * clr), 70 + int(50 * clr), 120 + int(50 * clr))), (0.7, (200, 170, 140)), (1, (240, 200, 150))])
    radial(c, 540, 600, 400, (255, 240, 200), 0.4 * clr)
    ground(c)
    c.save(); cam(c, 1.05 + 0.1 * ease(u), 0, 20 * u, 1.0)
    sp = clamp((t - wt(11, "broke") + 0.1) / 0.8)
    tablet(c, 540, 1420, sp)
    if 0 < sp < 1:
        radial(c, 540, 1420, 260, (255, 220, 160), 0.5 * (1 - sp))
    c.restore()
    a = clamp((t - wt(11, "lifted")) / 0.4) * clamp((wt(11, "broke") - 0.1 - t) / 0.3)
    if a > 0:
        text(c, "LIFTED", 540, 520, 140, TF_COND, CREAM, a, 0.08)
        text(c, "FOR A TIME", 540, 640, 60, TF_SANS, GOLD, a, 0.2)
    b = clamp((t - wt(11, "broke")) / 0.4)
    if b > 0:
        text(c, "THEY BROKE", 540, 470, 110, TF_COND, CREAM, b, 0.06)
        text(c, "THEIR WORD", 540, 600, 140, TF_COND, (255, 140, 100), b, 0.08)
    lab(c, "AL-A'RAF 7:135", t, B[6] + 0.3, B[7] + 0.2)


def s8_sea(c, t, u):
    lin(c, (0, 0, W, 1150), [(0, (8, 12, 36)), (0.7, (40, 50, 90)), (1, (90, 90, 120))])
    stars(c, t, 1 - 0.5 * u, ymax=1000)
    c.drawCircle(820, 420, 60, P((240, 236, 220), 0.9))
    radial(c, 820, 420, 200, (220, 230, 255), 0.3)
    c.save(); cam(c, 1 + 0.15 * ease(u), 0, 0, 1.0)
    lin(c, (0, 1150, W, H), [(0, (30, 60, 100)), (1, (8, 16, 34))])
    K.water(c, 1150, t, 1.0, (200, 220, 255), 40, 90, 6)
    for k in range(5):
        y = 1180 + k * 80
        p = skia.Path(); p.moveTo(-50, y)
        for j in range(25):
            p.lineTo(-50 + j * 50, y + math.sin(j * 0.7 + t * (1.5 + 0.2 * k) + k) * (10 + 6 * k))
        c.drawPath(p, P((150, 190, 230), 0.25, stroke=3))
    c.restore()
    light(c, 280, 1100, 40, t, 0.8)
    tf = wt(12, "Follow")
    a = clamp((t - wt(12, "sea")) / 0.4) * clamp((tf - 0.7 - t) / 0.4)
    if a > 0:
        text(c, "THE SEA", 540, 470, 150, TF_COND, GOLD, a, 0.08)
        text(c, "WAS WAITING", 540, 600, 100, TF_COND, CREAM, a, 0.06)
    d = ease(clamp((t - tf + 0.6) / 0.8))
    if d > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), P((6, 8, 14), 0.72 * d))
        star_orn(c, 540, 900, 70, t, d)
        text(c, "PART 8", 540, 1170 + 30 * (1 - d), 230, TF_COND, GOLD, d, 0.05)
        f = skia.Font(TF_COND, 96)
        bw = sum(f.measureText(ch) + 0.06 * 96 for ch in "FOLLOW") + 50
        c.drawRect(skia.Rect.MakeXYWH(540 - bw / 2, 1232, bw * ease(clamp((t - tf) / 0.35)), 100), P(GOLD, d))
        text(c, "FOLLOW", 540, 1315, 96, TF_COND, (30, 22, 14), d * clamp((t - tf - 0.1) / 0.3), 0.06)
        text(c, "THE SEA SPLITS  ·  COMING NEXT", 540, 1420, 34, TF_SANS, CREAM, d * clamp((t - tf - 0.4) / 0.4), 0.2)
    else:
        lab(c, "AL-A'RAF 7:136", t, B[7] + 0.3, tf - 0.5)


SCENES = [s1_hook, s2_famine, s3_ours, s4_refuse, s5_signs, s6_beg, s7_broken, s8_sea]


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
