"""Musa Part 1, illustrated version: seven painted, animated scenes in a 9:16 frame.
Musa (AS) is shown only as a glowing oval of light; no people are drawn.

  python3 paint.py --probe 2,7,11 [--size 540]     stills into out/paint_probe/
  python3 paint.py --out out/paint.mp4               full render (2 workers)
"""
import argparse, json, math, os, pathlib, subprocess, sys, time
import numpy as np
import skia

ROOT = pathlib.Path(__file__).parent
TIM = json.loads((ROOT / "audio/timing.json").read_text())
SEG = TIM["segments"]
DUR = TIM["total_duration"]
FPS = 30
W, H = 1080, 1920
L = {s["id"]: s["start"] for s in SEG}
E = {s["id"]: s["end"] for s in SEG}


def word_t(i, word):
    s = next(x for x in SEG if x["id"] == i)
    words = s["vo"].split()
    tot = sum(len(w) for w in words); acc = 0
    for w in words:
        if w.lower().strip(".,:!?'") .startswith(word.lower()):
            return s["start"] + (s["end"] - s["start"]) * acc / tot
        acc += len(w)
    return s["start"]


BOUNDS = [0.0, L[2] - 0.15, L[3] - 0.15, L[4] - 0.15, L[5] - 0.15, L[6] - 0.15, L[7] - 0.2, DUR]
XF = 0.45   # crossfade

TF_COND = skia.Typeface.MakeFromFile(str(ROOT / "fonts/cond.ttf"))
TF_SANS = skia.Typeface.MakeFromFile("/usr/share/fonts/truetype/google-fonts/ofl/montserrat/Montserrat[wght].ttf")
GOLD = (222, 182, 96)
CREAM = (246, 238, 218)


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def ease(x):
    x = clamp(x); return x * x * (3 - 2 * x)


def col(rgb, a=1.0):
    return skia.Color4f(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255, a)


def P(rgb=(0, 0, 0), a=1.0, stroke=None, blur=None, blend=None, cap=None):
    p = skia.Paint(AntiAlias=True)
    p.setColor4f(col(rgb, clamp(a)))
    if stroke:
        p.setStyle(skia.Paint.kStroke_Style); p.setStrokeWidth(stroke)
        p.setStrokeCap(cap or skia.Paint.kRound_Cap)
    if blur:
        p.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
    if blend:
        p.setBlendMode(blend)
    return p


def lin(c, rect, stops, horizontal=False):
    x0, y0, x1, y1 = rect
    pts = [skia.Point(x0, y0), skia.Point(x1, y0) if horizontal else skia.Point(x0, y1)]
    cols = [skia.Color(*s[1]) for s in stops]
    pos = [s[0] for s in stops]
    p = skia.Paint(AntiAlias=True); p.setShader(skia.GradientShader.MakeLinear(pts, cols, pos))
    c.drawRect(skia.Rect.MakeLTRB(x0, y0, x1, y1), p)


def radial(c, x, y, r, rgb, a, sy=1.0, blend=skia.BlendMode.kScreen, falloff=(0, 0.35, 1)):
    if a <= 0 or r <= 0:
        return
    p = skia.Paint(AntiAlias=True)
    cols = [skia.Color(*rgb, int(255 * clamp(a))), skia.Color(*rgb, int(255 * clamp(a) * 0.45)), skia.Color(*rgb, 0)]
    p.setShader(skia.GradientShader.MakeRadial(skia.Point(0, 0), r, cols, list(falloff)))
    if blend:
        p.setBlendMode(blend)
    c.save(); c.translate(x, y); c.scale(1, sy); c.drawCircle(0, 0, r, p); c.restore()


def text(c, s, x, y, size, tf, rgb, a=1.0, track=0.0, align="center"):
    if a <= 0:
        return
    f = skia.Font(tf, size)
    ws = [f.measureText(ch) + track * size for ch in s]
    tot = sum(ws) - track * size
    cx = x - tot / 2 if align == "center" else x
    p = P(rgb, a)
    sh = P((0, 0, 0), 0.55 * a, blur=size * 0.08)
    for ch, w in zip(s, ws):
        c.drawString(ch, cx + 3, y + 5, f, sh); c.drawString(ch, cx, y, f, p); cx += w


def label(c, s, t, t0, t1, y=250):
    a = clamp((t - t0) / 0.4) * clamp((t1 - t) / 0.4)
    if a <= 0:
        return
    f = skia.Font(TF_SANS, 40)
    tw = sum(f.measureText(ch) + 0.2 * 40 for ch in s)
    r = skia.RRect.MakeRectXY(skia.Rect.MakeXYWH(540 - tw / 2 - 30, y - 52, tw + 52, 76), 38, 38)
    c.drawRRect(r, P((14, 12, 20), 0.55 * a))
    c.drawRRect(r, P(GOLD, 0.85 * a, stroke=2.5))
    text(c, s, 540, y, 40, TF_SANS, GOLD, a, 0.2)


