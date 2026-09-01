# Hermes Agency CLI — Complete Production Reference

This guide provides operational syntax, flags, and real-world sample outputs for the Hermes Dropship CLI terminal (`python -m agency.cli`).

---

## 1. System Status & Security

### Operational Status
```bash
python -m agency.cli status
```
Displays SQLite database health, active candidates, verified suppliers, pending founder signals, and active cryptographic approval tokens.

### Governance & Access Audit
```bash
python -m agency.cli audit
```
Verifies Tool Access Tiers (ad spend and orders verified blocked without sign-off), cryptographic SHA-256 integrity across all approval tokens, and confirms zero-spend risk limits are enabled.

---

## 2. Product Discovery & Opportunity Scoring

### Catalog & Dossier Scanning
```bash
# Scan local markdown dossiers and product repositories
python -m agency.cli scan

# Search CJ Domestic Catalog (US or EU) and ingest matches directly
python -m agency.cli scan --query "magnetic" --warehouse US
```

### Opportunity Scoring Matrix
```bash
python -m agency.cli score
```
Runs pure `final_score()` across all candidates and prints the 4-D Opportunity Matrix (Profit, Risk, Trend, Opportunity Score, and Verdict).

---

## 3. Phase 2 Supplier Intelligence Commands

### Supplier Reality Audit (`verify`)
```bash
# Audit a specific candidate's supplier
python -m agency.cli verify cand-cj-sku-magnetic-cord-6p

# Audit all candidates in store
python -m agency.cli verify
```
**Sample Output:**
```text
═════════════════════════════════════════════════════════════════
  🏭 SUPPLIER REALITY AUDIT REPORT
═════════════════════════════════════════════════════════════════
  Verification ID : ver-20260901-cabc35
  Candidate ID    : cand-cj-sku-magnetic-cord-6p
  Supplier / SKU  : cj-dropshipping-us-domestic-hu (SKU-CAND-CJ-SKU-MAGNETIC)
  Stock Level     : 350 units in US (domestic)
  Quoted vs Real  : Product $3.80 -> $3.80 (Drift: +0.0%)
  Shipping        : $3.20 via USPS (3-5 days)
  Packaging Grade : polybag | Defect Rate: 1.2%
  Stability Score : 0.98 / 1.00 (Confidence: 92%)
  Status Verdict  : VERIFIED_PASS
  Notes           : All supplier checks verified: Domestic warehouse stock confirmed, transit <= 5 days.
═════════════════════════════════════════════════════════════════
```

### Margin Reconciliation (`reconcile`)
```bash
python -m agency.cli reconcile cand-cj-sku-magnetic-cord-6p
```
**Sample Output:**
```text
══════════════════════════════════════════════════════════════════════
  💰 MARGIN RECONCILIATION REPORT: Magnetic Cable Organizer 6-Pack Desk Clips
══════════════════════════════════════════════════════════════════════
  Status Verdict         : MARGIN_STABLE
  Compression Warning    : ✓ MARGIN SAFE
  Net Margin Delta       : -0.13 USD
----------------------------------------------------------------------
  Metric                       Theoretical        Verified & Buffered 
----------------------------------------------------------------------
  Product Sourcing Cost        $3.80              $3.80               
  Shipping & Carrier           $3.20              $3.33               
  Packaging Uplift             $0.00              $0.00               
  Total Landed Cost            $7.00              $7.13               
  Net Margin Per Order         $13.24             $13.11              
  COGS Multiple                —                  1.84               x
  Break-Even CPA               —                  $13.11              
  Expected ROAS                —                  2.72               x
══════════════════════════════════════════════════════════════════════
```

### Continuous Drift Monitoring (`drift`)
```bash
# Human-readable table
python -m agency.cli drift

# Machine-readable JSON output for automated dashboards
python -m agency.cli drift --json
```

### Chronological Verification History (`ver-history`)
```bash
python -m agency.cli ver-history cand-cj-sku-magnetic-cord-6p
```

---

## 4. Founder Trade Approvals & Execution

### List Pending Trade Signals
```bash
python -m agency.cli signals --status PENDING_FOUNDER_REVIEW
```

### Interactive Founder Review
```bash
python -m agency.cli review
```
Steps through pending trade signals one-by-one with `[A]pprove / [R]eject / [S]kip / [Q]uit` options.

### Direct Approval (Signed by Ahmad)
```bash
# Interactive confirmation prompt
python -m agency.cli approve sig-buy-cand-cj-sku-magnetic-cord-6p

# Non-interactive / script mode
python -m agency.cli approve sig-buy-cand-cj-sku-magnetic-cord-6p --yes --by Ahmad --budget 300.00
```

### Controlled Execution
```bash
# Execute through the single-point Execution Gateway
python -m agency.cli execute sig-buy-cand-cj-sku-magnetic-cord-6p
```
Verifies SHA-256 token, checks budget bounds, consumes approval token (preventing replay), and dispatches action.
