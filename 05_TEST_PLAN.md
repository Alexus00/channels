# 05 — TEST PLAN & METRICS

## Metrics to read (per post, after 48–72 h)
| Metric | Where | Good | Action if bad |
|---|---|---|---|
| Viewed vs swiped away ("Stannade kvar och tittade") | YT Studio → video → Engagement | ≥ 65% | Hook problem → new frame-1, captions at 0 s, stronger header |
| Avg % viewed / completion | YT Studio / TikTok analytics | ≥ 60% (≥100% on loops) | Pacing problem → cut dead air, shorten, loop end |
| Views at 72 h | all | campaign clip ≥ 5k (Gattouz payout threshold) | If < 1k on 5 posts in a row → change format/campaign |
| Shares / sends / comments | all | any share signal | Add question/debate angle |
| Subs per 1k views | YT | ≥ 1 | Make the channel identity clearer |

## Experiment rules
- Change **one variable at a time** across a batch of ~5 posts: hook type, length, layout, header wording, posting time.
- Keep a format for ≥ 30 posts before declaring it dead (new channels need time to be profiled).
- Log every post in `log/clips_log.csv` with: date, platform, account, campaign, file, hook type, length, views_72h, stayed_pct, avg_viewed_pct, notes.
- Every Monday: sort the log by views_72h; copy the top 2 formats, retire the bottom 2.

## Current hypotheses to test (in order)
1. Cold-open hook (payoff first) vs chronological → expect higher "stayed".
2. 8–15 s loops vs 25–35 s stories → which gets more views per campaign?
3. Header style: "[WHO] [DID WHAT]..." vs quote of the line ("ARE THOSE MONKEYS?").
4. Posting time: 20:00 vs 01:00 Swedish.
5. Narrated (Track B) vs pure clip on the owned channel.
