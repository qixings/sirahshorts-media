"""Musa Part 4, anime version. Backgrounds are AI anime stills (Higgsfield Soul) and two AI anime clips (Seedance 2.5),
animated here with slow camera moves, embers, the glowing light (Musa AS, and Harun AS), labels and the end card.
No people are shown.
  python3 paint4a.py --probe 2,7,...      python3 paint4a.py --out out/paint.mp4
"""
import argparse, json, math, pathlib, subprocess, sys, time
import numpy as np
import skia

ROOT = pathlib.Path(__file__).parent
sys.path.insert(0, str(ROOT.parents[1] / "engine" / "core"))
import paint as K
from paint import P, lin, radial, text, light, motes, star_orn, clamp, ease, W, H, FPS, GOLD, CREAM, TF_COND, TF_SANS

TIM = json.loads((ROOT / "audio/timing.json").read_text())
SEG = TIM["segments"]; DUR = TIM["total_duration"]
L = {s["id"]: s["start"] for s in SEG}


def wt(i, word):
    s = next(x for x in SEG if x["id"] == i)
    ws = s["vo"].split(); tot = sum(len(w) for w in ws); acc = 0
    for w in ws:
        if w.lower().strip(".,:!?'\"").startswith(word.lower()):
            return s["start"] + (s["end"] - s["start"]) * acc / tot
        acc += len(w)
    return s["start"]


SERP0 = wt(6, "serpent") - 2.6          # clip time 2.6 s is where the staff turns into the serpent
B = [0.0, L[3] - 0.15, wt(4, "Remove") - 0.25, L[5] - 0.15, SERP0, SERP0 + 5.9, L[8] - 0.15, L[9] - 0.15, L[10] - 0.15, L[12] - 0.15, DUR]
XF = 0.45
lab = K.label
AI = ROOT / "ai"

_img = {}


def img(name):
    if name not in _img:
        _img[name] = skia.Image.open(str(AI / f"a_{name}.png"))
    return _img[name]


def bg(c, name, u, z0=1.0, z1=1.12, ax=0.5, ay=0.5, dark=0.0, warm=None):
    """Draw a still filling the frame with a slow zoom from z0 to z1 around (ax, ay)."""
    im = img(name)
    s = max(W / im.width(), H / im.height()) * (z0 + (z1 - z0) * ease(u))
    w, h = im.width() * s, im.height() * s
    x = (W - w) * ax; y = (H - h) * ay
    c.drawImageRect(im, skia.Rect.MakeXYWH(x, y, w, h), skia.SamplingOptions(skia.FilterMode.kLinear))
    if dark > 0:
        c.drawRect(skia.Rect.MakeWH(W, H), P((6, 6, 16), dark))
    if warm:
        radial(c, *warm)


_clips = {}


def clip_frame(name, t):
    if name not in _clips:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(AI / name), "-vf",
                              f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},fps={FPS}",
                              "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
        _clips[name] = np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)
    fr = _clips[name]
    return fr[min(len(fr) - 1, max(0, int(t * FPS)))].astype(np.float32)


# ------------------------------------------------------------- scenes (skia)
def s1_camp(c, t, u):
    bg(c, "camp", u, 1.0, 1.14, 0.5, 0.75)
    motes(c, t, (255, 190, 110), a=0.3)
    go = ease(clamp((t - wt(2, "flame")) / 2.0))
    light(c, 640 + 60 * go, 1560 - 120 * go, 44, t, 1.0)
    a = clamp((3.8 - t) / 0.6) * clamp(t / 0.5)
    if a > 0:
        lin(c, (0, 0, W, 700), [(0, (6, 6, 14, int(225 * a))), (1, (6, 6, 14, 0))])
        star_orn(c, 540, 300, 58, t, a)
        text(c, "STORIES OF THE PROPHETS", 540, 420, 42, TF_SANS, GOLD, a, 0.24)
        text(c, "PROPHET MUSA  ·  PART 4", 540, 510, 92, TF_COND, CREAM, a, 0.06)
    lab(c, "TAHA 20:9-10", t, 3.7, B[1] + 0.2)


def s3_valley(c, t, u):
    bg(c, "valley", u, 1.0, 1.16, 0.5, 0.7)
    motes(c, t, (255, 180, 90), a=0.4)
    light(c, 760, 1500, 44, t, 1.0)
    a = clamp((t - wt(4, "sacred")) / 0.5)
    if a > 0:
        text(c, "TUWA", 540, 470, 150, TF_COND, GOLD, a, 0.14)
        text(c, "THE SACRED VALLEY", 540, 560, 40, TF_SANS, CREAM, a, 0.24)
    lab(c, "TAHA 20:11-12", t, B[2] + 0.3, B[3] + 0.2)


def s4_staff(c, t, u):
    bg(c, "staff", u, 1.04, 1.12, 0.6, 0.6)
    motes(c, t, (255, 180, 90), a=0.35)
    light(c, 330, 1400, 46, t, 1.0)
    lab(c, "TAHA 20:17-19", t, B[3] + 0.3, B[4] + 0.2)


def s6_returned(c, t, u):
    bg(c, "staff", u, 1.12, 1.0, 0.6, 0.6)
    radial(c, 760, 1350, 300, (255, 220, 150), 0.35 * clamp(1 - (t - B[5]) / 1.5))
    motes(c, t, (255, 180, 90), a=0.35)
    light(c, 330, 1400, 46, t, 1.0)
    lab(c, "TAHA 20:21", t, B[5] + 0.3, B[6] + 0.2)


