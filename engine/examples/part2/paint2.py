"""Musa Part 2, illustrated: palace years, the fight, repentance, the warning, flight, the well of Madyan.
Musa (AS) is the glowing oval of light; no people are drawn. Reuses the Part 1 painter's helpers.
  python3 paint2.py --probe 2,7,...      python3 paint2.py --out out/paint.mp4
"""
import argparse, json, math, pathlib, subprocess, sys, time
import numpy as np
import skia

ROOT = pathlib.Path(__file__).parent
sys.path.insert(0, str(ROOT.parents[2] / "engine" / "core"))  # repo/engine/core
import paint as K
from paint import P, lin, radial, text, label, light, palm, column, motes, stars, star_orn, cam, clamp, ease, W, H, FPS, GOLD, CREAM, TF_COND, TF_SANS

TIM = json.loads((ROOT / "audio/timing.json").read_text())
SEG = TIM["segments"]; DUR = TIM["total_duration"]
L = {s["id"]: s["start"] for s in SEG}; E = {s["id"]: s["end"] for s in SEG}


def wt(i, word):
    s = next(x for x in SEG if x["id"] == i)
    ws = s["vo"].split(); tot = sum(len(w) for w in ws); acc = 0
    for w in ws:
        if w.lower().strip(".,:!?'").startswith(word.lower()):
            return s["start"] + (s["end"] - s["start"]) * acc / tot
        acc += len(w)
    return s["start"]


B = [0.0, L[2] - 0.15, L[4] - 0.15, L[6] - 0.15, L[7] - 0.15, L[8] - 0.2, DUR]
XF = 0.45
R = np.random.default_rng(3)
DUST = [(R.uniform(0, W), R.uniform(900, 1700), R.uniform(3, 9), R.uniform(0, 6.28), R.uniform(0.5, 1.5)) for _ in range(140)]


def s1_palace(c, t, u):
    c.save(); cam(c, 1 + 0.1 * ease(u), 0, -30 * u, 1.0)
    lin(c, (0, 0, W, H), [(0, (30, 20, 14)), (0.5, (70, 46, 28)), (1, (40, 26, 18))])
    K.TEX.draw(c)
    door = skia.Path(); door.addRect(skia.Rect.MakeXYWH(390, 520, 300, 700)); door.addCircle(540, 520, 150)
    radial(c, 540, 800, 700, (255, 196, 120), 0.35)
    c.drawPath(door, P((255, 214, 150), 0.85))
    lin(c, (0, 1220, W, H), [(0, (120, 84, 52)), (1, (36, 24, 16))])
    for k in range(9):
        c.drawLine(0, 1220 + k ** 1.6 * 14, W, 1220 + k ** 1.6 * 14, P((80, 54, 32), 0.5, stroke=2))
    for x, w, sh in ((70, 220, 0.9), (1010, 220, 0.9), (250, 130, 0.6), (830, 130, 0.6)):
        column(c, x, 60 if w > 200 else 280, 1250 if w > 200 else 1225, w, t, sh)
    c.drawRect(skia.Rect.MakeLTRB(-50, 0, W + 50, 70), P((90, 60, 36)))
    g = ease(clamp((t - 0.6) / (B[1] - 0.6)))
    s = 34 + 40 * g
    radial(c, 540, 1330, 200 + 80 * g, (255, 220, 160), 0.35, sy=0.22)
    light(c, 540, 1180 - 30 * g, s, t, 0.9 + 0.3 * g)
    motes(c, t, a=0.45)
    c.restore()
    a = clamp((3.6 - t) / 0.6) * clamp(t / 0.5)
    lin(c, (0, 0, W, 700), [(0, (10, 6, 4, int(220 * a))), (1, (10, 6, 4, 0))]) if a > 0 else None
    if a > 0:
        star_orn(c, 540, 300, 58, t, a)
        text(c, "STORIES OF THE PROPHETS", 540, 420, 42, TF_SANS, GOLD, a, 0.24)
        text(c, "PROPHET MUSA  ·  PART 2", 540, 510, 92, TF_COND, CREAM, a, 0.06)
    K.label(c, "AL-QASAS 28:14", t, 3.5, B[1] + 0.2)


