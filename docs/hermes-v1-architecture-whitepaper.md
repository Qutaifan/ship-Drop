# Hermes-Ecom: Autonomous Sourcing Intelligence & Algorithmic Retail Arbitrage
## Technical Architecture Whitepaper & System Specification (v1.0.0)

**Author:** Ahmad (Founder & Sovereign Operator)  
**System Identity:** Hermes-Ecom  
**Date:** September 2026  
**License:** Free & Open Source (MIT / AGPL-3.0 Engine)  
**Repository Posture:** Production-Hardened, Governance-Gated, Zero-SaaS Overhead  

---

## Executive Summary

**Hermes-Ecom** is an autonomous, multi-agent e-commerce growth engine and algorithmic retail arbitrage operator. Conventional dropshipping architectures suffer from fatal systemic friction: unverified supplier pricing drift, sudden de-minimis regulatory penalties, advertising margin compression, uncoordinated multi-SKU failures, and fragile manual triage.

Hermes-Ecom solves these structural inefficiencies by treating retail arbitrage as a **deterministic, quantitative feedback loop**. The system pairs real-time supplier telemetry with time-series volatility modeling, graph-based network risk propagation, rule-based dynamic pricing, demand velocity forecasting, and cryptographic Founder-gated autonomous execution. 

The entire engine runs under a strict **Zero-SaaS Constraint**—operating locally on consumer hardware and self-hosted infrastructure at **€0 marginal SaaS cost**.

```
                           ┌────────────────────────────────────────────────────────┐
                           │               FOUNDER SOVEREIGN GOVERNANCE             │
                           │  - Cryptographic HMAC Execution Windows               │
                           │  - Manual Triage Gate (auto_drift_actions: false)      │
                           │  - Hard Stop Spend Caps & Instant Circuit Breakers    │
                           └───────────────────────────┬────────────────────────────┘
                                                       │
                                  ┌────────────────────┴────────────────────┐
                                  │                                         │
┌─────────────────────────────────▼──────────────────┐   ┌──────────────────▼────────────────────────────────┐
│             LAYER 5: ECONOMIC OPTIMIZATION         │   │            LAYER 4: NETWORK INTELLIGENCE          │
│ - Rule-Based Dynamic Pricing (FTC Safeguards)      │   │ - Bipartite Supplier Reputation Graph             │
│ - Price Elasticity Curve: Q(P) = Q0 * (P/P0)^(-ε)  │   │ - Warehouse & Carrier Blast Radius Assessment     │
│ - Demand Velocity & Reorder Point (ROP) Engine     │   │ - Multi-SKU Portfolio Rebalancer                  │
│ - Supplier Volume-Tier Negotiation Simulator       │   │ - Multi-Agent Predictive Drift (Collapse Prob)    │
│ - Global Portfolio Capital Allocator               │   │                                                   │
└─────────────────────────────────┬──────────────────┘   └──────────────────┬────────────────────────────────┘
                                  │                                         │
┌─────────────────────────────────▼─────────────────────────────────────────▼────────────────────────────────┐
│                              LAYER 3: SUPPLIER LIFECYCLE STATE MACHINE                                     │
│          [ACTIVE] ──(vol ≥ 0.10)──▶ [WATCHLIST] ──(stab < 0.80)──▶ [DEGRADED]                              │
│             │                                                         │                                    │
│       (stab < 0.70)                                             (stab < 0.70)                              │
│             ▼                                                         ▼                                    │
│          [CRITICAL] ────────────▶ [SUSPENDED / SELL_KILL] ─────────▶ [RETIRED]                             │
└─────────────────────────────────┬─────────────────────────────────────────┬────────────────────────────────┘
                                  │                                         │
┌─────────────────────────────────▼──────────────────┐   ┌──────────────────▼────────────────────────────────┐
│           LAYER 2: TEMPORAL INTELLIGENCE           │   │            LAYER 1: SNAPSHOT INTELLIGENCE         │
│ - 5-Vector Volatility Tracker                      │   │ - Sourcing Ranker (Python + TypeScript)           │
│ - Stability Drift & Volatility Index (σ)           │   │ - Deterministic Stability Score (0.00 - 1.00)     │
│ - Stock Velocity (units/audit)                     │   │ - 4 Operational Sourcing Tiers                    │
│ - Price Inflation Velocity & Defect Acceleration   │   │ - Reconciled True Margin Matrix (EU 2026 Duty)    │
│ - Persistent Time-Series Telemetry Artifacts       │   │ - 80/20 Resilient Multi-Supplier Allocator        │
└────────────────────────────────────────────────────┘   └───────────────────────────────────────────────────┘
```

