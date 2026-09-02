# Founder Approval & Signal Triage Guide

**Owner:** Ahmad (Founder & Sovereign Execution Authority)  
**Framework:** Hermes | Governance Tier 3 & 4  

---

## 1. Governance Principles
- Autonomous bots produce **proposals only**.
- No ad spend, supplier order submissions, or public storefront publishes can execute without an explicit cryptographic approval token signed by Ahmad.
- Replay protection enforces that each token can only be consumed once.

---

## 2. Signal Types & Triage Priorities

| Signal Type | Priority | Description | Required Decision |
|---|---|---|---|
| **`BUY`** | High | Candidate cleared 4-D Opportunity Score ($\ge 75$), verified domestic supplier ($\ge 0.85$ stability), and positive unit economics. | Authorize 7-day creative test budget (typically \$200–\$350). |
| **`SUPPLIER_SWITCH`** | High | Domestic inventory depleted or supplier drift detected. Viable demand exists but supplier requires migration. | Approve rerouting to secondary domestic warehouse. |
| **`SELL_KILL`** | Critical | Product unit economics compressed ($<\$12$), or severe drift detected ($>20\%$ cost hike), or market oversaturated ($>15$ advertisers). | Kill campaign / archive candidate to protect ad budget. |
| **`TREND_ALERT`** | Low | Consumer momentum detected on social/search, awaiting catalog cost verification. | Informational; monitor category ad volume. |

---

## 3. Signal Payload Schema

When inspecting a signal via CLI (`python -m agency.cli signals`) or automated webhooks:

```json
{
  "signal_id": "sig-supplier-drift-cand-cj-sku-magnetic-cord-6p-4a1b2c",
  "signal_type": "SUPPLIER_SWITCH",
  "candidate_id": "cand-cj-sku-magnetic-cord-6p",
  "product_name": "Magnetic Cable Organizer 6-Pack Desk Clips",
  "target_market": "US",
  "confidence": "high",
  "scores": {
    "profit_score": 50.0,
    "risk_score": 75.0,
    "trend_score": 60.0,
    "opportunity_score": 45.0,
    "supplier_score": 35.0
  },
  "hypothesis": {
    "predicted_ctr_percent": 2.0,
    "predicted_cvr_percent": 2.0,
    "predicted_cpa": 15.00,
    "predicted_net_margin": 10.00,
    "target_ad_budget": 0.0,
    "statement": "Supplier drift detected: STOCK_DEPLETED: Warehouse stock has dropped to 12 units. Stability score: 0.35."
  },
  "action_plan": {
    "execution_tier": 3,
    "recommended_action": "Switch supplier immediately to an authorized domestic warehouse.",
    "target_ad_budget": 0.0,
    "creative_hooks": [
      "Problem Hook: Halt ad spend until supplier switch is executed.",
      "Transformation Hook: Re-route fulfillment to secondary domestic warehouse.",
      "Lifestyle Hook: Update catalog stock parameters to domestic inventory."
    ],
    "contingency_rule": "Auto-pause ad campaign immediately upon supplier drift detection."
  },
  "approval_status": "PENDING_FOUNDER_REVIEW"
}
```

---

## 4. Founder Email / Push Notification Template

```
Subject: [HERMES ACTION REQUIRED] Trade Proposal: {signal_type} — {product_name}

Ahmad,

Hermes Intelligence Bots have emitted a trade recommendation requiring your sign-off:

Product: {product_name} ({candidate_id})
Signal:  {signal_type} (Confidence: {confidence})
Market:  {target_market}

Scores:
  • Opportunity Score : {opportunity_score} / 100
  • Profit Score      : {profit_score} / 100
  • Risk Score        : {risk_score} / 100
  • Supplier Stability: {stability_score} / 1.00

Forecast & Economics:
  • Net Margin        : ${predicted_net_margin}
  • Target CPA        : ${predicted_cpa}
  • Predicted CTR/CVR : {predicted_ctr}% / {predicted_cvr}%
  • Target Ad Budget  : ${target_ad_budget}

Recommended Action:
  {recommended_action}

To review and authorize:
  python -m agency.cli approve {signal_id} --by Ahmad

To reject:
  python -m agency.cli reject {signal_id} --reason "Alternative supplier preferred"
```

---

## 5. Escalation & Auto-Pause SLA
- **Target SLA**: 24 hours from signal emission to Founder decision.
- **Auto-Pause Safeguard**: If a product has active live campaigns and `STOCK_DEPLETED` (<10 units) or `WAREHOUSE_RELOCATION` occurs, ad spend is automatically halted via `contingency_rule` to prevent customer unfulfilled order backlogs.