# ------------------------------------------------------------- the light (Musa, AS)
def light(c, x, y, s, t, inten=1.0, sparkle=True):
    pulse = 1 + 0.06 * math.sin(t * 3.1)
    s *= pulse
    radial(c, x, y, s * 5.5, (255, 196, 110), 0.30 * inten)
    radial(c, x, y, s * 2.6, (255, 222, 160), 0.55 * inten, sy=1.25)
    c.save(); c.translate(x, y); c.scale(1, 1.38)
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeRadial(skia.Point(0, 0), s, [skia.Color(255, 255, 250, int(255 * min(1, inten))),
                skia.Color(255, 244, 205, int(235 * min(1, inten))), skia.Color(255, 214, 140, 0)], [0, 0.55, 1]))
    c.drawCircle(0, 0, s, p)
    c.restore()
    if sparkle:
        for k in range(9):
            ang = t * (0.7 + 0.08 * k) + k * 0.7
            rr = s * (2.1 + 0.4 * math.sin(t * 1.3 + k))
            px, py = x + math.cos(ang) * rr, y + math.sin(ang) * rr * 1.3
            tw = 0.5 + 0.5 * math.sin(t * 4 + k * 1.7)
            c.drawCircle(px, py, 2.2 + 2 * tw, P((255, 240, 200), 0.75 * tw * inten, blend=skia.BlendMode.kScreen))


# ------------------------------------------------------------- shared pieces
RNG = np.random.default_rng(7)
STARS = [(RNG.uniform(0, W), RNG.uniform(0, 1100), RNG.uniform(0.8, 2.6), RNG.uniform(0, 6.28)) for _ in range(230)]
MOTES = [(RNG.uniform(0, W), RNG.uniform(0, H), RNG.uniform(1.5, 4), RNG.uniform(0, 6.28), RNG.uniform(8, 25)) for _ in range(70)]


def stars(c, t, a=1.0, ymax=1100):
    for x, y, r, ph in STARS:
        if y > ymax:
            continue
        tw = 0.55 + 0.45 * math.sin(t * 2 + ph)
        c.drawCircle(x, y, r, P((255, 250, 235), a * tw))


def motes(c, t, rgb=(255, 220, 160), a=0.6, region=None):
    for x0, y0, r, ph, sp in MOTES:
        x = (x0 + math.sin(t * 0.5 + ph) * 40) % W
        y = (y0 - t * sp) % H
        if region and not (region[0] < x < region[2] and region[1] < y < region[3]):
            continue
        c.drawCircle(x, y, r, P(rgb, a * (0.5 + 0.5 * math.sin(t * 2 + ph)), blend=skia.BlendMode.kScreen))


def cam(c, zoom, px=0, py=0, depth=1.0):
    z = 1 + (zoom - 1) * depth
    c.translate(W / 2 + px * depth, H / 2 + py * depth); c.scale(z, z); c.translate(-W / 2, -H / 2)


def palm(c, x, y, h, rgb, t, ph=0):
    sway = math.sin(t * 0.9 + ph) * 6
    p = skia.Path(); p.moveTo(x, y); p.quadTo(x + h * 0.12, y - h * 0.5, x + sway, y - h)
    c.drawPath(p, P(rgb, 1, stroke=h * 0.045))
    tx, ty = x + sway, y - h
    for k in range(8):
        ang = -math.pi / 2 + (k - 3.5) * 0.42 + math.sin(t * 1.1 + k + ph) * 0.04
        L_ = h * 0.42
        ex, ey = tx + math.cos(ang) * L_, ty + math.sin(ang) * L_ * 0.55 + L_ * 0.35
        f = skia.Path(); f.moveTo(tx, ty); f.quadTo(tx + math.cos(ang) * L_ * 0.6, ty - L_ * 0.25, ex, ey)
        c.drawPath(f, P(rgb, 1, stroke=h * 0.03))


def basket(c, cx, cy, rx, t, glow=1.0, s_light=None, light_dy=0):
    ry = rx * 0.27; depth = rx * 0.78
    rim = skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry)
    c.drawOval(rim.makeOffset(8, depth * 0.9), P((0, 0, 0), 0.35, blur=18))
    c.drawOval(rim, P((52, 34, 18)))
    c.drawOval(rim.makeInset(rx * 0.22, ry * 0.3).makeOffset(0, ry * 0.12), P((128, 104, 76)))
    if s_light:
        light(c, cx, cy - ry * 0.2 - s_light * 0.55 + light_dy, s_light, t, glow)
    bowl = skia.Path()
    bowl.moveTo(cx - rx, cy)
    bowl.arcTo(rim, 180, -180, False)
    bowl.cubicTo(cx + rx * 0.95, cy + depth, cx - rx * 0.95, cy + depth, cx - rx, cy)
    bowl.close()
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear([skia.Point(cx - rx, 0), skia.Point(cx + rx, 0)],
                [skia.Color(96, 66, 34), skia.Color(176, 132, 72), skia.Color(84, 56, 30)], [0, 0.45, 1]))
    c.drawPath(bowl, p)
    c.save(); c.clipPath(bowl, skia.ClipOp.kIntersect, True)
    for k in range(1, 7):
        yy = cy + depth * k / 7.5
        c.drawLine(cx - rx, yy, cx + rx, yy, P((60, 40, 20), 0.55, stroke=3))
    for k in range(-12, 13):
        xx = cx + rx * k / 12
        c.drawLine(xx, cy, xx + 6, cy + depth, P((205, 160, 96), 0.35, stroke=3))
    c.restore()
    c.drawOval(rim, P((150, 108, 58), 1, stroke=rx * 0.07))
    c.drawOval(rim, P((210, 168, 100), 0.6, stroke=rx * 0.02))


