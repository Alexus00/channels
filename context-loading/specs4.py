import sys, json
from irlgen import build, preview
N = json.load(open("narr/narr.json"))
def narr(src, a, key, **kw):
    return dict(src=src, a=a, b=round(a + N[key]["dur"] + 0.25, 2), narr=f"narr/{key}.wav", nwords=N[key]["words"], duck=0.15, **kw)
S = "kai_tyla"
SPEC = dict(out="sr_kai_tyla_friendzone", credit="KAI CENAT · TWITCH", progress=True, progress_label="CONTEXT LOADING...",
    hook_lines=["KAI CENAT ASKED TYLA", "ON A DATE ON STREAM..."],
    highlight=["date", "tyla?", "friends,", "friends.", "real?", "serious.", "live", "much", "shot?", "friend-zoned,", "everyone."],
    fix={"tyler": "TYLA?"},
    parts=[dict(src=S, a=3.8, b=6.45, x=840),                                  # hook: the question
           narr(S, 0.0, "tyla_n1", x=840),
           dict(src=S, a=3.8, b=14.45, x=840),
           dict(src=S, a=15.1, b=20.65, x=960),
           dict(src=S, a=22.3, b=24.1, x=960),
           dict(src=S, a=28.7, b=33.95, x=960, zoom_at=29.0, zoom_len=1.3),     # payoff: "But we friends, though."
           narr(S, 34.0, "tyla_n2", x=960)])
if __name__ == "__main__":
    for p in SPEC["parts"]: p.setdefault("h", 1080)
    out, tot = build(SPEC)
    preview(out, [0.3] + [round(tot * f, 2) for f in (0.12, 0.25, 0.4, 0.55, 0.7, 0.85, 0.97)], "work/tyla_prev.jpg")
