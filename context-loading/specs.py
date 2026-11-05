import sys, json
from irlgen import build, preview
N = json.load(open("narr/narr.json"))
def narr(src, a, key, x=960, va=None, **kw):
    d = dict(src=src, a=a, b=round(a + N[key]["dur"] + 0.25, 2), x=x, narr=f"narr/{key}.wav", nwords=N[key]["words"], duck=0.15, **kw)
    if va is not None: d["va"] = va
    return d
SPECS = {
 "speed": dict(out="sr_speed_250k_prank", credit="ISHOWSPEED · TWITCH", progress=True, progress_label="CONTEXT LOADING...",
    hook_lines=["HE THOUGHT HE WON", "$250,000..."],
    highlight=["$250", ",000,", ",000!", ",000.", "prank.", "won", "better.", "ishowspeed", "news.", "it?", "failed"],
    parts=[dict(src="speed_250k", a=33.8, b=37.1, x=900),                         # hook
           narr("speed_250k", 0.0, "speed_n1", x=650),
           dict(src="speed_250k", a=28.4, b=39.3, x=900),
           dict(src="speed_250k", a=39.6, b=46.3, x=900, zoom_at=44.6, zoom_len=1.5),
           dict(src="speed_250k", a=46.3, b=52.6, x=960),
           dict(src="speed_250k", a=54.5, b=57.7, x=960),
           narr("speed_250k", 52.6, "speed_n2", x=960)]),
 "lacy": dict(out="sr_lacy_500k_yen_bill", credit="LACY · TWITCH", progress=True, progress_label="CONTEXT LOADING...",
    hook_lines=["LACY SAW THE BILL", "IN JAPAN..."],
    highlight=["500", ",000", "yen?", "bill", "this!", "thousands", "dinner.", "japan,", "lacy"],
    parts=[dict(src="lacy_bill", a=15.4, b=17.6, x=1000),
           narr("lacy_bill", 0.0, "lacy_n1"),
           dict(src="lacy_bill", a=8.7, b=23.0, x=1000, zoom_at=21.2, zoom_len=1.6),
           narr("lacy_bill", 23.0, "lacy_n2", x=1000)]),
 "jake": dict(out="sr_jake_drink_thrown", credit="JAKENBAKELIVE · TWITCH", progress=True, progress_label="CONTEXT LOADING...",
    hook_lines=["SOMEONE THREW A DRINK", "AT JAKENBAKE..."],
    highlight=["woah!", "hell?", "drink", "jakenbake,", "halloween.", "beer.", "bomb", "calm?", "stupid,"],
    parts=[dict(src="jake_drink", a=5.0, b=6.6, x=960),
           narr("jake_drink", 0.0, "jake_n1"),
           dict(src="jake_drink", a=9.0, b=13.4, x=960),
           dict(src="jake_drink", a=16.1, b=19.6, x=960),
           dict(src="jake_drink", a=27.9, b=31.2, x=960, zoom_at=29.2, zoom_len=1.4),
           narr("jake_drink", 31.2, "jake_n2")]),
 "maya": dict(out="sr_maya_wolfdog_roxy", credit="MAYA · TWITCH", progress=True, progress_label="CONTEXT LOADING...",
    hook_lines=["SHE'S MORE WOLF", "THAN DOG..."],
    highlight=["wolf", "dog.", "roxy,", "roxy", "wild", "pet", "dna", "normal", "akela,", "dog?"],
    fix={"akila,": "AKELA,"},
    parts=[dict(src="maya_roxy", a=9.5, b=12.55, x=800),
           narr("maya_roxy", 0.0, "maya_n1", x=800),
           dict(src="maya_roxy", a=0.1, b=12.55, x=800, zoom_at=10.0, zoom_len=1.6),
           dict(src="maya_roxy", a=17.0, b=23.95, x=800),
           dict(src="maya_roxy", a=28.7, b=35.6, x=800),
           dict(src="maya_roxy", a=40.5, b=45.3, x=800),
           narr("maya_roxy", 45.4, "maya_n2", x=800)]),
 "elly": dict(out="sr_elly_face_card", credit="E11YSA · TWITCH", progress=True, progress_label="CONTEXT LOADING...",
    hook_lines=["HE LITERALLY PAYS", "WITH FACE CARD..."],
    highlight=["face", "card,", "card", "jeremiah,", "jeremiah.", "line", "funny", "pays", "live?"],
    parts=[dict(src="elly_facecard", a=27.55, b=30.45, x=900),
           narr("elly_facecard", 0.0, "elly_n1", x=900),
           dict(src="elly_facecard", a=12.4, b=16.65, x=900),
           dict(src="elly_facecard", a=27.55, b=30.45, x=900),
           dict(src="elly_facecard", a=33.0, b=39.95, x=900, zoom_at=38.9, zoom_len=1.3),
           dict(src="elly_facecard", a=41.05, b=41.6, x=900),
           dict(src="elly_facecard", a=45.3, b=50.3, x=900),
           narr("elly_facecard", 52.0, "elly_n2", x=900)]),
 "quin": dict(out="sr_quin_standing_jump", credit="QUIN69 · TWITCH", progress=True, progress_label="CONTEXT LOADING...",
    hook_lines=["QUIN69 TRIED A", "STANDING JUMP..."],
    highlight=["jump.", "jump,", "die.", "water.", "hard,", "jumped?", "quin69"],
    drop=["clay"],
    parts=[dict(src="quin_dives", a=23.6, b=26.0, x=1000),
           narr("quin_dives", 0.0, "quin_n1", x=1000),
           dict(src="quin_dives", a=9.2, b=18.25, x=1000),
           dict(src="quin_dives", a=21.8, b=26.5, x=1000, zoom_at=23.7, zoom_len=0.9),
           narr("quin_dives", 26.5, "quin_n2", x=1000)]),
 "erobb": dict(out="sr_erobb_burp", credit="EROBB221 · TWITCH", progress=True, progress_label="CONTEXT LOADING...",
    hook_lines=["HE ASKED HER", "TO BURP HIM..."],
    highlight=["burp", "burp.", "baby", "baby.", "burning", "hurts.", "hard?", "him?", "me?"],
    parts=[dict(src="erobb_burp", a=13.2, b=14.55, x=960),
           narr("erobb_burp", 0.0, "erobb_n1", x=960),
           dict(src="erobb_burp", a=2.3, b=3.95, x=960),
           dict(src="erobb_burp", a=13.2, b=14.55, x=960),
           dict(src="erobb_burp", a=31.9, b=35.0, x=960),
           dict(src="erobb_burp", a=37.3, b=46.0, x=960, zoom_at=42.9, zoom_len=1.2),
           narr("erobb_burp", 46.0, "erobb_n2", x=960)]),
}
if __name__ == "__main__":
    for k in sys.argv[1:]:
        for p in SPECS[k]["parts"]: p.setdefault("h", 950)
        out, tot = build(SPECS[k])
        preview(out, [0.3] + [round(tot * f, 2) for f in (0.12, 0.25, 0.4, 0.55, 0.7, 0.85, 0.97)], f"work/{k}_prev.jpg")
    open("work/done.flag", "w").write("ok")
