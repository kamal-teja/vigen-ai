# app/tools/audio_tools.py
import os, boto3
from .bedrock_clients import put_bytes_s3

def _polly():
    return boto3.client("polly", region_name=os.getenv("AWS_REGION","us-east-1"))

def synth_dialogue_for_scene(scene: dict, bucket: str, out_prefix: str) -> str:
    """
    Generate scene-level narration with slightly slower pacing (≈85% speed).
    Writes: outputs/<RUN_ID>/audio/scene_<id>.mp3
    """
    text = scene.get("dialogue", "") or " "
    voice = os.getenv("POLLY_VOICE", "Joanna")
    fmt = os.getenv("POLLY_FORMAT", "mp3")

    # Wrap text in SSML to control pace (~85% normal speed)
    ssml_text = f"<speak><prosody rate='85%'>{text}</prosody></speak>"

    resp = _polly().synthesize_speech(
        Text=ssml_text,
        TextType="ssml",
        VoiceId=voice,
        OutputFormat=fmt,
    )

    audio = resp["AudioStream"].read()
    key = f"{out_prefix}/scene_{scene['id']}.{fmt}"
    put_bytes_s3(
        bucket,
        key,
        audio,
        content_type="audio/mpeg" if fmt == "mp3" else "application/octet-stream",
    )
    return key

