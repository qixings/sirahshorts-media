"""Musa Part 3, illustrated: the well of Madyan. No people drawn; Musa (AS) is the glowing light.
The women, shepherds and father appear only through sheep, staffs, footprints, a tent and lamps.
  python3 paint3.py --probe 2,7,...      python3 paint3.py --out out/paint.mp4
"""
import argparse, json, math, pathlib, subprocess, sys, time
import numpy as np
import skia

ROOT = pathlib.Path(__file__).parent
sys.path.insert(0, str(ROOT.parents[2] / "engine" / "core"))  # repo/engine/core
import paint as K
from paint import P, lin, radial, text, light, palm, motes, stars, star_orn, cam, clamp, ease, W, H, FPS, GOLD, CREAM, TF_COND, TF_SANS

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


B = [0.0, L[2] - 0.15, L[5] - 0.15, L[6] - 0.15, L[7] - 0.15, L[9] - 0.15, L[11] - 0.15, L[12] - 0.15, DUR]
XF = 0.45
lab = K.label


def sky_day(c, top=(120, 170, 220), bot=(250, 222, 170), hz=1100):
    lin(c, (0, 0, W, hz), [(0, top), (1, bot)])


def ground(c, y0=1050, a=(214, 170, 110), b=(150, 104, 62)):
    lin(c, (0, y0, W, H), [(0, a), (1, b)])


def dune_line(c, y, amp, col, ph=0):
    d = skia.Path(); d.moveTo(-100, H); d.lineTo(-100, y)
    d.cubicTo(250, y - amp, 500 + ph, y + amp * 0.4, 700, y - amp * 0.3)
    d.cubicTo(880, y - amp * 0.8, 1000, y, W + 100, y - amp * 0.2); d.lineTo(W + 100, H); d.close()
    c.drawPath(d, P(col))


def sheep(c, x, y, s, t, ph, wool=(238, 230, 214), head=(58, 46, 40), face=1):
    bob = math.sin(t * 3 + ph) * 3 * s
    c.save(); c.translate(x, y + bob); c.scale(s * face, s)
    for lx in (-30, -12, 14, 30):
        c.drawLine(lx, 20, lx + 2 * math.sin(t * 4 + ph + lx), 62, P(head, 1, stroke=7))
    c.drawOval(skia.Rect.MakeLTRB(-56, 40, 56, 72), P((0, 0, 0), 0.18, blur=8))
    for dx, dy, r in ((-30, 0, 30), (-6, -10, 34), (20, -2, 32), (36, 10, 24), (-36, 16, 22), (4, 14, 30)):
        c.drawCircle(dx, dy, r, P(wool))
    c.drawCircle(-6, -18, 26, P(tuple(min(255, v + 10) for v in wool)))
    c.save(); c.translate(56, -8 + math.sin(t * 2 + ph) * 4); c.rotate(18)
    c.drawOval(skia.Rect.MakeLTRB(-14, -20, 22, 16), P(head))
    c.drawOval(skia.Rect.MakeLTRB(-22, -22, -4, -10), P(head))
    c.restore(); c.restore()


def well(c, cx, cy, rx, t, wet=0.0):
    body = skia.Rect.MakeLTRB(cx - rx, cy - 30, cx + rx, cy + 170)
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear([skia.Point(cx - rx, 0), skia.Point(cx + rx, 0)],
                [skia.Color(150, 118, 84), skia.Color(220, 186, 140), skia.Color(130, 100, 70)], [0, 0.45, 1]))
    c.drawRect(body, p)
    for r_ in range(3):
        y = cy - 30 + r_ * 66
        c.drawLine(cx - rx, y, cx + rx, y, P((110, 84, 56), 0.7, stroke=4))
        for k in range(6):
            x = cx - rx + (k + 0.5 * (r_ % 2)) * rx / 3
            c.drawLine(x, y, x, y + 66, P((110, 84, 56), 0.5, stroke=3))
    c.drawOval(skia.Rect.MakeLTRB(cx - rx, cy - 70, cx + rx, cy + 10), P((40, 30, 24)))
    c.drawOval(skia.Rect.MakeLTRB(cx - rx, cy - 70, cx + rx, cy + 10), P((200, 170, 130), 1, stroke=12))
    for sx in (cx - rx + 24, cx + rx - 24):
        c.drawLine(sx, cy - 50, sx, cy - 360, P((96, 64, 40), 1, stroke=20))
    c.drawLine(cx - rx + 8, cy - 352, cx + rx - 8, cy - 352, P((110, 74, 46), 1, stroke=22))


