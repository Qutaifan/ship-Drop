"""Slack & Webhook Notification Dispatcher for Supplier Drift Signals."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, Optional


class DriftNotifier:
    def __init__(self, webhook_url: Optional[str] = None) -> None:
        self.webhook_url = webhook_url or os.getenv("HERMES_SLACK_WEBHOOK_URL", "")

    def format_slack_card(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """Formats a drift signal into an actionable Slack Block Kit payload."""
        sig_id = signal.get("signal_id", "sig-unknown")
        cid = signal.get("candidate_id", "cand-unknown")
        prod = signal.get("product_name", "Unknown Product")
        action = signal.get("recommended_action", signal.get("action_plan", {}).get("recommended_action", "Review proposal"))
        severity = signal.get("severity", "HIGH")
        flags = signal.get("flags", [])
        flags_text = " • " + "\n • ".join(flags) if flags else "Supplier parameters deviated from baseline."

        color = "#D9381E" if severity == "HIGH" else "#E5A823"

        return {
            "attachments": [
                {
                    "color": color,
                    "blocks": [
                        {
                            "type": "header",
                            "text": {
                                "type": "plain_text",
                                "text": f"🚨 Supplier Drift Alert: {prod}",
                                "emoji": True,
                            },
                        },
                        {
                            "type": "section",
                            "fields": [
                                {"type": "mrkdwn", "text": f"*Candidate:* `{cid}`"},
                                {"type": "mrkdwn", "text": f"*Severity:* `{severity}`"},
                                {"type": "mrkdwn", "text": f"*Signal ID:* `{sig_id}`"},
                                {"type": "mrkdwn", "text": f"*Action:* *{action}*"},
                            ],
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": f"*Drift Triggers:*\n{flags_text}",
                            },
                        },
                        {
                            "type": "context",
                            "elements": [
                                {
                                    "type": "mrkdwn",
                                    "text": f"🛠️ *Quick Approve:* `python -m agency.cli approve-signal {sig_id} --action APPROVE_SUPPLIER_SWITCH --actor Founder`",
                                }
                            ],
                        },
                    ],
                }
            ]
        }

    def dispatch(self, signal: Dict[str, Any]) -> bool:
        """Dispatches notification to configured webhook. Returns True on success."""
        payload = self.format_slack_card(signal)

        if not self.webhook_url:
            # Dry-run / terminal display if webhook URL is not set
            print("\n[Notifier: Webhook URL not configured (dry-run mode)]")
            print(f"  Alert: {signal.get('product_name')} -> {signal.get('signal_id')}")
            print(f"  Command: python -m agency.cli approve-signal {signal.get('signal_id')} --action APPROVE_SUPPLIER_SWITCH")
            return True

        req_data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.webhook_url,
            data=req_data,
            headers={"Content-Type": "application/json"},
        )

        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status in (200, 204)
        except Exception as e:
            print(f"⚠️ Failed to dispatch Slack notification: {e}")
            return False
