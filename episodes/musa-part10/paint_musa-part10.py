"""Musa Part 10, illustrated: Three Strange Acts. No people drawn; Musa (AS) is a glowing light; the servant of Allah is
only a green cloak. The boy is never shown: only a small ball left on the sand under a dimmed sky (kept modest, 18:74).
  python3 paint_musa-part10.py --probe 2,7,...      python3 paint_musa-part10.py --out out/paint.mp4
"""
import argparse, json, math, pathlib, subprocess, sys, time
import numpy as np
import skia

ROOT = pathlib.Path(__file__).parent
sys.path.insert(0, str(ROOT.parents[1] / "engine" / "core"))
import paint as K
from paint import basket, P, lin, radial, text, light, motes, stars, star_orn, cam, clamp, ease, W, H, FPS, GOLD, CREAM, TF_COND, TF_SANS

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


B = [0.0, L[2] - 0.15, L[4] - 0.15, L[6] - 0.15, L[8] - 0.15, L[10] - 0.15, L[11] - 0.15, L[12] - 0.15, DUR]
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


def fish(c, x, y, s, ang=0.0, a=1.0, t=0.0):
    """A small silver fish (a simple shape)."""
    if a <= 0:
        return
    c.save(); c.translate(x, y); c.rotate(ang); c.scale(s, s)
    wag = math.sin(t * 9) * 6
    b = skia.Path(); b.moveTo(-60, 0); b.cubicTo(-30, -30, 30, -30, 60, 0); b.cubicTo(30, 30, -30, 30, -60, 0); b.close()
    tl = skia.Path(); tl.moveTo(-54, 0); tl.lineTo(-92, -26 + wag); tl.lineTo(-86, 0); tl.lineTo(-92, 26 + wag); tl.close()
    radial(c, 0, 0, 120, (200, 230, 255), 0.35 * a)
    c.drawPath(tl, P((150, 176, 196), a))
    c.drawPath(b, P((196, 214, 228), a))
    c.drawLine(-30, 0, 44, 0, P((240, 248, 255), 0.6 * a, stroke=3))
    c.drawCircle(38, -6, 5, P((30, 40, 60), a))
    c.restore()


def rock(c, x, y, w, h, rgb=(96, 84, 78), a=1.0):
    p = skia.Path(); p.moveTo(x - w / 2, y)
    p.cubicTo(x - w / 2, y - h * 0.7, x - w * 0.25, y - h, x + w * 0.05, y - h)
    p.cubicTo(x + w * 0.4, y - h, x + w / 2, y - h * 0.5, x + w / 2, y); p.close()
    c.drawPath(p, P(rgb, a))
    hl = skia.Path(); hl.moveTo(x - w * 0.35, y - h * 0.55); hl.quadTo(x - w * 0.1, y - h * 0.95, x + w * 0.2, y - h * 0.9)
    c.drawPath(hl, P((min(255, rgb[0] + 60), min(255, rgb[1] + 55), min(255, rgb[2] + 50)), 0.5 * a, stroke=10))
    c.drawRect(skia.Rect.MakeLTRB(x - w / 2 - 20, y - 6, x + w / 2 + 20, y + 12), P((0, 0, 0), 0.25 * a, blur=10))


def two_seas(c, t, top=HZ, a=1.0):
    """Two seas meeting: a blue-green one on the left, a deeper blue on the right, a soft seam between them."""
    for sd, (sh, dp) in ((-1, ((70, 140, 140), (16, 60, 66))), (1, ((60, 96, 150), (14, 30, 70)))):
        c.save()
        clip = skia.Path(); clip.moveTo(540, top); clip.lineTo(540 + sd * 1200, top); clip.lineTo(540 + sd * 1200, H); clip.lineTo(540, H); clip.close()
        c.clipPath(clip, doAntiAlias=True)
        lin(c, (0, top, W, H), [(0, sh + (int(255 * a),)), (1, dp + (int(255 * a),))])
        c.restore()
    seam = skia.Path(); seam.moveTo(540, top)
    for j in range(20):
        yy = top + (H - top) * j / 19
        seam.lineTo(540 + (j / 19) * 0 + math.sin(t * 1.2 + j * 0.8) * 10 * j / 19, yy)
    c.drawPath(seam, P((220, 240, 240), 0.35 * a, stroke=10, blur=8))
    K.water(c, top, t, a, (220, 240, 255), 30, 80, 9)