---

## 1. Core Operating Principles & Governance Invariants

### 1.1 Founder Sovereign Governance
The system operates under the inviolable premise that **the Founder (Ahmad) holds sovereign approval authority over live capital deployment**:
1. **Default Gate**: `auto_drift_actions` remains set to `false`. Automated actions proposing supplier substitutions, marketing halts, or listing changes are queued as trade signals requiring Founder review.
2. **Autonomous Execution Windows**: When operational autonomy is desired, the Founder issues a time-boxed, spend-capped cryptographic grant signed via HMAC-SHA256 (`agency/governance/autonomous_windows.py`). Any action outside the permitted SKU list, exceeding the spend cap, or arriving post-expiration is rejected.
3. **Instant Killswitch**: An operator revocation command immediately halts all automated canary dispatches across the cluster.

### 1.2 The True Margin Matrix & 2026 Regulatory Compliance
Traditional e-commerce margin calculators fail in cross-border commerce by treating VAT as earned revenue and ignoring de-minimis duty elimination. Hermes-Ecom enforces the **True Margin Matrix**:

$$\text{Net Margin} = \left(\frac{\text{Retail}}{1 + \text{VAT}}\right) - (\text{Product Cost} + \text{Shipping} + \text{Import Duty}) - (0.03 \times \text{Gross Retail})$$

* **EU Customs Duty (1 July 2026 reform)**: The historical €150 customs-duty exemption was eliminated on 1 July 2026 and replaced by a **€3 flat duty per customs item** for direct-from-China consignments. Import VAT applies to every shipment.
* **Domestic Warehouse Mandate**: Direct Chinese dropshipping carries €3 duty + import VAT + €2 carrier handling on *every individual consumer package*. Fulfilling from an EU or US domestic warehouse pays duty once upon bulk container import, reducing per-order import duty to **€0.00**. Hermes-Ecom prioritizes verified domestic warehouses (`PREFERRED_DOMESTIC`).
* **The CAC Gate**: Net margin must equal or exceed **$2\times$ the median CPA benchmark (~€21.48 / \$21.48)** and **$\ge 3\times$ COGS**. Items failing this threshold are blocked by `scripts/profitability.py`.
* **Target Retail Band**: Fixed strictly at **€62.00 to €93.00** (approx. \$65 to \$98). Below €62, paid customer acquisition cannot sustain positive unit economics; above \$100, local AI-generated creative experiences an ad-conversion penalty compared to human lifestyle production.

---

## 2. Layered Architecture Specification

### Layer 1: Snapshot Intelligence (Sourcing Ranker & Normalization)
* **Dual-Runtime Engine**: Implemented identically in Python (`agency/core/sourcing_ranker.py`) and TypeScript (`agency/core/sourcing_ranker.ts`) to service both backend CLI workers and Next.js frontend interfaces.
* **Deterministic Stability Score**:
  $$\text{Stability} = (0.40 \cdot S_{\text{price}}) + (0.30 \cdot S_{\text{stock}}) + (0.20 \cdot S_{\text{defect}}) + (0.10 \cdot S_{\text{warehouse}})$$
  * $S_{\text{price}} = \max(0, 1 - 2 \cdot |\Delta P|)$
  * $S_{\text{stock}} = \min(1.0, \text{Stock} / 100)$
  * $S_{\text{defect}} = \max(0, 1 - (\text{Defect Rate} / 10))$
  * $S_{\text{warehouse}} = 1.0 \text{ (Domestic)} \mid 0.5 \text{ (Cross-Border)}$
