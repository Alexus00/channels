sort -u -t'|' -k1,1 chans.txt | while IFS='|' read cid name; do
  timeout 120 yt-dlp --flat-playlist --playlist-items 1:30 --js-runtimes node --extractor-args "youtube:player_client=mweb,web_embedded" --print "S|$cid|%(view_count)s|%(title)s" "https://www.youtube.com/channel/$cid/shorts" 2>/dev/null
  timeout 60 yt-dlp -J --flat-playlist --playlist-items 0 --js-runtimes node --extractor-args "youtube:player_client=mweb,web_embedded" "https://www.youtube.com/channel/$cid/shorts" 2>/dev/null | python3 -c "import json,sys
try:
  d=json.load(sys.stdin); print('C|$cid|'+str(d.get('channel_follower_count'))+'|'+(d.get('channel') or '$name'))
except Exception: print('C|$cid|None|$name')"
done
echo DONE
