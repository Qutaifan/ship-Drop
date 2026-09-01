# Hermes Canary Deployment Plan: Autonomous Supplier Actions (`auto_drift_actions`)

**Owner:** Ahmad (Founder)  
**Target Feature:** Staged activation of automated `SUPPLIER_SWITCH` and `SELL_KILL` actions  
**Current Global State:** `auto_drift_actions: false` (Founder Gate Active)  

---

## 1. Staged Rollout Timeline

```
  Phase 0: Triage Window (14 Days)
  ├── 100% Founder Sign-off required
  ├── Collect false positive rates & latency
  └── Verify stability score reliability
         │
         ▼
  Phase 1: Canary Cohort (3 SKUs / 7 Days)
  ├── auto_drift_actions = true ONLY for Canary Cohort
  ├── Non-canary products remain under Founder review
  └── Maximum automated spend / order cap: $250
         │
         ▼
  Phase 2: Expanded Canary (10 SKUs / 7 Days)
  ├── Multi-warehouse domestic switches enabled
  └── Real-time Slack dispatch & automated kill-switch
         │
         ▼
  Phase 3: Sovereign Full Autonomy
  └── auto_drift_actions = true globally with hard tripwires
```

---

## 2. Canary Cohort Selection Criteria
Only SKUs meeting all four criteria qualify for the initial Canary test:
1. **Proven Verification History**: $\ge 10$ verification cycles completed without flapping.
2. **High Supplier Stability**: Baseline stability score $\ge 0.85$.
3. **Established Secondary Supplier**: Candidate dossier must have a pre-verified domestic fallback warehouse on file.
4. **Resilient Net Margin**: Reconciled net margin $\ge \$15.00$ per sale ($> 2.5\times\text{COGS}$).

### Initial Recommended Canary Cohort (3 SKUs):
- `cand-cj-sku-magnetic-cord-6p` (Magnetic Cable Organizer)
- `candidate-us-2026-09-01-foldable-silicone-bowl` (Foldable Silicone Bowls)
- `candidate-us-2026-09-01-magnetic-cable-organizer` (Silicone Cord Clips)

---

## 3. Automated Tripwires & Instant Rollback Triggers

If **ANY** of the following tripwires trigger during the Canary run, the system automatically flips `auto_drift_actions` back to `false` and reverts to 100% Founder Sign-off:

| Tripwire | Threshold | Detection Mechanism | Automated Action |
|---|---|---|---|
| **False Positive Drift Alert** | $> 5\%$ of drift signals over 48 hours | Operator flags alert via `revert-verifications` | Global fallback to Founder Gate |
| **Margin Compression Surge** | $\Delta$ Net Margin drops $< -\$2.00$ post-switch | `MarginReconciler` post-switch check | Immediate kill-switch & pause listing |
| **Carrier Lead Time Breach** | Fallback warehouse exceeds 5 business days | Delivery tracking scan | Flag supplier & notify Founder |
| **Supplier API Flapping** | $> 2$ state transitions within 24 hours | Verification audit log scan | Place SKU in 48h Quarantine |

---

## 4. Operational Emergency Commands

```bash
# Instantly kill autonomous actions across all workers:
python -m agency.cli feature-flag set auto_drift_actions false

# Revert an errant supplier switch and restore previous landed costs:
python -m agency.cli revert-verifications <candidate_id> --count 1 --reason "Canary tripwire breached"

# Defer any questionable proposal into quarantine:
python -m agency.cli approve-signal <signal_id> --action DEFER --actor Founder
```
