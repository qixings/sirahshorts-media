"""Musa Part 4, illustrated: the fire on the mountain. No people drawn; Musa (AS) and Harun (AS) are glowing lights.
Scene 2 can use an AI-animated clip (ai/fire.mp4, made from the painted keyframe by Seedance image-to-video).
  python3 paint4.py --keyframe            python3 paint4.py --probe 2,7,...      python3 paint4.py --out out/paint.mp4
"""
import argparse, json, math, pathlib, subprocess, sys, time
import numpy as np
import skia

ROOT = pathlib.Path(__file__).parent
sys.path.insert(0, str(ROOT.parents[1] / "engine" / "core"))  # repo/engine/core
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


B = [0.0, L[3] - 0.15, wt(4, "Remove") - 0.25, L[5] - 0.15, L[8] - 0.15, L[9] - 0.15, L[10] - 0.15, L[12] - 0.15, DUR]
XF = 0.45
lab = K.label


# ------------------------------------------------------------- pieces
def night(c, top=(4, 6, 20), mid=(18, 18, 46), bot=(30, 20, 30)):
    lin(c, (0, 0, W, H), [(0, top), (0.6, mid), (1, bot)])


def mountain(c, col=(24, 20, 34), peak=(600, 640)):
    m = skia.Path(); m.moveTo(-100, 1560); m.lineTo(220, 1100); m.lineTo(380, 1160); m.lineTo(peak[0], peak[1])
    m.lineTo(790, 960); m.lineTo(930, 900); m.lineTo(W + 100, 1320); m.lineTo(W + 100, H); m.lineTo(-100, H); m.close()
    c.drawPath(m, P(col))
    ridge = skia.Path(); ridge.moveTo(220, 1100); ridge.lineTo(380, 1160); ridge.lineTo(peak[0], peak[1]); ridge.lineTo(790, 960)
    c.drawPath(ridge, P((70, 52, 70), 0.6, stroke=4))


def bush(c, x, y, s, col=(40, 34, 30)):
    c.drawLine(x, y, x - 4 * s, y - 70 * s, P((60, 42, 30), 1, stroke=10 * s))
    for dx, dy, r in ((-40, -90, 46), (0, -120, 54), (42, -92, 44), (-10, -70, 40), (24, -64, 38)):
        c.drawCircle(x + dx * s, y + dy * s, r * s, P(col))


def flames(c, x, y, t, scale=1.0, a=1.0):
    fl = 0.82 + 0.18 * math.sin(t * 12) + 0.08 * math.sin(t * 7.7)
    radial(c, x, y - 60 * scale, 520 * scale * fl, (255, 140, 50), 0.55 * a)
    radial(c, x, y - 60 * scale, 200 * scale * fl, (255, 220, 150), 0.6 * a)
    for k in range(7):
        h_ = (120 + 50 * (k % 3)) * fl * scale
        fp = skia.Path(); xx = x - 60 * scale + k * 20 * scale
        fp.moveTo(xx - 30 * scale, y); fp.quadTo(xx - 10 * scale + 14 * scale * math.sin(t * 9 + k), y - h_, xx, y - h_ * 1.25)
        fp.quadTo(xx + 34 * scale, y - h_ * 0.5, xx + 30 * scale, y); fp.close()
        c.drawPath(fp, P((255, 200 - k * 16, 90), 0.85 * a, blend=skia.BlendMode.kScreen))
    for k in range(10):
        ph = (t * 0.6 + k * 0.137) % 1
        ex = x + math.sin(k * 2.1 + t) * 50 * scale; ey = y - 80 * scale - ph * 360 * scale
        c.drawCircle(ex, ey, 3 * scale, P((255, 200, 120), (1 - ph) * a, blend=skia.BlendMode.kScreen))


