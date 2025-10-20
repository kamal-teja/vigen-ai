# # app/tools/edit_tools.py
# import os
# import shlex
# import subprocess
# import tempfile
# from pathlib import Path
# from typing import List, Tuple, Optional
# import json

# import boto3
# import platform

# def _ffmpeg_quote(path: str) -> str:
#     """Cross-platform quoting for FFmpeg paths."""
#     if platform.system() == "Windows":
#         # Always use double quotes for FFmpeg on Windows
#         return f'"{path}"'
#     return shlex.quote(path)

# # ---------- simple S3 helpers ----------
# _s3 = boto3.client("s3")

# def _download_s3(bucket: str, key: str, dst_dir: Path) -> Path:
#     dst = dst_dir / Path(key).name
#     dst.parent.mkdir(parents=True, exist_ok=True)
#     _s3.download_file(bucket, key, str(dst))
#     return dst

# def _upload_s3(bucket: str, src: Path, key: str) -> Tuple[str, str]:
#     key = key.strip("/")
#     _s3.upload_file(str(src), bucket, key)
#     return (http_url(bucket, key), key)

# def http_url(bucket: str, key: str) -> str:
#     return f"https://{bucket}.s3.amazonaws.com/{key}"

# # ---------- ffmpeg runner ----------
# def _run_ffmpeg(cmd: str) -> None:
#     print(f"\n🚀 ffmpeg: {cmd}")
#     proc = subprocess.run(cmd, shell=True)
#     if proc.returncode != 0:
#         raise RuntimeError(f"❌ FFmpeg failed: {cmd}")

# # ---------- public API (kept same names) ----------

# def mux_audio_over_video(
#     bucket: str,
#     video_key: str,
#     audio_key: str,
#     out_prefix: str,
#     scene_seconds: Optional[int] = None,  # ignored for FFmpeg but kept for compatibility
# ) -> Tuple[str, Optional[str]]:
#     """
#     Merge one video (.mp4) + one audio (.mp3/.m4a) -> MP4 with synced audio.
#     If out_prefix ends with "final video", write "final_video.mp4" there.
#     Otherwise write "<out_prefix>/scenes/<video_basename>_final.mp4".
#     Returns (http_url, None).
#     """
#     out_prefix = out_prefix.strip("/")
#     base_video = Path(video_key).stem

#     if Path(out_prefix).name.lower().replace("_", " ") == "final video":
#         out_key = f"{out_prefix}/final_video.mp4"
#     else:
#         out_key = f"{out_prefix}/scenes/{base_video}_final.mp4"

#     with tempfile.TemporaryDirectory() as td:
#         tdir = Path(td)
#         vpath = _download_s3(bucket, video_key, tdir)
#         apath = _download_s3(bucket, audio_key, tdir)
#         out_local = tdir / Path(out_key).name

#         # scale to 1280x720, 30fps; AAC audio @48k. -shortest keeps audio from trailing past video
#         cmd = (
#             f'ffmpeg -y -i {_ffmpeg_quote(str(vpath))} -i {_ffmpeg_quote(str(apath))} '
#             f'-vf "scale=1280:720,fps=30" '
#             f'-c:v libx264 -preset medium -crf 20 '
#             f'-c:a aac -b:a 192k -ar 48000 -shortest {_ffmpeg_quote(str(out_local))}'
#         )
#         _run_ffmpeg(cmd)

#         url, key = _upload_s3(bucket, out_local, out_key)
#         return url, None


# def concat_videos_to_single(
#     bucket: str,
#     video_keys: List[str],
#     out_prefix: str,
#     wait: bool = True,
# ) -> Tuple[str, str, Optional[str]]:
#     """
#     Concatenate multiple MP4 scene clips into one MP4 video-only (no audio).
#     Normalizes clips first to ensure same resolution/fps/codec, then concatenates.
#     Returns (http_url, out_key, None).
#     """
#     import tempfile
#     from pathlib import Path