def trough(c, x0, x1, y, fill):
    c.drawRect(skia.Rect.MakeLTRB(x0, y, x1, y + 70), P((120, 86, 56)))
    c.drawRect(skia.Rect.MakeLTRB(x0 + 12, y + 6, x1 - 12, y + 30), P((40, 30, 24)))
    if fill > 0:
        c.drawRect(skia.Rect.MakeLTRB(x0 + 12, y + 30 - 24 * fill, x1 - 12, y + 30), P((90, 170, 200), 0.95))
        c.drawLine(x0 + 14, y + 30 - 24 * fill, x1 - 14, y + 30 - 24 * fill, P((220, 245, 255), 0.7, stroke=3))


def staff(c, x, y, h, rgb=(84, 56, 34)):
    p = skia.Path(); p.moveTo(x, y); p.lineTo(x + 8, y - h); p.quadTo(x + 50, y - h - 50, x + 60, y - h + 10)
    c.drawPath(p, P(rgb, 1, stroke=10))


def footprints(c, t, t0, pts, every=0.28, col=(120, 82, 50)):
    for k, (x, y, s) in enumerate(pts):
        ft = t0 + k * every
        if t < ft:
            continue
        a = clamp((t - ft) / 0.2)
        c.save(); c.translate(x, y); c.scale(s, s)
        c.drawOval(skia.Rect.MakeXYWH(-12, -30, 24, 40), P(col, 0.8 * a))
        c.drawOval(skia.Rect.MakeXYWH(-9, 14, 18, 16), P(col, 0.8 * a))
        c.restore()


# ------------------------------------------------------------- scenes
def s1_arrive(c, t, u):
    sky_day(c, (150, 120, 150), (255, 200, 140))
    radial(c, 760, 760, 420, (255, 220, 160), 0.6)
    c.drawCircle(760, 760, 90, P((255, 238, 200)))
    c.save(); cam(c, 1 + 0.15 * ease(u), 0, 60 * u, 0.5)
    dune_line(c, 1000, 60, (196, 140, 100))
    well(c, 560, 1020, 70, t)
    palm(c, 470, 1010, 220, (120, 80, 60), t, 1); palm(c, 680, 1000, 180, (120, 80, 60), t, 2)
    c.restore()
    c.save(); cam(c, 1 + 0.15 * ease(u), 0, 60 * u, 1.0)
    dune_line(c, 1180, 90, (226, 172, 116), 60)
    dune_line(c, 1420, 120, (204, 150, 96), -80)
    v = ease(u)
    footprints(c, t, 0.6, [(400 + 40 * math.sin(k), 1880 - k * 62, 1.3 - k * 0.07) for k in range(12)], every=0.25, col=(150, 100, 60))
    light(c, 470 + 20 * math.sin(v * 3), 1820 - 700 * v, 60 - 20 * v, t, 1.0)
    c.restore()
    a = clamp((3.8 - t) / 0.6) * clamp(t / 0.5)
    if a > 0:
        lin(c, (0, 0, W, 700), [(0, (10, 6, 4, int(235 * a))), (1, (10, 6, 4, 0))])
        star_orn(c, 540, 300, 58, t, a)
        text(c, "STORIES OF THE PROPHETS", 540, 420, 42, TF_SANS, GOLD, a, 0.24)
        text(c, "PROPHET MUSA  ·  PART 3", 540, 510, 92, TF_COND, CREAM, a, 0.06)
    lab(c, "AL-QASAS 28:23", t, 3.7, B[1] + 0.2)


FLOCK = [(np.random.default_rng(9).uniform(-60, 520), np.random.default_rng(10 + k).uniform(1280, 1560), k) for k in range(16)]


def s2_crowd(c, t, u):
    sky_day(c)
    ground(c, 1050)
    c.save(); cam(c, 1.05 - 0.05 * ease(u), -40 * u, 0, 1.0)
    dune_line(c, 1060, 50, (230, 190, 130))
    well(c, 420, 1240, 130, t)
    r = np.random.default_rng(12)
    for k in range(18):           # the shepherds' big flock crowds the well
        x = r.uniform(60, 540); y = r.uniform(1340, 1640)
        sheep(c, x + math.sin(t * 0.8 + k) * 10, y, 0.85 + (y - 1340) / 900, t, k, face=1 if k % 3 else -1)
    for k, x in enumerate((120, 280, 470)):
        staff(c, x, 1380 + 40 * k, 380)
    # two small flocks held back, apart on the right, with two staffs
    held = clamp((t - wt(2, "women")) / 0.8)
    radial(c, 900, 1540, 300, (255, 236, 180), 0.5 * held, sy=0.6)
    for k, (x, y) in enumerate(((850, 1500), (980, 1540), (880, 1630), (1010, 1660))):
        sheep(c, x, y, 0.9, t, k + 30, wool=(246, 240, 228), face=-1)
    staff(c, 770, 1430, 420, (110, 74, 46)); staff(c, 1040, 1460, 420, (110, 74, 46))
    lx = 680 + 40 * ease(clamp((t - L[3]) / 1.0))
    light(c, lx, 1290, 50, t, 1.0)
    c.restore()
    lab(c, "AL-QASAS 28:23", t, B[1] + 0.3, B[2] + 0.2)


