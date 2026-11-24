"""Sirah Shorts Special: The Man Allah Spoke To (Jabir and his father after Uhud). No person is drawn, and the Prophet
(peace be upon him) is not shown at all, not even as light. Only places and objects: Uhud, a home, a lamp, palms, a book.
  python3 paint_special-man-allah-spoke-to.py --probe 2,7,...      python3 paint_musa-part7.py --out out/paint.mp4
"""
import argparse, json, math, pathlib, subprocess, sys, time
import numpy as np
import skia

ROOT = pathlib.Path(__file__).parent
sys.path.insert(0, str(ROOT.parents[1] / "engine" / "core"))
import paint as K
from paint import palm, P, lin, radial, text, light, motes, stars, star_orn, cam, clamp, ease, W, H, FPS, GOLD, CREAM, TF_COND, TF_SANS

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
def uhud(c, base, shade=1.0, px=0, col=(120, 62, 44)):
    """Mount Uhud: a long ridge of reddish rock."""
    cl = tuple(int(v * shade) for v in col)
    p = skia.Path(); p.moveTo(-100, base)
    pts = [(-100, base - 260), (80, base - 380), (220, base - 330), (360, base - 520), (520, base - 470),
           (660, base - 600), (820, base - 430), (960, base - 480), (1180, base - 300)]
    p.lineTo(*pts[0])
    for k in range(1, len(pts)):
        x0, y0 = pts[k - 1]; x1, y1 = pts[k]
        p.quadTo((x0 + x1) / 2 + px, min(y0, y1) - 30, x1 + px, y1)
    p.lineTo(1180, base); p.close()
    c.drawPath(p, P(cl))
    for k in range(7):
        x = 120 + k * 140 + px
        q = skia.Path(); q.moveTo(x, base - 300 - (k % 3) * 60); q.lineTo(x + 40, base - 120); q.lineTo(x - 10, base - 60)
        c.drawPath(q, P(tuple(int(v * 0.75) for v in cl), 0.6, stroke=6))


def house(c, cx, base, s, lamp=1.0, t=0.0, shade=1.0, windows=0.0):
    """A simple mud-brick house of Madinah with a palm-frond roof and a lit doorway."""
    w = 380 * s; h = 300 * s
    cl = tuple(int(v * shade) for v in (150, 108, 72))
    c.drawRect(skia.Rect.MakeLTRB(cx - w / 2, base - h, cx + w / 2, base), P(cl))
    c.drawRect(skia.Rect.MakeLTRB(cx - w / 2 - 20 * s, base - h - 26 * s, cx + w / 2 + 20 * s, base - h), P(tuple(int(v * 0.6) for v in cl)))
    for k in range(9):
        x = cx - w / 2 + k * w / 8
        c.drawLine(x, base - h - 26 * s, x + 6 * s, base - h - 44 * s, P((90, 70, 40), shade, stroke=5 * s))
    dw = 90 * s; dh = 170 * s
    door = skia.Rect.MakeLTRB(cx - dw / 2, base - dh, cx + dw / 2, base)
    c.drawRect(door, P((40, 24, 16)))
    if lamp > 0:
        fl = 0.85 + 0.15 * math.sin(t * 9) * math.sin(t * 5.3)
        c.drawRect(door, P((255, 170, 80), 0.55 * lamp * fl))
        radial(c, cx, base - dh * 0.5, 160 * s, (255, 180, 90), 0.5 * lamp * fl)
    if windows > 0:
        for sx in (-1, 1):
            r = skia.Rect.MakeXYWH(cx + sx * 120 * s - 30 * s, base - 220 * s, 60 * s, 50 * s)
            c.drawRect(r, P((255, 190, 100), 0.8 * windows))
            radial(c, r.centerX(), r.centerY(), 80 * s, (255, 190, 100), 0.35 * windows)


