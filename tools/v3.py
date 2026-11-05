import sys
from race3 import build
def yr(y):
    y = int(y); w = {0:"",1:"one",2:"two",3:"three",4:"four",5:"five",6:"six",7:"seven",8:"eight",9:"nine",10:"ten",11:"eleven",12:"twelve",
        13:"thirteen",14:"fourteen",15:"fifteen",16:"sixteen",17:"seventeen",18:"eighteen",19:"nineteen",20:"twenty",30:"thirty",40:"forty",
        50:"fifty",60:"sixty",70:"seventy",80:"eighty",90:"ninety"}
    two = lambda n: w[n] if n in w else w[n // 10 * 10] + " " + w[n % 10]
    if y >= 2000 and y < 2010: return "two thousand " + (w[y - 2000] if y > 2000 else "")
    return two(y // 100) + " " + (("oh " + w[y % 100]) if 0 < y % 100 < 10 else two(y % 100))
def P(label, tag, flag, time): return dict(label=label, tag=tag, flag=flag, time=time, say=f"{label.title()} {yr(tag)}")
SPECS = {
 "olympic": dict(out="ln_olympic_100m_champions", title=["EVERY OLYMPIC 100M CHAMPION", "RACING AT ONCE"], sub="REAL WINNING TIMES · 1988 – 2024",
    racers=[P("LEWIS","1988","🇺🇸",9.92), P("CHRISTIE","1992","🇬🇧",9.96), P("BAILEY","1996","🇨🇦",9.84), P("GREENE","2000","🇺🇸",9.87),
            P("GATLIN","2004","🇺🇸",9.85), P("BOLT","2008","🇯🇲",9.69), P("BOLT","2012","🇯🇲",9.63), P("BOLT","2016","🇯🇲",9.81),
            P("JACOBS","2020","🇮🇹",9.80), P("LYLES","2024","🇺🇸",9.79)],
    punch_tts="Usain Bolt... beat Usain Bolt. So who's the fastest ever?", punch="Usain Bolt... beat Usain Bolt. So who's the fastest ever?"),
 "wr": dict(out="ln_100m_world_records", title=["EVERY 100M WORLD RECORD", "RACING AT ONCE"], sub="REAL RECORD TIMES · 1968 – 2009",
    racers=[P("HINES","1968","🇺🇸",9.95), P("SMITH","1983","🇺🇸",9.93), P("LEWIS","1988","🇺🇸",9.92), P("BURRELL","1991","🇺🇸",9.90),
            P("LEWIS","1991","🇺🇸",9.86), P("BAILEY","1996","🇨🇦",9.84), P("GREENE","1999","🇺🇸",9.79), P("POWELL","2007","🇯🇲",9.74),
            P("BOLT","2008","🇯🇲",9.69), P("BOLT","2009","🇯🇲",9.58)],
    punch_tts="Nobody has touched nine point five eight since two thousand nine. Will anyone ever beat it?",
    punch="Nobody has touched 9.58 since 2009. Will anyone ever beat it?"),
}
if __name__ == "__main__":
    for k in sys.argv[1:]: build(SPECS[k])
