"""Hermes Founder-Gated Autonomous Execution Windows: Time-boxed cryptographic operational grants."""
from __future__ import annotations

import datetime
import hashlib
import hmac
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from agency.core.store import Store

ROOT = Path(__file__).resolve().parents[2]
WINDOWS_FILE = ROOT / "config" / "autonomous_windows.json"


class AutonomousWindowManager:
    """Manages time-boxed, spend-capped autonomous execution windows authorized by the Founder."""

    def __init__(self, store: Optional[Store] = None, secret_key: Optional[str] = None):
        self.store = store or Store()
        self.secret = (secret_key or os.getenv("HERMES_PROVENANCE_SECRET", "hermes-founder-gov-key-2026")).encode("utf-8")
        self._ensure_storage()

    def _ensure_storage(self) -> None:
        WINDOWS_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not WINDOWS_FILE.exists():
            with WINDOWS_FILE.open("w", encoding="utf-8") as f:
                json.dump({"active_windows": []}, f, indent=2)

    def _sign_window(self, payload: Dict[str, Any]) -> str:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hmac.new(self.secret, canonical.encode("utf-8"), hashlib.sha256).hexdigest()

    def grant_window(
        self,
        founder_actor: str,
        duration_hours: float,
        spend_cap: float,
        permitted_actions: Optional[List[str]] = None,
        permitted_skus: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Creates a time-boxed cryptographic autonomous execution window."""
        now = datetime.datetime.now(datetime.timezone.utc)
        expires = now + datetime.timedelta(hours=duration_hours)
        win_id = f"win-{now.strftime('%Y%m%d%H%M')}-{os.urandom(3).hex()}"

        core_payload = {
            "window_id": win_id,
            "authorized_by": founder_actor,
            "granted_at": now.isoformat(),
            "expires_at": expires.isoformat(),
            "duration_hours": duration_hours,
            "spend_cap": spend_cap,
            "consumed_spend": 0.0,
            "permitted_actions": permitted_actions or ["CANARY_ORDER_DISPATCH", "SUPPLIER_FAILOVER_SWITCH"],
            "permitted_skus": permitted_skus or ["*"],
            "status": "ACTIVE",
        }

        signature = self._sign_window(core_payload)
        full_window = {**core_payload, "cryptographic_token": signature}

        # Persist window
        with WINDOWS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)

        data["active_windows"].append(full_window)

        with WINDOWS_FILE.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        self.store.log_audit("AUTONOMOUS_WINDOW_GRANTED", {
            "window_id": win_id,
            "founder": founder_actor,
            "duration_hours": duration_hours,
            "spend_cap": spend_cap,
            "expires_at": expires.isoformat(),
        })

        return full_window

    def is_action_authorized(
        self,
        action: str,
        sku_id: str,
        spend_amount: float = 0.0,
    ) -> Dict[str, Any]:
        """Evaluates whether an action is permitted within an active, non-expired window."""
        now = datetime.datetime.now(datetime.timezone.utc)

        with WINDOWS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)

        for win in data.get("active_windows", []):
            if win.get("status") != "ACTIVE":
                continue

            # Check expiration
            expires = datetime.datetime.fromisoformat(win["expires_at"])
            if now > expires:
                win["status"] = "EXPIRED"
                continue

            # Check action permission
            allowed_acts = win.get("permitted_actions", [])
            if "*" not in allowed_acts and action not in allowed_acts:
                continue

            # Check SKU permission
            allowed_skus = win.get("permitted_skus", [])
            if "*" not in allowed_skus and sku_id not in allowed_skus:
                continue

            # Check spend limit
            current_consumed = float(win.get("consumed_spend", 0.0))
            cap = float(win.get("spend_cap", 0.0))
            if (current_consumed + spend_amount) > cap:
                continue

            # Verify cryptographic token
            token = win.get("cryptographic_token", "")
            verify_payload = {k: v for k, v in win.items() if k != "cryptographic_token"}
            expected_sig = self._sign_window(verify_payload)
            if not hmac.compare_digest(token, expected_sig):
                win["status"] = "TAMPER_REVOKED"
                continue

            # Action is authorized under this window!
            return {
                "authorized": True,
                "window_id": win["window_id"],
                "expires_at": win["expires_at"],
                "remaining_budget": round(cap - current_consumed - spend_amount, 2),
                "authorized_by": win.get("authorized_by"),
            }

        return {
            "authorized": False,
            "reason": "No active, non-expired autonomous execution window covers this action and spend amount.",
        }

    def consume_spend(self, window_id: str, spend_amount: float) -> bool:
        """Records consumed spend against the window."""
        with WINDOWS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)

        updated = False
        for win in data.get("active_windows", []):
            if win["window_id"] == window_id:
                win["consumed_spend"] = round(float(win.get("consumed_spend", 0.0)) + spend_amount, 2)
                # Re-sign with updated consumed spend
                verify_payload = {k: v for k, v in win.items() if k != "cryptographic_token"}
                win["cryptographic_token"] = self._sign_window(verify_payload)
                updated = True
                break

        if updated:
            with WINDOWS_FILE.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            self.store.log_audit("WINDOW_SPEND_CONSUMED", {"window_id": window_id, "amount": spend_amount})

        return updated

    def revoke_window(self, window_id: str, reason: str = "Manual operator revocation") -> bool:
        """Revokes an active autonomous execution window immediately."""
        with WINDOWS_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)

        found = False
        for win in data.get("active_windows", []):
            if win["window_id"] == window_id:
                win["status"] = "REVOKED"
                verify_payload = {k: v for k, v in win.items() if k != "cryptographic_token"}
                win["cryptographic_token"] = self._sign_window(verify_payload)
                found = True
                break

        if found:
            with WINDOWS_FILE.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            self.store.log_audit("AUTONOMOUS_WINDOW_REVOKED", {"window_id": window_id, "reason": reason})

        return found
