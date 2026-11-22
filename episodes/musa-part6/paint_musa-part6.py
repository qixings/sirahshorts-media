"""Musa Part 6, illustrated: The Magicians. No people drawn; Musa (AS) is a glowing light. The magicians are
shown only through their ropes, staffs and lamps; Pharaoh only through his palace and an empty throne.
  python3 paint_musa-part6.py --probe 2,7,...      python3 paint_musa-part6.py --out out/paint.mp4
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


B = [0.0, L[2] - 0.15, L[4] - 0.15, L[5] - 0.15, L[6] - 0.15, L[7] - 0.15, L[9] - 0.15, L[11] - 0.15, DUR]
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


# ------------------------------------------------------------- new pieces
ROPES = [(150 + k * 72 + (k % 3) * 18, 1430 + (k % 4) * 70 + (k % 2) * 25, 150 + (k % 5) * 30, k * 1.3) for k in range(12)]


def rope(c, x, y, length, t, ph, a=1.0, wig=1.0, rgb=(150, 108, 64)):
    """A rope (or a thin staff) lying on the sand; wig > 0 makes it seem to move."""
    if a <= 0:
        return
    n = 22; pts = []
    for k in range(n):
        f = k / (n - 1)
        pts.append((x - length / 2 + f * length, y + math.sin(f * 7 + t * 6 + ph) * 18 * wig * (0.3 + f)))
    p = skia.Path(); p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    c.drawPath(p, P((40, 26, 16), 0.45 * a, stroke=16))
    c.drawPath(p, P(rgb, a, stroke=11))
    c.drawPath(p, P((210, 170, 110), 0.5 * a, stroke=3))


def ropes(c, t, a=1.0, wig=1.0, eaten=0.0, cx=540, cy=1560):
    """All the ropes; 'eaten' pulls them toward (cx, cy) and shrinks them away."""
    for k, (x, y, ln, ph) in enumerate(ROPES):
        e = ease(clamp(eaten * 1.6 - k * 0.05))
        xx = x + (cx - x) * e; yy = y + (cy - y) * e
        rope(c, xx, yy, ln * (1 - e), t, ph, a * (1 - e), wig, (150 + (k % 3) * 14, 104 + (k % 2) * 12, 60))


def arena(c, t, u, sky=((40, 70, 120), (200, 170, 140), (250, 210, 150))):
    lin(c, (0, 0, W, 1300), [(0, sky[0]), (0.65, sky[1]), (1, sky[2])])
    radial(c, 860, 860, 260, (255, 240, 200), 0.7)
    c.drawCircle(860, 860, 70, P((255, 248, 225)))
    c.save(); cam(c, 1 + 0.08 * ease(u), 0, 0, 0.35)
    palace(c, 300, 1250, 0.55, 0.7, glow=0.2, t=t)
    c.restore()
    lin(c, (0, 1250, W, H), [(0, (196, 150, 98)), (1, (120, 82, 52))])
    # banners on poles around the festival ground
    for k, x in enumerate((70, 250, 830, 1010)):
        c.drawLine(x, 1360, x, 900, P((90, 60, 40), 1, stroke=10))
        fl = skia.Path(); sw = math.sin(t * 2.2 + k) * 24
        fl.moveTo(x, 910); fl.quadTo(x + 70, 930 + sw, x + 140, 920 + sw * 1.4); fl.lineTo(x + 140, 1010 + sw); fl.quadTo(x + 70, 1020 + sw, x, 1000); fl.close()
        c.drawPath(fl, P((170, 50, 40) if k % 2 else (200, 150, 60)))


def sparkles(c, t, a, n=40, seed=3, region=(0, 1250, W, 1800), rgb=(220, 200, 255)):
    rng = np.random.default_rng(seed)
    for k in range(n):
        x = rng.uniform(region[0], region[2]); y = rng.uniform(region[1], region[3]); ph = rng.uniform(0, 6.3)
        tw = 0.5 + 0.5 * math.sin(t * 5 + ph)
        c.drawCircle(x + math.sin(t + ph) * 20, y - (t * 30 + ph * 40) % 200, 2 + 3 * tw, P(rgb, a * tw, blend=skia.BlendMode.kScreen))


def coins(c, x, y, t, a=1.0):
    radial(c, x, y - 40, 260, (255, 200, 90), 0.5 * a)
    c.drawRect(skia.Rect.MakeLTRB(x - 170, y - 60, x + 170, y + 90), P((110, 66, 30), a))
    c.drawRect(skia.Rect.MakeLTRB(x - 170, y - 60, x + 170, y - 30), P((196, 150, 74), a))
    for k in range(14):
        cx = x - 140 + (k % 7) * 47; cy = y - 70 - (k // 7) * 26 + math.sin(t * 3 + k) * 2
        c.drawOval(skia.Rect.MakeLTRB(cx - 24, cy - 12, cx + 24, cy + 12), P((240, 200, 90), a))
        c.drawOval(skia.Rect.MakeLTRB(cx - 24, cy - 12, cx + 24, cy + 12), P((150, 110, 40), a, stroke=3))


# ------------------------------------------------------------- scenes
def s1_ropes(c, t, u):
    arena(c, t, u, ((70, 40, 70), (190, 110, 90), (240, 170, 110)))
    c.save(); cam(c, 1.05 + 0.12 * ease(u), 0, 40 * u, 1.0)
    ropes(c, t, 1.0, 1.0)
    sparkles(c, t, 0.6)
    fear = clamp((t - wt(1, "fear")) / 0.6)
    light(c, 540, 1300, 50, t, 1.0 - 0.4 * fear)
    c.restore()
    a = clamp((3.4 - t) / 0.6)
    if a > 0:
        lin(c, (0, 0, W, 700), [(0, (6, 6, 14, int(235 * a))), (1, (6, 6, 14, 0))])
        star_orn(c, 540, 300, 58, t, a)
        text(c, "STORIES OF THE PROPHETS", 540, 420, 42, TF_SANS, GOLD, a, 0.24)
        text(c, "PROPHET MUSA  ·  PART 6", 540, 510, 92, TF_COND, CREAM, a, 0.06)
    lab(c, "TAHA 20:66-67", t, 3.4, B[1] + 0.2)


def s2_festival(c, t, u):
    arena(c, t, u)
    c.save(); cam(c, 1 + 0.1 * ease(u), 0, 30 * u, 1.0)
    # rows of lamps: the gathered crowd is shown only by their lamps
    for r in range(3):
        for k in range(11):
            x = 60 + k * 96 + (r % 2) * 48; y = 1330 + r * 60
            radial(c, x, y, 34, (255, 190, 100), 0.5 + 0.15 * math.sin(t * 4 + k + r))
            c.drawCircle(x, y, 6, P((255, 230, 170)))
    light(c, 540, 1680, 46, t, 1.0)
    t3 = L[3]
    g = clamp((t - wt(3, "reward")) / 0.6)
    if g > 0:
        coins(c, 540, 1560, t, g)
    c.restore()
    a = clamp((t - wt(2, "festival")) / 0.4) * clamp((t3 - 0.1 - t) / 0.4)
    if a > 0:
        text(c, "THE DAY OF THE FESTIVAL", 540, 520, 96, TF_COND, CREAM, a, 0.06)
    b = clamp((t - wt(3, "close")) / 0.4)
    if b > 0:
        text(c, "A REWARD", 540, 520, 140, TF_COND, GOLD, b, 0.08)
    lab(c, "TAHA 20:59" if t < t3 else "AL-A'RAF 7:113-114", t, B[1] + 0.3, B[2] + 0.2)


def s3_spell(c, t, u):
    arena(c, t, u, ((60, 30, 80), (150, 80, 120), (220, 140, 120)))
    c.drawRect(skia.Rect.MakeWH(W, H), P((40, 10, 60), 0.3))
    c.save(); cam(c, 1.1 + 0.1 * ease(u), 0, 60 * u, 1.0)
    th = wt(4, "Their")
    drop = ease(clamp((t - th + 0.6) / 0.8))
    for k, (x, y, ln, ph) in enumerate(ROPES):
        yy = y - 700 * (1 - drop)
        rope(c, x, yy, ln, t, ph, drop, 0.4 + 0.6 * drop)
    sp = clamp((t - wt(4, "bewitched")) / 0.6)
    for k in range(3):
        rr = (t * 160 + k * 200) % 600
        c.drawCircle(540, 1500, 100 + rr, P((200, 160, 255), 0.25 * sp * (1 - rr / 600), stroke=6, blend=skia.BlendMode.kScreen))
    sparkles(c, t, 0.9 * sp, 70, 9)
    light(c, 540, 1250, 48, t, 0.8)
    c.restore()
    a = clamp((t - L[4] - 0.3) / 0.4) * clamp((th - 0.1 - t) / 0.4)
    if a > 0:
        text(c, "YOU THROW FIRST", 540, 520, 120, TF_COND, CREAM, a, 0.06)
    b = clamp((t - wt(4, "bewitched")) / 0.4)
    if b > 0:
        text(c, "IT BEWITCHED", 540, 460, 110, TF_COND, (230, 210, 255), b, 0.06)
        text(c, "THEIR EYES", 540, 570, 110, TF_COND, CREAM, b, 0.06)
    lab(c, "AL-A'RAF 7:115-116", t, B[2] + 0.3, B[3] + 0.2)


def s4_dontfear(c, t, u):
    lin(c, (0, 0, W, H), [(0, (6, 8, 24)), (0.6, (24, 24, 56)), (1, (50, 34, 46))])
    stars(c, t, 1.0, ymax=1300)
    c.save(); cam(c, 1 + 0.1 * ease(u), 0, -20 * u, 1.0)
    lin(c, (0, 1500, W, H), [(0, (80, 58, 46)), (1, (30, 20, 18))])
    rs = clamp((t - wt(5, "fear")) / 1.2)
    radial(c, 540, 700, 300 + 900 * rs, (255, 226, 160), 0.15 + 0.35 * rs)
    for k in range(12):
        ang = k * math.pi / 6 + t * 0.1
        if rs > 0:
            c.drawLine(540, 700, 540 + math.cos(ang) * 1400 * rs, 700 + math.sin(ang) * 1400 * rs,
                       P((255, 240, 200), 0.12 * rs, stroke=10, blend=skia.BlendMode.kScreen))
    light(c, 540, 1400, 50, t, 0.7 + 0.5 * rs)
    st = clamp((t - wt(5, "Throw")) / 0.5)
    staff(c, 610, 1520, 380, 8, a=0.4 + 0.6 * st)
    if st > 0:
        radial(c, 640, 1340, 160, (255, 230, 160), 0.5 * st)
    c.restore()
    a = clamp((t - wt(5, "fear")) / 0.4) * clamp((wt(5, "Throw") - t) / 0.3)
    if a > 0:
        text(c, "DO NOT FEAR", 540, 1100, 130, TF_COND, GOLD, a, 0.08)
    b = clamp((t - wt(5, "Throw")) / 0.4)
    if b > 0:
        text(c, "THROW", 540, 1100, 150, TF_COND, GOLD, b, 0.08)
    lab(c, "TAHA 20:68-69", t, B[3] + 0.3, B[4] + 0.2)


def s5_swallow(c, t, u):
    arena(c, t, u, ((60, 30, 60), (170, 90, 80), (240, 160, 100)))
    c.save(); cam(c, 1.08 + 0.1 * ease(u), 0, 40 * u, 1.0)
    t_throw = wt(6, "threw"); t_sw = wt(6, "swallowed")
    eat = clamp((t - t_sw + 0.3) / 1.6)
    ropes(c, t, 1.0, 1.0 - 0.5 * eat, eaten=eat, cx=620, cy=1600)
    if t < t_throw + 0.1:
        staff(c, 480, 1380, 400, 8)
    elif t < t_throw + 0.7:
        f = ease(clamp((t - t_throw - 0.1) / 0.5))
        staff(c, 480 + 80 * f, 1380 + 220 * f, 400 - 120 * f, 8 + 75 * f)
    else:
        m = ease(clamp((t - t_throw - 0.7) / 0.5))
        radial(c, 620, 1600, 300, (255, 220, 140), 0.5 * (1 - m) + 0.15)
        serpent(c, 620, 1600, 420 + 260 * eat, t, m, 0.6 + 0.4 * m)
    light(c, 360, 1260, 46, t, 1.0)
    c.restore()
    a = clamp((t - t_sw) / 0.4)
    if a > 0:
        text(c, "IT SWALLOWED", 540, 470, 120, TF_COND, GOLD, a, 0.08)
        text(c, "WHAT THEY FAKED", 540, 590, 100, TF_COND, CREAM, a, 0.06)
    lab(c, "AL-A'RAF 7:117", t, B[4] + 0.3, B[5] + 0.2)


def s6_prostrate(c, t, u):
    lin(c, (0, 0, W, 1300), [(0, (30, 60, 110)), (0.6, (200, 180, 160)), (1, (255, 220, 170))])
    radial(c, 540, 1250, 700, (255, 236, 190), 0.6)
    c.save(); cam(c, 1 + 0.12 * ease(u), 0, 30 * u, 1.0)
    lin(c, (0, 1250, W, H), [(0, (200, 156, 104)), (1, (120, 82, 52))])
    # the magicians' staffs laid down flat in rows, their lamps lowered to the ground
    fall = clamp((t - wt(7, "fell")) / 1.0)
    for r in range(2):
        for k in range(7):
            x = 120 + k * 140 + r * 70; y = 1420 + r * 130
            ang = -70 * (1 - ease(clamp(fall * 1.4 - k * 0.06)))
            c.save(); c.translate(x, y); c.rotate(ang)
            c.drawLine(-60, 0, 60, 0, P((110, 74, 46), 1, stroke=10)); c.restore()
            ly = y - 70 * (1 - ease(fall)) - 24
            radial(c, x, ly, 30, (255, 200, 120), 0.6)
            c.drawCircle(x, ly, 5, P((255, 236, 190)))
    light(c, 540, 1180, 52, t, 1.1)
    c.restore()
    motes(c, t, (255, 230, 180), a=0.4)
    a = clamp((t - wt(7, "truth")) / 0.4) * clamp((L[8] - 0.1 - t) / 0.4)
    if a > 0:
        text(c, "THE TRUTH", 540, 470, 140, TF_COND, GOLD, a, 0.08)
        text(c, "STOOD CLEAR", 540, 590, 100, TF_COND, CREAM, a, 0.06)
    b = clamp((t - wt(8, "worlds")) / 0.4)
    if b > 0:
        text(c, "LORD OF", 540, 470, 100, TF_COND, CREAM, b, 0.06)
        text(c, "THE WORLDS", 540, 600, 140, TF_COND, GOLD, b, 0.08)
    lab(c, "AL-A'RAF 7:118-122", t, B[5] + 0.3, B[6] + 0.2)


def s7_threat(c, t, u):
    t10 = L[10]
    calm = clamp((t - t10) / 1.0)
    hall(c, t, u, warm=(120, 30, 24))
    c.save(); cam(c, 1.15 - 0.1 * ease(u), 0, 0, 1.0)
    throne(c, 540, 1300, 0.85, 0.9)
    c.restore()
    c.drawRect(skia.Rect.MakeWH(W, H), P((40, 0, 0), 0.3 * (1 - calm)))
    # the believers' lamps stay lit, steady before the throne
    for k in range(7):
        x = 180 + k * 120
        radial(c, x, 1620, 40, (255, 210, 140), 0.55 + 0.4 * calm)
        c.drawCircle(x, 1620, 6, P((255, 240, 200)))
    a = clamp((t - wt(9, "permission")) / 0.4) * clamp((t10 - 0.1 - t) / 0.4)
    if a > 0:
        lin(c, (0, 300, W, 700), [(0, (10, 0, 0, 0)), (0.5, (10, 0, 0, int(170 * a))), (1, (10, 0, 0, 0))])
        text(c, "BEFORE I GAVE", 540, 470, 110, TF_COND, CREAM, a, 0.08)
        text(c, "PERMISSION?", 540, 590, 120, TF_COND, (255, 140, 100), a, 0.08)
    b = clamp((t - wt(10, "worldly")) / 0.4)
    if b > 0:
        text(c, "ONLY THIS", 540, 470, 110, TF_COND, CREAM, b, 0.06)
        text(c, "WORLDLY LIFE", 540, 590, 120, TF_COND, GOLD, b, 0.08)
    lab(c, "AL-A'RAF 7:123-124" if t < t10 else "TAHA 20:72", t, B[6] + 0.3, B[7] + 0.2)


def s8_end(c, t, u):
    lin(c, (0, 0, W, 1250), [(0, (12, 14, 40)), (0.7, (90, 60, 90)), (1, (220, 140, 90))])
    stars(c, t, 1 - 0.6 * u, ymax=900)
    lin(c, (0, 1250, W, H), [(0, (90, 54, 36)), (1, (30, 18, 16))])
    c.save(); cam(c, 1 + 0.12 * ease(u), 0, 0, 0.6)
    palace(c, 540, 1250, 1.0, 0.5, glow=0.2, t=t)
    c.restore()
    w = ease(u)
    for k in range(7):
        x = 180 + k * 120; y = 1560 - 160 * w - 10 * math.sin(t + k)
        radial(c, x, y, 40, (255, 210, 140), 0.7)
        c.drawCircle(x, y, 6, P((255, 240, 200)))
    motes(c, t, (255, 220, 160), a=0.35)
    tf = wt(12, "Follow")
    a = clamp((t - wt(11, "patience")) / 0.4) * clamp((tf - 0.7 - t) / 0.4)
    if a > 0:
        text(c, "POUR UPON US", 540, 450, 110, TF_COND, CREAM, a, 0.06)
        text(c, "PATIENCE", 540, 580, 150, TF_COND, GOLD, a, 0.08)
    d = ease(clamp((t - tf + 0.6) / 0.8))
    if d > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), P((10, 6, 10), 0.72 * d))
        star_orn(c, 540, 900, 70, t, d)
        text(c, "PART 7", 540, 1170 + 30 * (1 - d), 230, TF_COND, GOLD, d, 0.05)
        f = skia.Font(TF_COND, 96)
        bw = sum(f.measureText(ch) + 0.06 * 96 for ch in "FOLLOW") + 50
        c.drawRect(skia.Rect.MakeXYWH(540 - bw / 2, 1232, bw * ease(clamp((t - tf) / 0.35)), 100), P(GOLD, d))
        text(c, "FOLLOW", 540, 1315, 96, TF_COND, (30, 22, 14), d * clamp((t - tf - 0.1) / 0.3), 0.06)
        text(c, "THE SIGNS  ·  COMING NEXT", 540, 1420, 34, TF_SANS, CREAM, d * clamp((t - tf - 0.4) / 0.4), 0.2)
    else:
        lab(c, "AL-A'RAF 7:126", t, B[7] + 0.3, tf - 0.5)


SCENES = [s1_ropes, s2_festival, s3_spell, s4_dontfear, s5_swallow, s6_prostrate, s7_threat, s8_end]


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
