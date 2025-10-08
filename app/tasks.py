# app/tasks.py
# ------------------------------------------------------------
# Changes:
# 1) Enforce short dialogue per scene (fits ~6s).
# 2) New assembly flow:
#    - concat all scene videos -> one video
#    - concat all scene audios -> one audio
#    - mux the two into final_video.mp4
# ------------------------------------------------------------

import os
import json
from uuid import uuid4
from typing import List

from crewai import Task, Crew

from .tools.script_tools import generate_script, save_script_s3
from .tools.evaluation_tools import evaluate_script
from .tools.image_tools import generate_scene_image
from .tools.video_tools import generate_scene_video_from_image
from .tools.s3_utils import normalize_bucket_and_prefix
from .tools.bedrock_clients import put_json_s3

# New helpers (you'll add them in edit_tools.py below)
from .tools.edit_tools import (
    mux_audio_over_video,        # still available if you need per-scene mux
    concat_videos_to_single,     # NEW ffmpeg-based
    concat_audios_to_single,     # NEW ffmpeg-based
    mux_final_audio_video,       # NEW ffmpeg-based
)

# ---- Audio tool compatibility (new and legacy) ----
try:
    from .tools.audio_tools import synth_dialogue_for_scene as synth_dialogue_scene
except ImportError:
    from .tools.audio_tools import synth_dialogue as _synth_dialogue_legacy
    def synth_dialogue_scene(scene, bucket, out_prefix):
        return _synth_dialogue_legacy(scene.get("dialogue", ""), bucket, out_prefix)

# ---- S3 env (normalized) ----
S3_BUCKET_RAW = os.getenv("S3_BUCKET", "")
S3_PREFIX_RAW = os.getenv("S3_PREFIX", "outputs")
BUCKET, DEFAULT_PREFIX = normalize_bucket_and_prefix(S3_BUCKET_RAW, S3_PREFIX_RAW)

# Scene/video defaults
SCENE_SECONDS = int(os.getenv("SCENE_SECONDS", "6"))
# ~150 wpm ≈ 2.5 words/sec → 6 sec ≈ 15 words. A little cushion:
MAX_WORDS_PER_DIALOGUE = int(os.getenv("MAX_WORDS_PER_DIALOGUE", "18"))


def _trim_to_words(text: str, max_words: int) -> str:
    if not text:
        return ""
    words = text.split()
    if len(words) <= max_words:
        return text.strip()
    return " ".join(words[:max_words]).rstrip(",.;:!—- ") + "…"


def _enforce_dialogue_caps(script: dict, max_words: int) -> dict:
    """Mutates script in-place to cap dialogue length per scene."""
    scenes = script.get("scenes", [])
    for sc in scenes:
        dlg = sc.get("dialogue", "")
        sc["dialogue"] = _trim_to_words(dlg, max_words)
    return script


