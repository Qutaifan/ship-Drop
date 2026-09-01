# Hermes Desktop — Legendary Operator Cockpit Specification
## v1.0 Technical & Visual Design System Specification

**Target Platform:** Hermes Desktop (Tauri / Electron / WebGL)  
**Author:** Ahmad (Founder & Sovereign Operator)  
**Aesthetic Theme:** `Cyber-Frosted Obsidian` with Hermes Electric-Blue (`#00F0FF`) and Sovereign Gold (`#FFB800`) accents.  
**Telemetry Refresh Cadence:** 1,000ms – 3,000ms polling via `http://127.0.0.1:8080/api/v1`

---

## 1. Design System & Visual Tokens

### 1.1 Color Palette
```css
:root {
  /* Surface & Glass */
  --hermes-bg-void: #050811;
  --hermes-glass-panel: rgba(10, 16, 32, 0.75);
  --hermes-glass-border: rgba(0, 240, 255, 0.20);
  --hermes-glass-hover: rgba(0, 240, 255, 0.35);
  
  /* Primary Accents */
  --hermes-blue-electric: #00F0FF;
  --hermes-blue-glow: rgba(0, 240, 255, 0.40);
  --hermes-gold-sovereign: #FFB800;
  --hermes-gold-glow: rgba(255, 184, 0, 0.40);

  /* Status Tokens */
  --hermes-status-active: #00FF88;       /* Stability >= 0.85 (Green) */
  --hermes-status-watchlist: #FFDD00;    /* Drift warning (Yellow) */
  --hermes-status-degraded: #FF8800;     /* Reliability drop (Orange) */
  --hermes-status-critical: #FF0055;     /* Safety breach (Red) */
  --hermes-status-autonomous: #00BFFF;   /* Autonomous Window active (Cyan/Blue) */
}
```

### 1.2 Frosted Glass Shader & Effects
- **Backdrop Filter**: `blur(18px) saturate(180%)`
- **Panel Shadow**: `0 8px 32px 0 rgba(0, 0, 0, 0.65)`
- **Border Glow**: `inset 0 0 12px rgba(0, 240, 255, 0.08)`

---

## 2. Command Bridge: 5 Concentric Intelligence Rings

The home centerpiece features 5 GPU-rendered concentric rings pulsing with live agent telemetry:

```
                  ┌────────────────────────────────────────┐
                  │    RING 5: ECONOMIC OPTIMIZATION       │ ── Gross Revenue & Blended COGS
                  │  ┌──────────────────────────────────┐  │
                  │  │    RING 4: NETWORK EXPOSURE      │  │ ── Bipartite Systemic Blast Radius
                  │  │  ┌────────────────────────────┐  │  │
                  │  │  │   RING 3: LIFECYCLE STATE  │  │  │ ── Active / Watchlist / Critical
                  │  │  │  ┌──────────────────────┐  │  │  │
                  │  │  │  │ RING 2: VOLATILITY   │  │  │  │ ── Stability Drift & Inflation
                  │  │  │  │  ┌────────────────┐  │  │  │  │
                  │  │  │  │  │RING 1: STABILITY│  │  │  │  │ ── Deterministic Score (0.00-1.00)
                  │  │  │  │  │   [HERMES 3D]  │  │  │  │  │
                  │  │  │  │  └────────────────┘  │  │  │  │
                  │  │  │  └──────────────────────┘  │  │  │
                  │  │  └────────────────────────────┘  │  │
                  │  └──────────────────────────────────┘  │
                  └────────────────────────────────────────┘
```

| Layer Ring | Telemetry Source | Visual Animation Behavior |
|---|---|---|
| **Ring 1: Sourcing Stability** | `/api/v1/telemetry/overview` | Core ring radius: 1.2m; pulsing glow mapped to average stability ($0.00\text{--}1.00$). |
| **Ring 2: Volatility Drift** | `/api/v1/sourcing/supplier/<id>` | Radius: 1.6m; rotation speed mapped to stock velocity and lead time inflation. |
| **Ring 3: Lifecycle State** | `/api/v1/sourcing/skus` | Radius: 2.0m; shifts from emerald green (`ACTIVE`) to amber (`WATCHLIST`) or crimson (`CRITICAL`). |
| **Ring 4: Network Exposure** | `/api/v1/network/graph` | Radius: 2.4m; orbital nodes render connected warehouse and carrier nodes. |
| **Ring 5: Economic Optimization** | `/api/v1/economic/portfolio` | Outer ring radius: 2.8m; electric cyan pulse when Founder Autonomous Window is active. |

---

## 3. SKU Intelligence Card Specification

Each catalog SKU is rendered as a modular intelligence tile:
1. **Header**: SKU Name, Sourcing Stability Badge (`0.98`), Lifecycle Pill (`ACTIVE`).
2. **Telemetry Radar**:
   - Landed Cost (\$7.13) vs Retail (\$62.99).
   - Net Unit Margin (\$54.10) & COGS Multiple ($7.7\times$).
   - Inventory Runway Countdown (`64 days remaining`).
   - Meta DSA Competitor Anchor (`€69.90 observed median`).
3. **Action Bar**:
   - Quick Reprice button.
   - Failover Switch simulation toggle.
   - Direct link to Supplier Cockpit.

---

## 4. 3D Network Topology (Phase-4 Graph)
* **Canvas**: WebGL ForceGraph3D / Three.js.
* **Nodes**:
  - `SKU`: Hexagonal cyan prism.
  - `SUPPLIER`: Gold dodecahedron.
  - `WAREHOUSE`: Slate cube (glows red on drift).
  - `CARRIER`: Wireframe sphere.
* **Edges**: Elasticity springs indicating latency and volume allocation.

---

## 5. Autonomous Window Control Panel
* Real-time countdown timer: `HH:MM:SS` until window expiration.
* Remaining spend budget bar: `$Consumed / $SpendCap`.
* Cryptographic signature badge: `HMAC-SHA256: 72a8c...`.
* **Red Emergency Revoke Button**: Instantly triggers killswitch via `POST /api/v1/governance/window/revoke`.