def footprints(c, x0, y0, x1, y1, n, prog, a=1.0, pairs=2, rgb=(90, 64, 40)):
    """Footprints in the sand (no person), revealed along a path as prog goes 0 to 1."""
    for k in range(n):
        f = k / max(1, n - 1)
        if f > prog:
            break
        x = x0 + (x1 - x0) * f; y = y0 + (y1 - y0) * f
        sc = 0.45 + 0.55 * (y - HZ) / (H - HZ)
        for p_ in range(pairs):
            off = (p_ - (pairs - 1) / 2) * 90 * sc
            side = 1 if k % 2 else -1
            c.drawOval(skia.Rect.MakeXYWH(x + off + side * 12 * sc - 9 * sc, y - 15 * sc, 18 * sc, 30 * sc), P(rgb, 0.6 * a))


def cloak(c, x, y, s, t, a=1.0):
    """A folded green cloak laid on a rock: the servant of Allah, never drawn himself."""
    c.save(); c.translate(x, y); c.scale(s, s)
    radial(c, 0, -20, 260, (170, 230, 170), 0.35 * a)
    p = skia.Path(); p.moveTo(-150, 0); p.cubicTo(-140, -70, -60, -90, 0, -80); p.cubicTo(70, -90, 150, -60, 160, 0)
    p.cubicTo(100, 20, -100, 22, -150, 0); p.close()
    c.drawPath(p, P((52, 120, 70), a))
    for k in range(4):
        f = skia.Path(); f.moveTo(-110 + k * 70, -10); f.quadTo(-90 + k * 70, -60, -60 + k * 70, -70)
        c.drawPath(f, P((110, 180, 120), 0.5 * a, stroke=5))
    c.drawPath(p, P((24, 70, 40), a, stroke=4))
    fl = skia.Path(); fl.moveTo(90, -30); fl.cubicTo(150, 10, 170, 90, 150, 170); fl.lineTo(110, 160); fl.cubicTo(120, 90, 100, 30, 60, -10); fl.close()
    c.drawPath(fl, P((44, 104, 60), a)); c.drawPath(fl, P((24, 70, 40), a, stroke=3))
    c.restore()


def rays(c, x, y, g, t, rgb=(255, 236, 180)):
    for k in range(11):
        ang = math.pi / 2 + (k - 5) * 0.11 + math.sin(t * 0.5 + k) * 0.02
        c.drawLine(x, y - 1500, x + math.cos(ang) * 300, y, P(rgb, 0.08 * g, stroke=50, blur=14))
    radial(c, x, y, 380, rgb, 0.3 * g)


def boat(c, x, y, s, t, a=1.0):
    c.save(); c.translate(x, y + math.sin(t * 1.4) * 6); c.rotate(math.sin(t * 1.1) * 1.5); c.scale(s, s)
    hull = skia.Path(); hull.moveTo(-260, -40); hull.lineTo(260, -40); hull.cubicTo(220, 40, 120, 70, 0, 70); hull.cubicTo(-120, 70, -220, 40, -260, -40); hull.close()
    c.drawPath(hull, P((110, 70, 40), a))
    for k in range(3):
        c.drawLine(-230 + k * 10, -10 + k * 22, 230 - k * 10, -10 + k * 22, P((70, 44, 26), 0.8 * a, stroke=4))
    c.drawLine(0, -40, 0, -420, P((80, 54, 32), a, stroke=12))
    sail = skia.Path(); sail.moveTo(10, -400); sail.quadTo(170, -260, 200, -80); sail.lineTo(10, -80); sail.close()
    c.drawPath(sail, P((230, 214, 180), a))
    c.restore()


def bigtext(c, t, t0, t1, l1, l2, c1=CREAM, c2=GOLD, s1=120, s2=140):
    a = clamp((t - t0) / 0.4) * clamp((t1 - t) / 0.4)
    if a > 0:
        lin(c, (0, 260, W, 690), [(0, (6, 8, 16, 0)), (0.4, (6, 8, 16, int(120 * a))), (1, (6, 8, 16, 0))])
        if l1:
            text(c, l1, 540, 400, s1, TF_COND, c1, a, 0.06)
        text(c, l2, 540, 520 if l1 else 470, s2, TF_COND, c2, a, 0.08)