* **Operational Tiers**:
  * `PREFERRED_DOMESTIC`: Stability $\ge 0.85$, Domestic warehouse, Margin Multiple $\ge 3.0\times$.
  * `QUALIFIED_BACKUP`: Stability $\ge 0.70$, Lead time $\le 7$ days, Margin Multiple $\ge 2.5\times$.
  * `HIGH_RISK_MONITOR`: Stability $0.50\text{--}0.69$, elevated defect rate or price drift.
  * `REJECTED_UNVIABLE`: Stability $< 0.50$ or fails CAC Gate.
* **Resilient Routing (80/20 Rule)**: `SupplierAllocator` automatically distributes order fulfillment 80% to `PREFERRED_DOMESTIC` and 20% to `QUALIFIED_BACKUP` to keep secondary supply chains warm.

### Layer 2: Temporal Intelligence (Volatility & Forecasting)
* **Supplier Volatility Tracker** (`agency/bots/supplier_volatility_tracker.py`):
  * Analyzes historical audits to compute **Stability Drift** ($\Delta \text{Stability}$), **Volatility Index** ($\sigma$), **Stock Velocity** (units consumed per audit interval), **Price Inflation Velocity**, and **Lead Time Inflation**.
  * Emits persistent time-series snapshots to `data/supplier_health/<supplier_id>.timeline.json`.
* **Predictive Drift Engine** (`agency/core/predictive_drift.py`):
  * Projects 7-day stability collapse probability:
    $$P(\text{Collapse}) = \frac{1}{1 + e^{-12 \cdot (0.75 - \hat{s}_{7\text{d}})}}$$
  * Computes runout horizon days:
    $$\text{Runout Days} = \frac{\text{Current Stock}}{|\text{Burn Velocity}|}$$
  * Automatically issues `PREEMPTIVE_SWITCH_URGENT` when collapse probability exceeds 70% or inventory runout drops below 5 days.

### Layer 3: Supplier Lifecycle State Machine
* **Lifecycle Manager** (`agency/core/supplier_lifecycle.py`):
  Enforces formal operational states: `ACTIVE`, `WATCHLIST`, `DEGRADED`, `CRITICAL`, `SUSPENDED`, `RETIRED`.
* **Autonomous Replacement Engine** (`agency/bots/supplier_replacement_engine.py`):
  When a supplier transitions to `CRITICAL` or `SUSPENDED`, the engine automatically:
  1. Identifies the highest-ranked domestic alternative from the ranker.
  2. Runs allocation rebalancing via `SupplierAllocator`.
  3. Computes net margin delta simulation.
  4. Dispatches a cryptographic `sig-supplier-switch-*` trade signal for Founder sign-off.
  5. Falls back to an emergency listing pause (`SELL_KILL`) if zero qualified domestic alternatives exist.
* **Autonomous Canary Scaling** (`agency/governance/execution_gateway.py`):
  * Tier 1 (0–7 days stable): 3 test orders, \$250 spend cap.
  * Tier 2 (8–21 days stable): 5 test orders, \$400 spend cap.
  * Tier 3 (22+ days stable): 10 test orders, \$600 spend cap (`TRUSTED_DOMESTIC`).

### Layer 4: Network Intelligence (Reputation Graph & Portfolio Rebalancing)
* **Supplier Reputation Graph** (`agency/core/reputation_graph.py`):
  Maps catalog relationships across SKUs, Suppliers, Shared Domestic Warehouses, and Logistics Carriers. Computes the **Systemic Exposure Percentage** and blast radius of shared infrastructure failures.
