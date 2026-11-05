"""Config-driven YouTube Shorts builder (1080x1920).

A spec is a dict:
  out       output basename
  title     header title
  style     "countdown" | "rapid" | "story"
  cam_h     facecam panel height (split layout)
  accent    ASS colour for highlights (default yellow)
  hook      optional {"clip", "start", "end", "text"} cold open
  end_text  optional text shown over the last 1.6s
  items     list of {"label", "parts": [(clip, start, end), ...], "layout": "split"|"full",
                     "cam": [x,y,w,h], "game": [x,y,w,h], "full": [x,y,w,h],
                     "fix": {wrong_word: right_word}, "drop": [words], "caps": [(t, text), ...]}
  For "countdown" items are given in play order (#5 first); ranks are assigned automatically.
"""
import json, os, re, subprocess

D = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
HEAD_H = 500
YEL, WHT, RED, GRN = "&H0000E5FF&", "&H00FFFFFF&", "&H003030FF&", "&H0050FF50&"

_ld = lambda n: json.load(open(os.path.join(D, n))) if os.path.exists(os.path.join(D, n)) else {}
_w1 = _ld("words.json")
_w2 = _ld("words2.json")
_w3 = json.load(open(os.path.join(D, "words3.json"))) if os.path.exists(os.path.join(D, "words3.json")) else {}
CENSOR = {"fucking": "F*CKING", "fuck": "F*CK", "fucked": "F*CKED", "shit": "SH*T", "motherfuckers": "MOTHERF*CKERS",
          "dickhead": "D*CKHEAD", "bitch": "B*TCH", "dumbass": "DUMBA**", "pissing": "P*SSING", "cock": "C*CK", "dick": "D*CK", "ass": "A**", "-ass": "-A**", "shitter": "SH*TTER", "pussy": "P*SSY"}
SCREAM = re.compile(r"^(A+H+|A+R+G+H*|WOO+|HOLY|GO+D|OH|WOAH|NO+|FU+)", re.I)


def words_for(clip):
    if clip.startswith("c") and f"wav/{clip}.pcm" in _w1:
        return _w1[f"wav/{clip}.pcm"]
    return _w2.get(clip) or _w3.get(clip, [])


def src(clip):
    for d in ("raw", "raw2", "raw3"):
        p = os.path.join(D, d, clip + ".mp4")
        if os.path.exists(p): return p


def run(cmd):
    subprocess.run(cmd, check=True)


