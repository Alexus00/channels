"""Vertical builder for single-camera IRL footage (1080x1920).

Layout: hook header (0..HEAD), cropped action panel (HEAD..HEAD+PANEL), captions below the panel.
spec = dict(out, hook_lines=[...], highlight={words}, end_text, parts=[dict(src, a, b, x=center_x, zoom_at=None)])
"""
import json, os, re, subprocess

D = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.normpath(os.path.join(D, "..", "fonts"))
W, H, FPS = 1080, 1920, 30
HEAD, PANEL = 420, 960
CW, CH = 1215, 1080                      # source crop (9:8) -> 1080x960
YEL, WHT, RED = "&H0000E5FF&", "&H00FFFFFF&", "&H003030FF&"
WORDS = json.load(open(os.path.join(D, "words.json")))
CENSOR = {"fuck": "F*CK", "fucking": "F*CKING", "fucked": "F*CKED", "shit": "SH*T", "bitch": "B*TCH", "bitches": "B*TCHES", "fuckin": "F*CKIN", "shit,": "SH*T",
          "motherfucking": "MOTHERF*CKING", "motherfucker": "MOTHERF*CKER", "damn": "DAMN", "ass": "A**"}
DROP_ALWAYS = {"nigga", "niggas", "nigger"}


def run(cmd):
    subprocess.run(cmd, check=True)


