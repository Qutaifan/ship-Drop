---
name: ecommerce-validator
description: Systematically evaluate candidate dropshipping products against the 6-Criteria Formula, True Margin Matrix, Meta Ad Library competitor gates, and 2026 EU customs regulations.
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
Calculate unit economics under 2026 EU customs rules using `scripts/margin_solver.py`:
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