def run_pipeline(planner, script_writer, evaluator, imager, videographer, audio, editor,
                 prompts, product_name, product_desc, ad_idea):
    """
    Artifacts under:
    outputs/<RUN_ID>/
      script/script.json
      script/eval.json
      script/summary.json
      scene image/scene_<n>.png
      video/scene_<n>.mp4
      audio/scene_<n>.mp3
      final video/concat_video.mp4
      final video/concat_audio.mp4
      final video/final_video.mp4
    """
    run_id = uuid4().hex[:12]
    run_prefix = f"{DEFAULT_PREFIX}/{run_id}"

    # 1) Script generation + evaluation loop
    script = generate_script(product_name, product_desc, ad_idea, prompts["script"])
    # enforce short dialogues BEFORE synthesizing audio
    script = _enforce_dialogue_caps(script, MAX_WORDS_PER_DIALOGUE)
    print("Script generated succesfully with capped dialogue.")

    verdict = evaluate_script(product_name, product_desc, script, prompts["rubric"])
    rounds = 0
    while verdict.get("decision") != "approve" and rounds < 3:
        ad_idea += f"\n\nRevision requests: {verdict.get('notes','')}"
        script = generate_script(product_name, product_desc, ad_idea, prompts["script"])
        script = _enforce_dialogue_caps(script, MAX_WORDS_PER_DIALOGUE)
        verdict = evaluate_script(product_name, product_desc, script, prompts["rubric"])
        rounds += 1
    print("Evaluation completed.")

    # Save artifacts in /script/
    save_script_s3(script, BUCKET, f"{run_prefix}/script/script.json")
    put_json_s3(BUCKET, f"{run_prefix}/script/eval.json", verdict)

    # 2) Per-scene assets (no per-scene mux anymore)
    image_keys: List[str] = []
    video_keys: List[str] = []
    audio_keys: List[str] = []

    for idx, scene in enumerate(script.get("scenes", []), start=1):
        # a) Keyframe image
        img_key = generate_scene_image(scene, BUCKET, f"{run_prefix}/scene image")
        image_keys.append(img_key)

        # b) 6s video from image (Nova Reel/Kling via env VIDEO_PROVIDER)
        vid_key = generate_scene_video_from_image(BUCKET, img_key, scene, f"{run_prefix}/video")
        video_keys.append(vid_key)
        print(f"Scene {idx} video generated: {vid_key}")

        # c) Dialogue VO (short)
        aud_key = synth_dialogue_scene(scene, BUCKET, f"{run_prefix}/audio")
        audio_keys.append(aud_key)
        print(f"Scene {idx} audio generated: {aud_key}")

    # 3) Concat all videos -> one silent video
    combined_video_uri, combined_video_key, *_ = concat_videos_to_single(
    BUCKET, video_keys, f"{run_prefix}/final video")
    print("Concatenated video:", combined_video_key)

    # 4) Concat all audios -> one audio
    #    If some scenes have no audio (None), drop them from concat list.
    combined_audio_uri, combined_audio_key, *_ = concat_audios_to_single(
    BUCKET, audio_keys, f"{run_prefix}/final video")
    print("Concatenated audio:", combined_audio_key)

    # 5) Final mux (video + audio) -> final_video.mp4
    final_uri, final_key, *_ = mux_final_audio_video(
        BUCKET, combined_video_key, combined_audio_key, f"{run_prefix}/final video"
    )
    print("Final video at:", final_uri)

    # Summary
    # --- Summary metadata ---
    summary = {
        "run_id": run_id,
        "title": script.get("title", ""),
        "cta": script.get("cta", ""),
        "folders": {
            "script": f"s3://{BUCKET}/{run_prefix}/script/",
            "images": f"s3://{BUCKET}/{run_prefix}/scene image/",
            "video": f"s3://{BUCKET}/{run_prefix}/video/",
            "audio": f"s3://{BUCKET}/{run_prefix}/audio/",
            "final": f"s3://{BUCKET}/{run_prefix}/final video/"
        },
        "scene_assets": [
            {
                "scene_id": sc.get("id"),
                "image_key": ik,
                "video_key": vk,
                "audio_key": ak
            }
            for sc, ik, vk, ak in zip(script["scenes"], image_keys, video_keys, audio_keys)
        ],
        "combined": {
            "combined_video_key": combined_video_key,
            "combined_video_uri": combined_video_uri,
            "combined_audio_key": combined_audio_key,
            "combined_audio_uri": combined_audio_uri,
            "final_video_key": final_key,
            "final_video_uri": final_uri,
        },
    }
    put_json_s3(BUCKET, f"{run_prefix}/script/summary.json", summary)

    # --- Function result ---
    return {
        "run_prefix": run_prefix,
        "run_id": run_id,
        "script_s3": f"s3://{BUCKET}/{run_prefix}/script/script.json",
        "eval_s3": f"s3://{BUCKET}/{run_prefix}/script/eval.json",
        "summary_s3": f"s3://{BUCKET}/{run_prefix}/script/summary.json",
        "final_video_folder": f"s3://{BUCKET}/{run_prefix}/final video/",
        "final_video_key": final_key,
        "final_video_uri": final_uri,
        "first_scene_output": {
            "image": image_keys[0],
            "video": video_keys[0],
            "audio": audio_keys[0],
        },
    }

def build_crew(planner, script_writer, evaluator, imager, videographer, audio, editor):
    """
    CrewAI tasks (real agents; crew.py still constructs them).
    """
    tasks = [
        Task(
            description="Plan and orchestrate the pipeline (deterministic; no LLM needed).",
            expected_output='{"steps":["script","evaluate","images","video","audio","concat_video","concat_audio","final_mux"]}',
            agent=planner,
        ),
        Task(
            description="Generate a ≤60s ad script as strict JSON per prompts/script_prompt.md. Each scene dialogue must be ≤18 words to fit 6 seconds.",
            expected_output=(
                "script.json uploaded under script/ AND a Python dict with keys: "
                "title, brand_voice, scenes[], cta, safety_notes"
            ),
            agent=script_writer,
        ),
        Task(
            description="Evaluate the script using prompts/eval_rubric.md and decide approve/revise.",
            expected_output=(
                "eval.json with fields: scores{6 floats with two decimals}, overall_score (two decimals), "
                'decision ("approve"|"revise"), notes (≤80 words)'
            ),
            agent=evaluator,
        ),
        Task(
            description="Create 1 keyframe image per scene using Bedrock Nova Canvas.",
            expected_output='PNG files in S3 under "scene image/scene_*.png"; return list of S3 keys.',
            agent=imager,
        ),
        Task(
            description="Generate a 6s clip per scene (Nova Reel TEXT_VIDEO mode) or Kling (env VIDEO_PROVIDER).",
            expected_output='MP4 files in S3 under "video/scene_*.mp4"; return list of S3 keys.',
            agent=videographer,
        ),
        Task(
            description="Synthesize short dialogue VO per scene via Amazon Polly (~≤18 words).",
            expected_output='Audio files in S3 under "audio/scene_*.mp3"; return list of S3 keys.',
            agent=audio,
        ),
        Task(
            description="Concatenate all scene videos into one silent MP4 under final video/concat_video.mp4.",
            expected_output="MP4 key in S3.",
            agent=editor,
        ),
        Task(
            description="Concatenate all scene audios into one AAC/MP4 under final video/concat_audio.mp4.",
            expected_output="MP4 key in S3.",
            agent=editor,
        ),
        Task(
            description="Mux concatenated audio over concatenated video, aligned from 00:00:00:00, duration match.",
            expected_output='Single MP4 under "final video/final_video.mp4".',
            agent=editor,
        ),
    ]
    agents = [planner, script_writer, evaluator, imager, videographer, audio, editor]
    return Crew(agents=agents, tasks=tasks, verbose=True)
