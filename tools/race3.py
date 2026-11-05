"""LANE NINE LAB race engine v3 — broadcast-style race Short from real recorded times.

Timeline: cold-open photo finish ("WHO WON THIS?") -> rewind -> SET -> gun -> tracking camera race with
live commentary + 50m split -> 25% slow-motion finish with heartbeat -> flash + photo-finish tags -> results board.
All visuals and audio are generated here (no third-party footage or music).
"""
import json, math, os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

D = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(D, "..", "..", "fonts", "Montserrat.ttf")
EMOJI = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
VOICE = os.path.join(D, "..", "streamrewind", "voice", "en_US-ryan-high.onnx")
W, H, FPS, SR = 1080, 1920, 30, 48000
YEL, WHT, RED, BG = (255, 214, 0), (255, 255, 255), (255, 60, 60), (10, 12, 16)
KITS = {"🇺🇸": ((25, 45, 120), (200, 30, 45)), "🇯🇲": ((0, 150, 60), (255, 210, 0)), "🇬🇧": ((20, 40, 110), (220, 30, 40)),
        "🇨🇦": ((210, 25, 35), (255, 255, 255)), "🇮🇹": ((0, 90, 180), (255, 255, 255)), "🇫🇷": ((20, 50, 140), (230, 30, 40)),
        "🇳🇬": ((0, 135, 80), (255, 255, 255)), "🇰🇪": ((0, 0, 0), (190, 0, 0)), "🇿🇦": ((0, 120, 70), (255, 185, 0)),
        "🇯🇵": ((255, 255, 255), (200, 0, 40)), "🇧🇷": ((255, 220, 0), (0, 150, 60))}

_fc = {}
def font(size):
    if size not in _fc: _fc[size] = ImageFont.truetype(FONT, size)
    return _fc[size]
EF = ImageFont.truetype(EMOJI, 109)
_emo = {}
def emoji(ch, size):
    k = (ch, size)
    if k not in _emo:
        im = Image.new("RGBA", (136, 128), (0, 0, 0, 0)); ImageDraw.Draw(im).text((0, 0), ch, font=EF, embedded_color=True)
        im = im.crop(im.getbbox()); r = size / im.height
        _emo[k] = im.resize((max(1, int(im.width * r)), max(1, size)), Image.LANCZOS)
    return _emo[k]

def text(d, xy, s, size, fill, anchor="mm", stroke=6, maxw=1030):
    fn = font(size)
    while d.textlength(s, font=fn) > maxw and size > 14:
        size -= 2; fn = font(size)
    d.text(xy, s, font=fn, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(0, 0, 0))

# ---------------- physics ----------------
TAU = 1.25
def dist(t, T, L=100.0):
    if t <= 0: return 0.0
    v = L / (T - TAU * (1 - math.exp(-T / TAU)))
    if t < T: return v * (t - TAU * (1 - math.exp(-t / TAU)))
    return L + (t - T) * v * 0.55 * math.exp(-(t - T) * 1.5)      # decelerate after the line
def time_at(m, T):
    lo, hi = 0.0, T
    for _ in range(40):
        mid = (lo + hi) / 2
        if dist(mid, T) < m: lo = mid
        else: hi = mid
    return hi

