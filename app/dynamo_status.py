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
    status = "status"
    final_video_path = "final_video_path"
    # script_evaluation = "script_evaluation"
    # video_generation  = "video_generation"
    # audio_generation  = "audio_generation"
    # editing           = "editing"

STEP_ATTR = {
    StepName.status: "status",
    StepName.final_video_path: "final_video_path",
    # StepName.script_evaluation: "script_evaluation_status",
    # StepName.video_generation:  "video_generation_status",
    # StepName.audio_generation:  "audio_generation_status",
    # StepName.editing:           "editing_status",
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
        "status": "pending",
        "final_video_path": "pending",
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
    ensure_row(run_id)
    response = table.get_item(Key={"run_id": run_id})
    return response.get("Item")

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
