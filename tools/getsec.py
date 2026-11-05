import sys, re, subprocess, os
pl, name, a, b = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
lines = open(pl).read().splitlines()
t = 0.0; segs = []
dur = None
for ln in lines:
    if ln.startswith("#EXTINF:"): dur = float(ln[8:].split(",")[0])
    elif ln.startswith("http") and dur is not None:
        if t + dur > a and t < b: segs.append((t, ln))
        t += dur; dur = None
os.makedirs(name, exist_ok=True)
for i, (st, u) in enumerate(segs):
    subprocess.run(["curl", "-s", "-m", "120", "-o", f"{name}/{i:03d}.ts", u], check=True)
open(f"{name}/list.txt", "w").write("".join(f"file '{i:03d}.ts'\n" for i in range(len(segs))))
off = a - segs[0][0]
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{name}/list.txt", "-ss", f"{off}", "-t", f"{b-a}",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-c:a", "aac", "-b:a", "192k", f"hq_{name}.mp4"], check=True)
print(name, len(segs), "segments, start", segs[0][0])
