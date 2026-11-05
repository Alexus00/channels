"""Photo-finish race generator: real recorded times -> vertical race Short (1080x1920, 30fps)."""
import json, math, os, subprocess, sys, wave, struct
from PIL import Image, ImageDraw, ImageFont
D = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(D, "..", "..", "fonts", "Montserrat.ttf")
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
W, H, FPS = 1080, 1920, 30
YEL, WHT, RED, BG = (255, 214, 0), (255, 255, 255), (255, 60, 60), (12, 14, 18)
TRACK = (178, 60, 44); TRACK2 = (160, 52, 38)

def f(size): return ImageFont.truetype(FONT, size)
EF = ImageFont.truetype(EMOJI, 109)
_emo = {}
def emoji(ch, size):
    k = (ch, size)
    if k not in _emo:
        im = Image.new("RGBA", (136, 128), (0, 0, 0, 0)); ImageDraw.Draw(im).text((0, 0), ch, font=EF, embedded_color=True)
        im = im.crop(im.getbbox()); r = size / im.height
        _emo[k] = im.resize((max(1, int(im.width * r)), size), Image.LANCZOS)
    return _emo[k]

def dist(t, T, tau=1.25, L=100.0):
    """sprint model d(t)=v*(t - tau*(1-e^{-t/tau})), v chosen so d(T)=L"""
    if t <= 0: return 0.0
    v = L / (T - tau * (1 - math.exp(-T / tau)))
    return min(L, v * (t - tau * (1 - math.exp(-t / tau)))) if t < T else L + (t - T) * v * 0.15

def text(d, xy, s, size, fill, anchor="mm", stroke=6, maxw=1020):
    fn = f(size)
    while d.textlength(s, font=fn) > maxw and size > 16:
        size -= 2; fn = f(size)
    d.text(xy, s, font=fn, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0))

