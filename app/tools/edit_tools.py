# app/tools/edit_tools.py
import os
import shlex
import subprocess
import tempfile
from pathlib import Path
from typing import List, Tuple, Optional

import boto3

# ---------- simple S3 helpers ----------
_s3 = boto3.client("s3")

def _download_s3(bucket: str, key: str, dst_dir: Path) -> Path:
    dst = dst_dir / Path(key).name
    dst.parent.mkdir(parents=True, exist_ok=True)
    _s3.download_file(bucket, key, str(dst))
    return dst

def _upload_s3(bucket: str, src: Path, key: str) -> Tuple[str, str]:
    key = key.strip("/")
    _s3.upload_file(str(src), bucket, key)
    return (http_url(bucket, key), key)

def http_url(bucket: str, key: str) -> str:
    return f"https://{bucket}.s3.amazonaws.com/{key}"

# ---------- ffmpeg runner ----------
def _run_ffmpeg(cmd: str) -> None:
    print(f"\n🚀 ffmpeg: {cmd}")
    proc = subprocess.run(cmd, shell=True)
    if proc.returncode != 0:
        raise RuntimeError(f"❌ FFmpeg failed: {cmd}")

# ---------- public API (kept same names) ----------

def mux_audio_over_video(
    bucket: str,
    video_key: str,
    audio_key: str,
    out_prefix: str,
    scene_seconds: Optional[int] = None,  # ignored for FFmpeg but kept for compatibility
) -> Tuple[str, Optional[str]]:
    """
    Merge one video (.mp4) + one audio (.mp3/.m4a) -> MP4 with synced audio.
    If out_prefix ends with "final video", write "final_video.mp4" there.
    Otherwise write "<out_prefix>/scenes/<video_basename>_final.mp4".
    Returns (http_url, None).
    """
    out_prefix = out_prefix.strip("/")
    base_video = Path(video_key).stem

    if Path(out_prefix).name.lower().replace("_", " ") == "final video":
        out_key = f"{out_prefix}/final_video.mp4"
    else:
        out_key = f"{out_prefix}/scenes/{base_video}_final.mp4"

    with tempfile.TemporaryDirectory() as td:
        tdir = Path(td)
        vpath = _download_s3(bucket, video_key, tdir)
        apath = _download_s3(bucket, audio_key, tdir)
        out_local = tdir / Path(out_key).name

        # scale to 1280x720, 30fps; AAC audio @48k. -shortest keeps audio from trailing past video
        cmd = (
            f'ffmpeg -y -i {shlex.quote(str(vpath))} -i {shlex.quote(str(apath))} '
            f'-vf "scale=1280:720,fps=30" '
            f'-c:v libx264 -preset medium -crf 20 '
            f'-c:a aac -b:a 192k -ar 48000 -shortest {shlex.quote(str(out_local))}'
        )
        _run_ffmpeg(cmd)

        url, key = _upload_s3(bucket, out_local, out_key)
        return url, None


def concat_videos_to_single(
    bucket: str,
    video_keys: List[str],
    out_prefix: str,
    wait: bool = True,  # kept for compatibility; no async job with ffmpeg
) -> Tuple[str, str, Optional[str]]:
    """
    Concatenate multiple MP4 scene clips into one MP4 *video-only* (no audio).
    Re-encodes to ensure uniform parameters.
    Returns (http_url, out_key, None).
    """
    out_prefix = out_prefix.strip("/")
    out_key = f"{out_prefix}/combined_video.mp4"

    with tempfile.TemporaryDirectory() as td:
        tdir = Path(td)
        # download all scenes
        local_videos = [ _download_s3(bucket, k, tdir) for k in video_keys ]

        list_file = tdir / "concat_list.txt"
        with list_file.open("w") as f:
            for lp in local_videos:
                f.write(f"file '{lp.resolve()}'\n")

        out_local = tdir / "combined_video.mp4"

        # Re-encode to harmonize all parameters; drop audio (-an)
        cmd = (
            f'ffmpeg -y -f concat -safe 0 -i {shlex.quote(str(list_file))} '
            f'-vf "scale=1280:720,fps=30" '
            f'-c:v libx264 -preset medium -crf 20 -an {shlex.quote(str(out_local))}'
        )
        _run_ffmpeg(cmd)

        url, key = _upload_s3(bucket, out_local, out_key)
        return url, key, None


def concat_audios_to_single(
    bucket: str,
    audio_keys: List[str],
    out_prefix: str,
    wait: bool = True,  # kept for compatibility
) -> Tuple[str, str, Optional[str]]:
    """
    Concatenate multiple audio files to a single AAC (m4a) with consistent SR/codec.
    Returns (http_url, out_key, None).
    """
    out_prefix = out_prefix.strip("/")
    out_key = f"{out_prefix}/combined_audio.m4a"

    with tempfile.TemporaryDirectory() as td:
        tdir = Path(td)
        local_audios = [ _download_s3(bucket, k, tdir) for k in audio_keys ]
        out_local = tdir / "combined_audio.m4a"

        # Build input list and filter_complex concat
        inputs = " ".join([f'-i {shlex.quote(str(p))}' for p in local_audios])
        n = len(local_audios)
        streams = "".join([f"[{i}:a]" for i in range(n)])
        cmd = (
            f'ffmpeg -y {inputs} '
            f'-filter_complex "{streams}concat=n={n}:v=0:a=1[a]" '
            f'-map "[a]" -c:a aac -b:a 192k -ar 48000 {shlex.quote(str(out_local))}'
        )
        _run_ffmpeg(cmd)

        url, key = _upload_s3(bucket, out_local, out_key)
        return url, key, None


def mux_final_audio_video(
    bucket: str,
    combined_video_key: str,
    combined_audio_key: str,
    out_prefix: str,
) -> Tuple[str, str]:
    """
    Final mux: combined_video.mp4 + combined_audio.m4a -> final_video.mp4
    Returns (http_url, out_key).
    """
    out_prefix = out_prefix.strip("/")
    out_key = f"{out_prefix}/final_video.mp4"

    with tempfile.TemporaryDirectory() as td:
        tdir = Path(td)
        vpath = _download_s3(bucket, combined_video_key, tdir)
        apath = _download_s3(bucket, combined_audio_key, tdir)
        out_local = tdir / "final_video.mp4"

        cmd = (
            f'ffmpeg -y -i {shlex.quote(str(vpath))} -i {shlex.quote(str(apath))} '
            f'-c:v copy -c:a aac -b:a 192k -ar 48000 -shortest {shlex.quote(str(out_local))}'
        )
        _run_ffmpeg(cmd)

        url, key = _upload_s3(bucket, out_local, out_key)
        return url, key
