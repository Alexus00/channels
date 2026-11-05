# 02 — THE PERFECT SHORT (checklist — every clip must pass ALL of it)

## A. Moment selection (most important step)
- [ ] The moment is **standalone**: makes sense with zero knowledge of the stream.
- [ ] It has a clear **payoff** (reaction, reveal, punchline, absurd line, twist) — write it in one sentence.
- [ ] Emotion: funny / shocking / wholesome / "no way" / relatable. If you can't name the emotion, skip it.
- [ ] Strong moment sources: viewer-made clips with high views, chat spikes, loud audio peaks, "no way / is this real / what the" lines, strangers reacting, animals, lookalikes, big reveals, gambling-free wins.
- [ ] Clean: no slurs, no explicit sex talk, no betting-brand promo, nothing that breaks campaign rules (07).
- [ ] Language matches the campaign (run `tools/lang.py` — e.g. Gattouz requires 100% English speech).

## B. Hook (frame 1 → 2 s)
- [ ] **Frame 1 shows the payoff or the most curious thing** (the grillz, the monkey, the lookalike) — not an intro, not a wide shot, not blur.
- [ ] **Captions start at 0.0 s.** Never an empty caption area in the first second (our 51.6%-swipe flop had none for 7 s).
- [ ] Header (top) states what's happening in ≤ 2 short lines, curiosity-driven but TRUE:
      formula: `[WHO] + [DID WHAT]...` e.g. "GATTOUZ0 MATCHED WITH / HIS LOOKALIKE..."
- [ ] Hook line types that work: question from the clip ("ARE THOSE MONKEYS?"), pattern interrupt, the punchline line itself replayed first ("cold open"), "WAIT FOR..." only if the payoff really comes.
- [ ] Never misleading (campaign rejections + trust loss).

## C. Retention edit
- [ ] Length: **8–35 s** default. Short loops (8–15 s) for single-moment payoffs; 20–35 s for stories. >60 s only for TikTok Creator Rewards eligibility on strong stories.
- [ ] Cut every 1–2 s of dead air; no pauses > 0.4 s unless it's comedic timing.
- [ ] Cold open: hook clip (0.6–2 s) → rewind to setup → payoff → end.
- [ ] Punch-in zoom on each peak reaction (0.6–1.5 s). Quick white flash on hard cutaways (optional).
- [ ] Every shot sharp: replace blurry/whip-pan/back-of-head frames with a cutaway (J-cut) of the subject.
- [ ] **Loop**: last line flows into the first frame (end on a reaction that matches the opening).
- [ ] Progress bar (thin yellow) — signals "it's short", improves completion.
- [ ] Pattern break every ~8–12 s on longer clips (new angle, zoom, caption color, cut).

## D. Captions
- [ ] Accurate word-timed captions (faster-whisper word timestamps; verify by reading the dump).
- [ ] 1–3 words per chunk, Montserrat Black ~92 px, white with thick black outline, pop-in animation.
- [ ] Key words highlighted **yellow** (names, nouns of the payoff).
- [ ] Captions **never cover faces** (caption band between panels or below the action panel).
- [ ] Censor swears (F*CK, SH*T, B*TCH); remove slurs entirely (and cut them from audio if audible).
- [ ] Fix name spellings (Whisper mishears: "Gatoos"→GATTOUZ, "Dinesh"→DANESH, "saskie"→SASUKE).
- [ ] Don't cut a sentence mid-word at part ends (check the last caption chunk of every part).

## E. Technical specs (YouTube rejects otherwise)
- [ ] 1080×1920, 30 fps, H.264 high, yuv420p, AAC 192k 48 kHz.
- [ ] **SAR 1:1 and DAR 9:16** (`setsar=1` + `-aspect 9:16`). Wrong SAR → "Invalid video orientation". Fix existing file:
      `ffmpeg -i in.mp4 -c copy -bsf:v h264_metadata=sample_aspect_ratio=1/1 -aspect 9:16 out.mp4`
- [ ] Loudness −14 LUFS (loudnorm I=-14:TP=-1.5).
- [ ] Verify with `ffprobe -show_entries stream=width,height,sample_aspect_ratio,display_aspect_ratio`.

## F. Layouts (pick by source)
| Source | Layout | Tool |
|---|---|---|
| Streamer w/ facecam + game | facecam top / game bottom | `tools/shortgen.py` |
| IRL / single camera / podcast | header + 9:8 crop panel + caption area | `tools/irlgen.py` |
| Omegle/umingle/chat-roulette two-cam | stranger cam top / caption band / streamer cam bottom | `tools/camgen.py` |

## G. Cover / thumbnail
- [ ] 1080×1920: 2-line header (white + yellow), big face/action crop with yellow rules, 2-word red badge, `#TAG` footer.
- [ ] The cover shows the payoff object (grillz, monkey, lookalike face). Faces with emotion > objects > scenery.
- [ ] Tools: `tools/covers_irl.py`, `tools/covers_cam.py`, `tools/covergen.py`.

## H. Post text
- [ ] Title (YT): `[What happens] [emoji] #Creator #shorts` — < 60 chars before hashtags.
- [ ] Caption: one short line saying what happens + required campaign hashtag(s) (+ person hashtags if required).
- [ ] Campaign-specific: tags/@ rules (Danesh: NO @ anywhere; Gattouz: tag official account if available).
- [ ] No "follow/buy/DM/click" on promo-sensitive campaigns. Pinned comment = a question to drive replies (only where allowed).
- [ ] Made for kids = NO. Visibility = Public. Keep public ≥ 30 days for campaigns.

## I. Final QA (do it every time)
1. Read the full caption dump (every chunk) — fix fragments/cut words.
2. Look at a 7–20 frame contact sheet — fix blurry shots, wrong crops, covered faces.
3. Check first frame + last frame (hook + loop).
4. ffprobe SAR/DAR/duration.
5. Append to `log/clips_log.csv`.
