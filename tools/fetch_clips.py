import json, sys, urllib.request
login, period, n = sys.argv[1], sys.argv[2], int(sys.argv[3])
q = '{ user(login:"%s"){ clips(first:%d, criteria:{period:%s, sort:VIEWS_DESC}){edges{node{slug title viewCount durationSeconds createdAt game{name}}}}}}' % (login, n, period)
req = urllib.request.Request("https://gql.twitch.tv/gql", data=json.dumps({"query": q}).encode(),
                             headers={"Client-ID": "kimne78kx3ncx6brgo4mv6wki5h1ko"})
for i, e in enumerate(json.load(urllib.request.urlopen(req))["data"]["user"]["clips"]["edges"]):
    x = e["node"]
    print(i, x["viewCount"], x["durationSeconds"], x["createdAt"][:10], (x["game"] or {}).get("name"), "|", x["title"], "|", x["slug"])