#     out_prefix = out_prefix.strip("/")
#     out_key = f"{out_prefix}/combined_video.mp4"

#     with tempfile.TemporaryDirectory() as td:
#         tdir = Path(td)
#         local_videos = [_download_s3(bucket, k, tdir) for k in video_keys]
#         normalized_files = []

#         # Step 1: normalize each video
#         for i, lv in enumerate(local_videos, start=1):
#             norm_path = tdir / f"norm_{i}.mp4"
#             cmd = (
#                 f'ffmpeg -y -i {_ffmpeg_quote(str(lv))} '
#                 f'-vf "scale=1280:720,fps=30,format=yuv420p" '
#                 f'-c:v libx264 -preset fast -crf 20 -an {_ffmpeg_quote(str(norm_path))}'
#             )
#             _run_ffmpeg(cmd)
#             normalized_files.append(norm_path)

#         # Step 2: create concat list
#         list_file = tdir / "concat_list.txt"
#         with list_file.open("w") as f:
#             for nf in normalized_files:
#                 f.write(f"file '{nf.resolve()}'\n")

#         # Step 3: concatenate without re-encoding
#         out_local = tdir / "combined_video.mp4"
#         cmd = (
#             f'ffmpeg -y -f concat -safe 0 -i {_ffmpeg_quote(str(list_file))} '
#             f'-c copy {_ffmpeg_quote(str(out_local))}'
#         )
#         _run_ffmpeg(cmd)

#         # Step 4: upload to S3
#         url, key = _upload_s3(bucket, out_local, out_key)
#         return url, key, None



# def concat_audios_to_single(
#     bucket: str,
#     audio_keys: List[str],
#     out_prefix: str,
#     wait: bool = True,
# ) -> Tuple[str, str, Optional[str]]:
#     """
#     Concatenate multiple audio files to a single AAC (m4a) track with consistent
#     sample rate and a 1.5-second silence between clips.
#     """
#     import tempfile
#     from pathlib import Path

#     out_prefix = out_prefix.strip("/")
#     out_key = f"{out_prefix}/combined_audio.m4a"

#     with tempfile.TemporaryDirectory() as td:
#         tdir = Path(td)
#         local_audios = [_download_s3(bucket, k, tdir) for k in audio_keys]
#         normalized_audios = []

#         # Normalize all audios
#         for i, la in enumerate(local_audios, start=1):
#             norm_path = tdir / f"norm_{i}.m4a"
#             cmd = (
#                 f'ffmpeg -y -i {_ffmpeg_quote(str(la))} '
#                 f'-ar 48000 -ac 2 -c:a aac -b:a 192k {_ffmpeg_quote(str(norm_path))}'
#             )
#             _run_ffmpeg(cmd)
#             normalized_audios.append(norm_path)

#         # Add 1.5s silence after each clip except the last
#         out_local = tdir / "combined_audio.m4a"
#         inputs = " ".join([f'-i {_ffmpeg_quote(str(p))}' for p in normalized_audios])
#         n = len(normalized_audios)
#         streams = "".join([f"[{i}:a]adelay=0|0[a{i}];" for i in range(n)])

#         # generate silences and append between clips
#         filter_complex = ""
#         for i in range(n):
#             filter_complex += f"[{i}:a]"
#             if i < n - 1:
#                 filter_complex += f"anullsrc=r=48000:cl=stereo:d=1.5[a_sil{i}];"
#         filter_complex = "".join([f"[{i}:a]" for i in range(n)])  # simpler method

#         # Easier and reliable way:
#         concat_inputs = " ".join([f'-i {_ffmpeg_quote(str(p))}' for p in normalized_audios])
#         list_file = tdir / "audio_list.txt"
#         with list_file.open("w") as f:
#             for i, p in enumerate(normalized_audios):
#                 f.write(f"file '{p.resolve()}'\n")
#                 if i < len(normalized_audios) - 1:
#                     # Add 1.5 seconds of silence as a silent clip between audios
#                     silence = tdir / f"silence_{i}.m4a"
#                     os.system(
#                         f'ffmpeg -f lavfi -i anullsrc=r=48000:cl=stereo:d=1.5 '
#                         f'-c:a aac -b:a 192k -ar 48000 {silence}'
#                     )
#                     f.write(f"file '{silence.resolve()}'\n")

