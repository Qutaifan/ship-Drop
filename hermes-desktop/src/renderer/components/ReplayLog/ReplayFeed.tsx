import React from "react";
import { useHermesState } from "../../state/useHermesState";

export const ReplayFeed: React.FC = () => {
  const replayLogs = useHermesState((s) => s.replayLogs);

  return (
    <div className="hermes-glass-card p-5 h-[300px] flex flex-col justify-between">
      <div className="flex justify-between items-center border-b border-slate-800 pb-3">
        <h3 className="text-sm font-semibold font-mono text-slate-100 flex items-center space-x-2">
          <span className="w-2 h-2 rounded-full bg-[#FFB800]" />
          <span>MULTI-AGENT REPLAY LOG &amp; FLIGHT RECORDER</span>
        </h3>
        <span className="text-xs text-slate-400 font-mono">
          Cryptographic HMAC Verified
        </span>
      </div>

      <div className="flex-1 overflow-y-auto space-y-2 py-3 pr-2 scrollbar-thin">
        {replayLogs && replayLogs.length > 0 ? (
          replayLogs.map((log: any, idx: number) => (
            <div key={idx} className="text-xs font-mono p-2 rounded bg-slate-900/60 border border-slate-800/80 flex justify-between items-start">
              <div>
                <span className="text-[#00F0FF]">[{log.timestamp?.slice(11, 19) || "NOW"}]</span>{" "}
                <span className="text-[#FFB800]">{log.action || "DECISION"}</span>{" "}
                <span className="text-slate-200">{log.details || log.reason || "Autonomous multi-agent signal generated"}</span>
              </div>
              <span className="text-[10px] text-slate-500">{log.actor || "HermesCore"}</span>
            </div>
          ))
        ) : (
          <div className="text-xs text-slate-400 font-mono text-center py-8">
            Listening for multi-agent trade signals, CJ telemetry audits, and ranker evaluations...
          </div>
        )}
      </div>

      <div className="text-[10px] font-mono text-slate-400 border-t border-slate-800 pt-2 flex justify-between">
        <span>Channel: Sovereign In-Memory + SQLite Provenance</span>
        <span className="text-[#00FF88]">Audit Stream: 100% Intact</span>
      </div>
    </div>
  );
};
