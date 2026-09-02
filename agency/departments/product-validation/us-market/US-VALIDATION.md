# US Market - Product Validation Rules

## Critical Difference from EU
Per AGENTS.md: **The Meta Ad Library API does not return commercial US ads**. EU/UK is automatable; US requires manual counting in the web UI. This is a hard constraint that determines workflow.

## PROTOCOL-01 US Adaptation

### Step 1: Pre-screen (OBSERVE)
Same as EU: `python3 scripts/demand_screen.py --product "X" --market us`

### Step 2: Competitor Validation (MANUAL)
**No automation possible** for US commercial ad counting.

**Procedure** (record in `reports/YYYY-MM-DD-us-ad-library-manual-<product>.md`):
1. Open facebook.com/ads/library/?active_status=active&ad_type=all&country=US
2. Search exact product name + 2-3 feature keywords
3. **Require**: 5-10 distinct page names running ads
4. **Require**: 3+ ads active 30+ days
5. Record: page name, page likes, ad count, first-seen, last-seen, ad copy snippets
6. Repeat on TikTok Creative Center (US filter) and Google Shopping search

**Output format** (paste into PROTOCOL-01 report):
```
US Competitor Check:
- 7 distinct advertisers in Meta Ad Library
- 4 ads active 30+ days
- Top competitor: [name] (15 active ads, 50K page likes, 60+ day run)
- TikTok CC: 3 trending hashtags for this category
- Google Shopping: $X avg price, Y competitors listed
```

### Step 3: True Margin Matrix (USD, US Tax)
Use the formula in `us-market/US-MARKET.md`:
```
Net Margin = (Retail / (1 + State_Tax)) 
           - (Product_Cost + Shipping + Duty + 3PL_Fee + Sales_Tax_Remit_Cost)
           - (0.029 * Retail + 0.30)  // payment fee on gross
```

**Mandatory fields**:
- `retail` (USD, sales-tax-inclusive at checkout)
- `state_tax_rate` (0.0-0.10, varies by state)
- `product_cost` (FOB China or landed US)
- `shipping` (US domestic, $3-7 typical)
- `duty` (% of product_cost OR fixed $)
- `3pl_fee` (Amazon FBA, ShipBob, etc.)
- `payment_fee` (calculated: 2.9% × retail + $0.30)

### Step 4: CAC Gate
- Median CPA benchmark: **$23.50** (TikTok US median per AGENTS.md calibration)
- Net margin must be ≥ **2x $23.50 = $47.00** per sale
- 3x COGS gate still applies

### Step 5: Target Retail Band
- **USD $68 - $105** gross retail
- Below $68: 2x CAC gate unreachable at typical margin structures
- Above $105: AI creative inversion (ROAS 3.1x vs 3.7x human)

## US-Specific Heuristics to Apply

Read `learnings/HEURISTICS.md` first. Apply:
- H-001 (saturated viral novelties under €30 fail) — also applies to <$30 USD products
- Any new US-specific heuristics as they accumulate

## Output: US Product Brief Format
```markdown
# US Market Brief: <Product Name>

## Validation Date: YYYY-MM-DD
## Validator: Agency Product Validation

### Demand (Pre-screen)
- YouTube median views: X
- Short-form share: Y%
- Skeptic ratio: Z%

### Competition (Manual Ad Library)
- Meta Ad Library: N distinct advertisers
- Active 30+ days: M
- TikTok Creative Center: P trending hashtags
- Google Shopping: Q listed competitors

### True Margin Matrix (USD)
| Input | Value |
|---|---|
| Retail | $85.00 |
| State tax (TX 6.25%) | $5.31 |
| Product cost | $12.00 |
| Duty (25% Section 301) | $3.00 |
| Shipping (US 3PL) | $5.50 |
| 3PL fee | $3.50 |
| Payment fee (2.9% + $0.30) | $2.77 |
| **Net margin** | **$52.92** |

### Gate Results
- [x] 6-criteria: 6/6 passed
- [x] CAC gate: $52.92 ≥ $47.00 (2x benchmark) ✓
- [x] Margin floor: $52.92 > $20.00 ✓
- [x] 3x COGS: $52.92 > $36.00 ✓
- [x] Retail band: $85 in [$68, $105] ✓

### Verdict: LAUNCH (US)
### Hypothesis (numeric)
- Predicted CTR: 1.8% (TikTok US)
- Predicted CVR: 2.2%
- Predicted ROAS: 3.4x
- Predicted net margin/sale: $52.92
- Discount by running bias: n/a (no US CTR history yet)
```

## Script Updates Needed

The existing `scripts/margin_solver.py` is EUR-only. US variant needed:
- New: `scripts/margin_solver_us.py` (or parameterize with --market us)
- Inputs: state_tax_rate, duty_pct, 3pl_fee
- Output: net_margin_usd

The existing `scripts/ad_library.py` is EU-only by API design. For US, use:
- `scripts/ad_library_manual.py` (record + score manual count)
- Or just the template in `reports/_TEMPLATE.md` — manual paste

## State Tax Quick Reference (top 10 states by e-com sales)
| State | Rate | Notes |
|---|---|---|
| California | 7.25-10.50% | District taxes add up to 2.5% |
| Texas | 6.25% | Local up to 2% |
| New York | 4.0% + local 4.5% | ~8% total |
| Florida | 6.0% + local 1.5% | ~7% total |
| Illinois | 6.25% + local 3.5% | ~9.75% Chicago |
| Pennsylvania | 6.0% | + local in Allegheny/Philadelphia |
| Ohio | 5.75% + local 2.25% | ~8% total |
| Georgia | 4.0% + local 4% | ~8% total |
| North Carolina | 4.75% + local 2.75% | ~7.5% total |
| Michigan | 6.0% | flat |

**Strategy**: Calculate margins using the highest-volume-state rate you expect. Re-validate with home-state rate if nexus triggered.

## US Fulfillment Strategy (Anti-De-Minimis)

The $800 de minimis is RESTRICTED. Every direct shipment from China now incurs:
- Section 301 tariff (7.5% - 25% depending on HTS code)
- MPF (0.3464%, min $31.67)
- HMMPF (Section 301, 25% on covered goods)

**Solution**: US 3PL bulk import. Pay duty ONCE on the container/pallet, fulfill from US warehouse.

**Recommended providers (free/cheap)**:
- Amazon FBA (Small & Light program)
- ShipBob (no minimum, pay-per-order)
- ShipMonk (no minimum, 2-day shipping)
- eBay Fulfilled by eBay (free storage 30 days)
- Deliverr/Flexport (e-commerce focus)

**Cost in margin**: Add $3-7 per order 3PL fee. Factor into True Margin Matrix.

## Anti-Patterns to Avoid
- ❌ Pretending Meta Ad Library API works for US (it doesn't)
- ❌ Forgetting to include sales tax in retail price display (FTC violation)
- ❌ Not registering for sales tax once nexus triggered (back liability)
- ❌ Shipping from China direct with de minimis assumed (it's gone)
- ❌ Using EU margin formula for US (no VAT, but has sales tax + duty differences)
- ❌ Ignoring Section 301 tariff stack on China goods
- ❌ Comparing US CAC benchmark to EU's €21.48 (different CPMs)
