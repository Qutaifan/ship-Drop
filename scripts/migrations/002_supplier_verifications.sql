-- Migration 002: Create supplier_verifications table and performance indexes
-- Applied on: 2026-09-01
-- Framework: Hermes | Phase 2

CREATE TABLE IF NOT EXISTS supplier_verifications (
    verification_id TEXT PRIMARY KEY,
    candidate_id TEXT NOT NULL,
    supplier_id TEXT NOT NULL,
    sku TEXT NOT NULL,
    status TEXT NOT NULL,
    data TEXT NOT NULL,
    verified_at TEXT NOT NULL,
    verified_at_unix INTEGER NOT NULL
);

-- Performance indexes for rapid drift scanning and time-series audit queries
CREATE INDEX IF NOT EXISTS idx_verification_candidate ON supplier_verifications(candidate_id);
CREATE INDEX IF NOT EXISTS idx_verification_status ON supplier_verifications(status);
CREATE INDEX IF NOT EXISTS idx_verification_time ON supplier_verifications(verified_at_unix);
