# Hermes Sourcing Agent: Metrics Mapping & Scoring Formulas

**Framework:** Hermes-Ecom  
**Document Purpose:** Defines the explicit mapping between sourcing intelligence metrics and the underlying JSON schema fields, accompanied by the deterministic scoring engines used to rank suppliers and detect supply chain degradation.

---

## 1. Metrics to Schema Field Mapping (`schemas/supplier_verification.schema.json`)

| Sourcing Intelligence Metric | Exact Schema Property | Data Type | Validation Bounds / Allowed Values | Strategic Importance |
|---|---|---|---|---|
| **Verified Landed Cost** | `verified_product_cost` + `verified_shipping_cost` | `number` | Minimum: `0.00` | Base denominator for all unit margin, COGS multiple, and break-even CPA math. |
| **Product Unit Cost Drift** | `price_drift_percent` | `number` | Float (e.g. `0.08` for $+8\%$) | Detects stealth margin erosion or supplier price volatility. |
| **Domestic Warehouse Stock** | `stock_level` | `integer` | Minimum: `0` | Eliminates stockouts; $<30$ units immediately trips `STOCK_DEPLETED`. |
| **Warehouse Origin & Routing** | `warehouse_country`, `warehouse_type` | `string` | `"domestic"`, `"international_transit"` | Governs 2026 EU anti-de-minimis customs duty (€3 flat if non-EU vs €0 domestic). |
| **Fulfillment Carrier & Method** | `shipping_method` | `string` | `"USPS"`, `"UPS"`, `"FedEx"`, `"DHL"`, `"EU DPD"`, `"CN ePacket"`, `"other"` | Dictates freight reliability and customer delivery satisfaction. |
| **Lead Time Window** | `lead_days_min`, `lead_days_max` | `integer` | Minimum: `1` | Affects return rates; $>7$ days trips `LEAD_TIME_INFLATION`. |
| **Packaging Class & Uplift** | `packaging_type` | `string` | `"polybag"`, `"bubble_mailer"`, `"kraft_box"`, `"custom_box"` | Informs packaging cost uplift (+\$0.00 to +\$0.45) and damage risk during transit. |
| **Quality & Defect Ratio** | `defect_rate_percent` | `number` | `0.0` to `100.0` | Directly impacts refund provisions and chargeback liabilities. |
| **Supplier Feed Reliability** | `verification_confidence` | `number` | `0.0` to `1.0` | Down-weights unverified or scraping feeds; $<0.30$ trips `SUPPLIER_API_SILENCE`. |
| **Supplier Stability Score** | `stability_score` | `number` | `0.0` to `1.0` | Primary composite rank metric used for prioritization and canary selection. |
| **Verification Status** | `status` | `string` | `"VERIFIED_PASS"`, `"DRIFT_DETECTED"`, `"OUT_OF_STOCK"`, `"WAREHOUSE_MISMATCH"`, `"API_SILENCE"`, `"SKU_FRAGMENTATION"` | Discrete state flag dictating autonomous signal routing and triage urgency. |
| **Cryptographic Provenance** | `hmac_signature` | `string` | 64-char Hex Digest | Guarantees tamper-evident provenance across distributed workers. |

---

## 2. Deterministic Mathematical Formulas

### A. Supplier Stability Score Formula (`compute_stability_score`)
Evaluates supplier reality across four weighted pillars:
$$\text{Stability} = 0.4 \times (1 - |\text{price\_drift}|) + 0.3 \times \min\left(1.0, \frac{\text{stock\_level}}{200}\right) + 0.2 \times \max\left(0.0, 1 - \frac{\text{defect\_rate}}{10}\right) + 0.1 \times \mathbb{I}(\text{domestic})$$

- **Pillar 1 (40% Weight): Price Consistency**  
  Penalizes any variance between quoted sourcing cost and verified live catalog costs.
- **Pillar 2 (30% Weight): Inventory Depth**  
  Full credit requires at least 200 units on hand in the fulfillment warehouse.
- **Pillar 3 (20% Weight): Defect Immunity**  
  A defect rate of $0\%$ earns full score; any defect rate exceeding $10\%$ drops this component to $0.0$.
- **Pillar 4 (10% Weight): Domestic Fulfillment**  
  Awards $0.10$ if fulfillment originates from verified domestic soil (US or EU destination).

### B. Landed Cost & Margin Reconciliation Formula (`reconcile_margins`)
Enforces ex-VAT reality and carrier buffers:
$$\text{Buffered Shipping} = \text{Verified Shipping} \times (1 + \text{Volatility Buffer})$$
$$\text{Total Landed Cost} = \text{Verified Product Cost} + \text{Buffered Shipping} + \text{Duty} + \text{Packaging Uplift}$$
$$\text{Net Margin} = \frac{\text{Retail}}{1 + \text{VAT}} - \text{Total Landed Cost} - (0.03 \times \text{Retail}) - \text{Fixed Deductions}$$

- **Shipping Volatility Buffer**: Defaults to $+4\%$ to absorb fuel surcharges and dimensional adjustments.
- **Duty**: €3.00 flat per non-EU import consignment (effective July 1, 2026); €0.00 for domestic EU warehouses.
- **Fixed Deductions**: Returns allowance ($4\%$), customer support allocation (\$0.80), and payment processing ($3\%$).

### C. Margin Compression Decision Rules
The engine automatically flags `MARGIN_COMPRESSED` if any of three tripwires fire:
1. **Absolute Margin Loss**: $\text{Net Margin}_{\text{reconciled}} - \text{Net Margin}_{\text{initial}} \le -\$2.00$
2. **COGS Multiple Collapse**: Initial multiple $\ge 2.0\times\text{COGS}$ and reconciled multiple drops $< 2.0\times\text{COGS}$.
3. **Unviable Net Margin Floor**: Reconciled net margin drops below $\$10.00$ per unit.

### D. Actionability Score Formula (Drift Urgency Metric)
Calculates signal priority ($0.0\text{--}100.0$) when routing proposals to the Founder queue:
$$\text{Actionability Score} = \min\left(100.0, \text{Severity Weight} \times (1.0 - \text{Stability Score}) \times 100 \times \left(1.0 + \frac{|\Delta\text{Margin}|}{\text{Retail}}\right)\right)$$
- **Severity Weight**: `HIGH` = $1.2$, `MEDIUM` = $1.0$, `LOW` = $0.7$
- High delta and low stability escalate triage priority directly to the top of Ahmad's approval queue.