def tent(c, x, y, s, t, glow=1.0):
    p = skia.Path(); p.moveTo(x - 200 * s, y); p.lineTo(x - 60 * s, y - 230 * s); p.lineTo(x + 60 * s, y - 250 * s); p.lineTo(x + 210 * s, y); p.close()
    c.drawPath(p, P((70, 40, 34)))
    d = skia.Path(); d.moveTo(x - 50 * s, y); d.lineTo(x + 5 * s, y - 170 * s); d.lineTo(x + 60 * s, y); d.close()
    fl = 0.85 + 0.15 * math.sin(t * 8)
    radial(c, x, y - 60 * s, 280 * s * fl, (255, 160, 70), 0.35 * glow)
    c.drawPath(d, P((255, 180, 100), glow))


def staff(c, x, y, h, ang=0, rgb=(110, 74, 46), a=1.0):
    c.save(); c.translate(x, y); c.rotate(ang)
    p = skia.Path(); p.moveTo(0, 0); p.lineTo(6, -h); p.quadTo(44, -h - 44, 52, -h + 10)
    c.drawPath(p, P(rgb, a, stroke=12)); c.restore()


def serpent(c, x, y, length, t, a=1.0, prog=1.0):
    pts = []
    n = 40
    for k in range(n):
        f = k / (n - 1)
        px = x - length / 2 + f * length * prog
        py = y + math.sin(f * 9 - t * 7) * 46 * (0.4 + 0.6 * f)
        pts.append((px, py))
    for k in range(n - 1):
        w = 30 * (1 - 0.75 * (k / n))
        col = (186, 146, 70) if k % 4 < 2 else (150, 112, 52)
        c.drawLine(*pts[k], *pts[k + 1], P(col, a, stroke=w, cap=skia.Paint.kRound_Cap))
    hx, hy = pts[-1]
    c.drawOval(skia.Rect.MakeLTRB(hx - 10, hy - 26, hx + 46, hy + 22), P((170, 128, 58), a))
    c.drawCircle(hx + 26, hy - 8, 5, P((255, 230, 150), a))


def sandals(c, x, y, s, a=1.0):
    for dx in (-36, 36):
        c.save(); c.translate(x + dx * s, y); c.rotate(-8 if dx < 0 else 8)
        c.drawOval(skia.Rect.MakeLTRB(-20 * s, -56 * s, 20 * s, 56 * s), P((120, 82, 50), a))
        c.drawLine(-18 * s, -20 * s, 18 * s, -20 * s, P((70, 46, 28), a, stroke=8 * s))
        c.restore()


def column(c, x, top, bot, w, shade=1.0):
    K.column(c, x, top, bot, w, 0, shade)


# ------------------------------------------------------------- the AI shot
AI = ROOT / "ai/fire.mp4"
_ai_frames = None


def ai_frame(t):
    """Frame of the AI clip at local time t (seconds from scene start), as float32 RGB 1080x1920, or None."""
    global _ai_frames
    if _ai_frames is None:
        if not AI.exists():
            _ai_frames = []
        else:
            raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(AI), "-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}",
                                  "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
            _ai_frames = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    if len(_ai_frames) == 0:
        return None
    k = min(len(_ai_frames) - 1, max(0, int(t * FPS)))
    return _ai_frames[k].astype(np.float32)


def keyframe(c, t):
    """The painted still that the AI clip starts from (also the fallback for scene 2)."""
    night(c)
    stars(c, t, 1.0, ymax=900)
    mountain(c)
    bush(c, 600, 900, 1.3)
    flames(c, 600, 840, t, 1.25)
    motes(c, t, (255, 190, 110), a=0.35)


