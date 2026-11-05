"""python3 mknarr.py key "text" [key "text" ...]  -> narr/<key>.wav + narr.json words (display tokens = script words)."""
import json, sys, subprocess, numpy as np, wave
from faster_whisper import WhisperModel
N = json.load(open("narr/narr.json")); m = WhisperModel("small.en", device="cpu", compute_type="int8", cpu_threads=8)
args = sys.argv[1:]
for key, text in zip(args[::2], args[1::2]):
    raw = f"narr/{key}_raw.wav"
    subprocess.run(["python3", "-m", "piper", "-m", "voice/en_US-ryan-high.onnx", "--length-scale", "0.9", "-f", raw], input=text.encode(), check=True, capture_output=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,aresample=48000",
                    "-ac", "1", f"narr/{key}.wav"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"narr/{key}.wav", "-f", "s16le", "-ac", "1", "-ar", "16000", f"narr/{key}.pcm"], check=True)
    a = np.fromfile(f"narr/{key}.pcm", dtype=np.int16).astype(np.float32) / 32768; dur = len(a) / 16000
    segs, _ = m.transcribe(a, word_timestamps=True, beam_size=5)
    ws = [(w.start, w.end) for s in segs for w in s.words]
    toks = text.split()
    if len(ws) == len(toks):
        words = [(round(s, 2), round(e, 2), t) for (s, e), t in zip(ws, toks)]
    else:  # spread proportionally by characters
        L = sum(len(t) for t in toks); c = 0; words = []
        for t in toks:
            s = dur * c / L; c += len(t); words.append((round(s, 2), round(dur * c / L, 2), t))
    N[key] = dict(dur=round(dur, 2), words=words); print(key, round(dur, 2), len(ws), len(toks))
json.dump(N, open("narr/narr.json", "w"))