def reeds(c, t, side, n, seed, base_y=H + 30, hmin=500, hmax=1000, rgb=(16, 24, 20), px=0):
    r = np.random.default_rng(seed)
    for k in range(n):
        x = (r.uniform(-60, 300) if side < 0 else r.uniform(W - 300, W + 60)) + px
        h = r.uniform(hmin, hmax); ph = r.uniform(0, 6.28); w = r.uniform(5, 11)
        bend = math.sin(t * 1.2 + ph) * 26 + side * -40
        p = skia.Path(); p.moveTo(x, base_y); p.quadTo(x + bend * 0.3, base_y - h * 0.6, x + bend, base_y - h)
        c.drawPath(p, P(rgb, 1, stroke=w))
        if k % 2 == 0:
            tx, ty = x + bend, base_y - h
            for j in range(9):
                ang = -math.pi / 2 + (j - 4) * 0.22
                c.drawLine(tx, ty, tx + math.cos(ang) * 70, ty + math.sin(ang) * 70 + 25, P(rgb, 1, stroke=2.5))


def water(c, top, t, a=1.0, rgb=(255, 210, 160), speed=30, rows=70, seed=3):
    r = np.random.default_rng(seed)
    for k in range(rows):
        y = top + (k / rows) ** 1.6 * (H - top)
        x = (r.uniform(0, W) + t * speed * (0.5 + k / rows)) % (W + 200) - 100
        ln = 30 + 140 * k / rows
        tw = 0.5 + 0.5 * math.sin(t * 3 + k)
        c.drawLine(x, y, x + ln, y, P(rgb, a * 0.35 * tw, stroke=1.5 + 3 * k / rows))


# ------------------------------------------------------------- scenes
def s1_night(c, t, u):
    lin(c, (0, 0, W, 1300), [(0, (5, 8, 24)), (0.65, (22, 24, 54)), (1, (70, 48, 62))])
    stars(c, t, 1.0)
    c.save(); cam(c, 1 + 0.08 * u, -30 * u, 0, 0.3)
    radial(c, 840, 760, 240, (220, 220, 255), 0.22)
    c.drawCircle(840, 760, 70, P((242, 236, 210)))
    c.drawCircle(868, 742, 62, P((18, 20, 46)))
    for bx, bh, bw in ((180, 260, 420), (520, 170, 280)):
        tri = skia.Path(); tri.moveTo(bx - bw / 2, 1290); tri.lineTo(bx, 1290 - bh); tri.lineTo(bx + bw / 2, 1290); tri.close()
        c.drawPath(tri, P((34, 30, 52)))
    c.restore()
    c.save(); cam(c, 1 + 0.08 * u, -30 * u, 0, 0.65)
    r = np.random.default_rng(11)
    x = -40
    while x < W + 40:
        w = r.uniform(70, 150); h = r.uniform(90, 230)
        c.drawRect(skia.Rect.MakeXYWH(x, 1420 - h, w, h + 200), P((20, 17, 32)))
        for _ in range(int(r.integers(0, 3))):
            wx, wy = x + r.uniform(12, w - 26), 1420 - h + r.uniform(20, h - 30)
            fl = 0.65 + 0.35 * math.sin(t * 6 + wx)
            c.drawRect(skia.Rect.MakeXYWH(wx, wy, 14, 20), P((255, 170, 80), 0.75 * fl))
            radial(c, wx + 7, wy + 10, 40, (255, 150, 60), 0.25 * fl)
        x += w + r.uniform(-10, 8)
    py = skia.Path()     # palace pylon on the right
    py.moveTo(700, 1440); py.lineTo(740, 1030); py.lineTo(900, 1030); py.lineTo(940, 1440)
    py.moveTo(940, 1440); py.lineTo(960, 1120); py.lineTo(1120, 1120); py.lineTo(1140, 1440)
    c.drawPath(py, P((14, 12, 26)))
    c.restore()
    c.save(); cam(c, 1 + 0.08 * u, -30 * u, 0, 1.0)
    lin(c, (0, 1440, W, H), [(0, (16, 13, 22)), (1, (6, 5, 10))])
    for k in range(7):
        ph = k * 1.7
        x = (k * 190 + t * (60 if k % 2 else -50)) % (W + 300) - 150
        y = 1520 + (k % 3) * 70
        fl = 0.8 + 0.2 * math.sin(t * 13 + ph) + 0.1 * math.sin(t * 7.3 + ph)
        radial(c, x, y - 40, 170, (255, 140, 50), 0.35 * fl)
        c.drawLine(x, y + 60, x, y - 30, P((40, 28, 20), 1, stroke=8))
        fp = skia.Path(); fp.moveTo(x - 14, y - 30); fp.quadTo(x - 4 + 6 * math.sin(t * 9 + ph), y - 95 * fl, x + 2, y - 105 * fl)
        fp.quadTo(x + 18, y - 60, x + 14, y - 30); fp.close()
        c.drawPath(fp, P((255, 180, 70), 0.95)); c.drawCircle(x, y - 45, 9, P((255, 245, 200)))
    c.restore()
    a = clamp((3.9 - t) / 0.6) * clamp(t / 0.5)
    if a > 0:
        star_orn(c, 540, 300, 58, t, a)
        text(c, "STORIES OF THE PROPHETS", 540, 420, 42, TF_SANS, GOLD, a, 0.24)
        text(c, "PROPHET MUSA  ·  PART 1", 540, 510, 92, TF_COND, CREAM, a, 0.06)
    label(c, "PHARAOH'S DECREE  ·  AL-QASAS 28:4", t, 3.8, BOUNDS[1] + 0.2)


