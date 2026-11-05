import sys
from irlgen import build, preview

SPECS = {
 "nun": dict(out="danesh_nun_grillz", credit="DUKE DENNIS HALLOWEEN PARTY",
    hook_lines=["HE PUT ICED OUT GRILLZ", "ON HIS NUN MASK..."],
    highlight=["mask...", "look", "different.", "good.", "good,", "that!", "turn.", "crazy."],
    parts=[dict(src="d950", a=108.6, b=110.8, x=820,
                caps=[(0.0, 1.1, "LOOK AT"), (1.1, 2.2, "THE MASK...")]),          # hook: mask wearing the grillz
           dict(src="d950", a=101.5, b=112.5, x=900),
           dict(src="d950", a=119.0, b=126.3, x=900),
           dict(src="d950", a=127.4, b=135.0, x=960, zoom_at=133.6, zoom_len=1.4),
           dict(src="d950", a=138.5, b=141.3, x=960),
           dict(src="d950", a=144.2, b=146.6, x=960)]),
 "kai": dict(out="danesh_kai_cenat_mold", credit="DUKE DENNIS HALLOWEEN PARTY",
    hook_lines=["KAI CENAT MEETS", "DANESH DIAMONDS"],
    highlight=["mold?", "grill?", "danesh.", "danesh,", "boy.", "this,", "right."],
    fix={"dinesh": "DANESH."},
    parts=[dict(src="d1410", a=25.7, b=27.95, x=1150),                         # hook: "You ready to do the mold?"
           dict(src="d1410", a=17.6, b=19.5, x=1150),
           dict(src="d1410", a=23.7, b=31.5, x=1150, zoom_at=25.8, zoom_len=1.2),
           dict(src="d1410", a=37.4, b=37.98, x=1150),
           dict(src="d1410", a=41.45, b=43.2, x=1150),
           dict(src="d1410", a=43.25, b=46.3, x=1200, zoom_at=44.9, zoom_len=1.3)]),
 "duke": dict(out="danesh_duke_new_grillz", credit="DUKE DENNIS HALLOWEEN PARTY", progress=True,
    hook_lines=["DUKE DENNIS SHOWS OFF", "HIS NEW GRILLZ..."],
    highlight=["grill?", "guy.", "good.", "good,", "boy.", "grillz..."],
    parts=[dict(src="d950", a=10.95, b=11.55, x=730, y=360, h=620,
                caps=[(0.0, 0.6, "LOOK AT THE GRILLZ...")]),                # hook: grillz close-up
           dict(src="d1410", a=17.6, b=18.45, vsrc="d950", va=20.0, x=1330, y=300, h=560, flash=True),  # "You see his new grill?" over grillz
           dict(src="d1410", a=18.45, b=19.5, vsrc="d950", va=22.7, x=1250, h=950),                                      # "Oh, it's up there. Check it out."
           dict(src="d1410", a=26.95, b=27.95, vsrc="d950", va=21.2, x=990),               # "Look what we just did for my boy." over Danesh + Duke
           dict(src="d950", a=17.3, b=18.4, va=19.6, x=1000, caps=[(0.05, 0.55, "HE IS"), (0.55, 1.1, "THE GUY.")]),
           dict(src="d950", a=138.5, b=141.3, x=1300),
           dict(src="d950", a=145.7, b=146.6, va=140.5, x=1300)]),
}
if __name__ == "__main__":
    for k in sys.argv[1:]:
        for p in SPECS[k]["parts"]: p.setdefault("h", 950)
        out, tot = build(SPECS[k])
        preview(out, [0.2] + [round(tot * f, 2) for f in (0.15, 0.3, 0.45, 0.6, 0.75, 0.95)], f"work/{k}_prev.jpg")
