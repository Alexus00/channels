import json, sys, numpy as np
from faster_whisper import WhisperModel
vid = sys.argv[1]
det = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=4)
tr = WhisperModel("base.en", device="cpu", compute_type="int8", cpu_threads=4)
a = np.memmap(f"vod/{vid}.pcm", dtype=np.int16, mode="r")
SR, WIN = 16000, 20
out = {"lang": [], "words": []}
n = len(a) // (SR * WIN)
for i in range(n):
    ch = np.asarray(a[i*SR*WIN:(i+1)*SR*WIN], dtype=np.float32) / 32768
    if np.sqrt((ch**2).mean()) < 0.005: out["lang"].append("sil"); continue
    lang, p, _ = det.detect_language(ch)
    out["lang"].append(f"{lang}{int(p*100)}")
    if lang == "en" and p > 0.5:
        segs, _ = tr.transcribe(ch, word_timestamps=True, beam_size=1, condition_on_previous_text=False, vad_filter=True)
        out["words"] += [(round(w.start + i*WIN, 2), round(w.end + i*WIN, 2), w.word.strip()) for s in segs for w in s.words]
    if i % 30 == 0:
        json.dump(out, open(f"vod/{vid}_scan.json", "w")); print(vid, i, "/", n, flush=True)
json.dump(out, open(f"vod/{vid}_scan.json", "w")); print(vid, "done")
