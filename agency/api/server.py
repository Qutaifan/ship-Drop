"""Hermes Local Telemetry & Command API Server: Zero-SaaS HTTP bridge for Hermes Desktop."""
from __future__ import annotations

import datetime
import json
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional

from agency.bots.global_portfolio_optimizer import GlobalPortfolioOptimizer
from agency.bots.supplier_volatility_tracker import SupplierVolatilityTracker
from agency.core.competition_matrix import SupplierCompetitionMatrix
from agency.core.reputation_graph import SupplierReputationGraph
from agency.core.sourcing_ranker import SourcingRanker
from agency.core.store import Store
from agency.governance.autonomous_windows import AutonomousWindowManager

ROOT = Path(__file__).resolve().parents[2]


class HermesAPIHandler(BaseHTTPRequestHandler):
    store = Store()

    # Collaborators resolve from the *current* `store` on each access rather than
    # capturing it at class-definition time. Bound as class attributes they each
    # held the import-time Store, so assigning HermesAPIHandler.store — which is
    # how the handler is pointed at a different database — moved only the
    # endpoints using self.store directly. /telemetry/overview and
    # /economic/portfolio go through the optimizer and so kept reading the real
    # data directory, whatever store was injected.
    @property
    def window_mgr(self) -> AutonomousWindowManager:
        return AutonomousWindowManager(self.store)

    @property
    def optimizer(self) -> GlobalPortfolioOptimizer:
        return GlobalPortfolioOptimizer(self.store)

    @property
    def rep_graph(self) -> SupplierReputationGraph:
        return SupplierReputationGraph(self.store)

    @property
    def vol_tracker(self) -> SupplierVolatilityTracker:
        return SupplierVolatilityTracker(self.store)

    def _send_json(self, status_code: int, data: Any) -> None:
        payload = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self) -> None:
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)

        try:
            # 1. Five Intelligence Rings & System Vitals Overview
            if path == "/api/v1/telemetry/overview":
                port_res = self.optimizer.optimize_portfolio(total_monthly_marketing_budget=3000.0)
                graph_res = self.rep_graph.build_network_graph()
                win_status = self.window_mgr.is_action_authorized("CANARY_ORDER_DISPATCH", "any", 0.0)

                overview = {
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "system_state": "OPTIMAL",
                    "intelligence_rings": {
                        "ring_1_stability": {
                            "name": "Sourcing Stability Ring",
                            "value": port_res.get("portfolio_average_stability", 0.94),
                            "status": "GREEN" if port_res.get("portfolio_average_stability", 0) >= 0.85 else "YELLOW",
                        },
                        "ring_2_volatility": {
                            "name": "Volatility Drift Ring",
                            "value": 0.04,
                            "status": "GREEN",
                        },
                        "ring_3_lifecycle": {
                            "name": "Lifecycle State Ring",
                            "value": "ACTIVE",
                            "status": "GREEN",
                        },
                        "ring_4_network": {
                            "name": "Network Exposure Ring",
                            "value": f"{graph_res.get('node_count', 0)} Nodes",
                            "status": "GREEN",
                        },
                        "ring_5_economic": {
                            "name": "Economic Optimization Ring",
                            "value": f"${port_res.get('portfolio_monthly_net_margin', 0):,.2f}",
                            "status": "BLUE" if win_status.get("authorized") else "GREEN",
                        },
                    },
                    "system_vitals": {
                        "monthly_gross_revenue": port_res.get("portfolio_monthly_gross_revenue", 0.0),
                        "monthly_net_margin": port_res.get("portfolio_monthly_net_margin", 0.0),
                        "blended_cogs_multiple": port_res.get("blended_cogs_multiple", 0.0),
                        "autonomous_window_active": win_status.get("authorized", False),
                        "active_nodes": graph_res.get("node_count", 0),
                    },
                }
                self._send_json(200, overview)
                return

            # 2. SKU Intelligence Cards Grid
            if path == "/api/v1/sourcing/skus":
                candidates = self.store.list_candidates()
                skus_data = []
                for c in candidates:
                    cid = c.get("candidate_id", "")
                    matrix = SupplierCompetitionMatrix.generate_matrix(cid, self.store)
                    skus_data.append(matrix)
                self._send_json(200, {"sku_count": len(skus_data), "skus": skus_data})
                return

            # 3. Supplier Cockpit
            if path.startswith("/api/v1/sourcing/supplier/"):
                sup_id = path.replace("/api/v1/sourcing/supplier/", "")
                cid = query.get("candidate", [None])[0]
                analysis = self.vol_tracker.analyze_supplier(supplier_id=sup_id, candidate_id=cid)
                self._send_json(200, analysis)
                return

            # 4. Network Graph 3D Topology
            if path == "/api/v1/network/graph":
                graph_data = self.rep_graph.build_network_graph()
                self._send_json(200, graph_data)
                return

            # 5. Economic Brain & Portfolio
            if path == "/api/v1/economic/portfolio":
                budget = float(query.get("budget", [3000.0])[0])
                econ_data = self.optimizer.optimize_portfolio(total_monthly_marketing_budget=budget)
                self._send_json(200, econ_data)
                return

            # 6. Autonomous Windows Monitor
            if path == "/api/v1/governance/windows":
                from agency.config.settings import WINDOWS_FILE
                windows_file = WINDOWS_FILE
                wins = []
                if windows_file.exists():
                    with windows_file.open("r", encoding="utf-8") as f:
                        wins = json.load(f).get("active_windows", [])
                self._send_json(200, {"active_windows": wins})
                return

            # 7. Multi-Agent Replay Feed Log
            if path == "/api/v1/telemetry/replay":
                audit_logs = self.store.get_audit_trail(limit=50)
                self._send_json(200, {"events_count": len(audit_logs), "events": audit_logs})
                return

            # 8. Live Funnel Conversion Telemetry
            if path == "/api/v1/telemetry/conversion":
                from agency.ingestion.umami_telemetry_ingestion import UmamiTelemetryIngestion
                cid = query.get("candidate", ["cand-cj-sku-magnetic-cord-6p"])[0]
                funnel = UmamiTelemetryIngestion(self.store).get_sku_funnel_summary(cid)
                self._send_json(200, funnel)
                return

            # 9. Real Empirical Elasticity Curves
            if path == "/api/v1/economic/elasticity":
                from agency.ingestion.umami_telemetry_ingestion import UmamiTelemetryIngestion
                cid = query.get("candidate", ["cand-cj-sku-magnetic-cord-6p"])[0]
                funnel = UmamiTelemetryIngestion(self.store).get_sku_funnel_summary(cid)
                self._send_json(200, {
                    "candidate_id": cid,
                    "empirical_elasticity": funnel["empirical_elasticity_coefficient"],
                    "price_cohorts": funnel["price_cohorts"],
                    "real_cvr_percent": funnel["real_conversion_rate_percent"],
                    "profit_per_visitor_usd": funnel["profit_per_visitor_usd"],
                })
                return

            self._send_json(404, {"error": "Endpoint not found"})

        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def do_POST(self) -> None:
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        try:
            if path == "/api/v1/governance/window/grant":
                actor = payload.get("actor", "Founder")
                hours = float(payload.get("hours", 2.0))
                cap = float(payload.get("spend_cap", 500.0))
                win = self.window_mgr.grant_window(founder_actor=actor, duration_hours=hours, spend_cap=cap)
                self._send_json(200, win)
                return

            if path == "/api/v1/governance/window/revoke":
                win_id = payload.get("window_id", "")
                ok = self.window_mgr.revoke_window(win_id)
                self._send_json(200, {"success": ok, "window_id": win_id})
                return

            if path == "/api/v1/storefront/sync":
                from agency.ingestion.medusa_storefront_sync import MedusaStorefrontSync
                cid = payload.get("candidate_id", "cand-cj-sku-magnetic-cord-6p")
                publish = bool(payload.get("publish", False))
                sync_res = MedusaStorefrontSync(self.store).sync_candidate(candidate_id=cid, publish=publish)
                self._send_json(200, sync_res)
                return

            if path == "/api/v1/simulation/buyer-journey":
                from agency.bots.fake_buyer_journey import FakeBuyerJourneySimulator
                cid = payload.get("candidate_id", "cand-cj-sku-magnetic-cord-6p")
                cust = payload.get("customer_name", "Marcus Vance (Synthetic Buyer)")
                sim_res = FakeBuyerJourneySimulator(self.store).simulate_order(candidate_id=cid, customer_name=cust)
                self._send_json(200, sim_res)
                return

            # Stripe Sandbox Webhook Receiver
            if path == "/api/v1/webhooks/stripe":
                from agency.ingestion.stripe_telemetry_ingestion import StripeTelemetryIngestion
                stripe_engine = StripeTelemetryIngestion(self.store)
                res = stripe_engine.process_event(payload)
                self._send_json(200, res)
                return

            # Umami Cookieless Event Recorder
            if path == "/api/v1/telemetry/umami-event":
                from agency.ingestion.umami_telemetry_ingestion import UmamiTelemetryIngestion
                cid = payload.get("candidate_id", "cand-cj-sku-magnetic-cord-6p")
                evt = payload.get("event_type", "pageview")
                price = float(payload.get("price_point", 62.99))
                sess = payload.get("session_id")
                ref = payload.get("referrer", "tiktok_ads")
                res = UmamiTelemetryIngestion(self.store).record_event(
                    candidate_id=cid, event_type=evt, price_point=price, session_id=sess, referrer=ref,
                )
                self._send_json(200, res)
                return

            self._send_json(404, {"error": "Endpoint not found"})

        except Exception as e:
            self._send_json(500, {"error": str(e)})


def run_hermes_api_server(host: str = "127.0.0.1", port: int = 8080) -> None:
    """Starts the multi-threaded Hermes Telemetry HTTP Server."""
    server_address = (host, port)
    httpd = ThreadingHTTPServer(server_address, HermesAPIHandler)
    print(f"\n🚀 Hermes Telemetry API Server online at http://{host}:{port}")
    print(f"   Serving 13 live intelligence endpoints to Hermes Desktop...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Hermes Telemetry API Server stopping...")
        httpd.server_close()
