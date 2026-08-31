# US Market - Entry Summary

## Why US First Now
1. **$800 de minimis is GONE** for China-origin goods (Executive Order 2025). Every direct shipment now incurs full Section 301 duty + MPF + HMMPF. Direct ship is dead.
2. **US 3PL is the only viable fulfillment path** — bulk import, pay duty once, fulfill domestically. This is the US equivalent of the EU warehouse strategy.
3. **CPMs are 2x EU** (TikTok US $8-15 vs EU $4-8; Meta US $12-25 vs EU $5-12) — meaning you need higher absolute net margin per sale, which means higher retail ($68-105 vs EU €62-93).
4. **Meta Ad Library API does NOT return US commercial ads** (DSA only covers EU/UK). Competitor counts in the US must be done by hand in the web UI.

## The Three Hard Constraints

### 1. Sales tax (state-by-state)
- Federal VAT doesn't exist; each state runs its own sales tax
- Register once, file monthly/quarterly
- **Free shortcut**: Streamlined Sales Tax (SST) registration covers 24 states — register once at streamlinedsalestax.org

### 2. Bulk import to US 3PL (mandatory)
- Section 301 tariff on China goods is 7.5-25% depending on HTS code
- Direct ship is dead; every order would pay full duty stack
- 3PL (ShipBob, ShipMonk, Amazon FBA) costs $3-7 per order but eliminates per-order duty
- **Cascade rule**: duty paid once on bulk import → $0 per-order duty

### 3. Manual competitor validation
- Meta Ad Library API returns political/social-issue ads only for US
- 5-10 advertisers + 3+ active 30+ days must be **counted in the web UI by hand**
- Use `scripts/ad_library_us_manual.py` to record the manual count

## US Pricing Economics

| Item | Value |
|---|---|
| Target retail | $68 - $105 |
| Median US CPA | $23.50 |
| CAC gate | Net margin ≥ 2 × $23.50 = $47.00 |
| Net margin floor | $20 |
| 3x COGS gate | Standard |
| 3PL pick+pack | $3 - 7 per order |
| US shipping | $4 - 7 standard |
| Stripe fee | 2.9% + $0.30 on gross |

## Quick-Start (US)

1. **Pick 3PL** — ShipBob (free to start), ShipMonk, or Amazon FBA
2. **Pick first product** — must hit $68+ retail AND $47+ net margin AND clear CAC gate
3. **Validate**:
   ```bash
   # Pre-screen
   python3 scripts/demand_screen.py --product "X" --market us
   # Margin
   python3 scripts/margin_solver_us.py --retail 85 --state-tax 0.07 --cost 12 --shipping 5.50 --duty 0 --threepl 3.50
   # Competitor count (manual web UI)
   python3 scripts/ad_library_us_manual.py --product "X" --advertiser "Brand A" --first-seen 2026-06-01 --last-seen 2026-08-30 --ads 8 --likes 50000
   # ... add 4-9 more advertisers
   python3 scripts/ad_library_us_manual.py --product "X" --check
   ```
4. **Bulk-import first batch** to US 3PL (100-300 units, air freight for speed)
5. **Configure storefront**: US pricing, sales tax (Stripe Tax free or manual), 30-day return policy
6. **Launch test campaign**: $500-1000, Meta + TikTok US targeting
7. **Monitor**: daily sales check, reorder at 2 weeks remaining

## Per-Department US Playbooks

- `agency/departments/market-intelligence/us-market/US-MARKET.md` — market context, de minimis, sales tax, FTC
- `agency/departments/product-validation/us-market/US-VALIDATION.md` — PROTOCOL-01 US variant, manual ad library
- `agency/departments/financial-analytics/us-market/US-MARGIN-MATRIX.md` — corrected USD margin formula + worked examples
- `agency/departments/campaign-operations/us-market/US-CAMPAIGNS.md` — platform differences, US ad compliance, creative
- `agency/departments/supply-chain/us-market/US-FULFILMENT.md` — US 3PL selection, bulk import, Section 301, HTS

## Key Differences from EU at a Glance