# ---------------- runner sprite ----------------
def draw_runner(d, x, yb, s, kit, phase, mode, lean, spec_ht=150):
    """side view runner facing right. yb = feet baseline. s = scale (1 = front lane)."""
    shirt, short = kit; skin = (58, 42, 36)
    Ht = spec_ht * s; th = 0.26 * Ht; sh = 0.26 * Ht; torso = 0.30 * Ht; head = 0.085 * Ht
    lw = max(3, int(13 * s)); aw = max(3, int(10 * s))
    d.ellipse((x - 34 * s, yb - 6 * s, x + 34 * s, yb + 6 * s), fill=(110, 36, 26))      # shadow
    if mode == "set":
        hip = (x - 6 * s, yb - 0.30 * Ht)
        neck = (hip[0] + torso * 0.92, hip[1] - torso * 0.38)
        legs = [((hip[0] - th * 0.4, yb - th * 0.6), (hip[0] - th * 0.95, yb)), ((hip[0] + th * 0.15, yb - th * 0.55), (hip[0] + th * 0.05, yb))]
        arms = [((neck[0] + 4 * s, neck[1] + sh * 0.5), (neck[0] + 6 * s, yb)), ((neck[0] + 10 * s, neck[1] + sh * 0.5), (neck[0] + 14 * s, yb))]
    else:
        a = math.radians(lean)
        hip = (x, yb - (th + sh) * 0.93 - abs(math.sin(phase)) * 5 * s)
        neck = (hip[0] + torso * math.sin(a), hip[1] - torso * math.cos(a))
        legs, arms = [], []
        for side in (0, 1):
            ph = phase + side * math.pi
            ta = math.radians(38 * math.sin(ph))                     # thigh swing
            ka = math.radians(10 + 55 * (0.5 + 0.5 * math.sin(ph + 1.8)))   # knee bend
            knee = (hip[0] + th * math.sin(ta), hip[1] + th * math.cos(ta))
            foot = (knee[0] + sh * math.sin(ta - ka), knee[1] + sh * math.cos(ta - ka))
            legs.append((knee, foot))
            aa = math.radians(-45 * math.sin(ph))
            elb = (neck[0] + sh * 0.75 * math.sin(aa + a * 0.3), neck[1] + 8 * s + sh * 0.75 * math.cos(aa))
            hand = (elb[0] + sh * 0.7 * math.sin(aa + 1.2), elb[1] - sh * 0.35 * math.cos(aa + 1.2) + sh * 0.25)
            arms.append((elb, hand))
    # back limbs first (darker), torso, front limbs
    dark = tuple(int(c * 0.65) for c in skin)
    for (k_, f_), col in ((legs[1], dark), ):
        d.line((hip, k_, f_), fill=col, width=lw, joint="curve")
    for (e_, h_), col in ((arms[1], dark), ):
        d.line((neck, e_, h_), fill=col, width=aw, joint="curve")
    d.line((hip, legs[0][0]), fill=short, width=int(lw * 1.5))
    d.line((hip, neck), fill=shirt, width=int(lw * 2.1))
    d.line((hip, legs[0][0], legs[0][1]), fill=skin, width=lw, joint="curve")
    d.line(((hip[0] - 2, hip[1]), (hip[0] + 6 * s, hip[1] + 10 * s)), fill=short, width=int(lw * 1.8))
    hx, hy = neck[0] + head * 0.55, neck[1] - head * 0.9
    d.ellipse((hx - head, hy - head, hx + head, hy + head), fill=skin)
    d.line((neck, arms[0][0], arms[0][1]), fill=skin, width=aw, joint="curve")
    return hx, hy - head

# ---------------- audio synth ----------------
def noise(n, color="pink", seed=0):
    r = np.random.default_rng(seed).standard_normal(n)
    if color == "white": return r
    f = np.fft.rfft(r); fr = np.fft.rfftfreq(n, 1 / SR); fr[0] = 1
    f /= np.sqrt(fr) if color == "pink" else fr
    x = np.fft.irfft(f, n); return x / (np.abs(x).max() + 1e-9)
def lowpass(x, cutoff):
    a = math.exp(-2 * math.pi * cutoff / SR); y = np.empty_like(x); acc = 0.0
    # vectorised one-pole via lfilter-like loop in chunks (fast enough for <30 s)
    for i in range(len(x)):
        acc = (1 - a) * x[i] + a * acc; y[i] = acc
    return y
def place(buf, sig, t, gain=1.0):
    i = int(t * SR); j = min(len(buf), i + len(sig))
    if i < len(buf) and j > i: buf[i:j] += sig[: j - i] * gain

