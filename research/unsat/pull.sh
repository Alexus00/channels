while IFS='|' read k q; do
  timeout 120 yt-dlp --flat-playlist --js-runtimes node --extractor-args "youtube:player_client=mweb,web_embedded" --print "$k|%(channel)s|%(channel_id)s|%(view_count)s|%(duration)s|%(title)s" "ytsearch50:$q" 2>/dev/null
done < q.txt
echo DONE
