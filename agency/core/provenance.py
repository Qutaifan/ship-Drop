"""HMAC Provenance Signing & Data Retention for Supplier Verifications and Signals."""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import sqlite3
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

ROOT = Path(__file__).resolve().parents[2]
SECRET_KEY = os.getenv("HERMES_PROVENANCE_SECRET", "hermes-default-provenance-key-2026").encode("utf-8")


def sign_payload(payload: Dict[str, Any]) -> str:
    """Compute a deterministic HMAC-SHA256 signature for a dictionary payload."""
    canonical_bytes = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hmac.new(SECRET_KEY, canonical_bytes, hashlib.sha256).hexdigest()


def verify_payload_signature(payload: Dict[str, Any], signature: str) -> bool:
    """Verify that a given payload matches its HMAC-SHA256 signature."""
    expected = sign_payload(payload)
    return hmac.compare_digest(expected, signature)


def rotate_verifications(
    db_path: Path,
    retention_days: int = 90,
    archive_dir: Optional[Path] = None,
) -> Tuple[int, Optional[Path]]:
    """Rotate and archive verifications older than retention_days.

    Returns (purged_count, archive_file_path).
    """
    cutoff_unix = int(time.time()) - (retention_days * 86400)
    archive_file: Optional[Path] = None

    db_path = Path(db_path)
    if not db_path.exists():
        return 0, None

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    # Find records to archive
    rows = cursor.execute(
        "SELECT verification_id, candidate_id, supplier_id, sku, status, data, verified_at, verified_at_unix "
        "FROM supplier_verifications WHERE verified_at_unix < ?",
        (cutoff_unix,),
    ).fetchall()

    if not rows:
        conn.close()
        return 0, None

    # Write archive file if directory provided
    if archive_dir:
        archive_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        archive_file = archive_dir / f"verifications_archive_{ts}.jsonl"
        with archive_file.open("w", encoding="utf-8") as f:
            for r in rows:
                record = {
                    "verification_id": r[0],
                    "candidate_id": r[1],
                    "supplier_id": r[2],
                    "sku": r[3],
                    "status": r[4],
                    "data": json.loads(r[5]) if isinstance(r[5], str) else r[5],
                    "verified_at": r[6],
                    "verified_at_unix": r[7],
                }
                f.write(json.dumps(record) + "\n")

    # Purge old records
    cursor.execute("DELETE FROM supplier_verifications WHERE verified_at_unix < ?", (cutoff_unix,))
    conn.commit()
    purged_count = cursor.rowcount
    conn.close()

    return purged_count, archive_file
