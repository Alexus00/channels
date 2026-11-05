import json
from irlgen import build, preview
N = json.load(open("narr/narr.json"))
S = "kai_pc_broke"
def narr(a, key, **kw):
    return dict(src=S, a=a, b=round(a + N[key]["dur"] + 0.3, 2), narr=f"narr/{key}.wav", nwords=N[key]["words"], duck=0.12, **kw)
SPEC = dict(out="sr_kai_madden_rage", credit="KAI CENAT · TWITCH",
    hook_lines=["KAI CENAT SMASHED HIS", "SETUP OVER MADDEN..."],
    highlight=["done", "nine", "seven.", "fails.", "loses.", "disconnects.", "worst", "over.", "fair", "lose", "every"],
    parts=[dict(src=S, a=19.7, b=21.0, x=900),                                    # cold open: the smash
           dict(src=S, a=20.2, b=21.0, x=900, slow=2, caps=[], flash=True),     # slow-mo replay of the hit
           dict(src=S, a=21.0, b=21.9, x=960, caps=[]),                         # No Signal
           narr(0.5, "pc_n1", x=607, freeze=True, va=0.5, beat=True),             # setup on frozen scoreboard
           dict(src=S, a=0.8, b=4.9, x=607, beat=True),                           # "please... just one"
           narr(4.9, "pc_n2", x=607, freeze=True, va=4.9, beat=True),
           narr(8.0, "pc_n3", x=760, freeze=True, va=8.0, beat=True),
           dict(src=S, a=5.3, b=9.0, x=607, flash=True),                          # CONTEXT LOADED -> payoff
           dict(src=S, a=9.0, b=13.0, x=1300),
           dict(src=S, a=16.4, b=20.2, x=960),
           dict(src=S, a=20.4, b=26.6, x=960),
           narr(23.0, "pc_n4", x=960, freeze=True, va=23.0)])
if __name__ == "__main__":
    for p in SPEC["parts"]: p.setdefault("h", 1080)
    out, tot = build(SPEC)
    preview(out, [0.0, 0.5, 1.0, 1.5, 2.0, 2.6, 3.2, 3.7, 5.5, 9.5, 12, 15.5, 18, 22, 26, 30, tot - 1], "work/pc_prev.jpg")
