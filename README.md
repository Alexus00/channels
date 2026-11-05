# CLIP STUDIO — start here

This folder is the full playbook for running a daily short-form + long-form channel business
(clips, campaigns, own channels). A fresh Claude session should read the files in this order
and then follow them exactly.

| File | What it is |
|---|---|
| `01_STRATEGY.md` | How the money works, which tracks to run, the 90-day plan |
| `02_PERFECT_SHORT.md` | **The checklist every short must pass** (hook, edit, captions, specs, cover, text) |
| `03_ALGORITHM_AND_POLICY.md` | What the platforms reward/punish in 2026 (originality rules, reused content, copyright) |
| `04_NICHES.md` | Niche selection: views vs pay, what to run |
| `05_TEST_PLAN.md` | How to run experiments, which metrics, when to kill / double down |
| `06_WORKFLOW.md` | The exact technical pipeline + tools in `tools/` + known pitfalls |
| `07_CAMPAIGNS.md` | Rules of every clipping campaign we have run (read before touching one) |
| `08_LESSONS_LEARNED.md` | Real results from our own posts — what worked, what flopped, why |
| `SOURCES.md` | Research sources (Nov 2026) |
| `channel_plan/` | **Context Loading** owned-channel plan (PLAN.md) + launch kit; pilots in `projects/streamrewind/` |
| `log/clips_log.csv` | Every clip made/posted — check it to avoid duplicates, append to it |
| `tools/` | Editing + download scripts (Python + ffmpeg + faster-whisper) |
| `fonts/` | Montserrat Black + Anton (captions/covers) |

## Owner context
- Owner works from a **phone** (Swedish UI). Deliver files with SendUserFile, give copy-paste text.
- Channels: **@OneScrollMan** (YouTube, streamer clips: Joe Bart, ohnePixel) + a new campaign/clip account
  (YouTube/TikTok/IG). Metricool is connected for scheduling (brand id 7618343, Europe/Stockholm, free plan = 20 posts/month).
- Timezone: Sweden. US-audience posting time ≈ 20:00–01:00 Swedish (14:00–19:00 New York).

## Golden rules (never break)
1. Read the campaign rules (07) before cutting anything. Rejections cost more than slow work.
2. Every short passes `02_PERFECT_SHORT.md`. Hook = the payoff in frame 1, captions from 0.0s.
3. Transform, don't repost (03). Since Oct 2026 YouTube downranks re-uploads.
4. No slurs, no explicit sexual content, no misleading edits, no "free/giveaway" claims unless true and allowed.
5. Log every clip in `log/clips_log.csv`. Never post the same clip twice on one platform.

## Persistence warning
The cloud container is wiped between sessions. This folder must live in a **GitHub repo**
(private, e.g. `clip-studio`) so new sessions/scheduled tasks can clone it. If it isn't in a repo yet,
ask the owner to create one and push this folder.
