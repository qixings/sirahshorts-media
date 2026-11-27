"""Musa Part 9, illustrated: The Journey to Khidr. No people drawn; Musa (AS) is a glowing light. His young companion is
shown only by a second staff, a basket and footprints; the servant of Allah only by a green cloak on a rock under rays of light.
  python3 paint_musa-part9.py --probe 2,7,...      python3 paint_musa-part9.py --out out/paint.mp4
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


B = [0.0, L[2] - 0.15, L[3] - 0.15, L[5] - 0.15, L[7] - 0.15, L[8] - 0.15, L[10] - 0.15, L[12] - 0.15, DUR]
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


# ------------------------------------------------------------- scenes
def s1_hook(c, t, u):
    sky(c, (30, 44, 80), (140, 150, 170), (240, 210, 170))
    radial(c, 540, HZ, 520, (255, 226, 170), 0.5)
    c.save(); cam(c, 1.04 + 0.1 * ease(u), 0, 20 * u, 0.6)
    two_seas(c, t)
    c.restore()
    # the fish leaping in a bright arc over the meeting of the seas
    ph = (t * 0.45) % 1.0
    fx = 300 + 480 * ph; fy = 1420 - math.sin(ph * math.pi) * 380
    c.save(); cam(c, 1.05 + 0.12 * ease(u), 0, 30 * u, 1.0)
    for k in range(12):
        q = ph - k * 0.02
        if q > 0:
            radial(c, 300 + 480 * q, 1420 - math.sin(q * math.pi) * 380, 30 - 2 * k, (220, 240, 255), 0.4 * (1 - k / 12))
    fish(c, fx, fy, 1.3, ang=math.degrees(math.atan2(-math.cos(ph * math.pi) * 380 * math.pi, 480)), t=t)
    shore(c, 1640, cols=((200, 170, 120), (110, 84, 56)))
    light(c, 760, 1600, 44, t, 1.0)
    c.restore()
    a = clamp((3.2 - t) / 0.6)
    if a > 0:
        lin(c, (0, 0, W, 640), [(0, (6, 6, 14, int(225 * a))), (1, (6, 6, 14, 0))])
        star_orn(c, 540, 290, 50, t, a)
        text(c, "STORIES OF THE PROPHETS", 540, 400, 40, TF_SANS, GOLD, a, 0.24)
        text(c, "PROPHET MUSA  ·  PART 9", 540, 490, 86, TF_COND, CREAM, a, 0.06)
    b = clamp((t - 3.3) / 0.4)
    if b > 0:
        text(c, "A LOST FISH", 540, 400, 130, TF_COND, CREAM, b, 0.06)
        text(c, "SHOWS THE WAY", 540, 520, 120, TF_COND, GOLD, b, 0.08)
    lab(c, "AL-KAHF 18:64-65", t, 3.3, B[1] + 0.2)


def s2_journey(c, t, u):
    sky(c, (60, 90, 150), (200, 190, 170), (250, 220, 170))
    c.drawCircle(840, 830, 60, P((255, 246, 220))); radial(c, 840, 830, 300, (255, 230, 180), 0.4)
    c.save(); cam(c, 1.02 + 0.08 * ease(u), -40 * u, 0, 0.5)
    sea(c, t, HZ, 1.0, deep=(24, 60, 90), shallow=(110, 150, 170), glint=(255, 245, 220))
    c.restore()
    c.save(); cam(c, 1.05 + 0.14 * ease(u), -60 * u, 30 * u, 1.0)
    shore(c, 1300, cols=((214, 184, 132), (150, 112, 72)))
    prog = ease(u)
    footprints(c, 160, 1880, 160 + 700 * prog, 1880 - 420 * prog, 14, 1.0, pairs=2)
    hx, hy = 160 + 700 * prog, 1880 - 420 * prog
    light(c, hx + 60, hy - 120, 42, t, 1.0)
    # the companion: only his staff and the basket he carries, beside the light
    staff(c, hx - 70, hy + 40, 300, ang=-6 + 3 * math.sin(t * 2), a=0.95)
    basket(c, hx - 130, hy - 40, 50, t)
    c.restore()
    bigtext(c, t, wt(2, "two"), B[2] + 0.2, "WHERE THE", "TWO SEAS MEET")
    lab(c, "AL-KAHF 18:60", t, B[1] + 0.3, B[2] + 0.2)


def s3_rock(c, t, u):
    t4 = L[4]
    sky(c, (50, 40, 80), (200, 130, 110), (255, 190, 130))
    radial(c, 540, HZ, 520, (255, 200, 140), 0.6)
    c.save(); cam(c, 1.02 + 0.06 * ease(u), 0, 0, 0.5)
    two_seas(c, t)
    c.restore()
    c.save(); cam(c, 1.06 + 0.14 * ease(u), 0, 40 * u, 1.0)
    shore(c, 1500, cols=((190, 150, 110), (100, 74, 50)))
    rock(c, 360, 1640, 420, 300)
    staff(c, 560, 1650, 360, ang=12, a=1.0)
    staff(c, 610, 1660, 330, ang=18, a=1.0, rgb=(130, 94, 60))
    basket(c, 720, 1640, 70, t)
    light(c, 300, 1440, 40, t, 0.9)
    # the fish leaves the basket and takes its way into the sea, leaving a glowing tunnel in the water
    fp = clamp((t - t4 + 0.2) / 2.2)
    if fp > 0:
        x = 720 + (880 - 720) * fp; y = 1600 - math.sin(fp * math.pi) * 140 - 380 * fp
        for k in range(30):
            q = fp * k / 29
            qx = 720 + 160 * q; qy = 1600 - math.sin(q * math.pi) * 140 - 380 * q
            if q > 0.45:
                radial(c, qx, qy, 46, (200, 240, 255), 0.35)
        fish(c, x, y, 0.8, ang=-60 + 40 * fp, a=1.0 - clamp((fp - 0.85) / 0.15) * 0.6, t=t)
    c.restore()
    bigtext(c, t, wt(3, "forgot"), t4 - 0.1, "", "THEY FORGOT THE FISH", s2=110)
    bigtext(c, t, wt(4, "amazing"), B[3] + 0.2, "AN AMAZING", "WAY", s2=170)
    lab(c, "AL-KAHF 18:61", t, B[2] + 0.3, B[3] + 0.2)


def s4_back(c, t, u):
    t6 = L[6]
    sky(c, (90, 140, 200), (210, 220, 220), (250, 236, 200))
    c.drawCircle(860, 830, 70, P((255, 252, 235))); radial(c, 860, 830, 320, (255, 246, 210), 0.4)
    c.save(); cam(c, 1.02 + 0.06 * ease(u), 0, 0, 0.5)
    sea(c, t, HZ, 1.0, deep=(30, 70, 110), shallow=(130, 180, 200), glint=(255, 255, 240))
    c.restore()
    c.save(); cam(c, 1.05 + 0.12 * ease(u), 0, 30 * u, 1.0)
    shore(c, 1260, cols=((222, 196, 146), (160, 120, 80)))
    back = clamp((t - wt(6, "went")) / 3.0)
    footprints(c, 160, 1880, 860, 1460, 14, 1.0, pairs=2)
    # the empty basket, then the light turning back along its own footprints
    basket(c, 760, 1560, 60, t)
    hx = 860 - 700 * ease(back); hy = 1460 + 420 * ease(back)
    light(c, hx + 40, hy - 120, 42 + 6 * ease(back), t, 1.0)
    staff(c, hx - 60, hy + 20, 300, ang=-8, a=0.95)
    c.restore()
    bigtext(c, t, wt(5, "forgot"), t6 - 0.1, "“I FORGOT", "THE FISH!”", s1=110)
    bigtext(c, t, wt(6, "seeking"), B[4] + 0.2, "WHAT WE WERE", "SEEKING", s1=100, s2=160)
    lab(c, "AL-KAHF 18:62-64", t, B[3] + 0.3, B[4] + 0.2)


def s5_servant(c, t, u):
    g = ease(clamp((t - B[4]) / 1.6))
    sky(c, (40, 60, 110), (170, 190, 190), (250, 236, 200))
    c.save(); cam(c, 1.02 + 0.06 * ease(u), 0, 0, 0.5)
    two_seas(c, t)
    c.restore()
    c.save(); cam(c, 1.06 + 0.14 * ease(u), 0, 50 * u, 1.0)
    shore(c, 1460, cols=((210, 180, 130), (120, 90, 60)))
    rays(c, 420, 1560, g, t)
    rock(c, 420, 1640, 440, 280)
    cloak(c, 420, 1400, 1.0, t, g)
    motes(c, t, (220, 255, 220), a=0.5 * g)
    light(c, 840, 1560, 42, t, 1.0)
    c.restore()
    bigtext(c, t, wt(7, "servant"), wt(7, "mercy") - 0.1, "A SERVANT", "OF ALLAH", s2=150)
    bigtext(c, t, wt(7, "mercy"), B[5] + 0.2, "MERCY AND", "KNOWLEDGE", s1=100, s2=150, c2=(170, 230, 170))
    lab(c, "AL-KAHF 18:65", t, B[4] + 0.3, B[5] + 0.2)


def dialogue_bg(c, t, u, warm=0.0):
    sky(c, (30 + int(40 * warm), 40, 80), (150, 140 + int(20 * warm), 150), (240, 210, 170))
    c.save(); cam(c, 1.02 + 0.05 * ease(u), 0, 0, 0.5)
    two_seas(c, t)
    c.restore()


def s6_ask(c, t, u):
    t9 = L[9]
    dialogue_bg(c, t, u)
    c.save(); cam(c, 1.1 + 0.12 * ease(u), -40 + 80 * ease(u), 60 * u, 1.0)
    shore(c, 1500, cols=((200, 170, 124), (110, 82, 54)))
    rock(c, 300, 1700, 380, 240)
    cloak(c, 300, 1480, 0.85, t, 1.0)
    light(c, 780, 1580, 48, t, 1.0 + 0.2 * math.sin(t * 2))
    c.restore()
    bigtext(c, t, wt(8, "teach"), t9 - 0.1, "“TEACH ME", "WHAT YOU WERE TAUGHT”", s1=120, s2=90)
    bigtext(c, t, wt(9, "never"), B[6] + 0.2, "“YOU WILL NEVER", "HAVE PATIENCE”", s1=100, s2=130, c2=(170, 230, 170))
    lab(c, "AL-KAHF 18:66-68", t, B[5] + 0.3, B[6] + 0.2)


def s7_patient(c, t, u):
    t11 = L[11]
    dialogue_bg(c, t, u, warm=1.0)
    c.save(); cam(c, 1.08 + 0.1 * ease(u), 40 - 80 * ease(u), 60 * u, 1.0)
    shore(c, 1500, cols=((206, 174, 126), (116, 86, 56)))
    rock(c, 760, 1700, 380, 240)
    cloak(c, 760, 1480, 0.85, t, 1.0)
    light(c, 300, 1580, 48, t, 1.1)
    for k in range(5):
        radial(c, 300, 1580, 120 + 80 * k + 30 * math.sin(t * 2 + k), (255, 220, 150), 0.06)
    c.restore()
    bigtext(c, t, wt(10, "Allah"), t11 - 0.1, "“IF ALLAH WILLS,", "I WILL BE PATIENT”", s1=100, s2=110)
    bigtext(c, t, wt(11, "nothing"), B[7] + 0.2, "“ASK ME", "ABOUT NOTHING”", s2=130, c2=(170, 230, 170))
    lab(c, "AL-KAHF 18:69-70", t, B[6] + 0.3, B[7] + 0.2)


def s8_boat(c, t, u):
    sky(c, (20, 24, 54), (110, 80, 110), (230, 150, 110))
    radial(c, 540, HZ, 500, (255, 180, 120), 0.5)
    c.save(); cam(c, 1.02 + 0.08 * ease(u), 0, 0, 0.5)
    sea(c, t, HZ, 1.0, deep=(20, 34, 60), shallow=(120, 100, 110), glint=(255, 200, 150))
    c.restore()
    c.save(); cam(c, 1.05 + 0.12 * ease(u), 0, 30 * u, 1.0)
    boat(c, 620, 1330, 1.0, t)
    shore(c, 1560, cols=((170, 130, 96), (80, 60, 44)))
    light(c, 360, 1560, 44, t, 1.0)
    cloak(c, 520, 1640, 0.6, t, 0.9)
    c.restore()
    tf = wt(12, "Follow")
    a = clamp((t - wt(12, "silent")) / 0.4) * clamp((tf - 0.7 - t) / 0.4)
    if a > 0:
        text(c, "MUSA COULD NOT", 540, 400, 110, TF_COND, CREAM, a, 0.06)
        text(c, "STAY SILENT", 540, 520, 140, TF_COND, GOLD, a, 0.08)
    d = ease(clamp((t - tf + 0.6) / 0.8))
    if d > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), P((6, 8, 14), 0.72 * d))
        star_orn(c, 540, 900, 70, t, d)
        text(c, "PART 10", 540, 1170 + 30 * (1 - d), 230, TF_COND, GOLD, d, 0.05)
        f = skia.Font(TF_COND, 96)
        bw = sum(f.measureText(ch) + 0.06 * 96 for ch in "FOLLOW") + 50
        c.drawRect(skia.Rect.MakeXYWH(540 - bw / 2, 1232, bw * ease(clamp((t - tf) / 0.35)), 100), P(GOLD, d))
        text(c, "FOLLOW", 540, 1315, 96, TF_COND, (30, 22, 14), d * clamp((t - tf - 0.1) / 0.3), 0.06)
        text(c, "THREE STRANGE ACTS  ·  COMING NEXT", 540, 1420, 34, TF_SANS, CREAM, d * clamp((t - tf - 0.4) / 0.4), 0.2)
    else:
        lab(c, "AL-KAHF 18:71", t, B[7] + 0.3, tf - 0.5)


SCENES = [s1_hook, s2_journey, s3_rock, s4_back, s5_servant, s6_ask, s7_patient, s8_boat]


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