* **Multi-SKU Portfolio Rebalancing** (`agency/bots/portfolio_rebalancer.py`):
  When a shared domestic warehouse or supplier degrades, the rebalancer automatically detects all affected SKUs across the catalog, executes failovers in parallel, calculates the net portfolio margin delta, and logs a coordinated batch audit event.

### Layer 5: Economic Optimization Engine
* **Dynamic Pricing Module** (`agency/core/dynamic_pricing.py`):
  Simulates price elasticity $Q(P) = Q_0 \times (P / P_0)^{-\epsilon}$ across the target retail band (€62–93). Adjusts prices based on inventory scarcity rules while enforcing non-profiling FTC safeguards.
* **Demand Forecasting Module** (`agency/core/demand_forecasting.py`):
  Projects weekly and monthly unit volume from ad spend, CPC, and CVR, and computes the dynamic Reorder Point (ROP).
* **Supplier Negotiation Simulator** (`agency/bots/negotiation_simulator.py`):
  Models 4 volume-tier discounting curves (up to 18.5% wholesale discount) and generates copy-ready supplier pitch briefs.
* **Global Portfolio Optimizer** (`agency/bots/global_portfolio_optimizer.py`):
  Aggregates macro portfolio revenue, net margin, and blended COGS multiples, dynamically allocating 50% of ad capital to the top profit-generating SKU, 30% to the runner-up, and 20% across test lines.

---

## 3. Infrastructure & Deployment Topology

### 3.1 Zero-SaaS Local Stack
All infrastructure runs on existing self-hosted hardware (`ahmad-thinkbook`, Ubuntu 24/7 server; `hq-2`, Windows RTX 4060 GPU workstation):

| Component | Technology | Purpose | Marginal Cost |
|---|---|---|---|
| **Commerce Core** | Medusa v2 (MIT) | Headless store, promotions, order management | €0.00 |
| **Storefront** | Next.js 15+ (MIT) | 9:16 vertical video mobile landing pages, Stripe Express | €0.00 |
| **Relational DB** | PostgreSQL 16 | ACID catalog, inventory, and order storage | €0.00 |
| **Cache / Queue** | Valkey 7 (BSD-3) | In-memory pub/sub, worker task queues | €0.00 |
| **Object Store** | Cloudflare R2 | Asset storage (10GB free tier, zero egress fees) | €0.00 |
| **Public Ingress** | Cloudflare Tunnel | Commercial-use TLS tunnel; no open ports | €0.00 |
| **Telemetry** | Umami + SQLite | Cookieless GDPR analytics and cryptographic ledger | €0.00 |
| **Video Rendering** | Remotion + ComfyUI | Programmatic 9:16 vertical ad generation on RTX 4060 | €0.00 |

### 3.2 Systemd Daemon Execution
The autonomous worker runs as a dedicated, sandboxed system service (`infra/systemd/hermes-worker.service`) managed by `systemd` with daily log rotation (`infra/systemd/hermes-worker.logrotate`).

---

## 4. Verification & Safety Posture

The codebase maintains a zero-tolerance defect policy verified through automated multi-layered test suites:

* **Workspace Unit & Integration Tests**: 56/56 passing tests across rankers, allocators, volatility trackers, lifecycle state machines, predictive drift engines, dynamic pricing, and portfolio optimizers.
* **Contract Schema Validation**: 8/8 strict JSON schemas validated with `additionalProperties: false`.
* **Negative Defect Selftest**: `python scripts/selftest.py` catches 24/24 injected architectural and margin errors.
* **Smoke Suite**: `npm run agency:smoke` validates end-to-end verification, reconciliation, drift detection, history, and feature flag toggling.

---

## 5. Next Horizon: Phase-6 Live Sourcing Pilot

With the architecture verified and locked, Hermes-Ecom proceeds to **Phase-6 Production Data Wiring**:
1. Live Meta Ad Library commercial ad scraping across EU/UK DSA endpoints.
2. Direct API inventory synchronization with CJdropshipping domestic warehouses.
3. Automated Medusa v2 draft product creation and live Stripe payment test orders.