def oil_lamp(c, x, y, s, t, a=1.0, flame=1.0):
    """A small clay oil lamp with a flickering flame."""
    c.save(); c.translate(x, y); c.scale(s, s)
    p = skia.Path(); p.moveTo(-90, 0); p.quadTo(-80, 50, 0, 52); p.quadTo(90, 50, 110, -6); p.lineTo(150, -22); p.quadTo(110, -30, 60, -20)
    p.quadTo(0, -40, -60, -20); p.close()
    c.drawPath(p, P((150, 92, 52), a)); c.drawPath(p, P((96, 56, 30), a, stroke=4))
    c.drawOval(skia.Rect.MakeLTRB(-30, -34, 30, -14), P((70, 40, 22), a))
    if flame > 0:
        fl = 1 + 0.12 * math.sin(t * 11) + 0.08 * math.sin(t * 17)
        radial(c, 150, -70, 200, (255, 180, 90), 0.55 * a * flame)
        f = skia.Path(); f.moveTo(140, -24); f.quadTo(120, -70 * fl, 150, -120 * fl); f.quadTo(176, -70 * fl, 160, -24); f.close()
        c.drawPath(f, P((255, 200, 110), a * flame))
        g = skia.Path(); g.moveTo(146, -26); g.quadTo(138, -56 * fl, 151, -84 * fl); g.quadTo(164, -56 * fl, 156, -26); g.close()
        c.drawPath(g, P((255, 248, 220), a * flame))
    c.restore()


def veil(c, t, open_=0.0, a=1.0):
    """Two great soft curtains of light-filtered cloth (a veil), drifting."""
    for side in (-1, 1):
        for k in range(7):
            x0 = 540 + side * (40 + k * 80 + 420 * ease(open_))
            p = skia.Path(); p.moveTo(x0, -40)
            for j in range(1, 21):
                y = -40 + j * 100
                p.lineTo(x0 + math.sin(j * 0.5 + t * 0.9 + k) * 26 + side * j * 4, y)
            c.drawPath(p, P((230, 200, 160) if k % 2 else (190, 150, 120), 0.28 * a, stroke=90))


def dates(c, cx, base, n, a=1.0):
    for k in range(n):
        x = cx - n * 18 + k * 36 + (k % 2) * 10; y = base - (k % 3) * 22
        c.drawOval(skia.Rect.MakeLTRB(x - 16, y - 24, x + 16, y + 6), P((110, 50, 30), a))
        c.drawOval(skia.Rect.MakeLTRB(x - 8, y - 18, x + 2, y - 8), P((200, 120, 70), 0.6 * a))


def book(c, cx, cy, s, t, glow=1.0, turn=0.0):
    """An open book on a wooden stand (an object, no hands)."""
    c.save(); c.translate(cx, cy); c.scale(s, s)
    st = skia.Path(); st.moveTo(-260, 80); st.lineTo(0, 200); st.lineTo(260, 80); st.lineTo(260, 110); st.lineTo(0, 230); st.lineTo(-260, 110); st.close()
    c.drawPath(st, P((110, 70, 40)))
    c.drawLine(-120, 170, 120, 330, P((90, 56, 30), 1, stroke=18)); c.drawLine(120, 170, -120, 330, P((90, 56, 30), 1, stroke=18))
    radial(c, 0, 0, 420, (255, 220, 150), 0.45 * glow)
    for side in (-1, 1):
        p = skia.Path(); p.moveTo(0, 60); p.quadTo(side * 120, 10, side * 250, 30); p.lineTo(side * 250, -150); p.quadTo(side * 120, -170, 0, -120); p.close()
        c.drawPath(p, P((246, 232, 200))); c.drawPath(p, P((170, 130, 80), 1, stroke=4))
        for k in range(6):
            y = -110 + k * 26
            c.drawLine(side * 30, y + 6, side * 220, y - 8 + k * 2, P((150, 120, 80), 0.6, stroke=4))
    c.restore()


def sky(c, t, top, mid, bot, y1=1250):
    lin(c, (0, 0, W, y1), [(0, top), (0.6, mid), (1, bot)])


B = [0.0, L[2] - 0.15, L[4] - 0.15, L[5] - 0.15, L[6] - 0.15, L[8] - 0.15, L[9] - 0.15, L[11] - 0.15, DUR]
XF = 0.45
lab = K.label


# ------------------------------------------------------------- scenes
def s1_veil(c, t, u):
    lin(c, (0, 0, W, H), [(0, (8, 8, 26)), (0.5, (40, 30, 60)), (1, (90, 60, 50))])
    stars(c, t, 0.9, ymax=1900)
    op = clamp((t - wt(1, "But")) / 1.6)
    radial(c, 540, 980, 300 + 500 * op, (255, 226, 170), 0.15 + 0.35 * op)
    c.save(); cam(c, 1.06 + 0.1 * ease(u), 0, 0, 1.0)
    veil(c, t, 0.15 + 0.6 * op, 1.0)
    c.restore()
    motes(c, t, (255, 230, 180), a=0.5)
    a = clamp((3.2 - t) / 0.6)
    if a > 0:
        lin(c, (0, 0, W, 640), [(0, (6, 6, 14, int(225 * a))), (1, (6, 6, 14, 0))])
        star_orn(c, 540, 290, 50, t, a)
        text(c, "SIRAH SHORTS SPECIAL", 540, 400, 40, TF_SANS, GOLD, a, 0.24)
        text(c, "THE MAN ALLAH SPOKE TO", 540, 490, 76, TF_COND, CREAM, a, 0.05)
    b = clamp((t - 3.3) / 0.4)
    if b > 0:
        text(c, "NO VEIL", 540, 560, 150, TF_COND, GOLD, b * clamp((t - wt(1, "directly")) / 0.3), 0.08)
        text(c, "BEHIND A VEIL", 540, 560, 120, TF_COND, CREAM, b * clamp((wt(1, "directly") - t) / 0.3), 0.06)
    lab(c, "JAMI AT-TIRMIDHI 3010", t, 3.3, B[1] + 0.2)