def s2_room(c, t, u):
    c.save(); cam(c, 1 + 0.12 * ease(u), 0, -60 * ease(u), 1.0)
    lin(c, (0, 0, W, 1380), [(0, (40, 26, 18)), (1, (82, 54, 34))])
    TEX.draw(c)
    win = skia.Path(); win.addRect(skia.Rect.MakeXYWH(640, 330, 300, 420)); win.addCircle(790, 330, 150)
    c.save(); c.clipPath(win, skia.ClipOp.kIntersect, True)
    lin(c, (600, 160, 980, 760), [(0, (6, 10, 30)), (1, (26, 30, 66))])
    for x, y, r, ph in STARS[:60]:
        c.drawCircle(640 + x * 0.28, 170 + y * 0.5, r * 0.8, P((255, 250, 230), 0.5 + 0.5 * math.sin(t * 2 + ph)))
    c.drawCircle(860, 300, 36, P((240, 234, 210)))
    c.restore()
    c.drawPath(win, P((50, 32, 20), 1, stroke=22))
    door = skia.Path(); door.addRect(skia.Rect.MakeXYWH(420, 1010, 240, 380)); door.addCircle(540, 1010, 120)
    c.drawPath(door, P((20, 13, 10)))
    lin(c, (0, 1380, W, H), [(0, (58, 38, 24)), (1, (24, 16, 12))])
    for jx, js in ((880, 1.0), (980, 0.75), (120, 0.85)):
        jar = skia.Path(); by = 1470
        jar.moveTo(jx - 30 * js, by - 230 * js); jar.lineTo(jx + 30 * js, by - 230 * js)
        jar.cubicTo(jx + 120 * js, by - 170 * js, jx + 110 * js, by, jx + 40 * js, by)
        jar.lineTo(jx - 40 * js, by); jar.cubicTo(jx - 110 * js, by, jx - 120 * js, by - 170 * js, jx - 30 * js, by - 230 * js); jar.close()
        jp = skia.Paint(AntiAlias=True)
        jp.setShader(skia.GradientShader.MakeLinear([skia.Point(jx - 110 * js, 0), skia.Point(jx + 110 * js, 0)],
                     [skia.Color(70, 34, 20), skia.Color(150, 82, 46), skia.Color(56, 28, 18)], [0, 0.35, 1]))
        c.drawPath(jar, jp)
    c.drawRect(skia.Rect.MakeXYWH(60, 900, 330, 26), P((60, 40, 24)))
    fl = 0.85 + 0.1 * math.sin(t * 11) + 0.06 * math.sin(t * 17.3)
    radial(c, 220, 820, 900 * fl, (255, 150, 60), 0.38)
    lamp = skia.Path(); lamp.moveTo(150, 900); lamp.cubicTo(150, 840, 300, 840, 300, 900); lamp.close()
    c.drawPath(lamp, P((150, 90, 50)))
    fp = skia.Path(); fp.moveTo(278, 868); fp.quadTo(282 + 6 * math.sin(t * 9), 820 - 30 * fl, 286, 800 - 26 * fl); fp.quadTo(300, 840, 294, 868); fp.close()
    c.drawPath(fp, P((255, 190, 80))); c.drawCircle(287, 856, 8, P((255, 250, 220)))
    rise = -20 * ease(clamp((t - word_t(2, "nurse")) / 1.2))
    basket(c, 540, 1330, 300, t, glow=1.1, s_light=80, light_dy=rise)
    motes(c, t, a=0.5)
    c.restore()
    label(c, "AL-QASAS 28:7", t, BOUNDS[1] + 0.3, BOUNDS[2] + 0.2)


