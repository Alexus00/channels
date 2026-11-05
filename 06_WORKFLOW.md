# 06 — WORKFLOW (exact technical pipeline)

Environment: Linux, python3, ffmpeg (with libass), yt-dlp, faster-whisper (models cached under
~/.cache/huggingface: base.en, small.en, medium.en, small multilingual), PIL. Fonts in `../fonts`.

## 0. Project setup
Each job gets its own project dir (e.g. `work/gattouz/`). **Copy** the needed tool(s) into it — tools
resolve paths relative to their own folder: `src/` (video sources), `words.json` (transcripts), `out/`, `work/`,
and fonts at `<project>/../fonts`. Simplest: create projects as `clip-studio/projects/<name>/`.

## 1. Find moments
| Platform | How |
|---|---|
| **Kick** clips | `curl -H "Accept: application/json" -H "User-Agent: Mozilla/5.0" "https://kick.com/api/v2/channels/<slug>/clips?sort=view&time=all|month|week"` (paginate with `&cursor=`; response sometimes has trailing data — parse first JSON object). Field `clip_url` = m3u8 |
| **Kick** VODs | `https://kick.com/api/v2/channels/<slug>/videos` → `source` master.m3u8 (variants 1080p60/720p60/480p30/360p30/160p30) |
| **Twitch** clips | `python3 fetch_clips.py <login> LAST_DAY|LAST_WEEK|LAST_MONTH|ALL_TIME <N>` (public GQL; can't paginate all-time → one call with `first:N`) |
| **YouTube** | **Blocked from this server** (bot check / 429 / 403 on media even with node JS runtime). Workarounds: owner downloads with yt-dlp/a-Shell on their device and shares a **Dropbox/Google Drive link** (`dl=1` for Dropbox folders = zip). Metadata sometimes works with `--extractor-args youtube:player_client=mweb,web_embedded --js-runtimes node`. |

Scouting signals: viewer clip view counts, chat spikes, transcript lines like "no way / is this real / what the", loud peaks.

## 2. Download
- Kick/Twitch clip m3u8 (byte-range HLS): `yt-dlp -q --hls-prefer-native -o out.mp4 <m3u8>` ✅
- Kick VOD screening (cheap): `python3 getvod.py <master.m3u8> <id> 160p30` → audio pcm for scanning.
- Kick VOD exact range in 1080p: `python3 getrange.py <master.m3u8> <name> <start_s> <end_s>` → `src/<name>.mp4` + `wav/<name>.pcm` (30 fps re-encode).
- **ffmpeg cannot resolve hosts through the proxy** → never let ffmpeg/yt-dlp's ffmpeg downloader fetch URLs (`--download-sections` fails with 251). Download with curl/yt-dlp-native, then ffmpeg locally.

## 3. Transcribe + language check
- Decode audio to 16 kHz mono s16le PCM first (avoids PyAV metadata bugs):
  `ffmpeg -i x.mp4 -ac 1 -ar 16000 -f s16le wav/x.pcm`
- Language per 8–20 s window: `lang.py` (faster-whisper `small` multilingual `detect_language`). Required for English-only campaigns.
- Words: `tr.py <ids>` (small.en, word_timestamps, vad_filter) → `words.json` {id: [[start,end,word],...]} + readable dump.
- Long VODs: `vodscan.py`-style loop = detect language per 20 s, transcribe English windows with base.en (fast), then re-transcribe chosen ranges with small.en/medium.en.
- CPU is 4 cores: don't run >2 heavy jobs at once.

## 4. Build the edit (spec-driven)
**irlgen.py** (single camera) spec:
```python
dict(out="name", credit="SMALL CREDIT LINE", progress=True,
     hook_lines=["LINE ONE (yellow)", "LINE TWO..."],
     highlight=["words", "to", "yellow"], fix={"misheard": "CORRECT"},
     parts=[dict(src="srcname", a=10.9, b=11.95,        # audio+words source & seconds
                 va=20.0, vsrc="other",                  # optional: video from another moment (cutaway / J-cut)
                 x=730, y=360, h=620,                    # crop centre x, centre y, crop height (keeps 9:8)
                 zoom_at=11.3, zoom_len=0.6,             # punch-in
                 flash=True,                             # white flash on cut
                 drop=["word"], caps=[(0.0, 0.6, "MANUAL CAPTION")])])
```
`build(spec)` → `out/<name>.mp4`; `preview(path, [times], "work/x.jpg")` → contact sheet.
Sources: `src/hq_<src>.mp4` for irlgen; `src/<src>.mp4` for camgen.

**camgen.py** (chat-roulette two-cam) — same spec keys + per part `top=(x,y,w,h)`, `bot=(x,y,w,h)` crops
(umingle 1080p layout: top=(8,58,670,447) stranger, bot=(8,590,670,447) streamer), `zoom="top"|"bot"`.
Layout: header 0–280, top cam 280–1000, caption band 1000–1200, bottom cam 1200–1920.

**shortgen.py** (facecam + gameplay; countdown/rapid/story styles) — see docstring at top of file.

Example specs: `example_specs_irl.py` (Danesh), `example_specs_camstack.py` (Gattouz).

## 5. QA (mandatory)
```bash
python3 - <<'EOF'   # caption dump
import re; t=open("work/<name>/overlay.ass").read()
print("|".join(re.sub(r"\{[^}]*\}","",l.split(",,0,0,0,,")[1]) for l in t.splitlines() if ",Cap," in l))
EOF
ffmpeg -i out/<name>.mp4 -vf "fps=2,scale=216:-2,tile=12x2" -frames:v 1 work/sheet.jpg   # look at it
ffprobe -v error -select_streams v -show_entries stream=width,height,sample_aspect_ratio,display_aspect_ratio out/<name>.mp4
```
Fix: cut-off words at part ends (extend `b`), fragments (`drop`), blur (cutaway via `va`), faces under captions (crop `x/y`).

## 6. Covers
`covers_irl.py` / `covers_cam.py`: `cover(name, src, t, x, line1, line2, badge1, badge2)`; pick a frame with the payoff visible
(check candidate frames with a quick contact sheet first).

## 7. Deliver & schedule
- Copy finals to a user-visible folder (e.g. `/home/user/shorts/<campaign>/`) and send with **SendUserFile**.
- Give copy-paste title/caption/pinned comment + posting time.
- **Metricool** (MCP): `createScheduledPost` needs a public media URL → upload to a temp host first
  (uguu.se works, ~3 h expiry; litterbox.catbox.moe often 500s). Uploads need owner approval.
  Free plan: 20 posts/month. Times in Europe/Stockholm.
- Append to `log/clips_log.csv`.

## Known pitfalls
- `pgrep -f "<pattern>"` inside an until-loop matches its own shell → infinite wait. Use a pid or a done-file.
- Background jobs > 10 min: run with `run_in_background` and wait on a file/pid, not on pgrep of the command string.
- YouTube "Invalid video orientation" = SAR not 1:1 → `setsar=1` + `-aspect 9:16`.
- Whisper timestamps drift on music/noise; manual `caps` for key lines (hooks!) are safer.

## 8. Narration (Stream Rewind format)
- TTS: `pip install piper-tts`; voices from `https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/high/en_US-ryan-high.onnx` (+ `.onnx.json`).
  `echo "text" | python3 -m piper -m en_US-ryan-high.onnx --length-scale 0.9 -f line.wav`
- Get word timings by transcribing the wav (small.en), fix names by merging tokens ("I show speed" → IShowSpeed), store in `narr/narr.json` {key: {dur, words}}.
- irlgen part: `dict(src=..., a=..., b=a+dur+0.25, narr="narr/key.wav", nwords=words, duck=0.15)` → original audio ducked to 15% under the narrator; captions come from `nwords`.
- Scout: `tools/scout_twitch.py LAST_DAY|LAST_WEEK "IRL" "Just Chatting"` (English, top by views). Twitch clips download: `yt-dlp -f "best[height<=1080]" https://clips.twitch.tv/<slug>`.
- Projects need `projects/fonts` → symlink to `../fonts` (`ln -sfn ../fonts projects/fonts`), else captions fall back to a default font and covers crash.
