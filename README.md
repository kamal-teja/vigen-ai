# aws-agentic-ads

End-to-end **agentic AI** pipeline on **AWS** that turns:

**(product name, product description, advertisement idea) → final advertisement video(s) in S3**

Built with **CrewAI** for agent orchestration and AWS services for generation + post-production:

- **Bedrock**: Claude 3.7 (script), Nova Lite (evaluation), **Nova Canvas** (scene keyframes), **Nova Reel** (video)
- **Amazon Polly**: voice-over
- **AWS Elemental MediaConvert**: muxing/editing
- **Amazon S3**: artifact + final delivery

---

## ✨ Features

- Multi-agent flow (planning → script → evaluation loop → image → video → audio → edit)
- Strict JSON script schema (scenes with timing + dialogue)
- Automatic evaluator feedback loop (up to 3 revisions)
- Per-scene outputs (image, video, audio, final muxed clip) saved to S3
- Clear, modular tools for each AWS service
- Environment-driven model selection (swap models without code changes)

---

## 🏗️ Architecture

```
User CLI
  └─ app/main.py
      └─ Crew Orchestrator (planner)
          ├─ Script Agent  ── Bedrock (Claude 3.7) ─→ script.json
          ├─ Eval Agent    ── Bedrock (Nova Lite)  ─→ eval.json / rewrite loop
          ├─ Image Agent   ── Bedrock (Nova Canvas)→ scene_*.png
          ├─ Video Agent   ── Bedrock (Nova Reel)  ─→ scene_*.mp4
          ├─ Audio Agent   ── Amazon Polly         ─→ line_*.mp3
          └─ Editor Agent  ── MediaConvert         ─→ final/scene_*.mp4

All artifacts → Amazon S3 (optionally SSE-KMS)
```

---

## 🗂️ Repository Layout

```
aws-agentic-ads/
├─ README.md
├─ requirements.txt
├─ .env.example
├─ app/
│  ├─ main.py                 # CLI entrypoint
│  ├─ crew.py                 # wires agents + pipeline
│  ├─ agents.py               # CrewAI agent definitions
│  ├─ tasks.py                # sequential pipeline + evaluation loop
│  ├─ tools/
│  │  ├─ bedrock_clients.py   # boto3 clients + S3 helpers
│  │  ├─ script_tools.py      # Claude script generation
│  │  ├─ evaluation_tools.py  # Nova Lite evaluation
│  │  ├─ image_tools.py       # Nova Canvas (keyframes)
│  │  ├─ video_tools.py       # Nova Reel (short clips)
│  │  ├─ audio_tools.py       # Polly voiceover
│  │  └─ edit_tools.py        # MediaConvert mux
│  └─ prompts/
│     ├─ script_prompt.md     # JSON schema + constraints
│     └─ eval_rubric.md       # scoring rubric + threshold
```

---

## ✅ Prerequisites

- Python 3.10+
- AWS account with permissions for:
  - **bedrock:InvokeModel**, **bedrock:InvokeModelWithResponseStream**
  - **polly:SynthesizeSpeech**
  - **mediaconvert:DescribeEndpoints**, **mediaconvert:CreateJob**, **mediaconvert:GetJob**
  - **s3:GetObject**, **s3:PutObject**, **s3:ListBucket**
  - (optional) **kms:Encrypt/Decrypt** if using SSE-KMS
- Bedrock model access enabled in your **region** for:
  - Anthropic **Claude 3.7** (exact model ID varies by region)
  - **amazon.nova-lite** (text)
  - **amazon.nova-canvas** (image)
  - **amazon.nova-reel** (video)
- An S3 bucket for outputs
- A MediaConvert **IAM role** with S3 read/write

---

## 🔐 Minimal IAM (example)

> Adjust ARNs and bucket names; scope down to your resources.