def s3_nile(c, t, u):
    lin(c, (0, 0, W, 930), [(0, (36, 44, 92)), (0.55, (196, 120, 116)), (0.85, (250, 170, 120)), (1, (255, 210, 150))])
    c.save(); cam(c, 1 + 0.06 * u, 20 * u, 0, 0.3)
    radial(c, 700, 920, 420, (255, 200, 120), 0.6)
    c.drawCircle(700, 930, 95, P((255, 226, 170)))
    c.restore()
    c.save(); cam(c, 1 + 0.06 * u, 20 * u, 0, 0.5)
    c.drawRect(skia.Rect.MakeLTRB(-100, 905, W + 100, 950), P((70, 40, 48)))
    for k, x in enumerate((60, 150, 230, 860, 930, 1010)):
        palm(c, x, 935, 170 + 40 * (k % 3), (58, 32, 42), t, k)
    c.restore()
    lin(c, (0, 945, W, H), [(0, (232, 150, 120)), (0.25, (150, 96, 110)), (1, (22, 30, 58))])
    for k in range(40):     # sun column in the water
        y = 960 + k * 22; wob = math.sin(t * 4 + k * 0.9) * 30
        w_ = 180 * (1 - k / 45)
        c.drawLine(700 - w_ / 2 + wob, y, 700 + w_ / 2 + wob, y, P((255, 220, 160), 0.45 * (1 - k / 40), stroke=6))
    water(c, 960, t, 1.0, (255, 214, 170), speed=40)
    v = ease(u)
    bx, by, br = 330 + 260 * v, 1560 - 300 * v, 210 - 70 * v
    for k in range(3):
        ph = ((t * 0.6 + k / 3) % 1)
        rr = br * (1.1 + ph * 1.2)
        c.drawOval(skia.Rect.MakeLTRB(bx - rr, by - rr * 0.25 + br * 0.15, bx + rr, by + rr * 0.25 + br * 0.15), P((255, 230, 190), 0.35 * (1 - ph), stroke=3))
    basket(c, bx, by + math.sin(t * 2) * 6, br, t, 1.1, s_light=br * 0.28)
    c.save(); cam(c, 1 + 0.06 * u, -40 * u, 0, 1.4)
    reeds(c, t, -1, 14, 21); reeds(c, t, 1, 14, 22)
    c.restore()
    label(c, "THE NILE", t, BOUNDS[2] + 0.3, BOUNDS[3] + 0.2)


def column(c, x, top, bot, w, t, shade=1.0):
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear([skia.Point(x - w / 2, 0), skia.Point(x + w / 2, 0)],
                [skia.Color(*[int(v * shade) for v in (120, 86, 56)]), skia.Color(*[int(v * shade) for v in (226, 186, 128)]),
                 skia.Color(*[int(v * shade) for v in (96, 66, 44)])], [0, 0.4, 1]))
    c.drawRect(skia.Rect.MakeLTRB(x - w / 2, top + w * 0.6, x + w / 2, bot), p)
    cap = skia.Path(); cap.moveTo(x - w * 0.5, top + w * 0.6); cap.cubicTo(x - w * 0.95, top + w * 0.2, x - w * 0.8, top, x - w * 0.75, top)
    cap.lineTo(x + w * 0.75, top); cap.cubicTo(x + w * 0.8, top, x + w * 0.95, top + w * 0.2, x + w * 0.5, top + w * 0.6); cap.close()
    c.drawPath(cap, p)
    for k in range(4):
        yy = top + w * 0.8 + k * w * 0.18
        c.drawLine(x - w / 2, yy, x + w / 2, yy, P((90, 60, 36), 0.5 * shade, stroke=4))
    c.drawRect(skia.Rect.MakeLTRB(x - w * 0.62, bot - 24, x + w * 0.62, bot), P(tuple(int(v * shade) for v in (150, 112, 74))))


