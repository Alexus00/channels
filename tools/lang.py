import json, glob, os, numpy as np
from faster_whisper import WhisperModel
m = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=8)
C = json.load(open("clips.json"))
res = {}
for f in sorted(glob.glob("wav/*.pcm")):
    k = os.path.basename(f)[:-4]
    a = np.fromfile(f, dtype=np.int16).astype(np.float32) / 32768
    langs = []
    for st in range(0, max(1, len(a) - 16000 * 3), 16000 * 8):
        ch = a[st:st + 16000 * 8]
        if np.sqrt((ch ** 2).mean()) < 0.005: langs.append("sil"); continue
        lang, p, allp = m.detect_language(ch)
        langs.append(f"{lang}{int(p*100)}")
    res[k] = langs
    print(C[k]["views"], C[k]["duration"], C[k]["title"][:30], "|", " ".join(langs), flush=True)
json.dump(res, open("langs.json", "w"))