def build_audio(total, ev, speech, out_wav):
    n = int(total * SR); tt = np.arange(n) / SR
    bed = np.zeros(n); sfx = np.zeros(n)
    crowd = noise(n, "pink", 1); crowd = crowd - lowpass(crowd, 180)          # remove rumble
    env = np.interp(tt, ev["crowd_t"], ev["crowd_v"])
    bed += crowd * env * 0.75
    # tension drone during the race
    dr = np.zeros(n); m = (tt >= ev["gun"]) & (tt < ev["slow0"] + 0.3)
    rise = np.clip((tt - ev["gun"]) / max(0.1, ev["slow0"] - ev["gun"]), 0, 1)
    f0 = 55 * (1 + 0.12 * rise)
    ph = 2 * np.pi * np.cumsum(f0) / SR
    dr[m] = (np.sin(ph) * 0.5 + np.sin(2 * ph) * 0.25 + np.sin(3 * ph) * 0.12)[m] * (0.5 + 0.5 * np.sin(2 * np.pi * 4 * tt))[m]
    bed += dr * 0.20
    # footsteps: many runners, ~4.6 steps/s each
    rng = np.random.default_rng(3)
    step = noise(int(0.05 * SR), "white", 4) * np.exp(-np.linspace(0, 9, int(0.05 * SR)))
    step = lowpass(step, 1800)
    for r in range(ev["n"]):
        t0 = ev["gun"] + 0.15 + rng.uniform(0, 0.2)
        while t0 < ev["slow0"]:
            place(sfx, step, t0, 0.22); t0 += 1 / 4.6 * rng.uniform(0.95, 1.05)
    # set beep, gun, rewind, whoosh, heartbeat, impact
    beep = np.sin(2 * np.pi * 880 * np.arange(int(0.18 * SR)) / SR) * np.linspace(1, 0, int(0.18 * SR)) ** 0.3
    place(sfx, beep, ev["set"], 0.35)
    g = noise(int(0.45 * SR), "white", 5) * np.exp(-np.linspace(0, 12, int(0.45 * SR)))
    g += np.sin(2 * np.pi * 70 * np.arange(len(g)) / SR) * np.exp(-np.linspace(0, 8, len(g))) * 0.8
    place(sfx, g, ev["gun"], 0.9)
    L = int(ev["rew_len"] * SR); k = np.arange(L) / SR
    rew = np.sin(2 * np.pi * np.cumsum(np.linspace(1800, 300, L)) / SR) * 0.35 + noise(L, "white", 6) * 0.15
    place(sfx, rew * np.hanning(L), ev["rew0"], 0.6)
    for wt in ev["whoosh"]:
        Lw = int(0.5 * SR); wn = noise(Lw, "white", 7); wn = lowpass(wn, 2500) * np.hanning(Lw) ** 2
        place(sfx, wn, wt - 0.25, 1.4)
    hb = np.zeros(int(0.5 * SR)); kk = np.arange(len(hb)) / SR
    hb += np.sin(2 * np.pi * 52 * kk) * np.exp(-kk * 18)
    hb += np.roll(np.sin(2 * np.pi * 48 * kk) * np.exp(-kk * 22) * 0.7, int(0.18 * SR))
    t0 = ev["slow0"]
    while t0 < ev["slow1"]:
        place(sfx, hb, t0, 0.9); t0 += 0.75
    Li = int(1.2 * SR); ki = np.arange(Li) / SR
    imp = np.sin(2 * np.pi * 42 * ki) * np.exp(-ki * 4) + noise(Li, "white", 8) * np.exp(-ki * 10) * 0.5
    place(sfx, imp, ev["slow1"], 1.0)
    # speech with ducking
    sp = np.zeros(n)
    for path, t in speech:
        a = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"],
                                         capture_output=True).stdout, dtype=np.int16).astype(np.float64) / 32768
        place(sp, a, t, 1.0)
    duck = np.clip(1 - 0.55 * (np.convolve(np.abs(sp) > 0.02, np.ones(int(0.2 * SR)) / int(0.2 * SR), "same") > 0.05), 0.45, 1)
    mix = (bed * duck + sfx * (0.6 + 0.4 * duck)) * 0.8 + sp * 1.15
    mix /= max(1e-9, np.abs(mix).max()) / 0.95
    st = np.stack([mix, mix], 1)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f64le", "-ar", str(SR), "-ac", "2", "-i", "-", out_wav],
                   input=st.astype(np.float64).tobytes(), check=True)