def s2_city(c, t, u):
    hit = wt(3, "struck")
    sh = 14 * math.exp(-max(0, t - hit) * 6) * (t > hit)
    c.save(); c.translate(math.sin(t * 60) * sh, math.cos(t * 47) * sh)
    lin(c, (0, 0, W, 1000), [(0, (60, 40, 80)), (0.6, (190, 100, 70)), (1, (240, 150, 90))])
    VY = 950
    lw = skia.Path(); lw.moveTo(0, 0); lw.lineTo(400, 640); lw.lineTo(400, VY + 60); lw.lineTo(0, H); lw.close()
    rw = skia.Path(); rw.moveTo(W, 0); rw.lineTo(680, 640); rw.lineTo(680, VY + 60); rw.lineTo(W, H); rw.close()
    for pth, x0, x1 in ((lw, 0, 400), (rw, W, 680)):
        p = skia.Paint(AntiAlias=True)
        p.setShader(skia.GradientShader.MakeLinear([skia.Point(x0, 0), skia.Point(x1, 0)], [skia.Color(90, 56, 36), skia.Color(170, 110, 66)], [0, 1]))
        c.drawPath(pth, p)
    c.save(); c.clipPath(lw); K.TEX.draw(c); c.restore()
    c.save(); c.clipPath(rw); K.TEX.draw(c); c.restore()
    fl = skia.Path(); fl.moveTo(400, VY + 60); fl.lineTo(680, VY + 60); fl.lineTo(W, H); fl.lineTo(0, H); fl.close()
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear([skia.Point(0, VY), skia.Point(0, H)], [skia.Color(200, 140, 90), skia.Color(80, 50, 30)], [0, 1]))
    c.drawPath(fl, p)
    for k, (y, side) in enumerate(((420, -1), (700, 1), (980, -1))):      # awnings
        x = 0 if side < 0 else W
        aw = skia.Path(); aw.moveTo(x, y); aw.lineTo(x - side * 300, y + 90); aw.lineTo(x - side * 300, y + 130); aw.lineTo(x, y + 60); aw.close()
        c.drawPath(aw, P(((170, 50, 40), (60, 90, 120), (190, 150, 60))[k], 0.95))
    # the struggle: a churning dust cloud, then stillness
    calm = clamp((t - hit - 0.4) / 1.2)
    churn = clamp((t - L[2]) / 0.8) * (1 - calm)
    for x0, y0, r, ph, sp in DUST:
        ang = t * 2.4 * sp + ph
        rad = 140 + 120 * math.sin(ph * 3)
        x = 540 + math.cos(ang) * rad * (1 + 1.5 * clamp((t - hit) / 0.6) * (t > hit))
        y = 1300 + math.sin(ang * 1.3) * rad * 0.45
        c.drawCircle(x, y, r * 4 * (1 + churn), P((214, 176, 128), 0.22 * max(churn, 0.12 * (1 - calm * 0.8)), blur=r * 2.5))
    radial(c, 540, 1300, 330, (120, 70, 40), 0.35 * churn, sy=0.6, blend=None)
    lx = 200 + 220 * ease(clamp((t - wt(2, "found")) / 1.2))
    light(c, lx, 1240, 58, t, 1.1)
    f = clamp(1 - (t - hit) / 0.5) * (t >= hit)
    if f > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), P((255, 245, 225), 0.8 * f))
    c.drawRect(skia.Rect.MakeWH(W, H), P((10, 8, 20), 0.35 * calm))
    c.restore()
    K.label(c, "AL-QASAS 28:15", t, B[1] + 0.3, B[2] + 0.2)


def s3_night(c, t, u):
    lin(c, (0, 0, W, H), [(0, (4, 6, 20)), (0.7, (16, 20, 48)), (1, (10, 10, 24))])
    stars(c, t, 1.0, ymax=1300)
    c.drawCircle(820, 420, 64, P((240, 236, 210))); c.drawCircle(846, 402, 58, P((6, 9, 26)))
    dune = skia.Path(); dune.moveTo(0, 1450); dune.cubicTo(300, 1350, 700, 1520, W, 1400); dune.lineTo(W, H); dune.lineTo(0, H); dune.close()
    c.drawPath(dune, P((22, 20, 40)))
    fg = clamp((t - L[5]) / 0.8)
    if fg > 0:
        rp = skia.Path(); rp.moveTo(480, 0); rp.lineTo(600, 0); rp.lineTo(700, 1420); rp.lineTo(380, 1420); rp.close()
        c.drawPath(rp, P((255, 236, 190), 0.22 * fg, blend=skia.BlendMode.kScreen))
        radial(c, 540, 1350, 500, (255, 220, 160), 0.3 * fg)
    bow = 30 * math.sin(clamp((t - L[4]) / (E[4] - L[4])) * math.pi)
    light(c, 540, 1300 + bow, 40 + 22 * fg, t, 0.55 + 0.8 * fg)
    K.label(c, "AL-QASAS 28:16", t, B[2] + 0.3, B[3] + 0.2)


