"""Musa Part 8, illustrated: The Sea Splits. No people drawn; Musa (AS) is a glowing light. The Children of Israel are
shown only by their lamps; Pharaoh's army only by dust, banners, spear tips and chariot wheels.
  python3 paint_musa-part8.py --probe 2,7,...      python3 paint_musa-part8.py --out out/paint.mp4
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
        if w.lower().strip(".,:!?'\"“”").startswith(word.lower()):
            return s["start"] + (s["end"] - s["start"]) * acc / tot
        acc += len(w)
    return s["start"]


B = [0.0, L[2] - 0.15, L[4] - 0.15, L[6] - 0.15, L[7] - 0.15, L[9] - 0.15, L[10] - 0.15, L[12] - 0.15, DUR]
XF = 0.45
lab = K.label
HZ = 1020  # horizon


# ------------------------------------------------------------- pieces
def staff(c, x, y, h, ang=0, rgb=(110, 74, 46), a=1.0):
    c.save(); c.translate(x, y); c.rotate(ang)
    p = skia.Path(); p.moveTo(0, 0); p.lineTo(6, -h); p.quadTo(44, -h - 44, 52, -h + 10)
    c.drawPath(p, P(rgb, a, stroke=12)); c.restore()


def sky(c, top, mid, bot, y1=HZ):
    lin(c, (0, 0, W, y1), [(0, top), (0.65, mid), (1, bot)])


def sea(c, t, top=HZ, a=1.0, deep=(18, 40, 74), shallow=(48, 92, 130), glint=(220, 230, 255)):
    lin(c, (0, top, W, H), [(0, shallow + (int(255 * a),)), (1, deep + (int(255 * a),))])
    K.water(c, top, t, a, glint, 40, 90, 6)
    for k in range(6):
        y = top + 40 + k * 120
        p = skia.Path(); p.moveTo(-50, y)
        for j in range(25):
            p.lineTo(-50 + j * 50, y + math.sin(j * 0.7 + t * (1.4 + 0.2 * k) + k) * (8 + 5 * k))
        c.drawPath(p, P((150, 190, 230), 0.22 * a, stroke=3))


def shore(c, y0, cols=((176, 140, 96), (96, 70, 48)), x0=0, x1=W):
    p = skia.Path(); p.moveTo(x0 - 60, H + 40); p.lineTo(x0 - 60, y0 + 30)
    p.cubicTo(x0 + 300, y0 - 40, x1 - 400, y0 + 60, x1 + 60, y0); p.lineTo(x1 + 60, H + 40); p.close()
    c.save(); c.clipPath(p, doAntiAlias=True)
    lin(c, (0, y0 - 60, W, H), [(0, cols[0]), (1, cols[1])])
    c.restore()


def lamps(c, t, cx, cy, n=14, rows=2, sp=58, a=1.0, scale=1.0):
    """The Children of Israel, shown only as small lamps."""
    for r in range(rows):
        for k in range(n):
            x = cx + (k - n / 2) * sp * scale + r * sp * 0.5 * scale
            y = cy + r * 46 * scale + math.sin(k * 1.7 + r) * 8
            fl = 0.85 + 0.15 * math.sin(t * 8 + k * 2.1 + r)
            radial(c, x, y, 26 * scale, (255, 200, 120), 0.5 * a * fl)
            c.drawCircle(x, y, 4.5 * scale, P((255, 236, 190), a))


def army(c, t, x, y, s, a=1.0, n=9):
    """Pharaoh's army as objects only: a dust cloud, banners and spear tips on the horizon."""
    if a <= 0:
        return
    for k in range(7):
        radial(c, x + (k - 3) * 120 * s + math.sin(t * 0.8 + k) * 20, y - 40 * s, 200 * s, (170, 120, 80), 0.55 * a,
               blend=skia.BlendMode.kSrcOver)
    for k in range(n * 2):
        sx = x + (k - n) * 34 * s
        c.drawLine(sx, y, sx + 4 * s, y - 120 * s, P((40, 26, 20), a, stroke=3 * s))
        tri = skia.Path(); tri.moveTo(sx + 4 * s, y - 136 * s); tri.lineTo(sx - 4 * s, y - 118 * s); tri.lineTo(sx + 12 * s, y - 118 * s); tri.close()
        c.drawPath(tri, P((200, 180, 140), a))
    for k in range(n // 2):
        bx = x + (k - n / 4) * 120 * s
        c.drawLine(bx, y, bx, y - 230 * s, P((50, 30, 22), a, stroke=5 * s))
        fl = skia.Path(); wv = math.sin(t * 5 + k) * 12 * s
        fl.moveTo(bx, y - 230 * s); fl.quadTo(bx + 50 * s, y - 220 * s + wv, bx + 100 * s, y - 210 * s)
        fl.lineTo(bx + 100 * s, y - 160 * s); fl.quadTo(bx + 50 * s, y - 170 * s + wv, bx, y - 175 * s); fl.close()
        c.drawPath(fl, P((150, 36, 32), a))
        c.drawCircle(bx + 40 * s, y - 192 * s, 9 * s, P(GOLD, a))


def wheel(c, x, y, r, ang, a=1.0, rgb=(120, 84, 40)):
    c.drawCircle(x, y, r, P(rgb, a, stroke=r * 0.16))
    for k in range(6):
        q = ang + k * math.pi / 3
        c.drawLine(x, y, x + math.cos(q) * r, y + math.sin(q) * r, P(rgb, a, stroke=r * 0.08))
    c.drawCircle(x, y, r * 0.16, P(rgb, a))


def split_sea(c, t, prog, close=0.0):
    """Looking down the sea: a dry path opens in the middle with towering walls of water each side."""
    o = ease(prog) * (1 - ease(close))
    # sea surface (before the split) / sea floor path
    lin(c, (0, HZ, W, H), [(0, (48, 92, 130)), (1, (18, 40, 74))])
    K.water(c, HZ, t, 1.0 - 0.7 * o, (220, 230, 255), 40, 90, 6)
    if o <= 0:
        return
    path = skia.Path(); path.moveTo(540 - 30 * o, HZ); path.lineTo(540 + 30 * o, HZ)
    path.lineTo(540 + 420 * o, H + 20); path.lineTo(540 - 420 * o, H + 20); path.close()
    c.save(); c.clipPath(path, doAntiAlias=True)
    lin(c, (0, HZ, W, H), [(0, (150, 120, 86)), (1, (196, 160, 112))])
    for k in range(10):
        y = HZ + 40 + k * k * 9
        c.drawLine(0, y, W, y, P((120, 92, 64), 0.25, stroke=2 + k * 0.4))
    c.restore()
    hgt = 900 * o
    for sd in (-1, 1):
        wall = skia.Path()
        xin_top = 540 + sd * 30 * o; xin_bot = 540 + sd * 420 * o
        wall.moveTo(xin_top, HZ); wall.lineTo(xin_bot, H + 20); wall.lineTo(540 + sd * 900, H + 20); wall.lineTo(540 + sd * 900, HZ - hgt * 0.4)
        wall.lineTo(xin_top + sd * 60, HZ - hgt * 0.25); wall.close()
        c.save(); c.clipPath(wall, doAntiAlias=True)
        lin(c, (0, HZ - hgt, W, H), [(0, (90, 150, 190)), (0.4, (36, 84, 130)), (1, (10, 26, 52))])
        for k in range(14):
            yy = HZ - hgt * 0.4 + k * 80 + (t * 60 % 80)
            c.drawLine(540 + sd * 40, yy, 540 + sd * 900, yy - 30, P((170, 210, 240), 0.12, stroke=4))
        c.restore()
        # bright inner face
        face = skia.Path(); face.moveTo(xin_top, HZ); face.lineTo(xin_bot, H + 20); face.lineTo(xin_bot + sd * 70, H + 20)
        face.lineTo(xin_top + sd * 60, HZ - hgt * 0.25); face.close()
        c.drawPath(face, P((140, 200, 235), 0.35))
        # crest spray
        for k in range(10):
            f = k / 9
            sx = xin_top + sd * 60 + (540 + sd * 900 - xin_top - sd * 60) * f
            sy = HZ - hgt * (0.25 + 0.15 * f)
            radial(c, sx, sy + math.sin(t * 3 + k) * 8, 60, (230, 245, 255), 0.35 * o)


# ------------------------------------------------------------- scenes
def s1_hook(c, t, u):
    sky(c, (40, 34, 70), (190, 120, 100), (250, 190, 130))
    radial(c, 540, HZ, 500, (255, 210, 150), 0.6)
    c.save(); cam(c, 1.04 + 0.1 * ease(u), 0, 20 * u, 0.6)
    sea(c, t, HZ, 1.0, deep=(20, 40, 70), shallow=(90, 110, 140), glint=(255, 220, 180))
    c.restore()
    c.save(); cam(c, 1.06 + 0.12 * ease(u), 0, 40 * u, 1.0)
    shore(c, 1560)
    lamps(c, t, 560, 1620, n=12, rows=2, a=0.95)
    light(c, 540, 1500, 46, t, 1.0)
    c.restore()
    # the army closing in from behind (bottom edge), dust and banners
    c.save(); cam(c, 1.0 + 0.2 * ease(u), 0, -60 * u, 1.0)
    army(c, t, 540, H + 120 - 120 * ease(u), 1.5, 0.95)
    c.restore()
    a = clamp((3.2 - t) / 0.6)
    if a > 0:
        lin(c, (0, 0, W, 640), [(0, (6, 6, 14, int(225 * a))), (1, (6, 6, 14, 0))])
        star_orn(c, 540, 290, 50, t, a)
        text(c, "STORIES OF THE PROPHETS", 540, 400, 40, TF_SANS, GOLD, a, 0.24)
        text(c, "PROPHET MUSA  ·  PART 8", 540, 490, 86, TF_COND, CREAM, a, 0.06)
    b = clamp((t - 3.3) / 0.4)
    if b > 0:
        text(c, "NOWHERE", 540, 470, 120, TF_COND, CREAM, b, 0.06)
        text(c, "LEFT TO RUN", 540, 600, 140, TF_COND, GOLD, b, 0.08)
    lab(c, "ASH-SHU'ARA 26:61", t, 3.3, B[1] + 0.2)


def s2_night(c, t, u):
    t3 = L[3]
    sky(c, (4, 6, 22), (16, 20, 50), (40, 36, 70), 1200)
    stars(c, t, 1.0, ymax=1100)
    c.drawCircle(830, 380, 46, P((240, 236, 220), 0.9)); radial(c, 830, 380, 160, (220, 230, 255), 0.3)
    p3 = clamp((t - t3 + 0.2) / 0.6)
    c.save(); cam(c, 1 + 0.08 * ease(u), 0, 0, 0.5)
    # distant cities, lit by gatherers' torches in line 3
    for k, x in enumerate((140, 420, 760, 980)):
        base = 1180 + (k % 2) * 20
        c.drawRect(skia.Rect.MakeLTRB(x - 70, base - 70, x + 70, base), P((30, 24, 34)))
        c.drawRect(skia.Rect.MakeLTRB(x - 40, base - 120, x + 20, base - 70), P((30, 24, 34)))
        radial(c, x, base - 60, 120, (255, 140, 60), 0.5 * p3)
    c.restore()
    lin(c, (0, 1200, W, H), [(0, (60, 50, 54)), (1, (16, 12, 16))])
    c.save(); cam(c, 1.04 + 0.12 * ease(u), -80 * u, 30 * u, 1.0)
    prog = clamp((t - B[1]) / (B[2] - B[1]))
    lamps(c, t, 200 + 500 * prog, 1560, n=12, rows=2, a=0.95)
    light(c, 260 + 500 * prog + 380, 1470, 44, t, 0.95)
    # torches riding out from the palace in line 3
    if p3 > 0:
        for k in range(10):
            ang = k * 0.63
            r = 80 + 520 * ease(clamp((t - t3) / 3.0))
            x = 540 + math.cos(ang) * r; y = 1300 + math.sin(ang) * r * 0.25
            radial(c, x, y, 36, (255, 140, 60), 0.6 * p3)
            c.drawCircle(x, y, 6, P((255, 210, 140), p3))
    c.restore()
    a = clamp((t - wt(2, "Travel")) / 0.4) * clamp((t3 - 0.1 - t) / 0.4)
    if a > 0:
        text(c, "TRAVEL", 540, 470, 120, TF_COND, CREAM, a, 0.06)
        text(c, "BY NIGHT", 540, 600, 150, TF_COND, GOLD, a, 0.08)
    b = clamp((t - wt(3, "small")) / 0.4)
    if b > 0:
        text(c, "“ONLY A", 540, 470, 110, TF_COND, CREAM, b, 0.06)
        text(c, "SMALL BAND”", 540, 600, 140, TF_COND, (255, 140, 100), b, 0.08)
    lab(c, "ASH-SHU'ARA 26:52-54", t, B[1] + 0.3, B[2] + 0.2)


def s3_sunrise(c, t, u):
    t5 = L[5]
    sr = ease(clamp((t - B[2]) / 2.0))
    sky(c, (60 + int(60 * sr), 50 + int(50 * sr), 90), (200, 120 + int(30 * sr), 90), (255, 190, 120))
    sy = HZ + 60 - 200 * sr
    radial(c, 540, sy, 520, (255, 200, 120), 0.7); c.drawCircle(540, sy, 90, P((255, 226, 160)))
    c.save(); cam(c, 1.02 + 0.08 * ease(u), 0, 0, 0.5)
    sea(c, t, HZ, 1.0, deep=(30, 46, 74), shallow=(150, 120, 110), glint=(255, 210, 160))
    c.restore()
    c.save(); cam(c, 1.05 + 0.12 * ease(u), 0, 30 * u, 1.0)
    shore(c, 1420, cols=((196, 150, 100), (110, 76, 50)))
    lamps(c, t, 680, 1560, n=10, rows=2, a=0.9)
    light(c, 840, 1470, 44, t, 0.95)
    ap = ease(clamp((t - B[2]) / (B[3] - B[2])))
    army(c, t, 60 + 220 * ap, 1500 + 40 * ap, 0.8 + 0.5 * ap, 0.95)
    c.restore()
    if t > t5:
        c.drawRect(skia.Rect.MakeWH(W, H), P((40, 0, 0), 0.22 * clamp((t - t5) / 0.6)))
    a = clamp((t - wt(4, "sunrise")) / 0.4) * clamp((t5 - 0.1 - t) / 0.4)
    if a > 0:
        text(c, "AT SUNRISE", 540, 520, 140, TF_COND, (90, 40, 20), a, 0.06)
    b = clamp((t - wt(5, "overtaken")) / 0.3)
    if b > 0:
        text(c, "“WE WILL BE", 540, 470, 110, TF_COND, CREAM, b, 0.06)
        text(c, "OVERTAKEN!”", 540, 600, 140, TF_COND, (255, 140, 100), b, 0.08)
    lab(c, "ASH-SHU'ARA 26:60-61", t, B[2] + 0.3, B[3] + 0.2)


def s4_lord(c, t, u):
    g = ease(clamp((t - B[3]) / 1.2))
    sky(c, (30, 30, 70), (160, 120, 120), (250, 200, 150))
    c.save(); cam(c, 1.02 + 0.06 * ease(u), 0, 0, 0.5)
    sea(c, t, HZ, 1.0, deep=(24, 42, 70), shallow=(110, 120, 140), glint=(255, 230, 190))
    c.restore()
    c.save(); cam(c, 1.1 + 0.15 * ease(u), 0, 80 * u, 1.0)
    shore(c, 1480)
    for k in range(12):
        ang = -math.pi / 2 + (k - 5.5) * 0.18 + math.sin(t * 0.6) * 0.03
        x2 = 540 + math.cos(ang) * 1400; y2 = 1380 + math.sin(ang) * 1400
        c.drawLine(540, 1380, x2, y2, P((255, 230, 170), 0.10 * g, stroke=30, blur=10))
    radial(c, 540, 1380, 300 + 300 * g, (255, 226, 160), 0.25 + 0.3 * g)
    light(c, 540, 1380, 56, t, 1.0 + 0.4 * g)
    lamps(c, t, 560, 1640, n=12, rows=2, a=0.9)
    c.restore()
    a = clamp((t - wt(6, "Lord")) / 0.4)
    if a > 0:
        text(c, "MY LORD", 540, 470, 140, TF_COND, GOLD, a, 0.08)
        text(c, "IS WITH ME", 540, 600, 120, TF_COND, CREAM, a, 0.06)
    else:
        n = clamp((t - wt(6, "No")) / 0.3)
        text(c, "NO!", 540, 540, 180, TF_COND, CREAM, n, 0.08)
    lab(c, "ASH-SHU'ARA 26:62", t, B[3] + 0.3, B[4] + 0.2)


def s5_strike(c, t, u):
    ts = wt(7, "Strike")
    tsp = L[8] - 0.4
    prog = clamp((t - tsp) / 2.2)
    sky(c, (20, 24, 60), (120, 110, 140), (230, 190, 160))
    radial(c, 540, HZ, 600, (255, 220, 170), 0.4 + 0.3 * prog)
    c.save(); cam(c, 1.03 + 0.1 * ease(u), 0, 60 * ease(prog), 1.0)
    split_sea(c, t, prog)
    c.restore()
    # the staff raised then brought down, at the foot of the frame
    hit = ease(clamp((t - ts - 0.3) / 0.5))
    sa = clamp((t - B[4]) / 0.4) * clamp((tsp + 1.4 - t) / 0.5)
    if sa > 0:
        staff(c, 640, 1880, 520, ang=-25 + 25 * hit, a=sa)
        light(c, 540, 1700, 48, t, 0.9 * sa + 0.3)
        if 0.6 < hit:
            radial(c, 600, 1500, 400, (255, 240, 200), 0.5 * clamp((tsp + 1.2 - t) / 1.0))
    else:
        light(c, 540, 1700, 48, t, 0.9)
    a = clamp((t - ts) / 0.4) * clamp((tsp - t) / 0.3)
    if a > 0:
        text(c, "STRIKE", 540, 470, 140, TF_COND, CREAM, a, 0.06)
        text(c, "THE SEA", 540, 600, 150, TF_COND, GOLD, a, 0.08)
    b = clamp((t - wt(8, "mountain")) / 0.4)
    if b > 0:
        text(c, "LIKE GREAT", 540, 470, 110, TF_COND, CREAM, b, 0.06)
        text(c, "MOUNTAINS", 540, 600, 150, TF_COND, GOLD, b, 0.08)
    lab(c, "ASH-SHU'ARA 26:63", t, B[4] + 0.3, B[5] + 0.2)


def s6_saved(c, t, u):
    sky(c, (30, 40, 80), (150, 140, 150), (250, 210, 160))
    radial(c, 540, HZ, 600, (255, 230, 180), 0.6)
    c.save(); cam(c, 1.05 + 0.12 * ease(u), 0, 40 * u, 1.0)
    split_sea(c, t, 1.0)
    # lamps travelling down the path, getting smaller toward the far shore
    for k in range(16):
        f = ((k / 16) + u * 0.6) % 1.0
        y = H - 100 - (H - 100 - HZ - 20) * f
        x = 540 + math.sin(k * 2.3) * 160 * (1 - f)
        s = 1.0 - 0.8 * f
        radial(c, x, y, 26 * s, (255, 200, 120), 0.6)
        c.drawCircle(x, y, 5 * s, P((255, 236, 190)))
    fl = ease(u)
    light(c, 540, HZ + 80 + 300 * (1 - fl), 40 - 16 * fl, t, 1.0)
    c.restore()
    a = clamp((t - wt(9, "saved")) / 0.4)
    if a > 0:
        text(c, "ALLAH SAVED", 540, 470, 120, TF_COND, CREAM, a, 0.06)
        text(c, "THEM ALL", 540, 600, 150, TF_COND, GOLD, a, 0.08)
    lab(c, "ASH-SHU'ARA 26:65", t, B[5] + 0.3, B[6] + 0.2)


def s7_drown(c, t, u):
    t11 = L[11]
    cl = clamp((t - wt(10, "sea") + 0.6) / 1.4)
    sky(c, (20, 20, 40), (80, 70, 90), (140, 110, 110), HZ + 14)
    c.save(); cam(c, 1.05 + 0.1 * ease(u), 0, 30 * u, 1.0)
    split_sea(c, t, 1.0, close=cl)
    if cl < 1:
        army(c, t, 540, HZ + 260, 0.9, 1.0 - cl)
    if cl > 0:
        sea(c, t, HZ, ease(cl), deep=(12, 26, 48), shallow=(40, 70, 100))
    # what is left: a chariot wheel and a torn banner drifting
    if cl > 0.5:
        k = clamp((cl - 0.5) * 2)
        wheel(c, 360 + 30 * math.sin(t * 0.7), 1500 + 12 * math.sin(t * 1.3), 90, t * 0.2, k * 0.9)
        fl = skia.Path(); fl.moveTo(700, 1620); fl.quadTo(760, 1600 + 10 * math.sin(t * 2), 820, 1630); fl.lineTo(800, 1680); fl.quadTo(750, 1660, 700, 1670); fl.close()
        c.drawPath(fl, P((150, 36, 32), 0.85 * k))
    c.restore()
    if t > t11:
        c.drawRect(skia.Rect.MakeWH(W, H), P((10, 10, 20), 0.35 * clamp((t - t11) / 0.6)))
    a = clamp((t - wt(10, "covered")) / 0.4) * clamp((t11 - 0.1 - t) / 0.4)
    if a > 0:
        text(c, "THE SEA", 540, 470, 120, TF_COND, CREAM, a, 0.06)
        text(c, "COVERED THEM", 540, 600, 130, TF_COND, (160, 210, 240), a, 0.08)
    tn = wt(11, "Now")
    b = clamp((t - wt(11, "believe")) / 0.3) * clamp((tn - 0.1 - t) / 0.3)
    if b > 0:
        text(c, "“I BELIEVE!”", 540, 540, 140, TF_COND, CREAM, b, 0.06)
    d = clamp((t - tn) / 0.3)
    if d > 0:
        text(c, "“NOW?”", 540, 540, 190, TF_COND, GOLD, d, 0.08)
    lab(c, "YUNUS 10:90-91" if t > t11 - 0.2 else "TAHA 20:78", t, B[6] + 0.3, B[7] + 0.2)


def s8_sign(c, t, u):
    sky(c, (70, 90, 140), (220, 180, 150), (255, 220, 170))
    radial(c, 540, HZ - 100, 500, (255, 236, 190), 0.6); c.drawCircle(540, HZ - 120, 80, P((255, 244, 214)))
    c.save(); cam(c, 1.02 + 0.08 * ease(u), 0, 0, 0.5)
    sea(c, t, HZ, 1.0, deep=(40, 70, 100), shallow=(140, 160, 170), glint=(255, 240, 210))
    c.restore()
    c.save(); cam(c, 1.05 + 0.12 * ease(u), 0, 30 * u, 1.0)
    shore(c, 1500, cols=((214, 176, 120), (130, 96, 60)))
    # a sign left on the shore: a fallen golden crown (object only)
    cx, cy = 540, 1640
    radial(c, cx, cy - 30, 200, (255, 210, 120), 0.35)
    cr = skia.Path(); cr.moveTo(cx - 110, cy); cr.lineTo(cx - 120, cy - 90); cr.lineTo(cx - 60, cy - 40); cr.lineTo(cx, cy - 110)
    cr.lineTo(cx + 60, cy - 40); cr.lineTo(cx + 120, cy - 90); cr.lineTo(cx + 110, cy); cr.close()
    c.save(); c.rotate(-8, cx, cy)
    c.drawPath(cr, P((206, 160, 70))); c.drawPath(cr, P((120, 84, 30), 1, stroke=5))
    c.drawRect(skia.Rect.MakeLTRB(cx - 112, cy - 10, cx + 112, cy + 18), P((170, 120, 50)))
    for dx in (-60, 0, 60):
        c.drawCircle(cx + dx, cy + 4, 9, P((150, 40, 40)))
    c.restore()
    c.restore()
    motes(c, t, (255, 236, 200), a=0.35)
    tf = wt(13, "Follow")
    a = clamp((t - wt(12, "sign")) / 0.4) * clamp((L[13] - 0.1 - t) / 0.4)
    if a > 0:
        text(c, "A SIGN", 540, 470, 150, TF_COND, (90, 50, 20), a, 0.08)
        text(c, "FOR ALL WHO COME AFTER", 540, 580, 50, TF_SANS, (60, 40, 30), a, 0.16)
    n = clamp((t - L[13]) / 0.4) * clamp((tf - 0.7 - t) / 0.4)
    if n > 0:
        text(c, "NEXT:", 540, 470, 80, TF_COND, (60, 40, 30), n, 0.1)
        text(c, "A HIDDEN KNOWLEDGE", 540, 590, 100, TF_COND, (90, 50, 20), n, 0.06)
    d = ease(clamp((t - tf + 0.6) / 0.8))
    if d > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), P((6, 8, 14), 0.72 * d))
        star_orn(c, 540, 900, 70, t, d)
        text(c, "PART 9", 540, 1170 + 30 * (1 - d), 230, TF_COND, GOLD, d, 0.05)
        f = skia.Font(TF_COND, 96)
        bw = sum(f.measureText(ch) + 0.06 * 96 for ch in "FOLLOW") + 50
        c.drawRect(skia.Rect.MakeXYWH(540 - bw / 2, 1232, bw * ease(clamp((t - tf) / 0.35)), 100), P(GOLD, d))
        text(c, "FOLLOW", 540, 1315, 96, TF_COND, (30, 22, 14), d * clamp((t - tf - 0.1) / 0.3), 0.06)
        text(c, "THE JOURNEY TO KHIDR  ·  COMING NEXT", 540, 1420, 34, TF_SANS, CREAM, d * clamp((t - tf - 0.4) / 0.4), 0.2)
    else:
        lab(c, "YUNUS 10:92", t, B[7] + 0.3, tf - 0.5)


SCENES = [s1_hook, s2_night, s3_sunrise, s4_lord, s5_strike, s6_saved, s7_drown, s8_sign]


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