def s4_bank(c, t, u):
    lin(c, (0, 0, W, 1300), [(0, (246, 200, 140)), (1, (255, 232, 196))])
    radial(c, 820, 240, 520, (255, 236, 190), 0.5)
    v = ease(u)
    c.save(); cam(c, 1.06 - 0.06 * v, 0, 120 - 160 * v, 0.6)
    c.drawRect(skia.Rect.MakeLTRB(-100, 180, 900, 290), P((176, 132, 86)))
    c.drawRect(skia.Rect.MakeLTRB(-100, 280, 900, 300), P((120, 86, 56)))
    for k, x in enumerate((60, 330, 600)):
        column(c, x, 300, 1290, 150, t, 0.95)
    c.restore()
    c.save(); cam(c, 1.06 - 0.06 * v, 0, 120 - 160 * v, 1.0)
    for k in range(6):
        y = 1290 + k * 42
        c.drawRect(skia.Rect.MakeLTRB(-60 + k * 20, y, W + 60, y + 42), P((206 - k * 14, 168 - k * 12, 118 - k * 10)))
        c.drawLine(-60, y, W + 60, y, P((120, 86, 56), 0.6, stroke=3))
    lin(c, (0, 1540, W, H), [(0, (88, 140, 140)), (1, (26, 52, 66))])
    water(c, 1550, t, 0.9, (240, 250, 240), speed=20, rows=40)
    basket(c, 560, 1560 + math.sin(t * 1.8) * 5, 230, t, 1.25, s_light=66)
    c.restore()
    cur = skia.Path(); cur.moveTo(W, 0); cur.lineTo(W - 150, 0)       # sheer curtain on the right
    for k in range(21):
        y = k * H / 20; x = W - 150 - 50 * math.sin(t * 1.6 + k * 0.5) - 20 * k / 20
        cur.lineTo(x, y)
    cur.lineTo(W, H); cur.close()
    c.drawPath(cur, P((255, 248, 236), 0.38))
    label(c, "ASIYA  ·  AL-QASAS 28:9", t, BOUNDS[3] + 0.3, BOUNDS[4] + 0.2)


def s5_corridor(c, t, u):
    F, VY = 760, 860
    camz = 2.4 * ease(u)
    lin(c, (0, 0, W, H), [(0, (18, 12, 10)), (0.45, (46, 30, 20)), (1, (30, 20, 14))])

    def pr(x, y, z):
        return 540 + x * F / z, VY + (1.7 - y) * F / z
    dz = 22 - camz
    dx0, dy0 = pr(-1.1, 3.6, dz); dx1, dy1 = pr(1.1, 0, dz)
    fl = clamp((t - word_t(5, "mother")) / 1.0)
    radial(c, 540, (dy0 + dy1) / 2, 520 + 300 * fl, (255, 200, 120), 0.55 + 0.35 * fl)
    c.drawRect(skia.Rect.MakeLTRB(dx0, dy0, dx1, dy1), P((255, 226, 170), 0.9))
    fpath = skia.Path(); a0 = pr(-3, 0, 0.7); a1 = pr(3, 0, 0.7); b1 = pr(3, 0, dz); b0 = pr(-3, 0, dz)
    fpath.moveTo(*a0); fpath.lineTo(*a1); fpath.lineTo(*b1); fpath.lineTo(*b0); fpath.close()
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear([skia.Point(0, H), skia.Point(0, VY)], [skia.Color(70, 48, 32), skia.Color(150, 104, 66)], [0, 1]))
    c.drawPath(fpath, p)
    radial(c, 540, dy1 + 60, 420, (255, 200, 130), 0.35, sy=0.25)
    for zi in range(20, 0, -1):
        z = zi * 2.0 - camz
        if z < 0.9 or z > dz:
            continue
        shade = clamp(0.25 + 1.6 / z, 0.25, 1.0)
        for side in (-1, 1):
            x0, y0 = pr(side * 2.2, 4.8, z); _, y1 = pr(side * 2.2, 0, z)
            column(c, x0, y0, y1, 0.75 * F / z, t, shade)
    orb_z = 1.6 + camz * 0.2 + 15 * ease(clamp((t - L[5] - 0.3) / (word_t(5, "mother") - L[5])))
    ox, oy = pr(0, 1.3, orb_z - camz * 0.9 if orb_z - camz * 0.9 > 0.8 else 0.8)
    light(c, ox, oy, max(14, 0.32 * F / max(orb_z - camz * 0.9, 0.8)), t, 1.1)
    motes(c, t, a=0.4)
    label(c, "AL-QASAS 28:11-12", t, BOUNDS[4] + 0.3, BOUNDS[5] + 0.2)


