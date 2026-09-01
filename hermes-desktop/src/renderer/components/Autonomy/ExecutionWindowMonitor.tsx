import React from "react";
import { useHermesState } from "../../state/useHermesState";

export const ExecutionWindowMonitor: React.FC = () => {
  const { activeWindows, grantAutonomousWindow, revokeAutonomousWindow } = useHermesState();
  const currentWindow = activeWindows && activeWindows.length > 0 ? activeWindows[0] : null;

  return (
    <div className="hermes-glass-card p-5 space-y-4">
      <div className="flex justify-between items-center border-b border-slate-800 pb-3">
        <h3 className="text-sm font-semibold font-mono text-slate-100 flex items-center space-x-2">
          <span className={`w-2 h-2 rounded-full ${currentWindow ? "bg-[#00FF88] animate-pulse" : "bg-slate-600"}`} />
          <span>AUTONOMOUS EXECUTION WINDOW MONITOR</span>
        </h3>
        <span className={`text-xs font-mono px-2 py-0.5 rounded ${currentWindow ? "bg-emerald-950 text-[#00FF88] border border-emerald-500/40" : "bg-slate-800 text-slate-400"}`}>
          {currentWindow ? "AUTONOMY ARMED" : "FOUNDER GATED"}
        </span>
      </div>

      {currentWindow ? (
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-4 text-xs font-mono">
            <div>
              <span className="text-slate-400">Window ID:</span>
              <div className="text-slate-200 truncate mt-0.5">{currentWindow.window_id}</div>
            </div>
            <div>
              <span className="text-slate-400">Spend Cap / Remaining:</span>
              <div className="text-[#FFB800] mt-0.5">
                ${(currentWindow.remaining_spend_limit_usd || 0).toFixed(2)} / ${(currentWindow.spend_cap_usd || 0).toFixed(2)}
              </div>
            </div>
          </div>

          <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
            <div
              className="bg-[#00F0FF] h-2 rounded-full transition-all"
              style={{
                width: `${Math.min(100, ((currentWindow.remaining_spend_limit_usd || 1) / (currentWindow.spend_cap_usd || 1)) * 100)}%`,
              }}
            />
          </div>

          <div className="text-[10px] font-mono text-slate-400 truncate">
            Provenance HMAC: {currentWindow.hmac_signature}
          </div>

          <div className="pt-2">
            <button
              onClick={() => revokeAutonomousWindow(currentWindow.window_id)}
              className="w-full py-2 bg-rose-950/80 hover:bg-rose-900 border border-rose-600 text-rose-200 rounded text-xs font-mono uppercase tracking-wider transition-all"
            >
              🛑 EMERGENCY REVOKE AUTONOMOUS WINDOW
            </button>
          </div>
        </div>
      ) : (
        <div className="py-4 text-center space-y-3">
          <p className="text-xs text-slate-400 font-mono">
            No active autonomous execution window. All agent trading operations require explicit Founder approval.
          </p>
          <button
            onClick={() => grantAutonomousWindow(2.0, 500.0)}
            className="px-4 py-2 bg-[#00F0FF]/15 hover:bg-[#00F0FF]/30 border border-[#00F0FF]/50 text-[#00F0FF] rounded text-xs font-mono transition-all"
          >
            + Grant 2-Hour Autonomous Window ($500 Cap)
          </button>
        </div>
      )}
    </div>
  );
};
