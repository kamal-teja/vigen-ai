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
    script_generation = "script_generation"
    script_evaluation = "script_evaluation"
    video_generation  = "video_generation"
    audio_generation  = "audio_generation"
    editing           = "editing"

STEP_ATTR = {
    StepName.script_generation: "script_generation_status",
    StepName.script_evaluation: "script_evaluation_status",
    StepName.video_generation:  "video_generation_status",
    StepName.audio_generation:  "audio_generation_status",
    StepName.editing:           "editing_status",
}

def _now():
    return datetime.now(timezone.utc).isoformat()

def ensure_row(run_id: str):
    """Create the row if missing so polling works from the start."""
    item = table.get_item(Key={"id": run_id}).get("Item")
    if item: 
        return
    seed = {
        "id": run_id,
        "script_generation_status": "pending",
        "script_evaluation_status": "pending",
        "video_generation_status": "pending",
        "audio_generation_status": "pending",
        "editing_status": "pending",
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
        Key={"id": run_id},
        UpdateExpression="SET #a = :val, #u = :now",
        ExpressionAttributeNames={"#a": attr, "#u": "updated_at"},
        ExpressionAttributeValues={":val": status, ":now": _now()},
        ReturnValues="ALL_NEW",
    )
    return resp["Attributes"]

def get_status(run_id: str):
    """Fetch the consolidated row for UI."""
    ensure_row(run_id)
    response = table.get_item(Key={"id": run_id})
    return response.get("Item")