def s3_water(c, t, u):
    sky_day(c, (110, 160, 214), (250, 226, 180))
    ground(c, 1000)
    c.save(); cam(c, 1.08, 0, 30 * u, 1.0)
    well(c, 330, 1150, 130, t)
    pour = clamp((t - L[5] - 0.2) / 1.6)
    bx, by = 520, 1080 - 30 * math.sin(pour * math.pi)
    c.save(); c.translate(bx, by); c.rotate(-40 * pour)
    c.drawRect(skia.Rect.MakeXYWH(-40, -50, 80, 70), P((110, 72, 40))); c.restore()
    if 0 < pour < 1:
        for k in range(14):
            yy = by + 20 + k * 22 + (t * 400) % 22
            c.drawCircle(bx + 30 + math.sin(k) * 6, yy, 7, P((140, 200, 230), 0.8))
    trough(c, 450, 960, 1400, pour)
    for k, x in enumerate((520, 660, 800, 920)):
        sheep(c, x, 1330 + (k % 2) * 30, 0.95, t, k, face=-1 if k % 2 else 1)
    light(c, 420, 1000, 46, t, 1.0)
    motes(c, t, (255, 240, 200), a=0.35)
    c.restore()
    lab(c, "AL-QASAS 28:24", t, B[2] + 0.3, B[3] + 0.2)


def tree(c, x, y, t, s=1.0, col=(54, 70, 40)):
    c.drawLine(x, y, x - 10 * s, y - 330 * s, P((84, 58, 36), 1, stroke=34 * s))
    c.drawLine(x - 10 * s, y - 280 * s, x - 160 * s, y - 420 * s, P((84, 58, 36), 1, stroke=18 * s))
    c.drawLine(x - 10 * s, y - 300 * s, x + 150 * s, y - 430 * s, P((84, 58, 36), 1, stroke=18 * s))
    sw = math.sin(t * 0.9) * 6
    for dx, dy, rx, ry in ((-200, -450, 230, 70), (40, -480, 260, 80), (220, -440, 200, 60), (-60, -520, 200, 60)):
        c.drawOval(skia.Rect.MakeLTRB(x + (dx - rx + sw) * s, y + (dy - ry) * s, x + (dx + rx + sw) * s, y + (dy + ry) * s), P(col))


def s4_shade(c, t, u):
    sky_day(c, (230, 150, 100), (255, 214, 160))
    ground(c, 1100, (210, 160, 104), (140, 96, 60))
    c.save(); cam(c, 1 + 0.12 * ease(u), 0, -40 * u, 1.0)
    c.drawOval(skia.Rect.MakeLTRB(200, 1300, 900, 1440), P((60, 40, 24), 0.45, blur=24))
    tree(c, 560, 1360, t, 1.25)
    pray = clamp((t - wt(6, "prayed")) / 0.8)
    light(c, 560, 1260 + 25 * pray, 52, t, 0.7 + 0.25 * math.sin(t * 1.5) * pray + 0.2 * pray)
    if pray > 0:
        rp = skia.Path(); rp.moveTo(500, 0); rp.lineTo(620, 0); rp.lineTo(680, 1250); rp.lineTo(440, 1250); rp.close()
        c.drawPath(rp, P((255, 236, 190), 0.12 * pray, blend=skia.BlendMode.kScreen))
    motes(c, t, a=0.4)
    c.restore()
    lab(c, "AL-QASAS 28:24", t, B[3] + 0.3, B[4] + 0.2)


def s5_invite(c, t, u):
    sky_day(c, (226, 150, 110), (255, 220, 170))
    ground(c, 1100, (214, 164, 108), (150, 104, 64))
    c.save(); cam(c, 1.1 - 0.1 * ease(u), 0, 0, 1.0)
    c.drawOval(skia.Rect.MakeLTRB(150, 1250, 850, 1400), P((60, 40, 24), 0.4, blur=24))
    tree(c, 440, 1330, t, 1.1)
    light(c, 440, 1230, 50, t, 1.0)
    pts = [(960 - k * 45, 1800 - k * 40 + (16 if k % 2 else -16), 0.9 - k * 0.03) for k in range(11)]
    footprints(c, t, L[7] + 0.3, pts, every=0.3, col=(130, 88, 54))
    inv = clamp((t - L[8]) / 0.6)
    if inv > 0:
        c.drawLine(560, 1300, 980, 1100, P((255, 220, 150), 0.25 * inv, stroke=4))
        radial(c, 1000, 1080, 260, (255, 200, 120), 0.45 * inv)
    c.restore()
    lab(c, "AL-QASAS 28:25", t, B[4] + 0.3, B[5] + 0.2)


