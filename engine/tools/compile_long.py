#!/usr/bin/env python3
"""Join finished vertical episodes into one 16:9 long-form YouTube video.

Usage:
  python3 engine/tools/compile_long.py --prophet Musa --title "The Early Life" \
      --parts 1:"Saved by the River":videos/musa-part1.mp4 2:"The Flight":videos/musa-part2.mp4 \
      --out out/long/musa-1-3.mp4

Each part keeps its own audio. The vertical video sits in the centre, a blurred and darkened copy fills the
frame, and the side panels name the prophet and the part. A 4 second title card opens the film and a 6 second
end card closes it. Writes <out>.chapters.txt with YouTube chapter timestamps (first chapter at 0:00).
No music, no sound effects.
"""
import argparse, json, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "core", "fonts")
W, H, FPS = 1920, 1080, 30
GOLD, CREAM, DIM = (222, 182, 96), (240, 228, 204), (160, 146, 120)


def font(name, size):
    return ImageFont.truetype(os.path.join(FONTS, name), size)


def centred(d, y, txt, f, fill, x0=0, x1=W):
    w = d.textlength(txt, font=f)
    d.text((x0 + (x1 - x0 - w) / 2, y), txt, font=f, fill=fill)


def wrap(d, txt, f, maxw):
    lines, cur = [], ""
    for word in txt.split():
        t = (cur + " " + word).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = word
    if cur:
        lines.append(cur)
    return lines


def background():
    img = Image.new("RGB", (W, H), (10, 9, 14))
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    ImageDraw.Draw(glow).ellipse((W / 2 - 520, H / 2 - 360, W / 2 + 520, H / 2 + 360), fill=(60, 44, 20))
    return Image.blend(img, glow.filter(ImageFilter.GaussianBlur(220)), 0.9)


LOGO = os.path.join(FONTS, "..", "brand", "logo-transparent.png")


def paste_logo(img, size, cx, cy):
    lg = Image.open(LOGO).convert("RGBA").resize((size, size), Image.LANCZOS)
    img.paste(lg, (int(cx - size / 2), int(cy - size / 2)), lg)


def title_card(path, prophet, title, sub):
    img = background(); paste_logo(img, 300, W / 2, 210); d = ImageDraw.Draw(img)
    centred(d, 390, f"Prophet {prophet} (AS)", font("Cinzel.ttf", 118), GOLD)
    y = 560
    for ln in wrap(d, title, font("Cinzel.ttf", 64), 1500):
        centred(d, y, ln, font("Cinzel.ttf", 64), CREAM); y += 80
    centred(d, y + 30, sub, font("cond.ttf", 46), DIM)
    img.save(path)


def end_card(path, prophet, next_line):
    img = background(); paste_logo(img, 460, W / 2, 330); d = ImageDraw.Draw(img)
    centred(d, 600, next_line, font("cond.ttf", 60), CREAM)
    centred(d, 690, "Subscribe for the next part of the story", font("cond.ttf", 44), DIM)
    img.save(path)


def side_panels(path, prophet, n, title):
    """Transparent overlay with text in the two side bands (each 656px wide)."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    band = (W - 608) // 2
    fl, fs, fb = font("Cinzel.ttf", 56), font("cond.ttf", 40), font("cond.ttf", 120)
    centred(d, 430, "Prophet", fs, DIM, 0, band)
    centred(d, 480, f"{prophet} (AS)", fl, GOLD, 0, band)
    centred(d, 380, "PART", fs, DIM, W - band, W)
    centred(d, 420, str(n), fb, GOLD, W - band, W)
    y = 560
    for ln in wrap(d, title, font("cond.ttf", 52), band - 80):
        centred(d, y, ln.upper(), font("cond.ttf", 52), CREAM, W - band, W); y += 60
    img.save(path)


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit("ffmpeg failed:\n" + r.stderr[-2000:])


def still_clip(png, secs, out):
    run(["ffmpeg", "-y", "-loop", "1", "-t", str(secs), "-i", png, "-f", "lavfi", "-t", str(secs),
         "-i", "anullsrc=r=48000:cl=mono", "-vf", f"fps={FPS},format=yuv420p,fade=in:0:15,fade=out:st={secs-0.5}:d=0.5",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "128k", "-shortest", out])


def part_clip(src, overlay, out):
    fc = ("[0:v]split[a][b];"
          f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},boxblur=40:2,eq=brightness=-0.45:saturation=0.6[bg];"
          f"[b]scale=-2:{H}[fg];[bg][fg]overlay=(W-w)/2:0[v1];[v1][1:v]overlay=0:0,fps={FPS},format=yuv420p[v]")
    run(["ffmpeg", "-y", "-i", src, "-i", overlay, "-filter_complex", fc, "-map", "[v]", "-map", "0:a",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "128k", "-ar", "48000",
         "-ac", "1", out])


def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", p]).strip())


def ts(s):
    s = int(round(s)); return f"{s // 60}:{s % 60:02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prophet", required=True)
    ap.add_argument("--title", required=True, help="Film title, e.g. 'The Early Life'")
    ap.add_argument("--parts", nargs="+", required=True, help="N:Title:path")
    ap.add_argument("--next", default="", help="End card line, e.g. 'Next: Part 4, The Fire on the Mountain'")
    ap.add_argument("--out", required=True)
    ap.add_argument("--crf", default="23", help="Final quality; raise to 26-28 if the file is over 90 MB")
    a = ap.parse_args()
    parts = []
    for p in a.parts:
        n, t, path = p.split(":", 2); parts.append((int(n), t, path))
    first, last = parts[0][0], parts[-1][0]
    tmp = tempfile.mkdtemp()
    clips, chapters, t = [], [], 0.0
    title_card(f"{tmp}/title.png", a.prophet, a.title, f"Parts {first} to {last} · From the Qur'an")
    still_clip(f"{tmp}/title.png", 4, f"{tmp}/00.mp4"); clips.append(f"{tmp}/00.mp4")
    chapters.append((0.0, "Introduction")); t += dur(f"{tmp}/00.mp4")
    for i, (n, title, path) in enumerate(parts, 1):
        side_panels(f"{tmp}/side{i}.png", a.prophet, n, title)
        out = f"{tmp}/{i:02d}.mp4"; part_clip(path, f"{tmp}/side{i}.png", out); clips.append(out)
        chapters.append((t, f"Part {n}: {title}")); t += dur(out)
    end_card(f"{tmp}/end.png", a.prophet, a.next or f"Prophet {a.prophet} (AS) continues")
    still_clip(f"{tmp}/end.png", 6, f"{tmp}/99.mp4"); clips.append(f"{tmp}/99.mp4")
    with open(f"{tmp}/list.txt", "w") as f:
        f.writelines(f"file '{c}'\n" for c in clips)
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", f"{tmp}/list.txt", "-af", "loudnorm=I=-14:TP=-1.5",
         "-c:v", "libx264", "-preset", "veryfast", "-crf", a.crf, "-tune", "grain", "-c:a", "aac", "-b:a", "160k",
         "-movflags", "+faststart", a.out])
    ch = "\n".join(f"{ts(s)} {name}" for s, name in chapters)
    open(a.out + ".chapters.txt", "w").write(ch + "\n")
    # thumbnail 1280x720 from the title card
    Image.open(f"{tmp}/title.png").resize((1280, 720), Image.LANCZOS).save(a.out + ".thumb.jpg", quality=90)
    print(json.dumps({"out": a.out, "duration": round(dur(a.out), 1), "chapters": ch}, indent=1))


if __name__ == "__main__":
    main()
