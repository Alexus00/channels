# CHANNEL PLAN — "CONTEXT LOADING" (working name)

**One-line promise:** *The craziest stream moments of the week — with the story behind them, in under 40 seconds.*

## 1. Why this niche (evidence + fit)
| Criterion | Evidence | Verdict |
|---|---|---|
| Demand | Top weekly Twitch IRL/Just Chatting clips alone get 5k–50k views *on Twitch*; streamer moments are among the most-watched Shorts categories | ✅ huge, refreshes weekly |
| Originality (Oct 2026 Shorts rule, reused-content YPP rule) | Plain clip re-uploads are downranked and compilations struggle with YPP; **narration/commentary/storytelling** is the accepted transformation | ✅ our format adds a scripted narrator (context + verdict), cold-open restructure, captions, zooms |
| Producible daily by us | Kick + Twitch fully accessible (YouTube downloads blocked → avoid YouTube-only creators); Piper TTS works offline; editor + narration pipeline built | ✅ |
| Money | Shorts RPM low ($0.03–0.30/1k) → profit must come from long-form weekly recap (entertainment ~$2–4 RPM) + campaigns + sponsors | ⚠️ plan below |
| Synergy | Same footage world as our clipping campaigns (Jason, Gattouz, etc.) → research reused | ✅ |