#         cmd = (
#             f'ffmpeg -y -f concat -safe 0 -i {_ffmpeg_quote(str(list_file))} '
#             f'-c:a aac -b:a 192k -ar 48000 {_ffmpeg_quote(str(out_local))}'
#         )
#         _run_ffmpeg(cmd)

#         url, key = _upload_s3(bucket, out_local, out_key)
#         return url, key, None




# def mux_final_audio_video(
#     bucket: str,
#     combined_video_key: str,
#     combined_audio_key: str,
#     out_prefix: str,
# ) -> Tuple[str, str]:
#     """
#     Mux the combined video and audio into a single final MP4.
#     Ensures clean A/V sync, proper metadata, and streaming compatibility.
#     Returns (http_url, out_key).
#     """
#     import tempfile
#     from pathlib import Path

#     out_prefix = out_prefix.strip("/")
#     out_key = f"{out_prefix}/final_video.mp4"

#     with tempfile.TemporaryDirectory() as td:
#         tdir = Path(td)
#         vpath = _download_s3(bucket, combined_video_key, tdir)
#         apath = _download_s3(bucket, combined_audio_key, tdir)
#         out_local = tdir / "final_video.mp4"

#         # ✅ Proper mux command
#         cmd = (
#             f'ffmpeg -y -i {_ffmpeg_quote(str(vpath))} -i {_ffmpeg_quote(str(apath))} '
#             f'-c:v copy -c:a aac -b:a 192k -ar 48000 '
#             f'-movflags +faststart -avoid_negative_ts make_zero '
#             f'{_ffmpeg_quote(str(out_local))}'
#         )
#         _run_ffmpeg(cmd)

#         # Upload to S3
#         url, key = _upload_s3(bucket, out_local, out_key)
#         return url, key


# def _run(cmd: list, fail_msg: str):
#     p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
#     if p.returncode != 0:
#         raise RuntimeError(f"{fail_msg}:\n{' '.join(cmd)}\n--- stderr ---\n{p.stderr}")
#     return p

# def _ffprobe_duration(path: Path) -> float:
#     """Return media duration in seconds (float)."""
#     p = subprocess.run(
#         ["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",str(path)],
#         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
#     )
#     if p.returncode != 0 or not p.stdout.strip():
#         return 0.0
#     try:
#         return float(p.stdout.strip())
#     except:
#         return 0.0

# def make_local_ad_video_match_audio(
#     image_path: str,
#     tagline_text: str,
#     output_dir: str = "ad_output",
#     *,
#     final_name: str = "final_ad.mp4",
#     min_duration_sec: float = 3.0,   # minimum video length you want
#     fps: int = 30,
#     width: int = 1280,
#     height: int = 720,
#     voice_id: str = "Raveena",
#     polly_format: str = "mp3",
#     polly_region: str = "ap-south-1",
#     gain_db: float = 3.0,
#     tail_mode: str = "hold",         # "hold" = keep image; "black" = show black beyond min_duration
# ) -> dict:
#     """
#     Creates TTS first, measures its duration, then makes video to match audio (>= min_duration_sec).
#     tail_mode:
#       - "hold": still image for the full (matched) duration.
#       - "black": keep image for min_duration_sec, then black frames for any extra tail.
#     """
#     # tools
#     for tool in ("ffmpeg","ffprobe"):
#         subprocess.run([tool, "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

#     img = Path(image_path).expanduser().resolve()
#     if not img.exists():
#         raise FileNotFoundError(f"Image not found: {img}")

#     out_dir = Path(output_dir).expanduser().resolve()
#     out_dir.mkdir(parents=True, exist_ok=True)

