"""
Turn per-track activity data (from analyze_activity.py) into a cut decision
list: a sequence of {start, end, track} segments describing which source
should be on screen at each point in time.

Scoring rule:
- "screen" role tracks (browser, terminal, any UI capture) are scored by
  visual motion -- more motion = more likely something worth showing.
- "reaction" role tracks (webcam) are scored by audio/speech presence, not
  motion -- a person fidgeting isn't the same signal as a person actively
  reacting or narrating.

To avoid rapid flip-flopping, a candidate track must have the highest score
for at least --min-shot-seconds of consecutive samples before a cut is
actually made to it; until then the previous track holds.

IMPORTANT CAVEAT: this only produces a meaningful combined cut list if all
input tracks are simultaneous recordings of the same session (e.g. via
OBS's "Source Record" filter plugin recording each source to its own file
at the same time). Feeding it separately-recorded, non-simultaneous clips
(as in this skill's own smoke test) will run the pipeline correctly but the
resulting cut list does not represent a real edit decision, since the
tracks were never actually happening at the same time.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

from analyze_activity import compute_motion_series, compute_audio_rms_series


def resample_to_grid(series: list[tuple[float, float]], grid: np.ndarray) -> np.ndarray:
    """Linearly interpolate a (timestamp, value) series onto a shared time grid."""
    if not series:
        return np.zeros_like(grid)
    times = np.array([t for t, _ in series])
    values = np.array([v for _, v in series])
    return np.interp(grid, times, values, left=values[0], right=values[-1])


def normalize(x: np.ndarray) -> np.ndarray:
    lo, hi = float(np.min(x)), float(np.max(x))
    if hi - lo < 1e-9:
        return np.zeros_like(x)
    return (x - lo) / (hi - lo)


def decide_cuts(
    tracks: dict[str, dict],
    roles: dict[str, str],
    sample_fps: float = 2.0,
    min_shot_seconds: float = 2.0,
    reaction_audio_threshold: float = 0.01,
) -> list[dict]:
    """tracks: {name: {"path": str}}. roles: {name: "screen" | "reaction"}.

    Screen tracks (motion) and reaction tracks (audio) are different physical
    units (pixel difference vs. waveform RMS) -- they must never be compared
    by independently normalizing each to 0-1 and taking an argmax, since that
    turns pure noise on a flat track into a "confident" 0-1 signal that can
    spuriously outscore real motion on another track. Instead:
      - screen tracks are normalized *jointly* (shared scale, since they're
        the same modality) and compete with each other on relative motion.
      - a reaction track only becomes an eligible winner at samples where its
        RAW (non-normalized) audio RMS exceeds reaction_audio_threshold --
        i.e. actual detected speech/sound, not just "loudest relative moment
        in an otherwise silent room." If no reaction track clears the
        threshold at a given sample, the winner is decided among screen
        tracks only.
    """
    durations = []
    raw_motion = {}
    raw_audio = {}
    for name, info in tracks.items():
        motion = compute_motion_series(info["path"], sample_fps)
        audio = compute_audio_rms_series(info["path"], sample_fps)
        raw_motion[name] = motion
        raw_audio[name] = audio
        if motion:
            durations.append(motion[-1][0])

    end_time = max(durations) if durations else 0.0
    grid = np.arange(0, end_time, 1.0 / sample_fps)
    if len(grid) == 0:
        return []

    names = list(tracks.keys())
    screen_names = [n for n in names if roles.get(n, "screen") != "reaction"]
    reaction_names = [n for n in names if roles.get(n, "screen") == "reaction"]

    # Screen tracks: resample raw motion onto the shared grid, then normalize
    # JOINTLY across all screen tracks together so their relative magnitudes
    # stay meaningful (a quiet-but-real click on one track shouldn't be
    # rescaled to look as significant as a big scroll on another).
    screen_raw = {n: resample_to_grid(raw_motion[n], grid) for n in screen_names}
    if screen_raw:
        combined = np.concatenate(list(screen_raw.values()))
        lo, hi = float(np.min(combined)), float(np.max(combined))
        span = hi - lo if hi - lo > 1e-9 else 1.0
        screen_scores = {n: (v - lo) / span for n, v in screen_raw.items()}
    else:
        screen_scores = {}

    # Reaction tracks: keep RAW audio RMS (not normalized) so it can be
    # compared against an absolute, physically-meaningful threshold.
    reaction_raw = {n: resample_to_grid(raw_audio[n], grid) for n in reaction_names}

    raw_choice = np.zeros(len(grid), dtype=int)
    for t in range(len(grid)):
        # Prefer a reaction track only if it actually clears the speech threshold
        best_reaction = None
        best_reaction_val = -1.0
        for n in reaction_names:
            val = reaction_raw[n][t]
            if val >= reaction_audio_threshold and val > best_reaction_val:
                best_reaction = n
                best_reaction_val = val
        if best_reaction is not None:
            raw_choice[t] = names.index(best_reaction)
            continue
        # Otherwise pick the screen track with the most relative motion
        if screen_scores:
            best_screen = max(screen_scores, key=lambda n: screen_scores[n][t])
            raw_choice[t] = names.index(best_screen)
        elif reaction_names:
            # No screen tracks at all -- fall back to the loudest reaction track anyway
            best_reaction = max(reaction_names, key=lambda n: reaction_raw[n][t])
            raw_choice[t] = names.index(best_reaction)

    min_samples = max(1, round(min_shot_seconds * sample_fps))
    final_choice = np.zeros_like(raw_choice)
    current = raw_choice[0]
    i = 0
    while i < len(raw_choice):
        if raw_choice[i] == current:
            final_choice[i] = current
            i += 1
            continue
        # a different candidate starts here -- see how long it sustains
        candidate = raw_choice[i]
        j = i
        while j < len(raw_choice) and raw_choice[j] == candidate:
            j += 1
        run_len = j - i
        if run_len >= min_samples:
            current = candidate
        final_choice[i:j] = current
        i = j

    # Merge consecutive identical choices into segments
    segments = []
    seg_start_idx = 0
    for i in range(1, len(final_choice) + 1):
        if i == len(final_choice) or final_choice[i] != final_choice[seg_start_idx]:
            segments.append({
                "start": round(float(grid[seg_start_idx]), 2),
                "end": round(float(grid[i]) if i < len(grid) else end_time, 2),
                "track": names[final_choice[seg_start_idx]],
            })
            seg_start_idx = i

    return segments


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--track", action="append", required=True,
                         help="name=path=role, role is 'screen' or 'reaction'. Repeatable.")
    parser.add_argument("--sample-fps", type=float, default=2.0)
    parser.add_argument("--min-shot-seconds", type=float, default=2.0)
    parser.add_argument("--reaction-audio-threshold", type=float, default=0.01,
                         help="Minimum raw audio RMS (0-1 float scale) for a reaction "
                              "track to be considered actually speaking/reacting, "
                              "rather than just ambient room noise.")
    parser.add_argument("--out", required=True, help="Output cut-list JSON path")
    args = parser.parse_args()

    tracks = {}
    roles = {}
    for spec in args.track:
        name, path, role = spec.split("=", 2)
        tracks[name] = {"path": path}
        roles[name] = role

    segments = decide_cuts(tracks, roles, args.sample_fps, args.min_shot_seconds,
                            args.reaction_audio_threshold)
    result = {"tracks": {n: t["path"] for n, t in tracks.items()}, "segments": segments}
    with open(args.out, "w") as f:
        json.dump(result, f, indent=2)

    print(f"{len(segments)} segments:")
    for seg in segments:
        print(f"  {seg['start']:6.2f}s - {seg['end']:6.2f}s -> {seg['track']}")
    print(f"Wrote {args.out}")


if __name__ == "__main__":
    sys.exit(main())
