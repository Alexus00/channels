import json, sys, os, numpy as np
from faster_whisper import WhisperModel
m = WhisperModel("small.en", device="cpu", compute_type="int8", cpu_threads=8)
C = json.load(open("clips.json")); L = json.load(open("langs.json"))
W = json.load(open("words.json")) if os.path.exists("words.json") else {}
for k in sys.argv[1:]:
    a = np.fromfile(f"wav/{k}.pcm", dtype=np.int16).astype(np.float32) / 32768
    segs, _ = m.transcribe(a, word_timestamps=True, beam_size=5, condition_on_previous_text=False, vad_filter=True)
    W[k] = [(round(w.start, 2), round(w.end, 2), w.word.strip()) for s in segs for w in s.words]
    json.dump(W, open("words.json", "w"))
    print(f"\n### {k} | {C[k]['title']} | {C[k]['duration']}s | {C[k]['category']['name']}")
    line, t0 = [], None
    for a_, b_, w in W[k]:
        if t0 is None: t0 = a_
        line.append(w)
        if w[-1:] in ".?!" and len(line) > 3 or len(line) > 18:
            print(f"{t0:6.1f} {' '.join(line)}"); line, t0 = [], None
    if line: print(f"{t0:6.1f} {' '.join(line)}")
