"""LANE NINE LAB engine v4 — 'Lane 9 is a mystery' format.

0.0  PICK A LANE: start grid, lane 9 = black silhouette '???', countdown 3-2-1 (ticks), VO 'Pick a lane. Lane nine is a secret.'
gun  beat drops, tracking camera on the humans; lane 9 does something insane ('Who IS that?!')
end  25% slow-motion human photo finish (muffled music + heartbeat) -> flash/boom -> results board with lane 9 hidden
     -> REVEAL sting + big reveal card + VO punchline -> question.
"""
import math, os, subprocess
import numpy as np
from PIL import Image, ImageDraw
from race3 import emoji, text, font, dist, time_at, draw_runner, say, KITS, W, H, FPS, YEL, WHT, BG
import music as M

D = os.path.dirname(os.path.abspath(__file__))
SR = M.SR

def dist_any(t, r):
    if r.get("kind") == "cheetah":
        tau = 0.9; T = r["time"]; L = 100.0
        v = L / (T - tau * (1 - math.exp(-T / tau)))
        if t <= 0: return 0.0
        if t < T: return v * (t - tau * (1 - math.exp(-t / tau)))
        return L + 6 * (1 - math.exp(-(t - T) * 0.8))           # slows down and waits after the line
    return dist(t, r["time"])

def draw_cheetah(d, x, yb, s, phase, reveal):
    body = (40, 40, 44) if not reveal else (214, 160, 70); spot = (25, 20, 15)
    L = 150 * s; hgt = 46 * s
    bx0, by = x - L * 0.55, yb - 62 * s - abs(math.sin(phase)) * 8 * s
    d.ellipse((x - 34 * s, yb - 6 * s, x + 34 * s, yb + 6 * s), fill=(110, 36, 26))
    # legs (gallop)
    for k, (lx, ph) in enumerate(((bx0 + L * 0.15, phase), (bx0 + L * 0.25, phase + 0.6), (bx0 + L * 0.85, phase + math.pi), (bx0 + L * 0.95, phase + math.pi + 0.6))):
        a = math.radians(40 * math.sin(ph)); kx, ky = lx + 30 * s * math.sin(a), by + hgt * 0.4 + 30 * s * math.cos(a)
        fx, fy = kx + 26 * s * math.sin(a - 0.8), ky + 26 * s * math.cos(a - 0.8)
        d.line(((lx, by + hgt * 0.3), (kx, ky), (fx, min(fy, yb))), fill=body if k % 2 else tuple(int(c * 0.75) for c in body), width=max(3, int(9 * s)))
    d.ellipse((bx0, by, bx0 + L, by + hgt), fill=body)
    hx, hy = bx0 + L + 6 * s, by - 6 * s
    d.ellipse((hx - 22 * s, hy - 16 * s, hx + 26 * s, hy + 20 * s), fill=body)
    d.line(((bx0 + 4 * s, by + hgt * 0.4), (bx0 - 40 * s, by - 10 * s - 14 * s * math.sin(phase))), fill=body, width=max(3, int(8 * s)))
    if reveal:
        rng = np.random.default_rng(1)
        for _ in range(26):
            sx_, sy_ = bx0 + rng.uniform(0.1, 0.9) * L, by + rng.uniform(0.15, 0.85) * hgt
            d.ellipse((sx_ - 4 * s, sy_ - 4 * s, sx_ + 4 * s, sy_ + 4 * s), fill=spot)
    return hx, hy - 16 * s