def s7_hand(c, t, u):
    bg(c, "hill", u, 1.1, 1.2, 0.5, 0.4, dark=0.45)
    fl = clamp((t - wt(8, "shining")) / 0.6)
    light(c, 540, 1180, 62, t, 1.0 + 0.6 * fl)
    if fl > 0:
        radial(c, 540, 1180, 900 * fl, (255, 255, 255), 0.55 * fl)
        for k in range(14):
            ang = k * math.pi / 7 + t * 0.2
            r0, r1 = 120, 120 + 520 * fl
            c.drawLine(540 + math.cos(ang) * r0, 1180 + math.sin(ang) * r0, 540 + math.cos(ang) * r1, 1180 + math.sin(ang) * r1,
                       P((255, 255, 245), 0.35 * fl, stroke=6, blend=skia.BlendMode.kScreen))
    a = clamp((t - wt(8, "harm")) / 0.4)
    if a > 0:
        text(c, "ANOTHER SIGN", 540, 1620, 110, TF_COND, GOLD, a, 0.1)
    lab(c, "TAHA 20:22", t, B[6] + 0.3, B[7] + 0.2)


def s8_pharaoh(c, t, u):
    bg(c, "palace", u, 1.0, 1.15, 0.5, 0.55)
    a = clamp((t - wt(9, "Pharaoh")) / 0.4)
    if a > 0:
        lin(c, (0, 1300, W, H), [(0, (10, 4, 4, 0)), (1, (10, 4, 4, int(200 * a)))])
        text(c, "GO TO PHARAOH", 540, 1600, 120, TF_COND, CREAM, a, 0.08)
    lab(c, "TAHA 20:24", t, B[7] + 0.3, B[8] + 0.2)


def s9_prayer(c, t, u):
    bg(c, "hill", u, 1.0, 1.1, 0.5, 0.6)
    ch = clamp((t - wt(10, "chest")) / 1.0)
    radial(c, 540, 1330, 300 + 300 * ch, (255, 220, 150), 0.22 + 0.18 * ch)
    hr = ease(clamp((t - wt(10, "Haaroon")) / 1.0))
    light(c, 540 - 110 * hr, 1330, 56, t, 1.0)
    if hr > 0:
        light(c, 540 + 130 * hr, 1350, 46 * hr, t + 1.3, 0.9 * hr)
        text(c, "HARUN", 540 + 130 * hr, 1540, 64, TF_COND, GOLD, hr * clamp((B[9] - t) / 0.5), 0.12)
    gr = clamp((t - wt(11, "granted")) / 0.5)
    if gr > 0:
        radial(c, 540, 1340, 700, (255, 236, 190), 0.35 * gr)
        text(c, "GRANTED", 540, 1760, 140, TF_COND, GOLD, gr, 0.1)
    lab(c, "TAHA 20:25-36", t, B[8] + 0.3, B[9] + 0.2)


def s10_end(c, t, u):
    bg(c, "palace", u, 1.15, 1.25, 0.5, 0.55, dark=0.25)
    w = ease(u)
    light(c, 470, 1760 - 260 * w, 44 - 10 * w, t, 1.0)
    light(c, 610, 1780 - 260 * w, 38 - 8 * w, t + 1.3, 0.9)
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
        lab(c, "TAHA 20:42-43", t, B[9] + 0.3, tf - 0.5)


# index -> ("skia", fn) or ("clip", file, label)
SCENES = [("skia", s1_camp), ("clip", "fire_anime.mp4", "AL-QASAS 28:29-30"), ("skia", s3_valley), ("skia", s4_staff),
          ("clip", "serpent_anime.mp4", "TAHA 20:20"), ("skia", s6_returned), ("skia", s7_hand), ("skia", s8_pharaoh),
          ("skia", s9_prayer), ("skia", s10_end)]


def overlay(fn, t):
    surf = skia.Surface(W, H)
    with surf as c:
        c.clear(skia.Color(0, 0, 0, 0)); fn(c)
    a = surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType).astype(np.float32)
    return a[..., :3], a[..., 3:4] / 255.0


def scene_img(i, t):
    kind = SCENES[i]
    if kind[0] == "clip":
        f = clip_frame(kind[1], t - B[i])
        rgb, al = overlay(lambda c: lab(c, kind[2], t, B[i] + 0.3, B[i + 1] + 0.2), t)
        return f * (1 - al) + rgb * al
    surf = skia.Surface(W, H)
    with surf as c:
        c.clear(skia.Color(0, 0, 0))
        kind[1](c, t, clamp((t - B[i]) / (B[i + 1] - B[i])))
    return surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType)[..., :3].astype(np.float32)


def frame(t):
    n = len(SCENES)
    i = max(k for k in range(n) if B[k] <= t) if t < DUR else n - 1
    img_ = scene_img(i, t)
    if i < n - 1 and t > B[i + 1] - XF:
        a = ease((t - (B[i + 1] - XF)) / XF)
        img_ = img_ * (1 - a) + scene_img(i + 1, t) * a
    k = min(clamp(t / 0.5), clamp((DUR - t) / 0.6))
    img_ = img_ * K.VIG * k + K.GRAIN[int(t * FPS) % 6] * 0.6
    return np.clip(img_, 0, 255).astype(np.uint8)


def render_range(f0, f1, out):
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for n in range(f0, f1):
        enc.stdin.write(frame(n / FPS).tobytes())
    enc.stdin.close(); enc.wait()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--probe", default=""); ap.add_argument("--out", default="")
    a = ap.parse_args()
    print("scene starts", [round(b, 2) for b in B])
    if a.probe:
        from PIL import Image
        d = ROOT / "out/probe"; d.mkdir(parents=True, exist_ok=True)
        for ts in a.probe.split(","):
            Image.fromarray(frame(float(ts))).save(d / f"a{float(ts):06.2f}.png")
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