#     # paths
#     video_from_image = out_dir / "scene.mp4"
#     tts_original     = out_dir / f"tts_original.{polly_format}"
#     tts_wav_48k      = out_dir / "tts_48k.wav"
#     final_video      = out_dir / final_name

#     # 1) Polly TTS -> original compressed (mp3/ogg), then clean 48k stereo WAV
#     polly = boto3.client("polly", region_name=polly_region)
#     resp = polly.synthesize_speech(Text=tagline_text, OutputFormat=polly_format, VoiceId=voice_id)
#     if "AudioStream" not in resp:
#         raise RuntimeError("Polly returned no audio. Check creds/region/voice.")
#     with open(tts_original, "wb") as f:
#         f.write(resp["AudioStream"].read())

#     _run([
#         "ffmpeg","-y",
#         "-i",str(tts_original),
#         "-af", f"aformat=sample_fmts=s16:sample_rates=48000:channel_layouts=stereo,volume={gain_db}dB",
#         str(tts_wav_48k)
#     ], "FFmpeg normalize TTS failed")

#     # 2) Measure audio duration
#     audio_dur = _ffprobe_duration(tts_wav_48k)
#     # Fallback if ffprobe failed
#     if audio_dur <= 0:
#         audio_dur = float(min_duration_sec)
#     # Final duration is the larger of min_duration and audio duration
#     final_dur = max(float(min_duration_sec), float(audio_dur))

#     # 3) Build video to match final_dur
#     if tail_mode == "black" and final_dur > min_duration_sec:
#         # Build two segments: image for min_duration, black for (final_dur - min_duration), then concat
#         img_seg = out_dir / "img_seg.mp4"
#         blk_seg = out_dir / "blk_seg.mp4"
#         concat_list = out_dir / "concat_list.txt"

#         # image segment (min_duration)
#         _run([
#             "ffmpeg","-y",
#             "-loop","1","-framerate",str(fps),
#             "-i",str(img),
#             "-t",f"{min_duration_sec:.3f}",
#             "-vf",(
#                 f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
#                 f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,fps={fps}"
#             ),
#             "-c:v","libx264","-preset","medium","-crf","20",
#             "-pix_fmt","yuv420p","-movflags","+faststart",
#             str(img_seg)
#         ], "FFmpeg image segment failed")

#         # black tail (final_dur - min_duration)
#         tail_len = final_dur - min_duration_sec
#         _run([
#             "ffmpeg","-y",
#             "-f","lavfi","-i",f"color=color=black:size={width}x{height}:rate={fps}:duration={tail_len:.3f}",
#             "-c:v","libx264","-preset","medium","-crf","20",
#             "-pix_fmt","yuv420p","-movflags","+faststart",
#             str(blk_seg)
#         ], "FFmpeg black segment failed")

#         # concat
#         with concat_list.open("w") as f:
#             f.write(f"file '{img_seg}'\n")
#             f.write(f"file '{blk_seg}'\n")

#         _run([
#             "ffmpeg","-y",
#             "-f","concat","-safe","0",
#             "-i",str(concat_list),
#             "-c","copy",
#             str(video_from_image)
#         ], "FFmpeg concat segments failed")

#     else:
#         # hold image across the whole final duration
#         _run([
#             "ffmpeg","-y",
#             "-loop","1","-framerate",str(fps),
#             "-i",str(img),
#             "-t",f"{final_dur:.3f}",
#             "-vf",(
#                 f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
#                 f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,fps={fps}"
#             ),
#             "-c:v","libx264","-preset","medium","-crf","20",
#             "-pix_fmt","yuv420p","-movflags","+faststart",
#             str(video_from_image)
#         ], "FFmpeg image->video failed")

#     # 4) Merge (no trim; reset PTS to start; durations now aligned)
#     _run([
#         "ffmpeg","-y",
#         "-i",str(video_from_image),
#         "-i",str(tts_wav_48k),
#         "-filter_complex","[1:a]asetpts=PTS-STARTPTS, aformat=sample_fmts=s16:sample_rates=48000:channel_layouts=stereo[aout]",
#         "-map","0:v:0","-map","[aout]",
#         "-c:v","copy",
#         "-c:a","aac","-b:a","192k",
#         "-movflags","+faststart",
#         str(final_video)
#     ], "FFmpeg mux failed")

