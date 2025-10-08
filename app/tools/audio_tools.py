# app/tools/audio_tools.py
import os, boto3
from .bedrock_clients import put_bytes_s3

def _polly():
    return boto3.client("polly", region_name=os.getenv("AWS_REGION","us-east-1"))

def synth_dialogue_for_scene(scene: dict, bucket: str, out_prefix: str) -> str:
    """
    out_prefix example: outputs/<RUN_ID>/audio
    writes: outputs/<RUN_ID>/audio/scene_<id>.mp3
    """
    text = scene.get("dialogue","") or " "
    voice = os.getenv("POLLY_VOICE","Joanna")
    fmt = os.getenv("POLLY_FORMAT","mp3")

    resp = _polly().synthesize_speech(Text=text, VoiceId=voice, OutputFormat=fmt)
    audio = resp["AudioStream"].read()
    key = f"{out_prefix}/scene_{scene['id']}.{fmt}"
    put_bytes_s3(bucket, key, audio, content_type="audio/mpeg" if fmt=="mp3" else "application/octet-stream")
    return key
