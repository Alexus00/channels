# Owned channels — instructions for Claude (auto-loaded)
Owner runs YouTube Shorts from a phone with Swedish UI: keep replies short, give exact copy-paste title/description/pinned comment, time estimates and updates.

## Channels
- **Context Loading** (@contextloading10): narrated streamer stories (big streamers only: Kai, Speed, Adin, Jynxzi, CaseOh…). Signature format: cold-open hook → frozen frame + "CONTEXT LOADING" segmented bar that fills per narration beat (tick SFX) → "CONTEXT LOADED" → payoff → verdict question. AI narrator only (Piper en_US-ryan-high, tools/mknarr.py). Work in `context-loading/` (irlgen.py, camgen.py, specs*.py, covers*.py, scout_big.py, mknarr.py).
- **Lane Nine Lab** (ranking/race channel, parked): procedural race videos, `lane-nine-ranking/` (race4.py, music.py). No noise beds, tonal music only.
- Campaign account @WhyNotTop-3 and @OneScrollMan are used for campaigns (see the campaigns repo).

## Read first
README.md → 02_PERFECT_SHORT.md → 08_LESSONS_LEARNED.md → research/VERIFY_CONTEXT_NICHE.md. Log every clip in clips_log.csv (+ 24h/72h stats when owner sends screenshots).

## Environment notes
YouTube media download is blocked from the cloud (metadata works with yt-dlp mweb/web_embedded clients). Twitch clips via yt-dlp/GQL, Kick via api/v2 + HLS. Fonts in ./fonts (symlink as ../fonts from subprojects). Large media is never committed.