#     # quick probe (optional)
#     probe_a = subprocess.run(
#         ["ffprobe","-v","error","-show_streams","-select_streams","a","-of","json",str(final_video)],
#         stdout=subprocess.PIPE, text=True
#     ).stdout

#     return {
#         "tts_original": str(tts_original),
#         "tts_wav_48k": str(tts_wav_48k),
#         "audio_duration_sec": round(audio_dur, 3),
#         "video_built_duration_sec": round(final_dur, 3),
#         "video_from_image": str(video_from_image),
#         "final_video": str(final_video),
#         "final_audio_streams": json.loads(probe_a) if probe_a else {}
#     }


# paths = make_local_ad_video_match_audio(
#         image_path="/Users/fl_lpt-435/Downloads/AWS_hackaton/biofit_2310-_2.jpg",
#         tagline_text="Experience clarity and style—introducing the new Aurora sunglasses.",
#         output_dir="ad_output",
#         final_name="final_ad.mp4",
#         min_duration_sec=3.0,
#         fps=30,
#         width=1280,
#         height=720,
#         voice_id="Raveena",
#         polly_format="mp3",
#         polly_region="ap-south-1",
#         gain_db=3.0,
#         tail_mode="hold",  # or "black"
#     )



# app/tools/edit_tools.py
import os
import shlex
import subprocess
import tempfile
from pathlib import Path
from typing import List, Tuple, Optional
import boto3
import platform

# ---------- Cross-platform path quoting ----------
def _ffmpeg_quote(path: str) -> str:
    """Cross-platform quoting for FFmpeg paths."""
    if platform.system() == "Windows":
        return f'"{path}"'
    return shlex.quote(path)


# ---------- Simple S3 helpers ----------
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


# ---------- FFmpeg runner ----------
def _run_ffmpeg(cmd: str) -> None:
    """Execute an ffmpeg shell command and surface stderr on failure."""
    print(f"\n🚀 ffmpeg: {cmd}")
    proc = subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if proc.returncode != 0:
        stderr = proc.stderr.strip()
        stdout = proc.stdout.strip()
        raise RuntimeError(
            "❌ FFmpeg failed: "
            f"{cmd}\n--- stdout ---\n{stdout}\n--- stderr ---\n{stderr}"
        )


# ---------- Public API ----------
def mux_audio_over_video(
    bucket: str,
    video_key: str,
    audio_key: str,
    out_prefix: str,
    scene_seconds: Optional[int] = None,
) -> Tuple[str, Optional[str]]:
    """Merge one video (.mp4) + one audio (.mp3/.m4a) -> MP4 with synced audio."""
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

        cmd = (
            f'ffmpeg -y -i {_ffmpeg_quote(str(vpath))} -i {_ffmpeg_quote(str(apath))} '
            f'-vf "scale=1280:720,fps=30" '
            f'-c:v libx264 -preset medium -crf 20 '
            f'-c:a aac -b:a 192k -ar 48000 -shortest {_ffmpeg_quote(str(out_local))}'
        )
        _run_ffmpeg(cmd)

        url, key = _upload_s3(bucket, out_local, out_key)
        return url, None