def s6_tent(c, t, u):
    lin(c, (0, 0, W, 1150), [(0, (34, 30, 70)), (0.65, (150, 80, 90)), (1, (240, 140, 90))])
    stars(c, t, 0.6, ymax=600)
    ground(c, 1150, (120, 80, 60), (40, 28, 26))
    c.save(); cam(c, 1 + 0.1 * ease(u), 0, -40 * u, 1.0)
    tent = skia.Path(); tent.moveTo(160, 1420); tent.lineTo(330, 900); tent.lineTo(540, 840); tent.lineTo(750, 900); tent.lineTo(920, 1420); tent.close()
    c.drawPath(tent, P((96, 54, 40)))
    for k in range(6):
        c.drawLine(230 + k * 125, 1420, 330 + k * 85, 900, P((70, 38, 30), 0.6, stroke=6))
    door = skia.Path(); door.moveTo(440, 1420); door.lineTo(540, 1050); door.lineTo(640, 1420); door.close()
    fl = 0.85 + 0.15 * math.sin(t * 9)
    radial(c, 540, 1300, 520 * fl, (255, 170, 80), 0.45)
    c.drawPath(door, P((255, 196, 110)))
    for lx in (200, 880):
        c.drawLine(lx, 1440, lx, 1260, P((60, 40, 30), 1, stroke=8))
        radial(c, lx, 1250, 140, (255, 160, 70), 0.5 * fl); c.drawCircle(lx, 1250, 12, P((255, 230, 170)))
    light(c, 540, 1520, 48, t, 1.0)
    for k, x in enumerate((140, 940)):
        sheep(c, x, 1600, 0.8, t, k, wool=(200, 180, 160))
    c.restore()
    s_ = clamp((t - wt(10, "strong")) / 0.4) * clamp((B[6] + 0.2 - t) / 0.4)
    if s_ > 0:
        text(c, "STRONG", 540, 420, 130, TF_COND, GOLD, s_, 0.1)
        text(c, "&  TRUSTWORTHY", 540, 540, 92, TF_COND, CREAM, s_ * clamp((t - wt(10, "trustworthy")) / 0.4), 0.1)
        lab(c, "AL-QASAS 28:26", t, wt(10, "strong"), B[6] + 0.2, y=640)
    else:
        lab(c, "AL-QASAS 28:25", t, B[5] + 0.3, wt(10, "strong") - 0.1)


def s7_years(c, t, u):
    lin(c, (0, 0, W, H), [(0, (10, 10, 26)), (1, (30, 22, 30))])
    stars(c, t, 0.7, ymax=1900)
    t8 = wt(11, "eight")
    for k in range(10):
        ang = math.pi * (0.15 + 0.7 * k / 9)
        x = 540 - math.cos(ang) * 400; y = 1260 - math.sin(ang) * 420
        on = clamp((t - (t8 - 0.6 + k * 0.16)) / 0.25) if k < 8 else 0.35 * clamp((t - t8 - 1.2) / 0.4)
        lamp = skia.Path(); lamp.moveTo(x - 34, y + 20); lamp.cubicTo(x - 34, y - 10, x + 34, y - 10, x + 34, y + 20); lamp.close()
        c.drawPath(lamp, P((150, 90, 50)))
        if on > 0:
            radial(c, x, y - 20, 120, (255, 170, 70), 0.5 * on)
            fp = skia.Path(); fp.moveTo(x - 9, y); fp.quadTo(x, y - 52 * on, x + 9, y); fp.close()
            c.drawPath(fp, P((255, 210, 120), on))
    light(c, 540, 1180, 60, t, 1.0)
    a = clamp((t - t8) / 0.4)
    if a > 0:
        text(c, "8 YEARS", 540, 1460, 130, TF_COND, GOLD, a, 0.08)
    a2 = clamp((t - wt(11, "agreed")) / 0.4)
    if a2 > 0:
        text(c, "AGREED  ·  ALLAH IS WITNESS", 540, 1560, 40, TF_SANS, CREAM, a2, 0.2)
    lab(c, "AL-QASAS 28:27-28", t, B[6] + 0.3, B[7] + 0.2)


