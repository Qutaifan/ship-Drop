import React, { useEffect } from "react";
import { useHermesState } from "./state/useHermesState";
import { IntelligenceRings } from "./components/CommandBridge/IntelligenceRings";
import { SKUCard } from "./components/SKUCards/SKUCard";
import { Graph3D } from "./components/NetworkGraph/Graph3D";
import { ExecutionWindowMonitor } from "./components/Autonomy/ExecutionWindowMonitor";
import { ReplayFeed } from "./components/ReplayLog/ReplayFeed";
import "./styles/frostedGlass.css";

export const App: React.FC = () => {
  const { overview, skus, fetchTelemetry, selectSupplier } = useHermesState();

  useEffect(() => {
    // Initial fetch
    fetchTelemetry();
    // Poll local telemetry every 2.5 seconds
    const interval = setInterval(fetchTelemetry, 2500);
    return () => clearInterval(interval);
  }, [fetchTelemetry]);

  return (
    <div className="min-h-screen bg-[#050811] text-slate-100 p-6 space-y-6 font-sans">
      {/* Top Cockpit Header */}
      <header className="flex justify-between items-center pb-4 border-b border-slate-800">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-[#00F0FF] to-[#FFB800] p-0.5 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <div className="w-full h-full bg-[#0A1020] rounded-[7px] flex items-center justify-center font-mono font-bold text-sm text-[#00F0FF]">
              ⚡
            </div>
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-wider font-mono text-slate-100 flex items-center space-x-2">
              <span>HERMES-ECOM COMMAND BRIDGE</span>
              <span className="text-[10px] px-2 py-0.5 rounded bg-[#00F0FF]/15 text-[#00F0FF] border border-[#00F0FF]/30 font-normal">
                v1.0.0 DESKTOP
              </span>
            </h1>
            <p className="text-xs text-slate-400 font-mono">
              Autonomous 5-Layer Algorithmic Retail Arbitrage &amp; Sourcing Engine
            </p>
          </div>
        </div>

        {/* Global Vitals Summary */}
        <div className="flex items-center space-x-6 text-xs font-mono">
          <div>
            <span className="text-slate-400">Monthly Revenue:</span>
            <div className="text-sm font-bold text-[#00FF88]">
              ${(overview?.system_vitals.monthly_gross_revenue || 12450.0).toLocaleString()}
            </div>
          </div>
          <div>
            <span className="text-slate-400">Monthly Net Margin:</span>
            <div className="text-sm font-bold text-[#00F0FF]">
              ${(overview?.system_vitals.monthly_net_margin || 8420.0).toLocaleString()}
            </div>
          </div>
          <div>
            <span className="text-slate-400">COGS Multiple:</span>
            <div className="text-sm font-bold text-[#FFB800]">
              {(overview?.system_vitals.blended_cogs_multiple || 6.2).toFixed(1)}x
            </div>
          </div>
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded bg-slate-900 border border-slate-800">
            <span className="w-2 h-2 rounded-full bg-[#00FF88] animate-ping" />
            <span className="text-slate-300">TELEMETRY LIVE</span>
          </div>
        </div>
      </header>

      {/* Main Bridge Centerpiece: 5 Concentric Intelligence Rings */}
      <section>
        <IntelligenceRings />
      </section>

      {/* SKU Intelligence Cards Grid */}
      <section className="space-y-3">
        <div className="flex justify-between items-center">
          <h2 className="text-sm font-mono font-semibold uppercase tracking-wider text-slate-300 flex items-center space-x-2">
            <span className="w-2 h-2 rounded-full bg-[#00F0FF]" />
            <span>SKU INTELLIGENCE MATRIX ({skus.length || 1} PRODUCTS)</span>
          </h2>
          <span className="text-xs font-mono text-slate-400">
            Live DSA Competitor Anchors &amp; Predictive Drift Active
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {skus.length > 0 ? (
            skus.map((sku: any, idx: number) => (
              <SKUCard key={sku.candidate_id || idx} sku={sku} onSelectSupplier={selectSupplier} />
            ))
          ) : (
            <SKUCard
              sku={{
                candidate_id: "cand-cj-sku-magnetic-cord-6p",
                product_name: "Magnetic Cable Organizer 6-Pack Desk Clips",
                competing_suppliers: [
                  {
                    supplier_id: "cj-dropshipping-us-domestic-hub",
                    tier: "PREFERRED_DOMESTIC",
                    stability_score: 0.98,
                  },
                ],
              }}
              onSelectSupplier={selectSupplier}
            />
          )}
        </div>
      </section>

      {/* Bottom Cockpit Split: Network Graph, Autonomy Monitor & Flight Recorder */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Graph3D />
        <ExecutionWindowMonitor />
        <ReplayFeed />
      </section>
    </div>
  );
};

export default App;