def s2_uhud(c, t, u):
    dusk = clamp((t - L[3] + 0.3) / 1.2)
    sky(c, t, (60 - int(40 * dusk), 40, 70), (190 - int(90 * dusk), 100, 80), (240 - int(80 * dusk), 160, 110))
    radial(c, 760, 900, 260, (255, 200, 140), 0.5 * (1 - dusk))
    c.save(); cam(c, 1.02 + 0.08 * ease(u), -30 * u, 0, 0.4)
    uhud(c, 1300, 0.9 - 0.3 * dusk)
    c.restore()
    lin(c, (0, 1250, W, H), [(0, (130, 92, 60)), (1, (50, 34, 26))])
    c.save(); cam(c, 1.04 + 0.12 * ease(u), 0, 30 * u, 1.0)
    for k, x in enumerate((90, 980)):
        palm(c, x, 1600, 640, (40, 30, 24), t, k)
    house(c, 540, 1620, 1.1, lamp=0.4 + 0.6 * dusk, t=t, shade=0.85 - 0.3 * dusk)
    dates(c, 330, 1740, 7, clamp((t - wt(3, "debts")) / 0.5))
    c.restore()
    a = clamp((t - wt(2, "Uhud") + 0.2) / 0.4) * clamp((wt(2, "His") - 0.1 - t) / 0.3)
    if a > 0:
        text(c, "AFTER", 540, 470, 90, TF_COND, CREAM, a, 0.06)
        text(c, "UHUD", 540, 610, 160, TF_COND, GOLD, a, 0.08)
    b = clamp((t - wt(2, "martyred")) / 0.4) * clamp((L[3] - 0.1 - t) / 0.3)
    if b > 0:
        text(c, "HIS FATHER", 540, 470, 100, TF_COND, CREAM, b, 0.06)
        text(c, "MARTYRED", 540, 610, 150, TF_COND, GOLD, b, 0.08)
    d = clamp((t - wt(3, "family")) / 0.4)
    if d > 0:
        text(c, "A FAMILY", 540, 470, 110, TF_COND, CREAM, d, 0.06)
        text(c, "AND DEBTS", 540, 610, 140, TF_COND, GOLD, d, 0.08)
    lab(c, "SUNAN IBN MAJAH 190", t, B[1] + 0.3, B[2] + 0.2)


def s3_news(c, t, u):
    sky(c, t, (70, 90, 150), (230, 170, 130), (255, 220, 160))
    rise = ease(clamp((t - B[2]) / 3.0))
    radial(c, 540, 1180 - 160 * rise, 380, (255, 230, 170), 0.8)
    c.drawCircle(540, 1220 - 160 * rise, 90, P((255, 244, 214)))
    c.save(); cam(c, 1.02 + 0.08 * ease(u), 0, 0, 0.4)
    uhud(c, 1300, 0.55, col=(140, 80, 60))
    c.restore()
    lin(c, (0, 1250, W, H), [(0, (150, 110, 70)), (1, (70, 48, 34))])
    c.save(); cam(c, 1.05 + 0.1 * ease(u), 0, 30 * u, 1.0)
    for k, x in enumerate((60, 260, 820, 1020)):
        palm(c, x, 1700 + (k % 2) * 60, 700 - (k % 2) * 120, (36, 28, 22), t, k * 1.3)
    house(c, 540, 1640, 0.9, lamp=0.25, t=t, shade=0.9)
    c.restore()
    motes(c, t, (255, 236, 190), a=0.45)
    a = clamp((t - wt(4, "glad")) / 0.4)
    if a > 0:
        text(c, "GLAD NEWS", 540, 500, 150, TF_COND, GOLD, a, 0.08)
        text(c, "OF YOUR FATHER", 540, 610, 70, TF_COND, CREAM, a, 0.08)
    lab(c, "JAMI AT-TIRMIDHI 3010", t, B[2] + 0.3, B[3] + 0.2)


