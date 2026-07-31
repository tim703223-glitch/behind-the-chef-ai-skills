"""
Render an actual rough-cut video from a cut-decision list produced by
decide_cuts.py: trims the chosen segment out of each track's source file
and concatenates them in order into a single output video via ffmpeg.

This is a rough cut, not a final edit -- hard cuts only, no crossfades,
no audio ducking/mixing between tracks. It's meant to give an editor a
usable starting timeline, not a publish-ready video.
"""

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path


def get_ffmpeg_exe() -> str:
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def render_cut(cutlist_path: str, output_path: str) -> None:
    with open(cutlist_path) as f:
        cutlist = json.load(f)

    tracks = cutlist["tracks"]
    segments = cutlist["segments"]
    if not segments:
        raise ValueError("Cut list has no segments to render")

    ffmpeg = get_ffmpeg_exe()
    tmp_dir = Path(tempfile.mkdtemp(prefix="smart_cut_"))
    segment_files = []

    try:
        for i, seg in enumerate(segments):
            src = tracks[seg["track"]]
            duration = seg["end"] - seg["start"]
            out_seg = tmp_dir / f"seg_{i:04d}.mp4"
            cmd = [
                ffmpeg, "-y",
                "-ss", str(seg["start"]),
                "-i", src,
                "-t", str(duration),
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                "-c:a", "aac",
                "-avoid_negative_ts", "make_zero",
                str(out_seg),
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0 or not out_seg.exists():
                raise RuntimeError(f"ffmpeg failed on segment {i} ({seg}): {result.stderr[-2000:]}")
            segment_files.append(out_seg)
            print(f"  trimmed segment {i}: {seg['start']:.2f}-{seg['end']:.2f}s from '{seg['track']}'")

        concat_list_path = tmp_dir / "concat_list.txt"
        with open(concat_list_path, "w") as f:
            for seg_file in segment_files:
                # ffmpeg concat demuxer requires forward slashes / escaped paths
                safe_path = str(seg_file).replace("\\", "/")
                f.write(f"file '{safe_path}'\n")

        cmd = [
            ffmpeg, "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_list_path),
            "-c", "copy",
            output_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0 or not Path(output_path).exists():
            raise RuntimeError(f"ffmpeg concat failed: {result.stderr[-2000:]}")

        print(f"Rendered {len(segments)} segments -> {output_path}")
    finally:
        for f in segment_files:
            f.unlink(missing_ok=True)
        concat_list = tmp_dir / "concat_list.txt"
        concat_list.unlink(missing_ok=True)
        tmp_dir.rmdir()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cutlist", help="Cut-list JSON from decide_cuts.py")
    parser.add_argument("--out", required=True, help="Output rough-cut video path")
    args = parser.parse_args()
    render_cut(args.cutlist, args.out)


if __name__ == "__main__":
    sys.exit(main())