# ---------------- speech ----------------
_wm = None
def say(key, tts, disp, length=0.86):
    global _wm
    from faster_whisper import WhisperModel
    if _wm is None: _wm = WhisperModel("small.en", device="cpu", compute_type="int8", cpu_threads=4)
    os.makedirs(os.path.join(D, "narr"), exist_ok=True)
    wav = os.path.join(D, "narr", key + ".wav"); pcm = wav[:-4] + ".pcm"
    subprocess.run(["python3", "-m", "piper", "-m", VOICE, "--length-scale", str(length), "-f", wav], input=tts.encode(), check=True, capture_output=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav, "-ac", "1", "-ar", "16000", "-f", "s16le", pcm], check=True)
    a = np.fromfile(pcm, dtype=np.int16).astype(np.float32) / 32768
    segs, _ = _wm.transcribe(a, word_timestamps=True)
    ws = [(w.start, w.end) for s in segs for w in s.words]; toks = disp.split()
    if len(ws) != len(toks) and ws:
        st, en = ws[0][0], ws[-1][1]; step = (en - st) / len(toks); ws = [(st + i * step, st + (i + 1) * step) for i in range(len(toks))]
    return wav, len(a) / 16000, [(a_, b_, t_) for (a_, b_), t_ in zip(ws, toks)]