# ------------------------------------------------------------- new pieces
def torn_boat(c, x, y, s, t, hole=0.0, a=1.0):
    """The ship with a hole torn in its side: water sprays in (no people aboard are drawn)."""
    boat(c, x, y, s, t, a)
    if hole <= 0:
        return
    c.save(); c.translate(x, y + math.sin(t * 1.4) * 6); c.rotate(math.sin(t * 1.1) * 1.5); c.scale(s, s)
    hp = skia.Path(); hp.moveTo(-60, -10)
    for k in range(9):
        ang = k / 8 * math.pi * 2
        r = (30 + (12 if k % 2 else 0)) * hole
        hp.lineTo(-40 + math.cos(ang) * r * 1.4, 20 + math.sin(ang) * r * 0.8)
    hp.close()
    c.drawPath(hp, P((20, 14, 10), a))
    for k in range(7):
        ph = (t * 1.8 + k / 7) % 1.0
        dx = -40 + (k - 3) * 10 + ph * 40 * ((k % 3) - 1); dy = 20 - ph * 60 + ph * ph * 90
        c.drawCircle(dx, dy, 7 * (1 - ph) * hole + 1, P((190, 220, 240), 0.7 * a * hole))
    c.restore()


def ball(c, x, y, r, t, a=1.0):
    """A small, worn ball left alone on the sand."""
    c.drawOval(skia.Rect.MakeXYWH(x - r * 1.3, y + r * 0.7, r * 2.6, r * 0.6), P((0, 0, 0), 0.3 * a, blur=8))
    c.drawCircle(x, y, r, P((170, 120, 80), a))
    c.drawArc(skia.Rect.MakeXYWH(x - r, y - r, 2 * r, 2 * r), 200, 120, False, P((210, 170, 120), 0.7 * a, stroke=5))
    c.drawLine(x - r, y, x + r, y, P((120, 80, 50), 0.7 * a, stroke=3))


def houses(c, base, t, a=1.0, doors_shut=True):
    """A small town of flat-roofed houses with shut doors and dark windows."""
    xs = [(-40, 260, 300), (200, 220, 380), (400, 260, 260), (640, 240, 340), (860, 260, 290)]
    for x, w, h in xs:
        c.drawRect(skia.Rect.MakeXYWH(x, base - h, w, h), P((168, 128, 92), a))
        c.drawRect(skia.Rect.MakeXYWH(x - 8, base - h - 16, w + 16, 20), P((128, 94, 66), a))
        c.drawRect(skia.Rect.MakeXYWH(x + w * 0.4, base - 120, w * 0.22, 120), P((72, 48, 30), a))
        c.drawRect(skia.Rect.MakeXYWH(x + w * 0.15, base - h + 50, 40, 50), P((40, 30, 24), a))
    c.drawRect(skia.Rect.MakeXYWH(0, base, W, H - base), P((150, 116, 80), a))


def wall(c, x, y, cols, rows, t, tilt=0.0, built=1.0, a=1.0):
    """A mud-brick wall; tilt leans it, built raises the repaired rows one by one."""
    bw, bh = 120, 56
    c.save(); c.translate(x, y); c.rotate(tilt)
    for r in range(rows):
        f = clamp(built * rows - r)
        if f <= 0:
            continue
        off = (bw / 2) if r % 2 else 0
        for k in range(cols):
            bx = -cols * bw / 2 + k * bw + off - bw / 4
            by = -(r + 1) * bh - (1 - ease(f)) * 80
            c.drawRect(skia.Rect.MakeXYWH(bx, by, bw - 6, bh - 6), P((206, 150, 96), a * f))
            c.drawRect(skia.Rect.MakeXYWH(bx, by, bw - 6, bh - 6), P((92, 58, 34), a * f, stroke=5))
    c.restore()


def bowl(c, x, y, s, a=1.0):
    p = skia.Path(); p.moveTo(x - 70 * s, y); p.quadTo(x, y + 80 * s, x + 70 * s, y); p.close()
    c.drawPath(p, P((140, 96, 60), a)); c.drawLine(x - 74 * s, y, x + 74 * s, y, P((90, 60, 36), a, stroke=6))


