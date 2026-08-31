# US Market - True Margin Matrix (USD)

## Formula (corrected 2026-08-30, US variant)

```
Net Margin = (Retail / (1 + State_Tax)) 
           - (Product_Cost + Shipping + Duty + 3PL_Fee)
           - (0.029 * Retail + 0.30)
```

**Key differences from EU formula**:
1. State tax replaces EU VAT — remitted, never earned
2. Duty: Section 301 tariff (often 25%) on China-origin goods; 0% if from US 3PL bulk import
3. 3PL fee: US 3PL fulfillment (~$3-7/order), 0 if direct-from-China (but then high duty)
4. Payment fee: 2.9% + $0.30 on GROSS retail (sales-tax-inclusive)
5. No IOSS/OSS equivalent (sales tax state-by-state)

## US-Specific Heuristic (PROVISIONAL)
- US products need higher absolute retail ($68-105) to clear 2x CAC gate ($23.50 benchmark)
- US 3PL adds $3-7/order vs. €0-2 in EU warehouse — adjust target margin accordingly
- Sales tax is state-specific; use worst-case state for safe margin calculation

## Worked Examples

### Example 1: Direct from China (NO 3PL) — SHOULD FAIL
```
Retail:        $49.00 (sales-tax-inclusive, e.g. 7% state)
State tax:     7.0%  → $3.20
Product cost:  $8.00 (FOB China)
Duty:          25% Section 301 → $2.00
Shipping:      $3.10 (direct from China)
3PL:           $0.00 (direct)
Payment fee:   2.9% + $0.30 = $1.72
```

**Net Margin** = $49/1.07 - ($8 + $3.10 + $2) - $1.72 = $45.79 - $13.10 - $1.72 = **$30.97**

**Gate check**:
- 2x CAC: $30.97 ≥ $47.00 ❌ **FAIL** (US has higher CPMs, $47 minimum needed)
- 3x COGS: $30.97 ≥ $24.00 ✓
- Margin floor: $30.97 ≥ $20.00 ✓
- Retail band: $49 < $68 ❌ **FAIL** (too low for US market)

**Verdict**: FAIL on retail band AND 2x CAC gate. Direct-from-China is dead in the US at $49.

### Example 2: US 3PL with $85 retail — SHOULD PASS
```
Retail:        $85.00
State tax:     7.0% (CA-style) → $5.56
Product cost:  $12.00 (FOB China, duty paid on bulk import to US 3PL)
Duty:          $0.00 (already paid on bulk import to US 3PL)
Shipping:      $5.50 (US 3PL outbound)
3PL:           $3.50 (pick/pack fee)
Payment fee:   2.9% + $0.30 = $2.77
```

**Net Margin** = $85/1.07 - ($12 + $5.50 + $0 + $3.50) - $2.77 = $79.44 - $21.00 - $2.77 = **$55.67**

**Gate check**:
- 2x CAC: $55.67 ≥ $47.00 ✓
- 3x COGS: $55.67 ≥ $36.00 ✓
- Margin floor: $55.67 ≥ $20.00 ✓
- Retail band: $85 in [$68, $105] ✓

**Verdict**: PASS. Launch with confidence.

### Example 3: US 3PL, $45 retail — SHOULD FAIL
```
Retail:        $45.00
State tax:     7.0% → $2.94
Product cost:  $6.00
Duty:          $0 (paid in bulk)
Shipping:      $4.50
3PL:           $3.00
Payment fee:   2.9% + $0.30 = $1.61
```

**Net Margin** = $45/1.07 - ($6 + $4.50 + $0 + $3) - $1.61 = $42.06 - $13.50 - $1.61 = **$26.95**

**Gate check**:
- 2x CAC: $26.95 < $47.00 ❌ **FAIL**
- Retail band: $45 < $68 ❌ **FAIL**

**Verdict**: FAIL. US market requires higher retail due to higher CAC and 3PL costs.

## State Tax Variants

| Scenario | State | Rate | Notes |
|---|---|---|---|
| Conservative safe calc | CA + LA | 9.5% | Highest large market |
| National average | weighted | 7.0% | Use for initial screen |
| Best case (no nexus) | TX (no local) | 6.25% | Pre-nexus only |
| Pure base | AK/MT/NH/OR/DE | 0% | Live here for tax savings |
| After nexus triggered | varies | state rate | Remit from day 1 |

**Recommendation**: Calculate with 7.5% state tax for safe margin. If product passes there, US market is viable.

## Bulk Import vs Direct Ship

**Bulk Import to US 3PL** (the only viable path for China-origin):
- Pay Section 301 duty once on container/pallet
- 3PL stores inventory
- Per-order: pick + pack + ship domestic (no additional duty)
- Per-order cost: $3-7 (3PL fee) + $4-6 (US shipping)
- Lead time: 1-3 days to US customer

**Direct Ship from China** (NOT viable post-2025):
- Pay Section 301 duty on every order (no de minimis)
- 25% additional tariff on HTS-covered items
- MPF + HMMPF per shipment
- Lead time: 7-21 days
- Customer experience: poor (long waits, return friction)

**Verdict**: US 3PL is mandatory. Build this cost into the margin math.

## Scripts Update Plan

1. **scripts/margin_solver.py** — add --market us flag with state_tax_rate, duty_pct, 3pl_fee args
2. **scripts/profitability.py** — add US CAC benchmark ($23.50 vs EUR 21.48)
3. **scripts/ad_library.py** — keep EU-only, add US manual template at `scripts/ad_library_us_manual.md`

## References
- AGENTS.md PROTOCOL-01 (lines 49-68)
- AGENTS.md Sourcing & Regulatory Compliance (lines 36-43)
- US-MARKET.md (this directory)
- US-VALIDATION.md (this directory)
- learnings/HEURISTICS.md (apply US heuristics when present)