# ---------------- render ----------------
def render(spec):
    R = spec["racers"]; n = len(R)
    for r in R: r["kit"] = KITS.get(r["flag"], ((60, 60, 60), (200, 200, 200)))
    order = sorted(R, key=lambda r: r["time"]); lead, second = order[0], order[1]
    T1, TL = lead["time"], max(r["time"] for r in R)
    # ---- timeline (video seconds) ----
    hook, rew_len, set_len = 1.5, 0.75, 0.9
    t_rew0 = hook; t_set = hook + rew_len; t_gun = t_set + set_len
    rs0 = T1 - 0.45                                   # race time where slow-mo starts
    t_slow0 = t_gun + rs0
    slow_rate = 0.25; rs1 = TL + 0.25
    t_slow1 = t_slow0 + (rs1 - rs0) / slow_rate       # end of slow motion
    t_flash = t_slow1; t_board = t_flash + 1.4
    def race_t(vt):
        if vt < t_gun: return 0.0
        if vt < t_slow0: return vt - t_gun
        if vt < t_slow1: return rs0 + (vt - t_slow0) * slow_rate
        return rs1
    # ---- commentary ----
    sp_name = lambda r: r.get("say", r["label"].title())
    lines = []
    def add_line(key, tts, disp, at): lines.append((key, tts, disp, at))
    add_line("c0", "Who won this?", "WHO WON THIS?", 0.12)
    add_line("c1", spec.get("intro_tts", "And they're off!"), spec.get("intro", "AND THEY'RE OFF!"), t_gun + 0.25)
    t35 = t_gun + time_at(35, T1)
    add_line("c2", f"{sp_name(lead)} takes the lead!", f"{lead['label']} {lead.get('tag','')} TAKES THE LEAD!", t35)
    t70 = t_gun + time_at(68, T1)
    add_line("c3", f"{sp_name(second)} is right there!", f"{second['label']} {second.get('tag','')} IS RIGHT THERE!", t70)
    add_line("c4", "Photo finish!", "PHOTO FINISH!", t_slow0 + 0.15)
    add_line("c5", spec["punch_tts"], spec["punch"], t_board + 0.2)
    speech, caps = [], []
    t_prev_end = 0
    for key, tts, disp, at in lines:
        wav, dur, ws = say(spec["out"] + "_" + key, tts, disp)
        at = max(at, t_prev_end + 0.05)
        speech.append((wav, at)); t_prev_end = at + dur
        cur = []
        for a, b, w in ws:
            cur.append((a, b, w))
            if len(cur) == 3 or w[-1] in ".?!,":
                caps.append((at + cur[0][0], at + cur[-1][1] + 0.15, " ".join(x[2] for x in cur).upper())); cur = []
        if cur: caps.append((at + cur[0][0], at + cur[-1][1] + 0.15, " ".join(x[2] for x in cur).upper()))
    total = max(t_board + 4.2, t_prev_end + 1.2)
    for i in range(len(caps) - 1):
        a, b, s_ = caps[i]; caps[i] = (a, min(max(b, a + 0.4), caps[i + 1][0]), s_)
    split_t = t_gun + time_at(50, T1)
    split_txt = f"50M SPLIT · {lead['label']} {lead.get('tag','')} · {time_at(50, T1):.2f}s"
    # ---- geometry ----
    top_track, bot_track = 700, 1500
    lane_h = [58 + (112 - 58) * k / (n - 1) for k in range(n)]
    scale = sum(lane_h) / (bot_track - top_track); lane_h = [h / scale for h in lane_h]
    lane_y = [top_track + sum(lane_h[:k]) for k in range(n + 1)]
    PXM = spec.get('pxm', 48.0)
    wd = os.path.join(D, "work", spec["out"]); os.makedirs(wd, exist_ok=True)
    vid = os.path.join(wd, "video.mp4")
    proc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                             "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", vid], stdin=subprocess.PIPE)
    crowd_dots = np.random.default_rng(9).uniform(0, 1, (900, 3))
    nf = int(total * FPS)
    for fi in range(nf):
        vt = fi / FPS
        # which race time to show
        if vt < hook: rt = T1 + 0.005; mode = "hook"
        elif vt < t_set: rt = (T1 + 0.005) * (1 - (vt - t_rew0) / rew_len) ** 1.6; mode = "rew"
        elif vt < t_gun: rt = 0.0; mode = "set"
        else: rt = race_t(vt); mode = "slow" if t_slow0 <= vt < t_slow1 else ("race" if vt < t_slow0 else "done")
        ds = [dist(rt, r["time"]) if (mode != "set" and rt > 0) else 0.0 for r in R]
        lead_d = max(ds)
        # camera (metres at screen centre)
        if mode in ("set",) or lead_d < 8: camx = 8
        else: camx = lead_d - 2.5
        if mode in ("slow", "done", "hook") or lead_d > 96: camx = 97.8
        if mode == "rew": camx = max(8, lead_d - 2.5) if lead_d < 96 else 97.8
        zoom = 1.0
        if mode == "hook": zoom = 1.55 + 0.1 * (vt / hook)
        elif mode == "slow": zoom = 1.0 + 0.55 * min(1.0, (vt - t_slow0) / max(0.1, t_slow1 - t_slow0)) ** 0.7
        elif mode == "done": zoom = 1.55
        im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
        # sky + stands with parallax crowd
        for y in range(440, top_track):
            c = int(18 + 30 * (y - 440) / (top_track - 440)); d.line((0, y, W, y), fill=(c, c, c + 8))
        par = camx * PXM * 0.35
        for cx_, cy_, cc in crowd_dots:
            x = (cx_ * 2600 - par) % 2600 - 260; y = 470 + cy_ * 210
            col = [(200, 60, 60), (240, 240, 240), (60, 90, 200), (240, 200, 40), (90, 90, 90)][int(cc * 5)]
            bob = 2 * math.sin(vt * 9 + cx_ * 50) if mode in ("race", "slow") else 0
            d.ellipse((x - 5, y - 5 + bob, x + 5, y + 5 + bob), fill=col)
        d.rectangle((0, top_track - 18, W, top_track), fill=(40, 40, 48))
        # track lanes
        for k in range(n):
            col = (176, 58, 42) if k % 2 == 0 else (160, 50, 37)
            d.rectangle((0, lane_y[k], W, lane_y[k + 1]), fill=col)
            d.line((0, lane_y[k], W, lane_y[k]), fill=(235, 235, 235), width=2)
        d.line((0, bot_track, W, bot_track), fill=(235, 235, 235), width=3)
        sx = lambda m, k: 540 + (m - camx) * PXM * (lane_h[min(k, n - 1)] / lane_h[-1]) * zoom
        # metre lines (perspective)
        for m in range(0, 101, 5):
            pts = [(sx(m, k), lane_y[k]) for k in range(n)] + [(sx(m, n - 1) * 1.0, bot_track)]
            if all(p[0] < -50 or p[0] > W + 50 for p in pts): continue
            d.line(pts, fill=(215, 110, 95), width=2)
            if m % 10 == 0:
                text(d, (sx(m, n - 1), bot_track + 26), f"{m}M", 26, (230, 230, 230), stroke=3)
        # finish line (checkered, perspective)
        for k in range(n):
            x0 = sx(100, k); hgt = lane_h[k]; cs = max(6, int(hgt / 5))
            for j in range(int(hgt / cs) + 1):
                for q in range(2):
                    c = WHT if (j + q) % 2 == 0 else (0, 0, 0)
                    d.rectangle((x0 + q * cs, lane_y[k] + j * cs, x0 + q * cs + cs, min(lane_y[k + 1], lane_y[k] + j * cs + cs)), fill=c)
        # start blocks line
        d.line([(sx(0, k), lane_y[k]) for k in range(n)] + [(sx(0, n - 1), bot_track)], fill=WHT, width=4)
        # speed streaks
        if mode in ("race",) and lead_d > 12:
            for j in range(16):
                y = top_track + (j * 53 + fi * 7) % (bot_track - top_track); x = (j * 197 + fi * 41) % W
                d.line((x, y, x + 120, y), fill=(220, 120, 100), width=2)
        # runners back->front (bigger figures, no labels above heads)
        lead_k = max(range(n), key=lambda k: ds[k]) if mode in ("race", "slow") else None
        for k in range(n):
            r = R[k]; s = lane_h[k] / lane_h[-1] * zoom
            m = ds[k]; x = sx(m, k); yb = lane_y[k + 1] - 4 * s
            if x < -150 or x > W + 150: continue
            ht = lane_h[-1] * 2.05
            if mode == "set" or (rt <= 0 and mode != "rew"):
                draw_runner(d, x - 10 * s, yb, s, r["kit"], 0, "set", 0, ht); hx, hy = x, yb - ht * 0.6 * s
            else:
                lean = 45 - 33 * min(1, m / 30)
                if 98.5 < m < 100.6: lean = 34
                hx, hy = draw_runner(d, x, yb, s, r["kit"], m / 2.35 * 2 * math.pi, "run", lean, ht)
            if k == lead_k:
                d.polygon([(hx - 14 * s, hy - 26 * s), (hx + 14 * s, hy - 26 * s), (hx, hy - 6 * s)], fill=YEL, outline=(0, 0, 0))
            if rt >= r["time"] and mode in ("slow", "done"):
                rank = order.index(r) + 1
                text(d, (x + 40 * s, lane_y[k] + lane_h[k] * 0.55), f"#{rank}", int(22 + 12 * s), YEL if rank == 1 else WHT, anchor="lm", stroke=4)
        # fixed lane tags (left), like a TV graphic; compact during hook/slow-mo so trailing runners stay visible
        compact = mode in ("hook", "slow", "done")
        for k in range(n):
            r = R[k]; yc = lane_y[k] + lane_h[k] / 2; hh = max(26, lane_h[k] * 0.62)
            tw = 150 if compact else 360
            ov = Image.new("RGBA", (tw, int(hh)), (0, 0, 0, 150 if compact else 170)); im.paste(ov, (0, int(yc - hh / 2)), ov); d = ImageDraw.Draw(im)
            e = emoji(r["flag"], int(hh * 0.62)); im.paste(e, (8, int(yc - e.height / 2)), e)
            if not compact:
                text(d, (8 + e.width + 8, yc), f"{r['label']} {r.get('tag','')}", int(hh * 0.5), WHT, anchor="lm", stroke=3, maxw=280 - e.width - 24)
            elif rt < r["time"]:
                text(d, (8 + e.width + 6, yc), r.get("tag", ""), int(hh * 0.42), WHT, anchor="lm", stroke=3, maxw=tw - e.width - 14)
            if rt >= r["time"] and mode in ("slow", "done"):
                text(d, (tw - 8, yc), f"{r['time']:.2f}", int(hh * 0.45), YEL if order.index(r) == 0 else WHT, anchor="rm", stroke=3)
        # header
        d.rectangle((0, 0, W, 430), fill=BG)
        text(d, (W // 2, 105), spec["title"][0], 74, YEL); text(d, (W // 2, 195), spec["title"][1], 64, WHT)
        text(d, (W // 2, 268), spec["sub"], 32, (190, 190, 190), stroke=3)
        clock = min(rt, TL) if mode not in ("set",) else 0.0
        if mode == "hook": clock = T1
        d.rounded_rectangle((330, 312, 750, 412), radius=22, fill=(0, 0, 0), outline=YEL if mode in ("slow", "done", "hook") else (90, 90, 90), width=4)
        text(d, (W // 2, 362), f"{clock:05.2f}", 70, YEL if mode in ("slow", "done", "hook") else WHT)
        # overlays per mode
        if mode == "hook":
            d.line((sx(100, 0) + 10, top_track, sx(100, n - 1) + 10, bot_track), fill=YEL, width=4)
        if mode == "hook":
            gap = TL - T1
            d.rounded_rectangle((120, 560, W - 120, 640), radius=18, fill=(0, 0, 0), outline=YEL, width=3)
            text(d, (W // 2, 600), f"ONLY {gap:.2f}s BETWEEN 1ST AND {n}TH", 38, WHT, stroke=3, maxw=800)
        if mode == "rew":
            ov = Image.new("RGB", (W, H), (20, 40, 120)); im = Image.blend(im, ov, 0.25); d = ImageDraw.Draw(im)
            for y in range(440, 1520, 6): d.line((0, y, W, y), fill=(0, 0, 0), width=1)
            text(d, (W // 2, 600), "◀◀  REWIND", 80, WHT, stroke=8)
        if mode == "set":
            text(d, (W // 2, 600), "SET...", 96, WHT, stroke=9)
        if mode == "race" and vt - t_gun < 0.6:
            text(d, (W // 2, 600), "GO!", 120, YEL, stroke=10)
        if split_t <= vt < split_t + 1.6 and mode == "race":
            d.rounded_rectangle((90, 560, W - 90, 640), radius=18, fill=(0, 0, 0), outline=YEL, width=3)
            text(d, (W // 2, 600), split_txt, 36, WHT, stroke=3, maxw=860)
        if mode == "slow":
            im = Image.blend(im, Image.new("RGB", (W, H), (0, 0, 0)), 0.12); d = ImageDraw.Draw(im)
            text(d, (W // 2, 600), "SLOW MOTION  0.25x", 52, YEL, stroke=6)
            for y in range(440, 1520, 4):
                if (y // 4 + fi) % 3 == 0: d.line((0, y, W, y), fill=(0, 0, 0), width=1)
        if t_flash <= vt < t_flash + 0.15:
            im = Image.blend(im, Image.new("RGB", (W, H), WHT), 0.8); d = ImageDraw.Draw(im)
        if mode == "done" and vt < t_board:
            d.line((sx(100, 0) + 10, top_track, sx(100, n - 1) + 10, bot_track), fill=YEL, width=5)
            text(d, (W // 2, 600), "PHOTO FINISH", 80, YEL, stroke=8)
        if vt >= t_board:
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
            od.rounded_rectangle((50, 450, W - 50, 1510), radius=34, fill=(8, 8, 12, 238)); im.paste(ov, (0, 0), ov); d = ImageDraw.Draw(im)
            text(d, (W // 2, 530), spec.get("board_title", "OFFICIAL RESULT"), 64, YEL)
            rows = order; rh = (1490 - 620) / len(rows)
            for j, r in enumerate(rows):
                if vt - t_board < j * 0.09: continue
                yy = int(620 + j * rh + rh / 2); col = YEL if j == 0 else WHT
                if j == 0: d.rounded_rectangle((80, yy - rh / 2 + 4, W - 80, yy + rh / 2 - 4), radius=16, fill=(60, 50, 0))
                text(d, (120, yy), f"{j + 1}", 46, col, anchor="lm")
                e = emoji(r["flag"], 54); im.paste(e, (190, yy - 27), e)
                text(d, (270, yy), f"{r['label']} {r.get('tag','')}", 42, col, anchor="lm", stroke=5, maxw=560)
                gap = "" if j == 0 else f"+{r['time'] - order[0]['time']:.2f}"
                text(d, (W - 120, yy), f"{r['time']:.2f}", 46, col, anchor="rm")
                if gap: text(d, (W - 260, yy), gap, 30, (190, 190, 190), anchor="rm", stroke=3)
        # captions
        for a, b, s_ in caps:
            if a <= vt < b:
                hi = any(w in s_ for w in ("WON", "LEAD", "THERE", "PHOTO", "BOLT", "FASTEST", "9.58", "OFF"))
                text(d, (W // 2, 1650), s_, 84, YEL if hi else WHT, stroke=9, maxw=1000)
        # brand + progress
        text(d, (W // 2, 1830), spec.get("brand", "LANE NINE LAB"), 30, (170, 170, 170), stroke=3)
        d.rectangle((0, H - 12, int(W * vt / total), H), fill=YEL)
        proc.stdin.write(im.tobytes())
    proc.stdin.close(); proc.wait()
    crowd_t = [0, hook, t_rew0 + 0.1, t_set, t_gun, t_gun + 0.6, t_slow0, t_slow0 + 0.3, t_slow1, t_slow1 + 0.5, t_board + 1, total]
    crowd_v = [0.45, 0.45, 0.15, 0.35, 0.3, 0.8, 1.0, 0.35, 0.35, 1.0, 0.7, 0.55]
    ev = dict(n=n, gun=t_gun, set=t_set, rew0=t_rew0, rew_len=rew_len, slow0=t_slow0, slow1=t_slow1,
              whoosh=[t_rew0, t_slow0, t_board], crowd_t=crowd_t, crowd_v=crowd_v)
    return vid, total, ev, speech

def build(spec):
    vid, total, ev, speech = render(spec)
    wd = os.path.dirname(vid); wav = os.path.join(wd, "audio.wav")
    build_audio(total, ev, speech, wav)
    out = os.path.join(D, "out", spec["out"] + ".mp4"); os.makedirs(os.path.dirname(out), exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vid, "-i", wav, "-filter_complex", "[1:a]loudnorm=I=-14:TP=-1.5:LRA=9[a]",
                    "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest",
                    "-aspect", "9:16", "-movflags", "+faststart", out], check=True)
    print(spec["out"], f"{total:.1f}s")
    return out, total
