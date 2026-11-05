import sys, json
import irlgen, camgen
N = json.load(open("narr/narr.json"))
def narr(src, a, key, **kw):
    return dict(src=src, a=a, b=round(a + N[key]["dur"] + 0.25, 2), narr=f"narr/{key}.wav", nwords=N[key]["words"], duck=0.15, **kw)
EM = dict(x=1728, y=610, h=440)                           # Emily facecam crop
CS = dict(top=(0, 138, 402, 268), bot=(480, 200, 960, 640))   # CaseOh: facecam top, Minecraft bottom
SPECS = {
 "emily": (irlgen, dict(out="sr_emily_cops_scream", credit="EXTRAEMILY · TWITCH", progress=True, progress_label="CONTEXT LOADING...",
    hook_lines=["EXTRAEMILY SCREAMED SO LOUD", "THE COPS SHOWED UP..."],
    highlight=["police", "scream", "screamed", "okay,", "okay", "alone", "nice", "game?", "door.", "door", "officers"],
    parts=[dict(src="emily_cops", a=6.55, b=9.95, caps=[(0.0, 1.6, "THE POLICE CAME TO MY DOOR,"), (1.6, 3.4, "BECAUSE THEY HEARD ME SCREAM.")], **EM),
           narr("emily_cops", 27.1, "emily_n1", **EM),
           dict(src="emily_cops", a=13.2, b=25.0, zoom_at=22.0, zoom_len=1.4, **EM),
           dict(src="emily_cops", a=25.9, b=27.05, **EM),
           dict(src="emily_cops", a=39.9, b=47.05, **EM),
           dict(src="emily_cops", a=58.5, b=59.95, **EM),
           narr("emily_cops", 48.5, "emily_n2", **EM)])),
 "caseoh": (camgen, dict(out="sr_caseoh_freestyle", credit="CASEOH · TWITCH", progress=True, progress_label="CONTEXT LOADING...",
    hook_lines=["CASEOH STARTED FREESTYLING", "IN MINECRAFT..."],
    highlight=["diamonds,", "fly", "grinding,", "fun,", "day,", "away,", "run,", "10.", "freestyling."],
    parts=[dict(src="caseoh_freestyle", a=13.6, b=18.3, **CS),
           narr("caseoh_freestyle", 0.0, "caseoh_n1", **CS),
           dict(src="caseoh_freestyle", a=0.6, b=1.5, **CS),
           dict(src="caseoh_freestyle", a=13.6, b=28.3, zoom="top", zoom_at=19.0, zoom_len=1.6, **CS),
           dict(src="caseoh_freestyle", a=32.4, b=35.05, **CS),
           narr("caseoh_freestyle", 28.3, "caseoh_n2", **CS)])),
}
if __name__ == "__main__":
    for k in sys.argv[1:]:
        mod, spec = SPECS[k]
        if mod is irlgen:
            for p in spec["parts"]: p.setdefault("h", 950)
        out, tot = mod.build(spec)
        mod.preview(out, [0.3] + [round(tot * f, 2) for f in (0.12, 0.25, 0.4, 0.55, 0.7, 0.85, 0.97)], f"work/{k}_prev.jpg")
    open("work/done3.flag", "w").write("ok")