def s4_alley(c, t, u):
    jit = 4 * math.sin(t * 23)
    c.save(); c.translate(jit, 0)
    lin(c, (0, 0, W, H), [(0, (10, 8, 18)), (1, (30, 20, 20))])
    VY = 780
    lw = skia.Path(); lw.moveTo(-20, -20); lw.lineTo(470, VY - 60); lw.lineTo(470, VY + 40); lw.lineTo(-20, H); lw.close()
    rw = skia.Path(); rw.moveTo(W + 20, -20); rw.lineTo(610, VY - 60); rw.lineTo(610, VY + 40); rw.lineTo(W + 20, H); rw.close()
    c.drawPath(lw, P((46, 30, 24))); c.drawPath(rw, P((40, 26, 22)))
    fl = skia.Path(); fl.moveTo(470, VY + 40); fl.lineTo(610, VY + 40); fl.lineTo(W + 20, H); fl.lineTo(-20, H); fl.close()
    c.drawPath(fl, P((70, 50, 36)))
    for k, (x, y) in enumerate(((150, 700), (930, 900), (380, 760), (700, 760))):
        flk = 0.75 + 0.25 * math.sin(t * 14 + k * 2)
        radial(c, x, y, 260 * (1 if k < 2 else 0.5), (255, 140, 60), 0.4 * flk)
        c.drawCircle(x, y, 12 if k < 2 else 6, P((255, 220, 150)))
    # running footprints rushing toward the camera
    n = 14
    for k in range(n):
        ft = L[6] + k * 0.22
        if t < ft:
            continue
        a = clamp((t - ft) / 0.1) * clamp(1 - (t - ft) / 2.5)
        z = 1 - k / (n + 1)
        y = VY + 60 + (H - VY) * (1 - z) ** 1.0 * 0.95
        sc = 0.25 + 1.4 * (1 - z)
        x = 540 + (1 if k % 2 else -1) * 30 * sc
        c.save(); c.translate(x, y); c.scale(sc, sc)
        c.drawOval(skia.Rect.MakeXYWH(-14, -36, 28, 48), P((24, 16, 12), 0.75 * a))
        c.drawOval(skia.Rect.MakeXYWH(-10, 16, 20, 18), P((24, 16, 12), 0.75 * a))
        c.restore()
        radial(c, x, y, 50 * sc, (180, 140, 100), 0.25 * a * clamp(1 - (t - ft) / 0.6), blend=None)
    c.restore()
    radial(c, 540, H / 2, 1300, (160, 20, 20), 0.18 + 0.06 * math.sin(t * 5), blend=skia.BlendMode.kMultiply)
    K.label(c, "AL-QASAS 28:20", t, B[3] + 0.3, B[4] + 0.2)


def dunes(c, t, u, cols, base, amp, px=0):
    for i, (col_, y, a_) in enumerate(zip(cols, base, amp)):
        sh = (i * 260 + px * (i + 1)) % 600
        d = skia.Path(); d.moveTo(-300, H); d.lineTo(-300, y)
        d.cubicTo(150 - sh, y - a_, 450 - sh, y + a_ * 0.5, 700 - sh * 0.5, y - a_ * 0.3)
        d.cubicTo(900, y - a_ * 0.9, 1150, y + a_ * 0.2, W + 300, y - a_ * 0.4)
        d.lineTo(W + 300, H); d.close()
        p = skia.Paint(AntiAlias=True)
        hi = tuple(min(255, int(v * 1.25)) for v in col_)
        p.setShader(skia.GradientShader.MakeLinear([skia.Point(0, y - a_), skia.Point(0, y + 300)], [skia.Color(*hi), skia.Color(*col_)], [0, 1]))
        c.drawPath(d, p)


def s5_desert(c, t, u):
    lin(c, (0, 0, W, H), [(0, (6, 8, 26)), (0.55, (26, 34, 76)), (1, (16, 18, 40))])
    stars(c, t, 1.0, ymax=1000)
    radial(c, 760, 420, 300, (200, 210, 255), 0.25)
    c.drawCircle(760, 420, 110, P((236, 232, 214)))
    dunes(c, t, u, [(38, 40, 82), (52, 50, 92), (74, 64, 104), (98, 82, 116)], [1080, 1220, 1400, 1620], [80, 120, 150, 180], px=40 * u)
    trail = skia.Path(); trail.moveTo(560, H + 40); trail.cubicTo(300, 1600, 760, 1350, 520, 1080)
    pm = skia.PathMeasure(trail, False); Ltr = pm.getLength()
    for k in range(40):
        pos = pm.getPosTan(Ltr * k / 40)
        if pos:
            sc = 1 - k / 45
            c.drawOval(skia.Rect.MakeXYWH(pos[0].x() - 9 * sc, pos[0].y() - 5 * sc, 18 * sc, 10 * sc), P((40, 34, 66), 0.8))
    v = ease(clamp((t - L[7]) / (E[7] - L[7] + 0.4)))
    pos = pm.getPosTan(Ltr * (0.12 + 0.82 * v))
    if pos:
        light(c, pos[0].x(), pos[0].y() - 40 * (1 - v), 52 - 34 * v, t, 1.1)
    a = clamp((t - wt(7, "toward")) / 0.5) * clamp((B[5] + 0.2 - t) / 0.4)
    if a > 0:
        text(c, "TOWARD MADYAN", 540, 640, 120, TF_COND, GOLD, a, 0.08)
    K.label(c, "AL-QASAS 28:21-22", t, B[4] + 0.3, B[5] + 0.2)