| Aspect | EU | US |
|---|---|---|
| De minimis | €150 gone, €3 flat duty (2026-08-30) | $800 restricted (2025) |
| Tax on retail | VAT 17-27% by country | State sales tax 0-10% |
| Tax remittance | IOSS/OSS one-stop | SST + per-state registration |
| Customs | 1 customs item per consignment (often $3 duty) | Section 301 + MPF + HMMPF |
| Fulfilment strategy | EU warehouse | US 3PL bulk import |
| Retail target | €62-93 | $68-105 |
| Median CPA | €21.48 | $23.50 |
| Meta Ad Library API | Works (DSA-mandated) | Doesn't work (DSA doesn't apply) |
| Competitor check | `scripts/ad_library.py` | `scripts/ad_library_us_manual.py` (manual) |
| Currency | EUR | USD |
| Margin formula | `(R/1.19) - C - €3 - 0.03R` | `(R/1.07) - C - $0 - 3PL - 0.029R - $0.30` |

## EU-First vs US-First Decision

**EU-first advantages**:
- Competitor validation is automatable (Meta Ad Library API works)
- True Margin Matrix is well-calibrated
- AGENTS.md PROTOCOL-01/02/03 optimized for EU
- Stripe + IOSS + EU warehouse is a proven stack

**US-first advantages** (Ahmad's chosen direction):
- Larger addressable market (330M vs 450M EU, but US e-com is faster-growing)
- Higher AOV tolerance (US customers buy higher-priced goods)
- English-only content (no localization)
- Single currency, no FX exposure
- Bigger TikTok/Meta ad inventory for scaling

**The price of US-first**: Manual competitor validation, mandatory US 3PL, state-by-state sales tax, higher absolute CAC, no automation leverage. The agency must absorb these costs.

## Recommended Product Types (US Sweet Spot)

US market rewards different products than EU. Best categories:
- **Home organization** (US is furniture-depot-culture)
- **Pet accessories** (US pet market is $150B+)
- **Car accessories** (longer commutes, larger cars)
- **Outdoor/camping** (national-park culture)
- **Phone accessories** (high device penetration)
- **Fitness home gym** (gym-membership fatigue)
- **Kitchen gadgets** (open-floor-plan culture)
- **Tools & DIY** (US hardware-store culture)

Avoid:
- Apparel (returns, sizing, high CAC)
- Electronics (FCC cert, return rate)
- Children's toys (CPSIA, regulatory burden)
- Anything <$40 retail (can't clear US CAC gate)

## Scripts (US)

| Script | Purpose | Notes |
|---|---|---|
| `scripts/margin_solver_us.py` | US True Margin Matrix | USD, state tax, duty, 3PL, Stripe fee |
| `scripts/ad_library_us_manual.py` | Manual US Meta Ad Library | Records web-UI count, scores gate |
| `scripts/demand_screen.py` | YouTube demand pre-screen | Add `--market us` flag (TODO) |

The `margin_solver.py` (EU) and `margin_solver_us.py` (US) are intentionally separate — different formulas, different gates, different defaults. EU code is the reference; US is a deliberate variant.

## Compliance Quick-Reference

- **FTC pricing display**: Total price (incl. shipping + mandatory fees) before checkout
- **CAN-SPAM**: Working opt-out, postal address in footer, accurate subject
- **TCPA**: Prior express written consent for marketing texts
- **CCPA/CPRA (CA)**: Cookie banner, right to delete, opt-out of data sale
- **Sales tax nexus**: Register in states where threshold met
- **Section 301 duty**: Pay on bulk import to US 3PL (not per-order)
- **FTC Endorsement Guides**: #ad / #sponsored disclosures on all paid content
- **CPSIA**: Tracking labels + safety testing for children's products
- **FCC certification**: For RF-emitting electronics
- **Proposition 65 (CA)**: Cancer/reproductive harm warnings for specific chemicals

## Risk Posture (Hermes-Ecom)

- **Survival first**: US 3PL costs more upfront; budget conservatively
- **Risk-adjusted returns**: Higher CAC means smaller initial bets
- **No over-leverage**: Single market concentration = single-market risk
- **Learn from every outcome**: PROTOCOL-03 applies to US just like EU
- **Adapt to regime**: US 3PL landscape changes fast (Amazon FBA fee changes 2026, ShipBob acquisition by Maersk)
- **Continuous audit**: Re-validate US supplier every 90 days (Section 301 changes)