# ------------------------------------------------------------- scenes
def s1_hook(c, t, u):
    sky(c, (24, 30, 64), (120, 100, 130), (240, 170, 120))
    radial(c, 540, HZ, 520, (255, 196, 140), 0.5)
    c.save(); cam(c, 1.03 + 0.08 * ease(u), 0, 0, 0.5)
    sea(c, t, HZ, 1.0, deep=(20, 34, 60), shallow=(110, 96, 110), glint=(255, 210, 160))
    c.restore()
    c.save(); cam(c, 1.06 + 0.14 * ease(u), 0, 30 * u, 1.0)
    torn_boat(c, 560, 1330, 1.0, t, hole=0.0)
    shore(c, 1580, cols=((180, 140, 100), (90, 66, 46)))
    light(c, 330, 1580, 44, t, 1.0)
    cloak(c, 760, 1660, 0.6, t, 0.95)
    # three small marks of what is to come: a ship, a ball, a wall (gold rings)
    for k, lbl in enumerate(("1", "2", "3")):
        g = clamp((t - 3.4 - 0.25 * k) / 0.4)
        if g > 0:
            radial(c, 300 + 240 * k, 840, 90, (255, 220, 150), 0.4 * g)
            c.drawCircle(300 + 240 * k, 840, 56, P(GOLD, g, stroke=5))
            text(c, lbl, 300 + 240 * k, 872, 90, TF_COND, CREAM, g, 0.0)
    c.restore()
    a = clamp((3.2 - t) / 0.6)
    if a > 0:
        lin(c, (0, 0, W, 640), [(0, (6, 6, 14, int(225 * a))), (1, (6, 6, 14, 0))])
        star_orn(c, 540, 290, 50, t, a)
        text(c, "STORIES OF THE PROPHETS", 540, 400, 40, TF_SANS, GOLD, a, 0.24)
        text(c, "PROPHET MUSA  ·  PART 10", 540, 490, 86, TF_COND, CREAM, a, 0.06)
    b = clamp((t - 3.3) / 0.4)
    if b > 0:
        text(c, "THREE STRANGE", 540, 400, 130, TF_COND, CREAM, b, 0.06)
        text(c, "ACTS", 540, 530, 150, TF_COND, GOLD, b, 0.08)
    lab(c, "AL-KAHF 18:71-77", t, 3.3, B[1] + 0.2)


def s2_ship(c, t, u):
    hole = ease(clamp((t - wt(2, "tore")) / 0.8))
    sky(c, (40, 70, 120), (180, 170, 170), (250, 210, 160))
    c.drawCircle(820, 820, 60, P((255, 246, 220))); radial(c, 820, 820, 300, (255, 230, 180), 0.4)
    c.save(); cam(c, 1.02 + 0.06 * ease(u), 0, 0, 0.5)
    sea(c, t, HZ, 1.0, deep=(22, 50, 84), shallow=(100, 140, 166), glint=(255, 245, 220))
    c.restore()
    c.save(); cam(c, 1.08 + 0.2 * ease(u), -80 * u, 80 * u, 1.0)
    torn_boat(c, 540, 1420, 1.25, t, hole=hole)
    light(c, 760, 1210, 40, t, 1.0)
    cloak(c, 380, 1290, 0.45, t, 0.95)
    c.restore()
    bigtext(c, t, wt(2, "tore") + 0.3, L[3] - 0.1, "A HOLE IN", "THE SHIP")
    bigtext(c, t, wt(3, "drown"), B[2] + 0.2, "“TO DROWN", "ITS PEOPLE?”", s2=130)
    lab(c, "AL-KAHF 18:71", t, B[1] + 0.3, B[2] + 0.2)


def s3_patience(c, t, u):
    t5 = L[5]
    sky(c, (50, 60, 100), (170, 170, 170), (246, 214, 170))
    c.save(); cam(c, 1.02 + 0.05 * ease(u), 0, 0, 0.5)
    sea(c, t, HZ, 1.0, deep=(24, 50, 80), shallow=(120, 150, 170), glint=(255, 240, 220))
    c.restore()
    c.save(); cam(c, 1.08 + 0.1 * ease(u), 40 - 80 * ease(u), 60 * u, 1.0)
    shore(c, 1480, cols=((204, 172, 126), (114, 86, 56)))
    rock(c, 760, 1700, 380, 240)
    cloak(c, 760, 1480, 0.85, t, 1.0)
    dim = 1.0 - 0.25 * clamp((t - t5) / 0.6)
    light(c, 300, 1580, 46, t, dim)
    c.restore()
    bigtext(c, t, wt(4, "never"), t5 - 0.1, "“NEVER", "HAVE PATIENCE”", s2=130, c2=(170, 230, 170))
    bigtext(c, t, wt(5, "blame"), B[3] + 0.2, "“DO NOT", "BLAME ME”", s2=150)
    lab(c, "AL-KAHF 18:72-73", t, B[2] + 0.3, B[3] + 0.2)