def s8_fire(c, t, u):
    lin(c, (0, 0, W, H), [(0, (4, 6, 18)), (0.6, (16, 16, 40)), (1, (10, 8, 16))])
    stars(c, t, 1.0, ymax=1000)
    c.save(); cam(c, 1 + 0.25 * ease(clamp((t - B[7]) / 3.5)), 0, 120 * u, 0.8)
    m = skia.Path(); m.moveTo(-100, 1500); m.lineTo(260, 1050); m.lineTo(420, 1120); m.lineTo(600, 760); m.lineTo(780, 1000); m.lineTo(940, 920); m.lineTo(W + 100, 1300); m.lineTo(W + 100, H); m.lineTo(-100, H); m.close()
    c.drawPath(m, P((22, 18, 30)))
    fl = 0.8 + 0.2 * math.sin(t * 12) + 0.1 * math.sin(t * 7.7)
    ig = clamp((t - wt(12, "fire")) / 0.8)
    radial(c, 600, 760, 700 * fl * (0.4 + 0.6 * ig), (255, 140, 50), 0.55 * max(0.25, ig))
    for k in range(5):
        h_ = (150 + 60 * (k % 3)) * fl * (0.5 + 0.5 * ig)
        fp = skia.Path(); x = 560 + k * 20
        fp.moveTo(x - 40, 790); fp.quadTo(x - 14 + 16 * math.sin(t * 9 + k), 790 - h_, x, 780 - h_ * 1.2); fp.quadTo(x + 40, 790 - h_ * 0.5, x + 36, 790); fp.close()
        c.drawPath(fp, P((255, 190 - k * 20, 80), 0.9))
    c.restore()
    light(c, 540, 1700, 46, t, 0.9)
    tf = wt(13, "Follow")
    d = ease(clamp((t - tf + 0.6) / 0.8))
    if d > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), P((6, 6, 16), 0.72 * d))
        star_orn(c, 540, 900, 70, t, d)
        text(c, "PART 4", 540, 1170 + 30 * (1 - d), 230, TF_COND, GOLD, d, 0.05)
        f = skia.Font(TF_COND, 96)
        bw = sum(f.measureText(ch) + 0.06 * 96 for ch in "FOLLOW") + 50
        c.drawRect(skia.Rect.MakeXYWH(540 - bw / 2, 1232, bw * ease(clamp((t - tf) / 0.35)), 100), P(GOLD, d))
        text(c, "FOLLOW", 540, 1315, 96, TF_COND, (30, 22, 14), d * clamp((t - tf - 0.1) / 0.3), 0.06)
        text(c, "THE FIRE ON THE MOUNTAIN  ·  COMING NEXT", 540, 1420, 34, TF_SANS, CREAM, d * clamp((t - tf - 0.4) / 0.4), 0.2)
    else:
        lab(c, "AL-QASAS 28:29", t, wt(12, "fire"), tf - 0.5)


SCENES = [s1_arrive, s2_crowd, s3_water, s4_shade, s5_invite, s6_tent, s7_years, s8_fire]


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
    k = min(clamp(t / 0.5), clamp((DUR - t) / 0.6))
    img = img * K.VIG * k + K.GRAIN[int(t * FPS) % 6]
    return np.clip(img, 0, 255).astype(np.uint8)


def render_range(f0, f1, out):
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for n in range(f0, f1):
        enc.stdin.write(frame(n / FPS).tobytes())
    enc.stdin.close(); enc.wait()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--probe", default=""); ap.add_argument("--out", default="")
    a = ap.parse_args()
    if a.probe:
        from PIL import Image
        d = ROOT / "out/probe"; d.mkdir(parents=True, exist_ok=True)
        for ts in a.probe.split(","):
            Image.fromarray(frame(float(ts))).save(d / f"p{float(ts):06.2f}.png")
        print("probes done")
    if a.out:
        from multiprocessing import Process
        N = int(math.ceil(DUR * FPS)); k = 2
        cuts = [N * i // k for i in range(k + 1)]
        parts = [str(ROOT / f"out/part{i}.mp4") for i in range(k)]
        ps = [Process(target=render_range, args=(cuts[i], cuts[i + 1], parts[i])) for i in range(k)]
        t0 = time.time(); [p.start() for p in ps]; [p.join() for p in ps]
        lst = ROOT / "out/parts.txt"; lst.write_text("".join(f"file '{p}'\n" for p in parts))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(ROOT / a.out)], check=True)
        print(f"wrote {a.out} ({N} frames, {time.time() - t0:.0f}s)")
