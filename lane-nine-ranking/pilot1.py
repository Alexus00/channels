import json, subprocess, numpy as np
from faster_whisper import WhisperModel
from race import build
VOICE = "../streamrewind/voice/en_US-ryan-high.onnx"
m = WhisperModel("small.en", device="cpu", compute_type="int8", cpu_threads=4)
def say(key, tts, disp):
    subprocess.run(["python3", "-m", "piper", "-m", VOICE, "--length-scale", "0.9", "-f", f"narr/{key}.wav"], input=tts.encode(), check=True, capture_output=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"narr/{key}.wav", "-ac", "1", "-ar", "16000", "-f", "s16le", f"narr/{key}.pcm"], check=True)
    a = np.fromfile(f"narr/{key}.pcm", dtype=np.int16).astype(np.float32) / 32768
    segs, _ = m.transcribe(a, word_timestamps=True)
    ws = [(w.start, w.end) for s in segs for w in s.words]; toks = disp.split()
    if len(ws) != len(toks):
        st, en = ws[0][0], ws[-1][1]; step = (en - st) / len(toks); ws = [(st + i * step, st + (i + 1) * step) for i in range(len(toks))]
    return len(a) / 16000, list(zip([w[0] for w in ws], [w[1] for w in ws], toks))
R = [dict(label="LEWIS", tag="1988", flag="🇺🇸", time=9.92), dict(label="CHRISTIE", tag="1992", flag="🇬🇧", time=9.96),
     dict(label="BAILEY", tag="1996", flag="🇨🇦", time=9.84), dict(label="GREENE", tag="2000", flag="🇺🇸", time=9.87),
     dict(label="GATLIN", tag="2004", flag="🇺🇸", time=9.85), dict(label="BOLT", tag="2008", flag="🇯🇲", time=9.69),
     dict(label="BOLT", tag="2012", flag="🇯🇲", time=9.63), dict(label="BOLT", tag="2016", flag="🇯🇲", time=9.81),
     dict(label="JACOBS", tag="2020", flag="🇮🇹", time=9.80), dict(label="LYLES", tag="2024", flag="🇺🇸", time=9.79)]
start = 0.8
d1, w1 = say("n1", "Every Olympic one hundred meter champion since nineteen eighty eight. Racing at the same time.",
             "Every Olympic 100m champion since 1988. Racing at the same time.")
d2, w2 = say("n2", "Usain Bolt... beat Usain Bolt. So who is the fastest of all time?",
             "Usain Bolt... beat Usain Bolt. So who is the fastest of all time?")
t1 = start + 0.15; race_end = start + max(r["time"] for r in R) + 0.3; t2 = race_end + 1.0
HI = {"olympic", "100m", "1988.", "same", "bolt...", "bolt.", "fastest", "time?"}
def chunks(ws, t0):
    out, cur = [], []
    for a, b, w in ws:
        cur.append((a, b, w))
        if len(cur) == 2 or w[-1] in ".?,":
            out.append((t0 + cur[0][0], t0 + cur[-1][1], " ".join(x[2] for x in cur).upper(), any(x[2].lower() in HI for x in cur))); cur = []
    if cur: out.append((t0 + cur[0][0], t0 + cur[-1][1], " ".join(x[2] for x in cur).upper(), True))
    return out
c1, c2 = chunks(w1, t1), chunks(w2, t2)
caps = [(0, t1 + w1[0][0], "WHO WINS?", True)] + c1 + [(c1[-1][1], race_end, "WHO WINS?", True)] + c2
for i in range(len(caps) - 1):   # hold each chunk until the next one
    a, b, s, h = caps[i]; caps[i] = (a, max(b, caps[i + 1][0]), s, h)
spec = dict(out="pf_olympic_100m_champions", title=["EVERY OLYMPIC 100M CHAMPION", "RACING AT ONCE"],
            sub="REAL WINNING TIMES · 1988 – 2024", racers=R, start=start, caps=caps, board_title="PHOTO FINISH",
            narr=[("narr/n1.wav", t1), ("narr/n2.wav", t2)], board=max(4.2, d2 + 1.6), brand="PHOTO FINISH LAB")
build(spec)
