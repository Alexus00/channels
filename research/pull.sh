while read name cid; do
  for tab in videos shorts; do
    timeout 150 yt-dlp --flat-playlist --playlist-items 1:60 --js-runtimes node --extractor-args "youtube:player_client=mweb,web_embedded" \
      --print "$name|$tab|%(view_count)s|%(duration)s|%(title)s" "https://www.youtube.com/channel/$cid/$tab" 2>/dev/null
  done
  timeout 90 yt-dlp -J --flat-playlist --playlist-items 0 --js-runtimes node --extractor-args "youtube:player_client=mweb,web_embedded" "https://www.youtube.com/channel/$cid/videos" 2>/dev/null | python3 -c "import json,sys;d=json.load(sys.stdin);print('$name|SUBS|'+str(d.get('channel_follower_count'))+'||'+(d.get('description') or '').replace('\n',' ')[:200])"
done < chans.txt
echo DONE