def s4_ask(c, t, u):
    lin(c, (0, 0, W, H), [(0, (6, 10, 30)), (0.5, (24, 30, 70)), (1, (60, 50, 80))])
    stars(c, t, 1.0, ymax=1900)
    c.save(); cam(c, 1.0 + 0.14 * ease(u), 0, 0, 1.0)
    for k in range(5):
        y = 1300 + k * 120
        p = skia.Path(); p.moveTo(-60, y)
        for j in range(26):
            p.lineTo(-60 + j * 50, y + math.sin(j * 0.45 + t * 0.6 + k) * 40)
        c.drawPath(p, P((200, 210, 255) if k % 2 else (255, 220, 170), 0.12, stroke=60))
    c.restore()
    motes(c, t, (220, 230, 255), a=0.6)
    a = clamp((t - wt(5, "directly")) / 0.4) * clamp((wt(5, "Ask") - 0.1 - t) / 0.3)
    if a > 0:
        text(c, "ALLAH SPOKE", 540, 500, 120, TF_COND, CREAM, a, 0.06)
        text(c, "TO HIM DIRECTLY", 540, 610, 80, TF_COND, GOLD, a, 0.06)
    b = clamp((t - wt(5, "Ask")) / 0.4)
    if b > 0:
        text(c, "“ASK OF ME”", 540, 560, 150, TF_COND, GOLD, b, 0.08)
    lab(c, "SUNAN IBN MAJAH 190", t, B[3] + 0.3, B[4] + 0.2)


def s5_return(c, t, u):
    t7 = L[7]
    n = clamp((t - t7 + 0.3) / 1.0)
    sky(c, t, (14, 12, 34), (70 - int(30 * n), 40, 60), (140 - int(60 * n), 80, 70))
    stars(c, t, 0.5 + 0.5 * n, ymax=1000)
    c.save(); cam(c, 1.02 + 0.08 * ease(u), 0, 0, 0.4)
    uhud(c, 1320, 0.45)
    c.restore()
    lin(c, (0, 1300, W, H), [(0, (70, 50, 40)), (1, (20, 14, 12))])
    c.save(); cam(c, 1.06 + 0.14 * ease(u), 0, 20 * u, 1.0)
    oil_lamp(c, 470, 1560, 1.6, t, 1.0, 1.0)
    c.restore()
    motes(c, t, (255, 210, 150), a=0.4)
    a = clamp((t - wt(6, "life")) / 0.4) * clamp((t7 - 0.1 - t) / 0.3)
    if a > 0:
        text(c, "LIFE AGAIN", 540, 470, 120, TF_COND, CREAM, a, 0.06)
        text(c, "A SECOND TIME", 540, 600, 110, TF_COND, GOLD, a * clamp((t - wt(6, "second")) / 0.3), 0.06)
    b = clamp((t - wt(7, "decreed")) / 0.4)
    if b > 0:
        text(c, "IT IS DECREED", 540, 470, 100, TF_COND, CREAM, b, 0.06)
        text(c, "THEY WILL NOT RETURN", 540, 600, 90, TF_COND, GOLD, b * clamp((t - wt(7, "They")) / 0.3), 0.05)
    lab(c, "JAMI AT-TIRMIDHI 3010", t, B[4] + 0.3, B[5] + 0.2)


def s6_tell(c, t, u):
    sky(c, t, (10, 12, 34), (34, 32, 70), (70, 56, 80))
    stars(c, t, 0.9, ymax=1100)
    c.drawCircle(860, 860, 54, P((240, 236, 220), 0.9)); radial(c, 860, 860, 200, (220, 230, 255), 0.3)
    lin(c, (0, 1250, W, H), [(0, (60, 44, 36)), (1, (18, 12, 12))])
    c.save(); cam(c, 1.03 + 0.12 * ease(u), 0, 30 * u, 1.0)
    for k, x in enumerate((110, 970)):
        palm(c, x, 1650, 620, (20, 18, 22), t, k)
    w = clamp((t - wt(8, "left")) / 0.8)
    house(c, 540, 1660, 1.15, lamp=0.7, t=t, shade=0.5, windows=0.3 + 0.7 * w)
    c.restore()
    a = clamp((t - wt(8, "tell")) / 0.4)
    if a > 0:
        text(c, "TELL THOSE", 540, 470, 120, TF_COND, CREAM, a, 0.06)
        text(c, "I LEFT BEHIND", 540, 600, 120, TF_COND, GOLD, a, 0.06)
    lab(c, "SUNAN IBN MAJAH 190", t, B[5] + 0.3, B[6] + 0.2)


