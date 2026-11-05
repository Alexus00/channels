import sys, subprocess, os, concurrent.futures as cf
src, name, a, b = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4])
base = src.rsplit("/", 1)[0] + "/1080p60"
pl = subprocess.run(["curl", "-s", "-m", "60", f"{base}/playlist.m3u8"], capture_output=True, text=True).stdout.splitlines()
t, dur, segs = 0.0, None, []
for l in pl:
    if l.startswith("#EXTINF:"): dur = float(l[8:].split(",")[0])
    elif l and not l.startswith("#") and dur is not None:
        if t + dur > a and t < b: segs.append((t, l))
        t += dur; dur = None
d = f"vod/r_{name}"; os.makedirs(d, exist_ok=True)
def get(i): subprocess.run(["curl", "-s", "-m", "120", "--retry", "3", "-o", f"{d}/{i:03d}.ts", f"{base}/{segs[i][1]}"])
with cf.ThreadPoolExecutor(8) as ex: list(ex.map(get, range(len(segs))))
open(f"{d}/list.txt", "w").write("".join(f"file '{i:03d}.ts'\n" for i in range(len(segs))))
off = a - segs[0][0]
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{d}/list.txt", "-ss", f"{off}", "-t", f"{b - a}",
                "-vf", "fps=30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-c:a", "aac", "-b:a", "192k", f"src/{name}.mp4"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"src/{name}.mp4", "-ac", "1", "-ar", "16000", "-f", "s16le", f"wav/{name}.pcm"], check=True)
print(name, len(segs), "segs")
