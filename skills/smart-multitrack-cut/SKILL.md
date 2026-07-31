---
name: smart-multitrack-cut
description: "Automatically decide and render a rough cut across multiple separately-recorded video tracks (e.g. a screen capture and a webcam capture of the same session) based on real activity signals -- visual motion for screen tracks, detected speech for reaction/webcam tracks -- instead of a permanent split-screen or manual switching. Use when the user has multiple synced (or comparable) video tracks from one recording session and wants an automated first-pass edit that switches to whichever track is actually relevant at each moment."
metadata:
  author: user-derived
  source: "Built 2026-07-30 for the 'Behind the Chef AI' documentary's multi-source OBS recording setup (Chrome/Terminal/Webcam). Grew out of a rejected idea (live random camera-switching) -- a live director can't judge what's happening without seeing it happen, and neither can a script; a post-production tool that analyzes real activity signals after the fact can."
  version: "1.0.0"
---

# Smart Multitrack Cut

Turns multiple separately-recorded video tracks from one session into an automated rough-cut decision, based on what's actually happening in each track -- not randomness, and not a permanent split-screen.

## When to Activate

- The user has 2+ video files that were recorded during the same session (ideally simultaneously) and wants help deciding which one should be on screen at each moment
- The user wants an automated alternative to manually switching between a screen capture and a webcam/reaction shot
- The user explicitly asks for "smart cutting," "activity-based editing," or a similar automated multi-track edit assist

## Why Not Random, and Why Not Live

Two tempting-but-wrong approaches, and why this skill avoids both:

- **Live random switching** cuts away from whatever's actually happening with no regard for whether that moment matters -- it can cut to a reaction shot mid-click, or away from a reaction shot that was the whole point.
- **A live "director" (human or AI) making switch decisions in real time** has the same core problem if they can't actually see the moment happen with enough lead time to judge it well.

What works instead: analyze the **recorded** footage after the fact, where the full timeline is available, and make cut decisions from real signals (motion, speech) rather than guessing blind.

## Prerequisites

**Simultaneous, separately-recorded tracks.** This tool needs each source (screen, webcam, etc.) recorded to its own file, all covering the same real time window. The clean way to get that in OBS is the third-party **"Source Record" filter plugin** (by exeldro) applied per-source -- it was NOT available in the environment this skill was built in (`CreateSourceFilter` with kind `source_record_filter` returned "filter kind is not supported... check that any necessary plugins are loaded"). Until that plugin is installed, a manual workaround is to record each source solo (toggle scene item visibility, record, repeat) -- this validates the analysis logic but does **not** produce genuinely simultaneous tracks, so the resulting cut list won't reflect a real edit decision (see the Known Limitations section).

**Python packages**: `opencv-python` (`cv2`), `numpy`, `imageio-ffmpeg` (bundles a real ffmpeg binary -- no separate system ffmpeg install required).

**Audio matters.** If a reaction/webcam track's audio is meant to represent real speech, make sure the actual microphone (not the webcam's own weak/absent mic) is what's feeding that track's audio -- in an OBS setup, that usually means a dedicated `wasapi_input_capture` "Mic/Aux"-style source needs to be a scene item in whatever scene is being recorded, not just present somewhere in the app. A flat, near-silent audio track (checked via `analyze_activity.py`) is a sign this isn't wired up correctly, not a sign the room was simply quiet -- verify before trusting the reaction-detection results.

## The Three Scripts

Located in `scripts/`, meant to be run in sequence:

### 1. `analyze_activity.py` -- inspect raw signal before trusting anything

```
python analyze_activity.py video1.mp4 video2.mp4 ... [--sample-fps 2.0] [--out report.json]
```

Prints per-track motion (mean grayscale frame-diff, sampled at `--sample-fps`) and audio RMS summaries. **Always run this first** and sanity-check the numbers before running `decide_cuts.py` -- if a track that should have real signal (e.g. an active screen recording, or a person talking) comes back with a suspiciously flat/tiny range, something's wrong upstream (wrong file, audio not routed, wrong source), not with this script's math.

### 2. `decide_cuts.py` -- turn activity into a cut-decision list

```
python decide_cuts.py --track "name1=path1=role1" --track "name2=path2=role2" ... \
  --min-shot-seconds 2.0 --reaction-audio-threshold 0.01 --out cutlist.json
```

- `role` is either `screen` (scored by visual motion) or `reaction` (scored by detected speech, not motion -- a person fidgeting isn't the same signal as a person actively reacting).
- **Screen tracks are normalized jointly**, not independently -- comparing relative motion across screen tracks is meaningful because they're the same modality (pixel-diff units).
- **Reaction tracks use an absolute threshold on raw (non-normalized) audio RMS**, not a normalized score. This is the fix for the core bug found during this skill's own build: independently min-max-normalizing a near-silent audio track still rescales it to span the full 0-1 range, making pure room noise falsely outcompete real motion on another track after normalization. Never compare motion and audio by normalizing each separately and taking an argmax across modalities -- normalize within a modality, threshold across modalities.
- `--min-shot-seconds` prevents rapid flip-flopping: a new candidate track must sustain for at least this long before a cut is actually made to it.

### 3. `render_cut.py` -- produce an actual rough-cut video

```
python render_cut.py cutlist.json --out rough_cut.mp4
```

Trims each segment from its source file and concatenates them via ffmpeg. Hard cuts only -- no crossfades, no audio ducking/mixing between simultaneous tracks. This is meant to give an editor (human or a further automated pass) a usable starting timeline, not a publish-ready video.

## Known Limitations

- **Built and smoke-tested against sequentially-recorded clips, not simultaneous ones** (see Prerequisites) -- the pipeline runs correctly end-to-end, but a cut list produced from non-simultaneous input doesn't represent a real edit decision. Re-validate against genuinely simultaneous tracks once the Source Record plugin (or equivalent) is available.
- **`--reaction-audio-threshold` default (0.01) is an unvalidated placeholder**, not a calibrated speech-detection threshold -- it was never tested against real speech audio, since the test webcam clip's mic wasn't actually wired into the recording (see Prerequisites). Recalibrate once real narration audio is available: run `analyze_activity.py` on a clip with known speech and known silence, and set the threshold between the two observed ranges.
- **Hard cuts only** -- no crossfade/audio-mix support in `render_cut.py` yet.
- **No cursor/zoom-punch treatment** -- per research done for this project, raw full-screen capture cut into a vertical frame likely still needs a zoom/pan pass for cursor and small-text legibility; this skill decides *which track*, not *how to reframe it*. That's a separate, not-yet-built step.