# ------------------------------------------------------------- scenes
def s1_camp(c, t, u):
    night(c)
    stars(c, t, 1.0, ymax=1100)
    c.save(); cam(c, 1 + 0.12 * ease(u), 0, 50 * u, 0.4)
    mountain(c, (20, 18, 30), (760, 860))
    sp = clamp((t - wt(1, "fire")) / 0.8)
    if sp > 0:
        flames(c, 760, 900, t, 0.35, sp)
    c.restore()
    c.save(); cam(c, 1 + 0.12 * ease(u), 0, 50 * u, 1.0)
    lin(c, (0, 1450, W, H), [(0, (40, 30, 34)), (1, (16, 12, 18))])
    tent(c, 330, 1620, 1.2, t)
    for lx in (120, 560):
        radial(c, lx, 1560, 110, (255, 160, 70), 0.4); c.drawCircle(lx, 1560, 9, P((255, 230, 170)))
    go = clamp((t - wt(2, "flame")) / 1.5)
    light(c, 720 + 40 * go, 1600 - 80 * go, 50, t, 1.0)
    c.restore()
    a = clamp((3.8 - t) / 0.6) * clamp(t / 0.5)
    if a > 0:
        lin(c, (0, 0, W, 700), [(0, (6, 6, 14, int(235 * a))), (1, (6, 6, 14, 0))])
        star_orn(c, 540, 300, 58, t, a)
        text(c, "STORIES OF THE PROPHETS", 540, 420, 42, TF_SANS, GOLD, a, 0.24)
        text(c, "PROPHET MUSA  ·  PART 4", 540, 510, 92, TF_COND, CREAM, a, 0.06)
    lab(c, "TAHA 20:9-10", t, 3.7, B[1] + 0.2)


def s2_fire(c, t, u):
    keyframe(c, t)
    c.save(); cam(c, 1 + 0.1 * ease(u), 0, 0, 1.0)
    light(c, 600, 1500 - 120 * ease(u), 46, t, 1.0)
    c.restore()


def s3_valley(c, t, u):
    night(c, (8, 8, 24), (34, 26, 50), (60, 40, 36))
    stars(c, t, 0.8, ymax=800)
    c.save(); cam(c, 1.08 - 0.08 * ease(u), 0, 0, 1.0)
    radial(c, 540, 820, 900, (255, 150, 60), 0.35)
    lin(c, (0, 1250, W, H), [(0, (90, 60, 44)), (1, (30, 20, 20))])
    bush(c, 540, 1000, 1.0, (50, 40, 34)); flames(c, 540, 950, t, 0.8)
    off = clamp((t - wt(4, "sandals")) / 0.7)
    light(c, 540, 1420, 52, t, 1.0)
    sandals(c, 540 + 220 * ease(off), 1640 + 40 * ease(off), 1.0, 1.0)
    c.restore()
    a = clamp((t - wt(4, "sacred")) / 0.5)
    if a > 0:
        text(c, "TUWA", 540, 470, 150, TF_COND, GOLD, a, 0.14)
        text(c, "THE SACRED VALLEY", 540, 560, 40, TF_SANS, CREAM, a, 0.24)
    lab(c, "TAHA 20:11-12", t, B[2] + 0.3, B[3] + 0.2, y=250)


def s4_staff(c, t, u):
    night(c, (10, 8, 22), (40, 28, 44), (70, 46, 34))
    stars(c, t, 0.7, ymax=700)
    lin(c, (0, 1200, W, H), [(0, (110, 76, 50)), (1, (50, 34, 26))])
    c.save(); cam(c, 1 + 0.1 * ease(u), 0, -40 * u, 1.0)
    flames(c, 920, 1000, t, 0.5)
    light(c, 360, 1200, 50, t, 1.0)
    t_throw = wt(6, "Throw"); t_ser = wt(6, "serpent"); t_take = wt(7, "Take")
    if t < t_throw:
        staff(c, 450, 1360, 400, 8)
    elif t < t_ser - 0.3:
        f = ease(clamp((t - t_throw) / 0.5))
        staff(c, 450 + 60 * f, 1360 + 300 * f, 400 - 120 * f, 8 + 75 * f)
    elif t < t_take + 1.8:
        m = ease(clamp((t - (t_ser - 0.3)) / 0.5))
        radial(c, 640, 1620, 260, (255, 220, 140), 0.5 * (1 - m) + 0.1)
        serpent(c, 640, 1620, 520, t, m, 0.6 + 0.4 * m)
    else:
        f = ease(clamp((t - t_take - 1.8) / 0.6))
        radial(c, 560, 1500, 220, (255, 220, 140), 0.4 * (1 - f))
        staff(c, 450, 1360, 400, 8, a=f)
        serpent(c, 640, 1620, 520, t, 1 - f)
    c.restore()
    a = clamp((t - t_ser) / 0.4) * clamp((t_take - t) / 0.4)
    if a > 0:
        text(c, "A LIVING SERPENT", 540, 470, 110, TF_COND, GOLD, a, 0.1)
    lab(c, "TAHA 20:17-21", t, B[3] + 0.3, B[4] + 0.2)


