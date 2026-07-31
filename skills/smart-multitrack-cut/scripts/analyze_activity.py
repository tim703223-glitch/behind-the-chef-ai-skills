"""
Analyze per-track "activity" over time for a set of separately-recorded video
sources (e.g. a screen capture and a webcam capture of the same session),
and decide which source should be on-screen at each moment.

Core idea: screen tracks (browser, terminal) are scored by visual motion
(more motion = more likely something worth showing is happening). The
webcam track is scored by speech/audio presence (talking = a reaction or
narration beat worth cutting to), not by its own motion, since a person
fidgeting isn't the same signal as a person actively reacting.

This does NOT require the tracks to be time-synced to the same real-world
moment to compute a per-track activity score -- that part works on any
video file independently. Producing a genuinely correct combined cut list
across multiple sources does require them to be simultaneous recordings
(e.g. via OBS's "Source Record" filter plugin, recording each source to
its own file at the same time) -- see the skill's SKILL.md for that setup.
"""

import argparse
import json
import subprocess
import sys
import wave
from pathlib import Path

import cv2
import numpy as np


def get_ffmpeg_exe() -> str:
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def compute_motion_series(video_path: str, sample_fps: float = 2.0) -> list[tuple[float, float]]:
    """Sample frames at sample_fps and return (timestamp, motion_score) pairs.

    motion_score is the mean absolute grayscale pixel difference between
    consecutive sampled frames, normalized to roughly 0-1 by dividing by 255.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    native_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / native_fps if native_fps else 0.0

    step = max(1, round(native_fps / sample_fps))
    series: list[tuple[float, float]] = []
    prev_gray = None
    frame_idx = 0

    while True:
        ok = cap.grab()
        if not ok:
            break
        if frame_idx % step == 0:
            ok, frame = cap.retrieve()
            if not ok:
                break
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, (320, 180))  # downsample, motion detection doesn't need full res
            timestamp = frame_idx / native_fps
            if prev_gray is not None:
                diff = cv2.absdiff(gray, prev_gray)
                score = float(np.mean(diff)) / 255.0
                series.append((timestamp, score))
            prev_gray = gray
        frame_idx += 1

    cap.release()
    return series


def compute_audio_rms_series(video_path: str, sample_fps: float = 2.0) -> list[tuple[float, float]]:
    """Extract mono 16kHz PCM audio via ffmpeg and return (timestamp, rms) pairs,
    normalized roughly 0-1. Returns an empty list if the file has no audio stream.
    """
    ffmpeg = get_ffmpeg_exe()
    with_tmp = Path(video_path).with_suffix(".tmp_audio.wav")
    cmd = [ffmpeg, "-y", "-i", video_path, "-vn", "-ac", "1", "-ar", "16000", "-f", "wav", str(with_tmp)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if not with_tmp.exists():
        return []

    try:
        with wave.open(str(with_tmp), "rb") as wf:
            n_frames = wf.getnframes()
            sample_rate = wf.getframerate()
            raw = wf.readframes(n_frames)
        samples = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    finally:
        with_tmp.unlink(missing_ok=True)

    window = int(sample_rate / sample_fps)
    if window <= 0:
        return []

    series: list[tuple[float, float]] = []
    for start in range(0, len(samples), window):
        chunk = samples[start:start + window]
        if len(chunk) == 0:
            continue
        rms = float(np.sqrt(np.mean(chunk ** 2)))
        timestamp = start / sample_rate
        series.append((timestamp, rms))
    return series


def summarize(name: str, series: list[tuple[float, float]]) -> dict:
    if not series:
        return {"name": name, "count": 0, "mean": 0.0, "max": 0.0}
    values = [v for _, v in series]
    return {
        "name": name,
        "count": len(values),
        "mean": float(np.mean(values)),
        "max": float(np.max(values)),
        "p90": float(np.percentile(values, 90)),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("videos", nargs="+", help="Video files to analyze")
    parser.add_argument("--sample-fps", type=float, default=2.0)
    parser.add_argument("--out", help="Write full per-track series + summary to this JSON path")
    args = parser.parse_args()

    report = {}
    for video in args.videos:
        name = Path(video).stem
        motion = compute_motion_series(video, args.sample_fps)
        audio = compute_audio_rms_series(video, args.sample_fps)
        report[name] = {
            "path": video,
            "motion_summary": summarize(name, motion),
            "audio_summary": summarize(name, audio),
            "motion_series": motion,
            "audio_series": audio,
        }
        print(f"{name}: motion mean={report[name]['motion_summary']['mean']:.4f} "
              f"max={report[name]['motion_summary']['max']:.4f} | "
              f"audio mean={report[name]['audio_summary']['mean']:.4f} "
              f"max={report[name]['audio_summary']['max']:.4f}")

    if args.out:
        with open(args.out, "w") as f:
            json.dump(report, f, indent=2)
        print(f"Wrote {args.out}")


if __name__ == "__main__":
    sys.exit(main())
