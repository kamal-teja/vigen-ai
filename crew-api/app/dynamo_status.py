# dynamo_status.py
import os, boto3
from enum import Enum
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
AWS_REGION = os.getenv("AWS_REGION")
DDB_TABLE  = os.getenv("DDB_TABLE")   # your table with PK: id

dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
table = dynamodb.Table(name=DDB_TABLE)

class StepName(str, Enum):
    final_video_path = "final_video_path"
    script_generation_status = "script_generation_status"
    script_evaluation_status = "script_evaluation_status"
    video_generation_status = "video_generation_status"
    audio_generation_status = "audio_generation_status"
    editing_status = "editing_status"

STEP_ATTR = {
    StepName.final_video_path: "final_video_path",
    StepName.script_generation_status: "script_generation_status",
    StepName.script_evaluation_status: "script_evaluation_status",
    StepName.video_generation_status: "video_generation_status",
    StepName.audio_generation_status: "audio_generation_status",
    StepName.editing_status: "editing_status",
}

def _now():
    return datetime.now(timezone.utc).isoformat()

def ensure_row(run_id: str):
    """Create the row if missing so polling works from the start."""
    item = table.get_item(Key={"run_id": run_id}).get("Item")
    if item: 
        return
    seed = {
        "run_id": run_id,
        "script_generation_status": "PENDING",
        "script_evaluation_status": "PENDING",
        "video_generation_status": "PENDING",
        "audio_generation_status": "PENDING",
        "editing_status": "PENDING",
        "final_video_path": None,
        "updated_at": _now(),
    }
    table.put_item(Item=seed)

def update_status(run_id: str, step: StepName, status: str):
    """
    Update a single step status. status ∈ {"pending","running","completed","failed"}.
    """
    ensure_row(run_id)
    attr = STEP_ATTR[step]
    resp = table.update_item(
        Key={"run_id": run_id},
        UpdateExpression="SET #a = :val, #u = :now",
        ExpressionAttributeNames={"#a": attr, "#u": "updated_at"},
        ExpressionAttributeValues={":val": status, ":now": _now()},
        ReturnValues="ALL_NEW",
    )
    return resp["Attributes"]

def get_status(run_id: str):
    """Fetch the consolidated row for UI."""
    response = table.get_item(Key={"run_id": run_id})
    item = response.get("Item")
    if not item:
        return None
    return {
        'id': item['run_id'],
        'script_generation_status': item.get('script_generation_status', 'PENDING'),
        'script_evaluation_status': item.get('script_evaluation_status', 'PENDING'),
        'video_generation_status': item.get('video_generation_status', 'PENDING'),
        'audio_generation_status': item.get('audio_generation_status', 'PENDING'),
        'editing_status': item.get('editing_status', 'PENDING'),
        'updated_at': item['updated_at'],
        'final_video_uri': item.get('final_video_path')
    }

# def add_final_video_uri(run_id: str, video_uri: str):
#     """Adds the final video URI to the DynamoDB status item."""
#     ensure_row(run_id)
#     table.update_item(
#         Key={"run_id": run_id},
#         UpdateExpression="SET #uri = :uri_val, #u = :now",
#         ExpressionAttributeNames={"#uri": "final_video_uri", "#u": "updated_at"},
#         ExpressionAttributeValues={":uri_val": video_uri, ":now": _now()},
#     )
#     print(f"Final video URI for {run_id} saved to DynamoDB.")
