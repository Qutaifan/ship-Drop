---
name: ecommerce-validator
description: Validate dropshipping candidates against the 6-Criteria, margin and CAC gates.
version: 0.2.0
author: Ahmad, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [dropshipping, validation, margin, cac, eu-customs]
    related_skills: [comfyui-product-staging, veo-flow-ads]
---

> **Skill superseded in two places.** Step 2's "Buying Constraint 20.3% of VAT-inclusive retail" formula was a derived heuristic, not a real input constraint, and was retired 2026-08-30. The CAC gate from AGENTS.md §4A was added 2026-08-30 and is missing from this skill. Both fixes are below — read carefully before running.

---

# E-Commerce Product Validator Skill

Use this skill when evaluating a candidate product, analyzing niche viability, or creating a new entry in `products/<name>.md`.

---

## 1. Execution Workflow (PROTOCOL-01)

```
1. Demand Pre-Screen ──► 2. True Margin Matrix ──► 3. Competitor Gate ──► 4. Regulatory Check
   (scripts/demand_screen.py) (scripts/margin_solver.py) (scripts/ad_library.py)  (De Minimis / WEEE)
```

---

## 2. Step-by-Step Instructions

### Step 1: Demand & Proof-Burden Pre-Screen
Run the multi-pass YouTube pre-screen to measure keyword ranking stability, short-form viability, and proof burden:
```bash
python scripts/demand_screen.py "<product search term>"
```
- **Evaluation Rules**:
  - **Skeptic Ratio $\ge 50\%$**: Fails Criterion 3 (High proof burden — requires lab/chemical proof, unusable in a 3s silent video).
  - **Median Views $< 2,500$**: Fails Demand Floor (Near-zero consumer interest / commodity).
  - **Short-Form Share $\ge 20\%$**: Confirms the category exists naturally in vertical video format.

---

### Step 2: Sourcing & True Margin Matrix
**Run both gates in order. PASS requires both.**

**2a. Unit margin** — `scripts/margin_solver.py` (VAT-corrected 2026-08-30):

```
python scripts/margin_solver.py --retail <R> --cost <C> --shipping <S> --duty <D> --vat 0.19
```

Formula in the script: `Net Margin = (R ÷ (1 + VAT)) − (C + S + D) − 0.03 × R`. VAT is collected on the customer's behalf and remitted — it is never revenue. The 3% payment fee is charged on the gross, so it is NOT divided by VAT.

**2b. CAC gate** — `scripts/profitability.py` (added 2026-08-30, the gate the True Margin Matrix does not enforce):

```
python scripts/profitability.py --retail <R> --landed <L>
```

Net margin must be ≥ **2× median CPA benchmark** (~EUR 21.48 from Triple Whale Aug 2025–Jul 2026, 53,000+ brands). The script exits 1 on failure. A product can clear 3× COGS and still lose money on every advertised sale if CAC is ignored — that is exactly the failure mode this gate prevents.

**Evaluation Rules (combine both gates):**
- **COGS Gate**: Net Margin ≥ 3 × COGS (from 2a).
- **Profit Floor**: Net Margin > €15.00 (from 2a).
- **CAC Gate**: Net Margin ≥ 2 × median CPA ≈ EUR 21.48 (from 2b). **Non-negotiable for any product that will run paid ads.**
- **Direct-from-China EU duty**: Add €3 flat customs duty + import VAT + ~€2 carrier handling **per unit**. **Never** lump these into cost without surfacing them — the margin solver does NOT auto-add them. The skill author kept them out of the CLI by design; passing `--duty 3` is required for direct-from-China.
- **EU Warehouse Mandatory** (preferred path): Bulk import duty is paid once on the warehouse import. `--duty 0` is correct. The €3 + VAT + carrier does not apply to subsequent customer shipments.
```bash
python scripts/margin_solver.py --retail <target_price> --cost <unit_cost> --shipping <freight> --duty 0 --vat 0.19
```
- **Evaluation Rules**:
  - **Buying Constraint Rule**: Landed cost ($\text{Cost} + \text{Shipping} + \text{Duty}$) must be **$\le 20.3\%$ of VAT-inclusive retail** (at DE 19% VAT).
  - **COGS Gate**: $\text{Net Margin} \ge 3 \times \text{COGS}$.
  - **Profit Floor**: $\text{Net Margin} > €15.00$.
  - **EU Warehouse Mandatory**: Bulk import duty is paid once. If fulfilling direct-from-China, add €3 flat customs duty + import VAT + €2 carrier handling per unit.

---

### Step 3: Meta Ad Library Competitor Gate
Query the official Meta Graph API to verify commercial profitability and category saturation:
```bash
python scripts/ad_library.py "<product search term>" --countries DE,FR,NL
```
- **Evaluation Rules**:
  - **Competitors running ads**: Need **5 to 10 distinct advertisers**.
  - **Ads active 30+ days**: Need **$\ge 3$ aged ads** (proof of sustained profitability).
  - **Saturation Warning**: Over 15 active advertisers signals bid-up CPMs and high entry barriers.

---

### Step 4: Regulatory & Compliance Verification
- **WEEE & Battery Directives**: Non-electrical products prioritized. If electrical, register per-country WEEE and battery take-back obligations.
- **EU AI Act**: Ensure disclosure is planned for synthetic imagery: *"Product imagery assisted by generative AI"*.
- **FTC Pricing Safeguards**: All dynamic pricing must be rule-based (inventory/time), never user-profiled.

---

## 3. Generating the Product File
Populate `products/<product-slug>.md` using the exact structure required by `scripts/validate_workspace.py`. Only assign a **PASS** verdict if all criteria, margin gates, and competitor thresholds are fully satisfied.
