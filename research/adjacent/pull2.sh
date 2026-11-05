while IFS='|' read k cid name; do
  timeout 120 yt-dlp --flat-playlist --playlist-items 1:30 --js-runtimes node --extractor-args "youtube:player_client=mweb,web_embedded" --print "S|$k|$cid|%(view_count)s" "https://www.youtube.com/channel/$cid/shorts" 2>/dev/null
  timeout 60 yt-dlp -J --flat-playlist --playlist-items 0 --js-runtimes node --extractor-args "youtube:player_client=mweb,web_embedded" "https://www.youtube.com/channel/$cid/shorts" 2>/dev/null > /tmp/claude-0/-home-user/ce6c2c0f-4b27-56c6-b6f7-a34554f4ddc4/scratchpad/meta.json
  python3 -c "import json,sys
try: d=json.load(open(sys.argv[1])); print('C|'+sys.argv[2]+'|'+sys.argv[3]+'|'+str(d.get('channel_follower_count')))
except Exception: print('C|'+sys.argv[2]+'|'+sys.argv[3]+'|None')" /tmp/claude-0/-home-user/ce6c2c0f-4b27-56c6-b6f7-a34554f4ddc4/scratchpad/meta.json "$k" "$cid"
done < indie.txt
echo DONE