def s5_hand(c, t, u):
    lin(c, (0, 0, W, H), [(0, (12, 10, 26)), (1, (40, 30, 40))])
    stars(c, t, 0.8, ymax=1900)
    fl = clamp((t - wt(8, "shining")) / 0.6)
    light(c, 540, 1100, 64, t, 1.0 + 0.6 * fl)
    if fl > 0:
        radial(c, 540, 1100, 900 * fl, (255, 255, 255), 0.55 * fl)
        for k in range(14):
            ang = k * math.pi / 7 + t * 0.2
            r0, r1 = 120, 120 + 520 * fl
            c.drawLine(540 + math.cos(ang) * r0, 1100 + math.sin(ang) * r0, 540 + math.cos(ang) * r1, 1100 + math.sin(ang) * r1,
                       P((255, 255, 245), 0.35 * fl, stroke=6, blend=skia.BlendMode.kScreen))
    a = clamp((t - wt(8, "harm")) / 0.4)
    if a > 0:
        text(c, "ANOTHER SIGN", 540, 1560, 110, TF_COND, GOLD, a, 0.1)
    lab(c, "TAHA 20:22", t, B[4] + 0.3, B[5] + 0.2)


def s6_pharaoh(c, t, u):
    lin(c, (0, 0, W, 1250), [(0, (60, 14, 18)), (0.7, (170, 70, 40)), (1, (240, 140, 70))])
    radial(c, 540, 1180, 420, (255, 170, 90), 0.5)
    lin(c, (0, 1250, W, H), [(0, (120, 70, 44)), (1, (40, 22, 20))])
    c.save(); cam(c, 1 + 0.14 * ease(u), 0, 0, 1.0)
    for k, x in enumerate((240, 400, 680, 840)):
        column(c, x, 760, 1250, 90, 0.75)
    c.drawRect(skia.Rect.MakeLTRB(160, 700, 920, 770), P((120, 84, 56)))
    tri = skia.Path(); tri.moveTo(160, 700); tri.lineTo(540, 560); tri.lineTo(920, 700); tri.close()
    c.drawPath(tri, P((96, 66, 44)))
    c.restore()
    a = clamp((t - wt(9, "Pharaoh")) / 0.4)
    if a > 0:
        text(c, "GO TO PHARAOH", 540, 1520, 120, TF_COND, CREAM, a, 0.08)
    lab(c, "TAHA 20:24", t, B[5] + 0.3, B[6] + 0.2)


def s7_prayer(c, t, u):
    lin(c, (0, 0, W, H), [(0, (10, 14, 34)), (0.6, (40, 40, 80)), (1, (90, 60, 70))])
    stars(c, t, 0.9, ymax=1300)
    c.save(); cam(c, 1 + 0.1 * ease(u), 0, -30 * u, 1.0)
    lin(c, (0, 1500, W, H), [(0, (60, 40, 44)), (1, (20, 14, 18))])
    ch = clamp((t - wt(10, "chest")) / 1.0)
    radial(c, 540, 1180, 300 + 300 * ch, (255, 220, 150), 0.25 + 0.2 * ch)
    hr = ease(clamp((t - wt(10, "Haaroon")) / 1.0))
    mx = 540 - 110 * hr
    light(c, mx, 1180, 58, t, 1.0)
    if hr > 0:
        light(c, 540 + 130 * hr, 1200, 48 * hr, t + 1.3, 0.9 * hr)
    gr = clamp((t - wt(11, "granted")) / 0.5)
    if gr > 0:
        radial(c, 540, 1190, 700, (255, 236, 190), 0.35 * gr)
    c.restore()
    if hr > 0.05:
        text(c, "HARUN", 540 + 130 * hr, 1400, 64, TF_COND, GOLD, hr * clamp((B[7] - t) / 0.5), 0.12)
    if gr > 0:
        text(c, "GRANTED", 540, 1700, 140, TF_COND, GOLD, gr, 0.1)
    lab(c, "TAHA 20:25-36", t, B[6] + 0.3, B[7] + 0.2)


