import React from "react";

interface SKUCardProps {
  sku: any;
  onSelectSupplier?: (supplierId: string) => void;
}

export const SKUCard: React.FC<SKUCardProps> = ({ sku, onSelectSupplier }) => {
  const topSupplier = sku.competing_suppliers?.[0] || {};
  const isHealthy = (topSupplier.stability_score || 0.9) >= 0.85;

  return (
    <div className="hermes-glass-card p-5 flex flex-col justify-between space-y-4 hover:border-[#00F0FF]">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <span className="text-xs font-mono uppercase tracking-wider text-[#00F0FF]">
            {sku.candidate_id || "SKU-TARGET"}
          </span>
          <h3 className="text-base font-semibold text-slate-100 mt-1 line-clamp-1">
            {sku.product_name || "Catalog Product Item"}
          </h3>
        </div>
        <div className="flex flex-col items-end">
          <div
            className={`px-2.5 py-1 rounded text-xs font-bold font-mono ${
              isHealthy ? "bg-emerald-950/80 text-[#00FF88] border border-emerald-500/40" : "bg-rose-950/80 text-rose-400 border border-rose-500/40"
            }`}
          >
            STAB {(topSupplier.stability_score || 0.95).toFixed(2)}
          </div>
          <span className="text-[10px] uppercase font-mono tracking-widest text-slate-400 mt-1">
            {topSupplier.tier || "PREFERRED_DOMESTIC"}
          </span>
        </div>
      </div>

      {/* Primary Intelligence Metrics Grid */}
      <div className="grid grid-cols-3 gap-2 py-2 border-y border-slate-800/80 text-xs">
        <div>
          <div className="text-slate-400 text-[10px]">Optimized Price</div>
          <div className="text-sm font-bold text-slate-100 mt-0.5">$62.99</div>
          <div className="text-[9px] text-[#00FF88]">CAC Gate: PASS</div>
        </div>
        <div>
          <div className="text-slate-400 text-[10px]">DSA Competitor</div>
          <div className="text-sm font-bold text-[#FFB800] mt-0.5">€69.90</div>
          <div className="text-[9px] text-slate-400">Sweet Spot (6 ads)</div>
        </div>
        <div>
          <div className="text-slate-400 text-[10px]">Demand Runway</div>
          <div className="text-sm font-bold text-cyan-400 mt-0.5">64 Days</div>
          <div className="text-[9px] text-slate-400">ROP: 10 units</div>
        </div>
      </div>

      {/* Supplier & Action Bar */}
      <div className="flex justify-between items-center text-xs pt-1">
        <span className="text-slate-400 font-mono text-[11px] truncate max-w-[200px]">
          Hub: {topSupplier.supplier_id || "cj-domestic-hub"}
        </span>
        <button
          onClick={() => onSelectSupplier && onSelectSupplier(topSupplier.supplier_id)}
          className="px-3 py-1 bg-[#00F0FF]/10 hover:bg-[#00F0FF]/25 border border-[#00F0FF]/40 rounded text-[11px] font-mono text-[#00F0FF] transition-all"
        >
          Inspect Brain →
        </button>
      </div>
    </div>
  );
};
