# Smart Multitrack Cut — Build Write-Up

## 1. The Need

We'd just built a two-scene OBS setup (landscape for YouTube, vertical for Shorts/TikTok/Reels) with three switchable full-frame sources: Chrome, Terminal, and a webcam. The open question was *who decides which one is on screen at any given moment* — right now, that's a manual toggle.

The first idea on the table was tempting: let the camera direction be random, or just leave it up to Claude to decide live. Both got rejected on the spot, for the same underlying reason — a live cut needs to know what's actually happening at that moment to be a *good* cut, and neither a coin flip nor an AI with no live view of the room can judge that. A random cut can land mid-click on something important; a blind "just decide" is the same mistake wearing a different hat.

The better version of the idea: don't decide live at all. Analyze the *recorded* footage afterward, where the whole timeline already exists, and make the cut decision from real signals — motion on the screen tracks, detected speech on the reaction/webcam track — instead of guessing.

## 2. The Build Journey

1. **First blocker: no simultaneous multi-track recording.** The clean way to get separate, perfectly-synced files per source is OBS's third-party "Source Record" filter plugin. It wasn't installed — `CreateSourceFilter` came back with "Your specified filter kind is not supported by OBS. Check that any necessary plugins are loaded." Rather than stop, we used a manual workaround: toggle one source visible at a time and record three short clips sequentially (Chrome, Terminal, Webcam). Good enough to validate the *analysis logic*, explicitly not a substitute for real simultaneous tracks — logged as a known limitation, not hidden.

2. **A real privacy near-miss, caught immediately.** The Chrome test clip was supposed to show the OpenArt tab being scrolled. It actually recorded the Gmail inbox — because OBS's window capture follows whichever tab is frontmost in the Chrome window, not whichever tab is being scripted. Real subject lines were visible in that recording. We checked it together, agreed no actual secrets were exposed (no passwords, no API key values — just email address and vendor-name metadata), and kept the clip as an honest example rather than pretending it didn't happen. It's exactly the scenario a "dedicated recording browser profile" recommendation from earlier in the process was meant to prevent — and it happened anyway, which is worth more as a documented lesson than a quietly-deleted mistake.

3. **First real run of the cut-decision script: a degenerate result.** `decide_cuts.py`'s first output assigned the *entire* 48-second timeline to the webcam track — obviously wrong, since the room was quiet the whole time. Rather than accept it, we dug into the raw numbers: the webcam's audio track measured 2.5e-05 to 5.3e-05 RMS — essentially flat noise, not speech. The actual bug: each track's score was being independently min-max normalized before comparing them, and normalization always rescales *whatever range exists* to span 0–1 — even pure noise. So a flat, meaningless audio track was getting rescaled into a "confident" signal that could out-compete real motion on the other tracks, once compared this way.

4. **The fix, and why it's the right one.** Screen tracks (motion) got normalized *jointly* with each other, since they're the same modality and a shared scale keeps their relative comparison meaningful. The reaction track's audio, instead of being normalized at all, gets compared against an absolute threshold — is there enough raw signal to call this real speech, yes or no — rather than always being handed a rescaled "confidence" score whether or not anything real happened. Re-running with this fix produced a sensible 5-segment cut alternating between the two screen tracks based on actual relative motion, with the webcam correctly never winning (since there was no real speech in that clip).

5. **A second, unrelated gap, found while wrapping up.** While double-checking whether the webcam's own microphone needed special handling, we found something bigger: neither OBS scene actually had the real computer microphone ("Mic/Aux") added as a source at all — only the three video captures. Every recording made during this entire build had *no real narration audio whatsoever*. Fixed by adding Mic/Aux and Desktop Audio to both scenes. This means the audio-threshold logic in step 4 has never actually been tested against real speech yet — logged honestly as an open item, not glossed over.

## 3. Final Write-Up

**Purpose:** Given several separately-recorded video tracks from one session (a screen capture, a webcam), automatically decide which one should be on screen at each moment — based on what's actually happening (motion, detected speech), not randomness and not a permanent split-screen — and render an actual rough-cut video from that decision.

**Why it needed both of us:** The AI wrote the analysis math and caught the normalization bug by actually inspecting the raw numbers instead of trusting a clean-looking result. The human caught the deeper judgment call at the very start — that live random switching and "just let the AI decide in the moment" were both the wrong shape of solution, before any code got written — and separately caught the missing-microphone gap by asking a simple, practical question ("do we need the webcam's mic, or just the computer one I already use") that the AI wouldn't have thought to check on its own.

**End result:** Three working scripts (`analyze_activity.py`, `decide_cuts.py`, `render_cut.py`) that take raw multi-track footage and produce an actual cut-decision list plus a rendered rough-cut MP4, tested end-to-end on real recorded footage from this session. The core scoring bug (cross-modality normalization) is fixed and documented so it doesn't get reintroduced.

**Known limitations, honestly:**
- Tested against sequentially-recorded clips, not true simultaneous multi-track footage — needs re-validation once the Source Record plugin (or equivalent) is actually installed.
- The reaction-track audio threshold is an unvalidated placeholder — it's never been tested against real speech, because real narration audio wasn't even being recorded until the very end of this build.
- Hard cuts only — no crossfades or audio mixing yet.
- Doesn't do any cursor-zoom/legibility reframing — it decides *which* track, not how to reframe it for a small vertical phone screen.