def fit(box, ratio, anchor_y=0.5):
    """Largest sub-rect of box with aspect `ratio` (w/h), centred (vertically at anchor_y)."""
    x, y, w, h = box
    if w / h > ratio:
        nw = round(h * ratio); return [x + (w - nw) // 2, y, nw, h]
    nh = round(w / ratio); return [x, y + round((h - nh) * anchor_y), w, nh]


def crop(b):
    b = [int(v) // 2 * 2 for v in b]
    return f"crop={b[2]}:{b[3]}:{b[0]}:{b[1]}"


def peak(clip, a, b):
    """Time (in clip seconds) of the loudest 0.25s window between a and b."""
    import numpy as np
    for p in (os.path.join(D, w, clip + ".pcm") for w in ("wav", "wav2", "wav3")):
        if os.path.exists(p):
            x = np.fromfile(p, dtype=np.int16).astype(np.float32)[int(a * 16000):int(b * 16000)]
            hop = 4000
            n = len(x) // hop
            if n == 0: return None
            rms = [np.mean(x[i * hop:(i + 1) * hop] ** 2) for i in range(n)]
            return a + int(np.argmax(rms)) * 0.25
    return None


def shrink(box, z, anchor_y=0.4):
    """Zoomed-in sub-box (1/z of the size) for a punch-in."""
    x, y, w, h = box
    nw, nh = w / z, h / z
    return [x + (w - nw) / 2, y + (h - nh) * anchor_y, nw, nh]


def render_part(clip, a, b, item, cam_h, out):
    game_h = H - HEAD_H - cam_h
    lay = item.get("layout", "split")
    # punch-in: hard zoom on the face for 0.8s at the loudest moment
    pk = peak(clip, a, b) if item.get("punch", True) else None
    en = f"between(t,{max(0, pk - a - 0.05):.2f},{pk - a + 0.75:.2f})" if pk is not None else "0"
    if lay == "full":
        f = fit(item["full"], W / (H - HEAD_H), item.get("anchor", 0.4))
        fz = shrink(f, 1.25, 0.35)
        g = fit(item.get("bg", [0, 0, 1920, 1080]), W / H)
        vf = (f"[0:v]scale=1920:1080,setsar=1,fps={FPS},split=3[v1][v2][v4];"
              f"[v1]{crop(g)},scale={W}:{H},gblur=sigma=30,eq=brightness=-0.3[bg];"
              f"[v2]{crop(f)},scale={W}:{H - HEAD_H}:flags=lanczos,eq=contrast=1.05:saturation=1.1[m];"
              f"[v4]{crop(fz)},scale={W}:{H - HEAD_H}:flags=lanczos,eq=contrast=1.08:saturation=1.15[mz];"
              f"[bg][m]overlay=0:{HEAD_H}[t];[t][mz]overlay=0:{HEAD_H}:enable='{en}',format=yuv420p,setsar=1[v]")
    else:
        c = fit(item["cam"], W / cam_h, item.get("anchor", 0.35))
        cz = shrink(c, 1.3, 0.35)
        g = fit(item["game"], W / game_h, item.get("game_anchor", 0.5))
        hide = ",gblur=sigma=45,eq=brightness=-0.35" if item.get("hide_game") else ""
        vf = (f"[0:v]scale=1920:1080,setsar=1,fps={FPS},split=4[v1][v2][v3][v4];"
              f"[v1]{crop(g)},scale={W}:{H},gblur=sigma=30,eq=brightness=-0.3[bg];"
              f"[v2]{crop(c)},scale={W}:{cam_h}:flags=lanczos,eq=contrast=1.05:saturation=1.1[cam];"
              f"[v4]{crop(cz)},scale={W}:{cam_h}:flags=lanczos,eq=contrast=1.08:saturation=1.15[camz];"
              f"[v3]{crop(g)},scale={W}:{game_h}:flags=lanczos{hide}[game];"
              f"[bg][cam]overlay=0:{HEAD_H}[t0];[t0][camz]overlay=0:{HEAD_H}:enable='{en}'[t];"
              f"[t][game]overlay=0:{HEAD_H + cam_h},format=yuv420p,setsar=1[v]")
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a}", "-t", f"{b - a}", "-i", src(clip),
         "-filter_complex", vf + f";[0:a]aresample=48000,loudnorm=I=-14:TP=-1.5:LRA=7[a]",
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", out])


def ts(x):
    x = max(0, x)
    return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"


def build(spec):
    name, style = spec["out"], spec.get("style", "countdown")
    cam_h = spec.get("cam_h", 620)
    acc = spec.get("accent", YEL)
    wd = os.path.join(D, "work", name); os.makedirs(wd, exist_ok=True)
    items = spec["items"]
    n = len(items)

    # ---- render parts, build timeline ----
    parts, t = [], 0.0
    blocks = []  # (kind, idx, t0, t1, [(clip,a,b,tstart)])
    if spec.get("hook"):
        hk = spec["hook"]; it = dict(items[hk.get("item", -1)]); it.update(hk.get("over", {}))
        p = os.path.join(wd, "p_hook.mp4"); render_part(hk["clip"], hk["start"], hk["end"], it, cam_h, p)
        parts.append(p); blocks.append(("hook", None, t, t + hk["end"] - hk["start"], [])); t += hk["end"] - hk["start"]
    for i, it in enumerate(items):
        t0, segs = t, []
        for j, (clip, a, b) in enumerate(it["parts"]):
            p = os.path.join(wd, f"p{i}_{j}.mp4"); render_part(clip, a, b, it, cam_h, p)
            parts.append(p); segs.append((clip, a, b, t)); t += b - a
        blocks.append(("item", i, t0, t, segs))
    total = t
    with open(os.path.join(wd, "list.txt"), "w") as f:
        f.writelines(f"file '{os.path.basename(p)}'\n" for p in parts)
    joined = os.path.join(wd, "joined.mp4")
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(wd, "list.txt"),
         "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-c:a", "aac", "-b:a", "192k", joined])

    # ---- ASS overlay ----
    ev = []
    def add(st, en, style_, text, layer=0):
        ev.append(f"Dialogue: {layer},{ts(st)},{ts(en)},{style_},,0,0,0,,{text}")

    title_size = spec.get("title_size", 92)
    add(0, total, "Title", spec["title"])
    item_blocks = [b for b in blocks if b[0] == "item"]
    if style == "countdown":
        gap = 66; y0 = 150
        for k, (_, i, s, e, _) in enumerate(item_blocks):
            r = n - k; y = y0 + (r - 1) * gap
            lab = items[i]["label"]
            add(0, total, "List", f"{{\\pos(40,{y})}}{r}.")
            rv = s + items[i].get("reveal", 0)
            if rv > s: add(s, rv, "List", f"{{\\pos(110,{y})\\c{acc}\\fscx105\\fscy105}}???")
            add(rv, e, "List", f"{{\\pos(110,{y})\\c{acc}\\fscx105\\fscy105}}{lab}")
            add(e, total, "List", f"{{\\pos(110,{y})}}{lab}")
            add(s, s + 0.7, "Big", f"{{\\pos({W // 2},{HEAD_H + 300})\\fad(0,150)"
                                   f"\\t(0,120,\\fscx115\\fscy115)\\t(120,240,\\fscx100\\fscy100)}}#{r}", 3)
    elif style == "rapid":
        for k, (_, i, s, e, _) in enumerate(item_blocks):
            add(s, e, "Sub", f"{{\\pos({W // 2},300)\\c{acc}}}{spec.get('counter', 'UNBOX')} {k + 1}/{n}")
            rv = s + items[i].get("reveal", 0)
            if rv > s: add(s, rv, "List", f"{{\\an8\\pos({W // 2},400)}}???")
            add(rv, e, "List", f"{{\\an8\\pos({W // 2},400)\\fad(120,0)}}{items[i]['label']}")
    elif style == "story":
        for line, (y, col) in zip(spec.get("subtitle", []), [(250, acc), (330, WHT)]):
            add(0, total, "Sub2", f"{{\\pos({W // 2},{y})\\c{col}}}{line}")
        for (_, i, s, e, _) in item_blocks:
            if items[i].get("label"):
                rv = s + items[i].get("reveal", 0)
                if rv > s: add(s, rv, "List", f"{{\\an8\\pos({W // 2},400)\\c{acc}}}{items[i].get('pre', '???')}")
                add(rv, e, "List", f"{{\\an8\\pos({W // 2},400)\\c{acc}\\fad(120,0)}}{items[i]['label']}")

    cap_y = HEAD_H + (cam_h if items[0].get("layout", "split") == "split" else 880) + 10
    if spec.get("hook"):
        b = blocks[0]
        add(b[2], b[3], "Cap", f"{{\\pos({W // 2},{cap_y})\\c{acc}}}{spec['hook']['text']}", 2)

    for (_, i, s, e, segs) in item_blocks:
        it = items[i]
        cy = HEAD_H + (cam_h if it.get("layout", "split") == "split" else 880) + 10
        caps = []
        if "caps" in it:   # manual: times relative to item start
            caps = [(s + a, s + b, txt) for a, b, txt in it["caps"]]
        else:
            for clip, a, b, tst in segs:
                ws = [(w0 - a + tst, w1 - a + tst, w) for w0, w1, w in words_for(clip) if a - 0.05 <= w0 < b - 0.1]
                fix = it.get("fix", {}); drop = set(re.sub(r"[^\w'\-]", "", x).lower() for x in it.get("drop", []))
                for w0, w1, w in ws:
                    key = re.sub(r"[^\w'\-]", "", w).lower()
                    if key in drop: continue
                    w = fix.get(key, w)
                    caps.append((w0, w1, w))
        # words that start at the same moment (zero-length timings) are shown together
        merged = []
        for st, en, w in caps:
            if merged and abs(merged[-1][0] - st) < 0.02:
                merged[-1] = (merged[-1][0], max(merged[-1][1], en), merged[-1][2] + " " + w)
            else:
                merged.append((st, en, w))
        caps = merged
        for k, (st, en, w) in enumerate(caps):
            nxt = caps[k + 1][0] if k + 1 < len(caps) else e
            end = min(max(en, st + 0.3), nxt, e)
            if end <= st: continue
            out_words = []
            for part in w.upper().split():
                bare = re.sub(r"[^\w'\-]", "", part).lower()
                if bare in CENSOR:
                    part = CENSOR[bare] + re.sub(r"^[\w'\-]+", "", re.sub(r"[^\w'\-!?.,]", "", part))
                out_words.append(part)
            txt = " ".join(out_words)
            col = RED if (SCREAM.match(txt) and txt.endswith("!")) else (acc if k % 3 == 1 else WHT)
            add(st, end, "Cap", f"{{\\pos({W // 2},{cy})\\c{col}\\fscx80\\fscy80"
                                f"\\t(0,80,\\fscx108\\fscy108)\\t(80,140,\\fscx100\\fscy100)}}{txt}", 2)

    if spec.get("end_text"):
        add(total - 1.6, total, "Cap", f"{{\\pos({W // 2},{HEAD_H + 90})\\c{acc}\\fad(150,0)}}{spec['end_text']}", 4)

    hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Title,Montserrat Black,{title_size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,7,4,8,20,20,40,1
Style: List,Montserrat Black,60,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,5,3,7,40,20,0,1
Style: Sub,Montserrat Black,120,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,8,4,5,20,20,0,1
Style: Sub2,Montserrat Black,70,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,6,3,5,20,20,0,1
Style: Cap,Montserrat Black,104,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,1,0,0,0,100,100,0,0,1,9,5,5,40,40,0,1
Style: Big,Montserrat Black,260,&H0000E5FF,&H00FFFFFF,&H00000000,&H90000000,1,0,0,0,100,100,0,0,1,14,8,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ass = os.path.join(wd, "overlay.ass")
    open(ass, "w").write(hdr + "\n".join(ev) + "\n")
    os.makedirs(os.path.join(D, "out"), exist_ok=True)
    out = os.path.join(D, "out", name + ".mp4")
    run(["ffmpeg", "-v", "error", "-y", "-i", joined,
         "-vf", f"subtitles={ass}:fontsdir={os.path.join(D, '..', 'fonts')}",
         "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high", "-pix_fmt", "yuv420p",
         "-c:a", "copy", "-movflags", "+faststart", out])
    print(f"{name}: {total:.2f}s -> {out}")
    for kind, i, s, e, _ in blocks:
        print(f"   {s:5.2f}-{e:5.2f} {kind} {items[i]['label'] if i is not None else ''}")
    return out, blocks


def preview(path, times, dst):
    sel = "+".join(f"eq(n\\,{int(t * FPS)})" for t in times)
    run(["ffmpeg", "-v", "error", "-y", "-i", path, "-vf", f"select='{sel}',scale=300:-1,tile={len(times)}x1",
         "-vsync", "0", "-frames:v", "1", dst])