def render(spec):
    R = spec["racers"]; n = len(R)
    T_end = max(r["time"] for r in R); start = spec.get("start", 0.8)
    race_len = T_end + 0.3; freeze = 0.9; board = spec.get("board", 4.2)
    total = start + race_len + freeze + board
    top, bot = 430, 1560; lane_h = (bot - top) / n
    x0, x1 = 210, 1000      # start / finish x
    order = sorted(R, key=lambda r: r["time"])
    caps = spec.get("caps", [])
    wd = os.path.join(D, "work", spec["out"]); os.makedirs(wd, exist_ok=True)
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                             "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", os.path.join(wd, "video.mp4")], stdin=subprocess.PIPE)
    nf = int(total * FPS)
    for i in range(nf):
        t = i / FPS; rt = min(t - start, race_len)       # race clock
        finished = t >= start + race_len
        im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
        # header
        text(d, (W // 2, 120), spec["title"][0], 70, YEL); text(d, (W // 2, 210), spec["title"][1], 62, WHT)
        text(d, (W // 2, 290), spec.get("sub", ""), 34, (200, 200, 200), stroke=3)
        # timer
        clock = max(0.0, min(rt, T_end)) if t >= start else 0.0
        text(d, (W // 2, 375), f"{clock:05.2f}s", 64, WHT if not finished else YEL)
        # track
        for k in range(n):
            y = top + k * lane_h
            d.rectangle((0, y, W, y + lane_h), fill=TRACK if k % 2 == 0 else TRACK2)
            d.line((0, y, W, y), fill=(240, 240, 240), width=3)
        d.line((0, bot, W, bot), fill=(240, 240, 240), width=3)
        # camera: zoom into the last metres as the leader approaches (broadcast-style)
        lead = max(dist(rt, r["time"]) for r in R) if t >= start else 0
        z = min(1.0, max(0.0, (lead - 50) / 42)); z = z * z * (3 - 2 * z)
        span = 100 - z * (100 - spec.get("zoom_span", 14)); wend = 100 + span * 0.04; wst = wend - span
        X = lambda m: x0 + (x1 - x0) * (m - wst) / span
        step = 10 if span > 40 else (5 if span > 20 else 1)
        m0 = int(math.ceil(max(0, wst) / step) * step)
        for m in range(m0, 101, step):
            xm = int(X(m))
            if xm < x0: continue
            d.line((xm, top, xm, bot), fill=(205, 95, 80), width=2)
            if m % (5 if step == 1 else step) == 0:
                text(d, (xm, bot + 22), f"{m}m", 22, (220, 220, 220), stroke=3)
        fx = int(X(100))
        for k in range(int((bot - top) / 20)):
            d.rectangle((fx, top + k * 20, fx + 10, top + k * 20 + 20), fill=WHT if k % 2 == 0 else (0, 0, 0))
            d.rectangle((fx + 10, top + k * 20, fx + 20, top + k * 20 + 20), fill=(0, 0, 0) if k % 2 == 0 else WHT)
        if z > 0.05: text(d, (W - 20, top - 22), "PHOTO FINISH CAM", 24, YEL, anchor="rm", stroke=3)
        # lane label column
        d.rectangle((0, top, x0 - 10, bot), fill=(20, 20, 26))
        # runners
        for k, r in enumerate(R):
            yc = int(top + k * lane_h + lane_h / 2)
            text(d, (14, yc - 20), r["label"], 32, WHT, anchor="lm", stroke=4, maxw=x0 - 24)
            text(d, (14, yc + 20), r.get("tag", ""), 26, (230, 230, 230), anchor="lm", stroke=3, maxw=x0 - 24)
            dd = dist(rt, r["time"]) if t >= start else 0
            x = int(X(min(dd, 100 + span * 0.025)))
            x = max(x0 + 30, x)
            if t >= start and dd < 100:
                d.line((max(x0, x - 90), yc, x, yc), fill=(255, 235, 200), width=5)
            e = emoji(r["flag"], int(lane_h * 0.72)); im.paste(e, (x - e.width // 2, yc - e.height // 2), e)
            if rt >= r["time"]:
                rank = order.index(r) + 1
                col = YEL if rank == 1 else WHT
                text(d, (x - e.width // 2 - 12, yc), f"#{rank} {r['time']:.2f}", 30, col, anchor="rm", stroke=5)
        # photo finish flash + results board
        tb = t - (start + race_len)
        if 0 <= tb < 0.12:
            im = Image.blend(im, Image.new("RGB", (W, H), WHT), 0.7); d = ImageDraw.Draw(im)
        if tb >= freeze:
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            od.rounded_rectangle((60, top - 10, W - 60, bot + 10), radius=30, fill=(10, 10, 14, 235))
            im.paste(ov, (0, 0), ov); d = ImageDraw.Draw(im)
            text(d, (W // 2, top + 60), spec.get("board_title", "FINAL RESULTS"), 60, YEL)
            rows = order[: spec.get("board_rows", 10)]; rh = (bot - top - 150) / len(rows)
            for j, r in enumerate(rows):
                yy = int(top + 140 + j * rh + rh / 2)
                show = tb - freeze > j * 0.12
                if not show: continue
                col = YEL if j == 0 else WHT
                text(d, (110, yy), f"{j + 1}.", 44, col, anchor="lm")
                e = emoji(r["flag"], 52); im.paste(e, (190, yy - 26), e)
                text(d, (270, yy), f"{r['label']} {r.get('tag','')}", 40, col, anchor="lm", stroke=5)
                text(d, (W - 110, yy), f"{r['time']:.2f}", 44, col, anchor="rm")
        # captions (word-timed narration)
        for (a, b, s, c) in caps:
            if a <= t < b:
                text(d, (W // 2, 1720), s, 80, YEL if c else WHT, stroke=8)
        # progress bar + brand
        d.rectangle((0, H - 14, int(W * t / total), H), fill=YEL)
        text(d, (W // 2, H - 60), spec.get("brand", ""), 30, (200, 200, 200), stroke=3)
        proc.stdin.write(im.tobytes())
    proc.stdin.close(); proc.wait()
    return os.path.join(wd, "video.mp4"), total, start, race_len

def beep(path, freq=880, dur=0.22, vol=0.5, sr=48000):
    with wave.open(path, "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(b"".join(struct.pack("<h", int(vol * 32767 * math.sin(2 * math.pi * freq * i / sr) * min(1, (dur * sr - i) / 2000))) for i in range(int(dur * sr))))

def build(spec):
    vid, total, start, race_len = render(spec)
    wd = os.path.dirname(vid)
    beep(os.path.join(wd, "go.wav"), 1046, 0.25)
    beep(os.path.join(wd, "fin.wav"), 660, 0.35, 0.4)
    ins = ["-i", vid, "-f", "lavfi", "-t", f"{total}", "-i", "anullsrc=r=48000:cl=stereo", "-i", os.path.join(wd, "go.wav"), "-i", os.path.join(wd, "fin.wav")]
    flt = [f"[2:a]adelay={int(start*1000)}|{int(start*1000)}[g]", f"[3:a]adelay={int((start+race_len)*1000)}|{int((start+race_len)*1000)}[fn]"]
    mix = ["[1:a]", "[g]", "[fn]"]
    for j, (path, at) in enumerate(spec.get("narr", [])):
        ins += ["-i", path]; idx = 4 + j
        flt.append(f"[{idx}:a]aresample=48000,adelay={int(at*1000)}|{int(at*1000)},volume=1.7[n{j}]"); mix.append(f"[n{j}]")
    flt.append("".join(mix) + f"amix=inputs={len(mix)}:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9[a]")
    out = os.path.join(D, "out", spec["out"] + ".mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(flt), "-map", "0:v", "-map", "[a]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", "-aspect", "9:16", "-movflags", "+faststart", out], check=True)
    print(spec["out"], f"{total:.1f}s"); return out, total
