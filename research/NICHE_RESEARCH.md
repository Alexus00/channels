# NICHE RESEARCH — streamer moments / "context" channels (Nov 2026)

Method: 10 YouTube searches (≈320 results) → ranked channels → pulled the latest 60 videos + 60 Shorts
(views, durations, titles) and subscriber counts of the 11 most relevant channels. Raw data: `search.txt`, `chandata.txt`.

## The competitors that matter
| Channel | Subs | Model | Shorts median | Long median | Best hits |
|---|---|---|---|---|---|
| **StreamFlix** | 427k | **Narrated facts/lists about top streamers** — closest to us | **65k** | **588k** | Short "Kai Cenat Saved A Kid's Life" **16M**; "3 Most Expensive Jewelry Kai Cenat Owns" 7.4M; long "10 Times YouTubers Saved Lives" 7.7M, "How Fast Is IShowSpeed Actually?" 7.5M |
| **Internet Anarchist** | 1.87M | Narrated downfall/drama stories | 48k | **599k** | "The Never-Ending Downfall of KSI" 3M; Short "Pirate Software Has Lost Everything... 😳" 1.4M |
| **Nuke's Top 5** | 4.8M | Narrated "Top N" scary lists (adjacent niche) | — | **3.8M** | "5 Twitch Streamers Who Caught Ghosts on Stream" 6M |
| **Conflext** | 218k | Long listicles "Times Streamers ___" | — | 13k | "When Streamers Meet Old Friends From Their Past" 1.5M |
| **Celebrix** | 92k | Long listicles, dark/relationship themes | — | 4.6k | "15 Times Streamers Caught Their Girlfriends Cheating Live" 483k |
| **Stay Speechless** | 30k | Long listicles | — | 132k | "BEST vs WORST Speed Races.." 5.6M; "15 Times Jamal BROKE Character Live.." 3.5M |
| **SpeedUniverse** | 4.2M | Single-streamer fan clips (Speed) | 55k | 163k | Short "Bro Eats Anything 😭😂" **9.1M** |
| **Speedy Ben** | 200k | Speed fan clips | — | — | "clips that made IShowSpeed famous" **48M** |
| **Kai Cenat Shorts** | 62k | Plain Kai clips, descriptive titles | **10.5k** | 1M (comps) | ceiling ~37k on Shorts |
| **Top Kek** | 516k | Twitch compilations | 4.5k | 91k | "Most Viewed Twitch Clips OF ALL TIME 23" 990k |

## What the winners do (patterns in the data)
1. **Narration beats raw clips by ~6×.** Plain clip Shorts (Kai Cenat Shorts) median **10.5k**; narrated fact/story Shorts (StreamFlix) median **65k**. Matches the Oct-2026 originality rule → our narrator format is the right call.
2. **Mega-streamers carry the views.** Every top result is IShowSpeed, Kai Cenat, Jynxzi/CaseOh, Jamal, AMP, xQc. → ≥60% of our videos should feature Speed / Kai / top-10 English streamers. Name in the title, first word if possible.
3. **Winning themes (ranked by peak views):**
   - Heroic/wholesome: *saved a life*, *helped a fan*, *gave money back* (16M, 7.7M, 7.2M)
   - Money/expensive: *most expensive*, *$10 vs $10,000,000* (7.4M, 3.2M)
   - Fans/strangers going too far, meeting old friends (4.5M, 1.5M)
   - "Clips that made X famous" origin stories (48M)
   - Caught/exposed (cheating, scams, hacked) (2.8M, 483k)
   - Downfall/"lost everything" (3M) — only with verifiable facts
4. **Lists win on both lengths.** Shorts: "3 Most ___" / "3 Times ___". Long-form: "10/15/20 Times Streamers ___" (12–25 min).
5. **Title style:**
   - ≤ 8 words, name first, curiosity gap, ends with "..." and 0–2 emojis (😳😭💀).
   - Superlatives / numbers ("3 Most Expensive", "15 Times", "$10 vs $10,000,000").
   - Fan channels use ultra-vague "Bro ___ 😭" titles (9.1M), which works when the face in the first frame is famous.
6. **Long-form is where scale lives:** StreamFlix and Internet Anarchist both have ~600k median long-form views vs ~50–65k on Shorts. Shorts are the funnel; long-form is the business.
7. **Losers:** generic compilations with no story (Top Kek Shorts median 4.5k), dark/edgy listicles on small channels (Celebrix median 4.6k). Volume without a strong theme doesn't work.

## What we change in Context Loading
| Before | After |
|---|---|
| Any viral clip from the week | **≥60% Speed / Kai / top-10 English streamers**; trending clips only if the story is strong |
| Only single-story Shorts | **3 formats in rotation:** (A) single story (current), (B) **"3 Times / 3 Most ___" narrated list Short** (StreamFlix model), (C) "clips that made X famous"-style origin story |
| Header = what happens | Header = **theme hook**: "KAI CENAT SAVED A FAN...", "3 TIMES SPEED'S FANS WENT TOO FAR" |
| Weekly recap long-form | **Weekly themed listicle long-form** (12–20 min): "15 Times Streamers Saved Lives", "15 Times IShowSpeed Fans Went Too Far" + one weekly recap if time allows |
| Neutral verdict line | Verdict line that sparks comments ("Would you have done the same?") — keep |

## Guardrails
- Downfall/drama narration must only state verifiable facts (defamation risk). Prefer heroic/wholesome/money themes, which also performed best.
- Keep the same narrator, look and loading-bar brand so the channel is recognisable.