**Execution role policy** (attach to the compute that runs this app, e.g., EC2/CodeBuild/Lambda):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    { "Effect": "Allow", "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"], "Resource": "*" },
    { "Effect": "Allow", "Action": ["polly:SynthesizeSpeech"], "Resource": "*" },
    { "Effect": "Allow", "Action": ["mediaconvert:DescribeEndpoints","mediaconvert:CreateJob","mediaconvert:GetJob"], "Resource": "*" },
    { "Effect": "Allow", "Action": ["s3:PutObject","s3:GetObject","s3:ListBucket"], "Resource": [
      "arn:aws:s3:::your-ads-bucket",
      "arn:aws:s3:::your-ads-bucket/*"
    ]},
    { "Effect": "Allow", "Action": ["kms:Encrypt","kms:Decrypt","kms:GenerateDataKey","kms:DescribeKey"], "Resource": "arn:aws:kms:REGION:ACCOUNT:key/KEY-ID" }
  ]
}
```

**MediaConvert role** (used by MediaConvert job itself) should allow reading inputs & writing outputs to your S3 bucket:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    { "Sid": "S3Access", "Effect": "Allow",
      "Action": ["s3:GetObject","s3:PutObject","s3:ListBucket"],
      "Resource": [
        "arn:aws:s3:::your-ads-bucket",
        "arn:aws:s3:::your-ads-bucket/*"
      ]
    },
    { "Sid": "MCServicePassRole", "Effect": "Allow",
      "Action": ["iam:PassRole"], "Resource": "arn:aws:iam::ACCOUNT:role/MediaConvert_Default_Role"
    }
  ]
}
```

---

## ⚙️ Configuration

Copy `.env.example` to `.env` and fill values:

| Variable | Description |
|---|---|
| `AWS_REGION` | Region where Bedrock/Polly/MediaConvert are enabled |
| `S3_BUCKET` | Output bucket |
| `S3_PREFIX` | Prefix for run folders (default `outputs`) |
| `BEDROCK_SCRIPT_MODEL_ID` | e.g. `anthropic.claude-3-7-sonnet-2025-xx` |
| `BEDROCK_EVAL_MODEL_ID` | e.g. `amazon.nova-lite-v1:0` |
| `BEDROCK_IMAGE_MODEL_ID` | e.g. `amazon.nova-canvas-v1:0` |
| `BEDROCK_VIDEO_MODEL_ID` | e.g. `amazon.nova-reel-v1:0` |
| `POLLY_VOICE` | e.g. `Joanna`, `Matthew`, etc. |
| `POLLY_FORMAT` | `mp3` or `ogg_vorbis` |
| `MEDIACONVERT_ROLE_ARN` | Role ARN for MediaConvert job |
| `MEDIACONVERT_ENDPOINT` | (optional) Leave blank; app auto-discovers first run |
| `S3_SSE_KMS_KEY_ARN` | (optional) KMS key for S3 SSE |

> **Model IDs vary by region and date.** Check the Bedrock console for exact strings.
### Choose your video backend

Set in `.env`:

- `VIDEO_PROVIDER=nova` (default) → uses **Bedrock Nova Reel**
- `VIDEO_PROVIDER=kling` → uses **Kling AI** via a provider gateway (AIMLAPI or PiAPI)

When using Kling:

- `KLING_PROVIDER` = `aimlapi` or `piapi`
- `KLING_API_KEY` = your provider token
- `KLING_BASE_URL` = provider base URL (e.g., `https://api.aimlapi.com`)
- `KLING_MODEL` = provider model name (e.g., `kling-ai/v1.6-pro/image-to-video`)
- Ensure S3 images are accessible by the provider; this repo presigns image URLs automatically.

---

## 🚀 Setup & Run

```bash
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                # Fill in values
```

Run the pipeline:

```bash
python -m app.main   --name "StormSpeed News"   --desc "Real-time news app with instant alerts and deep coverage."   
```

Example output:

```json
{
  "run_prefix": "outputs/1737700000",
  "script_s3": "s3://your-ads-bucket/outputs/1737700000/script.json",
  "eval_s3": "s3://your-ads-bucket/outputs/1737700000/eval.json",
  "summary_s3": "s3://your-ads-bucket/outputs/1737700000/summary.json",
  "scene_outputs": [
    {"scene_id":1,"folder_url":"https://your-ads-bucket.s3.us-east-1.amazonaws.com/outputs/1737700000/final/","mediaconvert_job":"1234abcd..."}
  ]
}
```

Artifacts are written under `s3://{S3_BUCKET}/{S3_PREFIX}/{timestamp}/`.

- `script.json` – final approved script
- `eval.json` – evaluator scores/notes
- `images/scene_*.png` – Nova Canvas keyframes
- `video/scene_*.mp4` – Nova Reel clips (pre-mux)
- `audio/line_*.mp3` – Polly dialogue
- `final/scene_*.mp4` – muxed per-scene outputs
- `summary.json` – quick manifest of outputs

---

## 🧠 Agentic Flow

1. **Planning Agent** – deterministic; orchestrates steps (no LLM).
2. **Script Agent** – **Claude 3.7** produces strict JSON scenes (≤60s).
3. **Evaluation Agent** – **Nova Lite** scores & either **approve** or provide revision notes.
   - Auto rewrite loop (max 3 rounds) by appending notes to context.
