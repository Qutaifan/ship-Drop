-- Migration 002 Rollback: Drop supplier_verifications table and indexes
-- Framework: Hermes | Phase 2 Rollback

DROP INDEX IF EXISTS idx_verification_time;
DROP INDEX IF EXISTS idx_verification_status;
DROP INDEX IF EXISTS idx_verification_candidate;
DROP TABLE IF EXISTS supplier_verifications;