def s6_well(c, t, u):
    lin(c, (0, 0, W, H), [(0, (6, 8, 24)), (0.6, (34, 30, 66)), (1, (60, 44, 60))])
    stars(c, t, 1.0, ymax=1150)
    c.save(); cam(c, 1 + 0.12 * ease(u), 0, 30 * u, 1.0)
    dunes(c, t, u, [(40, 34, 60), (64, 50, 70)], [1250, 1500], [90, 70])
    palm(c, 230, 1330, 520, (18, 14, 28), t, 1); palm(c, 880, 1300, 420, (22, 18, 32), t, 2)
    cx, cy, rx = 560, 1440, 230
    radial(c, cx, cy - 120, 520, (255, 190, 120), 0.18)
    body = skia.Rect.MakeLTRB(cx - rx, cy - 40, cx + rx, cy + 220)
    p = skia.Paint(AntiAlias=True)
    p.setShader(skia.GradientShader.MakeLinear([skia.Point(cx - rx, 0), skia.Point(cx + rx, 0)],
                [skia.Color(70, 60, 70), skia.Color(150, 128, 120), skia.Color(56, 48, 60)], [0, 0.45, 1]))
    c.drawRect(body, p)
    for r_ in range(4):
        y = cy - 40 + r_ * 65
        c.drawLine(cx - rx, y, cx + rx, y, P((40, 34, 44), 0.7, stroke=4))
        for k in range(6):
            x = cx - rx + (k + 0.5 * (r_ % 2)) * rx / 3
            c.drawLine(x, y, x, y + 65, P((40, 34, 44), 0.5, stroke=3))
    c.drawOval(skia.Rect.MakeLTRB(cx - rx, cy - 90, cx + rx, cy + 10), P((20, 16, 24)))
    c.drawOval(skia.Rect.MakeLTRB(cx - rx, cy - 90, cx + rx, cy + 10), P((160, 140, 130), 1, stroke=14))
    for sx in (cx - rx + 30, cx + rx - 30):
        c.drawLine(sx, cy - 60, sx, cy - 420, P((70, 46, 30), 1, stroke=22))
    c.drawLine(cx - rx + 10, cy - 410, cx + rx - 10, cy - 410, P((80, 54, 34), 1, stroke=24))
    sw = math.sin(t * 1.4) * 6
    c.drawLine(cx, cy - 410, cx + sw, cy - 200, P((180, 160, 120), 1, stroke=4))
    c.drawRect(skia.Rect.MakeXYWH(cx + sw - 34, cy - 200, 68, 60), P((110, 72, 40)))
    c.restore()
    tf = wt(8, "Follow")
    d = ease(clamp((t - tf + 0.6) / 0.8))
    if d > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), P((6, 6, 16), 0.78 * d))
        star_orn(c, 540, 900, 70, t, d)
        text(c, "PART 3", 540, 1170 + 30 * (1 - d), 230, TF_COND, GOLD, d, 0.05)
        f = skia.Font(TF_COND, 96)
        bw = sum(f.measureText(ch) + 0.06 * 96 for ch in "FOLLOW") + 50
        c.drawRect(skia.Rect.MakeXYWH(540 - bw / 2, 1232, bw * ease(clamp((t - tf) / 0.35)), 100), P(GOLD, d))
        text(c, "FOLLOW", 540, 1315, 96, TF_COND, (30, 22, 14), d * clamp((t - tf - 0.1) / 0.3), 0.06)
        text(c, "THE WELL OF MADYAN  ·  COMING NEXT", 540, 1420, 34, TF_SANS, CREAM, d * clamp((t - tf - 0.4) / 0.4), 0.2)
    else:
        K.label(c, "THE WELL OF MADYAN", t, B[5] + 0.3, tf - 0.5)


SCENES = [s1_palace, s2_city, s3_night, s4_alley, s5_desert, s6_well]


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
