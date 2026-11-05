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


TOPY, CAMH, BOTY = 280, 720, 1200        # stranger cam 280..1000, caption band 1000..1200, streamer cam 1200..1920


def render_part(p, out):
    tx, ty, tw, th = p["top"]; bx, by_, bw, bh = p["bot"]
    va = p.get("va", p["a"]); dur = p["b"] - p["a"]
    en = "0"; zb = p.get("zoom", "bot")
    if p.get("zoom_at") is not None:
        t0 = p["zoom_at"] - va
        en = f"between(t,{t0:.2f},{t0 + p.get('zoom_len', 1.2):.2f})"
    zx, zy, zw, zh = (bx, by_, bw, bh) if zb == "bot" else (tx, ty, tw, th)
    zw2, zh2 = int(zw * 0.72) // 2 * 2, int(zh * 0.72) // 2 * 2
    zx2, zy2 = zx + (zw - zw2) // 2, zy + (zh - zh2) // 3
    zy_out = BOTY if zb == "bot" else TOPY
    vf = (f"[0:v]scale=1920:1080,setsar=1,fps={FPS},split=4[a][b][c][d];"
          f"[a]crop={tw}:{th}:{tx}:{ty},scale={W}:{H},gblur=sigma=40,eq=brightness=-0.4[bg];"
          f"[b]crop={tw}:{th}:{tx}:{ty},scale={W}:{CAMH}:flags=lanczos,eq=contrast=1.05:saturation=1.1[t];"
          f"[c]crop={bw}:{bh}:{bx}:{by_},scale={W}:{CAMH}:flags=lanczos,eq=contrast=1.05:saturation=1.1[u];"
          f"[d]crop={zw2}:{zh2}:{zx2}:{zy2},scale={W}:{CAMH}:flags=lanczos,eq=contrast=1.08:saturation=1.12[z];"
          f"[bg][t]overlay=0:{TOPY}[x1];[x1][u]overlay=0:{BOTY}[x2];[x2][z]overlay=0:{zy_out}:enable='{en}',"
          f"drawbox=x=0:y={TOPY + CAMH}:w={W}:h={BOTY - TOPY - CAMH}:color=black@0.55:t=fill,format=yuv420p,setsar=1[v]")
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{va}", "-t", f"{dur}", "-i", os.path.join(D, "src", f"{p.get('vsrc', p['src'])}.mp4"),
         "-ss", f"{p['a']}", "-t", f"{dur}", "-i", os.path.join(D, "src", f"{p['src']}.mp4"),
         *(["-i", p["narr"]] if p.get("narr") else []),
         "-filter_complex", vf + (f";[1:a]aresample=48000,volume={p.get('duck', 0.15)}[o];[2:a]aresample=48000,apad,volume=1.6[n];"
                                  f"[o][n]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=9[au]"
                                  if p.get("narr") else ";[1:a]aresample=48000,loudnorm=I=-14:TP=-1.5:LRA=9[au]"),
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
        timeline.append((t, p)); t += p["b"] - p["a"]
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
        y = 95 + k * 110 if len(hl) > 1 else 150
        add(0, total, "Hook", f"{{\\pos({W // 2},{y})\\c{YEL if k == 0 else WHT}}}{line}")
    # small source credit under the header (not a watermark: plain text credit)
    labels = [(t0, t0 + p["b"] - p["a"], p["label"]) for t0, p in timeline if p.get("label")]
    if labels:
        for st, en, lab in labels:
            add(st, en, "Label", f"{{\\pos({W // 2},{TOPY - 50})\\fad(80,0)}}{lab}", 1)
    else:
        add(0, total, "Small", f"{{\\pos({W // 2},{TOPY - 30})}}{spec.get('credit', '')}")

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
    # group into 1-3 word chunks for readability, keeping key words alone
    chunks, cur = [], []
    for c in caps:
        k = re.sub(r"[^\w'\-]", "", c[2]).lower()
        if cur and (len(cur) >= 3 or c[0] - cur[-1][1] > 0.35 or k in hi or c[3] != cur[-1][3] or
                    re.sub(r"[^\w'\-]", "", cur[-1][2]).lower() in hi or cur[-1][2][-1:] in ".?!,"):
            chunks.append(cur); cur = []
        cur.append(c)
    if cur: chunks.append(cur)
    CY = (TOPY + CAMH + BOTY) // 2
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
        by = BOTY - 12
        if spec.get("progress_label"):
            add(0, total, "Small", f"{{\\an4\\pos(24,{by - 26})\\c{YEL}\\fs30}}{spec['progress_label']}", 4)
        add(0, total, "Bar", f"{{\\pos(0,{by})\\an7\\c{YEL}\\clip(0,{by},1,{by + 10})\\t(0,{int(total * 1000)},\\clip(0,{by},{W},{by + 10}))\\p1}}m 0 0 l {W} 0 {W} 10 0 10{{\\p0}}", 4)
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
    run(["ffmpeg", "-v", "error", "-y", "-i", joined, "-vf", f"subtitles={ass}:fontsdir={FONTS},setsar=1",
         "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high", "-pix_fmt", "yuv420p",
         "-c:a", "copy", "-aspect", "9:16", "-movflags", "+faststart", out])
    print(f"{spec['out']}: {total:.1f}s")
    return out, total


def preview(path, times, dst):
    sel = "+".join(f"eq(n\\,{int(t * FPS)})" for t in times)
    run(["ffmpeg", "-v", "error", "-y", "-i", path, "-vf", f"select='{sel}',scale=270:-2,tile={len(times)}x1",
         "-vsync", "0", "-frames:v", "1", dst])
