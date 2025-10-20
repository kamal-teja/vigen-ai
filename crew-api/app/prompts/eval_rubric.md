# Advertisement Script Evaluation Rubric (JSON Only)

Evaluate the provided INPUT (which contains `product` and `script`). Do **not** assume facts not present in INPUT.

## Scoring Rules
- Each metric is scored from **0.00 to 1.00** with **EXACTLY two decimals** (e.g., `0.73`).
- If information is **missing or uncertain**, assign a **conservative score ≤ 0.50** and explain briefly in `notes`.
- Be strict: reward clarity, feasibility, and authentic brand alignment over flowery language.
- **If the script contains adult, suggestive, violent, or inappropriate sensory content**, assign:
  - `sensory_and_content_safety ≤ 0.30`
  - `decision = "revise"`
  - Add a rewritten version under `"suggested_rewrite"` field in output.

## Metrics (all keys must be present)
- **relevance_to_product_and_brand** — Ties clearly to product features/benefits/brand.
- **clarity_and_simplicity** — Message is immediately understandable; avoids jargon.
- **attention_grabbing_hook** — Early hook draws attention without sensationalism.
- **consistency_and_tone** — Tone/style is uniform and appropriate for the brand/audience.
- **logical_story_flow** — Scenes progress coherently toward a clear CTA.
- **uniqueness_and_creativity** — Distinctive idea; avoids clichés; memorable line or device.
- **sensory_and_content_safety** — Avoids adult, violent, discriminatory, or suggestive material; maintains family-safe and brand-appropriate tone.


## Decision Policy
- `overall_score` = arithmetic **mean** of the six metric scores (two decimals).
- `decision` = `"approve"` **iff** `overall_score ≥ 0.70` **AND** **no** single metric `< 0.60`; otherwise `"revise"`.
- If `"revise"` due to `sensory_and_content_safety < 0.60`, generate a **clean rewritten version** under `"suggested_rewrite"` that removes all inappropriate or adult content while retaining core intent.

## Output Requirements
- **Return STRICT JSON** (no extra text).
- Every score must be a float with **two decimals**.
- Keep `notes` concise (≤ 80 words). If `"revise"`, include **2–4 actionable suggestions**.
- If `"revise"` and `sensory_and_content_safety < 0.60`, include `"suggested_rewrite"` with a rewritten, safe version of the ad script.
- Return ONLY the JSON object conforming to the schema below. Do not wrap in backticks.

## JSON schema to return
{
  "scores": {
    "relevance_to_product_and_brand": 0.00,
    "clarity_and_simplicity": 0.00,
    "attention_grabbing_hook": 0.00,
    "consistency_and_tone": 0.00,
    "logical_story_flow": 0.00,
    "uniqueness_and_creativity": 0.00,
    "sensory_and_content_safety": 0.00
  },
  "overall_score": 0.00,
  "decision": "approve" | "revise",
  "notes": "short rationale; if 'revise', include 2–4 specific fixes",
  "suggested_rewrite": "clean, family-safe version of script (only if adult/suggestive elements found)"
}