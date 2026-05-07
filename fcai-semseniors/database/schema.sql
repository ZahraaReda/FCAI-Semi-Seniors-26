-- ============================================================
-- FCAI Semi Seniors 26' — PostgreSQL Schema
-- Run this in pgAdmin or psql after creating the database
-- ============================================================

-- Users
CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(80)  UNIQUE NOT NULL,
    email         VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    created_at    TIMESTAMP    DEFAULT NOW()
);

-- Profiles
CREATE TABLE IF NOT EXISTS profiles (
    id             SERIAL PRIMARY KEY,
    user_id        INTEGER      UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    full_name      VARCHAR(150) NOT NULL,
    photo_filename VARCHAR(260),
    senior_quote   VARCHAR(500),
    department     VARCHAR(10),
    quiz_completed BOOLEAN      DEFAULT FALSE,
    created_at     TIMESTAMP    DEFAULT NOW(),
    updated_at     TIMESTAMP    DEFAULT NOW()
);

-- Quiz Results (one row per user, upserted on retake)
CREATE TABLE IF NOT EXISTS quiz_results (
    id             SERIAL PRIMARY KEY,
    user_id        INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    cs_score       INTEGER   DEFAULT 0,
    ai_score       INTEGER   DEFAULT 0,
    mp_score       INTEGER   DEFAULT 0,
    mi_score       INTEGER   DEFAULT 0,
    answers        TEXT,
    suggested_dept VARCHAR(10),
    taken_at       TIMESTAMP DEFAULT NOW()
);

-- Memories (extra photos per user)
CREATE TABLE IF NOT EXISTS memories (
    id             SERIAL PRIMARY KEY,
    user_id        INTEGER      NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    photo_filename VARCHAR(260) NOT NULL,
    caption        VARCHAR(500),
    uploaded_at    TIMESTAMP    DEFAULT NOW()
);