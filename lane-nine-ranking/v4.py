import sys
from race4 import build
from v3 import yr
def P(label, tag, flag, time): return dict(label=label, tag=tag, flag=flag, time=time, say=f"{label.title()} {yr(tag)}")
SPECS = {
 "cheetah": dict(out="ln9_champions_vs_lane9", title=["8 OLYMPIC CHAMPIONS", "VS LANE 9"], sub="REAL RECORDED TIMES · LANE 9 IS A SECRET",
    racers=[P("BAILEY","1996","🇨🇦",9.84), P("GREENE","2000","🇺🇸",9.87), P("GATLIN","2004","🇺🇸",9.85), P("BOLT","2008","🇯🇲",9.69),
            P("BOLT","2012","🇯🇲",9.63), P("BOLT","2016","🇯🇲",9.81), P("JACOBS","2020","🇮🇹",9.80), P("LYLES","2024","🇺🇸",9.79),
            dict(label="SARAH", tag="CHEETAH", flag="🐾", time=5.95, mystery=True, kind="cheetah")],
    pick_tts="Pick a lane. Lane nine is a secret.", pick_disp="Pick a lane. Lane 9 is a secret.",
    mid_tts="Wait... lane nine is gone! Who is that?", mid_disp="Wait... lane 9 is gone! Who is that?!", mid_at=2.2,
    reveal_tts="Lane nine... was a cheetah. Sarah ran it in five point nine five seconds.", reveal_disp="Lane 9... was a cheetah. Sarah ran it in 5.95 seconds.",
    reveal_title="A CHEETAH", reveal_sub="SARAH · CINCINNATI ZOO · 100M IN 5.95s (2012)",
    q_tts="Which lane did you pick?", q_disp="Which lane did you pick?"),
 "wr": dict(out="ln9_world_records_vs_lane9", title=["8 WORLD RECORD HOLDERS", "VS LANE 9"], sub="REAL RECORD TIMES · LANE 9 IS A SECRET",
    racers=[P("SMITH","1983","🇺🇸",9.93), P("LEWIS","1988","🇺🇸",9.92), P("BURRELL","1991","🇺🇸",9.90), P("LEWIS","1991","🇺🇸",9.86),
            P("BAILEY","1996","🇨🇦",9.84), P("GREENE","1999","🇺🇸",9.79), P("POWELL","2007","🇯🇲",9.74), P("BOLT","2008","🇯🇲",9.69),
            dict(label="BOLT", tag="2009", flag="🇯🇲", time=9.58, mystery=True)],
    pick_tts="Pick a lane. Lane nine is a secret.", pick_disp="Pick a lane. Lane 9 is a secret.",
    mid_tts="Lane nine is pulling away! Who is that?", mid_disp="Lane 9 is pulling away! Who is that?!", mid_at=6.0,
    reveal_tts="Lane nine... was Usain Bolt. His nine point five eight is still the world record.", reveal_disp="Lane 9... was Usain Bolt. His 9.58 is still the world record.",
    reveal_title="USAIN BOLT", reveal_sub="BERLIN 2009 · 9.58s · STILL THE WORLD RECORD",
    q_tts="Which lane did you pick?", q_disp="Which lane did you pick?"),
}
if __name__ == "__main__":
    for k in sys.argv[1:]: build(SPECS[k])