def s6_sunset(c, t, u):
    c.save(); cam(c, 1 + 0.1 * ease(u), 0, -40 * u, 1.0)
    lin(c, (0, 0, W, 1420), [(0, (110, 54, 32)), (1, (170, 90, 50))])
    TEX.draw(c)
    win = skia.Rect.MakeXYWH(300, 220, 480, 640)
    c.save(); c.clipRect(win)
    lin(c, (300, 220, 780, 860), [(0, (250, 150, 90)), (0.7, (255, 200, 120)), (1, (255, 226, 170))])
    c.drawCircle(560, 780, 110, P((255, 238, 190)))
    c.restore()
    c.drawRect(win, P((70, 36, 20), 1, stroke=26))
    c.drawLine(540, 220, 540, 860, P((70, 36, 20), 1, stroke=14))
    for k in range(4):     # rays
        rp = skia.Path(); x0 = 330 + k * 120
        rp.moveTo(x0, 860); rp.lineTo(x0 + 100, 860); rp.lineTo(x0 + 330 + k * 40, 1700); rp.lineTo(x0 + 120 + k * 40, 1700); rp.close()
        c.drawPath(rp, P((255, 214, 150), 0.10 + 0.04 * math.sin(t * 1.5 + k), blend=skia.BlendMode.kScreen))
    lin(c, (0, 1420, W, H), [(0, (120, 64, 36)), (1, (44, 24, 16))])
    c.drawRoundRect(skia.Rect.MakeLTRB(170, 1330, 910, 1500), 50, 50, P((150, 50, 40)))
    c.drawRoundRect(skia.Rect.MakeLTRB(170, 1330, 910, 1380), 40, 40, P((190, 76, 56)))
    cloth = skia.Path(); cloth.moveTo(380, 1360); cloth.cubicTo(400, 1200, 680, 1200, 700, 1360); cloth.cubicTo(620, 1400, 460, 1400, 380, 1360)
    c.drawPath(cloth, P((240, 228, 206)))
    c.drawPath(cloth, P((190, 170, 140), 0.6, stroke=4))
    hit = clamp((t - word_t(6, "true")) / 0.6)
    light(c, 540, 1270, 56 + 10 * hit, t, 1.0 + 0.5 * hit)
    if hit > 0:
        for k in range(12):
            ang = k * math.pi / 6 + t * 0.2
            c.drawLine(540 + math.cos(ang) * 120, 1270 + math.sin(ang) * 120, 540 + math.cos(ang) * (120 + 260 * hit),
                       1270 + math.sin(ang) * (120 + 260 * hit), P((255, 230, 170), 0.35 * hit, stroke=5, blend=skia.BlendMode.kScreen))
    motes(c, t, a=0.6, region=(300, 860, 1080, 1700))
    c.restore()
    a = clamp((t - word_t(6, "true")) / 0.4) * clamp((BOUNDS[6] + 0.2 - t) / 0.4)
    if a > 0:
        text(c, "PROMISE KEPT", 540, 300 + 20 * (1 - a), 110, TF_COND, GOLD, a, 0.08)
    label(c, "AL-QASAS 28:13", t, word_t(6, "true") + 0.2, BOUNDS[6] + 0.2, y=390)


def star_orn(c, x, y, r, t, a):
    c.save(); c.translate(x, y); c.rotate(math.sin(t * 0.6) * 6)
    for k in (0, 45):
        c.save(); c.rotate(k); c.drawRect(skia.Rect.MakeXYWH(-r * 0.7, -r * 0.7, r * 1.4, r * 1.4), P(GOLD, a, stroke=4)); c.restore()
    c.drawCircle(0, 0, r * 0.32, P(GOLD, a, stroke=3))
    c.restore()


def s7_palace(c, t, u):
    lin(c, (0, 0, W, 1250), [(0, (20, 16, 48)), (0.6, (110, 56, 80)), (1, (236, 120, 70))])
    stars(c, t, 0.8 * clamp(u * 2), ymax=700)
    c.save(); cam(c, 1 + 0.14 * ease(u), 0, 40 * u, 0.7)
    radial(c, 540, 1240, 600, (255, 150, 80), 0.45, sy=0.5)
    sil = (16, 12, 26)
    pyl = skia.Path()
    pyl.moveTo(140, 1250); pyl.lineTo(200, 640); pyl.lineTo(440, 640); pyl.lineTo(470, 1250)
    pyl.moveTo(610, 1250); pyl.lineTo(640, 640); pyl.lineTo(880, 640); pyl.lineTo(940, 1250)
    c.drawPath(pyl, P(sil))
    c.drawRect(skia.Rect.MakeLTRB(470, 820, 610, 1250), P(sil))
    for ox in (60, 1010):
        ob = skia.Path(); ob.moveTo(ox - 26, 1250); ob.lineTo(ox - 16, 560); ob.lineTo(ox, 520); ob.lineTo(ox + 16, 560); ob.lineTo(ox + 26, 1250); ob.close()
        c.drawPath(ob, P(sil))
    for k in range(4):
        fl = 0.7 + 0.3 * math.sin(t * 5 + k * 2)
        for wx in (250 + k * 45, 690 + k * 45):
            c.drawRect(skia.Rect.MakeXYWH(wx, 900 + (k % 2) * 140, 18, 30), P((255, 170, 80), 0.8 * fl))
            radial(c, wx + 9, 915 + (k % 2) * 140, 50, (255, 150, 70), 0.3 * fl)
    c.restore()
    lin(c, (0, 1250, W, H), [(0, (140, 70, 70)), (0.3, (50, 30, 50)), (1, (8, 8, 18))])
    water(c, 1260, t, 0.8, (255, 170, 110), speed=25)
    c.save(); cam(c, 1 + 0.14 * ease(u), 0, 0, 1.3)
    reeds(c, t, -1, 9, 31, rgb=(10, 8, 16), hmin=350, hmax=700); reeds(c, t, 1, 9, 32, rgb=(10, 8, 16), hmin=350, hmax=700)
    c.restore()
    tf = word_t(7, "Follow")
    d = ease(clamp((t - tf + 0.6) / 0.8))
    if d > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), P((6, 6, 16), 0.78 * d))
        star_orn(c, 540, 560, 70, t, d)
        text(c, "PART 2", 540, 830 + 30 * (1 - d), 230, TF_COND, GOLD, d, 0.05)
        f = skia.Font(TF_COND, 96)
        bw = sum(f.measureText(ch) + 0.06 * 96 for ch in "FOLLOW") + 50
        c.drawRect(skia.Rect.MakeXYWH(540 - bw / 2, 892, bw * ease(clamp((t - tf) / 0.35)), 100), P(GOLD, d))
        text(c, "FOLLOW", 540, 975, 96, TF_COND, (30, 22, 14), d * clamp((t - tf - 0.1) / 0.3), 0.06)
        text(c, "THE PALACE YEARS  ·  COMING NEXT", 540, 1080, 34, TF_SANS, CREAM, d * clamp((t - tf - 0.4) / 0.4), 0.2)


