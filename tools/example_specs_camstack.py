import sys
from camgen import build, preview

UM = dict(top=(8, 58, 670, 447), bot=(8, 590, 670, 447))      # umingle layout: stranger cam / Gattouz cam
M = "clip_01M6CC7M92F7JW8P27YKJS6W97"
SPECS = {
 "monkeys": dict(out="gattouz_pet_monkeys", credit="GATTOUZ0 ON KICK", progress=True, layout=UM,
    hook_lines=["GATTOUZ0 SHOWED A STRANGER", "HIS PET MONKEYS..."],
    highlight=["monkeys?", "monkeys.", "kiwi.", "kisses", "lychee", "vegetables,", "healthy", "countries.", "date", "coffee", "beach"],
    fix={"lychee": "LYCHEE.", "kiwi.": "KIWI."},
    parts=[dict(src=M, a=57.4, b=59.25, caps=[(0.15, 1.85, "ARE THOSE MONKEYS?")]),          # hook
           dict(src=M, a=9.1, b=14.9, zoom_at=12.2, zoom_len=1.6),
           dict(src=M, a=48.4, b=52.6),
           dict(src=M, a=99.1, b=103.9),
           dict(src=M, a=121.3, b=126.3),
           dict(src=M, a=141.1, b=145.7, zoom_at=144.6, zoom_len=1.1)]),
 "lookalike": dict(out="gattouz_lookalike_son", credit="GATTOUZ0 ON KICK", progress=True, layout=UM,
    hook_lines=["GATTOUZ0 MATCHED WITH", "HIS LOOKALIKE..."],
    highlight=["me", "real?", "real", "you,", "son", "son,", "son?", "son.", "winning?", "child.", "young", "crazy"],
    parts=[dict(src="cr_lookalike", a=10.7, b=15.75, drop=["not,"]),                     # hook: "Why everyone look like me now?"
           dict(src="cr_lookalike", a=24.3, b=34.95, zoom="top", zoom_at=30.1, zoom_len=1.6),
           dict(src="cr_lookalike", a=41.95, b=49.2, caps=[(0.2, 1.3, "JUNIOR GATTOUZ."), (2.35, 3.15, "I THINK"), (3.15, 4.2, "HE'S MY CHILD."),
                (5.3, 5.75, "MY SON."), (5.75, 6.35, "HELLO SON,"), (6.35, 7.25, "HOW ARE YOU SON?")]),
           dict(src="cr_lookalike", a=51.6, b=54.4, caps=[(0.05, 0.95, "HELLO MY SON,"), (1.2, 1.9, "WHERE ARE YOU?"), (1.9, 2.8, "LOOKING FOR YOU.")]),
           dict(src="cr_lookalike", a=62.5, b=67.62, zoom="top", zoom_at=65.9, zoom_len=2.0)]),
 "fans": dict(out="gattouz_fans_cant_believe", credit="GATTOUZ0 ON KICK", progress=True, layout=UM,
    hook_lines=["STRANGERS CAN'T BELIEVE", "THEY MATCHED WITH GATTOUZ0"],
    highlight=["you", "bro?", "fingers", "five", "believe", "seven", "goat.", "genius", "fan", "smart", "love", "you!", "gattouz?"],
    fix={"gatoos": "GATTOUZ", "katu's": "GATTOUZ,", "katu's,": "GATTOUZ,", "those?": "GATTOUZ?"},
    parts=[dict(src="cr_fans2", a=11.45, b=15.6),                                          # hook: "Is this actually you bro?"
           dict(src="cr_fans2", a=20.2, b=27.1, zoom="top", zoom_at=25.9, zoom_len=1.2),
           dict(src="cr_fans1", a=22.6, b=28.7),
           dict(src="cr_fans1", a=31.2, b=38.0, caps=[(0.07, 1.4, "WHAT ARE YOU DOING HERE,"), (1.4, 2.4, "GATTOUZ?"), (2.4, 3.6, "I'M JUST"), (5.6, 6.25, "STREAMING"), (6.25, 6.8, "FOR FUN.")]),
           dict(src="cr_genius", a=23.85, b=31.2),
           dict(src="cr_genius", a=53.8, b=56.0, zoom="top", zoom_at=53.9, zoom_len=2.0)]),
 "belike": dict(out="gattouz_can_i_be_like_you", credit="GATTOUZ0 ON KICK", progress=True, layout=UM,
    hook_lines=["A FAN ASKED GATTOUZ0", "IF HE CAN BE LIKE HIM..."],
    highlight=["you?", "me.", "idea,", "moves.", "gattouz?", "good-looking", "-looking", "please?"],
    parts=[dict(src="cr_dab", a=51.7, b=56.0, zoom="bot", zoom_at=53.5, zoom_len=2.5),     # hook: "You reckon I can be like you?"
           dict(src="cr_dab", a=19.3, b=22.6, caps=[(0.06, 0.85, "NO WAY,"), (0.85, 1.5, "IS THAT ACTUALLY..."), (1.5, 2.45, "ARE YOU GATTOUZ?"), (2.45, 3.3, "WAIT, GATTOUZ!")]),
           dict(src="cr_dab", a=44.4, b=51.7),
           dict(src="cr_dab", a=51.7, b=60.75),
           dict(src="cr_dab", a=61.6, b=62.4)]),
}
if __name__ == "__main__":
    for k in sys.argv[1:]:
        for p in SPECS[k]["parts"]:
            for kk, vv in SPECS[k]["layout"].items(): p.setdefault(kk, vv)
        out, tot = build(SPECS[k])
        preview(out, [0.3] + [round(tot * f, 2) for f in (0.15, 0.3, 0.45, 0.6, 0.75, 0.95)], f"work/{k}_prev.jpg")
