import json, sys, urllib.request
def gql(q):
    req = urllib.request.Request("https://gql.twitch.tv/gql", data=json.dumps({"query": q}).encode(),
                                 headers={"Client-ID": "kimne78kx3ncx6brgo4mv6wki5h1ko"})
    return json.load(urllib.request.urlopen(req))
out = []
for game in sys.argv[2:]:
    q = '{ game(name:"%s"){ clips(first:%s, criteria:{period:%s, sort:VIEWS_DESC, languages:[EN]}){edges{node{slug title viewCount durationSeconds createdAt broadcaster{login} }}}}}' % (game, 100, sys.argv[1])
    d = gql(q)
    for e in (d.get("data") or {}).get("game", {}).get("clips", {}).get("edges", []):
        n = e["node"]; n["game"] = game; out.append(n)
    if d.get("errors"): print(d["errors"])
out.sort(key=lambda n: -n["viewCount"])
json.dump(out, open("scout.json", "w"))
for i, n in enumerate(out[:80]):
    print(i, n["viewCount"], n["durationSeconds"], n["createdAt"][:10], n["broadcaster"]["login"] if n["broadcaster"] else "?", n["game"][:8], "|", n["title"][:60], "|", n["slug"])