def concat_videos_to_single(
    bucket: str,
    video_keys: List[str],
    out_prefix: str,
    wait: bool = True,
) -> Tuple[str, str, Optional[str]]:
    """Concatenate multiple MP4 clips into one MP4 video-only file."""
    out_prefix = out_prefix.strip("/")
    out_key = f"{out_prefix}/combined_video.mp4"

    with tempfile.TemporaryDirectory() as td:
        tdir = Path(td)
        local_videos = [_download_s3(bucket, k, tdir) for k in video_keys]
        normalized_files = []

        # Normalize videos
        for i, lv in enumerate(local_videos, start=1):
            norm_path = tdir / f"norm_{i}.mp4"
            cmd = (
                f'ffmpeg -y -i {_ffmpeg_quote(str(lv))} '
                f'-vf "scale=1280:720,fps=30,format=yuv420p" '
                f'-c:v libx264 -preset fast -crf 20 -an {_ffmpeg_quote(str(norm_path))}'
            )
            _run_ffmpeg(cmd)
            normalized_files.append(norm_path)

        # Concat list file
        list_file = tdir / "concat_list.txt"
        with list_file.open("w") as f:
            for nf in normalized_files:
                f.write(f"file '{nf.resolve()}'\n")

        out_local = tdir / "combined_video.mp4"
        cmd = (
            f'ffmpeg -y -f concat -safe 0 -i {_ffmpeg_quote(str(list_file))} '
            f'-c copy {_ffmpeg_quote(str(out_local))}'
        )
        _run_ffmpeg(cmd)

        url, key = _upload_s3(bucket, out_local, out_key)
        return url, key, None


def concat_audios_to_single(
    bucket: str,
    audio_keys: List[str],
    out_prefix: str,
    wait: bool = True,
) -> Tuple[str, str, Optional[str]]:
    """Concatenate multiple audio files into a single AAC (m4a) track."""
    out_prefix = out_prefix.strip("/")
    out_key = f"{out_prefix}/combined_audio.m4a"

    with tempfile.TemporaryDirectory() as td:
        tdir = Path(td)
        local_audios = [_download_s3(bucket, k, tdir) for k in audio_keys]
        normalized_audios = []

        # Normalize audios
        for i, la in enumerate(local_audios, start=1):
            norm_path = tdir / f"norm_{i}.m4a"
            cmd = (
                f'ffmpeg -y -i {_ffmpeg_quote(str(la))} '
                f'-ar 48000 -ac 2 -c:a aac -b:a 192k {_ffmpeg_quote(str(norm_path))}'
            )
            _run_ffmpeg(cmd)
            normalized_audios.append(norm_path)

        # Add 1.5s silence between clips
        list_file = tdir / "audio_list.txt"
        with list_file.open("w") as f:
            for i, p in enumerate(normalized_audios):
                f.write(f"file '{p.resolve()}'\n")
                if i < len(normalized_audios) - 1:
                    silence = tdir / f"silence_{i}.m4a"
                    os.system(
                        f'ffmpeg -f lavfi -i anullsrc=r=48000:cl=stereo:d=1.5 '
                        f'-c:a aac -b:a 192k -ar 48000 {silence}'
                    )
                    f.write(f"file '{silence.resolve()}'\n")

        out_local = tdir / "combined_audio.m4a"
        cmd = (
            f'ffmpeg -y -f concat -safe 0 -i {_ffmpeg_quote(str(list_file))} '
            f'-c:a aac -b:a 192k -ar 48000 {_ffmpeg_quote(str(out_local))}'
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
    """Mux the combined video and audio into a single final MP4."""
    out_prefix = out_prefix.strip("/")
    out_key = f"{out_prefix}/final_video.mp4"

    with tempfile.TemporaryDirectory() as td:
        tdir = Path(td)
        vpath = _download_s3(bucket, combined_video_key, tdir)
        apath = _download_s3(bucket, combined_audio_key, tdir)
        out_local = tdir / "final_video.mp4"

        # ✅ Proper mux command
        cmd = (
            f'ffmpeg -y -i {_ffmpeg_quote(str(vpath))} -i {_ffmpeg_quote(str(apath))} '
            f'-c:v copy -c:a aac -b:a 192k -ar 48000 '
            f'-movflags +faststart -avoid_negative_ts make_zero '
            f'{_ffmpeg_quote(str(out_local))}'
        )
        _run_ffmpeg(cmd)

        url, key = _upload_s3(bucket, out_local, out_key)
        return url, key