def s7_verse(c, t, u):
    t10 = L[10]
    dawn = clamp((t - B[6]) / 4.0)
    sky(c, t, (30 + int(50 * dawn), 40 + int(60 * dawn), 90 + int(60 * dawn)), (120 + int(100 * dawn), 110 + int(60 * dawn), 130), (230, 190, 140), y1=1300)
    lin(c, (0, 1300, W, H), [(0, (110, 76, 50)), (1, (40, 26, 20))])
    c.save(); cam(c, 1.03 + 0.12 * ease(u), 0, 30 * u, 1.0)
    book(c, 540, 1380, 1.25, t, glow=0.6 + 0.4 * dawn)
    c.restore()
    motes(c, t, (255, 236, 190), a=0.55)
    a = clamp((t - wt(9, "Never")) / 0.4) * clamp((t10 - 0.1 - t) / 0.3)
    if a > 0:
        text(c, "NEVER THINK", 540, 470, 120, TF_COND, CREAM, a, 0.06)
        text(c, "THEY ARE DEAD", 540, 600, 120, TF_COND, GOLD, a * clamp((t - wt(9, "dead")) / 0.3), 0.06)
    b = clamp((t - wt(10, "alive")) / 0.4)
    if b > 0:
        text(c, "THEY ARE ALIVE", 540, 470, 120, TF_COND, GOLD, b, 0.06)
        text(c, "WITH THEIR LORD", 540, 600, 90, TF_COND, CREAM, b, 0.06)
    lab(c, "AL IMRAN 3:169", t, B[6] + 0.3, B[7] + 0.2)


def s8_end(c, t, u):
    sky(c, t, (40, 60, 110), (220, 170, 130), (255, 220, 160), y1=1300)
    radial(c, 540, 1150, 420, (255, 230, 170), 0.7)
    c.save(); cam(c, 1.02 + 0.08 * ease(u), 0, 0, 0.4)
    uhud(c, 1320, 0.6, col=(150, 90, 64))
    c.restore()
    lin(c, (0, 1300, W, H), [(0, (150, 110, 70)), (1, (60, 40, 30))])
    c.save(); cam(c, 1.04 + 0.1 * ease(u), 0, 20 * u, 1.0)
    for k, x in enumerate((80, 300, 780, 1000)):
        palm(c, x, 1720, 620 - (k % 2) * 100, (40, 30, 24), t, k)
    c.restore()
    motes(c, t, (255, 236, 190), a=0.5)
    tf = wt(11, "Follow")
    a = clamp((t - wt(11, "grief")) / 0.4) * clamp((wt(11, "Next") - 0.1 - t) / 0.3)
    if a > 0:
        text(c, "SOME GRIEF", 540, 470, 120, TF_COND, CREAM, a, 0.06)
        text(c, "HIDES GLAD NEWS", 540, 600, 110, TF_COND, GOLD, a, 0.06)
    d = ease(clamp((t - wt(11, "Next") + 0.2) / 0.8))
    if d > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), P((6, 8, 14), 0.72 * d))
        star_orn(c, 540, 900, 70, t, d)
        text(c, "PART 8", 540, 1170 + 30 * (1 - d), 230, TF_COND, GOLD, d, 0.05)
        f = skia.Font(TF_COND, 96)
        bw = sum(f.measureText(ch) + 0.06 * 96 for ch in "FOLLOW") + 50
        c.drawRect(skia.Rect.MakeXYWH(540 - bw / 2, 1232, bw * ease(clamp((t - tf) / 0.35)), 100), P(GOLD, d))
        text(c, "FOLLOW", 540, 1315, 96, TF_COND, (30, 22, 14), d * clamp((t - tf - 0.1) / 0.3), 0.06)
        text(c, "MUSA  ·  THE SEA SPLITS  ·  NEXT", 540, 1420, 34, TF_SANS, CREAM, d * clamp((t - tf - 0.3) / 0.4), 0.2)
    else:
        lab(c, "SIRAH SHORTS SPECIAL", t, B[7] + 0.3, wt(11, "Next") - 0.3)


SCENES = [s1_veil, s2_uhud, s3_news, s4_ask, s5_return, s6_tell, s7_verse, s8_end]


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