4. **Image Agent** – **Nova Canvas** creates 1 keyframe per scene.
5. **Video Agent** – **Nova Reel** animates each keyframe (3–12s per scene).
6. **Audio Agent** – **Polly** synthesizes dialogue.
7. **Editor Agent** – **MediaConvert** muxes audio over video and exports MP4.

> Want a **single final.mp4**? Add a concat job in `edit_tools.py` that stitches per-scene videos. (Left as an optional enhancement.)

---

## 🧪 Testing & Mocking

For low-cost dry runs:

- Reduce scenes (or total duration) by tweaking the script prompt.
- Temporarily skip Nova Reel calls and produce placeholder black frames with ffmpeg (not included here), or keep just Canvas images.
- Switch Polly voice to a cheaper one if needed.

---

## 💰 Cost Notes

- **Nova Reel** is typically the most expensive step. Keep clips short during iteration.
- Canvas (images) and Polly are comparatively cheap.
- MediaConvert charges per minute processed and outputs stored in S3.
- Use lifecycle rules on your S3 bucket to expire intermediate assets.

---

## 🔒 Security & Compliance

- Enable S3 **SSE-KMS** with your own key (`S3_SSE_KMS_KEY_ARN`).
- Limit IAM to your bucket and specific Bedrock models.
- Consider VPC endpoints for S3/Bedrock if running in private subnets.
- Avoid making the bucket public; prefer presigned URLs or CloudFront for sharing.

---

## 🩺 Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `UnrecognizedClientException` / invalid token | Local AWS creds missing/expired | `aws configure`, refresh role/session |
| `AccessDeniedException` on Bedrock | Model not enabled in region | Enable the model in Bedrock console; verify `BEDROCK_*_MODEL_ID` |
| Nova Canvas/Reel payload mismatch | API version differences | Check Bedrock docs for your region; adjust request/response fields in `image_tools.py` / `video_tools.py` |
| MediaConvert `DescribeEndpoints` failure | No endpoint in region | Ensure MediaConvert is supported in region; app auto-discovers and caches |
| MediaConvert job succeeds but no output | Role lacks S3 write | Update MediaConvert role policy for destination prefix |
| Polly voice not found | Voice not in region | Switch `POLLY_VOICE` to a supported voice |
| JSON parsing error after script gen | Claude returned prose | Strict prompt already enforces JSON; if it happens, add a JSON repair fallback in `script_tools.py` |

---

## 🔧 Extending

- **Final Stitch:** Add a second MediaConvert job that concatenates scene videos into `final/final.mp4`.
- **Step Functions:** Wrap each agent step in a state machine for retries, metrics, and alarms.
- **Observability:** Emit CloudWatch metrics/events per stage; add X-Ray where relevant.
- **Frontend:** Expose the pipeline via FastAPI + S3 presigned URLs for downloads.
- **Brand Packs:** Allow logo/color guidelines to condition the Canvas/Reel prompts.
- **Multilingual VO:** Map locale → Polly voice and translate dialogue with Bedrock first.

---

## 📄 JSON Schemas (high level)

**Script output (Claude):**
```json
{
  "title": "string",
  "brand_voice": "string",
  "scenes": [
    {
      "id": 1,
      "slug": "string",
      "visual_description": "string",
      "dialogue": "string",
      "duration_seconds": 6,
      "camera_directions": "string",
      "sfx": "string",
      "music_cue": "string"
    }
  ],
  "cta": "string",
  "safety_notes": "string"
}
```

**Evaluator verdict (Nova Lite):**
```json
{
  "scores": {
    "relevance": 0.9,
    "clarity": 0.9,
    "brand_fit": 0.85,
    "timing": 0.95,
    "imagery_feasibility": 0.9,
    "uniqueness": 0.8,
    "safety": 1.0
  },
  "decision": "approve",
  "notes": "string"
}
```

---

## 🧰 Local Tips

- Keep `.env` out of version control.
- If you want human preview of Canvas images locally, list the S3 `images/` keys and open with a viewer (or render in a simple Streamlit UI).

---

## 📜 License

MIT (or your org’s standard). Replace this with your preferred license.

---

## 🙋 FAQ

**Q: Which exact model IDs should I use?**  
A: Check **Bedrock → Model access** for your region. Copy the precise IDs into `.env`.

**Q: Can I change voices or languages?**  
A: Yes—set `POLLY_VOICE`. For multilingual scripts, translate dialogue via Bedrock before Polly.

**Q: How do I share outputs?**  
A: Keep the bucket private. Generate **presigned URLs** or front with **CloudFront**.

---

Happy shipping!