def s8_end(c, t, u):
    lin(c, (0, 0, W, 1250), [(0, (40, 10, 16)), (1, (150, 60, 40))])
    lin(c, (0, 1250, W, H), [(0, (90, 54, 36)), (1, (30, 18, 16))])
    c.save(); cam(c, 1 + 0.1 * ease(u), 0, 0, 0.6)
    for x in (300, 430, 650, 780):
        column(c, x, 900, 1250, 60, 0.55)
    c.restore()
    w = ease(u)
    light(c, 470, 1700 - 300 * w, 46 - 10 * w, t, 1.0)
    light(c, 610, 1720 - 300 * w, 40 - 8 * w, t + 1.3, 0.9)
    tf = wt(12, "Follow")
    d = ease(clamp((t - tf + 0.6) / 0.8))
    if d > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), P((10, 6, 10), 0.72 * d))
        star_orn(c, 540, 900, 70, t, d)
        text(c, "PART 5", 540, 1170 + 30 * (1 - d), 230, TF_COND, GOLD, d, 0.05)
        f = skia.Font(TF_COND, 96)
        bw = sum(f.measureText(ch) + 0.06 * 96 for ch in "FOLLOW") + 50
        c.drawRect(skia.Rect.MakeXYWH(540 - bw / 2, 1232, bw * ease(clamp((t - tf) / 0.35)), 100), P(GOLD, d))
        text(c, "FOLLOW", 540, 1315, 96, TF_COND, (30, 22, 14), d * clamp((t - tf - 0.1) / 0.3), 0.06)
        text(c, "FACING PHARAOH  ·  COMING NEXT", 540, 1420, 34, TF_SANS, CREAM, d * clamp((t - tf - 0.4) / 0.4), 0.2)
    else:
        lab(c, "TAHA 20:42-43", t, B[7] + 0.3, tf - 0.5)


SCENES = [s1_camp, s2_fire, s3_valley, s4_staff, s5_hand, s6_pharaoh, s7_prayer, s8_end]
LABELS = {1: ("AL-QASAS 28:29-30", "TAHA 20:11")}


def scene_img(i, t):
    if i == 1:
        f = ai_frame(t - B[1])
        if f is not None:
            surf = skia.Surface(W, H)
            with surf as c:
                c.clear(skia.Color(0, 0, 0, 0))
                lab(c, "AL-QASAS 28:29-30", t, B[1] + 0.3, B[2] + 0.2)
            ov = surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType).astype(np.float32)
            al = ov[..., 3:4] / 255.0
            return f * (1 - al) + ov[..., :3] * al
    surf = skia.Surface(W, H)
    with surf as c:
        c.clear(skia.Color(0, 0, 0))
        SCENES[i](c, t, clamp((t - B[i]) / (B[i + 1] - B[i])))
        if i == 1:
            lab(c, "AL-QASAS 28:29-30", t, B[1] + 0.3, B[2] + 0.2)
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
    ap = argparse.ArgumentParser(); ap.add_argument("--probe", default=""); ap.add_argument("--out", default=""); ap.add_argument("--keyframe", action="store_true")
    a = ap.parse_args()
    from PIL import Image
    if a.keyframe:
        surf = skia.Surface(W, H)
        with surf as c:
            c.clear(skia.Color(0, 0, 0)); keyframe(c, 1.0)
        arr = surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)[..., :3]
        (ROOT / "ai").mkdir(exist_ok=True); Image.fromarray(arr).save(ROOT / "ai/keyframe.png"); print("keyframe", B[1], B[2], "scene len", B[2] - B[1])
    if a.probe:
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