def render_part(p, out):
    ch = p.get("h", CH); cw = int(ch * CW / CH) // 2 * 2; ch = ch // 2 * 2
    x = int(min(max(p.get("x", 960) - cw // 2, 0), 1920 - cw)) // 2 * 2
    y = int(min(max(p.get("y", ch // 2) - ch // 2, 0), 1080 - ch)) // 2 * 2 if "y" in p else 0
    zx, zw = x + cw // 8, cw * 3 // 4
    zx, zw, zh = zx // 2 * 2, zw // 2 * 2, (ch * 3 // 4) // 2 * 2
    zy = y + (ch - zh) // 3 // 2 * 2
    en = "0"
    va = p.get("va", p["a"])                       # video can come from another moment (cutaway / J-cut)
    if p.get("zoom_at") is not None:
        t0 = p["zoom_at"] - va
        en = f"between(t,{t0:.2f},{t0 + p.get('zoom_len', 1.2):.2f})"
    fl = ",fade=t=in:st=0:d=0.12:color=white" if p.get("flash") else ""
    dur = p["b"] - p["a"]
    fz = f"trim=end_frame=1,setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={dur + 0.2}," if p.get("freeze") else ""
    sl = p.get("slow", 1)
    if sl != 1: fz += f"setpts={sl}*PTS,"
    vf = (f"[0:v]{fz}scale=1920:1080,setsar=1,fps={FPS},split=3[a][b][c];"
          f"[a]scale=608:1080,crop=608:1080,scale={W}:{H},gblur=sigma=40,eq=brightness=-0.35[bg];"
          f"[b]crop={cw}:{ch}:{x}:{y},scale={W}:{PANEL}:flags=lanczos,eq=contrast=1.05:saturation=1.08{fl}[m];"
          f"[c]crop={zw}:{zh}:{zx}:{zy},scale={W}:{PANEL}:flags=lanczos,eq=contrast=1.08:saturation=1.12[z];"
          f"[bg][m]overlay=0:{HEAD}[t];[t][z]overlay=0:{HEAD}:enable='{en}',format=yuv420p,setsar=1,trim=duration={dur * sl}[v]")
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{va}", "-t", f"{dur}", "-i", os.path.join(D, "src", f"hq_{p.get('vsrc', p['src'])}.mp4"),
         "-ss", f"{p['a']}", "-t", f"{dur}", "-i", os.path.join(D, "src", f"hq_{p['src']}.mp4"),
         *(["-i", p["narr"]] if p.get("narr") else []),
         "-filter_complex", vf + (f";[1:a]aresample=48000,volume={p.get('duck', 0.15)}[o];[2:a]aresample=48000,apad,volume=1.6[n];"
                                  f"[o][n]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9[au]"
                                  if p.get("narr") else f";[1:a]aresample=48000,atempo={1 / sl},loudnorm=I=-14:TP=-1.5:LRA=9[au]"),
         "-map", "[v]", "-map", "[au]", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
         "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", out])


def ts(x):
    x = max(0, x)
    return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"


def build(spec):
    wd = os.path.join(D, "work", spec["out"]); os.makedirs(wd, exist_ok=True)
    files, t, timeline = [], 0.0, []
    for i, p in enumerate(spec["parts"]):
        f = os.path.join(wd, f"p{i}.mp4"); render_part(p, f); files.append(f)
        timeline.append((t, p)); t += (p["b"] - p["a"]) * p.get("slow", 1)
    total = t
    open(os.path.join(wd, "list.txt"), "w").writelines(f"file '{os.path.basename(f)}'\n" for f in files)
    joined = os.path.join(wd, "joined.mp4")
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(wd, "list.txt"),
         "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-c:a", "aac", "-b:a", "192k", joined])

    ev = []
    def add(st, en, style, text, layer=0):
        ev.append(f"Dialogue: {layer},{ts(st)},{ts(en)},{style},,0,0,0,,{text}")

    # hook header: whole clip, first line yellow
    hl = spec["hook_lines"]
    for k, line in enumerate(hl):
        y = 150 + k * 120 if len(hl) > 1 else 210
        add(0, total, "Hook", f"{{\\pos({W // 2},{y})\\c{YEL if k == 0 else WHT}}}{line}")
    # small source credit under the header (not a watermark: plain text credit)
    labels = [(t0, t0 + p["b"] - p["a"], p["label"]) for t0, p in timeline if p.get("label")]
    if labels:
        for st, en, lab in labels:
            add(st, en, "Label", f"{{\\pos({W // 2},{HEAD - 50})\\fad(80,0)}}{lab}", 1)
    else:
        add(0, total, "Small", f"{{\\pos({W // 2},{HEAD - 34})}}{spec.get('credit', '')}")

    hi = {h.lower() for h in spec.get("highlight", [])}
    fix = {k.lower(): v for k, v in spec.get("fix", {}).items()}
    drop = {d.lower() for d in spec.get("drop", [])} | DROP_ALWAYS
    caps = []
    for t0, p in timeline:
        if "caps" in p:
            caps += [(t0 + a, t0 + b, w, id(p)) for a, b, w in p["caps"]]
            continue
        pfix = {k.lower(): v for k, v in p.get("fix", {}).items()}
        pdrop = {re.sub(r"[^\w'\-]", "", d).lower() for d in p.get("drop", [])}
        ws = [(a + p["a"], b + p["a"], w) for a, b, w in p["nwords"]] if "nwords" in p else WORDS[p["src"]]
        for a, b, w in ws:
            if not (p["a"] - 0.05 <= a < p["b"] - 0.1): continue
            key = re.sub(r"[^\w'\-]", "", w).lower()
            if key in drop or key in pdrop: continue
            w = pfix.get(key, fix.get(key, w))
            caps.append((a - p["a"] + t0, b - p["a"] + t0, w, id(p)))
    # merge split numbers ("$250" + ",000," -> "$250,000,")
    mc = []
    for c in caps:
        if mc and re.match(r"^,\d", c[2]) and re.search(r"\d$", mc[-1][2]):
            mc[-1] = (mc[-1][0], c[1], mc[-1][2] + c[2], mc[-1][3])
        else:
            mc.append(c)
    caps = mc
    # group into 1-3 word chunks for readability, keeping key words alone
    chunks, cur = [], []
    for c in caps:
        k = re.sub(r"[^\w'\-]", "", c[2]).lower()
        if cur and (len(cur) >= 3 or c[0] - cur[-1][1] > 0.35 or k in hi or c[3] != cur[-1][3] or
                    re.sub(r"[^\w'\-]", "", cur[-1][2]).lower() in hi or cur[-1][2][-1:] in ".?!,"):
            chunks.append(cur); cur = []
        cur.append(c)
    if cur: chunks.append(cur)
    CY = HEAD + PANEL + 150
    for i, ch in enumerate(chunks):
        st = ch[0][0]
        nxt = chunks[i + 1][0][0] if i + 1 < len(chunks) else total
        en = min(max(ch[-1][1], st + 0.35), nxt, total)
        parts = []
        for _, _, w, _ in ch:
            k = re.sub(r"[^\w'\-]", "", w).lower()
            txt = w.upper()
            if k in CENSOR: txt = CENSOR[k] + re.sub(r"^[\w'\-]+", "", re.sub(r"[^\w'\-!?.,]", "", txt))
            col = YEL if k in hi else WHT
            parts.append(f"{{\\c{col}}}{txt}")
        add(st, en, "Cap", f"{{\\pos({W // 2},{CY})\\fscx85\\fscy85\\t(0,90,\\fscx105\\fscy105)\\t(90,150,\\fscx100\\fscy100)}}" + " ".join(parts), 2)
    if spec.get("progress"):
        by = HEAD + PANEL - 10
        if spec.get("progress_label"):
            add(0, total, "Small", f"{{\\an4\\pos(24,{by - 26})\\c{YEL}\\fs30}}{spec['progress_label']}", 4)
        add(0, total, "Bar", f"{{\\pos(0,{by})\\an7\\c{YEL}\\clip(0,{by},1,{by + 10})\\t(0,{int(total * 1000)},\\clip(0,{by},{W},{by + 10}))\\p1}}m 0 0 l {W} 0 {W} 10 0 10{{\\p0}}", 4)
    beats = [t0 for t0, p in timeline if p.get("beat")]
    if beats:
        n = len(beats); gap = 14; x0, bw, by2, bh = 90, 900, 1745, 44
        sw = (bw - gap * (n - 1)) / n
        t_load = next(t0 + p["b"] - p["a"] for t0, p in timeline if p.get("beat") and t0 == beats[-1])
        box = lambda x, w: f"m {x:.0f} {by2} l {x + w:.0f} {by2} {x + w:.0f} {by2 + bh} {x:.0f} {by2 + bh}"
        GRN = "&H0050E650&"
        add(0, t_load, "Hook", f"{{\\an4\\pos({x0},{by2 - 40})\\fs44\\c{WHT}}}CONTEXT LOADING", 5)
        add(t_load, total, "Hook", f"{{\\an4\\pos({x0},{by2 - 40})\\fs44\\c{GRN}\\fscx130\\fscy130\\t(0,200,\\fscx100\\fscy100)}}CONTEXT LOADED", 5)
        for k, bt in enumerate(beats):
            x = x0 + k * (sw + gap)
            add(0, total, "Bar", f"{{\\pos(0,0)\\an7\\c&H00303030&\\1a&H40&\\bord3\\3c&H00FFFFFF&}}{{\\p1}}{box(x, sw)}{{\\p0}}", 5)
            add(bt, t_load, "Bar", f"{{\\pos(0,0)\\an7\\c{YEL}\\clip({x:.0f},{by2},{x:.0f},{by2 + bh})\\t(0,250,\\clip({x:.0f},{by2},{x + sw:.0f},{by2 + bh}))}}{{\\p1}}{box(x, sw)}{{\\p0}}", 6)
            add(t_load, total, "Bar", f"{{\\pos(0,0)\\an7\\c{GRN}}}{{\\p1}}{box(x, sw)}{{\\p0}}", 6)
        spec["_sfx"] = (beats, t_load)
    if spec.get("end_text"):
        add(total - 1.8, total, "Hook", f"{{\\pos({W // 2},{CY + 190})\\c{YEL}\\fad(150,0)}}{spec['end_text']}", 3)

    hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Hook,Montserrat Black,78,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,7,4,5,40,40,0,1
Style: Small,Montserrat Black,30,&H00C8C8C8,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,1,0,1,3,0,5,20,20,0,1
Style: Label,Montserrat Black,58,&H0000E5FF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,1,0,1,5,3,5,20,20,0,1
Style: Bar,Montserrat Black,20,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: Cap,Montserrat Black,92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,1,0,0,0,100,100,0,0,1,8,5,5,50,50,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ass = os.path.join(wd, "overlay.ass"); open(ass, "w").write(hdr + "\n".join(ev) + "\n")
    os.makedirs(os.path.join(D, "out"), exist_ok=True)
    out = os.path.join(D, "out", spec["out"] + ".mp4")
    aud = ["-c:a", "copy"]; sfx_in = []
    if spec.get("_sfx"):
        sfx = os.path.join(wd, "sfx.wav"); make_sfx(sfx, total, *spec["_sfx"])
        sfx_in = ["-i", sfx]
        aud = ["-filter_complex", "[0:a][1:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]", "-map", "0:v", "-map", "[a]",
               "-c:a", "aac", "-b:a", "192k", "-ar", "48000"]
    run(["ffmpeg", "-v", "error", "-y", "-i", joined, *sfx_in, "-vf", f"subtitles={ass}:fontsdir={FONTS},setsar=1",
         "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high", "-pix_fmt", "yuv420p",
         *aud, "-aspect", "9:16", "-movflags", "+faststart", out])
    print(f"{spec['out']}: {total:.1f}s")
    return out, total


def make_sfx(path, total, beats, t_load):
    """tonal UI ticks per loading beat + 'loaded' chime (no noise)."""
    import numpy as np, wave
    SR = 48000; buf = np.zeros(int((total + 1) * SR))
    def put(sig, t, g):
        i = int(t * SR); j = min(len(buf), i + len(sig)); buf[i:j] += sig[: j - i] * g
    def tone(f, d, dec):
        t = np.arange(int(d * SR)) / SR; return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * np.exp(-t * dec)
    for k, bt in enumerate(beats):
        put(tone(1200 + 150 * k, 0.09, 45), bt, 0.30); put(tone(1800 + 220 * k, 0.07, 60), bt + 0.06, 0.18)
    for k, f in enumerate((784, 988, 1175, 1568)):
        put(tone(f, 0.5, 6), t_load + 0.06 * k, 0.16)
    pcm = (np.clip(buf[: int(total * SR)], -1, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())


def preview(path, times, dst):
    sel = "+".join(f"eq(n\\,{int(t * FPS)})" for t in times)
    run(["ffmpeg", "-v", "error", "-y", "-i", path, "-vf", f"select='{sel}',scale=270:-2,tile={len(times)}x1",
         "-vsync", "0", "-frames:v", "1", dst])