def s4_boy(c, t, u):
    t7 = L[7]
    sky(c, (20, 22, 40), (70, 66, 86), (130, 110, 110))
    stars(c, t, 0.4)
    c.save(); cam(c, 1.03 + 0.06 * ease(u), 0, 0, 0.5)
    lin(c, (0, HZ, W, H), [(0, (90, 76, 70)), (1, (40, 32, 30))])
    c.restore()
    c.save(); cam(c, 1.06 + 0.16 * ease(u), 0, 40 * u, 1.0)
    shore(c, 1300, cols=((140, 116, 92), (70, 56, 44)))
    footprints(c, 160, 1880, 900, 1400, 12, 1.0, pairs=2, rgb=(60, 44, 32))
    ball(c, 560, 1620, 46, t)
    radial(c, 560, 1620, 200, (230, 220, 200), 0.15)
    g = clamp((t - t7) / 0.5)
    light(c, 240, 1520, 44 + 8 * g, t, 0.9 + 0.4 * g)
    cloak(c, 860, 1520, 0.6, t, 0.85)
    c.restore()
    bigtext(c, t, wt(7, "pure"), B[4] + 0.2, "“A PURE", "SOUL?”", s2=170)
    lab(c, "AL-KAHF 18:74", t, B[3] + 0.3, B[4] + 0.2)


def s5_warning(c, t, u):
    t9 = L[9]
    sky(c, (30, 40, 70), (130, 120, 140), (220, 170, 140))
    c.save(); cam(c, 1.02 + 0.05 * ease(u), 0, 0, 0.5)
    lin(c, (0, HZ, W, H), [(0, (150, 120, 96)), (1, (70, 54, 40))])
    c.restore()
    c.save(); cam(c, 1.1 + 0.1 * ease(u), -40 + 80 * ease(u), 60 * u, 1.0)
    shore(c, 1460, cols=((196, 160, 116), (104, 78, 52)))
    rock(c, 300, 1700, 380, 240)
    cloak(c, 300, 1480, 0.85, t, 1.0)
    light(c, 780, 1580, 46, t, 1.0)
    # distance opening between them after the promise
    for k in range(4):
        radial(c, 780, 1580, 120 + 70 * k + 20 * math.sin(t * 2 + k), (255, 220, 150), 0.05)
    c.restore()
    bigtext(c, t, wt(8, "never"), t9 - 0.1, "“DID I NOT", "TELL YOU?”", s2=140, c2=(170, 230, 170))
    bigtext(c, t, wt(9, "keep"), B[5] + 0.2, "“DO NOT KEEP", "ME WITH YOU”", s1=110, s2=120)
    lab(c, "AL-KAHF 18:75-76", t, B[4] + 0.3, B[5] + 0.2)


def s6_town(c, t, u):
    sky(c, (70, 100, 150), (220, 190, 160), (250, 210, 150))
    c.drawCircle(860, 760, 64, P((255, 240, 200))); radial(c, 860, 760, 300, (255, 220, 170), 0.4)
    c.save(); cam(c, 1.03 + 0.07 * ease(u), 0, 0, 0.6)
    houses(c, 1260, t)
    c.restore()
    c.save(); cam(c, 1.06 + 0.12 * ease(u), 0, 40 * u, 1.0)
    lin(c, (0, 1300, W, H), [(0, (190, 150, 104)), (1, (110, 80, 52))])
    wall(c, 640, 1560, 5, 5, t, tilt=8.0, built=1.0)
    bowl(c, 260, 1700, 1.0)
    light(c, 200, 1520, 42, t, 1.0)
    cloak(c, 400, 1720, 0.5, t, 0.9)
    c.restore()
    bigtext(c, t, wt(10, "refused"), wt(10, "rebuilt") - 0.1, "THEY WERE", "REFUSED FOOD", s2=130)
    bigtext(c, t, wt(10, "falling"), B[6] + 0.2, "A WALL ABOUT", "TO FALL", s1=110, s2=150)
    lab(c, "AL-KAHF 18:77", t, B[5] + 0.3, B[6] + 0.2)