Rejected: finance/AI (no expertise/footage), horror narration (needs visuals we can't source legally), pure clip reposts (downranked, YPP-risky), gaming highlights (Shorts can hurt long-form there).

## 2. Identity
- **Name:** Context Loading . Handle: @contextloading10 (renamed from @Top5Taper).
- **Look:** black header, yellow/white Montserrat Black headline, captions band, yellow progress bar, red badge on covers. Consistent = recognisable in feed.
- **Voice:** one consistent narrator (Piper "Ryan", 0.9 length scale). Narrator only: (1) 1-line context, (2) 1-line verdict/question at the end. The streamer's real audio carries the middle.
- **About:** "Every week the internet's biggest streamers do something insane. We rewind it and tell you what actually happened. New stories daily."

## 3. Formats
### A. Daily Short — "Rewind Story" (20–40 s) ← core
```
0.0–2.0  COLD OPEN: the payoff line/visual (captions from 0.0)
2.0–5.5  NARRATOR: who + where + setup ("Lacy was out to dinner in Japan, when someone checked the bill.")
5.5–30   THE MOMENT: real audio, cut tight, punch-in on peak
30–32    NARRATOR verdict/question ("Would you have fallen for it?") → drives comments, loops
```
Header: `[STREAMER/SUBJECT] [DID WHAT]...` Credit line: `STREAMER · PLATFORM` (attribution).
### B. Weekly long-form — "This Week on Stream" (10–14 min) ← money
- Top 15–20 moments of the week, each with narrator intro + context + verdict, chapters, ranking (#20 → #1).
- Mid-roll eligible (>8 min). Thumbnail: biggest face + "#1 WAS INSANE" style.
- Reuse the week's Shorts as building blocks (same narration pipeline) — 1 extra day of work/week.
### C. Opportunistic — campaign cross-posts
- When a featured streamer has an active clipping campaign whose rules allow it, post a compliant version on the campaign account (never the same file twice per platform).

## 4. Content engine (daily, ~1–2 h of compute)
1. **Scout** (morning): `scout_twitch.py LAST_DAY "IRL" "Just Chatting"` + streamer list + Kick `/api/v2/channels/<slug>/clips?sort=view&time=day` for Kick IRL (xQc, Adin Ross, N3on, Jack Doherty, Gattouz0 English parts…).
2. **Filter**: English, ≥ 3k clip views, a story (setup → payoff), no sexual/"jiggly" bait, no slurs, no violence-only, no gambling promo, no minors.
3. **Transcribe** + pick 3 → write narration (facts only from what's visible/said + clip title; never invent).
4. **Render** with `irlgen.py` narration parts (`narr=`, `nwords=`, `duck=`), QA per 02 checklist, covers.
5. **Post**: YouTube Shorts + TikTok + Reels (owned accounts) at 20:00/01:00 Swedish; log.
6. **Weekly (Sunday)**: assemble long-form from the week's best 15–20, publish Monday.

**Accuracy rule:** narration states only verifiable facts (streamer name, what happens on screen, quotes). No guessed prices/locations/relationships. If unsure, describe what we see ("someone checked the bill").

## 5. Monetization roadmap (realistic numbers)
| Stage | Trigger | Revenue sources | Est. / month |
|---|---|---|---|
| 0 (month 1–2) | launch | none on YT; TikTok/IG reach; campaign cross-posts | $0–300 (campaigns) |
| 1 | 1k subs + 10M Shorts views/90d **or** 4k watch hours (long-form makes this realistic: 20 videos × 2k views × 10 min ≈ 6.7k h) | YPP: long-form ads + Shorts share | 1M long views × ~$2.5 = **$2.5k**; 10M Shorts × $0.1 = $1k |
| 2 | TikTok 10k followers + 100k views/30d (if region eligible) | TikTok Creator Rewards on >60 s versions of best stories | $0.4–1 per 1k qualified |
| 3 | ~50k subs | sponsors (apps, games, energy drinks — no gambling), channel memberships, merch | $500–5k per deal |
Profit levers ranked: **long-form watch time > sponsors > campaigns > Shorts ads**.

## 6. 90-day calendar
| Week | Output | Goal / KPI |
|---|---|---|
| 1 | 7 Shorts (1/day), 3 pilots done | ≥ 60% "stayed" on 4/7 |
| 2 | 7 Shorts + 1st long-form (8–10 min) | find best hook type |
| 3–4 | 14 Shorts + 2 long-form | 1 Short ≥ 50k views; long-form AVD ≥ 40% |
| 5–8 | 28 Shorts + 4 long-form | 1k subs; apply YPP when eligible |
| 9–12 | 28 Shorts + 4 long-form + TikTok >60 s versions | 4k watch hours; first sponsor outreach at 10k subs |
**Kill/scale rules:** after 30 Shorts, if median views < 1k → change hook style/narrator/source mix; if any format gets 3× median → make 5 more of it immediately.

## 7. Risks & mitigations
- **Copyright claims** (streamer or music): keep moments short, transformed, credited; mute background music; dispute with fair-use (commentary) only when legitimate; never use paywalled/sub-only content.
- **Streamer objects**: remove immediately and blacklist.
- **YPP reused-content rejection**: narration on every video, original long-form scripts, consistent identity; reapply after 30 days if rejected.
- **Inauthentic/template flag**: vary narrator scripts, hooks and structures; never auto-post identical templates in bulk.

## UPDATE (Nov 2026 niche research — see research/NICHE_RESEARCH.md)
- Narrated fact/story Shorts ≈ 6× plain clip Shorts (median 65k vs 10.5k). Keep narration on every video.
- ≥60% of uploads feature IShowSpeed / Kai Cenat / top-10 English streamers; name first in title.
- Rotate 3 Short formats: (A) single story, (B) "3 Times / 3 Most ___" narrated list, (C) "clips that made X famous" origin story.
- Best themes: heroic/wholesome (saved a life, helped a fan), money/expensive, fans going too far, caught/exposed, origin stories.
- Long-form = themed listicles, 12–20 min ("15 Times Streamers ___"), weekly. Competitor long-form medians ≈ 600k vs ≈ 60k on Shorts.

## Decision (Nov 4 2026): AI narrator only
Owner does not want to record their own voice. The standard is the Piper `en_US-ryan-high` voice (length-scale 0.9) via `tools/mknarr.py`.
Originality comes from the script, the loading-bar signature format and the story structure, not from a real voice.
