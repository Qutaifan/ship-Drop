"""SQLite-backed Data Repository with schema validation, CRUD helpers, and audit queries."""
from __future__ import annotations

import datetime
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Union

from jsonschema import Draft202012Validator

from agency.config.settings import get_settings

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS_DIR = ROOT / "schemas"


class Store:
    """SQLite-backed repository managing candidates, suppliers, signals, approvals, and audit logs."""

    def __init__(
        self,
        db_path: Optional[Union[str, Path]] = None,
        data_dir: Optional[Path] = None,
    ):
        settings = get_settings()
        self.data_dir = data_dir or settings.DATA_DIR
        self.db_path = str(db_path or settings.DATABASE_PATH)

        # File mirrors for direct file browsing / backwards compatibility
        self.candidates_dir = self.data_dir / "candidates"
        self.suppliers_dir = self.data_dir / "suppliers"
        self.signals_dir = self.data_dir / "signals"
        self.approvals_dir = self.data_dir / "approvals"
        self.verifications_dir = self.data_dir / "verifications"
        self.audit_dir = self.data_dir / "audit"

        for directory in [
            self.candidates_dir,
            self.suppliers_dir,
            self.signals_dir,
            self.approvals_dir,
            self.verifications_dir,
            self.audit_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

        self._validators: Dict[str, Draft202012Validator] = {}
        self._init_validators()
        self._init_db()

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def _init_validators(self) -> None:
        schema_map = {
            "candidate": SCHEMAS_DIR / "candidate.schema.json",
            "supplier": SCHEMAS_DIR / "supplier.schema.json",
            "trade_signal": SCHEMAS_DIR / "trade_signal.schema.json",
            "approval": SCHEMAS_DIR / "approval.schema.json",
            "supplier_verification": SCHEMAS_DIR / "supplier_verification.schema.json",
            "evidence": SCHEMAS_DIR / "evidence.schema.json",
        }
        for name, path in schema_map.items():
            if path.exists():
                with path.open("r", encoding="utf-8") as f:
                    schema_data = json.load(f)
                    self._validators[name] = Draft202012Validator(schema_data)

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS candidates (
                    candidate_id TEXT PRIMARY KEY,
                    product_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    market_config_id TEXT NOT NULL,
                    data TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS suppliers (
                    supplier_id TEXT PRIMARY KEY,
                    supplier_name TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    warehouse_country TEXT NOT NULL,
                    data TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS signals (
                    signal_id TEXT PRIMARY KEY,
                    signal_type TEXT NOT NULL,
                    candidate_id TEXT NOT NULL,
                    approval_status TEXT NOT NULL,
                    data TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS approvals (
                    approval_id TEXT PRIMARY KEY,
                    action TEXT NOT NULL,
                    object_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    approved_by TEXT NOT NULL,
                    data TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS supplier_verifications (
                    verification_id TEXT PRIMARY KEY,
                    candidate_id TEXT NOT NULL,
                    supplier_id TEXT NOT NULL,
                    sku TEXT NOT NULL,
                    status TEXT NOT NULL,
                    data TEXT NOT NULL,
                    verified_at TEXT NOT NULL,
                    verified_at_unix INTEGER NOT NULL
                )
                """
            )
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_verification_candidate ON supplier_verifications(candidate_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_verification_status ON supplier_verifications(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_verification_time ON supplier_verifications(verified_at_unix)")

            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    details TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def validate(self, schema_name: str, data: Dict[str, Any]) -> List[str]:
        validator = self._validators.get(schema_name)
        if not validator:
            return [f"Unknown schema validator: {schema_name}"]
        return [err.message for err in validator.iter_errors(data)]

    # --- Candidate Repository ---
    def save_candidate(self, candidate_data: Dict[str, Any]) -> Path:
        errors = self.validate("candidate", candidate_data)
        if errors:
            raise ValueError(f"Candidate data failed schema validation: {errors}")

        candidate_id = candidate_data["candidate_id"]
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        created_at = candidate_data.get("created_at", now)
        data_json = json.dumps(candidate_data, ensure_ascii=False)

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO candidates (candidate_id, product_name, status, market_config_id, data, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(candidate_id) DO UPDATE SET
                    product_name=excluded.product_name,
                    status=excluded.status,
                    market_config_id=excluded.market_config_id,
                    data=excluded.data,
                    updated_at=excluded.updated_at
                """,
                (
                    candidate_id,
                    candidate_data.get("product_name", ""),
                    candidate_data.get("status", "VALIDATION_READY"),
                    candidate_data.get("market_config_id", "us-pilot"),
                    data_json,
                    created_at,
                    now,
                ),
            )
            conn.commit()

        # File mirror
        filepath = self.candidates_dir / f"{candidate_id}.json"
        with filepath.open("w", encoding="utf-8") as f:
            f.write(data_json)

        self.log_audit("CANDIDATE_SAVED", {"candidate_id": candidate_id, "status": candidate_data.get("status")})
        return filepath

    def get_candidate(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT data FROM candidates WHERE candidate_id = ?", (candidate_id,)).fetchone()
            if row:
                return json.loads(row["data"])

        filepath = self.candidates_dir / f"{candidate_id}.json"
        if filepath.exists():
            with filepath.open("r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def list_candidates(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            if status:
                rows = conn.execute("SELECT data FROM candidates WHERE status = ? ORDER BY created_at DESC", (status,)).fetchall()
            else:
                rows = conn.execute("SELECT data FROM candidates ORDER BY created_at DESC").fetchall()
            if rows:
                return [json.loads(r["data"]) for r in rows]

        results = []
        for file in self.candidates_dir.glob("*.json"):
            with file.open("r", encoding="utf-8") as f:
                c = json.load(f)
                if status and c.get("status") != status:
                    continue
                results.append(c)
        return sorted(results, key=lambda x: x.get("created_at", ""), reverse=True)

    def delete_candidate(self, candidate_id: str) -> bool:
        with self._get_connection() as conn:
            cur = conn.execute("DELETE FROM candidates WHERE candidate_id = ?", (candidate_id,))
            conn.commit()
            deleted = cur.rowcount > 0

        filepath = self.candidates_dir / f"{candidate_id}.json"
        if filepath.exists():
            filepath.unlink()

        if deleted:
            self.log_audit("CANDIDATE_DELETED", {"candidate_id": candidate_id})
        return deleted

    # --- Supplier Repository ---
    def save_supplier(self, supplier_data: Dict[str, Any]) -> Path:
        errors = self.validate("supplier", supplier_data)
        if errors:
            raise ValueError(f"Supplier data failed schema validation: {errors}")

        supplier_id = supplier_data["supplier_id"]
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        created_at = supplier_data.get("updated_at", now)
        data_json = json.dumps(supplier_data, ensure_ascii=False)

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO suppliers (supplier_id, supplier_name, platform, warehouse_country, data, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(supplier_id) DO UPDATE SET
                    supplier_name=excluded.supplier_name,
                    platform=excluded.platform,
                    warehouse_country=excluded.warehouse_country,
                    data=excluded.data,
                    updated_at=excluded.updated_at
                """,
                (
                    supplier_id,
                    supplier_data.get("supplier_name", ""),
                    supplier_data.get("platform", "cjdropshipping"),
                    supplier_data.get("warehouse_country", "US"),
                    data_json,
                    created_at,
                    now,
                ),
            )
            conn.commit()

        filepath = self.suppliers_dir / f"{supplier_id}.json"
        with filepath.open("w", encoding="utf-8") as f:
            f.write(data_json)

        self.log_audit("SUPPLIER_SAVED", {"supplier_id": supplier_id, "platform": supplier_data.get("platform")})
        return filepath

    def get_supplier(self, supplier_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT data FROM suppliers WHERE supplier_id = ?", (supplier_id,)).fetchone()
            if row:
                return json.loads(row["data"])

        filepath = self.suppliers_dir / f"{supplier_id}.json"
        if filepath.exists():
            with filepath.open("r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def list_suppliers(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            rows = conn.execute("SELECT data FROM suppliers ORDER BY updated_at DESC").fetchall()
            if rows:
                return [json.loads(r["data"]) for r in rows]

        results = []
        for file in self.suppliers_dir.glob("*.json"):
            with file.open("r", encoding="utf-8") as f:
                results.append(json.load(f))
        return sorted(results, key=lambda x: x.get("score", {}).get("total", 0), reverse=True)

    def delete_supplier(self, supplier_id: str) -> bool:
        with self._get_connection() as conn:
            cur = conn.execute("DELETE FROM suppliers WHERE supplier_id = ?", (supplier_id,))
            conn.commit()
            deleted = cur.rowcount > 0

        filepath = self.suppliers_dir / f"{supplier_id}.json"
        if filepath.exists():
            filepath.unlink()

        if deleted:
            self.log_audit("SUPPLIER_DELETED", {"supplier_id": supplier_id})
        return deleted

    # --- Signal Repository ---
    def save_signal(self, signal_data: Dict[str, Any]) -> Path:
        errors = self.validate("trade_signal", signal_data)
        if errors:
            raise ValueError(f"Trade signal failed schema validation: {errors}")

        signal_id = signal_data["signal_id"]
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        created_at = signal_data.get("created_at", now)
        data_json = json.dumps(signal_data, ensure_ascii=False)

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO signals (signal_id, signal_type, candidate_id, approval_status, data, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(signal_id) DO UPDATE SET
                    signal_type=excluded.signal_type,
                    candidate_id=excluded.candidate_id,
                    approval_status=excluded.approval_status,
                    data=excluded.data,
                    updated_at=excluded.updated_at
                """,
                (
                    signal_id,
                    signal_data.get("signal_type", "BUY"),
                    signal_data.get("candidate_id", ""),
                    signal_data.get("approval_status", "PENDING_FOUNDER_REVIEW"),
                    data_json,
                    created_at,
                    now,
                ),
            )
            conn.commit()

        filepath = self.signals_dir / f"{signal_id}.json"
        with filepath.open("w", encoding="utf-8") as f:
            f.write(data_json)

        self.log_audit("SIGNAL_GENERATED", {
            "signal_id": signal_id,
            "type": signal_data.get("signal_type"),
            "candidate_id": signal_data.get("candidate_id"),
            "approval_status": signal_data.get("approval_status"),
        })
        return filepath

    def get_signal(self, signal_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT data FROM signals WHERE signal_id = ?", (signal_id,)).fetchone()
            if row:
                return json.loads(row["data"])

        filepath = self.signals_dir / f"{signal_id}.json"
        if filepath.exists():
            with filepath.open("r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def list_signals(self, status: Optional[str] = None, signal_type: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            query = "SELECT data FROM signals WHERE 1=1"
            params: List[Any] = []
            if status:
                query += " AND approval_status = ?"
                params.append(status)
            if signal_type:
                query += " AND signal_type = ?"
                params.append(signal_type)
            query += " ORDER BY created_at DESC"
            rows = conn.execute(query, params).fetchall()
            if rows:
                return [json.loads(r["data"]) for r in rows]

        results = []
        for file in self.signals_dir.glob("*.json"):
            with file.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if status and data.get("approval_status") != status:
                    continue
                if signal_type and data.get("signal_type") != signal_type:
                    continue
                results.append(data)
        return sorted(results, key=lambda x: x.get("created_at", ""), reverse=True)

    def delete_signal(self, signal_id: str) -> bool:
        with self._get_connection() as conn:
            cur = conn.execute("DELETE FROM signals WHERE signal_id = ?", (signal_id,))
            conn.commit()
            deleted = cur.rowcount > 0

        filepath = self.signals_dir / f"{signal_id}.json"
        if filepath.exists():
            filepath.unlink()

        if deleted:
            self.log_audit("SIGNAL_DELETED", {"signal_id": signal_id})
        return deleted

    # --- Approval Repository ---
    def save_approval(self, approval_data: Dict[str, Any]) -> Path:
        errors = self.validate("approval", approval_data)
        if errors:
            raise ValueError(f"Approval failed schema validation: {errors}")

        approval_id = approval_data["approval_id"]
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        created_at = approval_data.get("approved_at", now)
        data_json = json.dumps(approval_data, ensure_ascii=False)

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO approvals (approval_id, action, object_id, status, approved_by, data, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(approval_id) DO UPDATE SET
                    action=excluded.action,
                    object_id=excluded.object_id,
                    status=excluded.status,
                    approved_by=excluded.approved_by,
                    data=excluded.data,
                    updated_at=excluded.updated_at
                """,
                (
                    approval_id,
                    approval_data.get("action", "test_campaign_launch"),
                    approval_data.get("object_id", ""),
                    approval_data.get("status", "APPROVED"),
                    approval_data.get("approved_by", "Ahmad"),
                    data_json,
                    created_at,
                    now,
                ),
            )
            conn.commit()
            conn.close()

        filepath = self.approvals_dir / f"{approval_id}.json"
        with filepath.open("w", encoding="utf-8") as f:
            f.write(data_json)

        self.log_audit("APPROVAL_RECORDED", {
            "approval_id": approval_id,
            "action": approval_data.get("action"),
            "approved_by": approval_data.get("approved_by"),
            "status": approval_data.get("status"),
        })
        return filepath

    def get_approval(self, approval_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT data FROM approvals WHERE approval_id = ?", (approval_id,)).fetchone()
            if row:
                return json.loads(row["data"])

        filepath = self.approvals_dir / f"{approval_id}.json"
        if filepath.exists():
            with filepath.open("r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def list_approvals(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            if status:
                rows = conn.execute("SELECT data FROM approvals WHERE status = ? ORDER BY created_at DESC", (status,)).fetchall()
            else:
                rows = conn.execute("SELECT data FROM approvals ORDER BY created_at DESC").fetchall()
            if rows:
                return [json.loads(r["data"]) for r in rows]

        results = []
        for file in self.approvals_dir.glob("*.json"):
            with file.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if status and data.get("status") != status:
                    continue
                results.append(data)
        return sorted(results, key=lambda x: x.get("approved_at", ""), reverse=True)

    def delete_approval(self, approval_id: str) -> bool:
        with self._get_connection() as conn:
            cur = conn.execute("DELETE FROM approvals WHERE approval_id = ?", (approval_id,))
            conn.commit()
            deleted = cur.rowcount > 0

        filepath = self.approvals_dir / f"{approval_id}.json"
        if filepath.exists():
            filepath.unlink()

        if deleted:
            self.log_audit("APPROVAL_DELETED", {"approval_id": approval_id})
        return deleted

    # --- Supplier Verification Repository ---
    def save_supplier_verification(self, verification_data: Dict[str, Any]) -> Path:
        errors = self.validate("supplier_verification", verification_data)
        if errors:
            raise ValueError(f"Supplier verification failed schema validation: {errors}")

        ver_id = verification_data["verification_id"]
        candidate_id = verification_data["candidate_id"]
        supplier_id = verification_data["supplier_id"]
        sku = verification_data["sku"]
        status = verification_data["status"]
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        verified_at = verification_data.get("verified_at", now)
        verified_at_unix = int(verification_data.get("verified_at_unix", int(datetime.datetime.now(datetime.timezone.utc).timestamp())))
        data_json = json.dumps(verification_data, ensure_ascii=False)

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO supplier_verifications (verification_id, candidate_id, supplier_id, sku, status, data, verified_at, verified_at_unix)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(verification_id) DO UPDATE SET
                    candidate_id=excluded.candidate_id,
                    supplier_id=excluded.supplier_id,
                    sku=excluded.sku,
                    status=excluded.status,
                    data=excluded.data,
                    verified_at=excluded.verified_at,
                    verified_at_unix=excluded.verified_at_unix
                """,
                (
                    ver_id,
                    candidate_id,
                    supplier_id,
                    sku,
                    status,
                    data_json,
                    verified_at,
                    verified_at_unix,
                ),
            )
            conn.commit()

        filepath = self.verifications_dir / f"{ver_id}.json"
        with filepath.open("w", encoding="utf-8") as f:
            f.write(data_json)

        self.log_audit("SUPPLIER_VERIFIED", {
            "verification_id": ver_id,
            "candidate_id": candidate_id,
            "sku": sku,
            "status": status,
            "stability_score": verification_data.get("stability_score"),
        })
        return filepath

    def get_supplier_verification(self, verification_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            row = conn.execute("SELECT data FROM supplier_verifications WHERE verification_id = ?", (verification_id,)).fetchone()
            if row:
                return json.loads(row["data"])

        filepath = self.verifications_dir / f"{verification_id}.json"
        if filepath.exists():
            with filepath.open("r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def get_latest_verification_for_candidate(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT data FROM supplier_verifications WHERE candidate_id = ? ORDER BY verified_at_unix DESC LIMIT 1",
                (candidate_id,),
            ).fetchone()
            if row:
                return json.loads(row["data"])

        # Fallback to filesystem
        matching = []
        for file in self.verifications_dir.glob("*.json"):
            with file.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("candidate_id") == candidate_id:
                    matching.append(data)
        if matching:
            matching.sort(key=lambda x: x.get("verified_at_unix", 0), reverse=True)
            return matching[0]
        return None

    def list_supplier_verifications(
        self,
        candidate_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            query = "SELECT data FROM supplier_verifications WHERE 1=1"
            params: List[Any] = []
            if candidate_id:
                query += " AND candidate_id = ?"
                params.append(candidate_id)
            if status:
                query += " AND status = ?"
                params.append(status)
            query += " ORDER BY verified_at_unix DESC LIMIT ?"
            params.append(limit)
            rows = conn.execute(query, params).fetchall()
            if rows:
                return [json.loads(r["data"]) for r in rows]

        results = []
        for file in self.verifications_dir.glob("*.json"):
            with file.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if candidate_id and data.get("candidate_id") != candidate_id:
                    continue
                if status and data.get("status") != status:
                    continue
                results.append(data)
        results.sort(key=lambda x: x.get("verified_at_unix", 0), reverse=True)
        return results[:limit]

    def delete_supplier_verification(self, verification_id: str) -> bool:
        with self._get_connection() as conn:
            cur = conn.execute("DELETE FROM supplier_verifications WHERE verification_id = ?", (verification_id,))
            conn.commit()
            deleted = cur.rowcount > 0

        filepath = self.verifications_dir / f"{verification_id}.json"
        if filepath.exists():
            filepath.unlink()

        if deleted:
            self.log_audit("SUPPLIER_VERIFICATION_DELETED", {"verification_id": verification_id})
        return deleted

    # --- Audit Queries ---
    def log_audit(self, event_type: str, details: Dict[str, Any]) -> None:
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        details_json = json.dumps(details, ensure_ascii=False)

        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO audit_log (event_type, details, created_at) VALUES (?, ?, ?)",
                (event_type, details_json, now),
            )
            conn.commit()

        # Mirror to jsonl
        log_file = self.audit_dir / "audit_log.jsonl"
        with log_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"timestamp": now, "event_type": event_type, "details": details}) + "\n")

    def get_audit_trail(self, limit: int = 50, event_type: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            if event_type:
                rows = conn.execute(
                    "SELECT event_type, details, created_at FROM audit_log WHERE event_type = ? ORDER BY id DESC LIMIT ?",
                    (event_type, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT event_type, details, created_at FROM audit_log ORDER BY id DESC LIMIT ?",
                    (limit,),
                ).fetchall()

            if rows:
                return [
                    {"timestamp": r["created_at"], "event_type": r["event_type"], "details": json.loads(r["details"])}
                    for r in rows
                ]

        log_file = self.audit_dir / "audit_log.jsonl"
        if not log_file.exists():
            return []
        lines = []
        with log_file.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    item = json.loads(line)
                    if event_type and item.get("event_type") != event_type:
                        continue
                    lines.append(item)
        return lines[-limit:]