def s7_wall(c, t, u):
    prog = ease(clamp((t - B[6]) / max(0.5, B[7] - B[6] - 0.3)))
    sky(c, (90, 120, 170), (230, 200, 170), (252, 220, 160))
    c.save(); cam(c, 1.03 + 0.05 * ease(u), 0, 0, 0.6)
    houses(c, 1220, t)
    c.restore()
    c.save(); cam(c, 1.1 + 0.12 * ease(u), 0, 50 * u, 1.0)
    lin(c, (0, 1260, W, H), [(0, (196, 156, 108)), (1, (114, 84, 56))])
    c.drawRect(skia.Rect.MakeXYWH(120, 1630, 840, 30), P((0, 0, 0), 0.25, blur=12))
    wall(c, 560, 1640, 6, 6, t, tilt=0.0, built=0.35 + 0.65 * prog)
    motes(c, t, (255, 230, 180), a=0.4)
    light(c, 160, 1560, 42, t, 1.0)
    cloak(c, 920, 1700, 0.5, t, 0.9)
    c.restore()
    bigtext(c, t, wt(11, "payment"), B[7] + 0.2, "“YOU COULD HAVE", "TAKEN PAYMENT”", s1=100, s2=120)
    lab(c, "AL-KAHF 18:77", t, B[6] + 0.3, B[7] + 0.2)


def s8_part(c, t, u):
    sky(c, (16, 18, 44), (90, 70, 110), (220, 140, 110))
    stars(c, t, 0.6)
    radial(c, 540, HZ, 520, (255, 180, 120), 0.4)
    c.save(); cam(c, 1.02 + 0.06 * ease(u), 0, 0, 0.5)
    lin(c, (0, HZ, W, H), [(0, (130, 100, 90)), (1, (50, 38, 34))])
    c.restore()
    c.save(); cam(c, 1.05 + 0.1 * ease(u), 0, 30 * u, 1.0)
    shore(c, 1300, cols=((170, 132, 98), (80, 60, 44)))
    # two paths that split apart
    for sd in (-1, 1):
        p = skia.Path(); p.moveTo(540, 1900); p.cubicTo(540 + sd * 40, 1600, 540 + sd * 240, 1380, 540 + sd * 420, 1180)
        c.drawPath(p, P((220, 190, 140), 0.35, stroke=60, blur=6))
    sep = ease(clamp((t - B[7]) / 3.0))
    light(c, 540 - 200 * sep, 1600 - 120 * sep, 44, t, 1.0)
    cloak(c, 540 + 220 * sep, 1660 - 120 * sep, 0.55, t, 0.95)
    c.restore()
    tf = wt(13, "Follow")
    a = clamp((t - wt(12, "part")) / 0.4) * clamp((wt(13, "wisdom") - 0.1 - t) / 0.4)
    if a > 0:
        text(c, "THIS IS WHERE", 540, 400, 110, TF_COND, CREAM, a, 0.06)
        text(c, "WE PART", 540, 530, 150, TF_COND, GOLD, a, 0.08)
    a2 = clamp((t - wt(13, "wisdom")) / 0.4) * clamp((tf - 0.7 - t) / 0.4)
    if a2 > 0:
        text(c, "THE HIDDEN", 540, 400, 120, TF_COND, CREAM, a2, 0.06)
        text(c, "WISDOM?", 540, 530, 150, TF_COND, GOLD, a2, 0.08)
    d = ease(clamp((t - tf + 0.6) / 0.8))
    if d > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), P((6, 8, 14), 0.72 * d))
        star_orn(c, 540, 900, 70, t, d)
        text(c, "PART 11", 540, 1170 + 30 * (1 - d), 230, TF_COND, GOLD, d, 0.05)
        f = skia.Font(TF_COND, 96)
        bw = sum(f.measureText(ch) + 0.06 * 96 for ch in "FOLLOW") + 50
        c.drawRect(skia.Rect.MakeXYWH(540 - bw / 2, 1232, bw * ease(clamp((t - tf) / 0.35)), 100), P(GOLD, d))
        text(c, "FOLLOW", 540, 1315, 96, TF_COND, (30, 22, 14), d * clamp((t - tf - 0.1) / 0.3), 0.06)
        text(c, "THE HIDDEN WISDOM  ·  COMING NEXT", 540, 1420, 34, TF_SANS, CREAM, d * clamp((t - tf - 0.4) / 0.4), 0.2)
    else:
        lab(c, "AL-KAHF 18:78", t, B[7] + 0.3, tf - 0.5)


SCENES = [s1_hook, s2_ship, s3_patience, s4_boy, s5_warning, s6_town, s7_wall, s8_part]


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
