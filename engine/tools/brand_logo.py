#!/usr/bin/env python3
"""Stamp the Sirah Shorts logo on the last seconds of a finished vertical episode.

Usage: python3 engine/tools/brand_logo.py in.mp4 out.mp4 [--secs 2.2] [--size 420] [--y 0.60]
The logo fades in over a soft dark circle in the lower middle (clear of the captions in the upper third and of the
platform buttons at the bottom), then holds to the end. Audio is copied unchanged.
"""
import argparse, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.join(HERE, "..", "core", "brand", "logo-transparent.png")

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out")
ap.add_argument("--secs", type=float, default=2.2)
ap.add_argument("--size", type=int, default=340)
ap.add_argument("--y", type=float, default=0.22)
a = ap.parse_args()
dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.src]))
st = max(0.0, dur - a.secs)
s = a.size
fc = (f"[1:v]scale={s}:{s},format=rgba,fade=in:st={st}:d=0.6:alpha=1[lg];"
      f"color=black@0.0:s={int(s*1.5)}x{int(s*1.5)},format=rgba,geq=r=0:g=0:b=0:"
      f"a='160*max(0,1-hypot(X-W/2,Y-H/2)/(W/2))'[sh0];[sh0]fade=in:st={st}:d=0.6:alpha=1[sh];"
      f"[0:v][sh]overlay=(W-w)/2:H*{a.y}-h/2:enable='gte(t,{st})'[v1];"
      f"[v1][lg]overlay=(W-w)/2:H*{a.y}-h/2:enable='gte(t,{st})'[v]")
subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", a.src, "-loop", "1", "-t", str(dur), "-i", LOGO,
                "-filter_complex", fc, "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-preset", "slow",
                "-crf", "27", "-tune", "grain", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", "-shortest", a.out], check=True)
print(a.out)
