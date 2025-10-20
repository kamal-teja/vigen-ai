-- Create custom types
CREATE TYPE adv_status AS ENUM (
  'draft','in_progress','evaluating','needs_fixes','approved',
  'rendering','generated','failed','published','archived'
);

CREATE TYPE asset_kind AS ENUM (
  'logo','product','lifestyle','background','music','other'
);

-- Extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS citext;

-- app_user table
CREATE TABLE app_user (
  user_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email         CITEXT UNIQUE NOT NULL,
  full_name     TEXT NOT NULL,
  role          TEXT NOT NULL DEFAULT 'creator',
  password_hash TEXT NOT NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- adv (advertisement) table
CREATE TABLE adv (
  adv_id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  owner_user_id        UUID NOT NULL REFERENCES app_user(user_id),
  title                TEXT NOT NULL,
  product_name         TEXT NOT NULL,
  product_desc         TEXT NOT NULL,
  language_tag         TEXT DEFAULT 'en-IN',
  aspect_ratio         TEXT DEFAULT '9:16',
  duration_sec         INT  NOT NULL DEFAULT 24 CHECK (duration_sec IN (18,24)),
  status               adv_status NOT NULL DEFAULT 'draft',
  run_id               TEXT,
  product_image_s3_uri TEXT,
  details_json_s3_uri  TEXT,
  script_s3_uri            TEXT,
  evaluator_report_s3_uri  TEXT,
  shot_plan_s3_uri         TEXT,
  subtitles_s3_uri         TEXT,
  reel_mp4_s3_uri          TEXT,
  reel_thumbnail_s3_uri    TEXT,
  status_updated_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  status_reason        TEXT,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- adv_asset table
CREATE TABLE adv_asset (
  asset_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  adv_id        UUID NOT NULL REFERENCES adv(adv_id) ON DELETE CASCADE,
  kind          asset_kind NOT NULL,
  name          TEXT,
  s3_uri        TEXT NOT NULL,
  width         INT,
  height        INT,
  rights_tag    TEXT,
  generated_by  TEXT,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes
CREATE INDEX idx_adv_owner ON adv(owner_user_id, created_at DESC);
CREATE INDEX idx_asset_adv ON adv_asset(adv_id);
