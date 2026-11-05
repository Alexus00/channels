import sys, subprocess, os, concurrent.futures as cf
base, name, q = sys.argv[1].rsplit("/", 1)[0], sys.argv[2], sys.argv[3]
pl = subprocess.run(["curl", "-s", "-m", "60", f"{base}/{q}/playlist.m3u8"], capture_output=True, text=True).stdout.splitlines()
segs = [l for l in pl if l and not l.startswith("#")]
d = f"vod/{name}_{q}"; os.makedirs(d, exist_ok=True)
def get(i):
    out = f"{d}/{i:05d}.ts"
    if not os.path.exists(out) or os.path.getsize(out) == 0:
        subprocess.run(["curl", "-s", "-m", "120", "--retry", "3", "-o", out, f"{base}/{q}/{segs[i]}"])
with cf.ThreadPoolExecutor(16) as ex: list(ex.map(get, range(len(segs))))
open(f"{d}/list.txt", "w").write("".join(f"file '{i:05d}.ts'\n" for i in range(len(segs))))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{d}/list.txt", "-vn", "-ac", "1", "-ar", "16000", "-f", "s16le", f"vod/{name}.pcm"], check=True)
print(name, len(segs), "segments")
