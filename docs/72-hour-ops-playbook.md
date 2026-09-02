# Hermes 72-Hour Operations Playbook

**Owner:** Ahmad (Founder)  
**Objective:** Maintain zero financial leakage, verify supplier stability telemetry, and collect triage metrics during the initial 72-hour deployment window.

---

## 1. Cadence & Schedule (Hours 0 – 72)

| Time Window | Operational Action | Command / Tool |
|---|---|---|
| **Every 1 Hour** | Automated Phase 2 Smoke Test | `npm run agency:smoke` |
| **Every 1 Hour** | Continuous Drift Scan Cycle | `python -m agency.cli drift --json` |
| **Every 4 Hours** | Scheduled Supplier Reality Audit | `python -m agency.cli verify` |
| **Every 24 Hours** | Verification Archival & Log Rotation | `python -m agency.cli rotate-verifications --days 90` |
| **Hour 72** | Canary Readiness Review | `python scripts/canary_controller.py status` |

---

## 2. Hard Alert Thresholds & Tripwires

| Metric | Target Normal | Alert Threshold | Immediate Action |
|---|---|---|---|
| **Supplier Stability Score** | $\ge 0.85$ | $< 0.70$ | Re-verify supplier coordinates and stock level. |
| **Landed Cost Drift** | $< 3\%$ | $\ge 8\%$ | Auto-generates `sig-supplier-drift-*` proposal. |
| **Stock Level Depth** | $\ge 200$ units | $< 30$ units | Immediate `STOCK_DEPLETED` emergency alert. |
| **Transit Lead Time** | $\le 5$ days | $> 7$ days | Flag carrier routing mismatch. |
| **False Positive Rate** | $0\%$ | $> 5\%$ | Trip circuit breaker; revert errant verification. |
| **Net Margin Compression** | Safe ($>\$15$) | Delta $< -\$2.00$ | Put listing on `HOLD` via `approve-signal`. |

---

## 3. Incident Response & Emergency Rollback

### Scenario 1: Supplier API Glitch / Flapping Telemetry
*Symptom:* Bot reports 0 stock or inaccurate 50% price spike due to vendor feed maintenance.
```bash
# 1. Revert the erroneous verification record (restores previous verified state):
python -m agency.cli revert-verifications <candidate_id> --count 1 --reason "Supplier feed glitch"

# 2. Defer any generated drift proposal into 48-hour quarantine:
python -m agency.cli approve-signal <signal_id> --action DEFER --actor Founder
```

### Scenario 2: Unplanned Spend / Circuit Breaker Trip
*Symptom:* Unintended action triggered or tripwire breached.
```bash
# 1. Instantly halt all automated actions globally:
python -m agency.cli feature-flag set auto_drift_actions false

# 2. Verify all live risk limits remain locked:
npm run agency:audit
```

### Scenario 3: Database Schema or Migration Issue
*Symptom:* SQLite query deadlock or column mismatch.
```bash
# Cleanly rollback migration 002:
python scripts/migrate.py down 002_supplier_verifications
```

---

## 4. Signal Triage Flow (Founder Manual Review)

When a notification arrives in Slack or CLI:
1. **Approve Domestic Switch:**
   ```bash
   python -m agency.cli approve-signal <sig_id> --action APPROVE_SUPPLIER_SWITCH --actor Founder
   ```
2. **Pause Listing (Prevent Deficit):**
   ```bash
   python -m agency.cli approve-signal <sig_id> --action PAUSE_LISTING --actor Founder
   ```
3. **Defer for Observation (48h):**
   ```bash
   python -m agency.cli approve-signal <sig_id> --action DEFER --actor Founder
   ```
