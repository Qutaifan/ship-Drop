import React from "react";
import { useHermesState } from "../../state/useHermesState";

export const Graph3D: React.FC = () => {
  const networkGraph = useHermesState((s) => s.networkGraph);
  const nodes = networkGraph?.nodes || [
    { id: "cand-cj-sku-magnetic-cord-6p", type: "SKU", color: "#00F0FF" },
    { id: "cj-dropshipping-us-domestic-hub", type: "SUPPLIER", color: "#FFB800" },
    { id: "us-east-nj-domestic", type: "WAREHOUSE", color: "#00FF88" },
    { id: "carrier-usps-priority", type: "CARRIER", color: "#8A2BE2" },
  ];

  return (
    <div className="hermes-glass-card p-5 h-[350px] flex flex-col justify-between">
      <div className="flex justify-between items-center border-b border-slate-800 pb-3">
        <h3 className="text-sm font-semibold font-mono text-slate-100 flex items-center space-x-2">
          <span className="w-2 h-2 rounded-full bg-[#00F0FF]" />
          <span>PHASE-4 NETWORK TOPOLOGY RADAR</span>
        </h3>
        <span className="text-xs text-[#00F0FF] font-mono">
          {nodes.length} Connected Nodes
        </span>
      </div>

      {/* Network Nodes Radar View */}
      <div className="flex-1 flex items-center justify-around py-4">
        {nodes.map((node: any) => (
          <div key={node.id} className="flex flex-col items-center space-y-2 group cursor-pointer">
            <div
              className="w-14 h-14 rounded-xl flex items-center justify-center border transition-all duration-300 group-hover:scale-110 shadow-lg"
              style={{
                borderColor: node.color || "#00F0FF",
                backgroundColor: `${node.color || "#00F0FF"}15`,
                boxShadow: `0 0 20px ${node.color || "#00F0FF"}30`,
              }}
            >
              <span className="text-xs font-mono font-bold" style={{ color: node.color || "#00F0FF" }}>
                {node.type?.slice(0, 3)}
              </span>
            </div>
            <div className="text-[11px] font-mono text-slate-300 max-w-[120px] text-center truncate">
              {node.id}
            </div>
            <div className="text-[9px] uppercase tracking-wider text-slate-400">
              {node.type}
            </div>
          </div>
        ))}
      </div>

      {/* Footer / Systemic Blast Radius Alert */}
      <div className="text-[11px] font-mono text-slate-400 flex justify-between items-center border-t border-slate-800/80 pt-2">
        <span>Systemic Blast Radius: &lt; 25% Portfolio</span>
        <span className="text-[#00FF88]">Multi-Hub Failover: ACTIVE</span>
      </div>
    </div>
  );
};