def render(spec):
    R = spec["racers"]; n = len(R)
    for r in R: r["kit"] = KITS.get(r.get("flag", ""), ((40, 40, 44), (40, 40, 44)))
    humans = [r for r in R if not r.get("mystery")]
    myst = [r for r in R if r.get("mystery")][0]
    hord = sorted(humans, key=lambda r: r["time"]); T1, TL = hord[0]["time"], max(r["time"] for r in humans)
    full_order = sorted(R, key=lambda r: r["time"])
    # ---------- timeline ----------
    t_gun = spec.get("pick_len", 3.0)
    rs0 = T1 - 0.5; t_slow0 = t_gun + rs0; slow_rate = 0.28; rs1 = TL + 0.25
    t_slow1 = t_slow0 + (rs1 - rs0) / slow_rate
    t_flash = t_slow1; t_board = t_flash + 1.2; t_reveal = t_board + spec.get("reveal_delay", 2.2)
    def race_t(vt):
        if vt < t_gun: return 0.0
        if vt < t_slow0: return vt - t_gun
        if vt < t_slow1: return rs0 + (vt - t_slow0) * slow_rate
        return rs1
    # ---------- voice ----------
    lines = [("v0", spec["pick_tts"], spec["pick_disp"], 0.15),
             ("v1", "And they're off!", "AND THEY'RE OFF!", t_gun + 0.2),
             ("v2", spec["mid_tts"], spec["mid_disp"], t_gun + spec.get("mid_at", 2.4)),
             ("v3", f"{hord[0].get('say', hord[0]['label'])} leads the humans!", f"{hord[0]['label']} {hord[0].get('tag','')} LEADS THE HUMANS!", t_gun + time_at(62, T1)),
             ("v4", "Photo finish!", "PHOTO FINISH!", t_slow0 + 0.1),
             ("v5", spec["reveal_tts"], spec["reveal_disp"], t_reveal + 0.15),
             ("v6", spec["q_tts"], spec["q_disp"], None)]
    speech, caps, t_end = [], [], 0
    for key, tts, disp, at in lines:
        wav, dur, ws = say(spec["out"] + "_" + key, tts, disp, length=0.82)
        at = t_end + 0.25 if at is None else max(at, t_end + 0.05)
        speech.append((wav, at)); t_end = at + dur
        cur = []
        for a, b, w in ws:
            cur.append((a, b, w))
            if len(cur) == 3 or w[-1] in ".?!,":
                caps.append((at + cur[0][0], at + cur[-1][1] + 0.12, " ".join(x[2] for x in cur).upper())); cur = []
        if cur: caps.append((at + cur[0][0], at + cur[-1][1] + 0.12, " ".join(x[2] for x in cur).upper()))
    total = t_end + 1.0
    for i in range(len(caps) - 1):
        a, b, s_ = caps[i]; caps[i] = (a, min(max(b, a + 0.45), caps[i + 1][0]), s_)
    # ---------- geometry ----------
    top_track, bot_track = 700, 1500
    lh = [58 + (112 - 58) * k / (n - 1) for k in range(n)]; sc = sum(lh) / (bot_track - top_track); lane_h = [h / sc for h in lh]
    lane_y = [top_track + sum(lane_h[:k]) for k in range(n + 1)]
    PXM = spec.get("pxm", 48.0)
    wd = os.path.join(D, "work", spec["out"]); os.makedirs(wd, exist_ok=True); vid = os.path.join(wd, "video.mp4")
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                             "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", vid], stdin=subprocess.PIPE)
    crowd = np.random.default_rng(9).uniform(0, 1, (900, 3))
    ticks = []
    for fi in range(int(total * FPS)):
        vt = fi / FPS
        if vt < t_gun: mode = "pick"; rt = 0.0
        else:
            rt = race_t(vt); mode = "slow" if t_slow0 <= vt < t_slow1 else ("race" if vt < t_slow0 else "done")
        ds = [dist_any(rt, r) if mode != "pick" else 0.0 for r in R]
        hum_d = max(ds[k] for k in range(n) if not R[k].get("mystery"))
        camx = 8 if hum_d < 8 else hum_d - 2.5
        if mode in ("slow", "done") or hum_d > 96: camx = 97.8
        zoom = 1.0
        if mode == "pick": zoom = 1.0 + 0.04 * vt
        elif mode == "slow": zoom = 1.0 + 0.55 * min(1.0, (vt - t_slow0) / max(0.1, t_slow1 - t_slow0)) ** 0.7
        elif mode == "done": zoom = 1.55
        im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
        # stands
        for y in range(440, top_track):
            c = int(18 + 30 * (y - 440) / (top_track - 440)); d.line((0, y, W, y), fill=(c, c, c + 8))
        par = camx * PXM * 0.35
        for cx_, cy_, cc in crowd:
            x = (cx_ * 2600 - par) % 2600 - 260; y = 470 + cy_ * 210
            col = [(200, 60, 60), (240, 240, 240), (60, 90, 200), (240, 200, 40), (90, 90, 90)][int(cc * 5)]
            bob = 3 * math.sin(vt * 9 + cx_ * 50) if mode in ("race", "slow") else 0
            d.ellipse((x - 5, y - 5 + bob, x + 5, y + 5 + bob), fill=col)
        d.rectangle((0, top_track - 18, W, top_track), fill=(40, 40, 48))
        for k in range(n):
            myl = R[k].get("mystery")
            col = ((176, 58, 42) if k % 2 == 0 else (160, 50, 37)) if not myl else (70, 40, 90)
            d.rectangle((0, lane_y[k], W, lane_y[k + 1]), fill=col)
            d.line((0, lane_y[k], W, lane_y[k]), fill=(235, 235, 235), width=2)
        d.line((0, bot_track, W, bot_track), fill=(235, 235, 235), width=3)
        sx = lambda m, k: 540 + (m - camx) * PXM * (lane_h[min(k, n - 1)] / lane_h[-1]) * zoom
        for m in range(0, 101, 5):
            pts = [(sx(m, k), lane_y[k]) for k in range(n)] + [(sx(m, n - 1), bot_track)]
            if all(p[0] < -50 or p[0] > W + 50 for p in pts): continue
            d.line(pts, fill=(215, 110, 95), width=2)
            if m % 10 == 0: text(d, (sx(m, n - 1), bot_track + 26), f"{m}M", 26, (230, 230, 230), stroke=3)
        for k in range(n):
            x0 = sx(100, k); hgt = lane_h[k]; cs = max(6, int(hgt / 5))
            for j in range(int(hgt / cs) + 1):
                for q in range(2):
                    c = WHT if (j + q) % 2 == 0 else (0, 0, 0)
                    d.rectangle((x0 + q * cs, lane_y[k] + j * cs, x0 + q * cs + cs, min(lane_y[k + 1], lane_y[k] + j * cs + cs)), fill=c)
        d.line([(sx(0, k), lane_y[k]) for k in range(n)] + [(sx(0, n - 1), bot_track)], fill=WHT, width=4)
        if mode == "race" and hum_d > 12:
            for j in range(16):
                y = top_track + (j * 53 + fi * 7) % (bot_track - top_track); x = (j * 197 + fi * 41) % W
                d.line((x, y, x + 120, y), fill=(220, 120, 100), width=2)
        lead_k = max((k for k in range(n) if not R[k].get("mystery")), key=lambda k: ds[k]) if mode in ("race", "slow") else None
        revealed = vt >= t_reveal
        for k in range(n):
            r = R[k]; s = lane_h[k] / lane_h[-1] * zoom; m = ds[k]; x = sx(m, k); yb = lane_y[k + 1] - 4 * s
            ht = lane_h[-1] * 2.05
            if r.get("mystery") and x > W + 60:
                # off-screen ahead: pulsing arrow
                p = 0.6 + 0.4 * math.sin(vt * 12)
                text(d, (W - 70, lane_y[k] + lane_h[k] / 2), f"??? {m:.0f}M ▶", int(30 * p + 10), YEL, anchor="rm", stroke=4)
                continue
            if x < -150 or x > W + 150: continue
            if r.get("kind") == "cheetah":
                hx, hy = draw_cheetah(d, x, yb, s * 1.1, m / 3.2 * 2 * math.pi, revealed)
            elif mode == "pick":
                draw_runner(d, x - 10 * s, yb, s, r["kit"] if not r.get("mystery") else ((30, 30, 34), (30, 30, 34)), 0, "set", 0, ht)
                hx, hy = x, yb - ht * 0.6 * s
            else:
                lean = 45 - 33 * min(1, m / 30)
                if 98.5 < m < 100.6: lean = 34
                kit = r["kit"] if (not r.get("mystery") or revealed) else ((25, 25, 28), (25, 25, 28))
                hx, hy = draw_runner(d, x, yb, s, kit, m / 2.35 * 2 * math.pi, "run", lean, ht)
            if r.get("mystery") and not revealed:
                text(d, (hx, hy - 30 * s), "?", int(40 * s + 14), YEL, stroke=5)
            if k == lead_k:
                d.polygon([(hx - 14 * s, hy - 26 * s), (hx + 14 * s, hy - 26 * s), (hx, hy - 6 * s)], fill=YEL, outline=(0, 0, 0))
        # lane tags
        compact = mode in ("slow", "done")
        for k in range(n):
            r = R[k]; yc = lane_y[k] + lane_h[k] / 2; hh = max(26, lane_h[k] * 0.66); tw = 170 if compact else 380
            ov = Image.new("RGBA", (tw, int(hh)), (0, 0, 0, 165)); im.paste(ov, (0, int(yc - hh / 2)), ov); d = ImageDraw.Draw(im)
            text(d, (24, yc), str(k + 1), int(hh * 0.62), YEL, stroke=3)
            if r.get("mystery") and not revealed:
                text(d, (52, yc), "???" if compact else "???  MYSTERY", int(hh * 0.52), YEL, anchor="lm", stroke=3, maxw=tw - 60)
            else:
                e = emoji(r.get("flag", "🐆"), int(hh * 0.6)); im.paste(e, (48, int(yc - e.height / 2)), e)
                if not compact:
                    text(d, (48 + e.width + 8, yc), f"{r['label']} {r.get('tag','')}", int(hh * 0.5), WHT, anchor="lm", stroke=3, maxw=tw - e.width - 64)
                else:
                    text(d, (48 + e.width + 6, yc), r.get("tag", ""), int(hh * 0.42), WHT, anchor="lm", stroke=3, maxw=tw - e.width - 56)
        # header + clock
        d.rectangle((0, 0, W, 430), fill=BG)
        text(d, (W // 2, 105), spec["title"][0], 74, YEL); text(d, (W // 2, 195), spec["title"][1], 64, WHT)
        text(d, (W // 2, 268), spec["sub"], 32, (190, 190, 190), stroke=3)
        clock = min(rt, TL)
        d.rounded_rectangle((330, 312, 750, 412), radius=22, fill=(0, 0, 0), outline=YEL if mode in ("slow", "done") else (90, 90, 90), width=4)
        text(d, (W // 2, 362), f"{clock:05.2f}", 70, YEL if mode in ("slow", "done") else WHT)
        # PICK phase overlay
        if mode == "pick":
            text(d, (W // 2, 560), "PICK A LANE 👇" if False else "PICK A LANE", 96, YEL, stroke=10)
            text(d, (W // 2, 650), "LANE 9 IS A SECRET", 44, WHT, stroke=5)
            cnt = 3 - int(vt / (t_gun / 3))
            if cnt >= 1:
                fr = (vt % (t_gun / 3)) / (t_gun / 3); size = int(220 - 60 * fr)
                text(d, (W // 2, 1100), str(cnt), size, WHT, stroke=12)
        if mode == "race" and vt - t_gun < 0.5:
            text(d, (W // 2, 600), "GO!", 130, YEL, stroke=10)
        if mode == "slow":
            text(d, (W // 2, 600), "SLOW MOTION", 56, YEL, stroke=6)
        if t_flash <= vt < t_flash + 0.12:
            im = Image.blend(im, Image.new("RGB", (W, H), WHT), 0.75); d = ImageDraw.Draw(im)
        if mode == "done" and vt < t_board:
            d.line((sx(100, 0) + 10, top_track, sx(100, n - 1) + 10, bot_track), fill=YEL, width=5)
            text(d, (W // 2, 600), "PHOTO FINISH", 84, YEL, stroke=8)
        if vt >= t_board:
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            od.rounded_rectangle((50, 450, W - 50, 1510), radius=34, fill=(8, 8, 12, 238)); im.paste(ov, (0, 0), ov); d = ImageDraw.Draw(im)
            text(d, (W // 2, 525), "OFFICIAL RESULT", 64, YEL)
            rows = full_order; rh = (1490 - 610) / len(rows)
            for j, r in enumerate(rows):
                if vt - t_board < j * 0.1:
                    continue
                yy = int(610 + j * rh + rh / 2); col = YEL if j == 0 else WHT
                if j == 0: d.rounded_rectangle((80, yy - rh / 2 + 4, W - 80, yy + rh / 2 - 4), radius=16, fill=(60, 50, 0))
                text(d, (120, yy), f"{j + 1}", 46, col, anchor="lm")
                if r.get("mystery") and not revealed:
                    text(d, (190, yy), "???  LANE 9", 44, YEL, anchor="lm", stroke=5)
                else:
                    e = emoji(r.get("flag", "🐆"), 54); im.paste(e, (190, yy - 27), e)
                    text(d, (270, yy), f"{r['label']} {r.get('tag','')}", 42, col, anchor="lm", stroke=5, maxw=560)
                text(d, (W - 120, yy), "?.??" if (r.get("mystery") and not revealed) else f"{r['time']:.2f}", 46, col, anchor="rm")
            if revealed:
                p = min(1, (vt - t_reveal) / 0.25)
                ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
                od.rounded_rectangle((90, 700, W - 90, 1300), radius=40, fill=(20, 14, 30, int(245 * p)), outline=YEL, width=6)
                im.paste(ov, (0, 0), ov); d = ImageDraw.Draw(im)
                text(d, (W // 2, 780), "LANE 9 WAS...", 60, WHT, stroke=6)
                text(d, (W // 2, 880), spec["reveal_title"], int(84 * (0.7 + 0.3 * p)), YEL, stroke=9)
                if myst.get("kind") == "cheetah":
                    draw_cheetah(d, W // 2 + 20, 1170, 1.9, vt * 9, True)
                else:
                    e = emoji(myst.get("flag", "❓"), 150); im.paste(e, (W // 2 - e.width // 2, 990), e)
                text(d, (W // 2, 1255), spec["reveal_sub"], 36, WHT, stroke=4, maxw=860)
        # captions
        for a, b, s_ in caps:
            if a <= vt < b:
                hi = any(w in s_ for w in ("LANE", "SECRET", "WHO", "THAT", "LEADS", "PHOTO", "CHEETAH", "9.58", "OFF", "WAS"))
                text(d, (W // 2, 1650), s_, 84, YEL if hi else WHT, stroke=9, maxw=1000)
        text(d, (W // 2, 1830), "LANE NINE LAB", 30, (170, 170, 170), stroke=3)
        d.rectangle((0, H - 12, int(W * vt / total), H), fill=YEL)
        proc.stdin.write(im.tobytes())
    proc.stdin.close(); proc.wait()
    return vid, total, dict(gun=t_gun, slow0=t_slow0, slow1=t_slow1, board=t_board, reveal=t_reveal, n_rows=n), speech

def build_audio(total, ev, speech, out_wav):
    n = int(total * SR)
    mus = M.track(total, ev["gun"], ev["slow0"], ev["slow1"], ev["board"])
    sfx = np.zeros(n)
    step = ev["gun"] / 3
    for i in range(3):
        M.place(sfx, M.beep(660 if i < 2 else 660, 0.16), i * step + 0.05, 0.5)
        for q in range(4): M.place(sfx, M.tick(1700), i * step + 0.05 + q * step / 4, 0.25)
    M.place(sfx, M.riser(ev["gun"] * 0.9), ev["gun"] * 0.1, 0.35)
    M.place(sfx, M.gun(), ev["gun"], 1.0); M.place(sfx, M.boom(1.2), ev["gun"], 0.6)
    t = ev["slow0"]
    while t < ev["slow1"]:
        M.place(sfx, M.heartbeat(), t, 1.0); t += 0.72
    M.place(sfx, M.boom(1.8), ev["slow1"], 1.1)
    for j in range(ev["n_rows"]): M.place(sfx, M.pluck(880 + j * 40, 0.12), ev["board"] + j * 0.1, 0.35)
    M.place(sfx, M.riser(1.6), ev["reveal"] - 1.6, 0.4)
    M.place(sfx, M.sting(), ev["reveal"], 1.0)
    sp = np.zeros(n)
    for path, t0 in speech:
        a = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"],
                                         capture_output=True).stdout, dtype=np.int16).astype(np.float64) / 32768
        M.place(sp, a, t0, 1.0)
    env = np.convolve((np.abs(sp) > 0.02).astype(float), np.ones(int(0.25 * SR)) / int(0.25 * SR), "same")
    duck = 1 - 0.5 * np.clip(env * 4, 0, 1)
    mix = mus * 0.42 * duck + sfx * 0.55 + sp * 1.25
    mix /= max(1e-9, np.abs(mix).max()) / 0.95
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f64le", "-ar", str(SR), "-ac", "1", "-i", "-", "-ac", "2", out_wav],
                   input=mix.astype(np.float64).tobytes(), check=True)

def build(spec):
    vid, total, ev, speech = render(spec)
    wav = os.path.join(os.path.dirname(vid), "audio.wav"); build_audio(total, ev, speech, wav)
    out = os.path.join(D, "out", spec["out"] + ".mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vid, "-i", wav, "-filter_complex", "[1:a]loudnorm=I=-14:TP=-1.5:LRA=11[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest",
                    "-aspect", "9:16", "-movflags", "+faststart", out], check=True)
    print(spec["out"], f"{total:.1f}s"); return out, total