SCENES = [s1_night, s2_room, s3_nile, s4_bank, s5_corridor, s6_sunset, s7_palace]


class Tex:
    """Static plaster texture, multiplied over walls."""
    def __init__(self):
        r = np.random.default_rng(5)
        n = r.standard_normal((H // 8, W // 8))
        from PIL import Image, ImageFilter
        im = Image.fromarray(np.clip(128 + n * 50, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2)).resize((W, H), Image.BICUBIC)
        a = np.asarray(im, np.uint8)
        rgba = np.dstack([a, a, a, np.full_like(a, 60)])
        self.img = skia.Image.fromarray(np.ascontiguousarray(rgba), colorType=skia.ColorType.kRGBA_8888_ColorType)

    def draw(self, c):
        p = skia.Paint(); p.setBlendMode(skia.BlendMode.kOverlay)
        c.drawImage(self.img, 0, 0, skia.SamplingOptions(), p)


TEX = Tex()
yy, xx = np.mgrid[0:H, 0:W]
VIG = (1 - 0.55 * np.clip(((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2, 0, 1) ** 1.3).astype(np.float32)[..., None]
GRAIN = [np.random.default_rng(i).normal(0, 7, (H, W, 1)).astype(np.float32) for i in range(6)]


def scene_img(i, t):
    surf = skia.Surface(W, H)
    with surf as c:
        c.clear(skia.Color(0, 0, 0))
        t0, t1 = BOUNDS[i], BOUNDS[i + 1]
        SCENES[i](c, t, clamp((t - t0) / (t1 - t0)))
    return surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)[..., :3].astype(np.float32)


def frame(t):
    i = max(k for k in range(7) if BOUNDS[k] <= t) if t < DUR else 6
    img = scene_img(i, t)
    if i < 6 and t > BOUNDS[i + 1] - XF:
        a = ease((t - (BOUNDS[i + 1] - XF)) / XF)
        img = img * (1 - a) + scene_img(i + 1, t) * a
    elif i > 0 and t < BOUNDS[i] + 0.0:
        pass
    a_in = clamp(t / 0.5); a_out = clamp((DUR - t) / 0.6)
    img = img * VIG * min(a_in, a_out) + GRAIN[int(t * FPS) % 6]
    return np.clip(img, 0, 255).astype(np.uint8)


def render_range(f0, f1, out):
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for n in range(f0, f1):
        enc.stdin.write(frame(n / FPS).tobytes())
    enc.stdin.close(); enc.wait()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe", default="")
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    if a.probe:
        from PIL import Image
        d = ROOT / "out/paint_probe"; d.mkdir(parents=True, exist_ok=True)
        for ts in a.probe.split(","):
            t0 = time.time(); Image.fromarray(frame(float(ts))).save(d / f"p{float(ts):06.2f}.png")
            print(ts, f"{time.time() - t0:.2f}s")
    if a.out:
        from multiprocessing import Process
        N = int(math.ceil(DUR * FPS)); k = 2
        cuts = [N * i // k for i in range(k + 1)]
        parts = [str(ROOT / f"out/part{i}.mp4") for i in range(k)]
        ps = [Process(target=render_range, args=(cuts[i], cuts[i + 1], parts[i])) for i in range(k)]
        t0 = time.time(); [p.start() for p in ps]; [p.join() for p in ps]
        lst = ROOT / "out/parts.txt"; lst.write_text("".join(f"file '{p}'\n" for p in parts))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", a.out], check=True)
        print(f"wrote {a.out} ({N} frames, {time.time() - t0:.0f}s)")
