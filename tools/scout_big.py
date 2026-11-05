import json, urllib.request, sys
BIG = ["kaicenat","ishowspeed","jynxzi","caseoh_","xqc","fanum","dukedennis","jasontheween","lacy","plaqueboymax","hasanabi",
       "ludwig","emiru","pokimane","zackrawrr","stableronaldo","tyler1","agent00","extraemily","sketch","yourragegaming","marlon",
       "rakai","kingsleyyy","tfue","summit1g","shroud","nickmercs","sneako","n3on","adinross","jackdoherty","cinna","valkyrae"]
def gql(q):
    req = urllib.request.Request("https://gql.twitch.tv/gql", data=json.dumps({"query": q}).encode(), headers={"Client-ID": "kimne78kx3ncx6brgo4mv6wki5h1ko"})
    return json.load(urllib.request.urlopen(req, timeout=30))
since = sys.argv[1]
out = []
for u in BIG:
    try:
        d = gql('{ user(login:"%s"){ clips(first:15, criteria:{period:LAST_WEEK, sort:VIEWS_DESC}){edges{node{slug title viewCount durationSeconds createdAt game{name}}}}}}' % u)
        for e in ((d.get("data") or {}).get("user") or {}).get("clips", {}).get("edges", []):
            n = e["node"]
            if n["createdAt"][:10] >= since: n["who"] = u; out.append(n)
    except Exception as ex: print("err", u, ex)
out.sort(key=lambda n: -n["viewCount"])
json.dump(out, open("work/scout_big.json", "w"))
for i, n in enumerate(out[:90]):
    print(i, n["viewCount"], n["durationSeconds"], n["createdAt"][5:16], n["who"], (n["game"] or {}).get("name", "")[:10], "|", n["title"][:60], "|", n["slug"])
